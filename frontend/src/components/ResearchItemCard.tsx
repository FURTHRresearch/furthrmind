import React, { useCallback, useEffect, useState } from "react";

import ContentCopyIcon from '@mui/icons-material/ContentCopy';
import ContentPasteIcon from '@mui/icons-material/ContentPaste';
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import Typography from "@mui/material/Typography";
import { CopyToClipboard } from 'react-copy-to-clipboard';
import FileCard from "./FileCard";

import OpenInNewIcon from '@mui/icons-material/OpenInNew';
import TableViewIcon from "@mui/icons-material/TableView";
import Stack from "@mui/material/Stack";

import DeleteIcon from '@mui/icons-material/Delete';
import LoadingButton from '@mui/lab/LoadingButton';
import Button from "@mui/material/Button";
import Checkbox from "@mui/material/Checkbox";
import Dialog from '@mui/material/Dialog';
import DialogActions from '@mui/material/DialogActions';
import DialogContent from '@mui/material/DialogContent';
import DialogContentText from '@mui/material/DialogContentText';
import DialogTitle from '@mui/material/DialogTitle';
import FormControlLabel from '@mui/material/FormControlLabel';
import FormGroup from '@mui/material/FormGroup';
import IconButton from "@mui/material/IconButton";
import Skeleton from "@mui/material/Skeleton";
import { styled } from '@mui/material/styles';
import Switch from "@mui/material/Switch";
import debounce from "lodash/debounce";
import { useParams } from "react-router-dom";
import AddField from "./Fields/AddField";
import RawDataOverlay from "./Overlays/RawDataOverlay";
import ImportDataOverlay from "./Overlays/ImportDataOverlay";

import ContentEditable from "react-contenteditable";
import ResearchItemOverlay from "./Overlays/ResearchItemOverlay";

import FileUploadButton from "./UploadButton/FileUploadButton";

import { useInView } from "react-intersection-observer";
import useSWR from "swr";
import DraggableFields from "./DraggableFields/draggableFields";

import MoreVertIcon from '@mui/icons-material/MoreVert';
import Menu from '@mui/material/Menu';
import MenuItem from '@mui/material/MenuItem';

import { Alert, Grid, InputLabel, Select, Snackbar, TextField, Tooltip } from "@mui/material";
import axios from "axios";
import { default as ItemSelector } from "./ItemSelector";

import { useMultiSelectStore } from "../zustand/multiSelectStore";
import SaveIcon from "@mui/icons-material/Save";
import DeleteForeverIcon from "@mui/icons-material/DeleteForever";
import FormControl from "@mui/material/FormControl";
import FormLabel from "@mui/material/FormLabel";
import RadioGroup from "@mui/material/RadioGroup";
import Radio from "@mui/material/Radio";
import Divider from "@mui/material/Divider";
import useGroupIndexStore from "../zustand/groupIndexStore";



const ListItem = styled('li')(({ theme }) => ({
    margin: theme.spacing(0.5),
}));

const fetcher = (url) => fetch(url).then((res) => res.json());

