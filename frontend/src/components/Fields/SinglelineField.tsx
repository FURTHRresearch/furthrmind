import { useUncontrolled } from '@mantine/hooks';
import TextField from '@mui/material/TextField';
import axios from 'axios';
import useDebouncedEffect from '../../hooks/useDebouncedEffect';
import FieldMenu from './FieldMenu';
import Tooltip from "@mui/material/Tooltip";

const SinglelineField = ({ value = null, initialValue, label, fieldDataId, onChange = (val) => null, validator = (val) => true, ...other }) => {
  // const [value, setValue] = useState(initialValue);
  const { writable } = other;
  const [_value, setValue] = useUncontrolled({
    value,
    defaultValue: initialValue,
    finalValue: '',
    rule: (val) => typeof val === 'string',
    onChange,
  });

  useDebouncedEffect(() => {
    axios.post('/web/fielddata/' + fieldDataId, { value: _value })
  }, 500, [_value]);

  return (
    <>
      <Tooltip title={label} placement={"left"} enterDelay={400} enterNextDelay={400}>
        <TextField
            error={!validator(_value)}
            label={label}
            variant="filled"
            value={_value}
            onChange={(e) => setValue(e.target.value)}
            fullWidth
            multiline
            disabled={!writable}
        />
      </Tooltip>

      {!other.menuDisabled && <FieldMenu fieldDataId={fieldDataId} label={label} {...other} />}
    </>
  )
}

export default SinglelineField;