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

export default function ArchiveProject({ setOpen, open, project}) {
    const theme = useTheme();
    const fullScreen = useMediaQuery(theme.breakpoints.down('md'));
    const [archiving, setArchiving] = useState(false);
    const [name, setName] = useState('');
    const [error, setError] = useState(false);
    const [errorMessage, setErrorMessage] = useState('');
    const [inputTouched, setInputTouched] = useState(false);

    const navitage = useNavigate();
    const params = useParams();

    const handleArchive = () => {
        setArchiving(true);
        axios.post(`/web/projects/${params.project}/archive`).then(r => {
            navitage('/');
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
        } else if (name.length > 0 && name !== project.name) {
            setError(true);
            setErrorMessage('Project name mismatch');

        } else if (name === project.name) {
            setError(false)
            setErrorMessage('')
        }
    }, [name, project.name, inputTouched]);

    return (
        <div>
            <Dialog
                fullScreen={fullScreen}
                open={open}
                onClose={() => setOpen(false)}
                aria-labelledby="responsive-dialog-title"
            >
                <DialogTitle style={{ fontWeight: 600 }}>
                    {!project.archived ? `Archive Project:  ${project.name}` : `Restore Project: ${project.name}`}
                </DialogTitle>
                <DialogContent>
                    <DialogContentText variant='body1' >
                        {!project.archived ? `Do you want to archive the project "${project.name}"`:
                        `Do you want to restore the project "${project.name}"`}
                    </DialogContentText>
                    <Typography variant="subtitle2" mt={2} mb={1}>Enter project name to confirm archiving.</Typography>
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
                    <LoadingButton loading={archiving} onClick={handleArchive} autoFocus sx={{ padding: '12px 16px' }} disabled={error}>
                        {!project.archived ? "Archive" : "Restore"}
                    </LoadingButton>
                </DialogActions>
            </Dialog>
        </div >
    );
}