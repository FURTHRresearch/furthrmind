import Button from '@mui/material/Button';
import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';

import AddField from './Fields/AddField';

import Skeleton from '@mui/material/Skeleton';

import useSWR from 'swr';
import DraggableFields from './DraggableFields/draggableFields';

import React, {useCallback} from 'react';

import axios from 'axios';
import debounce from 'lodash.debounce';

import DeleteIcon from '@mui/icons-material/Delete';
import MoreVertIcon from '@mui/icons-material/MoreVert';
import LoadingButton from '@mui/lab/LoadingButton';
import Dialog from '@mui/material/Dialog';
import Box from '@mui/material/Box'
import DialogActions from '@mui/material/DialogActions';
import DialogContent from '@mui/material/DialogContent';
import DialogContentText from '@mui/material/DialogContentText';
import DialogTitle from '@mui/material/DialogTitle';
import IconButton from '@mui/material/IconButton';
import Menu from '@mui/material/Menu';
import MenuItem from '@mui/material/MenuItem';
import TextField from "@mui/material/TextField";

const GroupPropertiesCard = ({groupId, setCurrentGroup, groups, mutateGroups}) => {
    const {data, mutate} =
        useSWR(`/web/item/groups/${groupId}`, (url) => fetch(url).then((res) => res.json()));
    const fields = data?.fields;
    const fieldAdded = (field: any) => {
        mutate({...data, fields: [...data.fields, field]});
    }
    // eslint-disable-next-line
    const saveName = useCallback(debounce((name) => {
        axios.post(`/web/groups/${groupId}`, {name}).then((res) => {
            const groupsCopy = []
            groups.map((g) => {
                if (g.id === groupId) {
                    g.name = name
                }
                groupsCopy.push(g)
            })
            mutateGroups(groupsCopy, {revalidate:false})
        }).catch((r) => {
            alert("Name already used")
        });
    }, 1000), [groupId]);

    const nameChanged = (e: any) => {
        let name = e.target.value
        mutate({...data, name}, false);
        saveName(name);

    }

    const updateFieldOnDragEnd = (result, fields) => {
        const {
            destination: {index: destinationIndex},
            source: {index: sourceIndex},
        } = result;
        if (destinationIndex !== sourceIndex) {
            const newFields = fields.slice();
            newFields.splice(destinationIndex, 0, newFields.splice(sourceIndex, 1)[0]);
            mutate({...data, fields: newFields}, false);
            axios.put(`/web/groups/${groupId}/fields`, {'fieldDataIds': newFields.map(f => f.id)});
        }
    };

    const handleFieldValueChange = (id, val) => {
        const newFields = fields.map(f => {
            return (f.id === id) ? {...f, Value: val} : f;
        })
        mutate({...data, fields: newFields}, false);
    }

    const handleFieldUnitChange = (id, val) => {
        const newFields = fields.map(f => {
            return (f.id === id) ? {...f, UnitID: val} : f;
        })
        mutate({...data, fields: newFields}, false);
    }

    return (
        <>
            <Card variant="outlined" style={{
                backgroundColor: "#e8f0fe",
                boxShadow: "2px 4px 4px rgba(0, 0, 0, 0.25)", maxWidth: "500px", marginBottom: "20px"
            }}>
                <CardContent>
                    <Box display={"flex"} marginBottom={"20px"}>
                        {data ? <TextField
                            value={data.name}
                            label={"Name"}
                            onChange={nameChanged}
                            style={{width: '100%'}}
                        /> : <Skeleton variant="text" style={{width: "80%"}}/>}
                        <GroupMenu name={data ? data.name : ''} group={groupId}
                                   setCurrentGroup={setCurrentGroup}
                                   groups={groups} mutateGroups={mutateGroups}
                        />
                    </Box>


                    {!data ? [...Array(5)].map(e => <>
                            <Skeleton variant="text" width="30%"/>
                            <Skeleton variant="rectangular" height={30}/>
                        </>) :
                        <div>
                            <DraggableFields
                                fields={data.fields}
                                isParent={true}
                                parentID={data.id}
                                parentType="groups"
                                updateFieldOnDragEnd={updateFieldOnDragEnd}
                                onFieldValueChange={handleFieldValueChange}
                                onFieldUnitChange={handleFieldUnitChange}
                                controlled
                                writable={data.writable}
                                admin={data.admin}
                            />
                            <hr/>
                            <AddField onAdded={fieldAdded} target="groups" targetId={groupId}
                                      notebook={false} admin={data.admin}/>
                        </div>}
                </CardContent>
            </Card>
        </>
    );
}

export default GroupPropertiesCard;

const GroupMenu = (props) => {
    const [anchorEl, setAnchorEl] = React.useState<null | HTMLElement>(null);
    const open = Boolean(anchorEl);
    const handleClick = (event: React.MouseEvent<HTMLElement>) => {
        setAnchorEl(event.currentTarget);
    };
    const handleClose = () => {
        setAnchorEl(null);
    };

    const [showDeleteDialog, setShowDeleteDialog] = React.useState(false);

    return (
        <>
            <IconButton
                onClick={handleClick}
            >
                <MoreVertIcon/>
            </IconButton>
            <Menu
                anchorEl={anchorEl}
                open={open}
                onClose={handleClose}
            >
                <MenuItem onClick={() => {
                    setShowDeleteDialog(true);
                    handleClose()
                }}>
                    <span style={{color: "red"}}><DeleteIcon/> Delete</span>
                </MenuItem>
            </Menu>
            <DeleteDialog groupId={props.group} name={props.name} open={showDeleteDialog}
                          handleClose={() => setShowDeleteDialog(false)} setCurrentGroup={props.setCurrentGroup}
                          groups={props.groups} mutateGroups={props.mutateGroups}/>
        </>
    )
}

const DeleteDialog = ({open, handleClose, name, groupId, setCurrentGroup, groups, mutateGroups}) => {
    const [loading, setLoading] = React.useState(false);
    const deleteItem = () => {
        setLoading(true);
        axios.delete(`/web/groups/${groupId}`).then(() => {
            setCurrentGroup(null)
            const groupsCopy = []
            groups.map((g) => {
                if (g.id !== groupId) {
                    groupsCopy.push(g)
                }
            })
            mutateGroups(groupsCopy);
            handleClose();
        });
    }
    return (
        <Dialog open={open} onClose={handleClose}>
            <DialogTitle>Delete {name}?</DialogTitle>
            <DialogContent>

                <DialogContentText>Deleting the group potentially removes your access to all the contained research
                    items.</DialogContentText>

            </DialogContent>
            <DialogActions>
                <Button onClick={handleClose} disabled={loading}>Cancel</Button>
                <LoadingButton loading={loading} onClick={deleteItem} color="warning">Delete</LoadingButton>
            </DialogActions>
        </Dialog>
    )
}
