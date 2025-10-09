import Masonry from '@mui/lab/Masonry';
import { Skeleton } from '@mui/material';
import Box from '@mui/material/Box';
import React, { useEffect, useState } from 'react';
import ErrorBoundary from './ErrorBoundary';
import ResearchItemCard from './ResearchItemCard';

import { useParams } from 'react-router-dom';
import CreateButton from './CreateButton';
import GroupPropertiesCard from './GroupPropertiesCard';
import NoData from './NoData/NoData';
import ExperimentPage from "../pages/ExperimentPage";


import useActiveResearchItems from '../hooks/useActiveResearchItems';
import SamplePage from "../pages/SamplePage";
import ResearchItemPage from "../pages/ResearchItemPage";
import axios from "axios";
import { log } from "console";

const ResearchItemList = ({ showGroupProperties, currentGroup, setCurrentGroup, groups, mutateGroups }) => {

    const [showCards, setShowCards] = useState(false);
    const [showExp, setShowExp] = useState(false);
    const [showSample, setShowSample] = useState(false);
    const [showResearchItem, setShowResearchItem] = useState(false);
    const [researchItems, setResearchItems] = useState([]);
    const [writable, setWritable] = useState(false);
    const [projectAdmin, setProjectAdmin] = useState(false);

    const params = useParams();
    const project = params.project;

    const loading = (groups === undefined);
    let activeResearchItems = useActiveResearchItems(true, groups);

    useEffect(() => {
        axios.get("/web/permissions/" + project).then((r) => {
            if (r.data === "write") {
                setWritable(true)
            } else if (r.data === "admin") {
                setWritable(true)
                setProjectAdmin(true)
            }
        })
    }, [project]);

    useEffect(() => {
        setShowCards(false);
        setShowExp(false);
        setShowSample(false);
        setShowResearchItem(false);
        setResearchItems(activeResearchItems);

    }, [activeResearchItems])

    useEffect(() => {
        if (researchItems === undefined) {
            return;
        }
        if (researchItems.length > 1) {
            setShowCards(true);
            setShowExp(false);
            setShowSample(false);
            setShowResearchItem(false);
        } else if (researchItems.length === 1) {
            setShowCards(false)
            setShowExp(false);
            setShowSample(false);
            setShowResearchItem(false);
            if (researchItems[0].type === 'Experiments') {
                setShowExp(true);
            } else if (researchItems[0].type === 'Samples') {
                setShowSample(true);
            } else if (researchItems[0].type !== "Experiments" && researchItems[0].type !== "Samples") {
                setShowResearchItem(true);
            }
        }
    }, [researchItems])
    return (
        <> 
            {(currentGroup && showGroupProperties) ?
                <Box><GroupPropertiesCard groupId={currentGroup.id} setCurrentGroup={setCurrentGroup}
                    groups={groups} mutateGroups={mutateGroups} />
                </Box> : null}
            {(showCards) && (
                <Masonry columns={{ xs: 1, md: 2, lg: 3, xl: 4 }} spacing={1}>
                    {loading && [...Array(9)].map((e, i) =>
                        <Skeleton key={i} style={{ borderRadius: '5px' }} variant="rectangular" height={600} />)}

                    {researchItems.map((item, index) => (
                        (item !== undefined) &&
                        <Box key={item.id}>
                            <ErrorBoundary>
                                <ResearchItemCard startInView={index < 5}
                                    group={currentGroup}
                                    type={item.type.toLowerCase()}
                                    project={project}
                                    itemId={item.id}
                                    withCheckbox={true}
                                    groups={groups}
                                    mutateGroups={mutateGroups}
                                />
                            </ErrorBoundary>
                        </Box>
                    ))}
                </Masonry>)
            }

            {(researchItems.length > 0 && showExp) && (
                <ExperimentPage expid={researchItems[0].id} project={project} group={currentGroup} 
                />)
            }
            {(researchItems.length > 0 && showSample) && (
                <SamplePage sampleid={researchItems[0].id} project={project} group={currentGroup} 
                />
            )}
            {(researchItems.length > 0 && showResearchItem) && (
                <ResearchItemPage researchitemid={researchItems[0].id} project={project} group={currentGroup} />
            )}

            {(researchItems.length < 1 && currentGroup) ? (
                <NoData
                    heading='Nothing here yet...'
                    subHeading="Hmm.. Seems like you don't have any research content. Create your awesome research content in just few clicks !"
                    style={{ margin: '20px 0px' }}
                    btnComponent={<CreateButton
                        currentGroup={currentGroup} writable={writable} 
                        admin={projectAdmin} groups={groups} mutateGroups={mutateGroups}/>}
                />
            ) : null}
        </>
    );
}

export default React.memo(ResearchItemList);
