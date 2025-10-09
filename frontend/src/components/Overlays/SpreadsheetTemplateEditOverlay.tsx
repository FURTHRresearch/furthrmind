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

export default function SpreadsheetTemplateEditOverlay({ onClose: onCloseHandler, open, setOpen, templateName, templateId }) {
    const theme = useTheme();
    const fullScreen = useMediaQuery(theme.breakpoints.down('md'));
    const [updating, setUpdating] = useState(false);
    const [editedData, setEditedData] = useState({
        templateName: '',
    })
    const [errorMessage, setErrorMessage] = useState({
        templateName: '',
    });
    const [inputTouched, setInputTouched] = useState({
        templateName: false,
    });

    const params = useParams();

    const handleUpdate = () => {
        setUpdating(true);
        axios.post(`/web/onlyoffice/update_template/${templateId}`, {
            name: editedData.templateName,
            projectid: params.project,
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
            templateName: templateName,
        })
    }, [templateName]);

    useEffect(() => {
        if (inputTouched.templateName && !editedData.templateName) {
            setErrorMessage({
                ...errorMessage,
                templateName: "Spreadsheet template name required"
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
                    Edit spreadsheet template
                </DialogTitle>
                <DialogContent>
                    {/* <DialogContentText variant='body1' >
                        You are deleting project <Typography variant='subtitle2' component='span' sx={{ color: 'black' }}>{projectName}</Typography> . You will lose access to all the data in this project.
                    </DialogContentText> */}
                    <Typography variant="subtitle2" mt={2} mb={1}>Spreadsheet template name</Typography>
                    <OutlinedInput
                        label='Template name'
                        fullWidth
                        notched={false}
                        onFocus={() => setInputTouched({ ...inputTouched, templateName: true })}
                        value={editedData.templateName}
                        error={inputTouched.templateName && errorMessage.templateName ? true : false}
                        name='templateName'
                        onChange={handleChange}
                        placeholder='Enter template name' />
                    {inputTouched.templateName && errorMessage.templateName && < Typography variant="subtitle1" style={{ color: 'red', fontSize: '12px' }} >{errorMessage.templateName}</Typography>}
                </DialogContent>
                <DialogActions className="mb-3" >
                    <Button autoFocus onClick={onCloseHandler} sx={{ color: '#707070', padding: '12px 16px' }}>
                        Cancel
                    </Button>
                    <LoadingButton

                        loading={updating} onClick={handleUpdate} autoFocus sx={{ padding: '12px 16px' }} disabled={errorMessage.templateName }>
                        Update
                    </LoadingButton>
                </DialogActions>
            </Dialog>
        </div >
    );
}