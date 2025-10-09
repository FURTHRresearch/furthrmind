import AddIcon from "@mui/icons-material/Add";
import ClearIcon from "@mui/icons-material/Clear";
import SearchIcon from "@mui/icons-material/Search";
import {Button, Typography} from "@mui/material";
import {useWindowWidth} from "@react-hook/window-size";
import React, {useCallback, useEffect} from "react";
import FilterCard from "../SearchFilter/FilterCard";
import FilterEditor from "../SearchFilter/FilterEditor";
import FilterSummary from "../SearchFilter/FilterSummary";
import classes from "./style.module.css";

import useFilterStore from "../../zustand/filterStore";
import FormControlLabel from "@mui/material/FormControlLabel";
import IconButton from "@mui/material/IconButton";
import SaveIcon from "@mui/icons-material/Save";
import FormControl from "@mui/material/FormControl";
import RadioGroup from "@mui/material/RadioGroup";
import Radio from "@mui/material/Radio";
import Dialog from "@mui/material/Dialog";
import DialogTitle from "@mui/material/DialogTitle";
import DialogContent from "@mui/material/DialogContent";
import DialogContentText from "@mui/material/DialogContentText";
import DialogActions from "@mui/material/DialogActions";
import LoadingButton from "@mui/lab/LoadingButton";
import TextField from "@mui/material/TextField";
import debounce from "lodash/debounce";
import axios from "axios";
import {useParams} from "react-router-dom";
import useSWR from "swr";
import DeleteIcon from "@mui/icons-material/Delete";
import EditIcon from "@mui/icons-material/Edit";
import hash from "stable-hash";
import DisplayedCategories from "./DisplayedCategories";
import IncludeLinked from "./IncludeLinked";

const fetcher = (url) => fetch(url).then((res) => res.json());

