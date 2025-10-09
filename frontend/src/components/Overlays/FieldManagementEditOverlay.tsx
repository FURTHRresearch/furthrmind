import {LoadingButton} from '@mui/lab';
import {OutlinedInput, Typography} from '@mui/material';
import Button from '@mui/material/Button';
import Dialog from '@mui/material/Dialog';
import DialogActions from '@mui/material/DialogActions';
import DialogContent from '@mui/material/DialogContent';
import DialogTitle from '@mui/material/DialogTitle';
import {useTheme} from '@mui/material/styles';
import useMediaQuery from '@mui/material/useMediaQuery';
import axios from 'axios';
import {useCallback, useEffect, useState} from 'react';
import {useParams} from 'react-router-dom';
import debounce from "lodash/debounce";

export default function FieldManagementEditOverlay({
                                                       onClose: onCloseHandler, open, setOpen,
                                                       fieldName, fieldId, rows, mutateFields
                                                   }) {
    const theme = useTheme();
    const fullScreen = useMediaQuery(theme.breakpoints.down('md'));
    const [updating, setUpdating] = useState(false);
    const [name, setName] = useState(fieldName)
    const [check, setCheck] = useState(true)
    const params = useParams();

    const handleUpdate = () => {
        setUpdating(true);
        axios.patch(`/web/fields/${fieldId}`, {
            name: name,
        }).then(r => {
            const copyRows = [...rows]
            copyRows.forEach((row) => {
                if (row.id === fieldId) {
                    row.name = name;
                }
            });
            mutateFields(copyRows)
            // mutateFields(rows.filter((row) => {
            //     if (row.id === fieldId) {
            //         row.name = name;
            //     };
            // }));

        })
        setOpen(false)
    }

    function checkName(nameToBeChecked) {
        axios.post(`/web/field/${fieldId}/check`, {name: nameToBeChecked}).then((r) => {
            if (r.data == "True") {
                setCheck(true)
            } else {
                setCheck(false)
            }

        })
    }
    const debouncedCheck = useCallback(debounce(checkName, 200), []);

    useEffect(() => {
        if (name === "") {
            setCheck(false)
            return;
        }
        if (name === fieldName) {
            setCheck(true)
            return
        } else {
            debouncedCheck(name)
        }

    }, [name]);

    return (
        <div>
            <Dialog
                fullScreen={fullScreen}
                fullWidth
                open={open}
                onClose={onCloseHandler}
                aria-labelledby="responsive-dialog-title"
            >
                <DialogTitle style={{fontWeight: 600}}>
                    Edit field name
                </DialogTitle>
                <DialogContent>
                    {/* <DialogContentText variant='body1' >
                        You are deleting project <Typography variant='subtitle2' component='span' sx={{ color: 'black' }}>{projectName}</Typography> . You will lose access to all the data in this project.
                    </DialogContentText> */}
                    <Typography variant="subtitle2" mt={2} mb={1}>Field name</Typography>
                    <OutlinedInput
                        label='Field name'
                        fullWidth
                        notched={false}
                        value={name}
                        name='fieldName'
                        onChange={(e) => {
                            setName((e.target.value))
                        }}
                        placeholder='Enter field name'/>
                    {!name && < Typography variant="subtitle1" style={{
                        color: 'red',
                        fontSize: '16px'
                    }}>Please enter a field name</Typography>}
                    {!check && name && < Typography variant="subtitle1" style={{
                        color: 'red',
                        fontSize: '16px'
                    }}>Name already in use. Please choose another one.</Typography>}

                </DialogContent>
                <DialogActions className="mb-3">
                    <Button autoFocus onClick={onCloseHandler} sx={{color: '#707070', padding: '12px 16px'}}>
                        Cancel
                    </Button>
                    <LoadingButton
                        loading={updating}
                        onClick={handleUpdate}
                        autoFocus
                        sx={{padding: '12px 16px'}}
                        disabled={(!check)}>
                        Update
                    </LoadingButton>
                </DialogActions>
            </Dialog>
        </div>
    );
}