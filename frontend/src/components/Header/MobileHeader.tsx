import CloseOutlinedIcon from '@mui/icons-material/CloseOutlined';
import Divider from '@mui/material/Divider';
import SwipeableDrawer from '@mui/material/SwipeableDrawer';
import { NavLink, useNavigate } from 'react-router-dom';
import classes from './MobileHeaderStyle.module.css';

const anchor = "left";

export default function SwipeableTemporaryDrawer({ open, setOpen }) {

    const navigate = useNavigate();

    const toggleDrawer = (value) => {
        setOpen(value)
    }

    const list = (anchor) => (
        <div className={classes.sideBarWrapper}>
            <div className={classes.closeArea}>
                <div className={classes.logoTitle}
                    onClick={() => navigate("/")}
                >FURTHRmind</div>
                <div className={classes.closeBtn}>
                    <CloseOutlinedIcon
                        onClick={() => toggleDrawer(false)} />
                </div>
            </div>
            <Divider />
            <div className={classes.linkArea}>
                <NavLink
                    className={({ isActive }) =>
                        isActive ? classes.menuItemActive : classes.menuItem
                    }
                    to="/projects"
                >
                    Projects
                </NavLink>
                {(process.env.NODE_ENV === "development") && (
                    <NavLink
                        className={({ isActive }) =>
                            isActive ? classes.menuItemActive : classes.menuItem
                        }
                        to="/inventory"
                    >
                        Inventory
                    </NavLink>
                )}
            </div>
        </div>

    );

    return (

        <SwipeableDrawer
            anchor={anchor}
            open={open}
            onClose={() => toggleDrawer(false)}
            onOpen={() => toggleDrawer(true)}
        >
            {list(anchor)}
        </SwipeableDrawer>

    );
}
