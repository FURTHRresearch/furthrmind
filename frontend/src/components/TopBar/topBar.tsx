import CalendarViewMonthIcon from "@mui/icons-material/CalendarViewMonth";
import CalendarViewWeekIcon from "@mui/icons-material/CalendarViewWeek";
import ClearIcon from "@mui/icons-material/Clear";
import CompareIcon from '@mui/icons-material/Compare';
import KeyboardArrowDownIcon from "@mui/icons-material/KeyboardArrowDown";
import KeyboardArrowUpIcon from "@mui/icons-material/KeyboardArrowUp";
import axios from "axios";
import {useNavigate, useParams} from "react-router-dom";
import useFilterStore from '../../zustand/filterStore';
import {useMultiSelectStore} from '../../zustand/multiSelectStore';
import classes from "./styles.module.css";
import FileUploadButton from "../UploadButton/FileUploadButtonTopBar";

import excelSvg from "../../images/excelPng.png";

import {IconButton, Tooltip} from "@mui/material";
import React from "react";

import Dialog from "@mui/material/Dialog";
import DialogTitle from "@mui/material/DialogTitle";
import DialogContent from "@mui/material/DialogContent";
import DialogActions from "@mui/material/DialogActions";
import Button from "@mui/material/Button";
import LoadingButton from "@mui/lab/LoadingButton";
import FormControl from "@mui/material/FormControl";
import FormLabel from "@mui/material/FormLabel";
import RadioGroup from "@mui/material/RadioGroup";
import FormControlLabel from "@mui/material/FormControlLabel";
import Radio from "@mui/material/Radio";

const TopBar = ({
                    name,
                    handleCompare,
                    onViewTypeChange,
                    viewType,
                    showGroupProperties,
                    onShowGroupPropertiesChange,
                }) => {
    const [selectedSpreadsheet, setSelectedSpreadsheet] = React.useState('None');
    const [showOpenSpreadsheetDialog, setShowOpenSpreadsheetDialog] = React.useState(false);
    const [dataResult, setDataResult] = React.useState();
    const multiSelectStore = useMultiSelectStore();
    const {project: projectId} = useParams();

    const filterList = useFilterStore((state) => state.filterList);
    const nameFilter = useFilterStore((state) => state.nameFilter);

    const clearAllSelection = () => {
        multiSelectStore.clearAllSelected();
    };

    const navigate = useNavigate();
    const params = useParams();

    const createDataView = () => {
        let name = null
        let displayedColumns = ["Name", "Type"]
        axios.post(`/dataviews`, {
            filterList,
            nameFilter,
            projectId,
            name,
            displayedColumns
        }).then(r => {
            navigate(`/projects/${params.project}/dataviews/` + r.data.id,
                {state: {resetFilter: false}});
        })
    }

    const openSpreadsheets = () => {
        const idString = multiSelectStore.selected

        function openInOnlyOffice(idString, spreadsheetId) {
            const a = document.createElement('a')
            a.href = "/web/onlyoffice/" + idString + "/" + spreadsheetId;
            document.body.appendChild(a)
            a.setAttribute('target', '_blank');
            a.click()
            document.body.removeChild(a)
        }

        const axiosTest = axios.get
        axiosTest('/web/onlyoffice/spreadsheets/' + idString).then(function (axiosTestResult) {
                const data = axiosTestResult.data;
                const existing = data.exists;

                if (existing == true) {
                    const spreadsheetId = data.results[0].id
                    openInOnlyOffice(idString, spreadsheetId)
                } else {
                    const spreadsheetId = "None"
                    openInOnlyOffice(idString, spreadsheetId)
                }
                // } else if (data.results.length === 0) {
                //     const spreadsheetId = "None"
                //     openInOnlyOffice(idString, spreadsheetId)
                //
                // } else {
                //     setDataResult(data.results)
                //     setShowOpenSpreadsheetDialog(true)
                // }
            }
        )
    };


    const closeOpenSpreadsheetsDialog = () => {
        setSelectedSpreadsheet('');
        setShowOpenSpreadsheetDialog(false)
    }

    const filesUploaded = (uuids) => {
        // axios.post(`/web/${data.id}/files`, { uuids }).then((res) => {
        //     mutate({ ...data, files: [...files, ...res.data] });
        // });
    };


    return (
        <React.Fragment>

            <div className={classes.topBar}>
                <div className={classes.titleWrap}
                     onClick={() => onShowGroupPropertiesChange(!showGroupProperties)}>
                    <div className={classes.titleCss}>{name}</div>
                    <div>
                        {showGroupProperties ? (
                            <KeyboardArrowUpIcon/>
                        ) : (
                            <KeyboardArrowDownIcon/>
                        )}
                    </div>
                </div>
                <div className={classes.iconsList}>
                    {multiSelectStore.selected.length > 0 && <React.Fragment>
                        {/* <div>
                                <DeleteIcon />
                            </div> */}
                        <Tooltip title="Clear">
                            <IconButton sx={{color: "black"}} onClick={clearAllSelection}>
                                <ClearIcon/>
                            </IconButton>
                        </Tooltip>

                        <Tooltip title="Compare">
                            <IconButton sx={{color: "black"}} onClick={handleCompare}>
                                <CompareIcon/>
                            </IconButton>
                        </Tooltip>

                        <Tooltip title="Open in spreadsheet">
                            <IconButton sx={{color: "black"}} onClick={openSpreadsheets}>
                                <img src={excelSvg} alt={""}/>
                            </IconButton>
                        </Tooltip>
                        {dataResult &&
                            <OpenSpreadsheetDialog setShowOpenSpreadsheetDialog={setShowOpenSpreadsheetDialog}
                                                   selectedSpreadsheet={selectedSpreadsheet}
                                                   setSelectedSpreadsheet={selectedSpreadsheet}
                                                   expIdString={multiSelectStore.selected}
                                                   open={showOpenSpreadsheetDialog}
                                                   handleClose={closeOpenSpreadsheetsDialog}
                                                   dataResult={dataResult}/>}


                        {(process.env.NODE_ENV === "development") && <Tooltip title="Upload file">
                            <FileUploadButton onUploaded={filesUploaded}/>
                        </Tooltip>}

                    </React.Fragment>
                    }
                    <div>
                        {viewType === 'cards' ? (
                            <Tooltip title="Table view">
                                <IconButton sx={{color: "black"}} onClick={() => onViewTypeChange("table")}>
                                    <CalendarViewMonthIcon/>
                                </IconButton>
                            </Tooltip>
                        ) : (
                            <Tooltip title="Card view">
                                <IconButton sx={{color: "black"}} onClick={() => onViewTypeChange("cards")}>
                                    <CalendarViewWeekIcon/>
                                </IconButton>
                            </Tooltip>

                        )}

                    </div>
                    {/*<Tooltip title={"Add a data analysis chart."}>*/}
                    {/*    <span>*/}
                    {/*        <IconButton onClick={createDataView} sx={{*/}
                    {/*            color: 'black',*/}
                    {/*            "&.Mui-disabled": {*/}
                    {/*                pointerEvents: "auto"*/}
                    {/*            }*/}
                    {/*        }}>*/}
                    {/*            <AddchartIcon/>*/}
                    {/*        </IconButton>*/}
                    {/*    </span>*/}
                    {/*</Tooltip>*/}
                </div>

            </div>
        </React.Fragment>
    );
};

