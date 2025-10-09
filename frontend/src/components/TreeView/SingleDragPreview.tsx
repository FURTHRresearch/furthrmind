import React from "react";
import {TypeIcon} from "./TypeIcon";
import styles from "./CustomNode.module.css";


export const SingleDragPreview = (props) => {
    const node = props.node;
    if (node === undefined) {
        return null;
    }
    return (
        <div style={{display: "block"}}>
            <div className={styles.rootDragging}>
                <div className={styles.icon}>
                    <TypeIcon
                        type={node.type}
                    />
                </div>
                <div>{node.name}</div>
            </div>
        </div>
    );
};