function FilterBar(props) {
    const filterStore = useFilterStore();

    const initialFilterList = props.filterList
    const initialNameFilter = props.nameFilter
    const displayedColumns = props.displayedColumns
    const setDisplayedColumns = props.setDisplayedColumns
    const dataView = props?.dataView
    const params = useParams();


    const {data: savedFilter, mutate: mutateSavedFilter} = useSWR(`/web/project/${params.project}/filter`, fetcher);


    useEffect(() => {
        if (initialFilterList.length === 0) {
            let f = null
            for (f in initialFilterList) {
                filterStore.saveFilter(f)
            }
        }
        if (initialNameFilter) {
            filterStore.setNameFilter(initialNameFilter)
        }

    }, [])


    const onlyWidth = useWindowWidth();
    const [nameFilterInput, setNameFilterInput] = React.useState("");
    const [searchActivated, setSearchActivated] = React.useState(false);

    const [showFilterSummary, setShowFilterSummary] = React.useState(false);
    const [showFilterOverlay, setShowFilterOverlay] = React.useState(false);
    const [openLoadOverlay, setOpenLoadOverlay] = React.useState(false);
    const [openSaveOverlay, setOpenSaveOverlay] = React.useState(false);
    const [openDeleteOverlay, setOpenDeleteOverlay] = React.useState(false);
    const [selectedFilterID, setSelectedFilterID] = React.useState(null);
    const [updateNameFilterItem, setUpdateNameFilterItem] = React.useState(null);
    const [deleteFilterItem, setDeleteFilterItem] = React.useState(null);
    const [showClearIcon, setShowClearIcon] = React.useState(false);
    const [showSaveIcon, setShowSaveIcon] = React.useState(false);
    const [colorSaveIcon, setColorSaveIcon] = React.useState("primary");

    const filterList = useFilterStore(
        (state) => state.filterList
    );

    const includeLinked = useFilterStore(
        (state) => state.includeLinked
    );

    const displayedCategories = useFilterStore(
        (state) => state.displayedCategories
    );

    const setDisplayedCategories = useFilterStore(
        (state) => state.setDisplayedCategories
    );

    const nameFilter = useFilterStore(
        (state) => state.nameFilter
    );

    const setNameFilter = useFilterStore(
        (state) => state.setNameFilter
    );

    const setPage = useFilterStore(
        (state) => state.setPage
    );

    const setIncludeLinked = useFilterStore((state) => state.setIncludeLinked);
    const groupMappingUpToDate = useFilterStore((state) => state.groupMappingUpToDate);

    useEffect(() => {
        setNameFilterInput(nameFilter);
    }, [nameFilter]);

    useEffect(() => {
        if (filterList.length > 0 || hash(displayedCategories) !== hash(["all"]) || selectedFilterID || nameFilter !== "") {
            setShowClearIcon(true)
        } else {
            setShowClearIcon(false)
        }
    }, [filterList, displayedCategories, nameFilter]);

    useEffect(() => {
        if (dataView) {
            setShowSaveIcon(false)
            return;
        }
        setShowSaveIcon(false)

        if (selectedFilterID === null) {
            if (filterList.length > 0 || hash(displayedCategories) !== hash(["all"]) ||
                hash(displayedColumns) !== hash(["Name", "Type"]) || nameFilter !== "") {
                setShowSaveIcon(true)
                setColorSaveIcon("primary")
                return
            }


        } else {
            let selectedFilter = {
                filter_list: [],
                include_linked: false,
                displayed_columns: [],
                displayed_categories: [],
                name_filter: ""
            };
            if (savedFilter) {
                savedFilter.map((sf) => {
                    if (selectedFilterID === sf.id) {
                        selectedFilter = sf
                    }
                })
                if (hash(filterList) !== hash(selectedFilter.filter_list) || includeLinked !== selectedFilter.include_linked ||
                    hash(displayedColumns) !== hash(selectedFilter.displayed_columns) ||
                    hash(displayedCategories) !== hash(selectedFilter.displayed_categories) ||
                    nameFilter !== selectedFilter.name_filter) {

                    setShowSaveIcon(true)
                    setColorSaveIcon("error")
                    return;
                }
            }

            setShowSaveIcon(false)
        }


    }, [filterList, includeLinked, displayedColumns, displayedCategories, nameFilter]);

    const handleBlur = () => {
        setSearchActivated(false);
        setNameFilter(nameFilterInput)
        setPage(1)
    };


    function loadFilter() {
        setOpenLoadOverlay(false)
        savedFilter.map((sf) => {
            if (sf.id === selectedFilterID) {
                filterStore.resetFilter()
                if (sf.filter_list.length > 0) {
                    sf.filter_list.map((f) => {
                        filterStore.saveFilter(f)
                    })

                }

                setIncludeLinked(sf.include_linked)
                setDisplayedColumns(sf.displayed_columns)
                setDisplayedCategories(sf.displayed_categories)
                setNameFilter(sf.name_filter)
                setPage(1)

                setShowFilterOverlay(false)

                return
            }
        })
    }

    function resetFilter() {
        filterStore.resetFilter();
        setSelectedFilterID(null)
        setDisplayedColumns(["Name", "Type"])
        setDisplayedCategories(["all"])
        setUpdateNameFilterItem(null)

    }

    function editFilterNameClicked(filterItem) {
        setUpdateNameFilterItem(filterItem)
        setOpenSaveOverlay(true)
    }

    function deleteFilterClicked(filterItem) {
        setDeleteFilterItem(filterItem)
        setOpenDeleteOverlay(true)
    }


    function saveFilter(name = "") {
        if (updateNameFilterItem) {
            const data = {
                name: name
            }
            axios.post(`/web/filter/${updateNameFilterItem.id}`, data).then((res) => {
                const savedFilterCopy = []
                savedFilter.map((sf) => {
                    if (sf.id === updateNameFilterItem.id) {
                        sf.name = name
                    }
                    savedFilterCopy.push(sf)
                })
                mutateSavedFilter(savedFilterCopy)
            })
            setOpenSaveOverlay(false)
            setUpdateNameFilterItem(null)
            return

        }
        if (selectedFilterID) {
            const data = {
                displayed_columns: displayedColumns,
                filter_list: filterList,
                include_linked: includeLinked,
                displayed_categories: displayedCategories,
                name_filter: nameFilter
            }
            axios.post(`/web/filter/${selectedFilterID}`, data).then((res) => {
                const savedFilterCopy = []
                savedFilter.map((sf) => {
                    if (sf.id === selectedFilterID) {
                        sf.displayed_columns = displayedColumns
                        sf.filter_list = filterList
                        sf.include_linked = includeLinked
                        sf.displayed_categories = displayedCategories
                        sf.name_filter = nameFilter
                    }
                    savedFilterCopy.push(sf)
                })
                mutateSavedFilter(savedFilterCopy)
            })

        } else {
            const data = {
                name: name,
                displayed_columns: displayedColumns,
                filter_list: filterList,
                name_filter: nameFilter,
                include_linked: includeLinked,
                displayed_categories: displayedCategories,
            }

            axios.post(`/web/project/${params.project}/filter`, data).then((res) => {
                mutateSavedFilter([...savedFilter, res.data])
            })
            setOpenSaveOverlay(false)
        }
        setShowSaveIcon(false)

    }

    function saveIconClicked() {
        if (selectedFilterID === null) {
            setOpenSaveOverlay(true)
        } else {
            saveFilter()
        }
    }


    return (
        <>
            <div className={classes.searchBarWrapper}>
                <div
                    className={classes.searchBarInputWrapper}
                    style={{width: searchActivated ? "100%" : null}}
                >
                    <input
                        type="text"
                        onFocus={() => setSearchActivated(true)}
                        onBlur={handleBlur}
                        onChange={(e) => setNameFilterInput(e.target.value)}
                        className={[classes.searchInput].join("")}
                        value={nameFilterInput}
                        placeholder={onlyWidth < 576 ? "" : "Search"}
                        onKeyDown={(e) =>
                            e.key === "Enter" ? filterStore.setNameFilter(nameFilterInput) : null
                        }
                    />
                    <SearchIcon
                        className={classes.searchIcon}
                        sx={{color: "#737373"}}
                        onClick={() => setSearchActivated(true)}
                    />
                    {nameFilterInput.length > 0 && !searchActivated && (
                        <ClearIcon
                            className={classes.clearIcon}
                            onClick={() => {
                                filterStore.setNameFilter("");
                            }}
                        />
                    )}
                </div>
                {!searchActivated && (
                    <>
                        <div
                            className={classes.filterListCss}
                            style={{padding: filterList.length > 2 ? "10px 20px" : "0px"}}
                        >
                            {filterList.slice(0, 2).map((opt) => {
                                if (opt) {
                                    return (
                                        <FilterCard
                                            key={opt.id}
                                            keyName={opt.field}
                                            value={opt["values"]}
                                            id={opt.id}
                                            setOpenLoadOverlay={setOpenLoadOverlay}
                                            dataView={dataView}
                                        />
                                    );
                                }
                            })}
                            {filterList.length > 2 && (
                                <Button
                                    style={{
                                        padding: "12px 15px"
                                    }}
                                    onClick={() => setShowFilterSummary(true)}
                                    variant="outlined"
                                >
                                    +{filterList.length - 2} more filter
                                </Button>
                            )}
                            {(filterList.length > 0 || nameFilter !== "") && <IncludeLinked/>
                                // <FormControlLabel control={<Switch/>} label="Include linked items"
                                //                   checked={includeLinked !== undefined ? includeLinked : false}
                                //                   onChange={includeLinkedChanged}
                                //                   style={{marginLeft: "20px"}}
                                // />

                            }
                        </div>

                        <div>
                            <DisplayedCategories/>
                            <LoadingButton
                                disableElevation
                                sx={{
                                    fontWeight: 600,
                                    fontFamily: "Roboto",
                                    padding: "6px 10px",
                                    marginRight: "20px"
                                }}
                                variant="contained"
                                onClick={() => setShowFilterOverlay(true)}
                                startIcon={<AddIcon/>}
                                loading={!groupMappingUpToDate}
                            >
                                Add filter
                            </LoadingButton>
                            {showClearIcon && <IconButton onClick={resetFilter}>
                                <ClearIcon/>
                            </IconButton>}
                            {showSaveIcon && <IconButton onClick={() => {
                                saveIconClicked()
                            }}>
                                <SaveIcon color={colorSaveIcon}/>
                            </IconButton>}
                        </div>

                    </>
                )}
            </div>
            <FilterEditor
                onClose={() => setShowFilterOverlay(false)}
                open={showFilterOverlay}
                setOpenLoadOverlay={setOpenLoadOverlay}
                dataView={dataView}
            />
            <FilterSummary open={showFilterSummary} onClose={() => setShowFilterSummary(false)}
                           setOpenLoadOverlay={setOpenLoadOverlay} dataView={dataView}/>
            <LoadFilterOverlay
                savedFilter={savedFilter}
                openLoadOverlay={openLoadOverlay}
                setOpenLoadOverlay={setOpenLoadOverlay}
                loadFilterFunction={loadFilter}
                setSelectedFilterID={setSelectedFilterID}
                editFilterNameClicked={editFilterNameClicked}
                deleteFilterClicked={deleteFilterClicked}

            />
            <SaveFilterOverlay open={openSaveOverlay} saveFilterMethod={saveFilter}
                               handleClose={() => setOpenSaveOverlay(false)} updateFilterItem={updateNameFilterItem}/>
            <DeleteFilterDialog open={openDeleteOverlay} handleClose={() => setOpenDeleteOverlay(false)}
                                setDeleteFilterItem={setDeleteFilterItem} savedFilter={savedFilter}
                                deleteFilterItem={deleteFilterItem} mutateSavedFilter={mutateSavedFilter}/>
        </>
    );
};

