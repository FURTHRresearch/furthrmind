import * as React from 'react';
import Header from "../components/Header/Header";
import styles from "./AdminPanelPage.module.css";
import classes from "./AdminPanelPage.module.css";

import AddIcon from '@mui/icons-material/Add';
import CheckBoxIcon from '@mui/icons-material/CheckBox';
import CheckBoxOutlineBlankIcon from '@mui/icons-material/CheckBoxOutlineBlank';
import DeleteIcon from '@mui/icons-material/Delete';
import EditIcon from '@mui/icons-material/Edit';
import GroupsIcon from '@mui/icons-material/Groups';
import PersonIcon from '@mui/icons-material/Person';
import Autocomplete from '@mui/material/Autocomplete';
import Avatar from "@mui/material/Avatar";
import Box from '@mui/material/Box';
import Checkbox from '@mui/material/Checkbox';
import Dialog from '@mui/material/Dialog';
import DialogActions from '@mui/material/DialogActions';
import DialogContent from '@mui/material/DialogContent';
import DialogTitle from '@mui/material/DialogTitle';
import FormControlLabel from '@mui/material/FormControlLabel';
import Grid from '@mui/material/Grid';
import IconButton from '@mui/material/IconButton';
import Paper from '@mui/material/Paper';
import Stack from '@mui/material/Stack';
import Tab from '@mui/material/Tab';
import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableContainer from '@mui/material/TableContainer';
import TableHead from '@mui/material/TableHead';
import TableRow from '@mui/material/TableRow';
import Tabs from '@mui/material/Tabs';
import TextField from '@mui/material/TextField';
import Tooltip from '@mui/material/Tooltip';

import axios from "axios";

import useSWR from "swr";

import {LoadingButton} from "@mui/lab";
import {Chip} from '@mui/material';
import Button from '@mui/material/Button';
import DeleteUser from "../components/Overlays/DeleteUser";
import {useState} from "react";

const fetcher = (url) => fetch(url).then((res) => res.json());

const AdminPanelPage = () => {
    const [currentTab, setCurrentTab] = React.useState(0);
    const [showAddUserModal, setShowAddUserModal] = React.useState(false);
    const [showAddGroupModal, setShowAddGroupModal] = React.useState(false);
    const [creating, setCreating] = React.useState(false);

    return (
        <div className={styles.pageStyle}>
            <Header/>
            <div className={styles.pageInnerWrapper} style={{padding: '30px 0'}}>
                <Paper style={{padding: '16px 32px'}}>
                    <Stack direction='row' justifyContent='space-between'>
                        <div className={classes.titleText}>Admin Setting</div>
                        {currentTab === 0 && <LoadingButton
                            startIcon={<AddIcon/>}
                            variant="outlined"
                            loading={creating}
                            disabled={showAddUserModal}
                            onClick={() => setShowAddUserModal(true)}
                            color="primary">ADD USER</LoadingButton>
                        }
                        {currentTab === 1 && <LoadingButton
                            startIcon={<AddIcon/>}
                            variant="outlined"
                            loading={creating}
                            disabled={showAddGroupModal}
                            onClick={() => setShowAddGroupModal(true)}
                            color="primary">ADD GROUP</LoadingButton>
                        }
                    </Stack>
                    <Box sx={{borderBottom: 1, borderColor: 'divider'}}>
                        <Tabs value={currentTab} onChange={(e, val) => setCurrentTab(val)}
                              style={{paddingBottom: '12px'}}>
                            <Tab icon={<PersonIcon/>} label="User List"/>
                            <Tab icon={<GroupsIcon/>} label="Group List"/>
                            {/* <Tab icon={<SettingsIcon />} label="Settings" /> */}
                        </Tabs>
                    </Box>
                    {currentTab === 0 && <UsersTable showAddUserModal={showAddUserModal}
                                                     setShowAddUserModal={setShowAddUserModal}
                                                     setCreating={setCreating}
                    />}
                    {currentTab === 1 && <UserGroups
                        showAddGroupModal={showAddGroupModal}
                        setShowAddGroupModal={setShowAddGroupModal}
                        setCreating={setCreating}
                    />}
                    {currentTab === 2 && 'Coming soon.'}
                </Paper>
            </div>
        </div>
    )
};

export default AdminPanelPage;