const ResearchItemCard = ({
    expanded = false,
    group, type, project, itemId,groups,
    mutateGroups,
    startInView = false,
    withCheckbox = false,
    
}) => {
    const [showRawData, setShowRawData] = React.useState(false);
    const [renderRawData, setRenderRawData] = React.useState(false);
    const [renderItemOverlay, setRenderItemOverlay] = React.useState(false);
    const [showItemOverlay, setShowItemOverlay] = React.useState(false);
    const [openImportToolDialog, setOpenImportToolDialog] = React.useState(false)
    const [openImportTool, setOpenImportTool] = React.useState(false)
    const [importFileList, setImportFileList] = React.useState([])
    const [_protected, setProtected] = React.useState(false)
    const [openDuplicateOverlay, setOpenDuplicateOverlay] = React.useState(false);
    const [rawDataGridSize, setRawDataGridSize] = React.useState(12)

    const { ref: inViewRef, inView } = useInView({
        rootMargin: "1000px",
        initialInView: startInView,
    });

    const rawDataImportTextFileExt = ["csv", "txt", "text", "dat", "asc", "info"]
    const rawDataImportExcelFileExt = ["xlsx", "xls"]

    const params = useParams();

    const multiSelectStore = useMultiSelectStore();

    const [wasInView, setWasInView] = React.useState(false);

    useEffect(() => {
        if (inView) setWasInView(true);
    }, [inView]);

    const { data, mutate } = useSWR(
        wasInView || inView ? `/web/item/${type}/${itemId}` : null,
        fetcher
    );

    useEffect(() => {
        if (data) {
            setProtected(data.Protected)
            if (data.rawdata) {
                if (data.rawdata.length === 1) {
                    setRawDataGridSize(12)
                } else if (data.rawdata.length === 2) {
                    setRawDataGridSize(6)
                } else {
                    setRawDataGridSize(4)
                }
            }
        }

    }, [data]);


    const writable = data ? data.writable : false;
    const admin = data ? data.admin : false;
    const files = data?.files;
    const linked_items = data?.linked_items;
    // const setSamples = (samples) => {
    //   mutate({ ...data, samples }, false);
    // };
    const fields = data?.fields;

    const fieldAdded = (field) => {
        mutate({ ...data, fields: [...fields, field] }, false);
    };
    const saveData = useCallback(
        (reqdata) => {
            fetch(`/web/item/${type}/` + data.id, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(reqdata),
            }).then((r) => {
                const groupsCopy = []
                groups.map((g) => {
                    if (g.id === data.id) {
                        g.name = reqdata.name
                    }
                    groupsCopy.push(g)
                })
                mutateGroups(groupsCopy, { revalidate: false })
            }
            );
        },
        [data?.id, type]
    );
    // eslint-disable-next-line
    const debouncedSave = useCallback(debounce(saveData, 1000), [saveData]);

    const protectedChanged = (e) => {
        mutate({ ...data, Protected: e.target.checked }, false);
        setProtected(e.target.checked)
        saveData({
            protected: e.target.checked,
        });
    };
    const nameChanged = (e) => {
        let doc = new DOMParser().parseFromString(e.target.innerText, 'text/html');
        let name = doc.body.textContent || "";
        mutate({ ...data, Name: name }, false);
        debouncedSave({ name });
    };
    const filesUploaded = (uuids) => {
        axios.post(`/web/${data.id}/files`, { uuids }).then((res) => {
            mutate({ ...data, files: [...files, ...res.data] });
            let rawDataImportTextFileList = []
            res.data.map((d) => {
                if (rawDataImportTextFileExt.includes(d.Name.split(".").pop())) {
                    rawDataImportTextFileList.push(d)
                }
            })
            if (rawDataImportTextFileList.length > 0) {
                setImportFileList(rawDataImportTextFileList)
                setOpenImportToolDialog(true)
            }
        });
    };

    const updateFieldOnDragEnd = (result, fields) => {
        const {
            destination: { index: destinationIndex },
            source: { index: sourceIndex },
        } = result;

        if (destinationIndex !== sourceIndex) {
            const newFields = fields.slice();
            newFields.splice(destinationIndex, 0, newFields.splice(sourceIndex, 1)[0]);
            mutate({ ...data, fields: newFields }, false);
            axios.put(`/web/item/${type}/${data.id}/fields`, { 'fieldDataIds': newFields.map(f => f.id) });
        }
    };

    const handleFieldValueChange = (id, val) => {
        const newFields = fields.map(f => {
            return (f.id === id) ? { ...f, Value: val } : f;
        })
        mutate({ ...data, fields: newFields }, false);

    }

    const handleFieldUnitChange = (id, val) => {
        const newFields = fields.map(f => {
            return (f.id === id) ? { ...f, UnitID: val } : f;
        })
        mutate({ ...data, fields: newFields }, false);
    }

    const sortedFiles = files ? files.sort((a, b) => (Boolean(a.Thumbnail) === Boolean(b.Thumbnail)) ? 0 : a.Thumbnail ? -1 : 1) : [];

    return (
        <div className="research-card">
            <Card
                ref={inViewRef}
                variant="outlined"
                style={{
                    borderColor: type === "experiments" ? "#3c8039" : (type === "samples" ? "#e3742f" : 'gray'),
                    opacity: data?.protected ? 0.5 : 1,
                    boxShadow: "2px 4px 4px rgba(0, 0, 0, 0.25)",
                }}
            >
                <CardContent>
                    {data ? <div style={{
                        display: "flex",
                        justifyContent: "space-between",
                        alignItems: "center",
                        marginTop: '-10px'
                    }}>
                        {withCheckbox && <div style={{ maxWidth: "30px" }}>
                            <Checkbox disableRipple={false} style={{ marginLeft: "-10px" }}
                                // @ts-ignore
                                checked={multiSelectStore.selected.includes(itemId)}
                                // @ts-ignore
                                onChange={(e) => multiSelectStore.toggleSelected(itemId)}
                            />
                        </div>}
                        <div style={{ maxWidth: "250px" }}>
                            {data && <Typography sx={{ textAlign: 'center' }} color="text.secondary">
                                {data.typeName}
                            </Typography>
                            }
                        </div>
                        <div style={{ marginRight: '-10px' }}>
                            <ResearchItemMenu
                                name={data ? data.Name : ''}
                                id={itemId}
                                group={group}
                                type={type}
                                shortId={data.shortId}
                                protected={_protected}
                                protectedChanged={protectedChanged}
                                writable={writable}
                                groups={groups}
                                mutateGroups={mutateGroups}
                                openDuplicateOverlay={openDuplicateOverlay}
                                setOpenDuplicateOverlay={setOpenDuplicateOverlay}
                                datatables={data.rawdata}
                            />
                        </div>
                    </div> : <Skeleton style={{ width: "100%" }} />}
                    <Typography variant="subtitle2" component="div">
                        {data ? (
                            (writable && !_protected) ? <ContentEditable
                                html={data.Name}
                                onChange={undefined}
                                onBlur={(e) => nameChanged(e)}
                                onKeyDown={(e) => {
                                    if (e.key === "Enter") e.preventDefault();
                                }}
                                tagName="div"
                                style={{ width: '100%' }}
                            /> : <div style={{ wordWrap: 'break-word' }}>{data.Name}</div>
                        ) : inView && <Skeleton variant="text" style={{ width: "80%" }} />}
                    </Typography>
                    {!data ? (
                        inView ? <ResearchItemSkeleton /> :
                            <div style={{ height: "65vh" }}>
                            </div>
                    ) : (
                        <div>
                            <div>

                                <Stack direction="row" spacing={2} sx={{ margin: '4px 0' }}>

                                    <Button startIcon={<OpenInNewIcon />}
                                        onClick={() => window.open(`/projects/${params.project}/${itemId}/spreadsheeteditor`, '_blank').focus()}
                                        color='success' size='small' fullWidth
                                        disabled={!data.writable}>
                                        Spreadsheet
                                    </Button>
                                    <SpreadSheetItemMenu data={data}
                                        onDeleted={() => mutate({ ...data, spreadsheet: false })} />

                                    <Button startIcon={<OpenInNewIcon />}
                                        onClick={() => window.open(`/projects/${params.project}/${type}/${itemId}`, '_blank').focus()}
                                        size='small' fullWidth>
                                        Expand
                                    </Button>
                                </Stack>

                                {/*{type === "samples" &&*/}
                                {/*    <Stack direction="row" spacing={2} sx={{margin: '4px 0'}}>*/}
                                {/*        /!*<Button startIcon={<OpenInNewIcon />} onClick={() => window.open(`/projects/${params.project}/samples/${itemId}/spreadsheeteditor`, '_blank').focus()} color='success' size='small' fullWidth>*!/*/}
                                {/*        /!*  Spreadsheet*!/*/}
                                {/*        /!*</Button>*!/*/}
                                {/*        <Button startIcon={<OpenInNewIcon/>}*/}
                                {/*                onClick={() => window.open(`/projects/${params.project}/samples/${itemId}`, '_blank').focus()}*/}
                                {/*                size='small' fullWidth>*/}
                                {/*            Expand*/}
                                {/*        </Button>*/}
                                {/*    </Stack>}*/}

                                {/*{type === "researchitems" &&*/}
                                {/*    <Stack direction="row" spacing={2} sx={{margin: '4px 0'}}>*/}
                                {/*        /!*<Button startIcon={<OpenInNewIcon />} onClick={() => window.open(`/projects/${params.project}/samples/${itemId}/spreadsheeteditor`, '_blank').focus()} color='success' size='small' fullWidth>*!/*/}
                                {/*        /!*  Spreadsheet*!/*/}
                                {/*        /!*</Button>*!/*/}
                                {/*        <Button startIcon={<OpenInNewIcon/>}*/}
                                {/*                onClick={() => window.open(`/projects/${params.project}/researchitems/${itemId}`, '_blank').focus()}*/}
                                {/*                size='small' fullWidth>*/}
                                {/*            Expand*/}
                                {/*        </Button>*/}
                                {/*    </Stack>}*/}

                                <div style={{ whiteSpace: 'nowrap', overflow: 'scroll', margin: '8px 0' }}>
                                    {sortedFiles.map((file, i) => {
                                        let file_ext = ""
                                        let file_name = ""
                                        if (file.Name != null) {
                                            file_ext = file.Name.split('.').pop()
                                            file_name = file.Name
                                        }
                                        return (
                                            <FileCard i={i} sortedFiles={sortedFiles} type={type} data={data} key={i}
                                                fileName={file_name} fileExtension={file_ext}
                                                onDeleted={(id) => mutate({
                                                    ...data,
                                                    files: data.files.filter(f => f.id !== id)
                                                })} file={file} />);
                                    })}
                                </div>


                                {(writable && !_protected) && <FileUploadButton onUploaded={filesUploaded} />}

                                {data?.rawdata
                                    && <Grid container columnSpacing={1}>
                                        {data["rawdata"].map((rawdata, i) => (
                                            <Grid item xs={rawDataGridSize}>
                                                <Button sx={{ marginTop: '8px' }} key={i} variant="outlined" onClick={() => {
                                                    setRenderRawData(true);
                                                    setShowRawData(rawdata.id);
                                                }} fullWidth size='small' startIcon={<TableViewIcon />}>
                                                    <Tooltip title={rawdata.name} placement="top">
                                                        <Typography overflow={"hidden"} variant="body2" fontSize={12}>{rawdata.name}</Typography>
                                                    </Tooltip>
                                                </Button>
                                            </Grid>
                                        ))}
                                    </Grid>}

                                {renderRawData ? (
                                    <RawDataOverlay
                                        onExited={() => setRenderRawData(false)}
                                        show={showRawData !== false}
                                        rawid={showRawData}
                                        onClose={() => setShowRawData(false)}
                                        writable={writable}
                                        itemData={data}
                                        mutateItem={mutate}
                                    />
                                ) : null}

                                {linked_items ? (
                                    <div className="field" style={{ marginTop: '16px' }}>
                                        <ItemSelector
                                            linked_items={linked_items}
                                            group={group}
                                            project={project}
                                            itemId={itemId}
                                            writable={(writable && !_protected)}
                                            _protected={_protected}
                                            data={data}
                                            mutateExp={mutate}
                                            type={type}
                                            groups={groups}
                                            mutateGroups={mutateGroups}
                                        />
                                    </div>
                                ) : null}


                                {data?.experiments ? (
                                    <div className="field" style={{ marginTop: "20px" }}>
                                        Used in Experiments
                                        <ul
                                            className="list-group"
                                            style={{ maxHeight: "50vh", overflowY: "scroll" }}
                                        >
                                            {data.experiments?.map((exp, i) => (
                                                <li
                                                    className="list-group-item list-group-item-action"
                                                    key={exp.id}
                                                    style={{ display: "flex" }}
                                                    onClick={() => {
                                                        setShowItemOverlay(exp.id);
                                                        setRenderItemOverlay(true);
                                                    }}
                                                >
                                                    {/*<GiMicroscope style={{marginRight: "10px", minHeight: "10px", minWidth: "10px"}}/>*/}
                                                    <Typography variant={"body1"}>  {exp["Name"]} </Typography>
                                                </li>
                                            ))}
                                            {data.experiments === 0 ? (
                                                <li className="list-group-item list-group-item-action">
                                                    Not used in experiments.
                                                </li>
                                            ) : null}
                                        </ul>
                                        {renderItemOverlay ? (
                                            <ResearchItemOverlay
                                                onExited={() => setRenderItemOverlay(false)}
                                                show={showItemOverlay !== false}
                                                onClose={() => setShowItemOverlay(false)}

                                                group={group}
                                                project={project}
                                                groups={groups}
                                                mutateGroups={mutateGroups}
                                                data={[{
                                                    id: showItemOverlay,
                                                }]}
                                            />
                                        ) : null}
                                    </div>
                                ) : null}

                                <DraggableFields
                                    fields={fields}
                                    isParent={true}
                                    parentID={data.id}
                                    parentType={type}
                                    autoExpanded={expanded}
                                    updateFieldOnDragEnd={updateFieldOnDragEnd}
                                    writable={(writable && !_protected)}
                                    admin={admin}
                                    onFieldValueChange={handleFieldValueChange}
                                    onFieldUnitChange={handleFieldUnitChange}
                                />
                            </div>


                            {(writable && !_protected) && <>
                                <hr />
                                <AddField
                                    onAdded={fieldAdded}
                                    target={type}
                                    targetId={itemId}
                                    notebook={false}
                                    admin={admin}
                                /></>}
                        </div>
                    )}
                </CardContent>
            </Card>
            <GenericDialog title={"Import data!"}
                subInfo={"We detected one or more files that could be imported. Do you want" +
                    " to open the raw data import tool?"} open={openImportToolDialog}
                handleClose={() => setOpenImportToolDialog(false)}
                handleSubmit={() => {
                    setOpenImportTool(true);
                    setOpenImportToolDialog(false)
                }}
                primaryActionText={"Open import tool"}
                dataResult={true} />
            <ImportDataOverlay show={openImportTool} onClose={() => setOpenImportTool(false)}
                setOpenImportTool={setOpenImportTool}
                fileList={importFileList} itemId={itemId}
                itemType={type}
                mutateData={mutate} data={data} />
            <DuplicateItemOverlay group={group} type={type} item={data} open={openDuplicateOverlay} setOpen={setOpenDuplicateOverlay}
                groups={groups} mutateGroups={mutateGroups}></DuplicateItemOverlay>
        </div>
    );
};

