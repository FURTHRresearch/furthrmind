import {LoadingButton} from '@mui/lab';
import {Stack, Typography} from '@mui/material';
import Button from '@mui/material/Button';
import Dialog from '@mui/material/Dialog';
import DialogActions from '@mui/material/DialogActions';
import DialogContent from '@mui/material/DialogContent';
import DialogTitle from '@mui/material/DialogTitle';

import axios from 'axios';
import {useState} from 'react';
import {useNavigate} from 'react-router-dom';
import FormControlLabel from "@mui/material/FormControlLabel";
import Checkbox from "@mui/material/Checkbox";

export default function CloneProject({setOpen, open, project}) {
    const [loading, setLoading] = useState(false);
    const [includeData, setIncludeData] = useState<boolean>(false);
    const [includeFile, setIncludeFile] = useState<boolean>(false);
    const [openSuccessDialog, setOpenSuccessDialog] = useState<boolean>(false);


    const navigate = useNavigate();

    const handleClone = () => {
        setLoading(true);
        const data = {includeData, includeFile}
        axios.post(`/web/projects/${project.id}/clone`, data).then(r => {
            setOpenSuccessDialog(true);
        });
    }

    function handleSuccesDialogClose(e) {
        setOpen(false)
        setOpenSuccessDialog(false);
    }
    return (
        <>
            <Dialog
                open={open}
                fullWidth
                style={{marginLeft: "auto", marginRight: "auto", width: "500px"}}
            >
                <DialogTitle>
                    Clone project: '{project.name}'
                </DialogTitle>
                <DialogContent>
                    <Typography>Include:</Typography>

                    <Stack direction={"column"} marginLeft={"40px"}>

                        <FormControlLabel control={<Checkbox checked={true}/>}
                                          label={"Fields, Units, and Research Categories"} disabled={true}/>
                        <FormControlLabel control={<Checkbox checked={includeData}/>}
                                          label={"Data"} onClick={() => {
                            setIncludeData(!includeData)
                        }}/>
                        <FormControlLabel control={<Checkbox checked={includeFile}/>}
                                          label={"Files"} onClick={() => {
                            setIncludeFile(!includeFile)
                        }}/>


                    </Stack>


                </DialogContent>
                <DialogActions>
                    <Button onClick={() => {
                        setOpen(false)
                    }}>Cancel</Button>
                    <LoadingButton color="success" loading={loading} onClick={handleClone}>
                        Clone
                    </LoadingButton>
                </DialogActions>
            </Dialog>
            {openSuccessDialog && <Dialog
                open={openSuccessDialog}
                fullWidth
                style={{marginLeft: "auto", marginRight: "auto", width: "400px"}}
            >
                <DialogTitle>
                    Clone successful
                </DialogTitle>
                <DialogContent>
                    {includeData ? <Typography>Your new project is created. Your data will be copied in background.
                        This might take a while.</Typography> : <Typography>Your new project is created.</Typography>}
                </DialogContent>
                <DialogActions>
                    <Button color="success" onClick={(e) => {handleSuccesDialogClose(e)}}>
                        Close
                    </Button>
                </DialogActions>
            </Dialog>}
        </>


    )
}