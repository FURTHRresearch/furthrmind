import { useState } from 'react';

import Dialog from '@mui/material/Dialog';
import DialogContent from '@mui/material/DialogContent';
// import DialogContentText from '@mui/material/DialogContentText';
import CloseIcon from '@mui/icons-material/Close';
import { Box, Checkbox, FormControlLabel, IconButton, OutlinedInput } from '@mui/material';
import DialogTitle from '@mui/material/DialogTitle';
import { useTheme } from '@mui/material/styles';
import useMediaQuery from '@mui/material/useMediaQuery';
import classes from './GenerateApiTokenStyle.module.css';
// import { useNavigate, useParams } from 'react-router-dom';
// import axios from 'axios';
import { LoadingButton } from '@mui/lab';
import axios from 'axios';
import useSWR from 'swr';

const fetcher = (url) => fetch(url).then((res) => res.json());

export default function GenerateToken({ setOpen, open }) {
    const theme = useTheme();
    const fullScreen = useMediaQuery(theme.breakpoints.down('md'));
    const [loading, setLoading] = useState(false);
    const [tokenName, setTokenName] = useState('');
    const [scope, setScope] = useState({
        read: true,
        write: true
    })
    const [key, setKey] = useState(undefined);

    const { data: token, mutate: mutateToken } = useSWR('/web/apikeys', fetcher);


    const handleCheckBox = (e) => {
        setScope({
            ...scope,
            [e.target.name]: e.target.checked
        })
    }

    const generateToken = () => {
        setLoading(true);
        axios.post('/web/apikeys', { name: tokenName }).then(r => {
            mutateToken([r.data, ...token]);
            setKey(r.data.key);
            setTokenName('');
            setLoading(false);
        })
    }


    return (
        <div>
            <Dialog
                fullScreen={fullScreen}
                open={open}
                onClose={() => setOpen(false)}
                aria-labelledby="responsive-dialog-title"
            >
                <Box display='flex' justifyContent='space-between'>
                    <DialogTitle style={{ fontWeight: '400px' }}>
                        New personal access token
                    </DialogTitle>
                    <IconButton
                        onClick={() => setOpen(prev => !prev)}
                        style={{ marginRight: '10px' }} size='small' disableRipple={true}>
                        <CloseIcon />
                    </IconButton>
                </Box>

                <DialogContent className={classes.modalBody}>
                    {!key ? <>
                        <div className={classes.inputWrapper}>
                            <div className={classes.labelName}>Token name</div>
                            <OutlinedInput id="outlined-basic"
                                notched={false}
                                label='Enter token name'
                                value={tokenName}
                                placeholder="Enter token name"
                                onChange={(e) => setTokenName(e.target.value)}
                                size="small" />
                        </div>
                        <div className={classes.inputWrapper}>
                            <div className={classes.labelName}>Scopes</div>
                            <Box display='flex'>
                                <FormControlLabel
                                    control={
                                        <Checkbox name="read" checked={scope.read} onChange={handleCheckBox} disabled />
                                    }
                                    label="Read (default)"
                                    sx={{ color: '#4c4c4c', height: '20px' }}
                                />
                                <FormControlLabel
                                    control={
                                        <Checkbox
                                            onChange={handleCheckBox}
                                            checked={scope.write}
                                            disabled
                                            name="write" sx={{ color: '#666666', fontSize: '12px' }} />
                                    }
                                    label="Write (optional)"
                                    sx={{ color: '#4c4c4c', height: '20px' }}
                                />
                            </Box>
                        </div>
                        <Box mt={5} mb={3}>
                            <LoadingButton variant='contained' autoFocus color="primary"
                                onClick={generateToken}
                                loading={loading}
                                fullWidth disableElevation>
                                Generate Token
                            </LoadingButton>
                        </Box>
                    </> : <>
                        <p>Your key is:</p>
                        <p><b>{key}</b></p>
                    </>}
                </DialogContent>

            </Dialog>
        </div>
    );
}