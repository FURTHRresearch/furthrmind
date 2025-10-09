import useSWR from "swr";
import hash from "stable-hash"
import useFilterStore from "../zustand/filterStore";
import useGroupIndexStore from "../zustand/groupIndexStore";
import createQueryString from "./createQueryString"
import {useEffect} from "react";

const fetcher = (url) => fetch(url).then((res) => res.json());


function usePageIndexDashboard(dataViewID) {

    const refreshInterval = useGroupIndexStore((state) => state.refreshInterval);
    const setGroupMappingUpToDate = useFilterStore((state) => state.setGroupMappingUpToDate);
    
    const queryString = createQueryString()

    function compareMethod(_old, _new) {
        // avoid rerendering during refresh
        if (_old === undefined) {
            return false
        }
        if (refreshInterval === 0) {
            return true
        }
        if (_new == undefined) {
            return true
        }

        if (hash(_old) === hash(_new)) {
            return true
        } else {
            return false
        }

    }

    function onSuccess(data) {
        setGroupMappingUpToDate(true)
    }

    const {data: pageGroupMappingDashboard, mutate: mutatePageGroupMapping} =
        useSWR(dataViewID ?  `/web/dataviews/${dataViewID}/page-item-index?${queryString}`: null, fetcher,
            {
                refreshInterval: 60000,
                dedupingInterval: 5000,
                compare: (a, b) => compareMethod(a, b),
                onSuccess: (data) => onSuccess(data)
            });

    return pageGroupMappingDashboard

}


export default usePageIndexDashboard;