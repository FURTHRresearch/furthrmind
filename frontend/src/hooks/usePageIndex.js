import useSWR from "swr";
import hash from "stable-hash"
import useFilterStore from "../zustand/filterStore";
import useGroupIndexStore from "../zustand/groupIndexStore";
import createQueryString from "./createQueryString"

const fetcher = (url) => fetch(url).then((res) => res.json());


function usePageIndex(project) {

    const refreshInterval = useGroupIndexStore((state) => state.refreshInterval);
    const setGroupMappingUpToDate = useFilterStore((state) => state.setGroupMappingUpToDate);
    const groupMappingUpToDate = useFilterStore((state) => state.groupMappingUpToDate);
    
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
        if (!groupMappingUpToDate) {
            setGroupMappingUpToDate(true)
        }
        
    }


    const {data: pageGroupMapping, mutate: mutatePageGroupMapping} =
        useSWR( `/web/projects/${project}/page-group-mapping?${createQueryString()}`, fetcher,
            {
                refreshInterval: refreshInterval,
                dedupingInterval: 2000,
                compare: (a, b) => compareMethod(a, b),
                onSuccess: (data) => onSuccess(data)
            });

    return pageGroupMapping

}


export default usePageIndex;