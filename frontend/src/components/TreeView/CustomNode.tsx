import React, {useEffect, useState} from "react";
import Typography from "@mui/material/Typography";
import ArrowRightIcon from "@mui/icons-material/ArrowRight";
import {TypeIcon} from "./TypeIcon";
import styles from "./CustomNode.module.css";
import useGroupIndexStore from '../../zustand/groupIndexStore';


export const CustomNode = (props) => {
    const {droppable, data} = props.node;
    let indent = props.depth * 20;
    let indent_px = `-${indent}px`;

    const handleToggle = (e) => {
        e.stopPropagation();
        props.onToggle(props.node.id);
    };

    const [selected, setSelected] = useState(false)
    const selectedItems = useGroupIndexStore((state) => state.selectedItems);


    useEffect(() => {
        function checkSelection() {
            let checked = false;
            selectedItems.map((s) => {
                    if (s.id == props.node.id) {
                        checked = true;
                    }
                }
            )
            return checked
        }

        setSelected(checkSelection());
    }, [selectedItems]);


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
        props.onSelect(event, props.node);
    }

    const handleSelectForDrop = () => {
        props.onSelectForDrag(event, props.node);
    }

    return (
        <>
            {props.node.visible && (
                <div
                    className={`tree-node ${styles.root} 
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
