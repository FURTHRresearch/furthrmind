
import { Button } from '@mui/material';
import { useEffect, useState } from 'react';

import ArchiveProject from '../../Overlays/ArchiveProject';
import DeleteProject from '../../Overlays/DeleteProject';
import TransferProject from '../../Overlays/TransferProject';
import CloneProject from "../../Overlays/CloneProject";

import classes from './style.module.css';
import { log } from 'console';
export default function Advance({ project}) {
    const [showArchiveModal, setShowArchiveModal] = useState(false);
    const [showDeleteModal, setShowDeleteModal] = useState(false);
    const [showTransferModal, setShowTransferModal] = useState(false);
    const [showCloneModal, setShowCloneModal] = useState(false);
    const [projectName, setProjectName] = useState('');

    const handleArchive = () => {
        setShowArchiveModal(true);
    }

    const handleDelete = () => {
        setShowDeleteModal(true);
    }

    const handleTransfer = () => {
        setShowTransferModal(true);
    }

    const handleClone = () => {
        setShowCloneModal(true);
    }

    useEffect(() => {
        if (project && project.name) {
            setProjectName(project.name);
        }
    }, [project])

    
    return (
        <div>
            {showArchiveModal && <ArchiveProject open={showArchiveModal} setOpen={setShowArchiveModal} project={project} />}
            {showDeleteModal && <DeleteProject open={showDeleteModal} setOpen={setShowDeleteModal} projectName={projectName} />}
            {showTransferModal && <TransferProject open={showTransferModal} setOpen={setShowTransferModal}
                                                   projectName={projectName} />}
            {showCloneModal && <CloneProject open={showCloneModal} setOpen={setShowCloneModal} project={project} />}

            <AdvanceCard
                heading={"Transfer project"}
                actionTitle={"Transfer"}
                handleClick={handleTransfer}
                desc={"Transfer the project to another user."}
                disabled={!project.delete}
            />
            <AdvanceCard
                heading={!project.archived ? "Archive project": "Restore project"}
                actionTitle={!project.archived ? "Archive": "Restore"}
                desc={!project.archived ? `Don't need this project anymore? Archive it.`: "The project is archived, do you want to restore it?"}
                handleClick={handleArchive}
                // buttonColor="#FE294B"
                disabled={!project.delete}
            />
            <AdvanceCard
                heading={"Clone project"}
                actionTitle={"Clone"}
                handleClick={handleClone}
                desc={"Create a new project with all fields and data from this project."}
            />
            <AdvanceCard
                heading={"Delete project"}
                actionTitle="Delete"
                desc={`Do you want to finally delete this project?`}
                handleClick={handleDelete}
                buttonColor="#FE294B"
                disabled={!project.delete}
            />
        </div>
    )
}


const AdvanceCard = ({ heading, actionTitle, desc, handleClick, buttonColor = null , disabled=false}) => {
    return (
        <div className={classes.cardOuterWrap}>
            <div className={classes.cardHeaderWrap}>
                <div className={classes.cardTitle}>
                    {heading}
                </div>
                <div>
                    <Button
                        variant="contained"
                        size="small"
                        disableElevation
                        disabled={disabled}
                        onClick={handleClick}
                        sx={{
                            marginRight: "20px",
                            minWidth: "90px",
                            background: buttonColor,
                            "&:hover": {
                                background: buttonColor
                            }
                        }}
                    >{
                            actionTitle}</Button>
                </div>
            </div>
            <div className={classes.cardContent}>
                {desc}
            </div>
        </div>
    )
}