import {create} from 'zustand';

export const useGroupIndexStore = create((set) => ({
    currentGroup: null,
    selectedItems: [],       // {groupId: x, itemId: y, type: z}
    loading:true,
    refreshInterval: 60000,
    groups: [],
    recentlyCreated: [],
    // only used for groups created from duplicate
    recentlyCreatedGroups: [],
    currentGroupIndex: [],
    setCurrentGroup: (group) => set(() => ({ currentGroup: group})),
    setLoading: (loading) => set(() => ({ loading: loading })),
    setSelection: (items) => set(() => ({ selectedItems: items})),
    resetSelection: () => set(() => ({ selectedItems: [] })),
    setRefreshInterval: (value) => set(() => ({refreshInterval: value})),
    setGroups: (items) => set(() => ({ groups: items})),
    resetRecentlyCreated: () => set(() => ({ recentlyCreated: []})),
    // only used for groups created from duplicate
    resetRecentlyCreatedGroups: () => set(() => ({ recentlyCreatedGroups: []})),
    addRecentlyCreated: (item) => set((state) => ({ recentlyCreated: [item, ...state.recentlyCreated]})),
    // only used for groups created from duplicate
    addRecentlyCreatedGroups: (item) => set((state) => ({ recentlyCreatedGroups: [item, ...state.recentlyCreatedGroups]})),
    setCurrentGroupIndex: (groups) => set(() => ({ currentGroupIndex: groups})),

}))

export default useGroupIndexStore;