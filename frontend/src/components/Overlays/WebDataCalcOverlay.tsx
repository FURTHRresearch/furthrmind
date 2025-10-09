import React, {useCallback} from 'react';

import Editor from "@monaco-editor/react";

import {LoadingButton} from '@mui/lab';
import {Box} from '@mui/material';
import Grid from '@mui/material/Grid';

import debounce from 'lodash/debounce';

import Modal from '@mui/material/Modal';

import axios from 'axios';
import useSWR, {useSWRConfig} from 'swr';

const style = {
    position: 'absolute' as 'absolute',
    top: '50%',
    left: '50%',
    transform: 'translate(-50%, -50%)',
    width: '80vw',
    background: 'white',
};

const WebDataCalcOverlay = ({data, show, onClose, parentId, parentType, ...other}) => {
    var editorRef = React.useRef(null);
    const [output, setOutput] = React.useState({stdout: '', stderr: '', error: '', message: ''});
    const [running, setRunning] = React.useState(false);
    const {mutate} = useSWRConfig()

    const {
        data: userCalc,
        mutate: mutateUserCalc
    } = useSWR(`/web/fields/${data.FieldID}/webdatacalcscript`, (url: string) => fetch(url).then(r => r.text()));
    // eslint-disable-next-line
    const saveCode = useCallback(debounce((code) => {
        axios.post('/web/webdatacalc/' + data.FieldID, {code});
        mutateUserCalc(code, false);
    }, 500), [data.FieldID]);

    const runScript = () => {
        setRunning(true);
        axios.post(`/web/webdatacalc/${data.id}/run`).then(r => {
            setRunning(false);
            setOutput(r.data.response);
            mutate(`/web/item/${parentType}/${parentId}`)

        });
    }

    return (
        <Modal open={show} onClose={onClose}>
            <Box sx={style}>
                <Grid container spacing={2}>
                    <Grid item xs={8}>
                        {userCalc !== undefined ? <Editor
                            height="80vh"
                            defaultLanguage={'python'}
                            path={'userCalc.py'}
                            defaultValue={userCalc}
                            theme={'light'}
                            onChange={(val) => saveCode(val)}
                            onMount={(editor) => editorRef.current = editor}
                            options={{
                                minimap: {
                                    enabled: false,
                                },
                            }}
                        /> : 'Loading...'}
                    </Grid>
                    <Grid item xs={4}>
                        <LoadingButton loading={running} sx={{margin: '16px 0'}} color='success' onClick={runScript}
                                       variant='contained'>Run</LoadingButton>
                        <div style={{maxHeight: '80vh', overflow: 'scroll'}}>
                            <h3>Output</h3>
                            <pre style={{whiteSpace: 'pre-wrap'}}>{output.stdout}</pre>
                            <h3>Errors</h3>
                            <p>{output.error}</p>
                            <p>{output.message}</p>
                            <pre>{output.stderr}</pre>
                            <h3>Documentation</h3>
                            <p>
                                <a href="https://sdk.furthrmind.com" target='_blank'
                                   rel='noreferrer'>Furthrmind python wrapper</a>
                            </p>
                            <p>
                                <a href="https://app.swaggerhub.com/apis-docs/furthr-research/API2/1.0.0"
                                   target='_blank' rel='noreferrer'>REST-API documentation</a>
                            </p>
                            <h3>Installed packages</h3>
                            <p>Next to the standard python libaries, the following packages are installed:<br/>
                            requests, pillow, numericalunits, pandas, scipy, numpy, openpyxl, docker, furthrmind.<br/>
                            If you need a package that is not listed here, just send us an email
                            to <a href="mailto:support@furthr-research.com">support@furthr-research.com</a></p>
                        </div>
                    </Grid>
                </Grid>
            </Box>
        </Modal>
    )
}

export default WebDataCalcOverlay;