export default TopBar;

const OpenSpreadsheetDialog = ({
                                   open,
                                   handleClose,
                                   dataResult,
                                   expIdString,
                                   setSelectedSpreadsheet,
                                   selectedSpreadsheet,
                                   setShowOpenSpreadsheetDialog
                               }) => {

    const handleRadioChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        setSelectedSpreadsheet((event.target as HTMLInputElement).value)
    };

    const handleOpenAsTemplate = () => {
        function openInOnlyOffice(expIdString, spreadsheetId) {
            const a = document.createElement('a')
            a.href = "/web/onlyoffice/" + expIdString + "/" + spreadsheetId;
            document.body.appendChild(a)
            a.setAttribute('target', '_blank');
            a.click()
            document.body.removeChild(a)
        }

        const spreadsheetId = selectedSpreadsheet

        openInOnlyOffice(expIdString, spreadsheetId)
        setShowOpenSpreadsheetDialog(false)


    }

    return (

        <Dialog open={open} onClose={handleClose} fullWidth>
            <DialogTitle>Choose "Your worksheet":</DialogTitle>
            <DialogContent>
                <FormControl>

                    <FormLabel id="demo-radio-buttons-group-label">Would you like import the "Your worksheet" sheet from
                        an exiting spreadsheet? Please select:</FormLabel>
                    <RadioGroup
                        aria-labelledby="demo-radio-buttons-group-label"
                        defaultValue="None"
                        name="radio-buttons-group"
                        onChange={handleRadioChange}
                    >
                        <hr/>
                        <FormControlLabel value="None" control={<Radio/>} label="Blank"/>
                        <hr/>
                        {dataResult.map(data => {
                            return (
                                <div>
                                    <FormControlLabel value={data.id} control={<Radio/>} label={data.name}/>
                                    <hr/>
                                </div>
                            )
                        })}


                    </RadioGroup>

                </FormControl>

            </DialogContent>
            <DialogActions>
                <Button onClick={handleClose}>Cancel</Button>
                <LoadingButton onClick={handleOpenAsTemplate} color="warning">Open</LoadingButton>
            </DialogActions>
        </Dialog>

    )
}
