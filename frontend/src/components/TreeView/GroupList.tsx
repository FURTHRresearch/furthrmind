import React, {useEffect, useState, useCallback} from 'react';

import useGroupIndexStore from '../../zustand/groupIndexStore';
import {getBackendOptions, MultiBackend, Tree} from "@minoru/react-dnd-treeview";
import {DndProvider} from "react-dnd";
import {CustomNode} from "./CustomNode";
import {MultipleDragPreview} from "./MultiDragPreview";
import styles from "./GroupList.module.css";
import {theme} from "./theme";
import {CssBaseline, ThemeProvider} from "@mui/material";
import axios from "axios";
import {useParams} from "react-router-dom";
import Dialog from "@mui/material/Dialog";
import DialogTitle from "@mui/material/DialogTitle";
import DialogContent from "@mui/material/DialogContent";
import DialogContentText from "@mui/material/DialogContentText";
import DialogActions from "@mui/material/DialogActions";
import Button from "@mui/material/Button";
import LoadingButton from "@mui/lab/LoadingButton";


const fetcher = (url) => fetch(url).then((res) => res.json());


const GroupList = ({
                       project,
                       loadingGroups,
                       setLoadingGroups = (val) => null,
                       setCurrentGroup,
                       setGroupName,
                       selectedTab, groups, mutateGroups
                   }) => {

    const setSelection = useGroupIndexStore((state) => state.setSelection);
    const selectedItems = useGroupIndexStore((state) => state.selectedItems);
    const [treeNodes, setTreeNodes] = React.useState([]);
    const [selectedForDrag, setSelectedForDrag] = React.useState([]);
    const [dropStarted, setDropStarted] = useState(false)
    const [open, setOpen] = useState(false)
    const [type, setType] = useState("")
    const [oldGroupName, setOldGroupName] = useState("")
    const [newGroupName, setNewGroupName] = useState("")
    const [newGroupId, setNewGroupId] = useState("")


    const handleSelect = (event, node) => {
        let itemList = []
        let itemIdList = []
        if (!event.ctrlKey && !event.metaKey) {
            itemList.push({
                id: node.id, type: node.type, group_id: node.group_id,
                name: node.name, parent: node.parent
            })
            setSelection(itemList)
        } else {
            // ctrl or command is key pressed, MultiSelection
            if ((node.type === "Groups") || (node.id.includes("/sep/"))) {
                // selected node is either a group or a category node. In this case, only this node can be selected.
                itemList = []
                itemIdList = []

            } else {
                selectedItems.map((s) => {
                    // remove all groups and category nodes
                    if (!(s.type === "Groups") && !(s.id.includes("/sep/"))) {
                        itemList.push(s)
                        itemIdList.push(s.id)
                    }
                })
            }

            if (itemIdList.includes(node.id)) {
                itemList.splice(itemIdList.indexOf(node.id), 1);
                setSelection(itemList);
            } else {
                itemList.push({
                    id: node.id, type: node.type, group_id: node.group_id,
                    name: node.name, parent: node.parent
                })
                setSelection(itemList);
            }
        }
        if (itemList.length > 0) {
            groups.map((g) => {
                if (g.id === itemList[itemList.length - 1].group_id) {
                    setGroupName(g.name)
                    setCurrentGroup(g)

                }
            })
        } else {
            setGroupName("")
            setCurrentGroup(null)
        }
    };

    useEffect(() => {

    }, []);

    function handleSelectForDrag(event, node) {
        if (node === undefined) {
            return
        }

        let itemList = []
        let itemIdList = []
        if ((node.type === "Groups") || (node.id.includes("/sep/"))) {
            // selected node is either a group or a category node. In this case, only this node can be selected.
            itemList = []
            itemIdList = []

        } else {
            selectedItems.map((s) => {
                // remove all groups and category nodes
                if (!(s.type === "Groups") && !(s.id.includes("/sep/"))) {
                    itemList.push(s)
                    itemIdList.push(s.id)
                }
            })
        }

        if (!(itemIdList.includes(node.id))) {
            itemList.push({
                id: node.id, type: node.type, group_id: node.group_id,
                name: node.name, parent: node.parent
            })
        }
        setSelectedForDrag(itemList);
    }

    useEffect(() => {
        if (groups === undefined) {
            setLoadingGroups(true);
            if (!dropStarted) {
                setTreeNodes([])
            }

        } else {
            if (loadingGroups) {
                if (groups.length > 0) {
                    const newSelection = compareSelection()
                    if (newSelection.length > 0) {
                        setSelection(newSelection)
                    } else {
                        setSelection([{
                            group_id: groups[0]["group_id"],
                            type: groups[0]["type"], id: groups[0]["id"],
                            name: groups[0]["name"], parent: groups[0]["parent"]
                        }])
                    }

                }
            }
            setLoadingGroups(false);
            if (!dropStarted) {
                const groupsCopy = [...groups]
                setTreeNodes(groupsCopy);
            }
        }
    }, [groups, setLoadingGroups]);


    function compareSelection() {
        const currentSelection = [...selectedItems]
        const newSelection = []
        const idList = []
        groups.forEach(function (item) {
            idList.push(item.id)
        })
        currentSelection.map((s) => {
            if (idList.includes(s.id)) {
                newSelection.push(s)
            }
        })
        return newSelection

    }


    const handleClose = () => {
        setOpen(false)
    }
    const handleItemDrop = (newTree, options) => {
        let group_id = null
        if (options.dropTargetId !== 0) {
            group_id = options.dropTargetId.substring(0, 24);
        }
        setNewGroupId(group_id)
        if (selectedForDrag.length === 1 && selectedForDrag[0].id.includes("/sep/")) {
            groups.map((g) => {
                if (g.id == newGroupId) {
                    setNewGroupName(g.name)
                } else if (g.id === selectedForDrag[0].group_id) {
                    setOldGroupName(g.name)
                }
            })
            setOpen(true)
            setType(selectedForDrag[0].type)
        } else {
            moveMethod(group_id)
        }
    }

    const moveMethod = (newGroupId) => {
        setOpen(false)
        setDropStarted(true)
        const groupsCopy = [...groups]

        // changes to the database will be made at the end. A list with objects
        // will be keep track of the changes.
        // [{"type": '', "id":"", "group_id": ""}
        let backendChangeList = []
        if (selectedForDrag.length === 1 && selectedForDrag[0].type === "Groups") {
            // a groups is dropped into another group
            // => change only the parent and group id of the selected group
            let newParent = newGroupId
            let oldGroupID = selectedForDrag[0].group_id
            if (newGroupId === null) {
                newParent = 0
            }
            if (oldGroupID === newGroupId) {
                setDropStarted(false)
                return;
            }
            groupsCopy.map((item) => {
                if (item.id === selectedForDrag[0].id) {
                    item.parent = newParent
                    item.group_id = newGroupId
                    backendChangeList.push({
                        id: item.id, new_group_id: newGroupId,
                        type: "Groups", old_group_id: oldGroupID
                    })
                }
            })
            selectedForDrag[0].group_id = newGroupId
            selectedForDrag[0].parent = newParent
            setSelection(selectedForDrag)


        } else if (selectedForDrag.length === 1 && selectedForDrag[0].id.includes("/sep/")) {
            // a complete category is moved
            // all items in this category must get a new parent. old parent is the
            // selected item. old parent visible must be set to fals,
            // new parent visible to true
            // new parent gets selected
            if (newGroupId === null) {
                // this is a forbidden move
                setDropStarted(false)
                return
            }
            let oldParent = selectedForDrag[0].id
            let oldGroupID = selectedForDrag[0].group_id
            let newParent = oldParent.replace(oldGroupID, newGroupId)

            if (oldGroupID === newGroupId) {
                setDropStarted(false)
                return;
            }

            let newParentFound = false
            groupsCopy.map((item) => {
                if (item.parent === oldParent) {
                    item.parent = newParent
                    item.group_id = newGroupId

                    backendChangeList.push({
                        id: item.id, new_group_id: newGroupId,
                        type: item.type, old_group_id: oldGroupID
                    })

                }
                
                if (item.id == newParent) {                    
                    item.visible = true
                    newParentFound = true
                }
                if (item.id == oldParent) {
                    item.visible = false
                }
            })
            if (!newParentFound) {
                let cat_node = {
                    id: newParent,
                    name: selectedForDrag[0].name,
                    type: selectedForDrag[0].type,
                    how_type: type,
                    short_id: "",
                    parent: newGroupId,
                    droppable: false,
                    expandable: true,
                    group_id: newGroupId,
                    visible: true,
                    text: selectedForDrag[0].text,
                }            
                groupsCopy.push(cat_node)
            }
            setSelection([{
                id: newParent, type: selectedForDrag[0].type,
                group_id: newGroupId,
                name: selectedForDrag[0].name, parent: newGroupId
            }])


        } else {
            // selceted items are direct items, no group or container
            if (newGroupId === null) {
                // this is a forbidden move
                setDropStarted(false)
                return
            }
            // if items are from dirfferent categories, new parent will be not the same
            // If an item, e.g. a exp is dropped into a group, the new parent
            // will not be the group itself, but the exp container in the group.
            // a list with new parent will be created in order to change the visibile flag

            let newParentList = []
            let oldParentList = []
            const newParentOldParentMapping = {}
            const nodeMapping = {}
            groupsCopy.map((item) => {
                nodeMapping[item.id] = item
                selectedForDrag.map((selected) => {

                    if (item.id === selected.id) {
                        let oldParent = selected.parent
                        let oldGroupID = selected.group_id
                        if (oldGroupID !== newGroupId) {
                            let newParent = oldParent.replace(oldGroupID, newGroupId)
                            newParentList.push(newParent)
                            oldParentList.push(oldParent)
                            newParentOldParentMapping[newParent] = oldParent
                            selected.group_id = newGroupId;
                            selected.parent = newParent
                            item.group_id = newGroupId;
                            item.parent = newParent

                            backendChangeList.push({
                                id: item.id, new_group_id: newGroupId,
                                type: item.type, old_group_id: oldGroupID
                            })
                        }

                    }
                })
            })
            setSelection(selectedForDrag)
            let newParentsFound = []
            
            groupsCopy.map((item) => {
                if (newParentList.includes(item.id)) {
                    item.visible = true
                    newParentsFound.push(item.id)
                } else if (oldParentList.includes(item.parent)) {
                    oldParentList.splice(oldParentList.indexOf(item.parent), 1)
                }
            })

            groupsCopy.map((item) => {
                if (oldParentList.includes(item.id)) {
                    item.visible = false
                }
            })
            newParentList.map((newParent) => {
                if (!newParentsFound.includes(newParent)) {
                    let oldParent = newParentOldParentMapping[newParent]
                    let oldNode = nodeMapping[oldParent]
                    let cat_node = {
                        id: newParent,
                        name: oldNode.name,
                        type: oldNode.type,
                        how_type: oldNode.how_type,
                        short_id: "",
                        parent: newGroupId,
                        droppable: false,
                        expandable: true,
                        group_id: newGroupId,
                        visible: true,
                        text: oldNode.text,
                    }
                    groupsCopy.push(cat_node)
                }
            })
        }
        mutateGroups(groupsCopy, {revalidate: false});
        setTreeNodes(groupsCopy)
        setDropStarted(false)
        if (backendChangeList.length > 0) {
            axios.post("/web/items/move", backendChangeList)
        }

    }


    return (
        <div>
            <ThemeProvider theme={theme}>
                <CssBaseline/>

                {treeNodes && (
                    <DndProvider backend={MultiBackend} options={getBackendOptions()}>
                        <Tree
                            tree={treeNodes}
                            sort={false}
                            rootId={0}
                            onDrop={handleItemDrop}
                            classes={{
                                root: styles.treeRoot,
                                draggingSource: styles.draggingSource,
                                dropTarget: styles.dropTarget
                            }}
                            render={(node, {depth, isOpen, onToggle}) => (
                                <CustomNode
                                    key={node.id}
                                    node={node}
                                    depth={depth}
                                    isOpen={isOpen}
                                    onToggle={onToggle}
                                    onSelect={handleSelect}
                                    onSelectForDrag={handleSelectForDrag}
                                    style={{display: "flex"}}
                                />
                            )}
                            dragPreviewRender={(monitorProps) => {
                                return <MultipleDragPreview nodes={selectedForDrag}/>;


                                // return <SingleDragPreview node={selectedForDrag[0]}/>;
                            }}
                        />
                    </DndProvider>
                )
                }


            </ThemeProvider>
            {open && (<MoveDialog open={open} handleClose={handleClose}
                                  type={type} oldGroupName={oldGroupName}
                                  newGroupName={newGroupName}
                                  newGroupId={newGroupId}
                                  moveMethod={moveMethod}/>)}


        </div>


    )
}

export default GroupList;

const MoveDialog = ({open, handleClose, type, oldGroupName, newGroupName, newGroupId, moveMethod}) => {
    const [loading, setLoading] = React.useState(false);
    const params = useParams();

    function handleMove() {
        handleClose()
        moveMethod(newGroupId)
    }

    return (
        <Dialog open={open} onClose={handleClose}>
            <DialogTitle>Move items?</DialogTitle>
            <DialogContent>

                <DialogContentText>Do you want to move
                    all {type} from {oldGroupName} to {newGroupName}.</DialogContentText>

            </DialogContent>
            <DialogActions>
                <Button onClick={handleClose} disabled={loading}>Cancel</Button>
                <LoadingButton loading={loading} onClick={handleMove} color="warning">Move items</LoadingButton>
            </DialogActions>
        </Dialog>
    )
}