function LoadFilterOverlay({
                               savedFilter,
                               openLoadOverlay,
                               setOpenLoadOverlay,
                               loadFilterFunction,
                               setSelectedFilterID,
                               editFilterNameClicked,
                               deleteFilterClicked
                           }) {
    useEffect(() => {
        setSelectedFilterID(null)
    }, []);

    const handleClose = () => {
        setOpenLoadOverlay(false)
        setSelectedFilterID(null)
        setItemSelected(false)
    }

    const [itemSelected, setItemSelected] = React.useState(false)

    const handleRadioChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        setSelectedFilterID((event.target as HTMLInputElement).value)
        setItemSelected(true)
    }

    return (
        <GenericDialog
            title='Select your filter template'
            handleClose={handleClose}
            open={openLoadOverlay}
            subInfo="Choose the filter you would like to apply"
            handleSubmit={loadFilterFunction}
            primaryActionText="Open"
            itemSelected={itemSelected}

        >
            <FormControl style={{width: "100%"}}>

                <RadioGroup
                    aria-labelledby="demo-radio-buttons-group-label"
                    defaultValue="None"
                    name="radio-buttons-group"
                    onChange={handleRadioChange}
                >
                    <hr/>

                    {(savedFilter !== undefined) && savedFilter.map(data => {
                        return (
                            <div>
                                <div style={{display: "flex"}}>

                                    <FormControlLabel value={data.id} control={<Radio/>} label={data.name}/>
                                    <div style={{marginLeft: "auto"}}>
                                        <IconButton onClick={() => editFilterNameClicked(data)}>
                                            <EditIcon/>
                                        </IconButton>
                                        <IconButton onClick={() => deleteFilterClicked(data)}>
                                            <DeleteIcon/>
                                        </IconButton>

                                    </div>
                                </div>
                                <hr/>
                            </div>
                        )
                    })}
                </RadioGroup>

            </FormControl>
        </GenericDialog>
    )
}