function UserGroups(props) {
    const {showAddGroupModal, setShowAddGroupModal, setCreating} = props
    const {data: groups, mutate: mutateGroups} = useSWR('/web/admin/usergroups', fetcher);
    const {data: users} = useSWR("/web/admin/users", fetcher);

    const options = React.useMemo(() => {
        return users ? users.map(u => u.id) : [];
    }, [users]);

    const getUserName = (id) => {
        return users ? users.find(u => u.id === id)?.email : "";
    }

    const newGroup = () => {
        let name = window.prompt('Enter group name');
        if (!name) {
            setShowAddGroupModal(false);
            return;
        }
        setCreating(true);
        axios.post('/web/admin/usergroups', {name}).then((r) => {
            mutateGroups([...groups, {id: r.data.id, name, users: []}]);
            setCreating(false);
            setShowAddGroupModal(false);
        });
    }

    const saveGroupMembers = (id, val) => {
        axios.post(`/web/admin/usergroups/${id}`, {users: val});
    }

    const deleteGroup = (id) => {
        if (window.confirm('Are you sure you want to delete this group?')) {
            axios.delete(`/web/admin/usergroups/${id}`).then(() => {
                mutateGroups(groups.filter(g => g.id !== id));
            });
        }
    }

    React.useEffect(() => {
        if (showAddGroupModal) {
            newGroup();
        }
    }, [showAddGroupModal])

    return (
        <>
            {groups && groups.map((group) => (
                <Paper sx={{padding: '24px', margin: '24px 0'}}>
                    <IconButton sx={{float: 'right'}} onClick={() => deleteGroup(group.id)}><DeleteIcon/></IconButton>
                    <h2>{group.name}</h2>
                    <Autocomplete
                        multiple
                        onChange={(e, val) => saveGroupMembers(group.id, val)}
                        options={options}
                        disableCloseOnSelect
                        disableClearable
                        defaultValue={group.users}
                        getOptionLabel={(option: any) => getUserName(option)}
                        renderOption={(props, option: any, {selected}) => (
                            <li {...props}>
                                <Checkbox
                                    icon={<CheckBoxOutlineBlankIcon fontSize="small"/>}
                                    checkedIcon={<CheckBoxIcon fontSize="small"/>}
                                    style={{marginRight: 8}}
                                    checked={selected}
                                />
                                {getUserName(option)}
                            </li>
                        )}
                        renderInput={(params) => (
                            <TextField {...params} label="Group members"/>
                        )}
                    />
                </Paper>
            ))}
        </>
    )
}

function UsersTable(props) {
    const {showAddUserModal, setShowAddUserModal, setCreating} = props
    const [showDeleteModal, setShowDeleteModal] = useState(false);
    const [userId, setUserId] = useState("")
    const [email, setEmail] = useState("")

    const {data: rows, mutate: mutateUsers} = useSWR("/web/admin/users", fetcher);
    const [editing, setEditing] = React.useState(false);


    const deleteUser = (id) => {
        const currentUser = rows?.find(u => u.id === id);
        setEmail(currentUser.email)
        setUserId(id)
        setShowDeleteModal(true)
    }

    const newUser = () => {
        let email = window.prompt('Enter email');
        if (!email) {
            setShowAddUserModal(false);
            return;
        }
        setCreating(true);
        axios.post('/web/admin/users', {email}).then((r) => {
            mutateUsers([...rows, {id: r.data.id, email}]);
            setCreating(false);
            setEditing(r.data.id);
            setShowAddUserModal(false);
        }).catch((e) => {
            alert("This email address is already in use");
            setShowAddUserModal(false);
            setCreating(false);
        });
    }

    React.useEffect(() => {
        if (showAddUserModal) {
            newUser();
        }
    }, [showAddUserModal]);

    function stringToColor(string) {
        string = string || '';
        let hash = 0;
        let i;

        /* eslint-disable no-bitwise */
        for (i = 0; i < string.length; i += 1) {
            hash = string.charCodeAt(i) + ((hash << 5) - hash);
        }

        let color = '#';

        for (i = 0; i < 3; i += 1) {
            const value = (hash >> (i * 8)) & 0xff;
            color += `00${value.toString(16)}`.slice(-2);
        }
        /* eslint-enable no-bitwise */

        return color;
    }

    function stringAvatar(name) {
        return {
            sx: {
                bgcolor: stringToColor(name),
            },
            children: name
        };
    }

    return (
        <Box mt={3}>

            <Paper sx={{mb: 2, width: '100%'}}>
                <TableContainer>
                    <Table>
                        <TableHead>
                            <TableRow>
                                <TableCell align='right'></TableCell>
                                <TableCell align='left'>Name</TableCell>
                                <TableCell align='left'>Email</TableCell>
                                <TableCell align='left'>Status</TableCell>
                                <TableCell align='left'>User Type</TableCell>
                                <TableCell></TableCell>
                            </TableRow>
                        </TableHead>
                        <TableBody>
                            {rows && rows.map(row =>
                                <TableRow
                                    hover
                                    key={row.id}
                                    onClick={() => setEditing(row.id)}
                                >
                                    <TableCell align='right'>
                                        <Avatar
                                            sx={{
                                                width: 20,
                                                height: 20,
                                                fontSize: "12px",
                                            }}
                                            src={row?.avatar}
                                            {...stringAvatar(row?.email)}
                                        >
                                            {row?.email?.charAt(0).toUpperCase()}
                                        </Avatar>
                                    </TableCell>
                                    <TableCell align="left">{row.firstName} {row.lastName}</TableCell>
                                    <TableCell align="left">{row.email}</TableCell>
                                    <TableCell align="left">
                                        <Chip
                                            label="Active" color="primary" variant="outlined"/>
                                    </TableCell>
                                    <TableCell align="left">{row.admin ? 'Admin' : 'User'}</TableCell>
                                    <TableCell align="right">
                                        <Tooltip title="Delete">
                                            <IconButton onClick={(e) => {
                                                e.stopPropagation();
                                                deleteUser(row.id)
                                            }}>
                                                <DeleteIcon/>
                                            </IconButton>
                                        </Tooltip>
                                        <Tooltip title="Edit">
                                            <IconButton onClick={(e) => {
                                                e.stopPropagation();
                                                setEditing(row.id)
                                            }}>
                                                <EditIcon/>
                                            </IconButton>
                                        </Tooltip>
                                    </TableCell>
                                </TableRow>
                            )}
                        </TableBody>
                    </Table>
                </TableContainer>
            </Paper>
            <EditUserOverlay open={editing} id={editing} onClose={() => setEditing(false)}/>
            {showDeleteModal && <DeleteUser open={showDeleteModal} setOpen={setShowDeleteModal}  email={email} userId={userId}
                                 users={rows} mutateUsers={mutateUsers}/>}

        </Box>
    );
}

