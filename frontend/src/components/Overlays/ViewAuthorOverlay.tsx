import { LoadingButton } from "@mui/lab";
import {FormControl, InputLabel, OutlinedInput, Select, Stack, Typography} from "@mui/material";
import Button from "@mui/material/Button";
import Dialog from "@mui/material/Dialog";
import DialogContent from "@mui/material/DialogContent";
import DialogTitle from "@mui/material/DialogTitle";
import { useTheme } from "@mui/material/styles";
import useMediaQuery from "@mui/material/useMediaQuery";
import React, { useEffect, useState } from "react";
import MenuItem from "@mui/material/MenuItem";
import {useParams} from "react-router-dom";
import axios from "axios";
import useSWR from "swr";
import CreateAuthorOverlay from "./CreateAuthorOverlay";
import AuthorEditOverlay from "./AuthorEditOverlay";

import AuthorDeleteOverlay from "./AuthorDeleteOverlay";
import DeleteIcon from '@mui/icons-material/Delete';
import EditIcon from '@mui/icons-material/Edit';
import TableCell from "@mui/material/TableCell";
import IconButton from "@mui/material/IconButton";
import AddIcon from "@mui/icons-material/Add";
import ResearchManagementCreateOverlay from "./ResearchManagementCreateOverlay";
import DeleteCategoryManagementOverlay from "./DeleteCategoryManagement";




export default function ViewAuthorOverlay({
    onClose: onCloseHandler,
    open,
    authorId,
    fieldId,
}) {
    const theme = useTheme();
    const fullScreen = useMediaQuery(theme.breakpoints.down("md"));
    const [openCreateOverlay, setOpenCreateOverlay] = useState(false)
    const [openEditOverlay, setOpenEditOverlay] = useState(false)

    const [openDeleteOverlay, setOpenDeleteOverlay] = useState(false)
    const [selectedAuthor, setSelectedAuthor] = useState('')

    const [updating, setUpdating] = useState(false);
    const [tempValue, setTempValue] = React.useState(authorId);
    const [creatingData, setCreatingData] = React.useState({
        authorName: '',
        authorInstitution: ''
    })
    const authorAdded = (author) => {
        //mutate({ ...data, fields: [...fields, field] }, false);
    };

    const handleUpdate = () => {
        setUpdating(true);
        axios.post(`/web/fielddata/setauthor`, {
            author: tempValue,
            fielddata: fieldId
        }).then(onCloseHandler);
    };

    const closeCreateOverlayHandler = () => {
        setOpenCreateOverlay(false);
        setCreatingData({
            authorInstitution: '',
            authorName: ''
        })
    }

    const closeEditOverlayHandler = () => {
        setOpenEditOverlay(false);
        setCreatingData({
            authorInstitution: '',
            authorName: ''
        })
    }

    const fetcher = url => fetch(url).then(res => res.json());
    const { data: authorsList } = useSWR('/web/author', fetcher);

    const getAuthorInformation = (e) => {
        setTempValue(e.target.value)
        authorsList != undefined && authorsList.map(author => {
            if (author['_id'] == e.target.value) {
                setSelectedAuthor(author)
            }
            }
        )



    }

    return (
        <div>
            <Dialog
                fullScreen={fullScreen}
                fullWidth
                open={open}
                onClose={onCloseHandler}
                aria-labelledby="responsive-dialog-title"
            >
                <DialogTitle style={{ fontWeight: 600 }}>Details</DialogTitle>
                <DialogContent>
                    <Typography variant="subtitle2" mt={2} mb={1}>
                        Author
          </Typography>
                    <Stack direction={{ xs: 'column', sm: 'row' }}
                           alignItems="center"
                           spacing = {1}>
                        <FormControl sx={{ m: 1, minWidth: 350 }} size="small">

                        <Select
                                value={tempValue}
                                variant="standard"
                                onChange={(e: any) => getAuthorInformation(e)}

                            >
                                {authorsList != undefined && authorsList.map((author) => (
                                    <MenuItem value={author['_id']} >{author.name} @ {author.institution}</MenuItem>

                                ))}


                            </Select>
                        </FormControl>


                                <IconButton
                                    onClick={() => setOpenEditOverlay(true)}
                                    aria-label="edit"
                                    size='small'>
                                    <EditIcon/>
                                </IconButton>

                                <IconButton
                                    onClick={() => setOpenDeleteOverlay(true)}
                                    aria-label="delete"
                                    size='small'>
                                    <DeleteIcon style={{color: "red"}}/>
                                </IconButton>

                                <Button variant="text" startIcon={<AddIcon/>}
                                    onClick={() => setOpenCreateOverlay(true)}
                                >add</Button>
                    </Stack>


                </DialogContent>
                {openCreateOverlay && <CreateAuthorOverlay
                    open={openCreateOverlay}
                    onClose={closeCreateOverlayHandler}
                    authorName={creatingData.authorName}
                    authorInstitution={creatingData.authorInstitution}

                />}
                {openDeleteOverlay && <AuthorDeleteOverlay
                    open={openDeleteOverlay}
                    setOpen={setOpenDeleteOverlay}
                    selectedAuthor = {selectedAuthor}
                    authorsList = {authorsList}
                />}
                {openEditOverlay && <AuthorEditOverlay
                    open={openEditOverlay}
                    onClose={closeEditOverlayHandler}
                    author = {selectedAuthor}

                />}
                <div
                    style={{
                        display: "flex",
                        justifyContent: "flex-end",
                        padding: "16px",
                        marginRight: "10px",
                    }}
                >
                        <Stack direction="row">
                            <Button
                                autoFocus
                                onClick={onCloseHandler}
                                sx={{ color: "#707070", padding: "12px 16px" }}
                            >
                                Cancel
              </Button>
                            <LoadingButton
                                loading={updating}
                                onClick={handleUpdate}
                                autoFocus
                                sx={{ padding: "12px 16px" }}
                            >
                                Ok
              </LoadingButton>
                        </Stack>

                </div>
            </Dialog>
        </div>
    );
}
