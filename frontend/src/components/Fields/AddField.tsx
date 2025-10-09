import React, {useEffect, useState} from 'react';

import {LinearProgress} from '@mui/material';
import Box from '@mui/material/Box';
import TextField from '@mui/material/TextField';
import axios from 'axios';
import Autocomplete, {createFilterOptions} from '@mui/material/Autocomplete';
import {useParams} from 'react-router-dom';
import useSWR from 'swr';

import NewFieldOverlay from "./NewFieldOverlay";

const fetcher = (url) => fetch(url).then((res) => res.json());

const AddField = ({target, targetId, onAdded, notebook, admin}) => {
    const [name, setName] = useState('');
    const [adding, setAdding] = useState(false);
    const [showNewFieldOverlay, setShowNewFieldOverlay] = useState(false);
    const [renderNewFieldOverlay, setRenderNewFieldOverlay] = useState(false);
    const [options, setOptions] = useState([]);
    const params = useParams();

    const {data: fields} = useSWR(`/web/projects/${params.project}/fields`, fetcher);
    const createNewNameOption = "-- Create new field --"

    useEffect(() => {

        let o = []
        if (admin) {
            o.push(createNewNameOption)
        }
        if (fields) {
            fields.map((f) => {
                if (notebook) {
                    if (f.type === "MultiLine") {
                        o.push(f.name)
                    }
                } else {
                    o.push(f.name)
                }
            })
        }
        setOptions(o)
    }, [fields, notebook]);

    const createField = (name) => {
        if (name.length === 0) return;
        setName(name)
        if (name === createNewNameOption) {
            if (admin === true) {
                setShowNewFieldOverlay(true);
                setRenderNewFieldOverlay(true);
            }

        } else if (fields.find(f => f.name === name)) {
            setAdding(true);
            axios.post(`/web/projects/${params.project}/item/${target}/${targetId}/fields`, {name}).then((r) => {
                setName('');
                onAdded(r.data);
                setAdding(false);
            });
        } else {
            if (admin === true) {
                setShowNewFieldOverlay(true);
                setRenderNewFieldOverlay(true);
            }
        }
    }

    return (
        <>
            <Autocomplete
                freeSolo
                autoHighlight
                disableClearable
                options={fields ? options : []}
                renderInput={(params) => <TextField {...params} variant="filled"
                                                    hiddenLabel placeholder="Add a new field"/>}
                onChange={(e, nv) => {
                    createField(nv);
                }}
                disabled={adding}
                value={name}
                // @ts-ignore
                filterOptions={(options, params) => {
                    const filtered = createFilterOptions()(options, params);

                    const {inputValue} = params;
                    // Suggest the creation of a new value
                    // @ts-ignore
                    const isExisting = options.some((option) => inputValue === option);
                    if (inputValue !== '' && !isExisting) {
                        filtered.push({
                            inputValue,
                            title: `Add "${inputValue}"`,
                        });
                    }

                    return filtered;
                }}
                // @ts-ignore
                getOptionLabel={(option) => (typeof option === 'string' ? option : option.inputValue)}
                // @ts-ignore
                renderOption={(props, option) =>
                    <li {...props}>{(typeof option === 'string' ? option : option.title)}</li>}
            />

            {adding && <Box sx={{width: '100%', paddingTop: '8px'}}><LinearProgress/></Box>}
            {renderNewFieldOverlay ?
                <NewFieldOverlay
                    targetType={target}
                    targetId={targetId}
                    // @ts-ignore
                    initialName={(typeof name === 'string' ? name : name.inputValue)}
                    show={showNewFieldOverlay}
                    onClose={() => {
                        setName('');
                        setShowNewFieldOverlay(false);
                    }}
                    onExited={() => {
                        setName('');
                        setRenderNewFieldOverlay(false)
                    }}
                    onCreated={(data) => {
                        onAdded(data);
                        setShowNewFieldOverlay(false);
                        setName('');
                    }}
                    createNewNameOption={createNewNameOption}
                    project={params.project}
                /> : null
            }
        </>
    );
}

export default AddField;