function EditUserOverlay({open, id, onClose}) {
    const [loading, setLoading] = React.useState(false);
    const [user, setUser] = React.useState<any>();
    const [password, setPassword] = React.useState('');
    const [passwordConfirm, setPasswordConfirm] = React.useState('');
    const {data: users, mutate: mutateUsers} = useSWR("/web/admin/users", fetcher);
    const {
        data: supervisors,
        mutate: mutateSupervisors
    } = useSWR(id ? `/web/admin/users/${id}/supervisors` : false, fetcher);

    const currentUser = users?.find(u => u.id === id);

    React.useEffect(() => {
        if (open) {
            setUser(currentUser);
            setPassword('');
            setPasswordConfirm('');
        }
    }, [currentUser, open]);

    const saveUser = () => {
        setLoading(true);
        let payload = user;
        payload.supervisors = supervisors;
        if (password && password === passwordConfirm) payload.password = password;
        axios.post(`/web/admin/users/${id}`, payload).then(r => {
            setLoading(false);
            mutateUsers(users.map(u => u.id === id ? user : u));
            onClose();
        });
    }

    const updateSupervisors = (val) => {
        mutateSupervisors(val.map(s => s.id), false);
    }

    return (
        <>
            <Dialog open={open} onClose={onClose}>
                <DialogTitle>Edit user</DialogTitle>
                <div style={{marginTop: '0.2em'}}></div>
                {user && <DialogContent>
                    <Grid container spacing={2}>
                        <Grid item xs={6}>
                            <TextField
                                label="First name"
                                fullWidth
                                value={user.firstName}
                                onChange={(e) => setUser({...user, firstName: e.target.value})}
                            />
                        </Grid>
                        <Grid item xs={6}>
                            <TextField
                                label="Last name"
                                fullWidth
                                value={user.lastName}
                                onChange={(e) => setUser({...user, lastName: e.target.value})}
                            />
                        </Grid>
                        <Grid item xs={12}>
                            <TextField
                                label="Email address"
                                fullWidth
                                value={user.email}
                                onChange={(e) => setUser({...user, email: e.target.value})}
                            />
                        </Grid>
                        <Grid item xs={6}>
                            <TextField
                                label="Password"
                                type="password"
                                placeholder="(unchanged)"
                                fullWidth
                                error={password !== passwordConfirm}
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                            />
                        </Grid>
                        <Grid item xs={6}>
                            <TextField
                                label="Password confirm"
                                type="password"
                                placeholder="(unchanged)"
                                fullWidth
                                error={password !== passwordConfirm}
                                value={passwordConfirm}
                                onChange={(e) => setPasswordConfirm(e.target.value)}
                            />
                        </Grid>
                        <Grid item xs={12}>
                            <FormControlLabel control={<Checkbox checked={user.admin} onChange={e => setUser({
                                ...user,
                                admin: e.target.checked
                            })}/>} label="Admin"/>
                        </Grid>
                        <Grid item xs={12}>
                            <Autocomplete
                                multiple
                                onChange={(e, val) => updateSupervisors(val)}
                                options={users}
                                disableCloseOnSelect
                                disableClearable
                                value={supervisors ? users.filter(u => supervisors.find(s => s === u.id)) : []}
                                getOptionLabel={(option: any) => option.email}
                                renderOption={(props, option: any, {selected}) => (
                                    <li {...props}>
                                        <Checkbox
                                            icon={<CheckBoxOutlineBlankIcon fontSize="small"/>}
                                            checkedIcon={<CheckBoxIcon fontSize="small"/>}
                                            style={{marginRight: 8}}
                                            checked={selected}
                                        />
                                        {option.email}
                                    </li>
                                )}
                                renderInput={(params) => (
                                    <TextField {...params} label="Direct supervisors"/>
                                )}
                            />
                        </Grid>
                    </Grid>
                </DialogContent>}
                <DialogActions>
                    <Button onClick={onClose} disabled={loading}>Close</Button>
                    <LoadingButton loading={loading} onClick={saveUser} color="success"
                                   disabled={password !== passwordConfirm}>Save</LoadingButton>
                </DialogActions>
            </Dialog>
        </>
    );
}