import create from 'zustand';

export const useMultiSelectStore = create((set) => ({
    selected: [], // array of selected items' ids
    addSelected: (ids) => set((state) => ({ selected: [...state.selected, ...ids] })),
    clearAllSelected: () => set({ selected: [] }),
    removeSelected: (id) => set((state) => ({ selected: state.selected.filter((i) => i !== id) })),
    toggleSelected: (id) => set((state) => ({ selected: state.selected.includes(id) ? state.selected.filter((i) => i !== id) : [...state.selected, id] })),
}))

export default useMultiSelectStore;