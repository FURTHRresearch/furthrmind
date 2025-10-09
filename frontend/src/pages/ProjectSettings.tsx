import {Skeleton} from '@mui/material';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import {useState} from 'react';
import {useParams} from 'react-router-dom';
import useSWR from 'swr';
import UserPermissions from '../components/ProjectPermissionList';
import Advance from '../components/Setting/Advance/advance';
import General from '../components/Setting/General/general';
import SideDrawer from '../components/SideDrawer';
import ResearchManagement from '../components/ResearchManagement';
import FieldManagement from '../components/FieldManagement';
import TemplateManagement from '../components/TemplateManagement'
import classes from './Setting.module.css';

const fetcher = url => fetch(url).then(res => res.json());

export default function ProjectSettings() {
    const [value, setValue] = useState(0);
    const handleChange = (event, newValue) => {
        setValue(newValue);
    };
    const params = useParams();
    const {data: project, mutate: mutateProject} = useSWR(`/web/projects/${params.project}/settings`, fetcher);


    return (
        <div className={classes.pageStyle}>
            <SideDrawer/>
            <div className={classes.pageInnerWrapper}>
                <div id="section1">
                    {!project ? <Skeleton width={120} sx={{marginTop: "40px"}}/> :
                        <div className={classes.headingWrapper}>
                            <div className={classes.heading}>
                                Project Settings
                            </div>
                        </div>
                    }
                    {!project ?
                        <Skeleton variant="rectangular" height={270} sx={{marginTop: "20px", borderRadius: "4px"}}/> :
                        <Box sx={{maxWidth: "630px", background: "white", borderRadius: "8px", margin: "20px 0px"}}>
                            <Box sx={{borderBottom: 1, borderColor: "divider", padding: "10px 8px"}}>
                                {/*<Tabs value={value} onChange={handleChange} aria-label="basic tabs example">*/}
                                {/*    <Tab label="General"/>*/}
                                {/*    {(user.id === project.owner) && <Tab label="Advanced"/>}*/}
                                {/*</Tabs>*/}
                                <General/>
                            </Box>
                            <Box sx={{borderBottom: 1, borderColor: "divider", padding: "10px 8px"}}>
                                <Advance project={project}/>
                            </Box>


                            {/*<TabPanel value={value} index={0}>*/}
                            {/*</TabPanel>*/}
                            {/*<TabPanel value={value} index={1}>*/}
                            {/*</TabPanel>*/}

                        </Box>
                    }

                </div>

                <div id="section2">
                    {!project ? <Skeleton width={120} sx={{marginTop: "40px"}}/> :
                        <div className={classes.headingWrapper}>
                            <div className={classes.heading}>
                                Collaborators
                            </div>
                        </div>
                    }
                    {!project ?
                        <Skeleton variant="rectangular" height={270} sx={{marginTop: "20px", borderRadius: "4px"}}/> :
                        <UserPermissions/>}
                </div>

                <div id="section3">
                    {!project ? <Skeleton width={120} sx={{marginTop: "40px"}}/> :
                        <div className={classes.headingWrapper}>
                            <div className={classes.heading}>
                                Field Management
                            </div>
                        </div>
                    }
                    {!project ?
                        <Skeleton variant="rectangular" height={270} sx={{marginTop: "20px", borderRadius: "4px"}}/> :
                        <FieldManagement/>}
                </div>

                <div id="section4">
                    {!project ? <Skeleton width={120} sx={{marginTop: "40px"}}/> :
                        <div className={classes.headingWrapper}>
                            <div className={classes.heading}>
                                Research Category Management
                            </div>
                        </div>
                    }
                    {!project ?
                        <Skeleton variant="rectangular" height={270} sx={{marginTop: "20px", borderRadius: "4px"}}/> :
                        <ResearchManagement/>}
                </div>

                <div id="section5">
                    {!project ? <Skeleton width={120} sx={{marginTop: "40px"}}/> :
                        <div className={classes.headingWrapper}>
                            <div className={classes.heading}>
                                Spreadsheet Template Management
                            </div>
                        </div>
                    }
                    {!project ?
                        <Skeleton variant="rectangular" height={270} sx={{marginTop: "20px", borderRadius: "4px"}}/> :
                        <TemplateManagement/>}
                </div>
                <div id={"section6"}>
                    {!project ? <Skeleton width={120} sx={{marginTop: "40px"}}/> :
                        <div className={classes.headingWrapper}>
                            <div className={classes.heading}>
                            </div>
                        </div>
                    }
                </div>
            </div>
        </div>
    )
}

function TabPanel(props) {
    const {children, value, index, ...other} = props;

    return (
        <div
            role="tabpanel"
            hidden={value !== index}
            id={`simple-tabpanel-${index}`}
            aria-labelledby={`simple-tab-${index}`}
            {...other}
        >
            {value === index && (
                <Box sx={{p: 3}}>
                    <Typography>{children}</Typography>
                </Box>
            )}
        </div>
    );
}