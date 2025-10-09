import React from 'react';
import RawData from '../RawData';

import Box from '@mui/material/Box';
import Modal from '@mui/material/Modal';

const style = {
  position: 'absolute' as 'absolute',
  top: '50%',
  left: '50%',
  transform: 'translate(-50%, -50%)',
  overflowY: "scroll",
  width: '80vw',
  maxHeight: '90vh'
};
const RawDataOverlay = ({ show, onClose, rawid, onExited, writable, itemData, mutateItem}) => {

  return (
    <Modal
      open={show}
      onClose={onClose}
    >
      <Box sx={style}>
        <RawData rawid={rawid} writable={writable} itemData={itemData} mutateItem={mutateItem} onClose={onClose} />
      </Box>
    </Modal>
  );
}

export default React.memo(RawDataOverlay);