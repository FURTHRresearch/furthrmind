import Tabs from "@mui/material/Tabs";
import Tab from "@mui/material/Tab";
import GroupList from "./GroupList";
import {useParams} from "react-router-dom";
import {useState} from "react";
import {Pagination} from "@mui/material";
import useFilterStore from "../../zustand/filterStore";

export default function BoxWithTreeView({setGroupName, setCurrentGroup, groups, mutateGroups}) {
    const params = useParams()
    const [selectedTab, setSelectedTab] = useState("all");
    const [loadingGroups, setLoadingGroups] = useState(true);
    const [siblingCount, setSiblingCount] = useState(0);
    const [boundaryCount, setBoundaryCount] = useState(1);
    const setRecent = useFilterStore((state) => state.setRecent);
    const setPage = useFilterStore((state) => state.setPage)
    const page = useFilterStore((state) => state.page)
    const maxPage = useFilterStore((state) => state.maxPage)

    function handleTabChange(e, newValue) {
        setSelectedTab(newValue);
        if (newValue === "recent") {
            setRecent(true);
        } else {
            setRecent(false);
        }

    }

    function handlePageChange(e, newValue) {
        setPage(newValue)
        if (newValue === 1) {
            setSiblingCount(0)
            setBoundaryCount(1)
        } else if (newValue === maxPage) {
            setSiblingCount(0)
            setBoundaryCount(1)
        } else {
            setSiblingCount(1)
            setBoundaryCount(1)
        }
    }

    return (

        <div style={{
            // height: `${calculateDynamicHeight(true)}px`,
            // position: windowWidth > 600 ? 'fixed' : 'static',
            // overflowY: 'auto',
            marginTop: '40px',
            marginRight: "10px",
            display: "flex",
            flexDirection: "column",

            // width: windowWidth > 600 ? calculateWidthForGroupList() : 'inherit'
        }}>
            <div style={{marginLeft: "auto", marginRight: "auto", marginTop: "15px", flexShrink: 0}}>
                <Tabs value={selectedTab} onChange={handleTabChange} aria-label="group list tab"
                >
                    <Tab label="All groups" value="all" style={{marginLeft: "auto"}}/>
                    <Tab label="Recent groups" value="recent" style={{marginRight: "auto"}}/>
                </Tabs>
            </div>

            <div style={{
                height: 'calc(100vh - 250px)',
                overflowY: 'auto',
                // minHeight: `${calculateDynamicHeight(true) - 100}px`
            }}>
                <GroupList
                    project={params.project}
                    // onSelectionChange={handleSelectionChange}
                    loadingGroups={loadingGroups}
                    setLoadingGroups={setLoadingGroups}
                    setGroupName={setGroupName}
                    setCurrentGroup={setCurrentGroup}
                    selectedTab={selectedTab}
                    groups={groups}
                    mutateGroups={mutateGroups}
                    // width={calculateWidthForGroupListItem()}
                />
            </div>
            <div style={{marginTop: "20px", flexShrink: 0}}>
                {(maxPage > 1) && <Pagination page={page}
                                               count={maxPage} size={"small"} onChange={handlePageChange}
                                               siblingCount={siblingCount} boundaryCount={boundaryCount}
                                               showFirstButton={false}
                                               showLastButton={false}
                                               style={{marginRight: "auto", marginLeft: "auto", width: "120%"}}
                />
                }

            </div>

        </div>

    )
}