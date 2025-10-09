import React from 'react';


import TreeItem, {treeItemClasses} from '@mui/lab/TreeItem';
import Box from '@mui/material/Box';
import {styled} from '@mui/material/styles';
import Typography from '@mui/material/Typography';
import {Draggable} from "react-beautiful-dnd";


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
    // [`& .${treeItemClasses.group}`]: {
    //     marginLeft: 0,
    //     [`& .${treeItemClasses.content}`]: {
    //         paddingLeft: theme.spacing(2),
    //     },
    // },
}));

export function StyledTreeItem(props) {
    const {
        nodeId,
        index,
        bgColor,
        color,
        labelIcon: LabelIcon,
        labelInfo,
        labelText,
        indend_level,
        ...other
    } = props;

    // const [{isDragging}, drag] = useDrag({
    //     collect: (monitor: DragSourceMonitor) => ({
    //         isDragging: monitor.isDragging()
    //     }),
    //     type: 'TreeItem'
    // })
    //
    // // stop event propagation and thus disable TreeView focus: required to make
    // // drop and drag work on seemingly all browsers (except for Firefox); see
    // //   https://github.com/mui/material-ui/issues/29518#issuecomment-990760866
    // const ref = useCallback((element: Element) => {
    //     element?.addEventListener('focusin', (e) => {
    //         e.stopImmediatePropagation();
    //     })
    //     drag(element);
    // }, [drag])
    return (
        <TreeItem

            label={
                <Draggable draggableId={nodeId} index={index}>
                    {provided => (
                        <Box sx={{display: 'flex', alignItems: 'center', p: 0.5, pr: 0}}
                             {...provided.draggableProps}
                             {...provided.dragHandleProps}
                             ref={provided.innerRef}
                        >
                            <Box component={LabelIcon} color="inherrit" sx={{mr: 1}}/>
                            <Typography variant="body2" sx={{fontWeight: 'inherit', flexGrow: 1}}>
                                {labelText}
                            </Typography>
                            <Typography variant="caption" color="inherit">
                                {labelInfo}
                            </Typography>
                        </Box>
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