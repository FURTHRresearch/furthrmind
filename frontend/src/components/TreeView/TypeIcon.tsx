import React from "react";
import FolderIcon from "@mui/icons-material/Folder";
import BiotechIcon from "@mui/icons-material/Biotech";
import ScienceIcon from "@mui/icons-material/Science";
import CategoryIcon from "@mui/icons-material/Category";

export const TypeIcon = (props) => {
    switch (props.type) {
        case "Groups":
            return <FolderIcon/>;
        case "Experiments":
            return <BiotechIcon/>;
        case "Samples":
            return <ScienceIcon/>;
        default:  // researchitems
            return <CategoryIcon/>;
    }
};
