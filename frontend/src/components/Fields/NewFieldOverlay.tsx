import React, {useCallback, useEffect, useState} from 'react';

import {FormControl, InputLabel, MenuItem, Select, Stack} from '@mui/material';
import Grid from '@mui/material/Grid';
import TextField from '@mui/material/TextField';
import axios from 'axios';

import LoadingButton from '@mui/lab/LoadingButton';
import Button from '@mui/material/Button';
import Dialog from '@mui/material/Dialog';
import DialogActions from '@mui/material/DialogActions';
import DialogContent from '@mui/material/DialogContent';
import DialogContentText from '@mui/material/DialogContentText';
import DialogTitle from '@mui/material/DialogTitle';
import {useParams} from 'react-router-dom';
import useSWR from 'swr';
import RadioGroup from "@mui/material/RadioGroup";
import Radio from "@mui/material/Radio";
import FormControlLabel from "@mui/material/FormControlLabel";
import debounce from "lodash/debounce";
import Typography from "@mui/material/Typography";

const fetcher = (url) => fetch(url).then((res) => res.json());

const NewFieldOverlay = ({
                             show,
                             onClose,
                             initialName,
                             onExited,
                             onCreated,
                             targetType,
                             targetId,
                             createNewNameOption,
                             project
                         }) => {
    const [newName, setNewName] = React.useState(initialName);
    const [type, setType] = React.useState('Numeric');
    const [createDisabled, setCreateDisable] = React.useState(false);
    const [creating, setCreating] = React.useState(false);
    const [calculationType, setCalculationType] = useState("Python");
    const [spreadSheetTemplate, setSpreadSheetTemplate] = useState(null);
    const [cell, setCell] = useState(null);
    const [check, setCheck] = React.useState(false)
    const [loading, setLoading] = React.useState(false)

    const {data: templates} = useSWR('/web/onlyoffice/' + project + '/spreadsheet_templates', fetcher);

    useEffect(() => {
        if (templates) {
            templates.results.unshift({id: "current_item",
                name: "Use the spreadsheet of the item the calculation belongs to"})
        }
    }, [templates]);

    useEffect(() => {
        if (initialName === createNewNameOption) {
            setNewName("")
        } else {
            setNewName(initialName);

        }
    }, [initialName]);

    useEffect(() => {
        setCreating(false);
    }, [show]);

    const params = useParams();

    const createField = () => {
        setCreating(true);
        axios.post(`/web/projects/${params.project}/fields`, {
            Name: newName,
            Type: type,
            targetType: targetType,
            targetId: targetId,
            spreadsheetTemplate: spreadSheetTemplate,
            cell: cell
        }).then(r => {
            onCreated(r.data);
            onClose()
        });
    }

    function onNameChange(event) {
        setNewName(event.target.value)
    }

    useEffect(() => {
        if (!newName) {
            setCreateDisable(true)
            return
        }
        if (type !== "RawDataCalc") {
            setCreateDisable(false)
            return;
        }
        if (calculationType === "Python") {
            setCreateDisable(false)
            return;
        } else {
            if (spreadSheetTemplate && cell) {
                setCreateDisable(false)
            } else setCreateDisable(true)
        }

    }, [newName, type, calculationType, spreadSheetTemplate, cell]);

    function handleRadioChange(event) {
        setCalculationType(event.target.value)
    }

    function spreadSheetTemplateChanged(event) {
        setSpreadSheetTemplate(event.target.value)
    }

    function cellChanged(event) {
        setCell(event.target.value)
    }

    function checkName(nameToBeChecked) {
        axios.post(`/web/project/${params.project}/field/check`, {name: nameToBeChecked}).then((r) => {
            if (r.data == "True") {
                setCheck(true)
            } else {
                setCheck(false)
            }
            setLoading(false)
        })
    }

    const debouncedCheck = useCallback(debounce(checkName, 200), []);

    useEffect(() => {
        if (newName === "") {
            setCheck(false)
            return;
        } else {
            setLoading(true)
            debouncedCheck(newName)
        }

    }, [newName]);

    return (

        <Dialog open={show} onClose={onClose} style={{marginLeft: "auto", marginRight: "auto", width: "50vh"}}>
            <DialogTitle>Create a new field</DialogTitle>
            <DialogContent>
                <DialogContentText>
                    The new field will be available throughout this project.
                </DialogContentText>
                <div style={{marginTop: '1em'}}></div>
                <Grid container spacing={2}>
                    <Grid item xs={12}>
                        <TextField
                            label="Name"
                            fullWidth
                            value={newName}
                            variant="standard"
                            placeholder={"Enter field name"}
                            onChange={onNameChange}
                        />
                        {!check && newName && !loading && < Typography style={{
                            color: 'red',
                            fontSize: '14px'
                        }}>Name already in use. Please choose another one</Typography>}
                    </Grid>
                    <Grid item xs={12}>
                        <FormControl fullWidth>
                            <InputLabel variant="standard">Type</InputLabel>
                            <Select
                                value={type}
                                variant="standard"
                                onChange={(e: any) => setType(e.target.value)}
                            >
                                <MenuItem value="RawDataCalc">Calculation</MenuItem>
                                <MenuItem value="CheckBox">Checkbox</MenuItem>
                                <MenuItem value="ChemicalStructure">Chemical structure</MenuItem>
                                <MenuItem value="Date">Date</MenuItem>
                                <MenuItem value="ComboBox">List field</MenuItem>
                                <MenuItem value="MultiLine">Notebook</MenuItem>
                                <MenuItem value="Numeric">Numeric</MenuItem>
                                <MenuItem value="NumericRange">Numeric range</MenuItem>
                                <MenuItem value="SingleLine">Textfield</MenuItem>

                            </Select>
                        </FormControl>
                    </Grid>
                </Grid>
                {(type === "RawDataCalc") &&
                    <RadioGroup
                        aria-labelledby="demo-radio-buttons-group-label"
                        defaultValue={calculationType}
                        name="radio-buttons-group"
                        onChange={handleRadioChange}
                    >
                        <Stack direction={"row"} style={{marginTop: "20px"}}>
                            <FormControlLabel value="Python" control={<Radio/>} label="Python"
                                              style={{marginLeft: "0px"}}/>
                            <FormControlLabel value="Spreadsheet" control={<Radio/>} label="From spreadsheet"
                                              style={{marginLeft: "auto", marginRight: "20px"}}/>
                        </Stack>

                    </RadioGroup>
                }
                {((calculationType === "Spreadsheet") && (type === "RawDataCalc")) &&
                    <Stack style={{marginTop: "20px"}} direction={"row"}>
                        <FormControl fullWidth>
                            <InputLabel variant="standard">Spreadsheet template</InputLabel>
                            <Select
                                value={spreadSheetTemplate}
                                variant="standard"
                                onChange={spreadSheetTemplateChanged}
                            >
                                {templates.results.map(option => <MenuItem key={option.id}
                                                                           value={option.id}>{option['name']}</MenuItem>)}

                            </Select>
                        </FormControl>
                        <TextField
                            label="Cell"
                            fullWidth
                            value={cell}
                            variant="standard"
                            placeholder={"e.g. 'A2'"}
                            onChange={cellChanged}
                            style={{width: "30%", marginLeft: "20px"}}
                        />
                    </Stack>

                }
            </DialogContent>
            <DialogActions>
                <Button onClick={onClose} disabled={creating}>Cancel</Button>
                <LoadingButton loading={creating} onClick={createField} disabled={!check || createDisabled}>Create
                    field</LoadingButton>
            </DialogActions>
        </Dialog>
    );
}

export default NewFieldOverlay