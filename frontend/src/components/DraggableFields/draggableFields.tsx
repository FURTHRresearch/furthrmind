import DragIndicatorIcon from "@mui/icons-material/DragIndicator";
import Button from "@mui/material/Button";
import React, {useRef, useState} from "react";
import {DragDropContext, Draggable, Droppable} from "react-beautiful-dnd";
import AutoField from "../Fields/AutoField";
import classes from "./style.module.css";

export default function DraggableFields(props) {
    const {updateFieldOnDragEnd, fields, autoExpanded = false} = props;
    const handleOnDragEnd = (result) => {
        updateFieldOnDragEnd(result, fields);
    };

    const [showAllFields, setShowAllFields] = useState(autoExpanded);
    const initialLength = useRef(fields.length).current;
    const expanded = showAllFields || fields.length > initialLength;
    return (
        <>
            <DragDropContext onDragEnd={handleOnDragEnd}>
                <Droppable droppableId="list">
                    {(provided) => (
                        <div ref={provided.innerRef} {...provided.droppableProps}>
                            {/* only re-render if the students array reference changes */}
                            <InnerList {...props} fields={expanded ? fields : fields.slice(0, 5)}/>
                            {provided.placeholder}
                        </div>
                    )}
                </Droppable>
            </DragDropContext>
            {(fields.length > 5 && !expanded) &&
                <Button fullWidth variant="text" onClick={() => setShowAllFields(true)}>Show all fields</Button>}
        </>
    );
}

const InnerList = (props) => {
    const {
        fields, isParent = false, parentID, parentType, writable, admin, controlled = false,
        onFieldValueChange = (id, val) => null, onFieldUnitChange = (id, val) => null
    } = props;
    const [mouseIn, setMouseIn] = useState(false);
    const [activeFieldID, setActiveFieldID] = useState("");
    const handleMouseIn = (fieldID) => {
        setActiveFieldID(fieldID);
        setMouseIn(true);
    };

    const handleMouseOut = () => {
        setActiveFieldID("");
        setMouseIn(false);
    };
    const getItemStyle = (isDragging, draggableStyle) => ({
        paddingLeft: isDragging ? "10px" : null,
        paddingBottom: isDragging ? "12px" : null,
        borderRadius: isDragging ? "4px" : null,
        boxShadow: isDragging ? "4px 5px 15px 0px rgb(0 0 0 / 40%)" : null,
        // styles we need to apply on draggables
        ...draggableStyle,
    });
    return (
        <React.Fragment>
            {fields.map((field, index) => (
                <Draggable key={field.id} draggableId={field.id} index={index} isDragDisabled={(!writable)}>
                    {(provided, snapshot) => (
                        <div
                            key={field.id}
                            ref={provided.innerRef}
                            {...provided.draggableProps}
                            {...provided.dragHandleProps}
                            className={`pt-2 ${classes.fieldWrapper}`}
                            style={getItemStyle(
                                snapshot.isDragging,
                                provided.draggableProps.style
                            )}
                            onMouseEnter={() => handleMouseIn(field.id)}
                            onMouseLeave={() => handleMouseOut()}
                        >
                            <DragIndicatorIcon className="mt-4"
                                               fontSize="small"
                                               style={{
                                                   opacity: mouseIn && activeFieldID === field.id ? 0.5 : 0.15,
                                                   marginLeft: "-17px",
                                                   position: 'relative',
                                                   top: "-10px"
                                               }}
                            />
                            <AutoField
                                key={`field_${field.id}`}
                                data={field}
                                parentId={parentID}
                                writable={writable}
                                admin={admin}
                                parentType={parentType}
                                controlled={controlled}
                                onChange={(val) => onFieldValueChange(field.id, val)}
                                onUnitChange={(val) => onFieldUnitChange(field.id, val)}
                            />


                        </div>
                    )}
                </Draggable>
            ))}
        </React.Fragment>
    );
};
