import CancelIcon from '@mui/icons-material/Cancel';
import Chip from '@mui/material/Chip';
import { useState } from 'react';
import classes from './FilterCardStyle.module.css';
import FilterEditor from './FilterEditor';

import useFilterStore from '../../zustand/filterStore';

const FilterCard = ({ keyName, value, id, setOpenLoadOverlay, dataView=false}) => {
    const [showCancel, setShowCancel] = useState(false);
    const [showEditor, setShowEditor] = useState(false);


    const deleteFilter = useFilterStore((state) => state.deleteFilter);

    const handleMouseDown = () => {
        setShowCancel(true)
    }

    const handleMouseOut = () => {
        setShowCancel(false);
    }

    const deleteHandler = (e) => {
        e.stopPropagation()
        deleteFilter(id)
    }
    return (
        <>
            <div className={classes.cardWrapper} onMouseEnter={handleMouseDown} onMouseLeave={handleMouseOut} onClick={() => setShowEditor(true)}>
                <div className={classes.keyCss}>
                    {keyName}:
                </div>
                <div className={classes.valueCss}>
                    <div className={classes.comboBoxWrapper}>
                        {value && value.map((v) => <Chip label={v.Name ? v.Name : v.name} />)}
                    </div>
                </div>
                <div className={classes.iconCss} style={{ visibility: showCancel ? "visible" : "hidden" }} onClick={(e) => deleteHandler(e)}>
                    <CancelIcon sx={{ color: "#F29E96" }} />
                </div>
            </div>
            <FilterEditor onClose={() => setShowEditor(false)} open={showEditor}
                          editFilterId={id} setOpenLoadOverlay={setOpenLoadOverlay} dataView={dataView}/>
        </>
    )
}

export default FilterCard;