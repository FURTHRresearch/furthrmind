import AppsIcon from '@mui/icons-material/Apps';
import DashboardIcon from '@mui/icons-material/Dashboard';
import TimelineIcon from '@mui/icons-material/Timeline';
import HomeIcon from '@mui/icons-material/Home';
import ScienceIcon from '@mui/icons-material/Science';
import SettingsIcon from '@mui/icons-material/Settings';
import {Tooltip} from '@mui/material';
import Box from "@mui/material/Box";
import Divider from "@mui/material/Divider";
import MuiDrawer from "@mui/material/Drawer";
import IconButton from "@mui/material/IconButton";
import List from "@mui/material/List";
import ListItem from "@mui/material/ListItem";
import ListItemIcon from "@mui/material/ListItemIcon";
import {styled} from "@mui/material/styles";
import * as React from "react";
import {useNavigate, useParams} from "react-router";
import {NavLink as RouterLink} from 'react-router-dom';
import logo from '../images/FURTHRmind.png';

const drawerWidth = 240;

function ListItemLink(props) {
    const {icon, to, isDisabled, primary} = props;

    const renderLink = React.useMemo(
        () =>
            React.forwardRef(function Link(itemProps, ref) {
                return (
                    <RouterLink
                        end
                        to={to}
                        ref={ref}
                        {...itemProps}
                        role={undefined}
                        style={({isActive}) => {
                            return {
                                display: "flex",
                                alignItems: "center",
                                justifyContent: "center",
                                margin: "0px 0px 8px 0px",
                                background: isActive ? "#0C6EFD" : ""
                            };
                        }}
                    />
                );
            }),
        [to]
    );

    return (
        <li>
            <ListItem button component={renderLink} disabled={isDisabled} sx={{height: "50px"}}>
                <Tooltip title={primary} placement="right">
                    <ListItemIcon
                        style={{color: "white", display: "flex", alignItems: "center", justifyContent: "center"}}>
                        {icon}
                    </ListItemIcon>
                </Tooltip>
            </ListItem>
        </li>
    );
}

const openedMixin = (theme) => ({
    width: drawerWidth,
    transition: theme.transitions.create("width", {
        easing: theme.transitions.easing.sharp,
        duration: theme.transitions.duration.enteringScreen
    }),
    overflowX: "hidden"
});

const closedMixin = (theme) => ({
    transition: theme.transitions.create("width", {
        easing: theme.transitions.easing.sharp,
        duration: theme.transitions.duration.leavingScreen
    }),
    overflowX: "hidden",
    width: `calc(${theme.spacing(7)} + 1px)`,
    [theme.breakpoints.up("sm")]: {
        width: `calc(${theme.spacing(9)} + 1px)`
    }
});

const DrawerHeader = styled("div")(({theme}) => ({
    display: "flex",
    alignItems: "center",
    justifyContent: "flex-end",
    padding: theme.spacing(0, 1),
    // necessary for content to be below app bar
    ...theme.mixins.toolbar
}));


const Drawer = styled(MuiDrawer, {
    shouldForwardProp: (prop) => prop !== "open"
})(({theme, open}) => ({
    width: drawerWidth,
    flexShrink: 0,
    whiteSpace: "nowrap",
    boxSizing: "border-box",
    ...(open && {
        ...openedMixin(theme),
        "& .MuiDrawer-paper": openedMixin(theme)
    }),
    ...(!open && {
        ...closedMixin(theme),
        "& .MuiDrawer-paper": closedMixin(theme)
    })
}));

export default function SideDrawer() {
    const {project: projectID} = useParams();
    const navigate = useNavigate();
    return (
        <Box sx={{display: "flex"}}>
            <Drawer
                variant="permanent"
                open={false}
                sx={{
                    ".MuiDrawer-paper": {
                        background: "#212529"
                    }
                }}
            >
                <DrawerHeader>
                    <IconButton onClick={() => navigate("/")}>
                        <img src={logo} alt='' style={{
                            width: '50px', position: "relative",
                            left: "10px"
                        }}/>
                    </IconButton>
                </DrawerHeader>
                <Divider/>
                <List>
                    {/*<ListItemLink to={`/projects`} primary="Projects" icon={<HomeIcon fontSize="large"/>}/>*/}
                    <ListItemLink to={`/projects/${projectID}/data`} primary="Data browser"
                                  icon={<TimelineIcon fontSize="large"/>}/>
                    <ListItemLink to={`/projects/${projectID}/dashboard`} primary="Dashboard"
                                  icon={<DashboardIcon fontSize="large"/>}/>
                    <ListItemLink to={`/projects/${projectID}/apps`} primary="Apps"
                                  icon={<AppsIcon fontSize="large"/>}/>
                    <ListItemLink to={`/projects/${projectID}/settings`} primary="Settings" icon={<SettingsIcon/>}/>
                    {(process.env.NODE_ENV === "development") &&
                        <ListItemLink to={`/inventory`} primary="Inventory" icon={<ScienceIcon/>}/>}
                </List>
            </Drawer>

        </Box>
    );
}
