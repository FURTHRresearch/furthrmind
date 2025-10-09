import React, {useCallback, useEffect} from 'react';
import AddIcon from '@mui/icons-material/Add';
import ArticleIcon from '@mui/icons-material/Article';
import BiotechIcon from '@mui/icons-material/Biotech';
import CategoryIcon from '@mui/icons-material/Category';
import FolderIcon from '@mui/icons-material/Folder';
import ScienceIcon from '@mui/icons-material/Science';
import LoadingButton from '@mui/lab/LoadingButton';
import Button from '@mui/material/Button';
import Dialog from '@mui/material/Dialog';
import DialogActions from '@mui/material/DialogActions';
import DialogContent from '@mui/material/DialogContent';
import DialogContentText from '@mui/material/DialogContentText';
import DialogTitle from '@mui/material/DialogTitle';
import Divider from '@mui/material/Divider';
import Menu from '@mui/material/Menu';
import MenuItem from '@mui/material/MenuItem';
import TextField from '@mui/material/TextField';
import axios from 'axios';
import CreateFromTemplate from './Overlays/CreateFromTemplate/CreateFromTemplate';

import {useParams} from 'react-router-dom';

import Grid from "@mui/material/Grid";
import {FormControl, InputLabel, Select, Typography} from "@mui/material";
import ResearchManagementCreateOverlay from "./Overlays/ResearchManagementCreateOverlay";
import useSWR from "swr";
import Stack from '@mui/material/Stack'
import debounce from "lodash/debounce";
import useGroupIndexStore from "../zustand/groupIndexStore";
import { add } from 'lodash';
import { log } from 'console';

const CreateButton = ({currentGroup, writable, admin, groups, mutateGroups}) => {

    const [menuAnchor, setMenuAnchor] = React.useState(null);
    const [createType, setCreateType] = React.useState(null);
    const [groupId, setGroupId] = React.useState("");
    const params = useParams();


    useEffect(() => {
        setGroupId("")
        if (currentGroup !== undefined && currentGroup !== null) {
            setGroupId(currentGroup.id)
        }
    }, [currentGroup]);

    return (
        <>
            <Button
                onClick={(e) => setMenuAnchor(e.currentTarget)}
                startIcon={<AddIcon/>}
                variant="outlined"
                disabled={!writable}
            >
                Create
            </Button>
            <Menu
                anchorEl={menuAnchor}
                open={Boolean(menuAnchor)}
                onClose={() => setMenuAnchor(null)}
                onClick={(e: any) => setMenuAnchor(null)}
                anchorOrigin={{
                    vertical: 'top',
                    horizontal: 'left',
                }}
                transformOrigin={{
                    vertical: 'top',
                    horizontal: 'left',
                }}
            >
                <MenuItem onClick={() => {
                    setCreateType('Groups')
                }}><span style={{color: "#1a73e8"}}><FolderIcon/> Group</span></MenuItem>
                <Divider/>
                <MenuItem disabled={!Boolean(groupId)} onClick={() => {
                    setCreateType('Subgroups')
                }}><span style={{color: "#1a73e8"}}><FolderIcon/> Subgroup</span></MenuItem>
                <MenuItem disabled={!Boolean(groupId)} onClick={() => {
                    setCreateType('Experiments')
                }}><span style={{color: "#3c8039"}}><BiotechIcon/> Experiment</span></MenuItem>
                <MenuItem disabled={!Boolean(groupId)} onClick={() => {
                    setCreateType('Samples')
                }}><span style={{color: "#e3742f"}}><ScienceIcon/> Sample</span></MenuItem>
                <MenuItem disabled={!Boolean(groupId)} onClick={() => {
                    setCreateType('Researchitems')
                }}><span style={{color: "grey"}}><CategoryIcon/> Research item</span></MenuItem>
                <Divider/>
                <MenuItem disabled={!Boolean(groupId)} onClick={() => {
                    setCreateType('fromTemplate')
                }}><span style={{color: "#1876D1"}}><ArticleIcon/> Duplicate</span></MenuItem>
            </Menu>
            {createType === "fromTemplate" && <CreateFromTemplate
                show={true}
                groupSelectedForTemplate={groupId}
                onClose={() => setCreateType(null)}
                mutateGroups={mutateGroups}
                admin={admin}
                groups={groups}
            />}
            {(createType === "Experiments" || createType === "Samples" ||
                    createType === "Groups" || createType === "Subgroups") &&
                <CreateDialog currentGroup={groupId}
                              type={createType}
                              open={Boolean(createType)}
                              groups={groups}
                              mutateGroups={mutateGroups}
                              handleClose={() => setCreateType(null)}/>}

            {createType === "Researchitems" && <NewResearchItem
                show={true}
                groupId={groupId}
                groups={groups}
                mutateGroups={mutateGroups}
                onClose={() => setCreateType(null)}
                admin={admin}
            />
            }


        </>

    );
}

