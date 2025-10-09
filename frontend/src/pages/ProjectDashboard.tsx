import {Chart as ChartJS, Legend, LinearScale, LineElement, PointElement, Tooltip} from 'chart.js';
import React, {useEffect, useRef, useState} from 'react';
import {useNavigate, useParams} from "react-router-dom";
import useSWR from 'swr';
import SideDrawer from '../components/SideDrawer';
import classes from './DashboardStyle.module.css';
import './ProjectDashboard.css';

import {DashboardLayoutComponent, PanelDirective, PanelsDirective} from '@syncfusion/ej2-react-layouts';
import axios from 'axios';
import NoData from '../components/NoData/NoData';
import useFilterStore from "../zustand/filterStore";
import {TextField} from "@mui/material";
import Dialog from "@mui/material/Dialog";
import DialogTitle from "@mui/material/DialogTitle";
import DialogContent from "@mui/material/DialogContent";
import DialogContentText from "@mui/material/DialogContentText";
import DialogActions from "@mui/material/DialogActions";
import Button from "@mui/material/Button";
import LoadingButton from "@mui/lab/LoadingButton";
import DataViewChart from "../components/Dashboard/DataViewChart";
import HeaderComponent from "../components/Dashboard/HeaderComponent";

const fetcher = (url) => fetch(url).then((res) => res.json());

ChartJS.register(LinearScale, PointElement, LineElement, Tooltip, Legend);

