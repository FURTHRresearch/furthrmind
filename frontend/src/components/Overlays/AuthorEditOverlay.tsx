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
import * as React from "react";

export default function AuthorEditOverlay({ onClose: onCloseHandler, open, author }) {
    const theme = useTheme();
    const fullScreen = useMediaQuery(theme.breakpoints.down('md'));
    const [updating, setUpdating] = useState(false);
    const [createdData, setCreatedData] = useState({
        authorName: '',
        authorInstitution: ''
    })


    const [errorMessage, setErrorMessage] = useState({
        authorName: '',
        authorInstitution: ''
    });
    const [inputTouched, setInputTouched] = useState({
        authorName: false,
        authorInstitution: false
    });

    const handleUpdate = () => {
        setUpdating(true);

        axios.post(`/web/author/${author['_id']}`, {
            name: createdData.authorName,
            institution: createdData.authorInstitution,
        }).then(onCloseHandler)

    }

    const handleChange = (e) => {
        setCreatedData({
            ...createdData,
            [e.target.name]: e.target.value
        })
    }

    useEffect(() => {
        setCreatedData({
            authorName: author.name,
            authorInstitution: author.institution
        })
    }, [author.name, author.institution]);

    useEffect(() => {
        if (inputTouched.authorName && !createdData.authorName) {
            setErrorMessage({
                ...errorMessage,
                authorName: "Author name required"
            })
        } else if (inputTouched.authorInstitution && !createdData.authorInstitution) {
            setErrorMessage({
                ...errorMessage,
                authorInstitution: "Author institution required"
            })
        } else {
            setErrorMessage({
                authorName: '',
                authorInstitution: ''
            })
        }
    }, [inputTouched, createdData]);

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
                    Edit author
                </DialogTitle>
                <DialogContent>

                    <Typography variant="subtitle2" mt={2} mb={1}>Name</Typography>
                    <OutlinedInput
                        label='Author name'
                        fullWidth
                        notched={false}
                        onFocus={() => setInputTouched({ ...inputTouched, authorName: true })}
                        value={createdData.authorName}
                        error={inputTouched.authorName && errorMessage.authorName ? true : false}
                        name='authorName'
                        onChange={handleChange}
                        placeholder='Enter author name' />
                    {inputTouched.authorName && errorMessage.authorName && < Typography variant="subtitle1" style={{ color: 'red', fontSize: '12px' }} >{errorMessage.authorName}</Typography>}
                    <Typography variant="subtitle2" mt={2} mb={1}>Institution</Typography>
                    <OutlinedInput
                        multiline
                        label='Author institution'
                        fullWidth
                        notched={false}
                        onFocus={() => setInputTouched({ ...inputTouched, authorInstitution: true })}
                        value={createdData.authorInstitution}
                        error={inputTouched.authorInstitution && errorMessage.authorInstitution ? true : false}
                        name='authorInstitution'
                        //minRows={4}
                        onChange={handleChange}
                        placeholder='Enter author institution' />
                    {inputTouched.authorInstitution && errorMessage.authorInstitution && < Typography variant="subtitle1" style={{ color: 'red', fontSize: '12px' }} >{errorMessage.authorInstitution}</Typography>}
                </DialogContent>
                <DialogActions className="mb-3" >
                    <Button autoFocus onClick={onCloseHandler} sx={{ color: '#707070', padding: '12px 16px' }}>
                        Cancel
                    </Button>
                    <LoadingButton

                        loading={updating} onClick={handleUpdate} autoFocus sx={{ padding: '12px 16px' }}
                        //disabled={errorMessage.authorName || errorMessage.authorInstitution}
                        >
                        Update
                    </LoadingButton>
                </DialogActions>
            </Dialog>
        </div >
    );
}