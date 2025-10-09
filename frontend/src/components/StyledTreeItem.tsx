import React from 'react';
import {
  Tree,
  getBackendOptions,
  MultiBackend,
} from "@minoru/react-dnd-treeview";


import TreeItem, {treeItemClasses} from '@mui/lab/TreeItem';
import Box from '@mui/material/Box';
import {styled} from '@mui/material/styles';
import Typography from '@mui/material/Typography';
import {Draggable, Droppable} from 'react-beautiful-dnd';

declare module 'react' {
    interface CSSProperties {
        '--tree-view-color'?: string;
        '--tree-view-bg-color'?: string;
    }
}

// type StyledTreeItemProps = TreeItemProps & {
//     bgColor?: string;
//     color?: string;
//     labelIcon: React.ElementType<SvgIconProps>;
//     labelInfo?: string;
//     labelText: string;
//     indent_level: number;
// };

export const StyledTreeItemRoot = styled(TreeItem)(({theme}) => ({

    color: theme.palette.text.secondary,
    [`& .${treeItemClasses.content}`]: {
        color: theme.palette.text.secondary,
        borderTopRightRadius: theme.spacing(2),
        borderBottomRightRadius: theme.spacing(2),
        paddingRight: theme.spacing(1),
        fontWeight: theme.typography.fontWeightMedium,
        '&.Mui-expanded': {
            fontWeight: theme.typography.fontWeightRegular,
        },
        '&:hover': {
            backgroundColor: theme.palette.action.hover,
        },
        '&.Mui-focused, &.Mui-selected, &.Mui-selected.Mui-focused': {
            backgroundColor: `var(--tree-view-bg-color, ${theme.palette.action.selected})`,
            color: 'var(--tree-view-color)',
        },
        [`& .${treeItemClasses.label}`]: {
            fontWeight: 'inherit',
            color: 'inherit',
        },
    },
    [`& .${treeItemClasses.group}`]: {
        marginLeft: 0,
        [`& .${treeItemClasses.content}`]: {
            paddingLeft: theme.spacing(2),
        },
    },
}));

export function StyledTreeItem(props) {
    const {
        bgColor,
        color,
        labelIcon: LabelIcon,
        labelInfo,
        labelText,
        indend_level,
        index,
        ...other
    } = props;

    return (
        <StyledTreeItemRoot
            label={
                <Draggable draggableId={props.nodeId} index={index}>
                    {provided => (
                        <div
                            {...provided.draggableProps}
                            {...provided.dragHandleProps}
                            ref={provided.innerRef}>
                            <Box sx={{display: 'flex', alignItems: 'center', p: 0.5, pr: 0}}>
                                <Box component={LabelIcon} color="inherit" sx={{mr: 1}}/>
                                <Typography variant="body2" sx={{fontWeight: 'inherit', flexGrow: 1}}>
                                    {labelText}
                                </Typography>
                                <Typography variant="caption" color="inherit">
                                    {labelInfo}
                                </Typography>
                            </Box>
                        </div>
                    )}

                </Draggable>
            }
            style={{
                '--tree-view-color': color,
                '--tree-view-bg-color': bgColor,
            }}
            {...other}
        />
    );
}

export function StyledTreeItemGroup(props) {
    const {
        bgColor,
        color,
        labelIcon: LabelIcon,
        labelInfo,
        labelText,
        indend_level,
        index,
        ...other
    } = props;

    return (
        <Droppable droppableId={props.nodeId}>
            {provided_drop => (
                <div
                    ref={provided_drop.innerRef}
                    {...provided_drop.droppableProps}

                >
                    <StyledTreeItemRoot
                        {...provided_drop.placeholder}

                        label={
                            <Draggable draggableId={props.nodeId} index={index}>
                                {provided_drag => (
                                    <div
                                        {...provided_drag.draggableProps}
                                        {...provided_drag.dragHandleProps}
                                        ref={provided_drag.innerRef}>
                                        <Box sx={{display: 'flex', alignItems: 'center', p: 0.5, pr: 0}}>
                                            <Box component={LabelIcon} color="inherit" sx={{mr: 1}}/>
                                            <Typography variant="body2" sx={{fontWeight: 'inherit', flexGrow: 1}}>
                                                {labelText}
                                            </Typography>
                                            <Typography variant="caption" color="inherit">
                                                {labelInfo}
                                            </Typography>
                                        </Box>
                                    </div>
                                )}

                            </Draggable>
                        }
                        style={{
                            '--tree-view-color': color,
                            '--tree-view-bg-color': bgColor,
                        }}
                        {...other}
                    />
                </div>

            )}

        </Droppable>


    );
}