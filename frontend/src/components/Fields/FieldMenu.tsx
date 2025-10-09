import EditIcon from '@mui/icons-material/Edit';
import MoreVertIcon from "@mui/icons-material/MoreVert";
import LoadingButton from '@mui/lab/LoadingButton';
import {IconButton, Menu, MenuItem} from "@mui/material";
import Button from '@mui/material/Button';
import TextField from '@mui/material/TextField';
import axios from 'axios';

import Dialog from '@mui/material/Dialog';
import DialogActions from '@mui/material/DialogActions';
import DialogContent from '@mui/material/DialogContent';
import DialogContentText from '@mui/material/DialogContentText';
import DialogTitle from '@mui/material/DialogTitle';

import React, {useCallback, useEffect} from "react";
import ViewAuthorOverlay from '../Overlays/ViewAuthorOverlay';

import {useParams} from "react-router-dom";
import useSWR from "swr";
import PersonIcon from "@mui/icons-material/Person";
import Divider from "@mui/material/Divider";
import DeleteIcon from "@mui/icons-material/Delete";
import debounce from "lodash/debounce";
import Typography from "@mui/material/Typography";

const FieldMenu = (props) => {
    const [anchorEl, setAnchorEl] = React.useState<null | HTMLElement>(null);
    const [deleteDialogOpen, setDeleteDialogOpen] = React.useState(false);
    const [renameDialogOpen, setRenameDialogOpen] = React.useState(false);

    const [viewAuthorOverlay, setViewAuthorOverlay] = React.useState(false);
    const closeViewAuthorOverlayHandler = () => {
        setViewAuthorOverlay(false);
    }
    return (
        <>
            <IconButton
                size="small"
                disabled={!props.writable}
                onClick={(event) => setAnchorEl(event.currentTarget)}
                sx={{
                    opacity: 0.5,
                    marginRight: '-12px'
                }}
            >
                <MoreVertIcon/>
            </IconButton>
            <Menu
                anchorEl={anchorEl}
                open={Boolean(anchorEl)}
                onClose={() => setAnchorEl(null)}
                onClick={() => setAnchorEl(null)}
            >

                {props.children}
                {props.parentType &&
                    <MenuItem onClick={() => setRenameDialogOpen(true)} disabled={!props.admin}>
                        <span><EditIcon/> Rename field</span>
                    </MenuItem>
                }
                {props.parentType &&
                    <MenuItem onClick={() => setDeleteDialogOpen(true)}>
                        <span style={{color: "red"}}><DeleteIcon/> Remove field</span>
                    </MenuItem>}
                <Divider/>
                <MenuItem onClick={() => setViewAuthorOverlay(true)}>
                    <span><PersonIcon/> Author details</span>
                </MenuItem>
            </Menu>
            <DeleteDialog {...props} handleClose={() => setDeleteDialogOpen(false)} open={deleteDialogOpen}/>
            <RenameDialog {...props} handleClose={() => setRenameDialogOpen(false)} open={renameDialogOpen}/>
            {viewAuthorOverlay && <ViewAuthorOverlay open={viewAuthorOverlay}
                                                     onClose={closeViewAuthorOverlayHandler}
                                                     authorId={props.authorId}
                                                     fieldId={props.fieldId}
            />

            }
        </>
    )
}

export default FieldMenu;

const DeleteDialog = ({open, handleClose, label, fieldDataId, parentId, parentType}) => {
    const [loading, setLoading] = React.useState(false);
    const params = useParams();
    
    React.useEffect(() => {
        setLoading(false);
    }, [open]);

    let url = `/web/item/${parentType}/${parentId}`
    if (parentType === "comboboxentries") {
        url = `/web/${parentType}/${parentId}`
    }

    const {data, mutate} =
        useSWR(url, (url) => fetch(url).then((res) => res.json()));
    const deleteItem = () => {
        setLoading(true);
        mutate({...data, fields: data.fields.filter((field) => field.id !== fieldDataId)}, false);
        // axios.post(`/web/item/${parentType}/${parentId}`,
        //     {fields: data.fields.filter((field) => field.id !== fieldDataId).map(f => f.id)}).then(() => {
        //     handleClose();
        // });
        axios.delete(`/web/projects/{${params.project}}/fielddata/${fieldDataId}`).then(() => {
            handleClose();
        });
    }
    return (
        <Dialog open={open} onClose={handleClose}>
            <DialogTitle>Remove {label} field?</DialogTitle>
            <DialogContent>

                <DialogContentText>
                    This will remove the field from your research item. Stored data is deleted. Other research items
                    will not be affected.
                </DialogContentText>

            </DialogContent>
            <DialogActions>
                <Button onClick={handleClose} disabled={loading}>Cancel</Button>
                <LoadingButton loading={loading} onClick={deleteItem} color="warning">Remove</LoadingButton>
            </DialogActions>
        </Dialog>
    )
}

const RenameDialog = ({open, handleClose, label, fieldDataId, fieldId, parentId, parentType}) => {
    const [loading, setLoading] = React.useState(false);
    const [loadingNameCheck, setLoadingNameCheck] = React.useState(false);
    const [newLabel, setNewLabel] = React.useState(label);
    const [check, setCheck] = React.useState(false)
    React.useEffect(() => {
        setLoading(false);
    }, [open]);
    
    let url = `/web/item/${parentType}/${parentId}`
    if (parentType === "comboboxentries") {
        url = `/web/${parentType}/${parentId}`
    }
    const {mutate} =
        useSWR(url, (url) => fetch(url).then((res) => res.json()));

    const params = useParams();

    const {
        data: fields,
        mutate: mutateFields
    } = useSWR(`/web/projects/${params.project}/fields`, (url) => fetch(url).then((res) => res.json()));

    const rename = () => {
        setLoading(true);
        axios.patch(`/web/fields/${fieldId}`, {name: newLabel}).then(() => {
            mutate();
            mutateFields(fields.map(f => f.id === fieldId ? {...f, name: newLabel} : f));
            setLoading(false);
            handleClose();
        });
    }

    function checkName(nameToBeChecked) {
        axios.post(`/web/field/${fieldId}/check`, {name: nameToBeChecked}).then((r) => {
            if (r.data == "True") {
                setCheck(true)
            } else {
                setCheck(false)
            }
            setLoadingNameCheck(false)
        })
    }

    const debouncedCheck = useCallback(debounce(checkName, 200), []);

    useEffect(() => {
        if (newLabel === "") {
            setCheck(false)
            return;
        } else if (newLabel === label){
            setCheck(true)
            return;
        }else {
            setLoadingNameCheck(true)
            debouncedCheck(newLabel)
        }

    }, [newLabel]);

    return (
        <Dialog open={open} onClose={handleClose}>
            <DialogTitle>Rename {label} field</DialogTitle>
            <DialogContent>

                <DialogContentText>
                    This will rename the field for all research items in the project. Changes take effect after the page
                    is reloaded.
                </DialogContentText>
                <TextField
                    autoFocus
                    margin="dense"
                    label="Name"
                    fullWidth
                    variant="standard"
                    value={newLabel}
                    onChange={(e) => setNewLabel(e.target.value)}
                />
                {!check && newLabel && !loadingNameCheck && < Typography style={{
                    color: 'red',
                    fontSize: '14px'
                }}>Name already in use. Please choose another one.</Typography>}

            </DialogContent>
            <DialogActions>
                <Button onClick={handleClose} disabled={loading}>Cancel</Button>
                <LoadingButton loading={loading} onClick={rename} disabled={!check || loadingNameCheck}>Rename </LoadingButton>
            </DialogActions>
        </Dialog>
    )
}

