import useSWR from "swr";
import hash from "stable-hash"
import useGroupIndexStore from "../zustand/groupIndexStore";
import createQueryString from "./createQueryString"
import { useMemo } from "react";
import useFilterStore from "../zustand/filterStore";

const fetcher = (url) => fetch(url).then((res) => res.json());

function useGroupIndex(project) {

    const refreshInterval = useGroupIndexStore((state) => state.refreshInterval);
    const recentlyCreatedGroups = useGroupIndexStore((state) => state.recentlyCreatedGroups);
    const queryString = createQueryString()

    const page = useFilterStore((state) => state.page)
    const pageGroupMapping = useFilterStore((state) => state.pageGroupMapping)
    const groupMappingUpToDate = useFilterStore((state) => state.groupMappingUpToDate)

    const groupIdQuery = useMemo(() => {

        if (!pageGroupMapping) {
            return ""
        }
        let groupIDs = []
        if (pageGroupMapping.hasOwnProperty(page)) {
            groupIDs = pageGroupMapping[page]
        }
        recentlyCreatedGroups.forEach((item) => {
            groupIDs.push(item)
        })
        return new URLSearchParams({
            groupIDs: JSON.stringify(groupIDs),

        }).toString()

    }, [queryString, page, pageGroupMapping, recentlyCreatedGroups]);


    function compareMethod(_old, _new) {
        // avoid rerendering during refresh

        if (_old === undefined) {
            return false
        }
        if (_new === undefined) {
            return true
        }

        const recentlyCreated = useGroupIndexStore.getState().recentlyCreated
        const oldCopy = [..._old]
        const newCopy = [..._new]

        for (let i = oldCopy.length - 1; i >= 0; i--) {
            if (recentlyCreated.includes(oldCopy[i].id)) {
                oldCopy.splice(i, 1)
            }
        }

        for (let i = newCopy.length - 1; i >= 0; i--) {
            if (recentlyCreated.includes(newCopy[i].id)) {
                newCopy.splice(i, 1)
            }
        }

        if (hash(oldCopy) == hash(newCopy)) {
            return true
        } else {
            return false
        }
    }

    function onSuccess(data) {

        const recentlyNode = []
        if (data === undefined) {
            return
        }
        const recentlyCreated = useGroupIndexStore.getState().recentlyCreated
        for (let i = data.length - 1; i >= 0; i--) {
            if (recentlyCreated.includes(data[i].id)) {
                let pos = recentlyCreated.indexOf(data[i].id)
                if (pos > recentlyNode.length - 1) {
                    recentlyNode.push(data[i])
                }
                else {
                    recentlyNode.splice(pos, 0, data[i])
                }
                data.splice(i, 1)
            }

        }
        data.unshift(...recentlyNode)
    }

    const { data: groups, mutate: mutateGroups } =
        useSWR(groupMappingUpToDate ? `/web/projects/${project}/groupindex?${queryString}&${groupIdQuery}` : null, fetcher,
            {
                refreshInterval: refreshInterval, dedupingInterval: 5000,
                compare: (a, b) => compareMethod(a, b),
                onSuccess: (data) => onSuccess(data),
                revalidateIfStale: false,
                revalidateOnFocus: false,
                revalidateOnMount: false,
            });

    return { groups, mutateGroups };


}


export default useGroupIndex;