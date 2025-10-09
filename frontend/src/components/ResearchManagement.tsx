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
import ResearchManagementEditOverlay from './Overlays/ResearchManagementEditOverlay';
import ResearchManagementCreateOverlay from './Overlays/ResearchManagementCreateOverlay';
import DeleteCategoryManagementOverlay from './Overlays/DeleteCategoryManagement';
import axios from "axios";
import {useParams} from "react-router-dom";
import classes from "./ProjectPermissionList.module.css";
import {Button} from "@mui/material";
import AddIcon from "@mui/icons-material/Add";
import useSWR from "swr";

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
        mutate: mutateResearchCategory
    } = useSWR('/web/projects/' + params.project + '/categories', fetcher);

    const [open, setOpen] = React.useState(false);
    const [openEditOverlay, setOpenEditOverlay] = React.useState(false);


    const [openDeleteOverlay, setOpenDeleteOverlay] = React.useState(false);
    const [editingData, setEditingData] = React.useState({
        categoryName: '',
        categoryDesc: ''
    })

    const openEditOverlayHandler = () => {
        setOpenEditOverlay(true);
    }

    const closeEditOverlayHandler = () => {
        setOpenEditOverlay(false);
        setEditingData({
            categoryDesc: '',
            categoryName: ''
        })
    }

    const handleEdit = (name: string, description: string) => {
        setEditingData({
            categoryName: name,
            categoryDesc: description,
        });
        openEditOverlayHandler();
    }


    const handleDelete = (name: string, description: string) => {
        setEditingData({
            categoryName: name,
            categoryDesc: description,
        });
        setOpenDeleteOverlay(true)
    }

    return (
        <React.Fragment>
            <TableRow sx={{'& > *': {borderBottom: 'unset'}}}>
                <TableCell component="th" scope="row">
                    {row.name}
                </TableCell>
                <TableCell>{String(row.description).substr(0, 50)}
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

            {openEditOverlay && <ResearchManagementEditOverlay
                open={openEditOverlay}
                setOpen={setOpenEditOverlay}
                onClose={closeEditOverlayHandler}
                categoryName={editingData.categoryName}
                categoryDesc={editingData.categoryDesc}
                categoryId={row.categoryid}
                mutateResearchCategory={mutateResearchCategory}
                rows={rows}

            />
            }
            {
                openDeleteOverlay && <DeleteCategoryManagementOverlay
                    open={openDeleteOverlay}
                    setOpen={setOpenDeleteOverlay}
                    categoryName={row.name}
                    categoryId={row.id}
                    mutateResearchCategory={mutateResearchCategory}
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
        mutate: mutateResearchCategory
    } = useSWR('/web/projects/' + params.project + '/categories', fetcher);
    const [openCreateOverlay, setOpenCreateOverlay] = React.useState(false)
    const [creatingData, setCreatingData] = React.useState({
        categoryName: '',
        categoryDesc: ''
    })
    const [admin, setAdmin] = React.useState(false)

    axios.get("/web/permissions/" + params.project).then((r) => {
        if (r.data === "admin") {
            setAdmin(true)
        }
    })

    const handleCreate = (name: string, description: string) => {
        setCreatingData({
            categoryName: name,
            categoryDesc: description
        });
        setOpenCreateOverlay(false);
    }
    const closeCreateOverlayHandler = () => {
        setOpenCreateOverlay(false);
        setCreatingData({
            categoryDesc: '',
            categoryName: ''
        })
    }


    return (
        <TableContainer component={Paper} className="mt-4">
            <Table aria-label="collapsible table">
                <TableHead>
                    <TableRow>
                        <TableCell>Category Name</TableCell>
                        <TableCell>Category Description</TableCell>
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
                >Add research category</Button>

            </div>
            {openCreateOverlay && <ResearchManagementCreateOverlay
                open={openCreateOverlay}
                onClose={closeCreateOverlayHandler}
                categoryName={creatingData.categoryName}
                categoryDesc={creatingData.categoryDesc}
                mutateResearchCategory={mutateResearchCategory}
                rows={rows}
            />
            }

        </TableContainer>
    );
}

