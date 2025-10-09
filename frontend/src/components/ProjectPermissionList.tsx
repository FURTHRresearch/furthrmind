import AddIcon from '@mui/icons-material/Add';
import CloseIcon from '@mui/icons-material/Close';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import SaveIcon from '@mui/icons-material/Save';
import {LoadingButton} from '@mui/lab';
import {Button, Card, Checkbox, IconButton, TextField} from '@mui/material';
import Autocomplete from '@mui/material/Autocomplete';
import * as React from 'react';
import {useEffect, useMemo, useState} from 'react';
import {useParams} from 'react-router-dom';
import useSWR from 'swr';
import classes from './ProjectPermissionList.module.css';

import GroupIcon from '@mui/icons-material/Group';
import Dialog from '@mui/material/Dialog';
import DialogActions from '@mui/material/DialogActions';
import DialogContent from '@mui/material/DialogContent';
import DialogContentText from '@mui/material/DialogContentText';
import DialogTitle from '@mui/material/DialogTitle';
import axios from 'axios';
import Tooltip from "@mui/material/Tooltip";
import Typography from "@mui/material/Typography";

const fetcher = url => fetch(url).then(res => res.json());

const UserPermission = () => {
    const params = useParams();
    const [showInviteDialog, setShowInviteDialog] = useState(false);
    const [showAddGroupDialog, setShowAddGroupDialog] = useState(false);

    const {
        data: collaborators,
        mutate: mutateCollaborators
    } = useSWR(`/web/projects/${params.project}/collaborators`, fetcher);
    const {data: project} = useSWR(`/web/projects/${params.project}/settings`, fetcher);
    const {data: user} = useSWR("/web/user", fetcher);

    const canEdit = useMemo(() => {
        if (!user || !project || !collaborators) return false;
        if (user.id === project.owner) return true;
        let userPermission = collaborators.find(c => c.id === user.id);
        return userPermission && userPermission.invite
    }, [collaborators, user, project]);

    const handleSave = (id, permission) => {
        axios.post(`/permissions/${id}`, permission);
        if (permission.invite === true) {
            permission.read = true
            permission.write = true
            permission.delete = true
        }
        mutateCollaborators(collaborators.map(c => (c.permissionId === id) ? permission : c), false);
    }

    return (
        <Card
            sx={{padding: "18px 0px", marginTop: "20px"}}>
            <div
                className={classes.dataWrapper}
            >
                <div className={classes.dataHeader}>

                    <div>
                    </div>
                    <div>
                        <Typography>Read</Typography>
                    </div>
                    <div>
                        <Typography>Write</Typography>
                    </div>
                    <div>
                        <Typography>Delete</Typography>
                    </div>
                    <div>
                        <Tooltip title={"Project admin have the following rights: Add user and user groups, change permissions of all collaborators, " +
                            "create/modify fields, units, and research categories"}>
                            <Typography>Project admin</Typography>
                        </Tooltip>
                    </div>
                    <div></div>
                </div>
                <div className={classes.dataFeedWrapper}>
                    {project && (
                        <div className={classes.dataCss}>
                            <div>
                                <Typography sx={{marginLeft:"20px"}}>{project.ownerEmail} (Owner)</Typography>

                            </div>
                            {[...Array(4)].map(e =>
                                <div><Checkbox checked={true} disabled={true}/></div>
                            )}
                            <div>
                            </div>
                        </div>
                    )}
                    {collaborators && project && collaborators.map((data) => data.id !== project.owner ? <DataRow
                        email={data.type === 'user' ? data.email : <> <GroupIcon/> {data.name}</>}
                        key={data.id}
                        initialPermission={data}
                        permissionId={data.permissionId}
                        savePermission={handleSave}
                        readOnly={!canEdit}
                        collaborators={collaborators}
                        mutateCollaborators={mutateCollaborators}
                    /> : null)}
                    <div className={classes.inviteUserBtn}>
                        <Button variant="text" startIcon={<AddIcon/>}
                                onClick={() => setShowInviteDialog(true)}
                                disabled={!canEdit}
                        >Invite User</Button>
                        <Button variant="text" startIcon={<AddIcon/>}
                                onClick={() => setShowAddGroupDialog(true)}
                                disabled={!canEdit}
                        >Add User Group</Button>
                    </div>
                </div>
            </div>
            {showInviteDialog && <InviteDialog open={true} onClose={() => setShowInviteDialog(false)}/>}
            {showAddGroupDialog && <AddGroupDialog open={true} onClose={() => setShowAddGroupDialog(false)}/>}
        </Card>
    )
}