export default React.memo(ResearchItemCard);

const ResearchItemSkeleton = (params) => {

    return (
        <>
            <Skeleton variant="rectangular" height={120} />
            <Skeleton variant="text" />
            <Skeleton variant="text" />
            <Skeleton variant="rectangular" height={60} />
            {[...Array(5)].map((e, i) => <div key={i}>
                <Skeleton variant="text" width="30%" />
                <Skeleton variant="rectangular" height={30} />
            </div>)}
            <Skeleton variant="text" />
            <hr />
            <Skeleton variant="rectangular" height={60} />
        </>
    );

}

const ResearchItemMenu = (props) => {
    const [anchorEl, setAnchorEl] = React.useState<null | HTMLElement>(null);
    const open = Boolean(anchorEl);
    const [openToast, setShowToast] = React.useState(false);
    const [openToastCopiedData, setShowToastCopiedData] = React.useState(false);

    const [metaData, setMetaData] = React.useState("");
    const handleClick = (event: React.MouseEvent<HTMLElement>) => {
        setAnchorEl(event.currentTarget);
    };
    const handleClose = () => {
        setAnchorEl(null);
    };


    const [showDeleteDialog, setShowDeleteDialog] = React.useState(false);
    const [showCopyDataClipboard, setShowCopyDataClipboard] = React.useState(false);
    return (
        <>
            <IconButton
                onClick={handleClick}
            // disabled={!props.writable}
            >
                <MoreVertIcon />
            </IconButton>
            <Menu
                anchorEl={anchorEl}
                open={open}
                onClose={handleClose}
            >
                <MenuItem>
                    <FormGroup>
                        <FormControlLabel control={<Switch />} label="Protected" checked={props.protected}
                            onChange={props.protectedChanged} disabled={!props.writable} />
                    </FormGroup>
                </MenuItem>
                <Divider sx={{ bgcolor: "black" }}></Divider>
                <MenuItem>
                    <CopyToClipboard text={props.shortId} onCopy={
                        () => setShowToast(true)
                    }>
                        <span> <ContentPasteIcon /> Copy short-id to clipboard</span>
                    </CopyToClipboard>
                </MenuItem>
                <MenuItem
                    onClick={() => { setShowCopyDataClipboard(true); handleClose() }}>
                    <span> <ContentPasteIcon /> Copy data to clipboard</span>
                </MenuItem>
                <MenuItem onClick={() => {
                    props.setOpenDuplicateOverlay(true)
                    handleClose()
                }}>
                    <span><ContentCopyIcon /> Duplicate item </span>
                </MenuItem>
                <Divider sx={{ bgcolor: "black" }}></Divider>
                <MenuItem onClick={() => {
                    setShowDeleteDialog(true);
                    handleClose()
                }}>
                    <span style={{ color: "red" }}><DeleteIcon /> Delete</span>
                </MenuItem>


            </Menu>
            <DeleteDialog {...props} open={showDeleteDialog} handleClose={() => setShowDeleteDialog(false)}
                groups={props.groups}
                mutateGroups={props.mutateGroups} />
            <Snackbar
                anchorOrigin={{
                    vertical: 'top',
                    horizontal: 'right'
                }}
                open={openToast} autoHideDuration={1000} onClose={() => setShowToast(false)} >
                <Alert onClose={() => setShowToast(false)} severity="success" sx={{ width: '100%' }}>
                    Short ID copied !
                </Alert>

            </Snackbar>
            <Snackbar
                anchorOrigin={{
                    vertical: 'top',
                    horizontal: 'right'
                }}
                open={openToastCopiedData} autoHideDuration={1000} onClose={() => setShowToastCopiedData(false)}>
                <Alert onClose={() => setShowToastCopiedData(false)} severity="success" sx={{ width: '100%' }}>
                    Data copied !
                </Alert>

            </Snackbar>

            <CopyDataClipboardOverlay {...props} open={showCopyDataClipboard} setOpen={setShowCopyDataClipboard}
                setShowToast={setShowToastCopiedData} datatables={props.datatables} />
        </>
    )
}
const SpreadSheetItemMenu = ({ data, onDeleted }) => {
    const [anchorEl, setAnchorEl] = React.useState<null | HTMLElement>(null);
    const open = Boolean(anchorEl);
    const params = useParams();
    const handleClick = (event: React.MouseEvent<HTMLElement>) => {
        setAnchorEl(event.currentTarget);
    };
    const [showSpreadsheetDeleteDialog, setShowSpreadsheetDeleteDialog] = React.useState(false);
    const handleClose = () => {
        setAnchorEl(null);
        setShowDialog(false);
    };

    const [showDialog, setShowDialog] = React.useState(false);
    const [openAsTemplate, setOpenAsTemplate] = React.useState(false);
    const [dialogToShowName, setDialogToShowName] = React.useState('');
    const [dataToSubmit, setDataToSubmit] = React.useState('');
    const [selectedTemplate, setSelectedTemplate] = React.useState('female');
    const [dataResult, setDataResult] = React.useState([]);

    const handleDialog = (name) => {
        setShowDialog(true);
        setDialogToShowName(name)
    }

    const handleSaveAsTemplate = () => {
        const type = data.typeName
        const name = dataToSubmit
        axios.post(`/web/onlyoffice/${params.project}/create_template/${type}/${data.id}`, { name }).then(() => {
            setShowDialog(false);
            setAnchorEl(null);
            setDialogToShowName('');
        });
    }


    const handleChange = (e) => {
        setDataToSubmit(e.target.value);
    }


    const handleOpenAsTemplate = () => {
        if (data.spreadsheet == false) {
            const axiosTest = axios.get
            axiosTest('/web/onlyoffice/' + params.project + '/spreadsheet_templates').then((axiosTestResult) => {
                setDataResult(axiosTestResult.data.results);
                setOpenAsTemplate(true);
            }
            )

        }
    }

    const openInOnlyoffice = () => {
        setOpenAsTemplate(false)
        const spreadsheetId = selectedTemplate
        const expId = data.id

        function openInOnlyOffice(expId, spreadsheetId) {
            const a = document.createElement('a')
            a.href = "/web/onlyoffice/" + expId + "/" + spreadsheetId;
            document.body.appendChild(a)
            a.setAttribute('target', '_blank');
            a.click()
            document.body.removeChild(a)
        }

        openInOnlyOffice(expId, spreadsheetId)
    }

    const closeOpenAsTemplateDialog = () => {
        setOpenAsTemplate(false);
        //clear selected template if user selected any
        setSelectedTemplate('');
    }

    const handleRadioChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        setSelectedTemplate((event.target as HTMLInputElement).value);
    };

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


                <MenuItem onClick={() => handleDialog(dialogs.save)}>
                    <Stack direction="row" spacing={2}>
                        {data.spreadsheet == true && <SaveIcon />}
                        {data.spreadsheet == false && <SaveIcon color="disabled" />}

                        <Typography>Save as template</Typography>
                    </Stack>
                </MenuItem>

                <MenuItem onClick={handleOpenAsTemplate}>
                    <Stack direction="row" spacing={2}>
                        {data.spreadsheet == false && <OpenInNewIcon />}
                        {data.spreadsheet == true && <OpenInNewIcon color="disabled" />}
                        <Typography>Open with template</Typography>
                    </Stack>
                </MenuItem>

                {data.spreadsheet == false && <MenuItem onClick={() => {
                    handleClose()
                }}>
                    <Stack direction="row" spacing={2}>
                        <DeleteForeverIcon color='disabled' />
                        <Typography>Delete spreadsheet</Typography>
                    </Stack>
                </MenuItem>}

                {data.spreadsheet == true && <MenuItem onClick={() => {
                    setShowSpreadsheetDeleteDialog(true);
                    handleClose()
                }}>
                    <Stack direction="row" spacing={2}>
                        <DeleteForeverIcon sx={{
                            color: '#E0144C'
                        }
                        } />
                        <Typography sx={{
                            color: '#E0144C'
                        }}>Delete spreadsheet</Typography>

                    </Stack>
                </MenuItem>}
            </Menu>

            <DeleteSpreadsheetDialog data={data} open={showSpreadsheetDeleteDialog}
                handleClose={() => setShowSpreadsheetDeleteDialog(false)} onDeleted={onDeleted} />

            {(openAsTemplate && dataResult) && <GenericDialog
                title='Open in spreadsheet template'
                handleClose={closeOpenAsTemplateDialog}
                open={openInOnlyoffice}
                handleSubmit={openInOnlyoffice}
                primaryActionText="Open"
            >
                <FormControl>

                    <FormLabel id="demo-radio-buttons-group-label">Choose the template you would like to open your
                        spreadsheet:</FormLabel>
                    <RadioGroup
                        aria-labelledby="demo-radio-buttons-group-label"
                        defaultValue="None"
                        name="radio-buttons-group"
                        onChange={handleRadioChange}
                    >
                        <hr />

                        {dataResult.map(data => {
                            return (
                                <div>
                                    <FormControlLabel value={data.id} control={<Radio />} label={data.name} />
                                    <hr />
                                </div>
                            )
                        })}
                    </RadioGroup>

                </FormControl>
            </GenericDialog>
            }

            {(openAsTemplate && !dataResult) && <GenericDialog
                title='Open in spreadsheet template'
                handleClose={closeOpenAsTemplateDialog}
                open={closeOpenAsTemplateDialog}
                primaryActionText="Ok"
                dataResult={dataResult}
            >
                <FormControl>

                    <FormLabel id="demo-radio-buttons-group-label">There is no template available. Please create one
                        first.</FormLabel>


                </FormControl>
            </GenericDialog>}


            {dialogToShowName === dialogs.save && data.spreadsheet == true && showDialog && <GenericDialog
                title="Save template "
                handleClose={handleClose}
                open={showDialog}
                primaryActionText="Save"
                handleSubmit={handleSaveAsTemplate}
                value={selectedTemplate}
            >
                <TextField id="outlined-basic" label="Enter template name" variant="outlined" fullWidth
                    name="templateName"
                    onChange={handleChange}
                />
            </GenericDialog>
            }


        </>
    )
}

