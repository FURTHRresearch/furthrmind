import Notebook from '../Notebook';

import Box from '@mui/material/Box';
import Modal from '@mui/material/Modal';

const style = {
  position: 'absolute' as 'absolute',
  top: '50%',
  left: '50%',
  transform: 'translate(-50%, -50%)',
  width: '80vw',
  background: 'white',
};

const NotebookOverlay = ({ show, onClose, notebookId, onChange = (v) => null }) => {
  return (
    <Modal
      open={show}
      onClose={onClose}
    >
      <Box sx={style}>
        <Notebook notebookId={notebookId} onChange={onChange} />
      </Box>
    </Modal>
  );
}

export default NotebookOverlay;