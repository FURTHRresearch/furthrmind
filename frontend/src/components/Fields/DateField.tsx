import TextField from '@mui/material/TextField';
import axios from 'axios';
import {useState} from 'react';
import FieldMenu from './FieldMenu';
import Tooltip from "@mui/material/Tooltip";

const DateField = ({initialValue, label, fieldDataId, validator = (val) => true, ...other}) => {
    const [value, setValue] = useState(initialValue.replace(/:[\d.]+Z$/g, ""));
    const {writable} = other;
    const handleChange = (e) => {
        setValue(e.target.value);
        axios.post(`/web/fielddata/${fieldDataId}`, {value: e.target.value});
    }
    return (
        <>
            <Tooltip title={label} placement={"left"} enterDelay={400} enterNextDelay={400}>
                <TextField
                    error={!validator(value)}
                    onChange={handleChange}
                    disabled={!writable}
                    label={label}
                    type="datetime-local"
                    defaultValue={value}
                    fullWidth
                    variant='filled'
                    InputLabelProps={{
                        shrink: true,
                    }}
                />
            </Tooltip>

            {!other.menuDisabled && <FieldMenu {...other} fieldDataId={fieldDataId} label={label} writable={writable}/>}
        </>
    );
}

export default DateField;
