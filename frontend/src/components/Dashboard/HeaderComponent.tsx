import React, {memo, useEffect, useState} from "react";
import {useNavigate, useParams} from "react-router-dom";
import axios from "axios";
import classes from "../../pages/DashboardStyle.module.css";
import MoreVertIcon from "@mui/icons-material/MoreVert";
import Popover from "@mui/material/Popover";
import EditIcon from "@mui/icons-material/Edit";
import Typography from "@mui/material/Typography";
import RefreshIcon from "@mui/icons-material/Refresh";
import DeleteIcon from "@mui/icons-material/Delete";
import {refreshChart} from "@syncfusion/ej2-react-spreadsheet";

function HeaderComponent({id, name, handleChartRefresh, handleDelete}) {

    const [anchorEl, setAnchorEl] = React.useState(null);
    const [updated, setUpdated] = useState("");
    const params = useParams();

    useEffect(() => {
        axios.get(`/dataviews/${id}/updated`).then(r => {
            setUpdated(r.data);
        });
    }, [])

    useEffect(() => {
        if (refreshChart === "") {
            axios.get(`/dataviews/${id}/updated`).then(r => {
                setUpdated(r.data);
            });
        }

    }, [refreshChart])

    const handleClick = (event) => {
        setAnchorEl(event.currentTarget);
    };

    const navigate = useNavigate();

    const handleClose = () => {
        setAnchorEl(null);
    };


    const handleEdit = () => {
        navigate(`/projects/${params.project}/dataviews/${id}`,
            {state: {resetFilter: true}});
    }

    function handleUpdate() {
        handleChartRefresh(id)
    }

    function onDelete() {
        handleDelete(id)
    }

    return (
        <div>
            <div className={classes.headerWrapper}>
                <div className={classes.headerTitle}>
                    {name}
                </div>
                <div className={classes.ellipsesIcon} onClick={handleClick}>
                    <MoreVertIcon sx={{fontSize: "16px"}}/>
                </div>
            </div>
            <div className={classes.subHeading}>
                Last Updated : {updated}
            </div>
            <HeaderPopover
                anchorEl={anchorEl}
                handleClose={handleClose}
                onEdit={handleEdit}
                onDelete={onDelete}
                onUpdate={handleUpdate}
            />
        </div>
    )
}


function HeaderPopover({anchorEl, handleClose, onEdit, onDelete, onUpdate}) {

    const open = Boolean(anchorEl);
    const id = open ? 'simple-popover' : undefined;

    return (
        <div>
            <Popover
                id={id}
                open={open}
                anchorEl={anchorEl}
                onClose={handleClose}
                anchorOrigin={{
                    vertical: 'bottom',
                    horizontal: 'left',
                }}
            >
                <div className="d-flex align-items-center" onClick={() => onEdit()}>
                    <div>
                        <EditIcon sx={{fontSize: "18px", marginLeft: "10px"}}/>
                    </div>
                    <div><Typography sx={{p: 1, cursor: "pointer", fontSize: "16px"}}>Edit data</Typography></div>
                </div>
                <div className="d-flex align-items-center" onClick={() => onUpdate()}>
                    <div>
                        <RefreshIcon sx={{fontSize: "18px", marginLeft: "10px"}}/>
                    </div>
                    <div><Typography sx={{p: 1, cursor: "pointer", fontSize: "16px"}}>Update chart</Typography>
                    </div>
                </div>
                <div className="d-flex align-items-center" onClick={() => onDelete()}>
                    <div>
                        <DeleteIcon sx={{fontSize: "18px", marginLeft: "10px"}}/>
                    </div>
                    <div><Typography sx={{p: 1, cursor: "pointer", fontSize: "16px"}}>Delete dashboard</Typography>
                    </div>
                </div>
            </Popover>
        </div>
    );
}

export default memo(HeaderComponent);