const dialogs = {
    save: 'SAVE',
    openWith: 'OPENWITH',
    delete: 'DELETE',
    show: 'SHOW'
}
const DeleteDialog = ({ open, handleClose, name, id, group, type, groups, mutateGroups }) => {
    const [loading, setLoading] = React.useState(false);
    const params = useParams();

    const deleteItem = () => {
        setLoading(true);
        let groupsCopy = []
        groups.map((item) => {
            if (item.id !== id) {
                groupsCopy.push(item)
            }
        })

        axios.delete(`/web/item/${type}/${id}`).then(() => {
            handleClose();
            mutateGroups(groupsCopy)

        });
    }
    return (
        <Dialog open={open} onClose={handleClose}>
            <DialogTitle>Delete {name}?</DialogTitle>
            <DialogContent>

                <DialogContentText></DialogContentText>

            </DialogContent>
            <DialogActions>
                <Button onClick={handleClose} disabled={loading}>Cancel</Button>
                <LoadingButton loading={loading} onClick={deleteItem} color="warning">Delete</LoadingButton>
            </DialogActions>
        </Dialog>
    )
}

const DeleteSpreadsheetDialog = ({ open, handleClose, data, onDeleted }) => {
    const [loading, setLoading] = React.useState(false);
    const params = useParams();

    const deleteItem = () => {
        setLoading(true);
        axios.delete(`/web/onlyoffice/delete_spreadsheet/${data.typeName}/${data.id}`).then(() => {
            handleClose();
            onDeleted();

        });
    }

    return (
        <Dialog open={open} onClose={handleClose}>
            <DialogTitle>Delete spreadsheet of {data.Name}?</DialogTitle>
            <DialogContent>

                <DialogContentText></DialogContentText>

            </DialogContent>
            <DialogActions>
                <Button onClick={handleClose} disabled={loading}>Cancel</Button>
                <LoadingButton loading={loading} onClick={deleteItem} color="warning">Delete</LoadingButton>
            </DialogActions>
        </Dialog>
    )
}

