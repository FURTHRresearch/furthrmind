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

export default function DeleteTemplate({ setOpen, open, templateName, templateId }) {
    const theme = useTheme();
    const fullScreen = useMediaQuery(theme.breakpoints.down('md'));
    const [deleting, setDeleting] = useState(false);

    const navitage = useNavigate();
    const params = useParams();

    const handleDelete = () => {
        setDeleting(true);
        axios.delete(`/web/onlyoffice/delete_template/${templateId}`).then(r => {
            setOpen(false)
            //mutate({...rows, spreadsheet: false})
        });
    }


    return (
        <div>
            <Dialog
                fullScreen={fullScreen}
                open={open}
                onClose={() => setOpen(false)}
                aria-labelledby="responsive-dialog-title"
            >
                <DialogTitle style={{ fontWeight: 600 }}>
                    Delete Template
                </DialogTitle>
                <DialogContent>
                    <DialogContentText variant='body1' >
                        You are deleting Template <Typography variant='subtitle2' component='span' sx={{ color: 'black' }}>{templateName}</Typography> .
                    </DialogContentText>
                    <Typography variant="body2" mt={2} mb={1} sx={{ color: "gray" }}>This action can not be undo, and it will delete all the associated info</Typography>
                </DialogContent>
                <DialogActions>
                    <Button autoFocus onClick={() => setOpen(false)} sx={{ color: '#707070', padding: '12px 16px' }}>
                        Cancel
                    </Button>
                    <LoadingButton loading={deleting} onClick={handleDelete} autoFocus sx={{ padding: '12px 16px' }}>
                        Delete
                    </LoadingButton>
                </DialogActions>
            </Dialog>
        </div >
    );
}