import React, {useCallback, useEffect, useRef, useState} from 'react';

import {Scatter} from "react-chartjs-2";
import DataGrid, {TextEditor} from 'react-data-grid';

import debounce from 'lodash/debounce';

import _ from 'lodash';

import {useParams} from 'react-router-dom';

import {Button, Paper, Stack, Typography} from '@mui/material';
import useSWR from 'swr';
import ChartEditorOverlay from './Overlays/ChartEditorOverlay';
import axios from "axios";
import Dialog from "@mui/material/Dialog";
import DialogTitle from "@mui/material/DialogTitle";
import DialogContent from "@mui/material/DialogContent";
import DialogContentText from "@mui/material/DialogContentText";
import DialogActions from "@mui/material/DialogActions";
import LoadingButton from "@mui/lab/LoadingButton";
import DownloadIcon from "@mui/icons-material/Download";
import DeleteIcon from "@mui/icons-material/Delete";
import Tooltip from "@mui/material/Tooltip";
import classes from "./Setting/General/style.module.css";
import EditIcon from "@mui/icons-material/Edit";
import {useWindowWidth} from "@react-hook/window-size";

const fetcher = url => fetch(url).then(res => res.json());

const dummyChartData = [
    {
        id: '62cc1f741b5538d365a94caa',
        name: 'Feed concentartion vs Permeate concentration',
        xAxis: 'Feed concentartion', yAxis: 'Permeate concentration'
    },
    {
        id: '62cc1f741b5538d365a94caa',
        name: 'Feed concentartion vs Permeate concentration',
        xAxis: 'Feed concentartion', yAxis: 'Permeate concentration'
    },
    {
        id: '62cc1f741b5538d365a94caa',
        name: 'Feed concentartion vs Permeate concentration',
        xAxis: 'Feed concentartion', yAxis: 'Permeate concentration'
    }
]

