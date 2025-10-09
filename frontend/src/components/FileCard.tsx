import Stack from "@mui/material/Stack";
import Tooltip from '@mui/material/Tooltip';
import { defaultStyles, FileIcon } from "react-file-icon";
import classes from "./FileCard.module.css";

import IconButton from "@mui/material/IconButton";
import MoreVertIcon from "@mui/icons-material/MoreVert";

import React from "react";
import Menu from "@mui/material/Menu";
import MenuItem from "@mui/material/MenuItem";
import FormGroup from "@mui/material/FormGroup";
import FormControlLabel from "@mui/material/FormControlLabel";
import Switch from "@mui/material/Switch";
import DeleteIcon from "@mui/icons-material/Delete";
import ContentCopyIcon from "@mui/icons-material/ContentCopy";
import SaveIcon from "@mui/icons-material/Save";
import Typography from "@mui/material/Typography";
import axios from "axios";
import OpenInNewIcon from "@mui/icons-material/OpenInNew";
import DeleteForeverIcon from "@mui/icons-material/DeleteForever";
import FileDownloadIcon from '@mui/icons-material/FileDownload';
import FileOpenIcon from '@mui/icons-material/FileOpen';
import FormControl from "@mui/material/FormControl";
import FormLabel from "@mui/material/FormLabel";
import RadioGroup from "@mui/material/RadioGroup";
import Radio from "@mui/material/Radio";
import {TextField} from "@mui/material";
import Dialog from "@mui/material/Dialog";
import DialogTitle from "@mui/material/DialogTitle";
import DialogContent from "@mui/material/DialogContent";
import DialogContentText from "@mui/material/DialogContentText";
import DialogActions from "@mui/material/DialogActions";
import Button from "@mui/material/Button";
import LoadingButton from "@mui/lab/LoadingButton";
import {useParams} from "react-router-dom";
import useSWR from "swr";
import LightBox from "./Overlays/LightBox";

const obj = {
    psd: (
        <div style={{ width: '48px' }}>
            <FileIcon
                size={48}
                color="#34364E"
                gradientOpacity={0}
                labelColor="#34364E"
                labelTextColor="#31C5F0"
                labelUppercase
                foldColor="#31C5F0"
                radius={2}
                extension="psd"
            />
        </div>
    ),
    ai: (
        <div style={{ width: '48px' }}>
            <FileIcon
                size={48}
                color="#423325"
                gradientOpacity={0}
                labelColor="#423325"
                labelTextColor="#FF7F18"
                labelUppercase
                foldColor="#FF7F18"
                radius={2}
                extension="ai"
            />
        </div>
    ),
    indd: (
        <div style={{ width: '48px' }}>
            <FileIcon
                size={48}
                color="#4B2B36"
                gradientOpacity={0}
                labelColor="#4B2B36"
                labelTextColor="#FF408C"
                labelUppercase
                foldColor="#FF408C"
                radius={2}
                extension="indd"
            />
        </div>
    ),
    doc: (
        <div style={{ width: '48px' }}>
            <FileIcon
                size={48}
                color="#2C5898"
                labelColor="#2C5898"
                labelUppercase
                type="document"
                glyphColor="rgba(255,255,255,0.4)"
                extension="doc"
            />
        </div>
    ),
    txt: (
        <div style={{ width: '48px' }}>
            <FileIcon
                size={48}
                color="#2C5898"
                labelColor="#2C5898"
                labelUppercase
                type="document"
                glyphColor="rgba(255,255,255,0.4)"
                extension="doc"
            />
        </div>
    ),
    xls: (
        <div style={{ width: '48px' }}>
            <FileIcon
                size={48}
                color="#1A754C"
                labelColor="#1A754C"
                labelUppercase
                type="spreadsheet"
                glyphColor="rgba(255,255,255,0.4)"
                extension="xls"
            />
        </div>
    ),
    ppt: <div style={{ width: '48px' }}>
        <FileIcon
            size={48}
            color="#D14423"
            labelColor="#D14423"
            labelUppercase
            type="presentation"
            glyphColor="rgba(255,255,255,0.4)"
            extension="ppt"
        />
    </div>
    ,
    png:
        <div style={{ width: '48px' }}>
            <FileIcon
                size={48}
                color="#D14423"
                labelColor="#D14423"
                labelUppercase
                type="presentation"
                glyphColor="rgba(255,255,255,0.4)"
                extension="png" />
        </div>,

    jpg:
        <div style={{ width: '48px' }}>
            <FileIcon
                size={48}
                color="#D14423"
                labelColor="#D14423"
                labelUppercase
                type="presentation"
                glyphColor="rgba(255,255,255,0.4)"
                extension="jpg"
            />
        </div>,

    pdf: (
        <div style={{ width: '48px' }}>
            <FileIcon
                size={48}
                color="#D14423"
                labelColor="#D14423"
                labelUppercase
                type="acrobat"
                glyphColor="rgba(255,255,255,0.4)"
                extension="pdf"
            />
        </div>
    ),
};


