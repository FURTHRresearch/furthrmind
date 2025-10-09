import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import {Button} from '@mui/material';
import {useParams} from 'react-router-dom';
import classes from './AppCard.module.css';
import React from "react";
import Iframe from 'react-iframe'
import {useState, useEffect} from "react";
import ReactModal from "react-modal";
import OpenApp from "../Overlays/OpenApp"


export default function AppCard({data}) {

    const params = useParams()

    const [showApp, setShowApp] = useState(false);


    function onClickMethod() {

        setShowApp(true)
        // window.location.href = `/web/projects/${params.project}/apps/${app_id}/content/index.html`
    }


    return (
        <div
            className={classes.appCardWrapper}
        >
            <div className={classes.appCardHeader}>
            </div>

            <div className={classes.title}>
                {data.name}
            </div>
            <div className={classes.subTitle}>
                {data.description}
            </div>
            <div>
                Version: {data.version}
            </div>
            <div className={classes.authorWrapper}>
                <div>
                    {data.author}
                </div>
            </div>
            <div>
                <Button variant="outlined" startIcon={<PlayArrowIcon/>} onClick={onClickMethod}>
                    Run
                </Button>

                {showApp ? <OpenApp
                    onClose={() => setShowApp(false)}
                    show={showApp}
                    app_url={data.url}
                /> : null}


            </div>
        </div>
    )
}
