import React from "react";
import {Badge} from "@mui/material";
import {TypeIcon} from "./TypeIcon";
import styles from "./CustomNode.module.css";


export const MultipleDragPreview = (props) => {
    return (
        <Badge
            classes={{badge: styles.badge}}
            color="error"
            badgeContent={props.nodes.length}
            anchorOrigin={{vertical: "top", horizontal: "right"}}
        >
            <div style={{display: "block"}}>
                {props.nodes.map((node) => (
                    <div className={styles.rootDragging}>
                        <div className={styles.icon}>
                            <TypeIcon
                                type={node.type}
                            />
                        </div>
                        <div>{node.name}</div>
                    </div>
                ))}
            </div>
        </Badge>
    );
};
