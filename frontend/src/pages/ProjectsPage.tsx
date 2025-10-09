import AddIcon from "@mui/icons-material/Add";
import {FormControlLabel, Menu, Skeleton, Switch, Typography} from "@mui/material";
import React, {useCallback, useEffect, useState} from "react";
import useSWR, {mutate, useSWRConfig} from "swr";
//seperation between external files and local files
import ProjectCard from "../components/Cards/ProjectCard";
import Header from "../components/Header/Header";
import SearchBar from "../components/SearchBar/SearchBar";
import {trimName} from "../utils/utils";
import classes from "./ProjectStyle.module.css";

import TextField from '@mui/material/TextField';

import LoadingButton from '@mui/lab/LoadingButton';
import Button from '@mui/material/Button';
import Dialog from '@mui/material/Dialog';
import DialogActions from '@mui/material/DialogActions';
import DialogContent from '@mui/material/DialogContent';
import DialogContentText from '@mui/material/DialogContentText';
import DialogTitle from '@mui/material/DialogTitle';
import axios from "axios";
import IconButton from "@mui/material/IconButton";
import MoreVertIcon from "@mui/icons-material/MoreVert";
import MenuItem from "@mui/material/MenuItem";
import debounce from "lodash/debounce";

const str2color = (input) => {
    let hash = [...(input)].reduce((acc, char) => {
        return char.charCodeAt(0) + ((acc << 5) - acc);
    }, 0);
    return `hsla(${hash % 360}, 95%, 35%, 0.9)`;
};

const Projects = () => {
    const {cache} = useSWRConfig();
    const [searchActivated, setSearchActivated] = useState(false);
    const [showCreateProject, setShowCreateProject] = useState(false);
    const [showArchived, setShowArchived] = useState(false);
    const [showActive, setShowActive] = useState(true);
    const [openMenu, setOpenMenu] = useState(false)
    const [anchorEl, setAnchorEl] = React.useState<null | HTMLElement>(null);

    const {data: projects, mutate: mutateProjects} = useSWR(
        "/web/projects",
        (url) => fetch(url).then((res) => res.json()),
        {refreshInterval: 30000}
    );

    const [hiddenProjects, setHiddenProjects] = useState([]);
    const [filterTerm, setFilterTerm] = useState("");

    useEffect(() => {
        if (!projects) return;
        let hidden = projects
            .filter((project) => {
                if (!project.Name.toLowerCase().includes(filterTerm.toLowerCase())) {
                    return true
                } else {
                    if (showActive) {
                        if (!project.archived) {
                            return false
                        }
                    }
                    if (showArchived) {
                        if (project.archived) {
                            return false
                        }
                    }
                    return true

                }

            })
            .map((project) => project.id);

        setHiddenProjects(hidden);
    }, [projects, filterTerm, showArchived, showActive]);

    const handleProjectCreated = (p) => {
        mutateProjects([...projects, p]);
    };

    const handleChange = (val) => {
        setFilterTerm(val);
    };

    // const prefetchGroups = async (project) => {
    //     let url = "/web/projects/" + project + "/groupindex"
    //     if (cache.get(url)) return;
    //     mutate(url, fetch(url).then(res => res.json()))
    // };

    function showArchivedChanged(event) {
        setShowArchived(event.target.checked)
    }

    function showActiveChanged(event) {
        setShowActive(event.target.checked)
    }

    const handleClick = (event: React.MouseEvent<HTMLElement>) => {
        setOpenMenu(true)
        setAnchorEl(event.currentTarget);
    };
    const handleClose = () => {
        setOpenMenu(false)
        setAnchorEl(null);
    };

    return (
        <div className={classes.pageStyle}>
            <Header/>
            <div className={classes.pageInnerWrapper}>
                <div style={{display: "flex"}}>
                    <div style={{width: "100vw"}}>
                        <SearchBar
                            searchActivated={searchActivated}
                            setSearchActivated={setSearchActivated}
                            handleChange={handleChange}
                            searchInput={filterTerm}
                            isLoading={!projects}
                            withButton={true}
                            buttonText="New project"
                            buttonClickHandler={() => setShowCreateProject(true)}
                            buttonIcon={<AddIcon/>}
                        />
                    </div>

                    <div style={{marginLeft: "20px", marginTop: "20px"}}>
                        <IconButton
                            onClick={handleClick}
                        >
                            <MoreVertIcon/>
                        </IconButton>
                        <Menu
                            anchorEl={anchorEl}
                            open={openMenu}
                            onClose={handleClose}
                        >
                            <MenuItem>
                                <FormControlLabel
                                    style={{marginLeft: "10px", marginRight: "10px"}}

                                    control={<Switch checked={showActive}
                                                     onClick={(e) => showActiveChanged(e)}
                                                     aria-label="Active projects"/>}
                                    label="Active projects"/>
                            </MenuItem>
                            <MenuItem>
                                <FormControlLabel
                                    style={{marginLeft: "10px", marginRight: "10px"}}

                                    control={<Switch checked={showArchived} onClick={(e) => showArchivedChanged(e)}
                                                     aria-label="Archived projects"/>}
                                    label="Archived projects"/>
                            </MenuItem>
                        </Menu>


                    </div>
                </div>


                <div className={classes.projectCardOuterWrapper}
                     style={{margin: !projects ? "20px 0px" : null}}
                >
                    {!projects ? (
                        new Array(12).fill(0).map((r, index) => <Skeleton
                            variant="rectangular"
                            key={index}
                            sx={{width: "100%"}}
                            animation="wave"
                            height={268}
                        />)
                    ) : (
                        <>
                            {projects.map((project, i) =>
                                !hiddenProjects.includes(project.id) ? (
                                    <div
                                        draggable="true"
                                        key={project.id}>
                                        {/*onMouseEnter={(e) => prefetchGroups(project.id)}>*/}
                                        <ProjectCard
                                            avatarBgColor={str2color(project.Name)}
                                            avatarName={trimName(project.Name)}
                                            projectName={project.Name}
                                            projectId={project.id}
                                            projectDescription={project.info || "No description."}
                                            creationDate={project.date}
                                            projectOwner={project.owner}
                                            archived={project.archived}
                                        />
                                    </div>
                                ) : null
                            )}
                        </>
                    )}
                </div>
            </div>
            <CreateProjectDialog open={showCreateProject} handleClose={() => setShowCreateProject(false)}
                                 handleProjectCreated={handleProjectCreated}/>
        </div>
    )
};

