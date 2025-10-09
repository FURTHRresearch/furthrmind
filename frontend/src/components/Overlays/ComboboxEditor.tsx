import LoadingButton from "@mui/lab/LoadingButton";
import {IconButton, MenuItem, TextField, Typography} from "@mui/material";
import Box from "@mui/material/Box";
import Modal from '@mui/material/Modal';
import Tab from "@mui/material/Tab";
import Tabs from "@mui/material/Tabs";
import Menu from "@mui/material/Menu"
import axios from "axios";
import debounce from "lodash/debounce";
import * as React from "react";
import {useEffect, useState} from "react";
import useSWR from "swr";

import AddField from "../Fields/AddField";

import Grid from '@mui/material/Grid';
import DraggableFields from "../DraggableFields/draggableFields";
import MoreVertIcon from "@mui/icons-material/MoreVert";
import DeleteIcon from "@mui/icons-material/Delete";
import Dialog from "@mui/material/Dialog";
import DialogTitle from "@mui/material/DialogTitle";
import DialogContent from "@mui/material/DialogContent";
import DialogContentText from "@mui/material/DialogContentText";
import DialogActions from "@mui/material/DialogActions";
import Button from "@mui/material/Button";


const ComboboxEditor = ({show, onClose, fieldId, fieldName, admin}) => {

    return (
        <Modal open={show} onClose={onClose} style={{maxHeight: "80vh", maxWidth: "64vw", margin: 'auto'}}>
            {<TabbedComboboxEditor fieldId={fieldId} fieldName={fieldName} admin={admin}/>}
        </Modal>

    )
}

export default ComboboxEditor;

const fetcher = (url) => fetch(url).then((res) => res.json());

function TabPanel(props) {
    const {children, value, index, ...other} = props;

    return (
        <div
            role="tabpanel"
            hidden={value !== index}
            {...other}
        >
            {value === index && (
                <Box>
                    <Typography>{children}</Typography>
                </Box>
            )}
        </div>
    );
}

