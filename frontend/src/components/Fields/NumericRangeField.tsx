import React, {useEffect, useMemo} from 'react';

import {useInView} from 'react-intersection-observer';

import NumbersIcon from '@mui/icons-material/Numbers';

import Select from '@mui/material/Select';
import UnitEditor from '../Overlays/UnitEditor';

import TextField from '@mui/material/TextField';
import FieldMenu from './FieldMenu';

import MenuItem from '@mui/material/MenuItem';


import './Field.css';
import axios from 'axios';
import {useParams} from 'react-router-dom';
import useSWR from 'swr';
import useDebouncedEffect from '../../hooks/useDebouncedEffect';
import Divider from "@mui/material/Divider";
import Tooltip from "@mui/material/Tooltip";
import {Typography} from "@mui/material";

const fetcher = url => fetch(url).then(res => res.json());

function groupBy(xs, key) {
    return xs.reduce(function (rv, x) {
        (rv[x[key]] = rv[x[key]] || []).push(x);
        return rv;
    }, {});
}

const NumericRangeField = ({
                               fieldDataId,
                               initialValue,
                               value = null,
                               onChange,
                               label,
                               initialUnitId,
                               unitId = null,
                               onUnitChange,
                               validator = (val) => true,
                               ...other
                           }) => {
    const [_value, setValue] = React.useState(initialValue);

    // const [_value, setValue] = useUncontrolled({
    //     value: value,
    //     defaultValue: initialValue,
    //     finalValue: null,
    //     rule: (val) => typeof val === 'string' || typeof val === 'number',
    //     onChange: onChange,
    // });


    const [_unitId, setUnitId] = React.useState(initialUnitId);
    // const [_unitId, setUnitId] = useUncontrolled({
    //     value: unitId,
    //     defaultValue: initialUnitId,
    //     finalValue: '',
    //     rule: (val) => typeof val === 'string',
    //     onChange: onUnitChange,
    // });

    const {writable} = other;

    const {inView, ref} = useInView({});

    const params = useParams();
    const {data: units} = useSWR(`/web/units?project=${'project' in params ? params.project : ''}`, fetcher, {dedupingInterval: 10000});
    const groups = useMemo(() => units ? groupBy(units, 'category') : [], [units])
    const getUnitName = (unitId: string) => {
        if (!units) return '';
        var unit = units.find(unit => unit.id === unitId);
        return (unit) ? unit.Name : '';
    }

    useDebouncedEffect(() => {
        axios.post('/web/fielddata/' + fieldDataId, {value: _value, unitId: _unitId}).then(
            onChange(_value)
        );
    }, 500, [_value]);

    useDebouncedEffect(() => {
        axios.post('/web/fielddata/' + fieldDataId, {value: _value, unitId: _unitId}).then(
            onUnitChange(_unitId)
        );
    }, 500, [_unitId]);

    return (
        <>
            <div ref={ref} className="field">
                <Tooltip title={label} placement={"left"} enterDelay={400} enterNextDelay={400}>
                    <div style={{display: "flex", justifyContent: "center"}}>
                        <div style={{width: "70%", display: "flex"}}>
                            <div style={{width: "45%"}}>
                                <NumericTextField validator={validator}
                                                  _value={_value} writable={writable}
                                                  label={label} setValue={setValue}
                                                  position={0}/>
                            </div>

                            <div style={{alignContent: "center", marginLeft: "auto", marginRight: "auto"}}>
                                <Typography variant={"h6"}>-</Typography>
                            </div>

                            <div style={{width: "45%"}}>
                                <NumericTextField validator={validator}
                                                  _value={_value} writable={writable}
                                                  label={label} setValue={setValue}
                                                  position={1}/>
                            </div>
                        </div>

                        <Select
                            value={_unitId}
                            onChange={(e) => setUnitId(e.target.value)}
                            native={true}
                            variant="filled"
                            disabled={!writable}
                            style={{width: "30%", marginLeft: "10px"}}
                        >
                            <option value=''> -</option>
                            {(inView && units)
                                ? Object.keys(groups).map((category) =>
                                    <optgroup label={category}>
                                        {groups[category].map((unit) => <option
                                            key={unit.id} value={unit.id}>{unit.Name}</option>)}
                                    </optgroup>)
                                : <option value={_unitId}>{getUnitName(_unitId)}</option>
                            }
                        </Select>
                    </div>
                    {/*<Stack direction="row" spacing={1}>*/}
                    {/*    <TextField*/}
                    {/*        error={!validator(_value)}*/}
                    {/*        disabled={!writable}*/}
                    {/*        label={label}*/}
                    {/*        variant="filled"*/}
                    {/*        value={_value}*/}
                    {/*        onChange={(e) => setValue(e.target.value)}*/}
                    {/*        type="number"*/}
                    {/*        fullWidth*/}
                    {/*    />*/}

                    {/*    <Select*/}
                    {/*        value={_unitId}*/}
                    {/*        onChange={(e) => setUnitId(e.target.value)}*/}
                    {/*        native={true}*/}
                    {/*        variant="filled"*/}
                    {/*        disabled={!writable}*/}
                    {/*        fullWidth*/}
                    {/*    >*/}
                    {/*        <option value=''> -</option>*/}
                    {/*        {(inView && units)*/}
                    {/*            ? Object.keys(groups).map((category) =>*/}
                    {/*                <optgroup label={category}>*/}
                    {/*                    {groups[category].map((unit) => <option value={unit.id}>{unit.Name}</option>)}*/}
                    {/*                </optgroup>)*/}
                    {/*            : <option value={_unitId}>{getUnitName(_unitId)}</option>*/}
                    {/*        }*/}
                    {/*    </Select>*/}
                    {/*</Stack>*/}
                </Tooltip>

            </div>
            {
                !other.menuDisabled && <NumericRangeMenu label={label} {...other} fieldDataId={fieldDataId}/>
            }
        </>
    )

}

export default NumericRangeField;

const NumericRangeMenu = (props) => {
    const [showUnitEditor, setShowUnitEditor] = React.useState(false);


    return (
        <>
            <FieldMenu {...props} >

                <MenuItem onClick={() => {
                    setShowUnitEditor(true);
                }} disabled={!props.admin}>
                    <span><NumbersIcon/> Edit units</span>
                </MenuItem>
                <Divider/>
            </FieldMenu>
            {showUnitEditor && <UnitEditor show={showUnitEditor} onClose={() => setShowUnitEditor(false)}/>}

        </>
    )
}

const NumericTextField = ({validator, _value, writable, label, setValue, position}) => {
    function onValueChange(val) {
        let value = [..._value]
        value[position] = val
        setValue(value)
    }

    const [_label, setLabel] = React.useState("")

    useEffect(() => {
        if (position === 0) {
            setLabel(`${label} min`)
        } else if (position === 1) {
            setLabel(`${label} max`)
        }
    }, [label, position]);

    return (
        <TextField
            error={!validator(_value[position])}
            disabled={!writable}
            label={_label}
            variant="filled"
            value={_value[position]}
            onChange={(e) => onValueChange(e.target.value)}
            type="number"
            fullWidth
            // sx={{paddingRight: "10px"}}
            onWheel={event => event.target.blur()}
            // InputLabelProps={{
            //     sx: {
            //         fontSize: "12px",
            //     }
            // }}
        />
    )

}