const GenericDialog = (props) => {
    const {title, subInfo, open, handleClose, handleSubmit, primaryActionText, itemSelected} = props;
    return (
        <Dialog open={open} onClose={handleClose}>
            <DialogTitle>{title}</DialogTitle>
            <DialogContent style={{width: "100%"}}>

                {subInfo && <DialogContentText>
                    {subInfo}
                </DialogContentText>}
                {props.children}
            </DialogContent>
            <DialogActions>
                <Button onClick={handleClose}>Cancel</Button>
                <LoadingButton onClick={handleSubmit} color="warning"
                               disabled={!itemSelected}>{primaryActionText}</LoadingButton>
            </DialogActions>
        </Dialog>
    )
}


export default FilterBar;

const SaveFilterOverlay = ({open, handleClose, saveFilterMethod, updateFilterItem}) => {
    const [name, setName] = React.useState('');
    const [check, setCheck] = React.useState(false)
    const [saving, setSaving] = React.useState(false)
    const [loading, setLoading] = React.useState(false)
    const [subtitle, setSubtitle] = React.useState("This will create a new filter")
    const [createWord, setCreateWord] = React.useState("Create")
    const debouncedCheck = useCallback(debounce(checkName, 200), []);
    const params = useParams();

    function checkName(nameToBeChecked) {
        let data = {
            name: nameToBeChecked
        }
        let url = ""
        if (updateFilterItem) {
            url = `/web/filter/${updateFilterItem.id}/check`

        } else {
            url = `/web/project/${params.project}/filter/check`

        }
        axios.post(url, data).then((r) => {
            if (r.data == "True") {
                setCheck(true)
            } else {
                setCheck(false)
            }
            setLoading(false)

        })
    }

    useEffect(() => {
        if (!name) {
            setCheck(false)
            return;
        } else {
            setLoading(true)
            debouncedCheck(name)
        }

    }, [name]);

    useEffect(() => {
        if (updateFilterItem) {
            setSubtitle("Update the filter name")
            setName(updateFilterItem.name)
            setCreateWord("Update")
        } else {
            setSubtitle("This will create a new filter")
            setCreateWord("Create")
            setName("")
        }

    }, [updateFilterItem]);

    function saveFilter() {
        saveFilterMethod(name)
    }

    return (
        <Dialog open={open} onClose={close} fullWidth>
            <DialogTitle>Save filter</DialogTitle>
            <DialogContent>


                <DialogContentText>{subtitle}</DialogContentText>

                <TextField
                    autoFocus
                    margin="dense"
                    label="Name"
                    fullWidth
                    variant="standard"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    onKeyDown={(e) => (e.key === 'Enter') ? saveFilter() : null}
                />
                {!check && name && !loading && < Typography style={{
                    color: 'red',
                    fontSize: '14px'
                }}>Name already in use. Please choose another one.</Typography>}

            </DialogContent>
            <DialogActions>
                <Button onClick={handleClose}>Cancel</Button>
                <LoadingButton loading={saving} onClick={saveFilter} disabled={!check}>{createWord}</LoadingButton>
            </DialogActions>
        </Dialog>
    )

}

const DeleteFilterDialog = ({
                                open,
                                handleClose,
                                deleteFilterItem,
                                setDeleteFilterItem,
                                mutateSavedFilter,
                                savedFilter
                            }) => {
    const [loading, setLoading] = React.useState(false);

    const deleteItem = () => {
        setLoading(true);
        let savedFilterCopy = []
        savedFilter.map((filter) => {
            if (filter.id !== deleteFilterItem.id) {
                savedFilterCopy.push(filter)
            }
        })

        axios.delete(`/web/filter/${deleteFilterItem.id}`).then(() => {
            handleClose();
            mutateSavedFilter(savedFilterCopy)
            setDeleteFilterItem(null)
            setLoading(false)

        });
    }
    return (
        <>
            {(deleteFilterItem) && <Dialog open={open} onClose={handleClose}>
                <DialogTitle>Delete: {deleteFilterItem.name}?</DialogTitle>
                <DialogContent>

                    <DialogContentText></DialogContentText>

                </DialogContent>
                <DialogActions>
                    <Button onClick={handleClose} disabled={loading}>Cancel</Button>
                    <LoadingButton loading={loading} onClick={deleteItem} color="warning">Delete</LoadingButton>
                </DialogActions>
            </Dialog>}
        </>
    )
}