const GenericDialog = (props) => {
    const { title, subInfo, open, handleClose, handleSubmit, primaryActionText, dataResult } = props;
    return (
        <Dialog open={open} onClose={handleClose} fullWidth>
            <DialogTitle>{title}</DialogTitle>
            <DialogContent>

                {subInfo && <DialogContentText>
                    {subInfo}
                </DialogContentText>}
                {props.children}
            </DialogContent>
            <DialogActions>
                {dataResult != false && <Button onClick={handleClose}>Cancel</Button>}
                {dataResult != false &&
                    <LoadingButton onClick={handleSubmit} color="warning">{primaryActionText}</LoadingButton>}
                {dataResult == false &&
                    <LoadingButton onClick={handleClose} color="warning">{primaryActionText}</LoadingButton>}
            </DialogActions>
        </Dialog>
    )
}


function DuplicateItemOverlay({ group, type, open, setOpen, item, groups, mutateGroups }) {

    const [creating, setCreating] = useState(false)
    const [copyFields, setCopyFields] = useState(true);
    const [copyDataTable, setCopyDataTable] = useState(false);
    const [copyFiles, setCopyFiles] = useState(false);

    const [showType, setShowType] = useState("")
    const addRecentlyCreated = useGroupIndexStore((state) => state.addRecentlyCreated);
    const addRecentlyCreatedGroups = useGroupIndexStore((state) => state.addRecentlyCreatedGroups);
    const params = useParams();

    function capitalizeFirstLetter(string) {
            return string.charAt(0).toUpperCase() + string.slice(1);
        }
    
    function createNodes(id, type, name, parentGroupID, parent) {

            const groupsCopy = []
            if (type === "groups") {
                const newItem = {
                    id: id,
                    name: name,
                    type: "Groups",
                    show_type: "Groups",
                    parent: parent,
                    group_id: id,
                    visible: true,
                    droppable: true,
                    expandable: true,
                    text: name
                }
                groupsCopy.push(newItem);
                groupsCopy.push(...groups)
                addRecentlyCreated(newItem.id);
                if (parent === 0) {
                    addRecentlyCreatedGroups(newItem.id);
                }
                mutateGroups(groupsCopy, { revalidate: true });

            } else {
                const typeCapitalized = capitalizeFirstLetter(type)
                let found = false
                const tempGroupCopy = [...groups]
                tempGroupCopy.map(item => {
                    if (item.id.toLowerCase() === `${parentGroupID}/sep/${type}`.toLowerCase()) {
                        item.visible = true;
                        found = true;
                    }
                })
                if (!found) {
                    let cat_node = {
                        id: `${parentGroupID}/sep/${typeCapitalized}`,
                        name: typeCapitalized,
                        type: typeCapitalized,
                        show_type: typeCapitalized,
                        short_id: "",
                        parent: parentGroupID,
                        droppable: false,
                        expandable: true,
                        group_id: parentGroupID,
                        visible: true,
                        text: typeCapitalized,
                    }
                    groupsCopy.push(cat_node)
                    addRecentlyCreated(cat_node.id);
                }
                const newItem = {
                    id: id,
                    name: name,
                    type: typeCapitalized,
                    show_type: typeCapitalized,
                    parent: `${parentGroupID}/sep/${typeCapitalized}`,
                    group_id: parentGroupID,
                    visible: true,
                    droppable: false,
                    expandable: false,
                    text: name
                }
                groupsCopy.push(newItem);
                groupsCopy.push(...groups)
                mutateGroups(groupsCopy, { revalidate: false });
                addRecentlyCreated(newItem.id);

            }

        }

    const create = (e) => {
        setCreating(true);
        axios.post(`/web/copy-template`, {
            targetProject: params.project,
            targetGroup: group.id,
            sourceId: item.id,
            collection: type,
            includeExps: true,
            includeSamples: true,
            includeResearchItems: true,
            includeSubgroups: true,
            includeFields: copyFields,
            includeRawData: copyDataTable,
            includeFiles: copyFiles

        }).then(res => {
            console.log(res.data);
            createNodes(res.data.id, type, res.data.name, group.id, group.parent);
            setCreating(false);
            setOpen(false)
            
        });

    }

    return (
        <Dialog
            open={open}
            fullWidth
            style={{ marginLeft: "auto", marginRight: "auto", width: "500px" }}
        >
            <DialogTitle>
                Duplicate {showType}: '{name}'
            </DialogTitle>
            <DialogContent>
                <Typography>Include:</Typography>
                <Stack direction={"column"} marginLeft={"40px"}>
                    <FormControlLabel control={<Checkbox checked={copyFields} />}
                        label={"fields"} onClick={() => {
                            setCopyFields(!copyFields)
                        }} />
                    <FormControlLabel control={<Checkbox checked={copyDataTable} />}
                        label={"data tables"} onClick={() => {
                            setCopyDataTable(!copyDataTable)
                        }} />
                    <FormControlLabel control={<Checkbox checked={copyFiles} />}
                        label={"files"} onClick={() => {
                            setCopyFiles(!copyFiles)
                        }} />


                </Stack>


            </DialogContent>
            <DialogActions>
                <Button onClick={() => {
                    setOpen(false)
                    setCreating(false)
                }}>Cancel</Button>
                <LoadingButton color="success" loading={creating} onClick={create}>
                    Duplicate
                </LoadingButton>
            </DialogActions>
        </Dialog>
    )

}


