import React, {useEffect, useState} from "react";
import Typography from "@mui/material/Typography";
import ArrowRightIcon from "@mui/icons-material/ArrowRight";
import {TypeIcon} from "./TypeIcon";
import styles from "./CustomNodeForTemplate.module.css";


export const CustomNodeForTemplate = (props) => {
    const {droppable, data} = props.node;
    let indent = props.depth * 20;
    let indent_px = `-${indent}px`;

    const handleToggle = (e) => {
        e.stopPropagation();
        props.onToggle(props.node.id);
    };


    const [selected, setSelected] = useState(false);

    useEffect(() => {
        if (props.selected.id == props.node.id) {
            setSelected(true);
        } else {
            setSelected(false);
        }
    }, [props.selected]);


    function selectSelectionStyle(typeString) {
        switch (typeString) {
            case 'Experiments':
                return styles.isSelectedExperiment;
            case'Samples':
                return styles.isSelectedSample;
            case 'Groups':
                return styles.isSelectedGroup;
            default:    // researchitems
                return styles.isSelectedResearchItem;
        }
    }

    const handleSelect = (event) => {
        props.onSelect(props.node);
    }

    const handleSelectForDrop = () => {

    }

    return (
        <>
            {props.node.visible && (
                <div
                    className={`tree-node-template ${styles.root} 
                               ${selected ? selectSelectionStyle(props.node.type) : ""}

                `}
                    style={{marginLeft: indent_px}}
                    onClick={handleSelect}
                    onMouseDown={handleSelectForDrop}
                >
                    <div
                        className={`${styles.expandIconWrapper}
                ${props.isOpen ? styles.isOpen : ""}
            `}
                    >
                        {props.node.expandable && (
                            <div onClick={handleToggle}>
                                <ArrowRightIcon/>
                            </div>
                        )}
                    </div>
                    <div>
                        <TypeIcon type={props.node.type}/>
                    </div>
                    <div className={styles.labelGridItem}>
                        <Typography variant="subtitle2">{props.node.name}</Typography>
                    </div>
                </div>
            )}

        </>

    )
        ;
};
