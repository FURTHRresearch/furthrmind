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
import SpreadsheetTemplateEditOverlay from './Overlays/SpreadsheetTemplateEditOverlay';
import DeleteTemplateOverlay from './Overlays/DeleteTemplate';
import {useParams} from "react-router-dom";
import axios from "axios";
import useSWR from "swr";

function createData(
    id: string,
    name: string,

) {
    return {
        id,
        name,
    };
}

function Row(props: { row: ReturnType<typeof createData> }) {
    const { row } = props;
    const [openEditOverlay, setOpenEditOverlay] = React.useState(false);
    const [openDeleteOverlay, setOpenDeleteOverlay] = React.useState(false);
    const [templateName, setTemplateName] = React.useState('');
    const [editingData, setEditingData] = React.useState({
        templateName: '',
    })

    const openEditOverlayHandler = () => {
        setOpenEditOverlay(true);
    }

    const closeEditOverlayHandler = () => {
        setOpenEditOverlay(false);
        setEditingData({
            templateName: ''
        })
    }

    const handleEdit = (name: string, ) => {
        setEditingData({
            templateName: name,

        });
        openEditOverlayHandler();
    }
    const handleDelete = (name: string, ) => {
        setTemplateName(name);
        setOpenDeleteOverlay(true)
    }

    return (
        <React.Fragment>
            <TableRow sx={{ '& > *': { borderBottom: 'unset' } }}>
                <TableCell component="th" scope="row" >
                    {row.name}
                </TableCell>

                <TableCell >
                </TableCell>

                <TableCell >
                </TableCell>
                <TableCell >
                </TableCell>
                <TableCell >
                </TableCell>
                <TableCell >
                </TableCell>
                <TableCell >
                </TableCell>

                <TableCell>
                    <IconButton aria-label="edit" size='small' onClick={() => handleEdit(row.name)}>
                    <EditIcon />
                    </IconButton>
                </TableCell>

                <TableCell>
                    <IconButton
                        onClick={() => handleDelete(row.name)}
                        aria-label="delete"
                        size='small'>
                        <DeleteIcon style={{ color: "red" }} />
                    </IconButton>
                </TableCell>


            </TableRow>
            {openEditOverlay && <SpreadsheetTemplateEditOverlay
                open={openEditOverlay}
                setOpen={setOpenEditOverlay}
                onClose={closeEditOverlayHandler}
                templateName={editingData.templateName}
                templateId = {row.id}
            />
            }

            {
                openDeleteOverlay && <DeleteTemplateOverlay
                    open={openDeleteOverlay}
                    setOpen={setOpenDeleteOverlay}
                    templateName={templateName}
                    templateId = {row.id}
                />
            }
        </React.Fragment>
    );
}



export default function CollapsibleTable() {
    const params = useParams()
    const fetcher = url => fetch(url).then(res => res.json());
    const { data: rows } = useSWR('/web/onlyoffice/'+params.project+'/spreadsheet_templates', fetcher);

    return (
        <TableContainer component={Paper} className="mt-4">
            <Table aria-label="collapsible table">
                <TableHead>
                    <TableRow>
                        <TableCell>Template Name</TableCell>
                        <TableCell />
                        <TableCell />
                        <TableCell />
                        <TableCell />
                        <TableCell />
                        <TableCell />
                        <TableCell />
                        <TableCell />

                    </TableRow>
                </TableHead>
                <TableBody>
                    {rows ? rows.results.map((row) => (
                        <Row key={row.name} row={row} />
                    )): null}
                </TableBody>
            </Table>
        </TableContainer>
    );
}