function AddGroupDialog({
                            open,
                            onClose,
                        }) {
    const [name, setName] = useState("");
    const [saving, setSaving] = useState(false);

    const params = useParams();
    const {
        data: collaborators,
        mutate: mutateCollaborators
    } = useSWR(`/web/projects/${params.project}/collaborators`, fetcher);

    const {data: groups, mutate: mutateGroups} = useSWR("/web/usergroups", fetcher);

    const addGroup = () => {
        setSaving(true);
        let group = groups.find(g => g.name === name);
        axios.post(`/web/projects/${params.project}/collaborators`, {
            groupId: group.id,
        }).then(res => {
            // mutateCollaborators([...collaborators,
            // { id: user.id, email: user.email, read: true, write: false, invite: false, delete: false }]);
            onClose();
        })
    }

    return (
        <>
            <Dialog
                open={open}
                onClose={onClose}
            >
                <DialogTitle>
                    Invite a user group to your project
                </DialogTitle>
                <DialogContent>
                    <Autocomplete
                        autoHighlight
                        disableClearable
                        options={groups ? groups.map((f) => f.name) : []}
                        renderInput={(params) => <TextField {...params} variant="filled"
                                                            hiddenLabel placeholder="Add group"/>}
                        value={name}
                        onChange={(e, nv) => setName(nv)}
                        disabled={saving}
                        onKeyDown={(e) => (e.key === 'Enter') ? addGroup() : null}
                    />
                </DialogContent>
                <DialogActions>
                    <Button onClick={onClose}>Cancel</Button>
                    <LoadingButton color="success" loading={saving} onClick={addGroup}>
                        Add Group
                    </LoadingButton>
                </DialogActions>
            </Dialog>
        </>
    )
}

function InviteDialog({
                          open,
                          onClose,
                      }) {
    const [email, setEmail] = useState("");
    const [saving, setSaving] = useState(false);

    const params = useParams();
    const {
        data: collaborators,
        mutate: mutateCollaborators
    } = useSWR(`/web/projects/${params.project}/collaborators`, fetcher);

    const {data: userlist} = useSWR("/web/userlist", fetcher);

    const inviteUser = () => {
        setSaving(true);
        let user = userlist.find(u => u.email === email);
        axios.post(`/web/projects/${params.project}/collaborators`, {
            userId: user.id,
        }).then(res => {
            mutateCollaborators([...collaborators,
                {id: user.id, email: user.email, read: true, write: false, invite: false, delete: false}]);
            onClose();
        })
    }

    return (
        <>
            <Dialog
                open={open}
                onClose={onClose}
            >
                <DialogTitle>
                    Invite an existing user to your project.
                </DialogTitle>
                <DialogContent>
                    <DialogContentText>
                        Please enter the email address of the user you want to invite.
                    </DialogContentText>
                    <Autocomplete
                        freeSolo
                        autoHighlight
                        disableClearable
                        options={userlist ? userlist.map((f) => f.email) : []}
                        renderInput={(params) => <TextField {...params} variant="filled"
                                                            hiddenLabel placeholder="Invite user"/>}
                        value={email}
                        onChange={(e, nv) => setEmail(nv)}
                        disabled={saving}
                        // onKeyDown={(e) => (e.key === 'Enter') ? inviteUser() : null}
                    />
                </DialogContent>
                <DialogActions>
                    <Button onClick={onClose}>Cancel</Button>
                    <LoadingButton color="success" loading={saving} onClick={inviteUser}>
                        Invite user
                    </LoadingButton>
                </DialogActions>
            </Dialog>
        </>
    )
}

