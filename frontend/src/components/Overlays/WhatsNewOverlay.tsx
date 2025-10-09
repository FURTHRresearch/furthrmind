import Button from '@mui/material/Button';
import Dialog from '@mui/material/Dialog';
import DialogActions from '@mui/material/DialogActions';
import DialogContent from '@mui/material/DialogContent';

import {Typography} from '@mui/material';
import React from "react";

const SignUpDialog = ({open, handleClose}) => {

    const [markdown, setMarkdown] = React.useState(undefined);
    const [version, setVersion] = React.useState(undefined);


    React.useEffect(() => {
        fetch('/web/current-version').then(res => res.text()).then(setVersion);
    }, []);

    return (
        <Dialog open={open} onClose={handleClose}>
            <DialogContent>
                {!version ?
                    <Typography>Loading</Typography> :
                    <Typography variant="h5" gutterBottom component="div">
                        Current version: {version}
                    </Typography>}
                <Typography marginTop={"20px"}>
                    Discover the latest updates, enhancements, and newly introduced features in our software. Checkout our <a
                    href=" https://furthrmind.com/docs" target="_blank" rel="noopener noreferrer">
                         Release notes
                    </a>
                </Typography>

            </DialogContent>
            <DialogActions>
                <Button onClick={handleClose} color="success">Awesome!</Button>
            </DialogActions>
        </Dialog>
    )
}

export default SignUpDialog;