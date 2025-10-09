import DeleteIcon from "@mui/icons-material/Delete";
import Button from "@mui/material/Button";
import useFilterStore from "../../zustand/filterStore";
import FilterCard from "./FilterCard";
import FilterOverlay from "./FilterOverlay";
import classes from "./SearchFilter.module.css";
import dataViewForTable from "../../pages/DataViewForTable";

export default function FilterSummary({ open, onClose, setOpenLoadOverlay, dataView=false}) {
    const filterList = useFilterStore(
        // @ts-ignore
        (state) => state.filterList
    );
    return (
        open && <FilterOverlay onClose={onClose} open={open} setOpenLoadOverlay={setOpenLoadOverlay}>
            <div className={classes.cardParentWrapper}>
                {filterList.map((opt) => {
                    return (
                        <FilterCard
                            key={opt.id}
                            keyName={opt.field}
                            value={opt.values}
                            id={opt.id}
                            setOpenLoadOverlay={setOpenLoadOverlay}
                            dataView={dataView}
                        />
                    );
                })}
            </div>
        </FilterOverlay>
    )
}