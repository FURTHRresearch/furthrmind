import EditIcon from '@mui/icons-material/Edit';
import {Button, Typography} from '@mui/material';
import {useWindowWidth} from '@react-hook/window-size';
import axios from 'axios';
import {useState} from 'react';
import {useParams} from 'react-router-dom';
import useSWR from 'swr';
import classes from './style.module.css';

const fetcher = url => fetch(url).then(res => res.json());

export default function General() {
    const onlyWidth = useWindowWidth();
    const params = useParams();
    const {data: project, mutate} = useSWR(`/web/projects/${params.project}/settings`, fetcher);

    const [editMode, setEditMode] = useState<any>({
        name: false,
        description: false
    });

    const handleEditState = (fieldName: any, state: any) => {
        setEditMode({
            [fieldName]: state
        })
    }

    const saveName = () => {
        axios.post(`/web/projects/${params.project}`, {name: project.name});
        setEditMode({
            name: false
        });
    }
    const saveDescription = () => {
        axios.post(`/web/projects/${params.project}`, {info: project.info});
        setEditMode({
            description: false
        });
    }

    return (
        <div className={classes.parentWrap}>
            <div className={classes.fieldWrap}>
                <Typography variant="subtitle2" gutterBottom component="div">
                    Project name
                </Typography>
                <div className={classes.textFieldOuterWrap}>
                    <div className={classes.textField}>
                        <input
                            type="text"
                            placeholder="Project name"
                            className={!editMode.name ? classes.inputFieldReadOnly : classes.inputField}
                            value={project?.name}
                            readOnly={!editMode.name}
                            onChange={(e) => {
                                mutate({...project, name: e.target.value}, false)
                            }}
                        />
                        {!editMode.name &&
                            <EditIcon sx={{fontSize: onlyWidth < 576 ? "14px" : "18px", cursor: "pointer"}}
                                      onClick={() => handleEditState("name", true)}
                            />
                        }
                    </div>
                    {
                        editMode.name &&
                        <div className={classes.editStateWrap}>
                            <Button
                                variant="outlined"
                                size="small"
                                onClick={() => handleEditState("name", false)}
                            >Cancel</Button>
                            <Button variant="contained" size="small" onClick={saveName}>Save</Button>
                        </div>
                    }
                </div>
            </div>

            <div className={classes.fieldWrap}>
                <Typography variant="subtitle2" gutterBottom component="div">
                    Description
                </Typography>
                <div className={classes.textFieldOuterWrap}>
                    <div className={classes.textField}>
                        <textarea placeholder="Short descripton"
                                  className={!editMode.description ? classes.inputFieldReadOnly : classes.inputField}
                                  value={project?.info}
                                  readOnly={!editMode.description}
                                  rows={4}
                                  onChange={(e) => {
                                      mutate({...project, info: e.target.value}, false)
                                  }}
                        />
                        {!editMode.description && <EditIcon
                            sx={{fontSize: onlyWidth < 576 ? "14px" : "18px", cursor: "pointer"}}
                            onClick={() => handleEditState("description", true)}
                        />
                        }
                    </div>
                    {
                        editMode.description &&
                        <div className={classes.editStateWrap}>
                            <Button
                                variant="outlined"
                                size="small"
                                onClick={() => handleEditState("description", false)}
                            >Cancel</Button>
                            <Button variant="contained" size="small" onClick={saveDescription}>Save</Button>
                        </div>
                    }
                </div>

            </div>

            <div className={classes.fieldWrap}>
                <Typography variant="subtitle2" gutterBottom component="div">
                    Project id
                </Typography>
                <div className={classes.textFieldOuterWrap}>
                    <div className={classes.textField}>
                        <input
                            type="text"
                            className={!editMode.name ? classes.inputFieldReadOnly : classes.inputField}
                            value={params.project}
                            readOnly={true}
                        />
                    </div>
                </div>
            </div>

        </div>
    )
}
