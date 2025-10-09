import React from 'react';
import ImportData from '../ImportData';

import Box from '@mui/material/Box';
import Modal from '@mui/material/Modal';
import {Button} from "@mui/material";

const style = {
    position: 'absolute' as 'absolute',
    top: '50%',
    left: '50%',
    transform: 'translate(-50%, -50%)',
    width: '80vw',
    maxHeight: '90vh',
    backgroundColor: "white",
};
const ImportDataOverlay = ({show, onClose, setOpenImportTool, fileList, itemId, itemType, mutateData, data}) => {

    return (
        <div>
            <Modal
                open={show}
                onClose={onClose}
            >
                <Box sx={style}>
                    <ImportData fileList={fileList} itemId={itemId} itemType={itemType} mutateItem={mutateData} itemData={data} onClose={onClose}/>

                </Box>

            </Modal>

        </div>


    )
        ;
}

export default React.memo(ImportDataOverlay);