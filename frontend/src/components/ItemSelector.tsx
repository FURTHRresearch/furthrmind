import CheckBoxIcon from '@mui/icons-material/CheckBox';
import CheckBoxOutlineBlankIcon from '@mui/icons-material/CheckBoxOutlineBlank';
import Autocomplete from '@mui/material/Autocomplete';
import Checkbox from '@mui/material/Checkbox';
import TextField from '@mui/material/TextField';

import React, {useCallback, useEffect, useState} from 'react';

import ResearchItemOverlay from './Overlays/ResearchItemOverlay';

import axios from 'axios';
import useSWR, {useSWRConfig} from "swr";
import debounce from "lodash/debounce";

const fetcher = url => fetch(url).then(res => res.json());


const icon = <CheckBoxOutlineBlankIcon fontSize="small"/>;
const checkedIcon = <CheckBoxIcon fontSize="small"/>;

// function groupBy(xs, key) {
//     return xs.reduce(function (rv, x) {
//         (rv[x[key]] = rv[x[key]] || []).push(x);
//         return rv;
//     }, {});
// };

const ItemSelector = ({linked_items, group, project, data, 
    mutateExp, itemId, type, writable, _protected, groups, mutateGroups}) => {
    const [renderItemOverlay, setRenderItemOverlay] = React.useState(false);
    const [showItemOverlay, setShowItemOverlay] = React.useState(false);
    const [showItemOverlayType, setShowItemOverlayType] = React.useState("");
    const [queryString, setQueryString] = useState("")
    // const [samples, setSamples] = React.useState([])
    // const [researchItems, setResearchItems] = React.useState([])
    const [mergedItems, setMergedItems] = React.useState([])
    const [chipProps, setChipProps] = React.useState(
        {
            clickable: true,
            disabled: false,
            onClick: (e: { target: any }) => {
                let name = e.target.textContent
                let id = linked_items.find(s => s.Name === name).id
                let type = linked_items.find(s => s.Name === name).Category
                if (type === 'Sample') {
                    type = 'samples'
                } else if (type === "Experiment") {
                    type = "experiments"
                } else {
                    type = "researchitems"
                }
                setShowItemOverlay(id);
                setShowItemOverlayType(type)
                setRenderItemOverlay(true);
            }
        })
    // const {data: smp} = useSWR('/web/projects/' + project + '/samples', fetcher)
    // const {data: items} = useSWR('/web/projects/' + project + '/researchitems', fetcher)

    const {data: items} = useSWR(`/web/projects/${project}/selector_items?${queryString}`, fetcher)


    const {mutate: globalMutate} = useSWRConfig()
    useEffect(() => {
        if (items) {
            // setSamples(smp)
            // setResearchItems(items)

            const _mergedItems = items ? [...linked_items, ...items.filter(s => !linked_items.some(ss => ss.id === s.id))] : linked_items
            setMergedItems(_mergedItems);
        }

    }, [items])

    useEffect(() => {
        let chipPros = {
            clickable: true,
            disabled: false,
            onClick: (e: { target: any }) => {
                let name = e.target.textContent
                let id = linked_items.find(s => s.Name === name).id
                let type = linked_items.find(s => s.Name === name).Category
                if (type === 'Sample') {
                    type = 'samples'
                } else if (type === "Experiment") {
                    type = "experiments"
                } else {
                    type = "researchitems"
                }
                setShowItemOverlay(id);
                setShowItemOverlayType(type)
                setRenderItemOverlay(true);
            }
        }
        if (_protected) {
            chipPros["onDelete"] = null
        }
        setChipProps(chipPros)
    }, [_protected]);

    // const groups = useMemo(() => mergedItems ? groupBy(mergedItems, 'category') : [], [units])

    // let {data: allSamples} = useSWR('/web/groups/' + group + '/samples', fetcher);
    // let {data: allResearchitems} = useSWR('/web/groups/' + group + '/researchitems', fetcher);

    // if (allSamples == undefined)
    //     allSamples = []
    // if (allResearchitems == undefined)
    //     allResearchitems = []


    const save = (items) => {
        axios.post(`/web/item/${type}/${itemId}`, {linked_items: items}).then(() => {
            mutateExp({...data, linked_items: items})
        })
        items.map((item) => {
            let type = item.Category
            if (type === "Sample") {
                type = "samples"
            } else if (type === "Experiment") {
                type = "experiments"
            } else {
                type = "researchitems"
            }
            globalMutate(`/web/item/${type}/${item.id}`)

        })
    }

    function onCloseHandler() {
        setShowItemOverlay(false)
        setShowItemOverlayType("")
    }

    function createQueryString(input) {
        const url_options = new URLSearchParams({
            name: input
        }).toString()
        setQueryString(url_options)

    }

    function inputChange(e) {
        debouncedSetInput(e.target.value)
    }

    function autocompleteOnBlur() {
        debouncedSetInput("")
    }

    const debouncedSetInput = useCallback(debounce(createQueryString, 300), []);

    return (
        <>
            <Autocomplete
                multiple
                // disableClearable={!writable}
                onChange={(e, value) => save(value)}
                options={mergedItems}
                // options={mergedItems.sort((a, b) => a.Category.localeCompare(b.Category))}
                groupBy={(option) => option.DisplayedCategory}
                onInputChange={(e) => inputChange(e)}
                disabled={!writable}
                onBlur={() => autocompleteOnBlur()}
                ChipProps={chipProps}
                defaultValue={linked_items}
                getOptionLabel={(option: any) => option.Name}
                renderOption={(props, option: any, {selected}) => (
                    <li {...props} key={option.id}>
                        <Checkbox
                            icon={icon}
                            checkedIcon={checkedIcon}
                            style={{marginRight: 8}}
                            checked={selected}
                        />

                        {option.Name}
                    </li>
                )}
                renderInput={(params) => (
                    <TextField {...params} label="Linked items"/>
                )}
                // renderGroup={(params) => (
                //     <Box key={params.key}>
                //         <Typography fontSize={15} fontWeight={"bold"}>
                //             {params.group}
                //         </Typography>
                //         {params.children}
                //     </Box>
                // )}
            />
            {renderItemOverlay ? (
                <ResearchItemOverlay
                    onExited={() => setRenderItemOverlay(false)}
                    show={showItemOverlay !== false}
                    onClose={() => onCloseHandler()}
                    group={group}
                    project={project}
                    groups={groups}
                    mutateGroups={mutateGroups}
                    data={[{
                        id: showItemOverlay,
                        type: showItemOverlayType,
                        group_id: group
                    }]}

                />
            ) : null}
        </>
    );
}

    export default ItemSelector;