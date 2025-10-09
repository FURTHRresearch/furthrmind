import Button from '@mui/material/Button';
import Dialog from '@mui/material/Dialog';
import DialogActions from '@mui/material/DialogActions';
import DialogContent from '@mui/material/DialogContent';
import DialogContentText from '@mui/material/DialogContentText';
import DialogTitle from '@mui/material/DialogTitle';
import { useTheme } from '@mui/material/styles';
import TextField from '@mui/material/TextField';
import useMediaQuery from '@mui/material/useMediaQuery';
import { useState } from 'react';

export default function AuthenticationDialog({ setOpen, open, callback }) {
    const theme = useTheme();
    const fullScreen = useMediaQuery(theme.breakpoints.down('md'));
    const [password, setPassword] = useState("");

    const handleSubmit = () => {
        callback(password);
    }

    return (
        <div>
            <Dialog
                fullScreen={fullScreen}
                open={open}
                onClose={() => setOpen(false)}
                aria-labelledby="responsive-dialog-title"
            >
                <DialogTitle >
                    Authentication required
                </DialogTitle>
                <DialogContent>
                    <DialogContentText>
                        Please enter your current password to apply these changes.

                    </DialogContentText>
                    <TextField
                        autoFocus
                        margin="dense"
                        onChange={(e) => setPassword(e.target.value)}
                        id="name"
                        placeholder="Password"
                        label="Password"
                        type="password"
                        fullWidth
                        variant="standard"
                        onKeyPress={(e) => { if (e.key === 'Enter') handleSubmit() }}
                    />
                </DialogContent>
                <DialogActions>
                    <Button onClick={() => setOpen(false)}>
                        Cancel
                    </Button>
                    <Button onClick={handleSubmit} color="success">
                        Save
                    </Button>
                </DialogActions>
            </Dialog>
        </div >
    );
}