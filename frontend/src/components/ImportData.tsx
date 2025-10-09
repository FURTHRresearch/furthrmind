import React, {useEffect, useState} from 'react';

import {Scatter} from "react-chartjs-2";
import DataGrid from 'react-data-grid';

import {useParams} from 'react-router-dom';

import {Box, Button, FormControl, InputLabel, Paper, Stack} from '@mui/material';
import Papa from "papaparse/papaparse"
import Select from "@mui/material/Select";
import Typography from "@mui/material/Typography";
import KeyboardArrowUpIcon from "@mui/icons-material/KeyboardArrowUp";
import KeyboardArrowDownIcon from "@mui/icons-material/KeyboardArrowDown";
import classes from "./TopBar/styles.module.css";
import TextField from "@mui/material/TextField";
import axios from "axios"
import {LoadingButton} from "@mui/lab";
import Dialog from "@mui/material/Dialog";
import DialogTitle from "@mui/material/DialogTitle";
import DialogContent from "@mui/material/DialogContent";
import DialogContentText from "@mui/material/DialogContentText";
import DialogActions from "@mui/material/DialogActions";
import {preview} from "vite";

const fetcher = url => fetch(url).then(res => res.json());

const testData = {
    "id": "65844440fd95065a6f53cfb2",
    "Name": "HFs_LBL_p_10_i_Layer_1_10.csv"
}

const testData2 = {
    "id": "65844f11fd95065a6f53cfc0",
    "Name": "HFs_LBL_p_10_i_Layer_1_10 with comma.csv"
}

const columnDelimiter = [
    "auto", ",", ";", "tab"
]