export default Projects;

const CreateProjectDialog = ({
                                 open, handleClose, handleProjectCreated
                             }) => {

    const [name, setName] = React.useState('');
    const [description, setDescription] = React.useState('');
    const [creating, setCreating] = React.useState(false);
    const [check, setCheck] = React.useState(false)
    const [loading, setLoading] = React.useState(false)


    React.useEffect(() => {
        setName('');
        setDescription('');
        setCreating(false);
    }, [open]);


    const create = () => {
        setCreating(true);
        axios.post('/web/projects', {name, description}).then(res => {
            setCreating(false);
            handleProjectCreated(res.data);
            handleClose();
        });
    }

    function checkName(nameToBeChecked) {
        let data = {
            name: nameToBeChecked,
        }

        axios.post(`/web/projects/check`, data).then((r) => {
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

    return (
        <Dialog open={open} onClose={handleClose}>
            <DialogTitle>New project</DialogTitle>
            <DialogContent>

                <DialogContentText sx={{marginBottom: "10px"}}>Please enter a name and a short
                    description.</DialogContentText>

                <TextField
                    autoFocus
                    margin="dense"
                    variant="outlined"
                    label="Project name"
                    fullWidth
                    value={name}
                    placeholder={"project-carbon"}
                    sx={{marginBottom: "8px"}}
                    onChange={(e) => setName(e.target.value)}
                />
                <TextField
                    margin="dense"
                    label="Project description"
                    variant="outlined"
                    fullWidth
                    multiline
                    value={description}
                    onChange={(e) => setDescription(e.target.value)}
                />
                {!check && name && !loading && < Typography style={{
                    color: 'red',
                    fontSize: '14px'
                }}>Name already in use. Please choose another one.</Typography>}
            </DialogContent>
            <DialogActions>
                <Button onClick={handleClose}>Cancel</Button>
                <LoadingButton loading={creating} onClick={create} disabled={!check}>Create</LoadingButton>
            </DialogActions>
        </Dialog>
    )
}

