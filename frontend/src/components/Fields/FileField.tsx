import { useUncontrolled } from '@mantine/hooks';
import { Box, Paper, Stack } from '@mui/material';
import axios from 'axios';
import useSWR from 'swr';
import FileCard from '../FileCard';
import FileUploadButton from '../UploadButton/FileUploadButton';
import classes from './DataCalcFieldStyle.module.css';
import FieldMenu from './FieldMenu';

const fetcher = (url) => fetch(url).then((res) => res.json());

export default function ({ value = null, initialValue = '', label, fieldDataId, onChange = (val) => null, validator = (val) => true, ...other }) {

    const [_value, setValue] = useUncontrolled({
        value,
        defaultValue: initialValue,
        finalValue: '',
        rule: (val) => typeof val === 'string',
        onChange,
    });

    const handleUploaded = (uuids) => {
        axios.post(`/web/files`, { uuid: uuids[0] }).then(res => {
            setValue(res.data.id);
            axios.post('/web/fielddata/' + fieldDataId, { value: res.data.id });
        })
    }

    const { data: fileData } = useSWR(_value.length > 8 ? `/web/files/${_value}/data` : null, fetcher);

    return (
        <>
            <div className={classes.parentWrapper} style={{ border: validator(_value) ? '' : '2px solid red' }}>
                <Stack direction="row" spacing={2} alignItems="center" justifyContent='space-between'>
                    <div className={classes.labelCss}>{label}</div>
                    <FileUploadButton onUploaded={handleUploaded} />
                </Stack>
                {fileData && <Paper
                    elevation={0}
                    sx={{
                        padding: '8px 12px',
                        margin: '8px 0px'
                    }}
                >
                    <Box>
                        <FileCard fileName={fileData.name} fileExtension={fileData.name.split('.').pop()} file={fileData} />
                    </Box>
                </Paper>}
            </div>
            {!other.menuDisabled && <FieldMenu label={label} {...other} />}
        </>
    )
}