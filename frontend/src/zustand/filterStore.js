import create from 'zustand';

export const useFilterStore = create((set) => ({
    filterList: [],
    nameFilter: '',
    includeLinked: "none",
    displayedCategories: ['all'],
    recent: false,
    page: 1,
    maxPage: 1,
    pageGroupMapping: {},
    avoidRefresh: false,
    groupMappingUpToDate: true,
    oldQueryString: '',
    setNameFilter: (name) => {
        set(() => ({ nameFilter: name, page: 1 }))
        // set(() => ({ groupMappingUpToDate: false }))
    },
    resetFilter: () => {
        set(() => ({
            filterList: [],
            nameFilter: '',
            includeLinked: "none",
            displayedCategories: ["all"],
            page: 1
        }))
        // set(() => ({ groupMappingUpToDate: false }))
    },
    deleteFilter: (id) => {
        set((state) => ({
            filterList: state.filterList.filter(item => item.id !== id),
            page: 1
        }))
        // set(() => ({ groupMappingUpToDate: false }))
    },
    saveFilter: (filter) => {
        set((state) => ({
            filterList:
                state.filterList.find(item => item.id === filter.id) ? state.filterList.map(item => item.id === filter.id ? filter : item) : [...state.filterList, filter],
            page: 1
        }))
        // set(() => ({ groupMappingUpToDate: false }))
    },
    setIncludeLinked: (include) => {
        set(() => ({ includeLinked: include }))
        // set(() => ({ groupMappingUpToDate: false }))
    },
    setDisplayedCategories: (displayedCategoriesNew) => {
        set(() => ({ displayedCategories: displayedCategoriesNew }))
        // set(() => ({ groupMappingUpToDate: false }))

    },
    setRecent: (recent) => {
        set(() => ({ pageGroupMapping: {}, recent: recent }))
        // set(() => ({ groupMappingUpToDate: false }))
    },
    setPage: (page) => set(() => ({ page: page })),
    setMaxPage: (maxPage) => set(() => ({ maxPage: maxPage })),
    setPageGroupMapping: (pageGroupMapping) => set(() => ({ pageGroupMapping: pageGroupMapping })),
    setGroupMappingUpToDate: (groupMappingUpToDate) => set(() => ({ groupMappingUpToDate: groupMappingUpToDate })),
    setOldQueryString: (oldQueryString) => set(() => ({ oldQueryString: oldQueryString })),
}))

export default useFilterStore;