import Button from '@mui/material/Button';
import Dialog from '@mui/material/Dialog';
import DialogActions from '@mui/material/DialogActions';
import DialogContent from '@mui/material/DialogContent';
import DialogContentText from '@mui/material/DialogContentText';
import DialogTitle from '@mui/material/DialogTitle';
import TextField from '@mui/material/TextField';
import * as React from 'react';
import {useEffect, useState} from 'react';
import {useNavigate, useParams} from "react-router-dom";
import useSWR from "swr";
import axios from "axios";
import Autocomplete from "@mui/material/Autocomplete";
import {LoadingButton} from "@mui/lab";
import {OutlinedInput, Typography} from "@mui/material";


export default function TransferProject({
                                            open,
                                            setOpen,
                                            projectName,
                                        }) {
    const [email, setEmail] = useState("");
    const [saving, setSaving] = useState(false);
    const [name, setName] = useState('');

    const [error, setError] = useState(false);
    const [errorMessage, setErrorMessage] = useState('');
    const [inputTouched, setInputTouched] = useState(false);

    const params = useParams();

    const fetcher = url => fetch(url).then(res => res.json());


    const {data: userlist} = useSWR("/web/userlist", fetcher);
    const navigate = useNavigate();

    const transferProject = () => {
        setSaving(true);
        let user = userlist.find(u => u.email === email);
        axios.post(`/web/projects/${params.project}/owner`, {
            userId: user.id,
        }).then(res => {
            setOpen(false);
            setSaving(false)
            navigate('/')
        })
    }

    const handleChange = (e) => {
        setName(e.target.value);
        if (error) {
            setError(false);
        }
    }


    useEffect(() => {
        let user = (userlist) ? userlist.find(u => u.email === email) : null
        if (name.length === 0) {
            setError(true);
            setErrorMessage('Email address is required');
        } else if (!user) {
            setError(true)
            setErrorMessage("No user with this email address found")
        } else if (name.length > 0 && name !== projectName) {
            setError(true);
            setErrorMessage('Project name mismatch');
        } else if (name === email) {
            setError(false)
            setErrorMessage('')
        }
    }, [name, email, inputTouched]);

    return (
        <>
            <Dialog
                open={open}
                onClose={() => setOpen(false)}
            >
                <DialogTitle>
                    Transfer project "{projectName}" to a new user.
                </DialogTitle>
                <DialogContent>
                    <Typography variant="subtitle2" mt={2} mb={1}>Select user.</Typography>
                    <Autocomplete
                        freeSolo
                        autoHighlight
                        disableClearable
                        options={userlist ? userlist.map((f) => f.email) : []}
                        renderInput={(params) => <TextField {...params} variant="filled"
                                                            hiddenLabel placeholder="Select user"
                                                            onChange={(e) => setEmail(e.target.value)}/>}
                        value={email}
                        onChange={(e, nv) => setEmail(nv)}
                        disabled={saving}
                        // onKeyDown={(e) => (e.key === 'Enter') ? inviteUser() : null}
                    />
                    <Typography variant="subtitle2" mt={2} mb={1}>Enter the project name to confirm the
                        transfer.</Typography>
                    <OutlinedInput
                        label='Project name'
                        fullWidth
                        notched={false}
                        onFocus={() => setInputTouched(true)}
                        value={name}
                        error={error && inputTouched}
                        name='name'
                        onChange={handleChange}
                        placeholder='Enter project name'/>
                    {inputTouched && error && < Typography variant="subtitle1" style={{
                        color: 'red',
                        fontSize: '12px'
                    }}>{errorMessage}</Typography>}
                    <Typography variant="subtitle2" mt={2} mb={1}>This action may take up to one be.</Typography>

                </DialogContent>
                <DialogActions>
                    <Button onClick={() => setOpen(false)}>Cancel</Button>
                    <LoadingButton color="success" loading={saving} onClick={transferProject}
                                   disabled={error}>
                        Transfer project
                    </LoadingButton>
                </DialogActions>
            </Dialog>
        </>
    )
}