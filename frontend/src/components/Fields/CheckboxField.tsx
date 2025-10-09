import {Checkbox, FormControlLabel, FormGroup} from '@mui/material';
import FieldMenu from './FieldMenu';

import axios from 'axios';

import {useUncontrolled} from '@mantine/hooks';
import Tooltip from "@mui/material/Tooltip";

const CheckboxField = ({initialValue, value = null, label, fieldDataId, onChange = (val) => null, ...other}) => {

    const {writable} = other;

    const [_value, setValue] = useUncontrolled({
        value,
        defaultValue: initialValue,
        finalValue: false,
        rule: (val) => typeof val === 'boolean',
        onChange,
    });


    const handleChanged = (e) => {
        setValue(e.target.checked);
        axios.post('/web/fielddata/' + fieldDataId, {value: e.target.checked});
    }

    return (
        <>
            <Tooltip title={label} placement={"left"} enterDelay={400} enterNextDelay={400}>
                <FormGroup sx={{width: "100%"}}>
                    <FormControlLabel
                        control={<Checkbox checked={_value} onChange={handleChanged} disabled={!writable}/>}
                        label={label}/>
                </FormGroup>
            </Tooltip>

            {!other.menuDisabled && <FieldMenu fieldDataId={fieldDataId} {...other} label={label}/>}
        </>
    )
}

export default CheckboxField;