function TabbedComboboxEditor({fieldId, fieldName, admin}) {
    const [value, setValue] = React.useState(0);
    const [activeOption, setActiveOption] = React.useState(undefined);
    const [activeOptionID, setActiveOptionID] = React.useState("-");
    const [activeOptionName, setActiveOptionName] = React.useState("-");
    const [newEntryName, setNewEntryName] = React.useState("");
    const [creatingEntry, setCreatingEntry] = React.useState(false);
    const [anchorEl, setAnchorEl] = React.useState<null | HTMLElement>(null);
    const [deleteDialogOpen, setDeleteDialogOpen] = useState(false)
    const handleChange = (event: React.SyntheticEvent, newValue: number) => {
        setValue(newValue);
    };
    const {data: combos, mutate: mutateCombos} = useSWR(
        "/web/comboboxentries/" + fieldId + "/entries",
        fetcher
    );

    const createEntry = () => {
        // name is required
        if (newEntryName) {
            setCreatingEntry(true);
            axios
                .post("/web/comboboxentries/" + fieldId + "/entries", {
                    name: newEntryName,
                })
                .then((r) => {
                    let newCombos = combos.concat({
                        id: r.data.id,
                        name: newEntryName,
                        fields: []
                    }).sort((a, b) => a.name.localeCompare(b.name));
                    mutateCombos(newCombos);
                    setNewEntryName("");
                    setCreatingEntry(false);
                    setValue(newCombos.findIndex((c) => c.id === r.data.id));
                });
        }
    };

    const optionNameChanged = (e: any) => {
        setActiveOptionName(e.target.value)
    };

    const optionNameFocusLost = (e: any, id: string) => {
        const newCombos = combos.map(option =>
            option.id === id ? {...option, name: e.target.value} : option
        );
        mutateCombos(newCombos, false);
        axios.post("/web/comboboxentries/" + id, {name: e.target.value})
    };

    const {data, mutate} =
        useSWR("/web/comboboxentries/" + activeOptionID, fetcher)

    const fieldAdded = (field, optionId) => {
        let combosCopy = [...combos]
        combosCopy.map((c) => {
            if (c.id === optionId) {
                c["fields"] = [...c["fields"], field]
                data["fields"] = c["fields"]
                mutate(data)
            }
        })
        mutateCombos(combosCopy)

    }

    useEffect(() => {
        setActiveOption(combos[value])
        setActiveOptionID("-")
        if (combos[value] !== undefined) {
            setActiveOptionID(combos[value].id)
            setActiveOptionName(combos[value].name)
        }

    }, [combos, value]);

    return (
        <Box
            sx={{
                bgcolor: "background.paper",
                display: "flex",
                flexGrow: 1,
                padding: "16px",
            }}
        >
            <Grid container spacing={2}>
                <Grid item xs={12}>
                    <h3>List options for field: '{fieldName}'</h3>
                </Grid>
                <Grid item xs={4}>
                    <Tabs
                        orientation="vertical"
                        variant="scrollable"
                        value={value}
                        onChange={handleChange}
                        aria-label="Vertical tabs example"
                        sx={{
                            borderRight: 1,
                            border: 1,
                            borderColor: "divider",
                            overflow: "auto",
                            maxHeight: "50vh",
                        }}
                    >
                        {combos.length > 0 &&
                            combos.map((option: any, index) => (
                                <Tab label={option.name} id={option.id} key={option.id}
                                     sx={{textTransform: "none"}}/>
                            ))}
                    </Tabs>
                </Grid>
                <Grid item xs={8}>
                    {activeOption &&
                        <TabPanel
                            value={value}
                            index={value}
                            sx={{padding: '0px 24px !important'}}
                        >
                            <div style={{maxHeight: '50vh', overflowY: 'auto', overflowX: 'hidden'}}>
                                {(activeOptionID !== undefined) &&
                                    <Box display={"flex"}>
                                        <TextField
                                            margin="dense"
                                            label="Name"
                                            fullWidth
                                            value={activeOptionName}
                                            onChange={(e: any) => optionNameChanged(e)}
                                            onBlur={(e: any) => optionNameFocusLost(e, activeOptionID)}
                                        />
                                        <IconButton
                                            size="small"
                                            onClick={(event) => setAnchorEl(event.currentTarget)}
                                            sx={{
                                                opacity: 0.5,
                                                marginRight: '-12px'
                                            }}
                                        >
                                            <MoreVertIcon/>
                                        </IconButton>
                                        <Menu anchorEl={anchorEl}
                                              open={Boolean(anchorEl)}
                                              onClose={() => setAnchorEl(null)}
                                              onClick={() => setAnchorEl(null)}>
                                            <MenuItem onClick={() => setDeleteDialogOpen(true)}>
                                                <span style={{color: "red"}}><DeleteIcon/> Delete entry</span>
                                            </MenuItem>
                                        </Menu>
                                        <DeleteDialog
                                            label={"List option"} comboID={activeOptionID}
                                            handleClose={() => setDeleteDialogOpen(false)}
                                            open={deleteDialogOpen}
                                            combos={combos}
                                            mutateCombos={mutateCombos}
                                            setValue={setValue}
                                        />
                                    </Box>}

                                {!activeOptionID ?
                                    <>Loading...</> :
                                    <ComboBoxFieldList activeOptionID={activeOptionID} admin={admin}/>}
                            </div>
                        </TabPanel>}
                </Grid>
                <Grid item xs={4}>
                    <div>
                        <Box sx={{display: "flex", columnGap: "10px", marginRight: "10px"}}>
                            <TextField
                                fullWidth
                                label="Add a new entry"
                                id="fullWidth"
                                size="small"
                                placeholder="Add a new entry"
                                value={newEntryName}
                                onChange={(e) => setNewEntryName(e.target.value)}
                                disabled={creatingEntry}
                                onKeyDown={(e) => (e.key === "Enter" ? createEntry() : null)}
                            />
                            <LoadingButton
                                color="primary"
                                variant="contained"
                                onClick={() => createEntry()}
                                loading={creatingEntry ? true : false}
                                disabled={(!newEntryName || creatingEntry) && !admin}
                            >
                                Add
                            </LoadingButton>
                        </Box>
                    </div>
                </Grid>
                <Grid item xs={8}>
                    <AddField
                        onAdded={(field) => fieldAdded(field, activeOptionID)}
                        target="comboboxentries"
                        targetId={activeOptionID}
                        notebook={false}
                        admin={admin}/>
                </Grid>
            </Grid>
        </Box>
    );
}


