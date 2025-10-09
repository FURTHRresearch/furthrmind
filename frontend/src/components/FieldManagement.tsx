import * as React from 'react';
import Box from '@mui/material/Box';
import Collapse from '@mui/material/Collapse';
import IconButton from '@mui/material/IconButton';
import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableContainer from '@mui/material/TableContainer';
import TableHead from '@mui/material/TableHead';
import TableRow from '@mui/material/TableRow';
import Typography from '@mui/material/Typography';
import Paper from '@mui/material/Paper';
import DeleteIcon from '@mui/icons-material/Delete';
import EditIcon from '@mui/icons-material/Edit';
import KeyboardArrowDownIcon from '@mui/icons-material/KeyboardArrowDown';
import KeyboardArrowUpIcon from '@mui/icons-material/KeyboardArrowUp';

import axios from "axios";
import {useParams} from "react-router-dom";
import classes from "./ProjectPermissionList.module.css";
import {Button} from "@mui/material";
import AddIcon from "@mui/icons-material/Add";
import useSWR from "swr";
import NewFieldOverlay from "./Fields/NewFieldOverlay";
import FieldManagementEditOverlay from "./Overlays/FieldManagementEditOverlay";
import DeleteFieldManagement from "./Overlays/DeleteFieldManagement";

function createData(
    id: string,
    name: string,
    description: string,
) {
    return {
        id,
        name,
        description,
    };
}


function Row({row, admin}) {

    const params = useParams()
    const fetcher = url => fetch(url).then(res => res.json());
    const {
        data: rows,
        mutate: mutateFields
    } = useSWR('/web/projects/' + params.project + '/fields', fetcher);

    const [open, setOpen] = React.useState(false);
    const [openEditOverlay, setOpenEditOverlay] = React.useState(false);


    const [openDeleteOverlay, setOpenDeleteOverlay] = React.useState(false);
    const [editingData, setEditingData] = React.useState({
        fieldName: ''
    })

    const openEditOverlayHandler = () => {
        setOpenEditOverlay(true);
    }

    const closeEditOverlayHandler = () => {
        setOpenEditOverlay(false);
        setEditingData({
            fieldName: ''
        })
    }

    const handleEdit = (name: string, description: string) => {
        setEditingData({
            fieldName: name,
        });
        openEditOverlayHandler();
    }


    const handleDelete = (name: string, description: string) => {
        setEditingData({
            fieldName: name,
        });
        setOpenDeleteOverlay(true)
    }

    return (
        <React.Fragment>
            <TableRow sx={{'& > *': {borderBottom: 'unset'}}}>
                <TableCell component="th" scope="row">
                    {row.name}
                </TableCell>
                <TableCell>{String(row.type).substr(0, 50)}
                    {String(row.description).length > 50 &&
                        <React.Fragment>
                            ....
                            <IconButton
                                aria-label="expand row"
                                size="small"
                                onClick={() => setOpen(!open)}
                            >
                                {open ? <KeyboardArrowUpIcon/> : <KeyboardArrowDownIcon/>}
                            </IconButton>
                        </React.Fragment>
                    }
                </TableCell>
                <TableCell>
                    <IconButton aria-label="edit" size='small' onClick={() => handleEdit(row.name, row.description)}
                                disabled={!admin}>
                        <EditIcon/>
                    </IconButton>
                </TableCell>
                <TableCell>

                    <IconButton
                        onClick={() => handleDelete(row.name, row.description)}
                        aria-label="delete"
                        size='small'
                        disabled={!admin}
                    >
                        <DeleteIcon/>
                    </IconButton>
                </TableCell>

            </TableRow>
            <TableRow>
                <TableCell style={{paddingBottom: 0, paddingTop: 0}} colSpan={6}>
                    <Collapse in={open} timeout="auto" unmountOnExit>
                        <Box sx={{margin: 1}}>
                            <Typography variant="h6" gutterBottom component="div">
                                Detailed Description
                            </Typography>
                            <Typography variant="body2" gutterBottom component="div">
                                {row.description}
                            </Typography>

                        </Box>
                    </Collapse>
                </TableCell>
            </TableRow>

            {openEditOverlay && <FieldManagementEditOverlay
                open={openEditOverlay}
                setOpen={setOpenEditOverlay}
                onClose={closeEditOverlayHandler}
                fieldName={row.name}
                fieldId={row.id}
                mutateFields={mutateFields}
                rows={rows}

            />
            }
            {
                openDeleteOverlay && <DeleteFieldManagement
                    open={openDeleteOverlay}
                    setOpen={setOpenDeleteOverlay}
                    fieldName={row.name}
                    fieldId={row.id}
                    mutateFields={mutateFields}
                    rows={rows}
                />
            }
        </React.Fragment>
    );
}

export default function CollapsibleTable() {

    const params = useParams()
    const fetcher = url => fetch(url).then(res => res.json());
    const {
        data: rows,
        mutate: mutateFields
    } = useSWR('/web/projects/' + params.project + '/fields', fetcher);
    const [openCreateOverlay, setOpenCreateOverlay] = React.useState(false)
    const [creatingData, setCreatingData] = React.useState({
        fieldName: '',
        fieldType: ""
    })
    const [admin, setAdmin] = React.useState(false)

    axios.get("/web/permissions/" + params.project).then((r) => {
        if (r.data === "admin") {
            setAdmin(true)
        }
    })


    function onAdded(data) {
        const rowsCopy = []
        mutateFields([{
            id: data.id,
            name: data.Name,
            type: data.Type
        }, ...rows])

    }

    return (
        <TableContainer component={Paper} className="mt-4">
            <Table aria-label="collapsible table">
                <TableHead>
                    <TableRow>
                        <TableCell>Field Name</TableCell>
                        <TableCell>Field Type</TableCell>
                        <TableCell/>
                        <TableCell/>
                    </TableRow>
                </TableHead>
                <TableBody>


                    {rows ? rows.map((row) => (
                        <Row key={row.name} row={row} admin={admin}/>
                    )) : null}
                </TableBody>
            </Table>
            <div className={classes.inviteUserBtn}>
                <Button variant="text" startIcon={<AddIcon/>}
                        onClick={() => setOpenCreateOverlay(true)} disabled={!admin}
                >Add Field</Button>
                <div></div>

            </div>
            {openCreateOverlay && <NewFieldOverlay
                targetType={null}
                targetId={null}
                initialName={""}
                show={openCreateOverlay}
                onClose={() => {
                    setOpenCreateOverlay(false);
                }}
                onExited={() => {
                    setOpenCreateOverlay(false)
                }}
                onCreated={(data) => {
                    onAdded(data);
                    setOpenCreateOverlay(false);
                }}
                createNewNameOption={"--"}
                project={params.project}

            />
            }

        </TableContainer>
    );
}

