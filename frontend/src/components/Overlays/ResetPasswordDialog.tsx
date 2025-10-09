import LoadingButton from '@mui/lab/LoadingButton';
import Button from '@mui/material/Button';
import Dialog from '@mui/material/Dialog';
import DialogActions from '@mui/material/DialogActions';
import DialogContent from '@mui/material/DialogContent';
import DialogContentText from '@mui/material/DialogContentText';
import DialogTitle from '@mui/material/DialogTitle';
import TextField from '@mui/material/TextField';
import axios from "axios";
import React from "react";


const ResetPasswordDialog = ({ open, handleClose }) => {
    const [loading, setLoading] = React.useState(false);
    const [complete, setComplete] = React.useState(false);
    const [email, setEmail] = React.useState('');

    const resetPassword = () => {
        setLoading(true);
        axios.post(`/web/password-reset`, { email }).then(() => {
            setLoading(false);
            setComplete(true);
        }).catch(() => {
            alert('Something went wrong. Please try again.');
            handleClose();
        });
    };
    return (
        <Dialog open={open} onClose={handleClose} fullWidth>
            <DialogTitle>{!complete ? "Reset your password" : "Request received"}</DialogTitle>
            <DialogContent>
                {!complete ? (<>
                    <DialogContentText>
                        Please enter your email address. We will send you an email with instructions on how to reset your password.
                    </DialogContentText>
                    <div style={{ marginTop: '1em' }}></div>
                    <TextField
                        label="Email address"
                        fullWidth
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        onKeyPress={(e) => { if (e.key === 'Enter') resetPassword() }}
                    />
                </>) : (<>
                    <DialogContentText>
                        If your email is registered, you will receive an email with instructions on how to reset your password.
                    </DialogContentText>
                </>)}

            </DialogContent>
            <DialogActions>
                {complete && <Button onClick={handleClose} color="success">Close</Button>}
                {!complete && <LoadingButton loading={loading} onClick={resetPassword} >Reset password</LoadingButton>}
            </DialogActions>
        </Dialog>
    )
}

export default ResetPasswordDialog;