const DataRow = ({
                     email,
                     initialPermission,
                     permissionId,
                     savePermission,
                     readOnly,
                     collaborators,
                     mutateCollaborators
                 }) => {
    const [editMode, setEditMode] = useState(false);
    const [permission, setPermission] = useState(initialPermission);
    const [openDeleteDialog, setOpenDeleteDialog] = useState(false);

    useEffect(() => {
        if (editMode) return;
        setPermission(initialPermission);
    }, [editMode, initialPermission])


    return (
        <div className={classes.dataCss}>

            <div>
                <Typography sx={{marginLeft:"30px"}}>{email}</Typography>

            </div>
            <div>
                <Checkbox
                    checked={permission.read}
                    name="read"
                    disabled={!editMode}
                    onChange={(e) => setPermission({...permission, read: e.target.checked})}
                />
            </div>
            <div>
                <Checkbox
                    checked={permission.write}
                    name="write"
                    disabled={!editMode}
                    onChange={(e) => setPermission({...permission, write: e.target.checked})}
                />
            </div>
            <div>
                <Checkbox
                    checked={permission.delete}
                    name="delete"
                    disabled={!editMode}
                    onChange={(e) => setPermission({...permission, delete: e.target.checked})}
                />
            </div>
            <div>
                <Checkbox
                    checked={permission.invite}
                    name="admin"
                    disabled={!editMode}
                    onChange={(e) => setPermission({...permission, invite: e.target.checked})}
                />
            </div>
            <div>
                {editMode ?
                    <div className="d-flex align-items-center">
                        <SaveIcon
                            sx={{
                                fontSize: "20px",
                                cursor: "pointer"
                            }}
                            onClick={() => {
                                savePermission(permissionId, permission);
                                setEditMode(false)
                            }}
                        />
                        <CloseIcon
                            sx={{
                                marginLeft: "10px",
                                fontSize: "20px",
                                cursor: "pointer"
                            }}
                            onClick={() => setEditMode(false)}
                        />
                    </div> :
                    <div className="d-flex align-items-center">
                        <IconButton onClick={() => setEditMode(true)} disabled={readOnly} sx={{marginLeft: "-40px"}}>
                            <EditIcon fontSize='small'/>
                        </IconButton>
                        <IconButton onClick={() => setOpenDeleteDialog(true)} disabled={readOnly}>
                            <DeleteIcon fontSize='small'/>
                        </IconButton>
                        <DeleteDialog open={openDeleteDialog} handleClose={() => setOpenDeleteDialog(false)}
                                      label={"collaborator"} permissionId={permissionId} collaborators={collaborators}
                                      mutateColaborators={mutateCollaborators}/>
                        {/* <DeleteOutlineTwoToneIcon
                            sx={{
                                color: "red",
                                marginLeft: "10px",
                                fontSize: "20px",
                                cursor: "pointer"
                            }}
                            onClick={() => null}
                        /> */}
                    </div>
                }
            </div>
        </div>
    )
}
export default UserPermission


const DeleteDialog = ({open, handleClose, label, permissionId, collaborators, mutateColaborators}) => {
    const [loading, setLoading] = React.useState(false);
    React.useEffect(() => {
        setLoading(false);
    }, [open]);


    const deleteItem = () => {
        setLoading(true);

        axios.delete(`/web/permissions/${permissionId}`).then(() => {
            const dataCopy = []
            collaborators.map((c) => {
                if (c.permissionId !== permissionId) {
                    dataCopy.push(c)
                }
            })
            mutateColaborators(dataCopy)
            handleClose();
        });
    }
    return (
        <Dialog open={open} onClose={handleClose}>
            <DialogTitle>Remove {label}?</DialogTitle>
            <DialogContent>

                <DialogContentText>
                    This will remove the collaborator from this project.
                </DialogContentText>

            </DialogContent>
            <DialogActions>
                <Button onClick={handleClose} disabled={loading}>Cancel</Button>
                <LoadingButton loading={loading} onClick={deleteItem} color="warning">Remove</LoadingButton>
            </DialogActions>
        </Dialog>
    )
}