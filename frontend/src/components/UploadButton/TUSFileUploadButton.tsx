import React from 'react';

import Uppy from '@uppy/core';
import '@uppy/core/dist/style.css';
import '@uppy/dashboard/dist/style.css';
import {DashboardModal} from '@uppy/react';
import Tus from '@uppy/tus';

import UploadIcon from '@mui/icons-material/Upload';
import Button from "@mui/material/Button";


class TUSFileUploadButton extends React.Component<{ onUploaded: any }, { open: boolean }> {
    uppy: any;

    constructor(props: any) {
        super(props);
        this.state = {
            open: false
        };

        this.uppy = new Uppy({
            autoProceed: true,
        }).use(Tus, {endpoint: '/tus-upload', chunkSize: 1 * 1024 * 1024})
            .on('complete', result => {
                let uuids = result.successful.map(rs => rs.uploadURL.split('/')[2]);
                this.props.onUploaded(uuids, result);
            });
    }

    componentWillUnmount() {
        this.uppy.close()
    }

    render() {
        return (
            <div>
                <Button size="small" variant="outlined" startIcon={<UploadIcon/>}
                        onClick={() => this.setState({open: true})} style={{width: "100%"}}>
                    Upload file
                </Button>
                {open && <DashboardModal
                    uppy={this.uppy}
                    closeModalOnClickOutside
                    open={this.state.open}
                    onRequestClose={() => this.setState({open: false})}
                    proudlyDisplayPoweredByUppy={false}
                />}
            </div>
        )
    }
}

export default TUSFileUploadButton;
