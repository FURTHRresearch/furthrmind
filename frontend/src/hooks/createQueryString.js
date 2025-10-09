import { set } from "lodash";
import useFilterStore from "../zustand/filterStore";
import { useMemo } from "react";

function createQueryString() {
    const filterList = useFilterStore((state) => state.filterList);
    const searchTerm = useFilterStore((state) => state.nameFilter);
    const includeLinked = useFilterStore((state) => state.includeLinked);
    const displayedCategories = useFilterStore((state) => state.displayedCategories);
    const recent = useFilterStore((state) => state.recent)
    const oldQueryString = useFilterStore((state) => state.oldQueryString)
    const setOldQueryString = useFilterStore((state) => state.setOldQueryString)
    const setGroupMappingUpToDate = useFilterStore((state) => state.setGroupMappingUpToDate)

    let groupFilter = filterList.find(f => f.type === "groups");
    let sampleFilter = filterList.find(f => f.type === "samples");
    let researchItemFilter = filterList.find(f => f.type === "researchitems");
    let experimentFilter = filterList.find(f => f.type === "experiments");


    const queryString = useMemo(() => {

        const qs =  new URLSearchParams({
            comboFieldValues: JSON.stringify(filterList.filter(f => f.type === "combobox").map(f => {
                return {
                    field: f.id,
                    values: f.values
                }
            })),
            groupFilter: groupFilter ? JSON.stringify(groupFilter.values.map(v => v.id)) : '[]',
            sampleFilter: sampleFilter ? JSON.stringify(sampleFilter.values.map(v => v.id)) : '[]',
            researchItemFilter: researchItemFilter ? JSON.stringify(researchItemFilter.values.map(v => v.id)) : '[]',
            experimentFilter: experimentFilter ? JSON.stringify(experimentFilter.values.map(v => v.id)) : '[]',
            numericFilter: JSON.stringify(filterList.filter(f => f.type === "numeric").map(f => {
                return {
                    field: f.id,
                    min: f.values[0].min,
                    max: f.values[0].max,
                    unit: f.values[0].unit
                }
            })),
            dateFilter: JSON.stringify(filterList.filter(f => f.type === "date").map(f => {
                if (f.id === "date_created") {
                    let min = f.values[0].min
                    min = convertToUTC(min)
                    let max = f.values[0].max
                    max = convertToUTC(max)
                    return {
                        field: f.id,
                        min: min,
                        max: max,
                        option: f.values[0].option
                    }
                } else {
                    return {
                        field: f.id,
                        min: f.values[0].min,
                        max: f.values[0].max,
                        option: f.values[0].option
                    }
                }
            })),
            textFilter: JSON.stringify(filterList.filter(f => f.type === "text").map(f => {
                return {
                    field: f.id,
                    value: f.values[0].value
                }
            })),
            checkFilter: JSON.stringify(filterList.filter(f => f.type === "checkbox").map(f => {
                return {
                    field: f.id,
                    value: f.values[0].value
                }
            })),
            nameFilter: searchTerm,
            includeLinked: includeLinked,
            displayedCategories: JSON.stringify(displayedCategories),
            recent: String(recent),
        }).toString()

        if (oldQueryString !== qs) {
            setOldQueryString(qs)
            setGroupMappingUpToDate(false)
        }
        return qs
    }, [filterList, searchTerm, recent, includeLinked, displayedCategories]);

    function convertToUTC(date) {
        const localDate = new Date(date);

        // Get UTC components
        const year = localDate.getUTCFullYear();
        const month = String(localDate.getUTCMonth() + 1).padStart(2, '0'); // Months are zero-based in JavaScript
        const day = String(localDate.getUTCDate()).padStart(2, '0');
        const hours = String(localDate.getUTCHours()).padStart(2, '0');
        const minutes = String(localDate.getUTCMinutes()).padStart(2, '0');

        const dateUTCStr = `${year}-${month}-${day}T${hours}:${minutes}`
        return dateUTCStr
    }

    return queryString
}


export default createQueryString;