export default function DasboardPage() {
    const cellSpacing = [10, 10]
    const chartRef = useRef([]);
    const dashboardLayoutRef = useRef(null);
    const params = useParams();
    const navigate = useNavigate();
    const [openDialog, setOpenDialog] = React.useState(false);
    const resetFilter = useFilterStore((state) => state.resetFilter);

    useEffect(() => {
        resetFilter()
    }, []);


    const {data: dataviews, mutate: mutateDataviews} = useSWR(`/web/projects/${params.project}/dataviews`, fetcher);

    const [refreshChart, setRefreshChart] = React.useState({});

    const [dashBoards, setDashBoards] = useState([])
    // useEffect(() => {
    //     if (dataviews) {
    //         const dashBoards = dataviews.map((dataview, i) => {
    //             return {
    //                 id: dataview.id,
    //                 sizeX: dataview.sizeX,
    //                 sizeY: dataview.sizeY,
    //                 row: dataview.row,
    //                 col: dataview.col,
    //                 content: (props) => DataViewChart(props),
    //                 header: (props) => HeaderComponent(props),
    //                 contentProps: {dataview, refreshChart, setRefreshChart},
    //                 headerProps: {dataview, handleDelete, handleChartRefresh},
    //             }
    //
    //         })
    //         setDashBoards(dashBoards)
    //     } else {
    //         setDashBoards([])
    //     }
    //
    // }, [dataviews]);


    function handleDelete(dataviewId) {
        axios.delete(`/dataviews/${dataviewId}`).then(r => {
            const newDV = []
            dataviews.map((dv) => {
                if (dv.id != dataviewId) {
                    newDV.push(dv)
                }
            })
            mutateDataviews(newDV)
        })
    }

    function handleChartRefresh(dataviewId) {
        setRefreshChart(dataviewId)

    }

    function handlePanelPositionChange() {
        const updatedPosition = dashboardLayoutRef.current.serialize();
        const newConfig = updatedPosition.map((panel, index) => {
            const {row, col, sizeX, sizeY} = panel;
            return {
                id: dataviews[index].id,
                row,
                col,
                sizeX,
                sizeY
            }
        });
        axios.post(`/web/projects/${params.project}/dataviews/positions`, newConfig);
    }


    function handleClose() {
        setOpenDialog(false);
    }

    function handleCreateDashboard(name) {
        let displayedColumns = ["Name", "Type"]
        let displayedCategories = ["all"]
        axios.post(`/dataviews`, {
            filterList: [],
            nameFilter: "",
            projectId: params.project,
            name: name,
            displayedColumns,
            includeLinked: "none",
            displayedCategories: displayedCategories
        }).then(r => {
            setOpenDialog(false)
            navigate(`/projects/${params.project}/dataviews/` + r.data.id,
                {state: {resetFilter: false}});
        })
    }

    function handleOpenDialog() {
        setOpenDialog(true);
    }

    function dataViewChart(dataview, refreshChart, setRefreshChart) {
        return (
            <DataViewChart dataview={dataview} refreshChart={refreshChart} setRefreshChart={setRefreshChart}/>
        )
    }

    function headerComponent(id, name) {
        return (
            <HeaderComponent id={id} name={name} handleChartRefresh={handleChartRefresh} handleDelete={handleDelete}/>
        )
    }

    return (
        <div className={classes.pageStyle} style={{minHeight: '100vh'}}>
            <SideDrawer/>
            <div className={classes.pageInnerWrapper}>
                <div className={classes.headingWrapper}>
                    <div className={classes.heading}>
                        Project Dashboards
                    </div>

                    <Button variant="outlined" onClick={handleOpenDialog}
                            style={{marginLeft: "auto", textTransform: 'uppercase'}}>
                        Create new chart
                    </Button>

                    <div>
                        {/* <Button variant="outlined" disabled>Do stuff</Button> */}
                    </div>
                </div>

                {dataviews && dataviews.length === 0 && <NoData
                    heading='No charts'
                />}
                {dataviews && dataviews.length > 0 && <div>
                    <DashboardLayoutComponent
                        id="analytic_dashboard"
                        cellSpacing={cellSpacing}
                        columns={4}
                        allowDragging={true}
                        draggableHandle='.e-panel-content'
                        allowResizing={true}
                        ref={dashboardLayoutRef}
                        allowFloating={true}
                        resizeStop={handlePanelPositionChange}
                        change={handlePanelPositionChange}
                    >
                        <PanelsDirective>

                            {
                                dataviews.map((dv, index) => {
                                    // const headerProps = {
                                    //     index: index,
                                    //     name: dv.name,
                                    //     id: dv.id,
                                    //     sizeX: dv.sizeX,
                                    //     sizeY: dv.sizeY,
                                    //     row: dv.row,
                                    //     col: dv.col,
                                    // };
                                    // const contentProps = {
                                    //     dataview: dv,
                                    //     index: index,
                                    //     id: dv.id,
                                    //     refreshChart,
                                    //     setRefreshChart
                                    // };

                                    return (
                                        <PanelDirective sizeX={dv.sizeX} sizeY={dv.sizeY} row={dv.row}
                                                        col={dv.col}
                                                        content={() => dataViewChart(
                                                            dv, refreshChart, setRefreshChart)}
                                                        header={() => headerComponent(dv.id, dv.name)}></PanelDirective>
                                    )
                                })
                            }
                        </PanelsDirective>
                    </DashboardLayoutComponent>
                </div>
                }


                <div>
                    {openDialog && <GenericDialog
                        title="Create new chart "
                        handleClose={handleClose}
                        open={openDialog}
                        primaryActionText="Create"
                        handleSubmit={handleCreateDashboard}
                    >

                    </GenericDialog>}
                </div>


            </div>
        </div>
    )
}


const GenericDialog = (props) => {
    const {title, subInfo, open, handleClose, handleSubmit, primaryActionText, dataResult} = props;
    const [newDashboardName, setNewDashboardName] = useState(false);
    function handleSetNewDashboardName(e) {
        setNewDashboardName(e.target.value)
    }

    return (
        <Dialog open={open} onClose={handleClose} fullWidth>
            <DialogTitle>{title}</DialogTitle>
            <DialogContent>

                {subInfo && <DialogContentText>
                    {subInfo}
                </DialogContentText>}
                {props.children}
                <TextField id="outlined-basic" label="Enter the dashboard name" variant="outlined" fullWidth
                           name="templateName"
                           onChange={handleSetNewDashboardName}
                />
            </DialogContent>
            <DialogActions>
                {dataResult != false && <Button onClick={handleClose}>Cancel</Button>}
                {dataResult != false &&
                    <LoadingButton onClick={() => handleSubmit(newDashboardName)} color="warning">{primaryActionText}</LoadingButton>}
                {dataResult == false &&
                    <LoadingButton onClick={handleClose} color="warning">{primaryActionText}</LoadingButton>}
            </DialogActions>
        </Dialog>
    )
}