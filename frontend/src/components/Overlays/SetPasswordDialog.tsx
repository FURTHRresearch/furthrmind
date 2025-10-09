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
import axios from "axios";
import React from "react";

// @ts-ignore
const token = new Proxy(new URLSearchParams(window.location.search), { get: (searchParams, prop) => searchParams.get(prop), }).token;

const SetPasswordDialog = ({ open, handleClose }) => {
    const [loading, setLoading] = React.useState(false);
    const [complete, setComplete] = React.useState(false);
    const [password, setPassword] = React.useState('');
    const [repeat, setRepeat] = React.useState('');

    const savePassword = () => {
        setLoading(true);
        axios.post(`/web/set-password`, { password, password2: repeat, token }).then(() => {
            setLoading(false);
            setComplete(true);
        }).catch(() => {
            alert('Something went wrong. Please try again.');
            handleClose();
        });
    };
    return (
        <Dialog open={open} onClose={handleClose}>
            <DialogTitle>{!complete ? "Set your password" : "Success"}</DialogTitle>
            <DialogContent>
                {!complete ? (<>
                    <div style={{ marginTop: '1em' }}></div>
                    <Grid container spacing={2}>
                        <Grid item xs={12}>
                            <TextField
                                label="Password"
                                type="password"
                                fullWidth
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                            />
                        </Grid>
                        <Grid item xs={12}>
                            <TextField
                                label="Repeat password"
                                fullWidth
                                value={repeat}
                                type="password"
                                onChange={(e) => setRepeat(e.target.value)}
                                onKeyPress={(e) => { if (e.key === 'Enter') savePassword() }}
                                InputProps={{
                                    endAdornment: <InputAdornment position="start"></InputAdornment>,
                                }}
                            />
                        </Grid>
                    </Grid>
                </>) : (<>
                    <DialogContentText>
                        Password set. You can login now.
                    </DialogContentText>
                </>)}

            </DialogContent>
            <DialogActions>
                {complete && <Button onClick={handleClose} color="success">Close</Button>}
                {!complete && <LoadingButton loading={loading} onClick={savePassword} >Set password</LoadingButton>}
            </DialogActions>
        </Dialog>
    )
}

export default SetPasswordDialog;