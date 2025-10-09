import React, {useCallback, useState} from 'react';

import ListIcon from '@mui/icons-material/List';
import {FormControl, InputLabel} from '@mui/material';
import MenuItem from '@mui/material/MenuItem';
import Select from '@mui/material/Select';
import ComboboxEditor from '../Overlays/ComboboxEditor';

import FieldMenu from './FieldMenu';

import {useUncontrolled} from '@mantine/hooks';
import axios from 'axios';
import {useInView} from 'react-intersection-observer';
import useSWR from 'swr';
import AddComboOption from '../Overlays/AddComboOption';
import ViewAuthorOverlay from '../Overlays/ViewAuthorOverlay';
import Divider from "@mui/material/Divider";
import Tooltip from "@mui/material/Tooltip";

const addNewText = 'Add new option';

const fetcher = url => fetch(url).then(res => res.json());

const ComboboxField = ({
                           initialValue,
                           value = null,
                           label,
                           fieldId,
                           dataId,
                           admin,
                           onChange = (val) => null,
                           validator = (val) => true,
                           ...other
                       }) => {
    // const [value, setValue] = React.useState(initialValue ? initialValue : "");
    const [_value, setValue] = useUncontrolled({
        value,
        defaultValue: initialValue,
        finalValue: "",
        rule: (val) => typeof val === 'string',
        onChange,
    });

    const [addNewComboModal, setAddNewComboModal] = useState(false);
    const [loading, setLoading] = useState(false);

    const {writable} = other;

    const {ref, inView} = useInView({});

    const {
        data: combos,
        mutate: mutateCombos
    } = useSWR('/web/comboboxentries/' + fieldId + '/entries', fetcher, {dedupingInterval: 10000});

    const valueChanged = (e: any) => {
        if (e.target.value === addNewText) {
            setAddNewComboModal(true);
        } else {
            setValue(e.target.value);
            axios.post('/web/fielddata/' + dataId, {value: e.target.value});
        }
    }
    const getCurrentValueLabel = useCallback(() => {
        if (!combos) return "";
        var option = combos.find(option => option.id === _value);
        return (option) ? option.name : '';
    }, [combos, _value]);

    // useEffect(() => {
    //   onChange(getCurrentValueLabel());
    // }, [getCurrentValueLabel, onChange]);

    const submitBtnHandler = (_value) => {
        if (_value) {
            setLoading(true);
            axios
                .post("/web/comboboxentries/" + fieldId + "/entries", {
                    name: _value
                })
                .then((r) => {
                    setLoading(false);
                    setAddNewComboModal(false);
                    let newCombos = combos.concat({id: r.data.id, name: _value});
                    setValue(r.data.id);
                    axios.post('/web/fielddata/' + dataId, {value: r.data.id})
                    mutateCombos(newCombos);
                }).catch((err) => {
                alert("This name is already in use. Please choose another name.");
                setAddNewComboModal(false);

            });
        }
    }

    const cancelBtnHandler = () => {
        setAddNewComboModal(false);
    }

    return (
        <>
            <Tooltip title={label} placement={"left"} enterDelay={400} enterNextDelay={400}>

                <div ref={ref} className="field">
                    <FormControl fullWidth error={!validator(_value)}>
                        <InputLabel variant="filled">
                            {label}
                        </InputLabel>
                        <Select
                            variant='filled'
                            value={_value}
                            disabled={!writable}
                            onChange={valueChanged}
                            native={true}
                        >
                            <option>--</option>
                            {(inView && combos) ? combos.map(option => <option key={option.id}
                                                                               value={option.id}>{option['name']}</option>) :
                                <option value={_value}>{getCurrentValueLabel()}</option>}
                            <option value={addNewText}>"Add new option"</option>
                        </Select>
                    </FormControl>
                </div>
            </Tooltip>


            {!other.menuDisabled && <ComboBoxMenu fieldId={fieldId} label={label} admin={admin} {...other} />}
            {addNewComboModal && <AddComboOption
                headingTitle='Add new option'
                description='This will create a new option'
                textFieldLabel='Option name'
                primaryBtnTextLabel='Submit'
                secondaryBtnTextLabel='Cancel'
                primaryBtnActionHandler={submitBtnHandler}
                secondaryBtnActionHandler={cancelBtnHandler}
                textFieldPlaceholder='Add new option'
                open={addNewComboModal}
                loading={loading}
                setOpen={setAddNewComboModal}
            />}
        </>
    )

}

export default ComboboxField;

const ComboBoxMenu = (props) => {
    const [showComboboxEditor, setShowComboboxEditor] = React.useState(false);
    const [viewAuthorOverlay, setViewAuthorOverlay] = React.useState(false);
    const closeViewAuthorOverlayHandler = () => {
        setViewAuthorOverlay(false);
    }
    return (
        <>
            <FieldMenu {...props} >
                <MenuItem onClick={() => {
                    setShowComboboxEditor(true);
                }}>
                    <span><ListIcon/> Edit entries</span>
                </MenuItem>
                <Divider/>
                {/*<MenuItem onClick={() => setViewAuthorOverlay(true)}>*/}
                {/*  <span><PersonIcon /> View Author</span>*/}
                {/*</MenuItem>*/}
            </FieldMenu>
            {showComboboxEditor && < ComboboxEditor
                show={showComboboxEditor}
                onClose={() => setShowComboboxEditor(false)}
                fieldId={props.fieldId}
                fieldName={props.label}
                admin={props.admin}
            />}
            {
                viewAuthorOverlay && <ViewAuthorOverlay open={viewAuthorOverlay}
                                                        onClose={closeViewAuthorOverlayHandler}/>

            }
        </>
    )
}
