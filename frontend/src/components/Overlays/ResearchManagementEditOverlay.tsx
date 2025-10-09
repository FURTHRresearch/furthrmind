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

export default function ResearchManagementEditOverlay({ onClose: onCloseHandler, open, setOpen,
                                                          categoryName, categoryDesc, categoryId, rows, mutateResearchCategory }) {
    const theme = useTheme();
    const fullScreen = useMediaQuery(theme.breakpoints.down('md'));
    const [updating, setUpdating] = useState(false);
    const [editedData, setEditedData] = useState({
        categoryName: '',
        categoryDesc: ''
    })
    const [errorMessage, setErrorMessage] = useState({
        categoryName: '',
        categoryDesc: ''
    });
    const [inputTouched, setInputTouched] = useState({
        categoryName: false,
        categoryDesc: false
    });

    const params = useParams();

    const handleUpdate = () => {
        setUpdating(true);
        axios.post(`/web/categories/${categoryId}`, {
            name: editedData.categoryName,
            description: editedData.categoryDesc,
            projectid: params.project,
        }).then(r => {
            mutateResearchCategory(rows.filter((row) => {
                if ( row.id == 'categoryId') {
                    row.name =editedData.categoryName;
                    row.description = editedData.categoryDesc;
                };
            }));

        })
        setOpen(false)



    }

    const handleChange = (e) => {
        setEditedData({
            ...editedData,
            [e.target.name]: e.target.value
        })
    }

    useEffect(() => {
        setEditedData({
            categoryName: categoryName,
            categoryDesc: categoryDesc
        })
    }, [categoryName, categoryDesc]);

    useEffect(() => {
        if (inputTouched.categoryName && !editedData.categoryName) {
            setErrorMessage({
                ...errorMessage,
                categoryName: "Category name required"
            })
        } else if (inputTouched.categoryDesc && !editedData.categoryDesc) {
            setErrorMessage({
                ...errorMessage,
                categoryDesc: "Category description required"
            })
        } else {
            setErrorMessage({
                categoryName: '',
                categoryDesc: ''
            })
        }
    }, [inputTouched, editedData]);

    return (
        <div>
            <Dialog
                fullScreen={fullScreen}
                fullWidth
                open={open}
                onClose={onCloseHandler}
                aria-labelledby="responsive-dialog-title"
            >
                <DialogTitle style={{ fontWeight: 600 }}>
                    Edit research category
                </DialogTitle>
                <DialogContent>
                    {/* <DialogContentText variant='body1' >
                        You are deleting project <Typography variant='subtitle2' component='span' sx={{ color: 'black' }}>{projectName}</Typography> . You will lose access to all the data in this project.
                    </DialogContentText> */}
                    <Typography variant="subtitle2" mt={2} mb={1}>Category name</Typography>
                    <OutlinedInput
                        label='Category name'
                        fullWidth
                        notched={false}
                        onFocus={() => setInputTouched({ ...inputTouched, categoryName: true })}
                        value={editedData.categoryName}
                        error={inputTouched.categoryName && errorMessage.categoryName ? true : false}
                        name='categoryName'
                        onChange={handleChange}
                        placeholder='Enter category name' />
                    {inputTouched.categoryName && errorMessage.categoryName && < Typography variant="subtitle1" style={{ color: 'red', fontSize: '12px' }} >{errorMessage.categoryName}</Typography>}
                    <Typography variant="subtitle2" mt={2} mb={1}>Category description</Typography>
                    <OutlinedInput
                        multiline
                        label='Category description'
                        fullWidth
                        notched={false}
                        onFocus={() => setInputTouched({ ...inputTouched, categoryDesc: true })}
                        value={editedData.categoryDesc}
                        error={inputTouched.categoryDesc && errorMessage.categoryDesc ? true : false}
                        name='categoryDesc'
                        minRows={4}
                        onChange={handleChange}
                        placeholder='Enter category description' />
                    {inputTouched.categoryDesc && errorMessage.categoryDesc && < Typography variant="subtitle1" style={{ color: 'red', fontSize: '12px' }} >{errorMessage.categoryDesc}</Typography>}
                </DialogContent>
                <DialogActions className="mb-3" >
                    <Button autoFocus onClick={onCloseHandler} sx={{ color: '#707070', padding: '12px 16px' }}>
                        Cancel
                    </Button>
                    <LoadingButton
                        loading={updating}
                        onClick={handleUpdate}
                        autoFocus sx={{ padding: '12px 16px' }}
                        disabled={errorMessage.categoryName || errorMessage.categoryDesc}>
                        Update
                    </LoadingButton>
                </DialogActions>
            </Dialog>
        </div >
    );
}