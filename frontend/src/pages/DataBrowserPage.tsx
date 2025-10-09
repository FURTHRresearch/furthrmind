import Box from "@mui/material/Box";
import Grid from "@mui/material/Grid";
import {useWindowHeight, useWindowWidth} from '@react-hook/window-size';
import {useCallback, useEffect, useState} from "react";
import {useParams} from "react-router-dom";

import CreateButton from "../components/CreateButton";
import NoData from "../components/NoData/NoData";
import ResearchItemOverlay from "../components/Overlays/ResearchItemOverlay";
import ResearchItemList from "../components/ResearchItemList";
import FilterBar from "../components/SearchBar/FilterBar";
import SideDrawer from "../components/SideDrawer";
import TableView from "../components/TableView/tableView";
import TopBar from "../components/TopBar/topBar";
import useActiveResearchItems from "../hooks/useActiveResearchItems";

import useFilterStore from "../zustand/filterStore";
import useGroupIndexStore from "../zustand/groupIndexStore";
import {useMultiSelectStore} from "../zustand/multiSelectStore";
import useSWR from "swr";
import fetcher from "../utils/fetcher";
import axios from "axios";
import BoxWithTreeView from "../components/TreeView/BoxWithTreeView";
import usePageIndex from "../hooks/usePageIndex";
import useGroupIndex from "../hooks/useGroupIndex";