const dummyData = [{
    "Feed concentartion": [10, 100, 120, 140, 150, 65, 70, 80, 90, 100],
    "Permeate concentration": [30, 40, 5, 60, 110, 80, 99, 77, 55, 66]
}]
const RawData = ({rawid, writable = true, itemData, mutateItem, onClose}) => {
    const [showChartEditor, setShowChartEditor] = useState(false);
    const [openDelete, setOpenDelete] = useState(false);
    const [columns, setColumns] = React.useState([]);
    const [rows, setRows] = React.useState([]);
    const [downloadPrepare, setDownloadPrepare] = React.useState(false);
    const [editMode, setEditMode] = React.useState(false);
    const [name, setName] = React.useState("")

    const onlyWidth = useWindowWidth();

    const lastDataCols = React.useRef({});

    const params = useParams();
    const {data: units} = useSWR(`/web/units?project=${'project' in params ? params.project : ''}`, fetcher, {dedupingInterval: 10000});

    const createGridData = useCallback((data: any) => {
        let columns = [];
        let rowNumber = data.columns[0].Data.length;
        let rows = new Array(rowNumber).fill(undefined).map(u => ({}));
        for (const col of data.columns) {
            const colId = col.id;
            lastDataCols.current[colId] = col.Data;

            const unit = (col.UnitID !== null && units) ? (' [' + units.find(u => u.id === col.UnitID)?.Name + ']') : '';
            let c = {
                key: colId,
                name: col.Name + unit,
                editor: TextEditor,
            };

            columns.push(c);
            for (var i = 0; i < rowNumber; i++) {
                // @ts-ignore
                rows[i][col.id] = col.Data[i];
            }
            addEmptyRow(rows)
        }
        setColumns(columns);
        setRows(rows);
    }, [units]);

    useEffect(() => {
        fetch('/web/rawdata/' + rawid)
            .then((response) => response.json())
            .then((d) => {
                setName(d.name)
                createGridData(d);
            });
    }, [rawid, createGridData]);

    const saveColumn = (colId: string, data: any) => {
        fetch('/columns/' + colId, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        })
    }

    const compareDataAndSave = useRef(debounce((rows: any) => {
        let newDataCols = {};
        for (const row of rows) {
            for (const colId in row) {
                if (!newDataCols[colId]) {
                    newDataCols[colId] = [];
                }
                newDataCols[colId].push(row[colId]);
            }
        }
        for (const [key, value] of Object.entries(newDataCols)) {
            if (!_.isEqual(lastDataCols.current[key], value)) {
                saveColumn(key, value);
                lastDataCols.current[key] = value;
            }
        }
    }, 500)).current;

    const handleRowsChange = (rows: any) => {
        const rowsForSaving = [...rows]
        addEmptyRow(rows)
        setRows(rows);
        removeEmptyRows(rowsForSaving)
        compareDataAndSave(rowsForSaving);

    }

    function removeEmptyRows(rows: any) {
        let check = true

        while (check) {
            if (rows.length === 0) {
                check = false
            } else {
                let lastRow = rows[rows.length - 1];
                let removeRow = true
                for (const colId in lastRow) {
                    if ((lastRow[colId] !== undefined) && (lastRow[colId] !== null) && (lastRow[colId] !== "")) {
                        removeRow = false
                    }
                }
                if (removeRow) {
                    rows.pop()
                } else {
                    check = false
                }
            }
        }
    }

    function addEmptyRow(rows: any) {
        let lastRow = rows[rows.length - 1];
        let addRow = false
        for (const colId in lastRow) {
            if ((lastRow[colId] !== undefined) && (lastRow[colId] !== null) && (lastRow[colId] !== "")) {
                addRow = true;
                break
            }

        }
        if (addRow) {
            let newRow = {}
            for (const colId in lastRow) {
                newRow[colId] = undefined;
            }
            rows.push(newRow)
        }
    }

    const handleCreateChartForTableView = () => {
        setShowChartEditor(true);
    }

    function handleDeleteClose() {
        onClose()
        setOpenDelete(false)
    }

    const handleChartClose = () => {
        setShowChartEditor(false);
    }

    function downloadCSV() {

        const downloadFile = (file_id) => {
            function download() {
                const a = document.createElement('a')
                const url = "/web/files/" + file_id + "?download=true"
                a.href = url
                a.download = url.split('/').pop()
                document.body.appendChild(a)
                a.click()
                document.body.removeChild(a)
            }

            download()
        }
        setDownloadPrepare(true)
        axios.get("/rawdata/" + rawid + "/csv")
            .then((response) => {
                    const file_id = response.data
                    downloadFile(file_id)
                    setDownloadPrepare(false)
                }
            )
    }

    const handleEditState = (state: any) => {
        setEditMode(state)
    }

    const saveName = () => {
        axios.post(`/web/rawdata/${rawid}`, {name: name});
        setEditMode(false);
        const copyItemDataRadata = [...itemData.rawdata]
        copyItemDataRadata.map((rawdata) => {
            if (rawdata.id === rawid) {
                rawdata.name = name
            }
        })
        mutateItem({...itemData, rawdata: copyItemDataRadata})
    }

    return (Object.keys(columns).length === 0) ? (<>Loading...</>) : (
        <Paper style={{padding: '12px 16px'}}>
            <Stack direction={"row"}>
                <Typography style={{width: "250px"}} variant="h6" gutterBottom component="div">
                    Raw data table name:
                </Typography>
                <div className={classes.textFieldOuterWrap}>
                    <div className={classes.textField}>
                        <input
                            type="text"
                            placeholder="Table name"
                            className={!editMode ? classes.inputFieldReadOnly : classes.inputField}
                            value={name}
                            readOnly={!editMode}
                            onChange={(e) => {
                                setName(e.target.value)
                            }
                            }
                        />
                        {!editMode &&
                            <EditIcon sx={{fontSize: onlyWidth < 576 ? "14px" : "18px", cursor: "pointer"}}
                                      onClick={() => handleEditState(true)}
                            />
                        }
                    </div>
                    {
                        editMode &&
                        <div className={classes.editStateWrap}>
                            <Button
                                variant="outlined"
                                size="small"
                                onClick={() => handleEditState(false)}
                            >Cancel</Button>
                            <Button variant="contained" size="small" onClick={saveName}>Save</Button>
                        </div>
                    }
                </div>
                <div
                    style={{alignItems: "flex-end", justifyContent: 'flex-end', marginLeft: "auto"}}
                >
                    {/*<Button*/}
                    {/*    variant='contained'*/}
                    {/*    disabled*/}
                    {/*    onClick={handleCreateChartForTableView}*/}
                    {/*>CREATE CHART</Button>*/}
                    <Tooltip title={"Download raw data as csv"}>
                        <LoadingButton
                            loading={downloadPrepare}
                            onClick={() => downloadCSV()}
                        >
                            <DownloadIcon/>
                        </LoadingButton>
                    </Tooltip>
                    <Tooltip title={"Delete raw data"}>
                        <LoadingButton
                            onClick={() => setOpenDelete(true)}
                        >
                            <DeleteIcon/>
                        </LoadingButton>
                    </Tooltip>


                </div>
            </Stack>

            {/*<Stack direction='column'>*/}

            {/* <Box mt={4} mb={8}>
                    <div style={{
                        fontFamily: "Roboto",
                        fontSize: "18px",
                        fontWeight: 600,
                        lineHeight: "18px",
                        letterSpacing: "0.1px",
                        color: "black",
                        textDecoration: "underline",
                        paddingLeft: "24px"
                    }}>Charts</div>

                    <Container>
                        <Grid container mt={2} spacing={2}>
                            {dummyChartData && dummyData &&
                                dummyChartData.map((chart, index) => (
                                    <Grid md={4} item>
                                        <Paper>

                                            <ScatterChart
                                                data={dummyData}
                                                chart={chart}
                                            />

                                        </Paper>
                                    </Grid>
                                ))}
                        </Grid>
                    </Container>
                </Box> */}


            {/*</Stack>*/}
            <DataGrid
                columns={columns}
                rows={rows}
                style={{height: '65vh', marginTop: "30px"}}
                onRowsChange={handleRowsChange}
                defaultColumnOptions={{
                    resizable: true,                 
                  }}
                
            />
            {showChartEditor && <ChartEditorOverlay
                columns={columns}
                rows={rows}
                show={showChartEditor}
                onClose={handleChartClose}
            />}
            <div style={{display: "flex", marginTop: "30px", marginBottom: "30px", marginRight: "30px"}}>

                <Button
                    variant={"outlined"}
                    onClick={onClose}
                    style={{width: "100px", height: "50px", marginLeft: "auto"}}
                >Close</Button>
            </div>
            <DeleteDialog open={openDelete} handleClose={handleDeleteClose}
                          id={rawid} name={"raw data"} itemData={itemData} mutateItem={mutateItem}/>
        </Paper>
    )

}

