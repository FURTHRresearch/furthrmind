import React, {useEffect, useMemo, useState} from "react";


import "./UnitEditor.css";

import DeleteIcon from "@mui/icons-material/Delete";
import EditIcon from "@mui/icons-material/Edit";
import Dialog from "@mui/material/Dialog";
import DialogContent from "@mui/material/DialogContent";
import DialogTitle from "@mui/material/DialogTitle";
import Paper from "@mui/material/Paper";
import Table from "@mui/material/Table";
import TableBody from "@mui/material/TableBody";
import TableCell from "@mui/material/TableCell";
import TableContainer from "@mui/material/TableContainer";
import TableHead from "@mui/material/TableHead";
import TableRow from "@mui/material/TableRow";
import axios from "axios";
import sanitizeHtml from "sanitize-html";
import useSWR from "swr";


import {useParams} from "react-router-dom";

import {Box, Button, IconButton, Stack, Typography} from "@mui/material";
import AddUnit from "./AddUnit";

const fetcher = (url) => fetch(url).then((res) => res.json());


const UnitEditor = ({show, onClose}) => {
    const [showAddUnitModal, setShowAddUnitModal] = useState(false);

    const [editData, setEditData] = useState({id: '', Name: '', Definition: ''});

    const params = useParams();

    const {data: units} = useSWR(
        `/web/units?project=${"project" in params ? params.project : ""}`,
        fetcher
    );

    const customUnits = useMemo(() => units ? units.filter(u => u.editable) : undefined, [units]);

    // useEffect(() => {
    //     if (customUnits && customUnits.length === 0) {
    //         setShowAddUnitModal(true);
    //     }
    // }, [customUnits, setShowAddUnitModal, show]);

    const handleRowEdit = (id) => {
        setEditData(customUnits.find(u => u.id === id));
        setShowAddUnitModal(true);
    };

    return (
        <Dialog open={show} onClose={onClose} fullWidth maxWidth="md">
            <DialogTitle sx={{padding: "10px 24px 5px 24px"}}>
                Custom units
            </DialogTitle>
            <DialogContent>
                <Typography variant="body1" sx={{color: "#6F7A7D", marginBottom: '1em'}}>
                    Define your own custom unit which suites your research in more better
                    and accurate way.
                </Typography>

                {showAddUnitModal && <AddUnit
                    show={showAddUnitModal}
                    onClose={() => {
                        setShowAddUnitModal(false);
                        setEditData({id: '', Name: '', Definition: ''});
                    }}
                    unitId={editData.id}
                    initialName={editData.Name}
                    initialDefinition={editData.Definition}
                />}

                <Box mt={4}>
                    <UnitEditorTable
                        data={customUnits}
                        handleRowEdit={handleRowEdit}
                    />
                    <Button
                        variant="contained"
                        style={{marginTop: "15px"}}
                        onClick={() => setShowAddUnitModal(true)}
                    >
                        Add new unit
                    </Button>
                </Box>

            </DialogContent>
        </Dialog>
    );
};

export default UnitEditor;

const UnitEditorTable = ({
                             data,
                             handleRowEdit,
                         }) => {

    return (
        <React.Fragment>
            <TableContainer component={Paper} sx={{maxHeight: 465}}>
                <Table sx={{minWidth: 650}} stickyHeader aria-label="sticky table">
                    <TableHead>
                        <TableRow>
                            <TableCell>Unit Name</TableCell>
                            {/* <TableCell align="left">Unit category</TableCell> */}
                            <TableCell align="left">Unit definition</TableCell>
                            <TableCell align="left">Action</TableCell>
                        </TableRow>
                    </TableHead>
                    <TableBody>
                        {data.map((row) => (
                            <UnitRow
                                row={row}
                                handleEdit={() => handleRowEdit(row.id)}
                            />
                        ))}
                    </TableBody>
                </Table>
            </TableContainer>
        </React.Fragment>
    );
};

const UnitRow = ({
                     row,
                     handleEdit,
                 }) => {

    const handleDelete = () => {
        axios.delete(`/web/units/${row.id}`);
        mutateUnits(units.filter(u => u.id !== row.id), false);
    };

    const params = useParams();

    const {data: units, mutate: mutateUnits} = useSWR(
        `/web/units?project=${"project" in params ? params.project : ""}`,
        fetcher
    );

    const renderUnitDefinition = (definition: string) => {
        if (definition === null || definition === undefined) return "";
        let matches = definition.matchAll(/<u>(.*?)<\/u>/g);

        for (const m of matches) {
            definition = definition.replace(
                m[0],
                '<span class="unit" contentEditable="false" unit="' +
                m[1] +
                '">' +
                units.find((u) => u.id === m[1])?.Name +
                "</span>"
            );
        }
        return definition;
    };

    return (
        <TableRow>
            <TableCell component="th" scope="row">
                {row.Name}
            </TableCell>
            {/* <TableCell align="left">{row.category}</TableCell> */}
            <TableCell align="left">
                <div dangerouslySetInnerHTML={{__html: sanitizeHtml(renderUnitDefinition(row.Definition))}}></div>
            </TableCell>
            <TableCell align="left">
                <Stack direction="row">
                    <IconButton onClick={handleEdit}>
                        <EditIcon sx={{fontSize: "16px"}}/>
                    </IconButton>
                    <IconButton>
                        <DeleteIcon sx={{fontSize: "16px"}} onClick={handleDelete}/>
                    </IconButton>
                </Stack>
            </TableCell>
        </TableRow>
    );
};