
import React from 'react';

import Box from '@mui/material/Box';
import Modal from '@mui/material/Modal';
import DataViewForTable from '../../pages/DataViewForTable';

const style = {
    position: 'absolute' as 'absolute',
    top: "0%",
    left: '10%',
    background: 'white',
    right: '10%'
};
const ChartEditorOverlay = ({ show, onClose, columns, rows, writable = true }) => {

    return (
        <Modal
            open={show}
            onClose={onClose}
        >
            <Box sx={style}>
                <DataViewForTable columns={columns} rows={rows} onClose={onClose} />
            </Box>
        </Modal>
    );
}

export default React.memo(ChartEditorOverlay);