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

export default function DeleteCategoryManagement({ setOpen, open, categoryName, categoryId, mutateResearchCategory, rows}) {
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
        axios.delete(`/web/categories/${categoryId}`).then(r => {

            mutateResearchCategory(rows.filter((row) => {
                return row.id !== 'categoryId';
            }));
        });
        setOpen(false)
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
            setErrorMessage('Category name is required');
        } else if (name.length > 0 && name !== categoryName) {
            setError(true);
            setErrorMessage('Category name mismatch');

        } else if (name === categoryName) {
            setError(false)
            setErrorMessage('')
        }
    }, [name, categoryName, inputTouched]);

    return (
        <div>
            <Dialog
                fullScreen={fullScreen}
                open={open}
                onClose={() => setOpen(false)}
                aria-labelledby="responsive-dialog-title"
            >
                <DialogTitle style={{ fontWeight: 600 }}>
                    Delete Category: {categoryName}
                </DialogTitle>
                <DialogContent>
                    <DialogContentText variant='body1' >
                        You are deleting Category <Typography variant='subtitle2' component='span' sx={{ color: 'black' }}>{categoryName}</Typography> .
                    </DialogContentText>
                    <Typography variant="body2" mt={2} mb={1} sx={{ color: "gray" }}>This action can not be undo, and it will delete all research items belong to this category.</Typography>

                    <Typography variant="subtitle2" mt={2} mb={1}>Enter category name to confirm deletion.</Typography>
                    <OutlinedInput
                        label='Research Category Name'
                        fullWidth
                        notched={false}
                        onFocus={() => setInputTouched(true)}
                        value={name}
                        error={error && inputTouched}
                        name='name'
                        onChange={handleChange}
                        placeholder='Enter Research Category Name' />
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