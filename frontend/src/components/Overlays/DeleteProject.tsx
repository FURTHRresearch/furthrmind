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

export default function DeleteProject({ setOpen, open, projectName }) {
    const theme = useTheme();
    const fullScreen = useMediaQuery(theme.breakpoints.down('md'));
    const [deleting, setDeleting] = useState(false);
    const [name, setName] = useState('');
    const [error, setError] = useState(false);
    const [errorMessage, setErrorMessage] = useState('');
    const [inputTouched, setInputTouched] = useState(false);

    const navigate = useNavigate();
    const params = useParams();

    const handleDelete = () => {
        setDeleting(true);
        axios.delete(`/web/projects/${params.project}`).then(r => {
            navigate('/');
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
            setErrorMessage('Project name is required');
        } else if (name.length > 0 && name !== projectName) {
            setError(true);
            setErrorMessage('Project name mismatch');

        } else if (name === projectName) {
            setError(false)
            setErrorMessage('')
        }
    }, [name, projectName, inputTouched]);

    return (
        <div>
            <Dialog
                fullScreen={fullScreen}
                open={open}
                onClose={() => setOpen(false)}
                aria-labelledby="responsive-dialog-title"
            >
                <DialogTitle style={{ fontWeight: 600 }}>
                    Delete Project: {projectName}
                </DialogTitle>
                <DialogContent>
                    <DialogContentText variant='body1' >
                        You are deleting project <Typography variant='subtitle2' component='span' sx={{ color: 'black' }}>{projectName}</Typography> .
                        The project and all data belonging to it will be delete permanently. This action cannot be undone.
                    </DialogContentText>
                    <Typography variant="subtitle2" mt={2} mb={1}>Enter project name to confirm deleting.</Typography>
                    <OutlinedInput
                        label='Project Name'
                        fullWidth
                        notched={false}
                        onFocus={() => setInputTouched(true)}
                        value={name}
                        error={error && inputTouched}
                        name='name'
                        onChange={handleChange}
                        placeholder='Enter Project Name' />
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