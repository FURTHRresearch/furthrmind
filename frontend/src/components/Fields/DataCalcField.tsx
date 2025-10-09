import EditIcon from '@mui/icons-material/Edit';
import ExpandLessIcon from '@mui/icons-material/ExpandLess';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import {LoadingButton} from '@mui/lab';
import {Box, Button, IconButton, Paper, Stack, Tooltip, Typography} from '@mui/material';
import useMediaQuery from '@mui/material/useMediaQuery';
import axios from 'axios';
import {useEffect, useState} from 'react';
import WebDataCalcOverlay from '../Overlays/WebDataCalcOverlay';
import classes from './DataCalcFieldStyle.module.css';
import FieldMenu from './FieldMenu';
import {useSWRConfig} from "swr"

const DataCalcField = ({label, data, ...other}) => {
    const {parentId, parentType} = other;
    const {mutate} = useSWRConfig()

    const matches = useMediaQuery('(max-width:768px)');
    const [showOverlay, setShowOverlay] = useState(false);
    const [showResult, setShowResult] = useState(false);
    const [running, setRunning] = useState(false);
    const [result, setResult] = useState(data.calculationResult);

    const runScript = () => {
        setRunning(true);
        axios.post(`/web/webdatacalc/${data.id}/run`, {'experimentId': parentId}).then(r => {
            setRunning(false);
            if (r.data.response.stderr !== '') alert(r.data.response.stderr);
            else {
                const resultObject = JSON.parse(r.data.response.stdout)
                setResult(resultObject);
            }
            
            mutate(`/web/item/${parentType}/${parentId}`)
        });
    }

    useEffect(() => {
        if (result) {
            setShowResult(true);
        }
    }, [result]);


    return (
        <>
            <Tooltip title={label} placement={"left"} enterDelay={400} enterNextDelay={400}>

                <div className={classes.parentWrapper}>
                    <Stack
                        direction='row' justifyContent='space-between' alignItems='center' sx={{width: '100%'}}>
                        <div className={classes.labelCss}>{label}</div>
                        <Stack direction='row'>
                            <LoadingButton size='small' color='success' startIcon={<PlayArrowIcon/>} onClick={runScript}
                                           loading={running}>Run</LoadingButton>
                            <Tooltip
                                title={!((data.calculationType === "WebDataCalc") || (data.calculationType === "Spreadsheet")) ? "Legacy calculations can only be edited in the desktop app" : ""}
                                arrow placement="top">
                                <Button
                                    component="div"
                                    size='small'
                                    sx={{
                                        "&.Mui-disabled": {
                                            pointerEvents: "auto"
                                        }
                                    }}
                                    startIcon={<EditIcon/>}
                                    onClick={() => setShowOverlay(true)}
                                    disabled={!((data.calculationType === "WebDataCalc") || (data.calculationType === "Spreadsheet"))}
                                >Edit</Button>
                            </Tooltip>
                            <IconButton aria-label="expand" onClick={() => setShowResult(prev => !prev)}>
                                {!showResult ? <ExpandMoreIcon sx={{
                                    color: '#28231d'
                                }}/> : <ExpandLessIcon
                                    sx={{
                                        color: '#28231d'
                                    }}
                                />}
                            </IconButton>
                        </Stack>
                    </Stack>


                    {
                        showResult && <Paper
                            elevation={0}
                            sx={{
                                padding: '8px 12px',
                                margin: '8px 0px'
                            }}
                        >
                            {!result && <Typography>No result</Typography>}
                            {result && <Box>
                                <Typography>Results :</Typography>
                                {Object.entries(result).map(([k, v], i) => {
                                    return (
                                        <Stack
                                            alignItems='center'
                                            direction='row'
                                            justifyContent="space-between"
                                            flexGrow={1}
                                            sx={{
                                                width: '100%'
                                            }}
                                        >
                                            <Typography>{k} :</Typography>
                                            <Typography>{v}</Typography>
                                        </Stack>
                                    )
                                })}
                            </Box>}
                        </Paper>
                    }

                </div>
            </Tooltip>
            {((data.calculationType === "WebDataCalc") || (data.calculationType === "Spreadsheet")) && showOverlay &&
                <WebDataCalcOverlay
                    parentId={parentId}
                    parentType={parentType}
                    data={data}
                    show={showOverlay}
                    onClose={() => setShowOverlay(false)}
                    {...other}
                />}
            <FieldMenu label={label} {...other} />

        </>
    )
}

export default DataCalcField;