export default function FileCard({
    fileExtension,
    fileName,
    file,
    onDeleted = (id) => null,
    data,
    type,
    i,
    sortedFiles,
})


{
    const FileItemMenu = ({props}) => {
        const [anchorEl, setAnchorEl] = React.useState<null | HTMLElement>(null);
        const open = Boolean(anchorEl);
        const handleClick = (event: React.MouseEvent<HTMLElement>) => {
            setAnchorEl(event.currentTarget);
        };
        const [showDeleteDialog, setShowDeleteDialog] = React.useState(false);
        const handleClose = () => {
            setAnchorEl(null);
            setShowDialog(false);
        };
        const [showDialog, setShowDialog] = React.useState(false);
        const supportedFiles = ['.pdf', '.png', '.jpg', '.jpeg', '.mp4', '.txt','.xls', '.xlsx', '.xlsm', 
            '.doc', '.docx', '.ppt', '.pptx']

        const downloadFile = () => {
            function download() {
                const a = document.createElement('a')
                const url = "/web/files/" + file["id"] + "?download=true"
                a.href = url
                a.download = url.split('/').pop()
                document.body.appendChild(a)
                a.click()
                document.body.removeChild(a)
            }
            download()
            setShowDialog(false);
            setAnchorEl(null);
        }

        const openFile = () => {
            function viewFile() {
                const a = document.createElement('a')
                const url = "/web/files/" + file["id"] + "?view=true";
                a.href = url
                document.body.appendChild(a)
                a.setAttribute('target', '_blank');
                a.click()
                document.body.removeChild(a)
            }
            function openInOnlyOffice() {
                const a = document.createElement('a')
                const url = "/web/onlyoffice/files/" + file["id"];
                a.href = url
                document.body.appendChild(a)
                a.setAttribute('target', '_blank');
                a.click()
                document.body.removeChild(a)
            }

            const open = ["doc", "docm", "docx", "docxf", "csv",  "xls", "xlsb", "xlsm", "xlsx", "xlt", "xltm", "xltx",
                 "pps", "ppsm", "ppsx", "ppt", "pptm", "pptx" ];

            if (open.includes(fileExtension)){
                openInOnlyOffice()
            } else {
                viewFile()
            }
            setShowDialog(false);
            setAnchorEl(null);
        }
        return (
                        <>
                <IconButton
                    onClick={handleClick}
                    size='small'
                >
                    <MoreVertIcon />
                </IconButton>
                <Menu
                    anchorEl={anchorEl}
                    open={open}
                    onClose={handleClose}
                >

                    {supportedFiles.includes('.' + fileName.split('.').pop()) && <MenuItem onClick={openFile}>
                        <Stack direction="row" spacing={2}>
                            <FileOpenIcon />
                            <Typography>Open</Typography>
                        </Stack>
                    </MenuItem>}

                    {!supportedFiles.includes('.' + fileName.split('.').pop()) && <MenuItem>
                        <Stack direction="row" spacing={2}>
                            <FileOpenIcon color ="disabled" />
                            <Typography>Open</Typography>
                        </Stack>
                    </MenuItem>}

                    <MenuItem onClick={downloadFile}>
                        <Stack direction="row" spacing={2}>
                            <FileDownloadIcon />
                            <Typography>Download</Typography>
                        </Stack>
                    </MenuItem>


                    <MenuItem onClick={() => { setShowDeleteDialog(true); handleClose() }} disabled={(!data.writable || data.Protected)}>
                        <Stack direction="row" spacing={2}>
                            <DeleteForeverIcon sx={{
                                color: '#E0144C'
                            }
                            } />
                            <Typography sx={{
                                color: '#E0144C'
                            }}>Delete</Typography>
                        </Stack>
                    </MenuItem>

                </Menu>

                <DeleteFileDialog {...props} open={showDeleteDialog} handleClose={() => setShowDeleteDialog(false)}  onDeleted = {onDeleted}/>

            </>
        )
    }

    const DeleteFileDialog = ({ open, handleClose, name, id, onDeleted, props, }) => {
        const [loading, setLoading] = React.useState(false);
        const params = useParams();
        const deleteItem = () => {
            setLoading(true);


            axios.delete(`/web/item/${type}/${data.id}/files/${file["id"]}`).then(() => {
                onDeleted(id);
                handleClose();
            });
        }
        return (
            <Dialog open={open} onClose={handleClose}>
                <DialogTitle>Delete {fileName} ?</DialogTitle>
                <DialogContent>

                    <DialogContentText></DialogContentText>

                </DialogContent>
                <DialogActions>
                    <Button onClick={handleClose} disabled={loading}>Cancel</Button>
                    <LoadingButton loading={loading} onClick={deleteItem} color="warning" >Delete</LoadingButton>
                </DialogActions>
            </Dialog>
        )
    }
    const [showLightBox, setShowLightBox] = React.useState(false);
    const [lightBoxIndex, setLightBoxIndex] = React.useState(0);


    // @ts-ignore
    if (file.Thumbnail)
        return (
            <div
                className={classes.cardWrapper}
            >
                <Stack direction="row" mt={1} spacing={2} alignItems="left">
                    <Tooltip title={fileName} placement='top'>
                        <div style={{ width: "42px" }}>


                            <img
                                width="65px"
                                className="graph"
                                style={{cursor: "pointer"}}
                                key={file.Thumbnail}
                                src={"/web/files/" + file.Thumbnail}
                                loading="lazy"
                                alt=""
                                onClick={() => {
                                    setShowLightBox(true);
                                    setLightBoxIndex(i);
                                }}
                            />

                                <div style={{fontSize: "12px"}}>{fileName.slice(0, 10)}... </div>

                            </div>

                    </Tooltip>
                    {showLightBox &&
                        <LightBox
                            show={true}
                            initialIndex={lightBoxIndex}
                            onClose={() => setShowLightBox(false)}
                            images={sortedFiles.filter(f => Boolean(f.Thumbnail))}
                        />
                    }


                    <div className={classes.cardContent} >
                        <FileItemMenu />

                    </div>

                </Stack>


            </div>)
    else return (
        <div
            className={classes.cardWrapper}
        >
            <Stack direction="row" mt={1} spacing={2} alignItems="left">
                <Tooltip title={fileName} placement='top'>
                    <div style={{ width: "42px" }}>
                        {obj[fileExtension] ? (
                            obj[fileExtension]
                        ) : (
                            <div style={{ width: "42px" }}>
                                <FileIcon
                                    extension={fileExtension}
                                    {...defaultStyles[fileExtension]}
                                />
                            </div>

                        )}
                        <div style={{fontSize: "12px"}}>{fileName.slice(0, 10)}... </div>

                    </div>

                </Tooltip>


                <div className={classes.cardContent}>
                    <FileItemMenu />

                </div>

            </Stack>


        </div>

    );

}


