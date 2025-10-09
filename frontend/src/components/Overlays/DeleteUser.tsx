import { LoadingButton } from '@mui/lab';
import { OutlinedInput, Typography } from '@mui/material';
import Button from '@mui/material/Button';
import Dialog from '@mui/material/Dialog';
import DialogActions from '@mui/material/DialogActions';
import DialogContent from '@mui/material/DialogContent';
import DialogContentText from '@mui/material/DialogContentText';
import DialogTitle from '@mui/material/DialogTitle';
import { useTheme } from '@mui/material/styles';
import useMediaQuery from '@mui/material/useMediaQuery';
import axios from 'axios';
import { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';

export default function DeleteUser({ setOpen, open, email, userId, users, mutateUsers }) {
    const theme = useTheme();
    const fullScreen = useMediaQuery(theme.breakpoints.down('md'));
    const [deleting, setDeleting] = useState(false);
    const [name, setName] = useState('');
    const [error, setError] = useState(false);
    const [errorMessage, setErrorMessage] = useState('');
    const [inputTouched, setInputTouched] = useState(false);

    const navitage = useNavigate();
    const params = useParams();

    const handleDelete = () => {
        setDeleting(true);
        axios.delete(`/web/admin/users/${userId}`).then(r => {
            mutateUsers(users.filter(u => u.id !== userId));
            setOpen(false)
        });
    }

    const handleChange = (e) => {
        setName(e.target.value);
        if (error) {
            setError(false);
        }
    }

    useEffect(() => {
        if (name.length === 0) {
            setError(true);
            setErrorMessage('Email address is required');
        } else if (name.length > 0 && name !== email) {
            setError(true);
            setErrorMessage('Email address mismatch');

        } else if (name === email) {
            setError(false)
            setErrorMessage('')
        }
    }, [name, email, inputTouched]);

    return (
        <div>
            <Dialog
                fullScreen={fullScreen}
                open={open}
                onClose={() => setOpen(false)}
                aria-labelledby="responsive-dialog-title"
            >
                <DialogTitle style={{ fontWeight: 600 }}>
                    Delete User {email}
                </DialogTitle>
                <DialogContent>
                    <DialogContentText variant='body1' >
                        You are deleting user <Typography variant='subtitle2' component='span' sx={{ color: 'black' }}>{email}</Typography>. All projects of this
                        user will be archived and assigned to the FURTHRmind admins.
                    </DialogContentText>
                    <Typography variant="subtitle2" mt={2} mb={1}>Enter email address to confirm deleting.</Typography>
                    <OutlinedInput
                        label='Email address'
                        fullWidth
                        notched={false}
                        onFocus={() => setInputTouched(true)}
                        value={name}
                        error={error && inputTouched}
                        name='name'
                        onChange={handleChange}
                        placeholder='Enter Email Address' />
                    {inputTouched && error && < Typography variant="subtitle1" style={{ color: 'red', fontSize: '12px' }} >{errorMessage}</Typography>}
                </DialogContent>
                <DialogActions>
                    <Button autoFocus onClick={() => setOpen(false)} sx={{ color: '#707070', padding: '12px 16px' }}>
                        Cancel
                    </Button>
                    <LoadingButton loading={deleting} onClick={handleDelete} autoFocus sx={{ padding: '12px 16px' }} disabled={error}>
                        Delete
                    </LoadingButton>
                </DialogActions>
            </Dialog>
        </div >
    );
}