import {Backdrop, Button} from "@mui/material";
import React, {useEffect, useState} from "react";
import classes from "./SearchFilter.module.css";


const FilterOverlay = ({
                           editFilterId = null,
                           filterApplied = [],
                           setFilterApplied = (val) => null,
                           handleDelete = (val) => null,
                           onClose,
                           showSummary = false,
                           handleEditFilter = (a, b, c) => null,
                           editModeFilter = false,
                           closeEditFilterMode = () => null,
                           updateFilterAppliedNumber = (n) => null,
                           children,
                           setOpenLoadOverlay,
                           dataView = false,
                           ...other
                       }) => {
    const [addFilterModal, setAddFilterModal] = useState(false);


    const addFilterHandler = (data) => {
        const imprintFilterApplied = filterApplied.slice();
        imprintFilterApplied.push(data);
        setFilterApplied(imprintFilterApplied);
        onClose()
    };

    const closeFilterModal = () => {
        setAddFilterModal(false);
    };


    useEffect(() => {

        if (showSummary) {
            setAddFilterModal(false)
        } else {
            setAddFilterModal(true)
        }
        if (editModeFilter) {
            setAddFilterModal(true)
        }

    }, [showSummary, editModeFilter]);


    const deleteAllHandler = () => {
        setFilterApplied([]);
        onClose()
    }

    return (
        <Backdrop open={true} onClick={onClose} sx={{zIndex: (theme) => theme.zIndex.drawer + 1}}>

            <div className={classes.parentWrapper} onClick={(e) => e.stopPropagation()}>
                <div className={classes.headerWrapper}>
                    <div className={classes.mainTitleCss}>
                        Filter by
                    </div>
                    {(!dataView) && <Button disableElevation
                            variant="outlined"
                            onClick={() => {
                                setOpenLoadOverlay(true)
                            }}>
                        Load filter
                    </Button>}

                </div>
                <div className={classes.subHeaderWrapper} style={{minHeight: '10px'}}>
                </div>
                <div className={classes.bodyWrapper}>
                    {children}
                </div>
            </div>

        </Backdrop>

    );
};

export default FilterOverlay;