function CopyDataClipboardOverlay({ id, type, open, setOpen, setShowToast, datatables }) {
    // const item = props.item
    const [copying, setCopying] = useState(false)
    const [decimalSeparator, setDecimalSeparator] = useState(".");
    const [format, setFormat] = useState(",");
    const [elementsToBeCopied, setElementToBeCopied] = useState([]);
    const [allChecked, setAllCheck] = useState(true);
    const [openToastMetaData, setShowToastMetaData] = React.useState(false);
    const [metaData, setMetaData] = useState("");

    const [buttonText, setButtonText] = useState("Copy")
    const [buttonDisabled, setButtonDisabled] = useState(false)

    const [showType, setShowType] = useState("")

    useEffect(() => {
        const elements = [{ id: "metadata", name: "Meta data", checked: true }]
        datatables.map(table => {
            elements.push({ id: table.id, name: table.name, checked: true })
        })
        setElementToBeCopied(elements)
    }, [datatables])

    const params = useParams();

    function elementChanged(e, id) {
        let allChecked = true
        const elements = [...elementsToBeCopied]
        elements.map(element => {
            if (element.id === id) {
                element.checked = e.target.checked
            }
            if (element.checked === false) {
                allChecked = false
            }
        })
        if (allChecked) {
            setAllCheck(true)
        }
        else {
            setAllCheck(false)
        }
        setElementToBeCopied(elements)
        
        
    }

    function allChanged(e) {
        setAllCheck(e.target.checked)
        const elements = [...elementsToBeCopied]
        if (e.target.checked) {
            elements.map(element => {
                element.checked = true
            })
        }
        else {
            elements.map(element => {
                element.checked = false
            })
        }
        setElementToBeCopied(elements)

    }
    
    function copyData(format, decimalSeparator, elementsToBeCopied) {
        const data = {
            decimalSeparator: decimalSeparator,
            format: format,
            elementsToCopy: elementsToBeCopied.filter(e => e.checked).map(e => e.id)
        }

        axios.post(`/web/projects/${params.project}/${type}/${id}/copy-clipboard`, data).then((res) => {
            if (format === "json") {
                setMetaData(JSON.stringify(res.data, null, 2))
            } else {
                setMetaData(res.data)
            }
            setButtonDisabled(false)
            setShowToastMetaData(true)
            setCopying(false)
        })
    }

    const debouncedCopyData = useCallback(
    debounce((format, decimalSeparator, elementsToBeCopied) => {
        copyData(format, decimalSeparator, elementsToBeCopied);
    }, 500),
    []
);

    useEffect(() => {
        setButtonDisabled(true)
        setCopying(true)
        if (open) {
            debouncedCopyData(format, decimalSeparator, elementsToBeCopied)
        }

    }, [open, format, decimalSeparator, elementsToBeCopied])


    return (
        <Dialog
            open={open}
            fullWidth
            style={{ marginLeft: "auto", marginRight: "auto", width: "450px" }}
        >
            <DialogTitle>
                Copy data to clipboard
            </DialogTitle>
            <DialogContent>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                    <Typography style={{ marginTop: "8px" }}>Decimal separator:</Typography>

                    <FormControl style={{ minWidth: "50%", }}>
                        <Select
                            value={decimalSeparator}
                            variant="standard"
                            onChange={(e: any) => setDecimalSeparator(e.target.value)}
                        >
                            <MenuItem value=".">"." (Point)</MenuItem>
                            <MenuItem value=",">"," (Comma)</MenuItem>

                        </Select>
                    </FormControl>
                </div>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginTop: "30px" }}>
                    <Typography style={{ marginTop: "8px" }}>Format:</Typography>

                    <FormControl style={{ minWidth: "50%" }}>

                        <Select
                            value={format}
                            variant="standard"
                            onChange={(e: any) => setFormat(e.target.value)}
                        >
                            <MenuItem value={"\t"} key={"\t"}>CSV Tab separated</MenuItem>
                            <MenuItem value={","} key={","}>CSV "," separated</MenuItem>
                            <MenuItem value={";"} key={";"}>CSV ";" separated</MenuItem>
                            <MenuItem value={"json"} key={"json"}>JSON</MenuItem>

                        </Select>
                    </FormControl>

                </div>
                <div >
                    <div style={{ display: "flex", marginTop: "40px" }}>
                        <Typography style={{ marginTop: "8px" }}>Elements to be copied:</Typography>
                        <FormControlLabel key={"all"} control={<Checkbox checked={allChecked}
                         onChange={(e) => allChanged(e)} style={{marginLeft: "20px"}} />} label={""} />
                    </div>
                    <Stack direction={"column"} style={{ marginLeft: "40px", marginTop: "10px" }}>
                        {elementsToBeCopied.map(element =>
                            <FormControlLabel key={element.id} 
                            control={<Checkbox checked={element.checked} onChange={(e) => elementChanged(e, element.id)} />} label={element.name} />
                        )
                        }
                    </Stack>

                    {/* <FormControl style={{ minWidth: "40%" }}>
                        
                    </FormControl> */}
                </div>




            </DialogContent>
            <DialogActions>
                <Button onClick={() => {
                    setOpen(false)
                    setCopying(false)
                }}>Cancel</Button>
                <CopyToClipboard text={metaData} onClick={() => {  }}>
                    <LoadingButton color="success" loading={copying} onClick={() => {
                        // setOpen(false)
                        setShowToast(true)
                    }}
                        disabled={buttonDisabled}>
                        {buttonText}
                    </LoadingButton>
                </CopyToClipboard>


            </DialogActions>
        </Dialog>
    )

}