function ComboBoxFieldList({activeOptionID, admin}) {
    const [comboID, setComboID] = useState(activeOptionID)
    const [loaded, setLoaded] = useState(false)

    const {data: option, mutate: mutateOption} = useSWR(
        "/web/comboboxentries/" + comboID,
        fetcher
    );
    useEffect(() => {
        setLoaded(false)
        setComboID(activeOptionID)
    }, [activeOptionID]);

    useEffect(() => {
        if (option !== undefined) {
            setLoaded(true)
        } else {
            setLoaded(false)
        }
    }, [option, comboID]);

    const handleFieldValueChange = (id, val) => {
        const newFields = option["fields"].map(f => {
            return (f.id === id) ? {...f, Value: val} : f;
        })
        mutateOption({...option, fields: newFields}, false);

    }

    const handleFieldUnitChange = (id, val) => {
        const newFields = option["fields"].map(f => {
            return (f.id === id) ? {...f, UnitID: val} : f;
        })
        mutateOption({...option, fields: newFields}, false);
    }

    const updateFieldOnDragEnd = (result, fields) => {
        const {
            destination: {index: destinationIndex},
            source: {index: sourceIndex},
        } = result;
        if (destinationIndex !== sourceIndex) {
            const newFields = option["fields"].slice();
            newFields.splice(destinationIndex, 0, newFields.splice(sourceIndex, 1)[0]);
            mutateOption({...option, fields: newFields}, false);
            axios.put(`/web/comboboxentries/${activeOptionID}/fields`, {'fieldDataIds': newFields.map(f => f.id)});
        }
    };

    return <>
        {!loaded ? <>Loading</> :
            <DraggableFields
                fields={option["fields"]}
                isParent={false}
                parentID={comboID}
                parentType={'comboboxentries'}
                autoExpanded={true}
                updateFieldOnDragEnd={updateFieldOnDragEnd}
                onFieldValueChange={handleFieldValueChange}
                onFieldUnitChange={handleFieldUnitChange}
                controlled={false}
                admin={admin}
            />}
    </>
}


const DeleteDialog = ({open, handleClose, label, comboID, combos, mutateCombos, setValue}) => {
    const [loading, setLoading] = React.useState(false);
    React.useEffect(() => {
        setLoading(false);
    }, [open]);


    const deleteItem = () => {
        setLoading(true);

        axios.delete(`/web/comboboxentries/${comboID}`).then(() => {
            const dataCopy = []
            combos.map((c) => {
                if (c.id !== comboID) {
                    dataCopy.push(c)
                }
            })
            mutateCombos(dataCopy)
            setValue(0)
            handleClose();
        });
    }
    return (
        <Dialog open={open} onClose={handleClose}>
            <DialogTitle>Remove {label}?</DialogTitle>
            <DialogContent>

                <DialogContentText>
                    This will remove the option from your list field and will remove it
                    everywhere it was used.
                </DialogContentText>

            </DialogContent>
            <DialogActions>
                <Button onClick={handleClose} disabled={loading}>Cancel</Button>
                <LoadingButton loading={loading} onClick={deleteItem} color="warning">Remove</LoadingButton>
            </DialogActions>
        </Dialog>
    )
}