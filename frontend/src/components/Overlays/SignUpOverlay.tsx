import LoadingButton from '@mui/lab/LoadingButton';
import Button from '@mui/material/Button';
import Dialog from '@mui/material/Dialog';
import DialogActions from '@mui/material/DialogActions';
import DialogContent from '@mui/material/DialogContent';
import DialogContentText from '@mui/material/DialogContentText';
import DialogTitle from '@mui/material/DialogTitle';
import Grid from '@mui/material/Grid';
import InputAdornment from '@mui/material/InputAdornment';
import TextField from '@mui/material/TextField';
import CheckMark from '../AnimatedSymbols/CheckMark';

import axios from 'axios';
import React, { useEffect } from "react";
import useSWR from 'swr';

const fetcher = (url: string) => axios.get(url).then(res => res.data);

const SignUpDialog = ({open, handleClose}) => {
    const [loading, setLoading] = React.useState(false);
    const [complete, setComplete] = React.useState(false);
    const [email, setEmail] = React.useState('');
    const [firstName, setFirstName] = React.useState('');
    const [lastName, setLastName] = React.useState('');
    const [signupText, setSignupText] = React.useState("");



    const {data: domain} = useSWR('/web/allowed-signup-domain', fetcher);
    React.useEffect(() => {
        setLoading(false);
    }, [open]);

    useEffect(() => {
        fetch(`/web/signup-text`).then(res => res.text()).then(setSignupText);
        
    }, [])

    


    const signUp = () => {
        setLoading(true);
        axios.post(`/web/signup`, {email, firstName, lastName}).then(() => {
            setLoading(false);
            setComplete(true);
        }).catch(err => {
            alert("Email address already in use");
            setLoading(false);
            setComplete(false);
        });
    };

    function onClose() {
        setComplete(false);
        handleClose();
    }

    if (signupText !== "") {
        return (
            <Dialog open={open} onClose={onClose}>
                <DialogTitle>Sign up</DialogTitle>
                <DialogContent sx={{"white-space": "pre-line"}}>{signupText}</DialogContent>
            </Dialog>
        )
    }
    if (typeof domain === 'string' && domain.length === 0) {
        return (
            <Dialog open={open} onClose={onClose}>
                <DialogTitle>{!complete ? "Sign up" : "Check your inbox"}</DialogTitle>
                <DialogContent>
                    {!complete ? (<>
                        <DialogContentText>
                            Sign up with your email address. We'll email you the instructions.
                        </DialogContentText>
                        <div style={{marginTop: '1em'}}></div>
                        <Grid container spacing={2}>
                            <Grid item xs={6}>
                                <TextField
                                    label="First name"
                                    fullWidth
                                    value={firstName}
                                    onChange={(e) => setFirstName(e.target.value)}
                                />
                            </Grid>
                            <Grid item xs={6}>
                                <TextField
                                    label="Last name"
                                    fullWidth
                                    value={lastName}
                                    onChange={(e) => setLastName(e.target.value)}
                                />
                            </Grid>
                            <Grid item xs={12}>
                                <TextField
                                    label="Email address"
                                    fullWidth
                                    value={email}
                                    onChange={(e) => setEmail(e.target.value)}
                                    onKeyPress={(e) => {
                                        if (e.key === 'Enter') signUp()
                                    }}
                                    //                                 InputProps={{
                                    //                                     endAdornment: <InputAdornment position="start">@{domain}</InputAdornment>,
                                    //                                 }}
                                />
                            </Grid>
                        </Grid>
                    </>) : (<>
                        < CheckMark/>
                    </>)}

                </DialogContent>
                <DialogActions>
                    <Button onClick={onClose} disabled={loading}>Close</Button>
                    {!complete &&
                        <LoadingButton disabled={!Boolean(email)} loading={loading} onClick={signUp} color="success">Sign
                            up</LoadingButton>}
                </DialogActions>
            </Dialog>
        )

    } else {
        return (
            <Dialog open={open} onClose={onClose}>
                <DialogTitle>{!complete ? "Sign up" : "Check your inbox"}</DialogTitle>
                <DialogContent>
                    {!complete ? (<>
                        <DialogContentText>
                            If you have an @{domain} email address you can sign up right away. We'll email you the
                            instructions.
                        </DialogContentText>
                        <div style={{marginTop: '1em'}}></div>
                        <Grid container spacing={2}>
                            <Grid item xs={6}>
                                <TextField
                                    label="First name"
                                    fullWidth
                                    value={firstName}
                                    onChange={(e) => setFirstName(e.target.value)}
                                />
                            </Grid>
                            <Grid item xs={6}>
                                <TextField
                                    label="Last name"
                                    fullWidth
                                    value={lastName}
                                    onChange={(e) => setLastName(e.target.value)}
                                />
                            </Grid>
                            <Grid item xs={12}>
                                <TextField
                                    label="Email address"
                                    fullWidth
                                    value={email}
                                    onChange={(e) => setEmail(e.target.value)}
                                    onKeyPress={(e) => {
                                        if (e.key === 'Enter') signUp()
                                    }}
                                    InputProps={{
                                        endAdornment: <InputAdornment position="start">@{domain}</InputAdornment>,
                                    }}
                                />
                            </Grid>
                        </Grid>
                    </>) : (<>
                        <CheckMark/>
                    </>)}

                </DialogContent>
                <DialogActions>
                    <Button onClick={onClose} disabled={loading}>Close</Button>
                    {!complete &&
                        <LoadingButton disabled={!Boolean(email)} loading={loading} onClick={signUp} color="success">Sign
                            up</LoadingButton>}
                </DialogActions>
            </Dialog>
        )
    }

}

export default SignUpDialog;