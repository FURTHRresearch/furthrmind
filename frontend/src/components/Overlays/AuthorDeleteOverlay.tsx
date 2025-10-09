import { LoadingButton } from '@mui/lab';
import {FormControl, InputLabel, OutlinedInput, Select, Stack, Typography} from "@mui/material";

import Button from '@mui/material/Button';
import Dialog from '@mui/material/Dialog';
import DialogActions from '@mui/material/DialogActions';
import DialogContent from '@mui/material/DialogContent';
import DialogContentText from '@mui/material/DialogContentText';
import DialogTitle from '@mui/material/DialogTitle';
import { useTheme } from '@mui/material/styles';
import useMediaQuery from '@mui/material/useMediaQuery';
import axios from 'axios';
import React, { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import MenuItem from "@mui/material/MenuItem";

export default function AuthorDeleteOverlay({ setOpen, open, selectedAuthor, authorsList}) {
    const theme = useTheme();
    const fullScreen = useMediaQuery(theme.breakpoints.down('md'));
    const [deleting, setDeleting] = useState(false);
    const [error, setError] = useState(false);
    const [errorMessage, setErrorMessage] = useState('');
    const [inputTouched, setInputTouched] = useState(false);
    const [alternativeAuthor, setAlternativeAuthor] = useState("")
    

    const handleDelete = () => {
        setDeleting(true);
        axios.delete(`/web/author/${selectedAuthor['_id']}/${alternativeAuthor}`).then(r => {
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
                    Delete author
                </DialogTitle>
                <DialogContent>
                    {selectedAuthor.institution == "" && <DialogContentText variant='body1' >
                        You are deleting author <Typography variant='subtitle2' component='span' sx={{ color: 'black' }}>{selectedAuthor.name} </Typography> .
                    </DialogContentText>}

                    {selectedAuthor.institution != "" && <DialogContentText variant='body1' >
                        You are deleting author <Typography variant='subtitle2' component='span' sx={{ color: 'black' }}>{selectedAuthor.name} @ {selectedAuthor.institution} </Typography> .
                    </DialogContentText>}


                    <Typography variant="body2" mt={2} mb={1} sx={{ color: "gray" }}>This action can not be undo and you need to choose a replacement author.</Typography>

                    <Typography variant="subtitle2" mt={2} mb={1}>Choose replacement author to confirm deletion</Typography>
                    <Stack direction={{ xs: 'column', sm: 'row' }}
                           alignItems="center"
                           spacing = {1}>
                        <FormControl sx={{ m: 1, minWidth: 450 }} size="small">
                            <Select
                                value={alternativeAuthor}
                                variant="standard"
                                onChange={(e: any) => setAlternativeAuthor(e.target.value)}
                            >
                                {authorsList != undefined && authorsList.map((author) => (
                                    author.name != selectedAuthor.name && <MenuItem value={author['_id']}>{author.name} @ {author.institution}</MenuItem>
                                ))}


                            </Select>
                        </FormControl>
                    </Stack>
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