import {Button, Paper, Stack} from '@mui/material';
import Grid from '@mui/material/Grid';
import {useEffect, useState} from 'react';
import {useParams} from 'react-router-dom';
import useSWR from 'swr';
import AddField from '../components/Fields/AddField';
import Notebook from '../components/Notebook';
import ResearchItemCard from '../components/ResearchItemCard';
import SideDrawer from '../components/SideDrawer';
import LighthouseImage from '../images/lighthouse.svg';
import classes from './DashboardStyle.module.css';
import useGroupIndex from '../hooks/useGroupIndex';

const fetcher = (url) => fetch(url).then((res) => res.json());

export default function ResearchItemPage(props) {
    let researchitemid = ""
    let project = "";
    let group = "";

    let marginRight = "40px"
    let marginLeft = "116px"


    if (props.researchitemid === undefined) {
        // called as standalone page
        const params = useParams();
        researchitemid = params.researchitemid;
        project = params.project;
    } else {
        // opend in databrowserview
        researchitemid = props.researchitemid;
        project = props.project;
        group = props.group;
        marginRight = "20px"
        marginLeft = "0px"
    }

    const {groups, mutateGroups} = useGroupIndex(project)


    const {data, mutate} = useSWR(`/web/item/researchitems/${researchitemid}`, fetcher);
    const [hideAddNewField, setHideAddNewField] = useState(true);
    const [notebooks, setNotebooks] = useState([]);

    useEffect(() => {
        if (data) {
            setNotebooks(data?.fields.filter((field) => field.Type === 'MultiLine'))
        }
    }, [data]);

    return (
        <>
            <div className={classes.pageStyle} style={{minHeight: '100vh'}}>
                <SideDrawer/>
                <div style={{marginRight: marginRight, marginLeft: marginLeft}}>
                    <div className={classes.headingWrapper}>
                        {/* <div className={classes.heading}>
              Experiment
            </div> */}
                    </div>
                    <div>
                        <Grid container spacing={3}>
                            <Grid item xs={4}>
                                <ResearchItemCard type='researchitems' itemId={researchitemid} group={group}
                                                  project={project} expanded={true} 
                                                  groups={groups} mutateGroups={mutateGroups}/>
                            </Grid>
                            <Grid item xs={8}>
                                {notebooks && notebooks.map((field) => (
                                    <>
                                        <h3>{field.Name}</h3>
                                        <Notebook notebookId={field.Value}/>
                                        <p></p>
                                    </>
                                ))}
                                {notebooks && !notebooks.length && (<Paper sx={{padding: '32px 32px'}}>
                                    <div className={classes.heading}
                                         style={{letterSpacing: "1px", fontSize: "28px", fontWeight: '600'}}>Notebook
                                    </div>
                                    <Stack alignItems='center' justifyContent='center' my={5} spacing={2}>
                                        <img src={LighthouseImage} alt="No notes"
                                             style={{width: "300px", height: '300px'}}/>
                                        <div className={classes.heading}
                                             style={{fontSize: '14px', fontWeight: '400'}}> This researchitem doesn't
                                            have any notebooks. Try adding a notebook field.
                                        </div>
                                        <Button variant="contained" onClick={() => setHideAddNewField(false)}>Add a notebook</Button>
                                    </Stack>
                                    {
                                        notebooks && !notebooks.length ? !hideAddNewField ? <AddField
                                            onAdded={(field) => {
                                                mutate({...data, fields: [...data.fields, field]}, false);
                                            }}
                                            target={'researchitems'}
                                            targetId={researchitemid}
                                            notebook={true}
                                            admin={data.admin}
                                        /> : null : <AddField
                                            onAdded={(field) => {
                                                mutate({...data, fields: [...data.fields, field]}, false);
                                            }}
                                            target={'researchitems'}
                                            targetId={researchitemid}
                                            notebook={true}
                                            admin={data.admin}
                                        />
                                    }


                                </Paper>)}
                            </Grid>
                        </Grid>
                    </div>
                </div>
            </div>
        </>
    );
}


