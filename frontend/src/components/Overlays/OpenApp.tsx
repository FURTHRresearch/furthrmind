import Notebook from '../Notebook';

import Box from '@mui/material/Box';
import Modal from '@mui/material/Modal';
import Iframe from "react-iframe";
import React, {useRef} from "react";
import {useParams} from 'react-router-dom';
import axios from "axios";


const style = {
    position: 'absolute' as 'absolute',
    top: '50%',
    left: '50%',
    transform: 'translate(-50%, -50%)',
    width: '95%',
    height: '90%',
    background: 'white',
};

const OpenApp = ({show, onClose, app_url}) => {
    const params = useParams()

    // const url = `/web/projects/${params.project}/apps/${app_id}/content/index.html`

    // const app = useRef()
    var api_key = ""

    function timeoutedMessage() {
        setTimeout(sendMessage, 1000)
    }

    function sendMessage() {
        axios.post("/api2/key").then(res => {
            const api_key = res.data
            axios.get("/web/webapp-callback").then(res => {
                document.querySelector("iframe").contentWindow.postMessage({
                "host": res.data,
                "origin": window.location.origin,
                "projectID": params.project,
                "apiKey": api_key
            }, app_url)
            })
        })

        // window.postMessage({"host": window.location.origin, "projectID": params.project}, "*")
    }

    return (
        <Modal
            open={show}
            onClose={onClose}
        >
            <Box sx={style}>
                <Iframe url={app_url} width={"100%"} height={"100%"} onLoad={timeoutedMessage} id={"iframe"}/>
            </Box>
        </Modal>
    );
}

export default OpenApp;