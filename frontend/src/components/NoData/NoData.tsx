import { Box, Stack, Button } from '@mui/material';
import NoDataImage from '../../images/prediction.svg';
import classes from './noDataStyle.module.css';
export default function NoData(props) {
    const { heading, subHeading, btnText = '', btnActionHandler, style = {}, btnComponent = null } = props;
    return (
        <div className={classes.parentWrapper} style={{ ...style }}>
            <Stack direction='column' alignItems='center' >
                <Box className={classes.imgWrapper} mt={2}>
                    <img src={NoDataImage} alt="no data" />
                </Box>
                <Box className={classes.heading} mt={5} ml={-4} >
                    {heading}
                </Box>
                <Box className={classes.subHeading} mt={2} mb={btnText === '' ? 3 : 0}>
                    {subHeading}
                </Box>
                {btnText !== '' && !btnComponent && <Box mt={3} ml={-4}>
                    <Button
                        variant='contained'
                        disableElevation
                        onClick={btnActionHandler}
                    >
                        {btnText}
                    </Button>
                </Box>
                }
                {
                    btnComponent && <Box ml={-4}>
                        {btnComponent}
                    </Box>
                }
            </Stack>
        </div>
    )
}