import {Avatar, Stack} from "@mui/material";
import {useNavigate} from "react-router-dom";

import {format} from "date-fns";


import classes from "./ProjectCard.module.css";
import Typography from "@mui/material/Typography";

export default function ProjectCard({
                                        avatarBgColor,
                                        avatarName,
                                        projectName,
                                        projectId,
                                        projectDescription = "",
                                        creationDate = null,
                                        projectOwner = '',
                                        archived
                                    }) {
    const navigate = useNavigate();

    const redirectToProject = () => {
        const path = "/projects/" + projectId + "/data";
        navigate(path);
    };

    return (
        <div className={classes.cardWrapper} onClick={redirectToProject}>

            <hr className={classes.lineBar}/>
            <Stack direction="row">

                <Avatar
                    // className={classes.avatar}
                    sx={{
                        bgcolor: avatarBgColor,
                        height: "60px",
                        width: "60px",
                        fontFamily: "Roboto",
                        fontWeight: 600,
                        fontSize: "24px",
                        marginTop: "-47px"
                    }}
                >
                    {avatarName}
                </Avatar>
                {(archived) && <Typography variant={"subtitle2"}
                                           style={{marginLeft: "auto", marginTop: "-55px", marginRight: "5px"}}>
                    Archived
                </Typography>}

            </Stack>

            <div className={classes.title}>{projectName}</div>
            <div className={classes.subTitle}>{projectOwner}</div>
            <div className={classes.textCss}>
                {projectDescription}
            </div>
            <div className={classes.dateText}>{format(new Date(creationDate), 'dd. MMMM, yyyy')}</div>

        </div>
    )
        ;
}
