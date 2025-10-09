import React from 'react';

import AwsS3Multipart from '@uppy/aws-s3-multipart';
import Uppy from '@uppy/core';
import '@uppy/core/dist/style.css';
import '@uppy/dashboard/dist/style.css';
import { DashboardModal, useUppy } from '@uppy/react';

import UploadFileIcon from '@mui/icons-material/UploadFile';

import {IconButton} from "@mui/material";


const S3FileUploadButton = ({ onUploaded }) => {
  const [open, setOpen] = React.useState(false);
  const uppy = useUppy(() => {
    return new Uppy({
      autoProceed: true,
    }).use(AwsS3Multipart, {
      limit: 4,
      companionUrl: '/web/',
    }).on('complete', result => {
      onUploaded(result.successful.map(rs => rs.uploadURL.split('/')[2]));
    })
  });

  return (
    <div>

      <IconButton sx={{ color: "black" }} onClick={() => setOpen(true)} style={{ width: "100%" }} >

        <UploadFileIcon />
      </IconButton>

      {open && <DashboardModal
        uppy={uppy}
        closeModalOnClickOutside
        open={open}
        onRequestClose={() => setOpen(false)}
        proudlyDisplayPoweredByUppy={false}
      />}
    </div>
  )
}

export default S3FileUploadButton;