export default CreateButton;

const CreateDialog = ({open, handleClose, type, currentGroup, groups, mutateGroups}) => {
    const [name, setName] = React.useState('');
    const [creating, setCreating] = React.useState(false);
    const [check, setCheck] = React.useState(false)
    const [loading, setLoading] = React.useState(false)
    const typeName = type.slice(0, -1)
    const addRecentlyCreated = useGroupIndexStore((state) => state.addRecentlyCreated);
    const addRecentlyCreatedGroups = useGroupIndexStore((state) => state.addRecentlyCreatedGroups);


    React.useEffect(() => {
        setName('');
        setCreating(false);
    }, [open]);

    const params = useParams();

    function checkName(nameToBeChecked) {
        let data = {
            name: nameToBeChecked,
            group_id: null
        }
        if (type !== "Groups") {
            data["group_id"] = currentGroup
        }

        axios.post(`/web/project/${params.project}/item/${type}/check`, data).then((r) => {
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
        if (!name) {
            setCheck(false)
            return;
        } else {
            setLoading(true)
            debouncedCheck(name)
        }

    }, [name]);

    const createItem = () => {
        setCreating(true);
        if (type === 'Groups') {
            const url = `/web/projects/${params.project}/groups`;
            axios.post(url, {name: name}).then(r => {
                const newItem = r.data;
                const groupsCopy = [newItem];
                addRecentlyCreated(newItem.id);
                addRecentlyCreatedGroups(newItem.id);
                groupsCopy.push(...groups);
                mutateGroups(groupsCopy, {revalidate: false});
                setCreating(false);

                handleClose();
            })
            // .catch(err => {
            //     alert('Group name already exists.');
            //     handleClose();
            // })

        } else if (type === 'Subgroups') {
            const url = `/web/projects/${params.project}/groups`;
            axios.post(url, {name: name, groupid: currentGroup}).then(r => {
                const newItem = r.data;
                const groupsCopy = [newItem];
                groupsCopy.push(...groups);
                mutateGroups(groupsCopy, {revalidate: false});
                addRecentlyCreated(newItem.id);
                setCreating(false);
                handleClose();
            }).catch(err => {
                alert('Group name already exists.');
                handleClose();
            });
        } else {
            axios.post('/web/groups/' + currentGroup + '/' + type.toLowerCase(), {name: name}).then(r => {
                const groupsCopy = [...groups];
                let found = false
                groupsCopy.map(item => {
                    if (item.id.toLowerCase() === `${currentGroup}/sep/${type}`.toLowerCase()) {
                        item.visible = true;
                        found = true;
                    }

                })
                if (!found) {
                    const cat_node = r.data.cat_node
                    groupsCopy.push(cat_node)
                    addRecentlyCreated(cat_node.id);
                }
                const newItem = r.data.node;
           
                const groupsNew = [newItem];
                groupsNew.push(...groupsCopy);
                mutateGroups(groupsNew, {revalidate: false});
                addRecentlyCreated(newItem.id);
                setCreating(false);
                handleClose();
            }).catch(err => {
                alert('Name already exists.');
                handleClose();
            });
        }
    }

    return (
        <Dialog open={open} onClose={handleClose}>
            <DialogTitle>New {type}</DialogTitle>
            <DialogContent>


                <DialogContentText>This will create a new {typeName.toLowerCase()} in the current selected
                    group.</DialogContentText>

                <TextField
                    autoFocus
                    margin="dense"
                    label="Name"
                    fullWidth
                    variant="standard"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    onKeyDown={(e) => (e.key === 'Enter') ? createItem() : null}
                />
                {!check && name && !loading && < Typography style={{
                    color: 'red',
                    fontSize: '14px'
                }}>Name already in use. Please choose another one.</Typography>}

            </DialogContent>
            <DialogActions>
                <Button onClick={handleClose}>Cancel</Button>
                <LoadingButton loading={creating} onClick={createItem} disabled={!check}>Create</LoadingButton>
            </DialogActions>
        </Dialog>
    )
}

let setRows = false
let catList = []

const NewResearchItem = ({show, onClose, groupId, groups, mutateGroups, admin}) => {
    const [name, setName] = React.useState("");
    const [type, setType] = React.useState('');
    const [categoryName, setCategoryName] = React.useState('');
    const [categoryFound, setCategoryFound] = React.useState(false);
    const [creating, setCreating] = React.useState(false);
    const [openCreateOverlay, setOpenCreateOverlay] = React.useState(false)
    const [creatingData, setCreatingData] = React.useState({
        categoryName: '',
        categoryDesc: ''
    })
    const [check, setCheck] = React.useState(false)
    const [loading, setLoading] = React.useState(false)
    const params = useParams();
    const addRecentlyCreated = useGroupIndexStore((state) => state.addRecentlyCreated);

    const fetcher = url => fetch(url).then(res => res.json());
    const {
        data: categories,
        mutate: mutateResearchCategory
    } = useSWR('/web/projects/' + params.project + '/categories', fetcher);


    useEffect(() => {
        setName("");
    }, [""]);

    useEffect(() => {
        setCreating(false);
    }, [show]);

    // if (setRows==false) {
    //     getResearchCategorys()
    // }

    function checkName(nameToBeChecked, categroy_id) {
        const data = {
            name: nameToBeChecked,
            group_id: groupId,
            category_id: categroy_id
        }
        if (!categroy_id) {
            return
        }
        axios.post(`/web/project/${params.project}/item/${categroy_id}/check`, data).then((r) => {
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
        if (name === "") {
            setCheck(false)
            return;
        } else if (!type) {
            setCheck(false)
            return;
        } else {
            setLoading(true)
            debouncedCheck(name, type)
        }

    }, [name, type]);

    const createResearchItem = () => {
        setCreating(true);
        axios.post(`/web/groups/${groupId}/researchitems`, {
            name: name,
            research_category_id: type,
        }).then(r => {
            const groupsCopy = [...groups];
            let found = false
            groupsCopy.map(item => {
                if (item.id.toLowerCase() === `${groupId}/sep/${categoryName}`.toLowerCase()) {
                    item.visible = true;
                    found = true;
                }
            })
            if (!found) {
                const cat_node = r.data.cat_node
                groupsCopy.push(cat_node)
                addRecentlyCreated(cat_node.id);
            }
            console.log(r.data)
            const newItem = r.data.node;
            const groupsNew = [newItem];
            groupsNew.push(...groupsCopy);
            mutateGroups(groupsNew, {revalidate: false});
            addRecentlyCreated(newItem.id);

            setCreating(false);
            onClose();

        }).catch(err => {
            alert('Name already exists.');
            onClose();
        });
        ;
    }

    function onNameChange(event) {
        setName(event.target.value)
    }

    function onCategoryChange(event) {
        setType(event.target.value)
        setCategoryFound(false)
        categories.map(category => {
            if (category.id === event.target.value) {
                setCategoryName(category.name)
                setCategoryFound(true)
            }
        })
    }

    const closeCreateOverlayHandler = () => {
        setOpenCreateOverlay(false);
        setCreatingData({
            categoryDesc: '',
            categoryName: ''
        })
    }

    return (
        <Dialog open={show} onClose={onClose}>
            <DialogTitle>Create a new research item</DialogTitle>
            <DialogContent>
                <DialogContentText>
                    Type a research item name and select the research category.
                </DialogContentText>
                <div style={{marginTop: '1em'}}></div>
                <Grid item xs={12}>
                    <TextField
                        label="Name"
                        fullWidth
                        variant="standard"
                        onChange={(e) => onNameChange(e)}

                    />
                </Grid>
                {!check && name && type && !loading && < Typography variant="subtitle1" style={{
                    color: 'red',
                    fontSize: '14px'
                }}>Name already in use. Please choose another one.</Typography>}
                {(categories) && <Stack direction={"row"} marginTop={"20px"}>
                    <FormControl style={{width: "100%"}}>
                        <InputLabel variant="standard">Research category</InputLabel>
                        <Select
                            value={type ?? ""}
                            variant="standard"
                            onChange={(e: any) => onCategoryChange(e)}
                        >

                            {categories.map((category) => (
                                <MenuItem value={category.id}>{category.name}</MenuItem>

                            ))}

                        </Select>
                    </FormControl>
                    <div style={{marginTop: "10px", marginLeft: "20px"}}>
                        <Button variant="text" startIcon={<AddIcon/>}
                                onClick={() => setOpenCreateOverlay(true)} disabled={!admin}
                        >Category</Button>

                    </div>

                </Stack>
                }

            </DialogContent>
            <DialogActions>
                <Button onClick={onClose} disabled={creating}>Cancel</Button>
                <LoadingButton loading={creating} onClick={createResearchItem}
                               disabled={!check && !loading}>Create</LoadingButton>
            </DialogActions>
            {openCreateOverlay && <ResearchManagementCreateOverlay
                open={openCreateOverlay}
                onClose={closeCreateOverlayHandler}
                categoryName={creatingData.categoryName}
                categoryDesc={creatingData.categoryDesc}
                mutateResearchCategory={mutateResearchCategory}
                rows={categories}
            />}
        </Dialog>
    );
}
