import BiotechIcon from '@mui/icons-material/Biotech';
import ScienceIcon from '@mui/icons-material/Science';
import CategoryIcon from '@mui/icons-material/Category';

import { LoadingButton } from '@mui/lab';
import { Button, Checkbox, FormControl, Grid, MenuItem, Modal, Pagination, Stack } from '@mui/material';
import axios from 'axios';
import * as React from 'react';
import { useCallback, useEffect, useMemo, useState } from 'react';
import { useParams } from 'react-router-dom';
import classes from './CreateTemplateStyle.module.css';
import GroupListForTemplate from './GroupListForTemplate';
import FormControlLabel from "@mui/material/FormControlLabel";
import DialogTitle from "@mui/material/DialogTitle";
import DialogContent from "@mui/material/DialogContent";
import DialogActions from "@mui/material/DialogActions";
import Dialog from "@mui/material/Dialog";
import Typography from "@mui/material/Typography";
import InputLabel from "@mui/material/InputLabel";
import Select from "@mui/material/Select";
import useSWR from "swr";
import useGroupIndexStore from "../../../zustand/groupIndexStore";
import debounce from "lodash/debounce";
import SearchIcon from "@mui/icons-material/Search";

const fetcher = (url) => fetch(url).then((res) => res.json());
const validShortIdLength = 10;
const invalidShortIdMessage = 'Short ID not found.';