export default RawData;


function ScatterChart({chart, data}) {
    const {xAxis, yAxis} = chart;
    return (<Scatter
        data={{
            datasets: [
                {
                    label: `${xAxis} vs ${yAxis}`,
                    data: data.map((d) => {
                        return {x: d[xAxis], y: d[yAxis]};
                    }),
                    backgroundColor: "rgba(255, 99, 132, 1)",
                },
            ],
        }}
        options={{
            scales: {
                y: {
                    title: {
                        display: true,
                        text: yAxis,
                    },
                },
                x: {
                    title: {
                        display: true,
                        text: xAxis,
                    },
                },
            },
        }}
    />)
}


const DeleteDialog = ({open, handleClose, name, id, itemData, mutateItem}) => {
    const [loading, setLoading] = React.useState(false);
    const params = useParams();

    const deleteItem = () => {
        setLoading(true);
        let rawdata = []
        let itemDataCopy = {...itemData}
        axios.delete(`/web/rawdata/${id}`).then(() => {
            handleClose();
            itemData.rawdata.map((r) => {
                if (r.id !== id) {
                    rawdata.push(r)
                }
            })
            itemDataCopy.rawdata = rawdata
            mutateItem(itemDataCopy)

        });
    }
    return (
        <Dialog open={open} onClose={handleClose}>
            <DialogTitle>Delete {name}?</DialogTitle>
            <DialogContent>

                <DialogContentText></DialogContentText>

            </DialogContent>
            <DialogActions>
                <Button onClick={handleClose} disabled={loading}>Cancel</Button>
                <LoadingButton loading={loading} onClick={deleteItem} color="warning">Delete</LoadingButton>
            </DialogActions>
        </Dialog>
    )
}