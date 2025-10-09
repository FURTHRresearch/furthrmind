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
import { useEffect, useState } from 'react';

export default function AddComboOption(props) {
    const {
        setOpen,
        open,
        headingTitle,
        description,
        textFieldLabel,
        primaryBtnTextLabel,
        secondaryBtnTextLabel,
        primaryBtnActionHandler,
        secondaryBtnActionHandler,
        textFieldPlaceholder,
        loading = false
    } = props;

    const theme = useTheme();
    const fullScreen = useMediaQuery(theme.breakpoints.down('md'));
    const [name, setName] = useState('');
    const [error, setError] = useState(false);
    const [errorMessage, setErrorMessage] = useState('');
    const [inputTouched, setInputTouched] = useState(false);

    const handleChange = (e) => {
        setName(e.target.value);
        if (error) {
            setError(false);
        }
    }

    useEffect(() => {
        if (name.length === 0) {
            setError(true);
            setErrorMessage(`${textFieldLabel} is required`);
        } else {
            setError(false)
            setErrorMessage('')
        }
    }, [name, inputTouched]);

    const submitHandler = () => {
        primaryBtnActionHandler(name);
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
                    {headingTitle}
                </DialogTitle>
                <DialogContent>
                    <DialogContentText variant='body1' >
                        {description}
                    </DialogContentText>
                    <Typography variant="subtitle2" mt={2} mb={1}>{textFieldLabel}</Typography>
                    <OutlinedInput
                        label='name'
                        fullWidth
                        notched={false}
                        onFocus={() => setInputTouched(true)}
                        value={name}
                        error={error && inputTouched}
                        name='name'
                        onChange={handleChange}
                        placeholder={textFieldPlaceholder} />
                    {inputTouched && error && < Typography variant="subtitle1" style={{ color: 'red', fontSize: '12px' }} >{errorMessage}</Typography>}
                </DialogContent>
                <DialogActions>
                    <Button autoFocus onClick={secondaryBtnActionHandler} sx={{ color: '#707070', padding: '12px 16px' }}>
                        {secondaryBtnTextLabel}
                    </Button>
                    <LoadingButton onClick={submitHandler} autoFocus sx={{ padding: '12px 16px' }} disabled={error} loading={loading}>
                        {primaryBtnTextLabel}
                    </LoadingButton>
                </DialogActions>
            </Dialog>
        </div >
    );
}