const CreateFromTemplate = ({ show, onClose, groupSelectedForTemplate, mutateGroups, admin, groups }) => {
    const [searchActivated, setSearchActivated] = useState(false);
    const [searchInput, setSearchInput] = useState("");
    const [items, setItems] = useState([]);
    const [typedShortID, setTypedShortID] = useState('');
    const [invalidShortID, setInvalidShortID] = useState(false);
    const params = useParams();
    const [project, setProject] = useState(params.project);
    const [openCreateOverlay, setOpenCreateOverlay] = useState(false);
    const [id, setId] = useState("");
    const [type, setType] = useState("");
    const [parent, setParent] = useState("");
    const [name, setName] = useState("");
    const [currentGroup, setCurrentGroup] = useState({
        id: "", name: "", parent: ""
    })
    const [allGroups, setAllGroups] = useState([]);

    const [page, setPage] = useState(1)
    const [siblingCount, setSiblingCount] = useState(0);
    const [boundaryCount, setBoundaryCount] = useState(1);

    const [maxIndex, setMaxIndex] = useState(1)
    const [nameSearch, setNameSearch] = useState("")
    const [input, setInput] = useState("")

    const queryString = useMemo(() => {
        return new URLSearchParams({
            comboFieldValues: '[]',
            groupFilter: '[]',
            sampleFilter: '[]',
            researchItemFilter: '[]',
            experimentFilter: '[]',
            numericFilter: '[]',
            dateFilter: '[]',
            textFilter: '[]',
            nameFilter: nameSearch,
            displayedCategories: JSON.stringify(["all"]),
            recent: "all",
            index: String(page),
        }).toString()
    }, [page, nameSearch]);

    const { data: pageMapping } = useSWR(`/web/projects/${project}/page-group-mapping?${queryString}`,
        (url) => fetch(url).then((res) => res.json()));



    useEffect(() => {
        if (!pageMapping) {
            setMaxIndex(1)
            return
        }
        setMaxIndex(pageMapping.maxPage)
        setPage(1)      

    }, [pageMapping]);
    
    const handleChange = (val: string) => {
        setSearchInput(val);
    };


    useEffect(() => {
        if (!pageMapping) {
            return
        }
        let groupIDs = pageMapping.pageGroupMapping[page]
        const groupIdQuery = new URLSearchParams({
            groupIDs: JSON.stringify(groupIDs),

        }).toString()
        

        axios.get(`/web/projects/${project}/groupindex?${queryString}&${groupIdQuery}`).then((res) => {
            const data = res.data;
            setAllGroups(data);
        })


    }, [pageMapping, page]);

    const handleShortIdTyped = (e) => {
        setTypedShortID(e.target.value);
    }

    useEffect(() => {
        if (typedShortID.length > 0 && typedShortID.length < validShortIdLength) {
            setInvalidShortID(true);
        } else {
            setInvalidShortID(false);
        }

    }, [typedShortID])


    function duplicateGroupClicked(event) {
        setId(currentGroup.id)
        setName(currentGroup.name)
        setParent(currentGroup.parent)
        setType("groups")
        setOpenCreateOverlay(true)

    }

    function handlePageChange(e, newValue) {
        setPage(newValue)
        if (newValue === 1) {
            setSiblingCount(0)
            setBoundaryCount(1)
        } else if (newValue === maxIndex) {
            setSiblingCount(0)
            setBoundaryCount(1)
        } else {
            setSiblingCount(1)
            setBoundaryCount(1)
        }
    }

    function inputChanged(value) {
        setInput(value)
        debouncedNameSearch(value)
    }

    function nameSearchChanged(value) {
        setNameSearch(value)
    }

    const debouncedNameSearch = useCallback(debounce(nameSearchChanged, 300), []);

    return (
        <Modal open={show} onClose={onClose} disableAutoFocus={true} style={{ overflow: "auto" }}>
            <div className={classes.modalWrapper}>
                <div className={classes.mainHeader}>
                    <Grid container spacing={2}>
                        {(admin) && <Grid item xs={3}>
                            <ProjectSelector project={project} onChange={(v) => setProject(v)} />
                        </Grid>
                        }

                        {/*<Grid item xs={2}>*/}
                        {/*    <Stack direction="column">*/}
                        {/*        <TextField id="outlined-basic"*/}
                        {/*                   label="Short ID"*/}
                        {/*                   variant="outlined"*/}
                        {/*                   fullWidth*/}
                        {/*                   sx={{*/}
                        {/*                       background: "white"*/}
                        {/*                   }}*/}
                        {/*                   placeholder="Short ID"*/}
                        {/*                   onChange={handleShortIdTyped}*/}
                        {/*                   value={typedShortID}*/}
                        {/*                   error={invalidShortID}*/}


                        {/*        />*/}
                        {/*        {invalidShortID && <Typography sx={{color: 'red'}}*/}
                        {/*                                       className="mt-2">{invalidShortIdMessage}</Typography>}*/}
                        {/*    </Stack>*/}

                        {/*</Grid>*/}
                    </Grid>
                </div>
                {(admin) && <hr />}
                {project ? <>
                    {/*<SearchBar*/}
                    {/*    searchActivated={searchActivated}*/}
                    {/*    setSearchActivated={setSearchActivated}*/}
                    {/*    handleChange={handleChange}*/}
                    {/*    searchInput={searchInput}*/}
                    {/*    isLoading={false}*/}
                    {/*    withButton={false}*/}
                    {/*/>*/}

                    <div className={classes.boxWrapper}>
                        <div style={{ display: "flex", flexDirection: "column", marginLeft: "-30px" }}>
                            <input
                                type="text"
                                onFocus={() => setSearchActivated(true)}
                                onChange={(e) => inputChanged(e.target.value)}
                                className={[classes.searchInput].join("")}
                                value={input}
                                placeholder={"Search"}
                                onKeyDown={(e) => (e.key === 'Enter') ? inputChanged(e.target.value) : null}


                            />
                            <SearchIcon className={classes.searchIcon} sx={{ color: "#737373" }}
                                onClick={() => setSearchActivated(true)} />


                            <div className={classes.child1}>
                                <GroupListForTemplate
                                    project={project}
                                    setItems={setItems}
                                    searchTerm={searchInput}
                                    typedShortID={typedShortID}
                                    invalidShortID={invalidShortID}
                                    setCurrentGroup={setCurrentGroup}
                                    groups={allGroups}
                                />

                            </div>
                            <div style={{ marginTop: "20px", flexShrink: 0 }}>
                                {(maxIndex > 1) &&
                                    <Pagination count={maxIndex} size={"small"} onChange={handlePageChange}
                                        siblingCount={siblingCount} boundaryCount={boundaryCount}
                                        showFirstButton={false}
                                        showLastButton={false}
                                        style={{
                                            marginRight: "auto",
                                            marginLeft: "auto",
                                            width: "100%"
                                        }}
                                    />
                                }

                            </div>
                        </div>


                        <div>
                            <Stack direction={"column"}>
                                {(currentGroup.id) && <div style={{ marginTop: "auto", marginBottom: "20px" }}>
                                    <LoadingButton
                                        variant="contained"
                                        loading={false}
                                        style={{
                                            background: "#1a73e8",
                                        }}
                                        className={classes.cardSelectButtonCss}
                                        onClick={duplicateGroupClicked}
                                    >
                                        Duplicate group
                                    </LoadingButton>
                                </div>
                                }

                                {items.length > 0 &&

                                    <div className={classes.child2}>

                                        <div className={classes.cardWrapper}>
                                            {items.length > 0 && items.map((item, key) => {
                                                return (
                                                    <CardView
                                                        type={item.type.toLowerCase()}
                                                        name={item.name}
                                                        id={item.id}
                                                        setOpenCreateOverlay={setOpenCreateOverlay}
                                                    />

                                                )
                                            })}
                                        </div>
                                    </div>
                                }
                            </Stack>

                        </div>


                    </div>
                </> : <div>
                    <p>Please select a project or enter a short id to copy from above.</p>
                </div>}
                <div>
                    {
                        openCreateOverlay &&
                        <CreateOverlay targetGroup={groupSelectedForTemplate}
                            onCreated={onClose}
                            open={openCreateOverlay} setOpen={setOpenCreateOverlay}
                        />
                    }
                </div>
            </div>
        </Modal>

    )

    function ProjectSelector({ project, onChange }) {
        const params = useParams();
        const { data: projects } = useSWR("/web/projects", fetcher);
        // const [value, setValue] = useState(params.project);
        return (<FormControl fullWidth>
            <InputLabel>Project</InputLabel>
            <Select
                labelId="demo-simple-select-label"
                id="demo-simple-select"
                value={project}
                label="Project"
                sx={{ backgroundColor: 'white' }}
                onChange={(e) => {
                    // setValue(e.target.value);
                    onChange(e.target.value)
                }}
            >
                {projects && projects.map((project) =>
                    <MenuItem value={project.id}>{project.Name}</MenuItem>
                )}
            </Select>
        </FormControl>)
    }

    function CardView({
        name, type, id, setOpenCreateOverlay
    }) {
        const isExperiment = type === "experiments";

        function selectClicked(e) {
            setId(id)
            setName(name)
            setType(type)
            setOpenCreateOverlay(true)
        }


        return (
            <div className={classes.cardViewWrapper}>
                <div className={classes.cardBody} style={{ background: isExperiment ? "#E6F4EA" : "#FCEEE2" }}>
                    <Stack direction={"row"} spacing={3}>
                        <div className={classes.cardIconCss}>
                            {type === "experiments" && <ScienceIcon />}
                            {type === "samples" && <BiotechIcon />}
                            {type === "researchitems" && <CategoryIcon />}

                        </div>
                        <div>

                            <div className={classes.cardDetailWrapper}>
                                <div className={classes.cardTypeCss}>{type}:</div>
                                {/* <div className={classes.cardDateCss}>09/2022</div> */}
                            </div>
                            <div className={classes.cardIdCss}>
                                {name}
                            </div>
                        </div>
                    </Stack>

                </div>
                <div className={classes.cardFooter}>
                    <Stack direction={"row"}>
                        <div className={classes.cardSelect}
                            style={{ marginTop: "auto", marginBottom: "auto", marginLeft: "20px" }}>
                            <LoadingButton
                                variant="contained"
                                style={{ background: isExperiment ? "#369383" : "#E3742E" }}
                                className={classes.cardSelectButtonCss}
                                onClick={selectClicked}
                            >
                                Select
                            </LoadingButton>
                        </div>
                    </Stack>


                </div>
            </div>
        )
    }

    function CreateOverlay({ targetGroup, onCreated, open, setOpen }) {

        const [creating, setCreating] = useState(false)
        const [includeExperiments, setIncludeExperiments] = useState(true);
        const [includeSamples, setIncludeSamples] = useState(true);
        const [includeResearchItems, setIncludeResearchItems] = useState(true);
        const [includeSubgroups, setIncludeSubgroups] = useState(true);
        const [copyFields, setCopyFields] = useState(true);
        const [copyDataTable, setCopyDataTable] = useState(false);
        const [copyFiles, setCopyFiles] = useState(false);

        const [showType, setShowType] = useState("")
        const addRecentlyCreated = useGroupIndexStore((state) => state.addRecentlyCreated);
        const addRecentlyCreatedGroups = useGroupIndexStore((state) => state.addRecentlyCreatedGroups);


        useEffect(() => {
            const list = ["samples", "experiments", "groups"]
            if (list.includes(type)) {
                setShowType(type.slice(0, -1))
            } else {
                setShowType(type)
            }
        }, [type]);

        function capitalizeFirstLetter(string) {
            return string.charAt(0).toUpperCase() + string.slice(1);
        }

        function createNodes(id, type, name, parentGroupID, parent) {

            const groupsCopy = []
            if (type === "groups") {
                const newItem = {
                    id: id,
                    name: name,
                    type: "Groups",
                    show_type: "Groups",
                    parent: parent,
                    group_id: id,
                    visible: true,
                    droppable: true,
                    expandable: true,
                    text: name
                }
                groupsCopy.push(newItem);
                groupsCopy.push(...groups)
                addRecentlyCreated(newItem.id);
                if (parent === 0) {
                    addRecentlyCreatedGroups(newItem.id);
                }
                mutateGroups(groupsCopy, { revalidate: true });

            } else {
                const typeCapitalized = capitalizeFirstLetter(type)
                let found = false
                const tempGroupCopy = [...groups]
                tempGroupCopy.map(item => {
                    if (item.id.toLowerCase() === `${parentGroupID}/sep/${type}`.toLowerCase()) {
                        item.visible = true;
                        found = true;
                    }
                })
                if (!found) {
                    let cat_node = {
                        id: `${parentGroupID}/sep/${typeCapitalized}`,
                        name: typeCapitalized,
                        type: typeCapitalized,
                        show_type: typeCapitalized,
                        short_id: "",
                        parent: parentGroupID,
                        droppable: false,
                        expandable: true,
                        group_id: parentGroupID,
                        visible: true,
                        text: typeCapitalized,
                    }
                    groupsCopy.push(cat_node)
                    addRecentlyCreated(cat_node.id);
                }
                const newItem = {
                    id: id,
                    name: name,
                    type: typeCapitalized,
                    show_type: typeCapitalized,
                    parent: `${parentGroupID}/sep/${typeCapitalized}`,
                    group_id: parentGroupID,
                    visible: true,
                    droppable: false,
                    expandable: false,
                    text: name
                }
                groupsCopy.push(newItem);
                groupsCopy.push(...groups)
                mutateGroups(groupsCopy, { revalidate: false });
                addRecentlyCreated(newItem.id);
                

            }

        }

        const params = useParams();
        const create = (e) => {
            setCreating(true);
            axios.post(`/web/copy-template`, {
                targetProject: params.project,
                targetGroup,
                sourceId: id,
                collection: type,
                includeExps: includeExperiments,
                includeSamples: includeSamples,
                includeResearchItems: includeResearchItems,
                includeSubgroups: includeSubgroups,
                includeFields: copyFields,
                includeRawData: copyDataTable,
                includeFiles: copyFiles

            }).then(res => {

                const data = res.data;
                createNodes(data.id, type, data.name, targetGroup, parent);
                setCreating(false);
                setOpenCreateOverlay(false)
                onCreated();

            });

        }

        return (
            <Dialog
                open={open}
                fullWidth
                style={{ marginLeft: "auto", marginRight: "auto", width: "500px" }}
            >
                <DialogTitle>
                    Duplicate {showType}: '{name}'
                </DialogTitle>
                <DialogContent>
                    <Typography>Include:</Typography>
                    <Stack direction={"column"} marginLeft={"40px"}>
                        {(type === "groups") &&
                            <FormControlLabel control={<Checkbox checked={includeSubgroups} />}
                                label={"subgroups"} onClick={() => {
                                    setIncludeSubgroups(!includeSubgroups)
                                }}
                            />
                        }
                        {(type === "groups") &&
                            <FormControlLabel control={<Checkbox checked={includeExperiments} />}
                                label={"experiments"} onClick={() => {
                                    setIncludeExperiments(!includeExperiments)
                                }}
                            />
                        }
                        {(type === "groups") &&
                            <FormControlLabel control={<Checkbox checked={includeSamples} />}
                                label={"samples"} onClick={() => {
                                    setIncludeSamples(!includeSamples)
                                }}
                            />
                        }
                        {(type === "groups") &&
                            <FormControlLabel control={<Checkbox checked={includeResearchItems} />}
                                label={"researchitems"} onClick={() => {
                                    setIncludeResearchItems(!includeResearchItems)
                                }}
                            />
                        }
                        <FormControlLabel control={<Checkbox checked={copyFields} />}
                            label={"fields"} onClick={() => {
                                setCopyFields(!copyFields)
                            }} />
                        <FormControlLabel control={<Checkbox checked={copyDataTable} />}
                            label={"data tables"} onClick={() => {
                                setCopyDataTable(!copyDataTable)
                            }} />
                        <FormControlLabel control={<Checkbox checked={copyFiles} />}
                            label={"files"} onClick={() => {
                                setCopyFiles(!copyFiles)
                            }} />


                    </Stack>
                    <Typography>Your data will be copied in background. It may take a while depending on the amount of data to be duplcated.</Typography>
                </DialogContent>
                <DialogActions>
                    <Button onClick={() => {
                        setOpen(false)
                    }}>Cancel</Button>
                    <LoadingButton color="success" loading={creating} onClick={create}>
                        Duplicate
                    </LoadingButton>
                </DialogActions>
            </Dialog>
        )

    }
}


export default CreateFromTemplate;

