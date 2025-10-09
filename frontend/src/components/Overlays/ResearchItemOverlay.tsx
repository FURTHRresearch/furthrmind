import ResearchItemCard from '../ResearchItemCard';

import Modal from '@mui/material/Modal';

const style = {
    position: 'absolute' as 'absolute',
    display: 'grid',
    gridTemplateColumns: '1fr 1fr 1fr',
    rowGap: '10px',
    columnGap: '10px',
    margin: "5% 8%",
    overflow: 'auto'

};

const ResearchItemOverlay = ({ group, project, show,
    onClose, onExited, data, groups, mutateGroups }) => {
    data.forEach(function (item, i) {
        if (!("group_id" in item)) {
            item.group_id = group.id
        }
    })

    return (
        <Modal open={show} onClose={onClose} disableAutoFocus={true} style={{ overflow: "auto" }}>
            <div style={style} onClick={() => onClose()}>
                {
                    data.map(({ id, type, group_id }) =>

                        <div style={{ width: "400px", marginBottom: "10px", maxHeight: "1200px", overflow: "auto" }}
                            onClick={(e) => {
                                e.stopPropagation()
                            }}>
                            <ResearchItemCard startInView={false} group={group}
                                project={project} itemId={id} type={type.toLowerCase()}
                                withCheckbox={false} groups={groups} mutateGroups={mutateGroups}
                            />
                        </div>
                    )
                }
            </div>
        </Modal>
    )

}

export default ResearchItemOverlay;