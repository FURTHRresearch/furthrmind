import classes from './MetricCardStyle.module.css';
import Avatar from '@mui/material/Avatar';

const MetricsCard = ({ avatarBgColor, title, subTitle, icon }) => {
        // const onlyWidth = useWindowWidth();
    return (
        <div className={classes.cardWrapper}>
            <div>
                <Avatar sx={{ bgcolor: avatarBgColor, height: "70px", width: "70px" }}>
                    {icon}
                </Avatar>
            </div>
            <div className={classes.cardTextWrapper}>
                <div className={classes.mainTextCss}>{title}</div>
                <div className={classes.subTextCss}>{subTitle}</div>
            </div>
        </div >
    )
}

export default MetricsCard;