const subHeadingWhenNoDataDueToFilter = 'Hmm.. seems like there is no experiment data found for the particular filter you applied';
const DataBrowserPage = (props) => {
    // @ts-ignore
    const filterList = useFilterStore((state) => state.filterList);

    const height = useWindowHeight();
    const windowWidth = useWindowWidth();
    const [groupName, setGroupName] = useState("");
    const [currentGroup, setCurrentGroup] = useState(null);
    const [activateCompare, setActivateCompare] = useState(false);
    const [researchDataToCompare, setResearchDataToCompare] = useState([]);
    const [viewType, setViewType] = useState("cards");
    const [showGroupProperties, setShowGroupProperties] = useState(false);

    const params = useParams();

    const resetMultiSelect = useMultiSelectStore((state) => state.clearAllSelected);
    const resetFilter = useFilterStore((state) => state.resetFilter);
    const resetGroupIndexSelected = useGroupIndexStore((state) => state.resetSelection);
    const groupIndexSelected = useGroupIndexStore((state) => state.selectedItems);
    const setGroupIndexSelected = useGroupIndexStore((state) => state.setSelection);
    const [init, setInit] = useState(true)
    const [writable, setWritable] = useState(false);
    const [admin, setAdmin] = useState(false);

    const searchTerm = useFilterStore((state) => state.nameFilter);
    const includeLinked = useFilterStore((state) => state.includeLinked);
    const displayedCategories = useFilterStore((state) => state.displayedCategories);
    const recent = useFilterStore((state) => state.recent)
    const resetRecentlyCreated = useGroupIndexStore((state) => state.resetRecentlyCreated);
    const resetRecentlyCreatedGroups = useGroupIndexStore((state) => state.resetRecentlyCreatedGroups);


    useEffect(() => {
        resetFilter();
        resetGroupIndexSelected();
        resetMultiSelect();
        axios.get("/web/permissions/" + project).then((r) => {
            if (r.data === "admin") {
                setWritable(true)
                setAdmin(true)
            } else if (r.data === "write") {
                setWritable(true)
            } else {
                setWritable(false)
            }
        })
    }, [params.project]);


    const handleCompare = () => {
        setActivateCompare(true);
    }

    const multiSelectStore = useMultiSelectStore();
    const project = params.project;

    const {groups, mutateGroups} = useGroupIndex(project);

    const activeResearchItems = useActiveResearchItems(true, groups)


    const maxPageAndPageGroupMapping = usePageIndex(project)
    const setMaxPage = useFilterStore((state) => state.setMaxPage)
    const setPage = useFilterStore((state) => state.setPage)
    const page = useFilterStore((state) => state.page)
    const setPageGroupMapping = useFilterStore((state) => state.setPageGroupMapping)

    useEffect(() => {
        if (maxPageAndPageGroupMapping) {
            setMaxPage(maxPageAndPageGroupMapping.maxPage)
            setPageGroupMapping(maxPageAndPageGroupMapping.pageGroupMapping)
            setPage(1)
        }

    }, [maxPageAndPageGroupMapping]);

    useEffect(() => {
        resetRecentlyCreated()
        resetRecentlyCreatedGroups()
    }, [filterList, searchTerm, recent, includeLinked, displayedCategories, page]);


    useEffect(() => {
        if (groups) {
            let groupFound = false;
            if (currentGroup) {
                groups.map((g) => {
                    if (g.id === currentGroup.id) {
                        groupFound = true;
                        setCurrentGroup(g)
                        setGroupName(g.name)
                        setGroupIndexSelected([{
                            groupId: g["id"],
                            type: g["type"],
                            id: g["id"],
                            name: g["name"],
                            parent: g["parent"]
                        }])
                    }
                })
            }
            if (groupFound === false) {
                if (groups[0]) {
                    setCurrentGroup(groups[0])
                    setGroupName(groups[0].name)
                    setGroupIndexSelected([{
                        groupId: groups[0]["id"],
                        type: groups[0]["type"],
                        id: groups[0]["id"],
                        name: groups[0]["name"],
                        parent: groups[0]["parent"]
                    }])
                }
            }

        }
    }, [groups])


    const {data: categories} = useSWR(`/web/projects/${project}/categories`, fetcher, {dedupingInterval: 2000});


    useEffect(() => {
        if (activateCompare) {
            let category_names = []
            categories.forEach(function (c) {
                category_names.push(c.name)
            })


            const result = [];
            groups.map((item) => {
                if (multiSelectStore.selected.includes(item.id)) {
                    result.push(item)
                }
            })

            setResearchDataToCompare(result);
        }
    }, [activateCompare])

    const calculateDynamicHeight = useCallback((forGroup = false) => {
        let offsetPercent: number;
        if (height < 1000) {
            offsetPercent = 11;
        } else if (height > 1000) {
            offsetPercent = 5;
        }
        const maxDivHeight = (height - ((height * offsetPercent) / 100));

        let result = forGroup && windowWidth < 600 ? height > 600 ? 80 : Math.ceil(maxDivHeight - 40).toFixed(0) : Math.ceil(maxDivHeight - 40).toFixed(0);

        return result;
    }, [height, windowWidth])

    // const calculateWidthForGroupList = useCallback(() => {
    //     // check only when width>600 becuase
    //     // we are adding fixed then only
    //      let width = windowWidth / 12
    //     if (windowWidth > 1200) {
    //         width = width * 2 - 30
    //         return `${width}px`
    //     } else if (windowWidth < 1200 && windowWidth > 992) {
    //         width = width * 2.5 - 30
    //         return `${width}px`
    //     } else if (windowWidth < 992 && windowWidth > 768) {
    //         width = width * 3 - 30
    //         return `${width}px`
    //     } else if (windowWidth < 768 && windowWidth > 576) {
    //         width = width * 6 - 30
    //         return `${width}px`
    //     } else {
    //         width = width * 12
    //         return `${width}px`
    //     }
    //
    // }, [windowWidth])


    const [displayedColumns, setDisplayedColumns] = useState(["Name", "Type"]);
    return (
        <div id="parr">
            <Box
                sx={{display: "flex", backgroundColor: "#f5f5f7", minHeight: "100vh"}}
            >
                <SideDrawer/>
                <Box
                    component="main"
                    sx={{flexGrow: 1, px: 3, height: "100vh", overflowY: "hidden", width: '100%'}}
                >
                    <FilterBar filterList={[]} nameFilter={""} displayedColumns={displayedColumns}
                               setDisplayedColumns={setDisplayedColumns}/>
                    <Grid container spacing={2}>
                        <Grid item xs={12} sm={6} md={3} lg={2.5} xl={2}>
                            <Box style={{position: 'fixed'}}>
                                <CreateButton currentGroup={currentGroup} writable={writable} 
                                admin={admin} groups={groups} mutateGroups={mutateGroups}/>
                            </Box>
                            <BoxWithTreeView setGroupName={setGroupName}
                                             setCurrentGroup={setCurrentGroup}
                                             groups={groups} mutateGroups={mutateGroups}></BoxWithTreeView>

                        </Grid>
                        <Grid item xs={12} sm={6} md={9} lg={9.5} xl={10}>
                            <TopBar
                                name={groupName}
                                handleCompare={handleCompare}
                                onViewTypeChange={setViewType}
                                viewType={viewType}
                                showGroupProperties={showGroupProperties}
                                onShowGroupPropertiesChange={setShowGroupProperties}
                            />

                            {/* subheading will only be present when either data is not
              there or filtered data is not there */}
                            {currentGroup !== null &&
                                <Box style={{maxHeight: 'calc(100vh - 150px)', overflow: 'scroll'}}>
                                    {viewType === "table" && (
                                        <TableView
                                            group={currentGroup}
                                            project={project}
                                            showGroupProperties={showGroupProperties}
                                            showSelector={true}
                                            displayedColumns={displayedColumns}
                                            setDisplayedColumns={setDisplayedColumns}
                                            setCurrentGroup={setCurrentGroup}
                                            items={activeResearchItems}
                                            maxPageAndPageItemMapping={null}
                                            dataViewId={null}
                                            groups={groups}
                                            mutateGroups={mutateGroups}
                                        />
                                    )}
                                    {viewType === "cards" && (
                                        <ResearchItemList
                                            showGroupProperties={showGroupProperties}
                                            currentGroup={currentGroup}
                                            setCurrentGroup={setCurrentGroup}
                                            groups={groups}
                                            mutateGroups={mutateGroups}
                                        />
                                    )}
                                </Box>
                            }
                            {currentGroup === null && filterList.length > 0 && <Box>
                                <NoData
                                    heading='No data found'
                                    subHeading={subHeadingWhenNoDataDueToFilter}
                                    style={{margin: '20px 0px'}}
                                />
                            </Box>
                            }
                        </Grid>
                    </Grid>
                </Box>
            </Box>
            {
                activateCompare && <ResearchItemOverlay
                    data={researchDataToCompare}
                    onExited={() => setActivateCompare(false)}
                    show={activateCompare}
                    onClose={() => setActivateCompare(false)}
                    group={currentGroup}
                    project={project}
                    groups={groups}
                    mutateGroups={mutateGroups}

                />
            }
        </div>
    );
};

export default DataBrowserPage;