const ImportData = ({fileList, itemId, itemType, itemData, mutateItem, onClose}) => {
    const [fileString, setFileString] = useState("")
    const [columns, setColumns] = React.useState([]);
    const [rows, setRows] = React.useState([]);
    const [textData, setTextData] = React.useState("");
    const [selectedFileId, setSelectedFileId] = React.useState(fileList[0].id)
    const [showAdvancedOptions, setShowAdvancedOptions] = React.useState(false)
    const [delimiter, setDelimiter] = useState({})
    const [headerNumber, setHeaderNumber] = useState({})
    const [rawDataName, setRawDataName] = useState({})
    const [imported, setImported] = useState({})
    const [loading, setLoading] = useState(false)
    const [openNotification, setOpenNotification] = useState(false)


    useEffect(() => {
        if (fileList.length === 1) {
            setFileString("file")
        } else {
            setFileString("files")
        }
        let headerNumberCopy = {}
        let delimiterCopy = {}
        let rawDataNameCopy = {}
        let importedCopy = {}
        fileList.map((f) => {
            headerNumberCopy[f.id] = 0
            delimiterCopy[f.id] = columnDelimiter[0]
            rawDataNameCopy[f.id] = "Data table"
            importedCopy[f.id] = false
        })
        setHeaderNumber(headerNumberCopy)
        setDelimiter(delimiterCopy)
        setRawDataName(rawDataNameCopy)
        setImported(importedCopy)
    }, [fileList]);


    const params = useParams();

    function parseData(data, config) {
        Papa.parse(data, config)
    }

    function onParsePreviewComplete(data: any) {
        createGridData(data)
    }

    function createGridData(data: any) {
        let columns = []
        let rows = []
        let rowIndex = 0
        let columnNameList = []
        let headerRow = 0
        if (headerNumber[selectedFileId] !== undefined) {
            headerRow = headerNumber[selectedFileId]
        }
        if (data.data) {
            data.data.map((row) => {
                    if (rowIndex >= Number(headerRow)) {
                        let rowDict = {}
                        let columnIndex = 0
                        row.map((val) => {
                            if (rowIndex - Number(headerRow) === 0) {
                                if (columnNameList.includes(val)) {

                                }
                                columns.push({
                                    "key": columnIndex,
                                    "name": val
                                })
                            } else {
                                if (columnIndex < columns.length) {
                                    rowDict[columnIndex] = val
                                }
                            }
                            columnIndex += 1
                        })
                        if (Object.keys(rowDict).length > 0) {
                            rows.push(rowDict)
                        }
                    }
                    rowIndex += 1
                }
            )
            setColumns(columns)
            setRows(rows)
        }


    };

    function transform_value(val, col) {
        let valNumber = Number(val)
        if (isNaN(valNumber)) {
            let newVal = val.replace(",", ".")
            newVal = Number(newVal)
            if (isNaN(newVal)) {
                return val
            } else {
                return newVal
            }
        } else {
            return valNumber
        }
    }


    useEffect(() => {
        fetch(`/web/files/${selectedFileId}`)
            .then((response) => response.text())
            .then((data) => {
                setTextData(data)
            });
    }, [selectedFileId]);

    useEffect(() => {
        let del = ""
        if (delimiter[selectedFileId] !== undefined) {
            del = delimiter[selectedFileId]
        }
        if (del === "auto") {
            del = ""
        } else if (del === "tab") {
            del = "\t"
        }
        let skip = 0
        if (headerNumber[selectedFileId] !== undefined) {
            skip = Number(headerNumber[selectedFileId])
        }
        let preview = skip + 20
        let parseConfigPreview = {
            "delimiter": del,
            "newline": "",
            "preview": preview,
            "transform": transform_value,
            "complete": onParsePreviewComplete,
            "skipFirstNLines": skip
        }

        parseData(textData, parseConfigPreview);
    }, [textData, delimiter, headerNumber]);


    function importData() {
        let del = ""
        if (delimiter[selectedFileId] !== undefined) {
            del = delimiter[selectedFileId]
        }
        if (del === "auto") {
            del = ""
        } else if (del === "tab") {
            del = "\t"
        }
        let skip = 0
        if (headerNumber[selectedFileId] !== undefined) {
            skip = Number(headerNumber[selectedFileId])
        }

        let parseConfigFinal = {
            "delimiter": del,
            "newline": "",
            "transform": transform_value,
            "complete": onParseFinalComplete,
            "skipFirstNLines": skip
        }
        parseData(textData, parseConfigFinal)

    }

    function prepareColumnData(data: any) {

        let columns = []
        let rowIndex = 0
        let columnNameList = []
        let headerRow = 0
        if (headerNumber[selectedFileId] !== undefined) {
            headerRow = headerNumber[selectedFileId]
        }
        if (data.data) {
            data.data.map((row) => {
                    if (rowIndex >= Number(headerRow)) {
                        let rowDict = {}
                        let columnIndex = 0
                        row.map((val) => {
                            if (rowIndex - Number(headerRow) === 0) {
                                if (columnNameList.includes(val)) {

                                }
                                columns.push({
                                    "name": val,
                                    "data": []
                                })
                            } else {
                                if (columnIndex < columns.length) {
                                    columns[columnIndex]["data"].push(val)
                                }
                            }
                            columnIndex += 1
                        })
                    }
                    rowIndex += 1
                }
            )

        }
        return columns


    };

    function onParseFinalComplete(parsedData) {
        let columns = prepareColumnData(parsedData)
        let name = rawDataName[selectedFileId]
        let data = {
            "name": name,
            "columns": columns
        }
        setLoading(true)
        axios.post(`/web/rawdata/${itemType}/${itemId}`, data).then((r) => {
            let raw_data_id = r.data
            let importedCopy = {...imported}
            importedCopy[selectedFileId] = true
            setImported(importedCopy)
            setLoading(false)
            setOpenNotification(true)
            mutateItem({...itemData, rawdata: [...itemData.rawdata, {id: raw_data_id, name: name}]})
        })
    }

    function fileChanged(e) {
        setSelectedFileId(e.target.value)
    }

    function onShowAdvancedOptions(value: boolean) {
        setShowAdvancedOptions(value)
    }

    function headerRowChanged(value) {
        value = value.split(".")[0]
        let headerNumberCopy = {...headerNumber}
        headerNumberCopy[selectedFileId] = value
        setHeaderNumber(headerNumberCopy)
    }

    function rawDataNameChanged(value) {
        let rawDataNameCopy = {...rawDataName}
        rawDataNameCopy[selectedFileId] = value
        setRawDataName(rawDataNameCopy)
    }

    function onKeyPressHeader(event) {
        if ([",", "."].includes(event.key)) {
            event.preventDefault()
        }
    }

    function delimiterChanged(event) {
        let value = event.target.value
        let delimiterCopy = {...delimiter}
        delimiterCopy[selectedFileId] = value
        setDelimiter(delimiterCopy)

    }

    return <div>
        <Paper style={{padding: '12px 16px'}}>
            <Typography variant={"h6"}>We found {fileList.length} {fileString} that can be imported</Typography>
            <Box
                display='flex'
                justifyContent='flex'
                my={3}
            >   {fileList && <Box display={"block"}>
                <FormControl>
                    <InputLabel variant={"filled"}> Select a file</InputLabel>
                    <Select
                        variant="filled"
                        label={"Select a file"}
                        value={selectedFileId}
                        onChange={(e) => fileChanged(e)}
                        native={true}
                        style={{width: "500px", height: "60px"}}
                    >
                        {fileList.map((option,) => <option key={option.id}
                                                           value={option.id}>{option['Name']}</option>)}
                    </Select>
                </FormControl>

            </Box>}

                <Box width={"100%"}></Box>
                <LoadingButton
                    variant={"outlined"}
                    onClick={importData}
                    style={{width: "300px", height: "50px", alignContent: "center"}}
                    disabled={imported[selectedFileId]}
                    loading={loading}
                >Import data
                </LoadingButton>
            </Box>
            <Box display={"flex"}>
                <div className={classes.titleWrap}
                     onClick={() => onShowAdvancedOptions(!showAdvancedOptions)}>
                    <Typography variant={"subtitle2"} marginRight={"20px"}>Advanced options</Typography>

                    <div>
                        {showAdvancedOptions ? (
                            <KeyboardArrowUpIcon/>
                        ) : (
                            <KeyboardArrowDownIcon/>
                        )}
                    </div>
                </div>
            </Box>
            {showAdvancedOptions && <Stack marginTop="10px" spacing={"20px"} direction={"row"}>
                <FormControl>
                    <InputLabel variant={"filled"}> Column delimiter</InputLabel>
                    <Select
                        variant="filled"
                        // label={"Select a file"}
                        value={delimiter[selectedFileId]}
                        onChange={(e) => delimiterChanged(e)}
                        native={true}
                        style={{width: "150px"}}

                    >
                        {columnDelimiter.map(option => <option key={option}
                                                               value={option}>{option}</option>)}
                    </Select>
                </FormControl>
                <TextField
                    variant="filled"
                    label={"Header row"}
                    value={headerNumber[selectedFileId]}
                    onChange={(e) => headerRowChanged(e.target.value)}
                    style={{width: "150px"}}
                    type="number"
                    onKeyPress={(e) => onKeyPressHeader(e)}
                />

                <TextField
                    variant="filled"
                    label={"Raw data name"}
                    value={rawDataName[selectedFileId]}
                    onChange={(e) => rawDataNameChanged(e.target.value)}
                    style={{width: "200px"}}
                />
            </Stack>}
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

            <DataGrid
                columns={columns}
                rows={rows}
                style={{height: '55vh', marginTop: "20px"}}
                className="rdg-light"

            />

            <div style={{display: "flex", marginTop: "30px", marginBottom: "30px", marginRight: "30px"}}>

                <Button
                    variant={"outlined"}
                    onClick={onClose}
                    style={{width: "100px", height: "50px", marginLeft: "auto"}}
                >Close</Button>
            </div>


        </Paper>
        <GenericDialog title={"Import successful!"}
                       subInfo={"Your data have been successfully imported"} open={openNotification}
                       handleClose={() => setOpenNotification(false)}
                       primaryActionText={"Close"}
        />
    </div>


}

export default ImportData;


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

const GenericDialog = (props) => {
    const {title, subInfo, open, handleClose} = props;
    return (
        <Dialog open={open} onClose={handleClose} fullWidth>
            <DialogTitle>{title}</DialogTitle>
            <DialogContent>
                {subInfo && <DialogContentText>
                    {subInfo}
                </DialogContentText>}
                {props.children}
            </DialogContent>
            <DialogActions>
                <Button onClick={handleClose}>Ok</Button>
            </DialogActions>
        </Dialog>
    )
}
