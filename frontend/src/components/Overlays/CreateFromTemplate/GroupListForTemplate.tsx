import React, {useEffect, useMemo} from 'react';

import Skeleton from '@mui/material/Skeleton';
import classes from './GroupListForTemplateStyle.module.css';
import styles from "./GroupListForTemplate.module.css";
import {CustomNodeForTemplate} from "./CustomNodeForTemplate";
import {getBackendOptions, MultiBackend, Tree} from "@minoru/react-dnd-treeview";
import {DndProvider} from "react-dnd";
import useSWR from 'swr';
import axios from "axios";
import useGroupIndexStore from "../../../zustand/groupIndexStore";


const GroupListForTemplate = ({project, setItems, searchTerm = "", typedShortID, invalidShortID, setCurrentGroup,
                              groups}) => {

    const [selected, setSelected] = React.useState({group_id: ""});



    // const groups = useMemo(() => {
    //     function checkShortID(item) {
    //         console.log(item.shortId)
    //         return item.shortId == typedShortID
    //     }
    //
    //     console.log(typedShortID)
    //     console.log(invalidShortID)
    //
    //     if (!unfilteredGroups) return undefined;
    //     if (searchTerm === "") {
    //         if (!(invalidShortID) && typedShortID) {
    //             console.log(typedShortID)
    //
    //             return unfilteredGroups.reduce((res, g) => {
    //                 console.log(1)
    //                 let exps = g.experiments.filter(checkShortID);
    //                 let smps = g.samples.filter(checkShortID);
    //                 if (exps.length > 0 || smps.length > 0) {
    //                     res.push({...g, experiments: exps, samples: smps});
    //                 }
    //                 return res
    //             },[])
    //         } else {
    //             return unfilteredGroups;
    //         }
    //     } else {
    //         return unfilteredGroups.reduce((res, g) => {
    //             if (g.name.toLowerCase().includes(searchTerm.toLowerCase())) {
    //                 res.push(g)
    //             } else {
    //                 let exps = g.experiments.filter(e => e.name.toLowerCase().includes(searchTerm.toLowerCase()));
    //                 let smps = g.samples.filter(s => s.name.toLowerCase().includes(searchTerm.toLowerCase()));
    //                 if (exps.length > 0 || smps.length > 0) {
    //                     res.push({...g, experiments: exps, samples: smps});
    //                 }
    //             }
    //             return res;
    //         }, []);
    //     }
    // }, [unfilteredGroups, searchTerm, invalidShortID, typedShortID]);

    function findAllParentsRecursive(inputParentIdList) {
        if (groups === undefined) {
            return [];
        }
        if (inputParentIdList === undefined) {
            return [];
        }
        let parentIdList = [...inputParentIdList];
        let newParentIdList = []
        inputParentIdList.map((groupId) => {
            groups.map((item) => {
                if (((item.type === "Groups") || (item.id.includes("/sep/"))) && item.parent == groupId) {
                    if (!(parentIdList.includes(item.id))) {
                        parentIdList.push(item.id);
                    }
                    if (!(newParentIdList.includes(item.id))) {
                        newParentIdList.push(item.id);
                    }
                }
            })
        })
        if (newParentIdList.length > 0) {
            newParentIdList = findAllParentsRecursive(newParentIdList);
            newParentIdList.map((parentId) => {
                if (!(parentIdList.includes(parentId))) {
                    parentIdList.push(parentId);
                }
            })
        }
        return parentIdList;
    }

    function findAllItemsFromParent(parentIdList) {
        if (groups === undefined) {
            return [];
        }
        let items = []
        groups.map((item) => {
            if ((parentIdList.includes(item.parent)) && (item.type !== "Groups") && !(item.id.includes("/sep/"))) {
                items.push(item)

            }
        })
        return items;
    }

    function researchitems(node) {

        if (groups === undefined) {
            return [];
        }
        let res = []

        if (Object.keys(node).length === 0) {
            return []
        }
        if ((node.type === 'Groups') || (node.id.includes("/sep/"))) {
            let parentIdList = findAllParentsRecursive([node.id]);
            res = [...findAllItemsFromParent(parentIdList)]
        } else {
            groups.map((item) => {
                if (node.id === item.id) {
                    res.push(item)
                }
            })
        }

        return res;
    }

    const handleSelect = (node) => {
        setSelected(node);
        setCurrentGroup({"id": node.id, "name": node.name, "parent": node.parent});
        let items = researchitems(node);
        setItems(items)
    };
    const handleSelectForDrag = (event, nodeIds) => {
        // keep, since node needs a method
    };


    // useEffect(() => {
    //     if (selected.length < 1) return;
    //     if (!(groups && groups.length > 0)) return;
    //
    //     let items = selected.map(s => {
    //         let group = s.substring(0, 24);
    //         let type = s.substring(24);
    //         let g = groups.find(g => g.id === group);
    //         if (!g) return [];
    //         if (type === 'experiments') return g.experiments;
    //         else if (type === 'samples') return g.samples;
    //         else return [...g.experiments, ...g.samples];
    //     }).flat(1);
    //     let selectedGroups = selected.map(s => s.substring(0, 24));
    //     changeGroup(selectedGroups[0], items);
    // }, [selected, groups]);

    // useEffect(() => {
    //     if (!(groups && groups.length > 0)) return;
    //     if (selected.length < 1 || !groups.find(g => g.id === selected[0].substring(0, 24))) {
    //         setSelected([groups[0].id]);
    //     }
    // }, [groups, selected]);

    function handleDrop() {

    }

    function handleCanDrag() {
        return false;
    }

    return (
        <div className={classes.templateList}>
            {(groups === undefined) ? (<p>No groups</p>) :
                <DndProvider backend={MultiBackend} options={getBackendOptions()}>

                    <Tree
                        tree={groups}
                        rootId={0}
                        classes={{
                            root: styles.treeRoot,
                            draggingSource: styles.draggingSource,
                            dropTarget: styles.dropTarget
                        }}
                        onDrop={handleDrop}
                        canDrag={handleCanDrag}
                        render={(node, {depth, isOpen, onToggle}) => (
                            <CustomNodeForTemplate
                                node={node}
                                depth={depth}
                                isOpen={isOpen}
                                onToggle={onToggle}
                                onSelect={handleSelect}
                                onSelectForDrag={handleSelectForDrag}
                                style={{display: "flex"}}
                                selected={selected}
                                setSelected={setSelected}
                            />
                        )}
                    />
                </DndProvider>}
            {/*<TreeView*/}
            {/*    id="group-list"*/}
            {/*    selected={selected}*/}
            {/*    multiSelect*/}
            {/*    onNodeSelect={handleSelect}*/}
            {/*    defaultCollapseIcon={<ArrowDropDownIcon/>}*/}
            {/*    defaultExpandIcon={<ArrowRightIcon/>}*/}
            {/*    defaultEndIcon={<div style={{width: 24}}/>}*/}
            {/*    sx={{flexGrow: 1, maxWidth: 400}}*/}
            {/*>*/}
            {/*    {groups && groups.map((g, index) => (*/}
            {/*        < StyledTreeItem*/}
            {/*            key={uuidv4()}*/}
            {/*            nodeId={g.id}*/}
            {/*            labelText={g.name}*/}
            {/*            labelIcon={FolderIcon}*/}
            {/*            color="#1a73e8"*/}
            {/*            bgColor="#e8f0fe"*/}
            {/*        >*/}
            {/*            {g.experiments.length > 0 && <StyledTreeItem*/}
            {/*                nodeId={g.id + 'experiments'}*/}
            {/*                labelText="Experiments"*/}
            {/*                labelIcon={BiotechIcon}*/}
            {/*                color="#3c8039"*/}
            {/*                bgColor="#e6f4ea"*/}
            {/*            />}*/}
            {/*            {g.samples.length > 0 && <StyledTreeItem*/}
            {/*                nodeId={g.id + 'samples'}*/}
            {/*                labelText="Samples"*/}
            {/*                labelIcon={ScienceIcon}*/}
            {/*                color="#e3742f"*/}
            {/*                bgColor="#fcefe3"*/}
            {/*            />}*/}
            {/*        </StyledTreeItem>))}*/}
            {/*</TreeView>*/}
        </div>
    );

}

export default GroupListForTemplate;