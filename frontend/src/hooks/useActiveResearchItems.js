import {useMemo} from "react";
import {useParams} from "react-router-dom";
import useGroupIndexStore from "../zustand/groupIndexStore";

function useActiveResearchItems(useGroupSelection = true, groups) {
    const params = useParams();
    const project = params.project;
    const selectedItems = useGroupIndexStore((state) => state.selectedItems);
    const selection = []


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

    const researchItems = useMemo(() => {
        if (groups === undefined) {
            return [];
        }
        let res = []
        if (!useGroupSelection) {
            groups.map((item) => {
                if ((item.type !== "Groups") && !(item.id.includes("/sep/"))) {
                    res.push(item)
                }
            })
        } else {
            if (selectedItems === undefined) {
                return []
            }
            if (selectedItems.length === 0) {
                return []
            }
            if ((selectedItems[0].type === 'Groups') || (selectedItems[0].id.includes("/sep/"))) {
                let parentIdList = findAllParentsRecursive(selectedItems.map((item) => item.id));
                res = [...findAllItemsFromParent(parentIdList)]
            } else {
                let selectedIds = selectedItems.map((item) => item.id);
                groups.map((item) => {
                    if (selectedIds.includes(item.id)) {
                        res.push(item)
                    }
                })
            }


        }
        return res;
    }, [selectedItems, groups])
    return researchItems;


    // let groupId = s.groupId;
    // let type = s.type;
    // let itemId = s.itemId;
    // let g = groups.find(g => g.id === groupId);
    // if (!g) g = groups[0];
    // if (type !== '' && type in g && itemId === '') {
    //     return g[type];
    // } else if (g !== undefined && type in g) {
    //     let items = g[type]
    //     let result = []
    //     items.map(i => {
    //         if (i.id === itemId) {
    //             result.push(i)
    //         }
    //     })
    //     return result;
    ;
    // let res = [...g.experiments, ...g.samples];
    //
    //
    // if (categories) res = categories.reduce((acc, cat) => cat.name in g ? acc.concat(g[cat.name]) : acc, res);
    // console.log(res)
    // return res;
    // }


}

export default useActiveResearchItems;