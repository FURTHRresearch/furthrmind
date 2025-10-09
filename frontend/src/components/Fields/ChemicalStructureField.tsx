import axios from 'axios';
import React, {useEffect, useState} from 'react';
import useSWR from "swr";
import useDebouncedEffect from '../../hooks/useDebouncedEffect';
import SmilesDrawerComponent from '../SmilesDrawerComponent';
import StructureEditor from "../StructureEditor";
import FieldMenu from './FieldMenu';
import Box from '@mui/material/Box';
import Modal from '@mui/material/Modal';
import Typography from "@mui/material/Typography";
import MenuItem from "@mui/material/MenuItem";
import Divider from "@mui/material/Divider";
import ScienceIcon from "@mui/icons-material/Science";
import Tooltip from "@mui/material/Tooltip";
import {Stack} from "@mui/material";

const fetcher = (url) => fetch(url).then((res) => res.json());

const ChemicalStructureField = ({value, initialSmiles, ...other}) => {
    const [showEditor, setShowEditor] = useState(false);
    const [smiles, setSmiles] = useState(initialSmiles);
    useDebouncedEffect(() => {
        axios.post('/web/fielddata/' + other.fieldDataId, {value})
    }, 500, [value]);

    return (
        <Tooltip title={other.label} placement={"left"} enterDelay={400} enterNextDelay={400}>
            <Stack direction={"row"} width={"100%"}>
                {(smiles !== "") ? <div>
                    <Box display={"grid"} marginTop={"10px"}>
                        <Typography variant={"subtitle2"} marginLeft={"15px"}>
                            {other.label}
                        </Typography>
                        <Box display={"block"}>
                            <SmilesDrawerComponent smiles={smiles}/>

                        </Box>

                    </Box>

                </div> : <div>

                    <Typography variant={"subtitle2"} marginLeft={"15px"}>
                        {other.label}
                    </Typography>
                </div>}

                {
                    !other.menuDisabled && <Box marginLeft={"auto"} marginTop={"auto"} marginBottom={"auto"}>
                        <ChemicalStructureMenu fieldId={other.fieldDataId} label={other.label} {...other}
                                               setShowEditor={setShowEditor}/>
                    </Box>
                }


                <StructureEditorOverlay show={showEditor} handleClose={() => setShowEditor(false)} id={value}
                                        onChange={setSmiles}/>
            </Stack>


        </Tooltip>

    )
}

export default ChemicalStructureField;

const overlayBoxStyle = {
    position: 'absolute' as 'absolute',
    top:
        '50%',
    left:
        '50%',
    transform:
        'translate(-50%, -50%)',
    width:
        '80vw',
    background:
        'white',
};

const StructureEditorOverlay = ({
                                    handleClose,
                                    id,
                                    show,
                                    onChange,
                                }) => {
    const [isLoaded, setIsLoaded] = useState(false);
    const [initialStructure, setInitialStructure] = useState("");

    const {data} = useSWR("/web/chemicalstructures/" + id, fetcher);

    useEffect(() => {
        if (data) {
            if (data["cdxml"]) {
                setInitialStructure(data["cdxml"])
            } else {
                setInitialStructure(data["smiles"])
            }
            setIsLoaded(true);
        }

    }, [data]);

    const structureChanged = (smiles, cdxml) => {
        onChange(smiles);
        axios.post("/web/chemicalstructures/" + id, {
            smiles: smiles,
            cdxml: cdxml,
        });
    };

    return (
        <Modal
            open={show}
            onClose={handleClose}
        >
            <Box sx={overlayBoxStyle}>
                {data ? (
                    <div>
                        {isLoaded ? (
                            // <Suspense fallback={<div>Loading...</div>}>
                            <StructureEditor
                                height="600px"
                                initialStructure={initialStructure}
                                onChange={structureChanged}
                            />
                            // </Suspense>
                        ) : (
                            <div>Loading...</div>
                        )}
                    </div>
                ) : null}
            </Box>
        </Modal>
    );
};

const ChemicalStructureMenu = (props) => {
    const [showStructureEditor, setShowSTructureEditor] = React.useState(false);
    const [viewAuthorOverlay, setViewAuthorOverlay] = React.useState(false);
    const closeViewAuthorOverlayHandler = () => {
        setViewAuthorOverlay(false);
    }
    return (
        <>
            <FieldMenu {...props}>
                <MenuItem onClick={() => {
                    props.setShowEditor(true);
                }}>
                    <span><ScienceIcon/> Edit structure</span>
                </MenuItem>
                <Divider/>
                {/*<MenuItem onClick={() => setViewAuthorOverlay(true)}>*/}
                {/*  <span><PersonIcon /> View Author</span>*/}
                {/*</MenuItem>*/}
            </FieldMenu>

        </>
    )
}