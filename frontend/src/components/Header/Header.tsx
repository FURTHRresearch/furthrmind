import AdminPanelSettingsIcon from '@mui/icons-material/AdminPanelSettings';
import Logout from '@mui/icons-material/Logout';
import MenuIcon from "@mui/icons-material/Menu";
import Settings from '@mui/icons-material/Settings';
import { Avatar } from "@mui/material";
import Box from '@mui/material/Box';
import Divider from '@mui/material/Divider';
import IconButton from '@mui/material/IconButton';
import ListItemIcon from '@mui/material/ListItemIcon';
import Menu from '@mui/material/Menu';
import MenuItem from '@mui/material/MenuItem';
import Tooltip from '@mui/material/Tooltip';
import React, { useState } from "react";
import { NavLink, useNavigate } from "react-router-dom";
import WhatsNewOverlay from '../Overlays/WhatsNewOverlay';
import MobileMenuHeader from './MobileHeader';
import classes from "./style.module.css";

import useSWR from "swr";

const fetcher = url => fetch(url).then(res => res.json());

export default function Header() {
  const navigate = useNavigate()
  const [showMobileMenu, setShowMobileMenu] = useState(false);
  const [showWhatsNew, setShowWhatsNew] = useState(false);

  const { data: user } = useSWR("/web/user", fetcher);

  const [accountMenuAnchor, setAccountMenuAnchor] = React.useState(null);

  const handleMobileHandler = () => {
    setShowMobileMenu(true);
  }

  return (
    <div className={classes.headerWrap}>
      <div className={classes.brandArea}>
        <div className={classes.sideBarMenuIcon}>
          <MenuIcon onClick={handleMobileHandler} />
        </div>
        <div className={classes.logoTitle}
          onClick={() => navigate("/")}
        >FURTHRmind</div>
      </div>

      <div />
      <Box sx={{ display: 'flex', alignItems: 'center', textAlign: 'center', columnGap: '28px', justifyContent: 'flex-end' }}>
        <div className={classes.menuWrapper}>
          <a href="https://furthrmind.com/docs" className={classes.menuItem} target="_blank" rel="noopener noreferrer">
            Documentation
          </a>
          <span className={classes.menuItem} onClick={() => setShowWhatsNew(true)}>
            What's new?
          </span>
        </div>
        <Tooltip title="Account settings">
          <IconButton onClick={(event) => setAccountMenuAnchor(event.currentTarget)}>
            <Avatar
              sx={{
                width: 25,
                height: 25,
                fontSize: "14px",
              }}
              src={user?.avatar}
            >
              {user?.email?.charAt(0).toUpperCase()}
            </Avatar>
          </IconButton>
        </Tooltip>
      </Box>
      <Menu
        anchorEl={accountMenuAnchor}
        id="account-menu"
        open={Boolean(accountMenuAnchor)}
        onClose={() => setAccountMenuAnchor(null)}
        onClick={() => setAccountMenuAnchor(null)}
        PaperProps={{
          elevation: 0,
          sx: {
            overflow: 'visible',
            filter: 'drop-shadow(0px 2px 8px rgba(0,0,0,0.32))',
            mt: 1.5,
            '& .MuiAvatar-root': {
              width: 32,
              height: 32,
              ml: -0.5,
              mr: 1,
            },
            '&:before': {
              content: '""',
              display: 'block',
              position: 'absolute',
              top: 0,
              right: 14,
              width: 10,
              height: 10,
              bgcolor: 'background.paper',
              transform: 'translateY(-50%) rotate(45deg)',
              zIndex: 0,
            },
          },
        }}
        transformOrigin={{ horizontal: 'right', vertical: 'top' }}
        anchorOrigin={{ horizontal: 'right', vertical: 'bottom' }}
      >
        <MenuItem>
          {user?.email}
        </MenuItem>
        <Divider />
        {user?.admin && <NavLink to={'/admin'} style={{ textDecoration: 'none', color: '#000' }}>
          <MenuItem>
            <ListItemIcon>
              <AdminPanelSettingsIcon fontSize="small" />
            </ListItemIcon>
            Admin Settings
          </MenuItem>
        </NavLink>}
        <NavLink to={'/settings/profile'} style={{ textDecoration: 'none', color: '#000' }}>
          <MenuItem>
            <ListItemIcon>
              <Settings fontSize="small" />
            </ListItemIcon>
            User Settings
          </MenuItem>
        </NavLink>
        <MenuItem onClick={() => window.location.href = "/logout"}>
          <ListItemIcon>
            <Logout fontSize="small" />
          </ListItemIcon>
          Logout
        </MenuItem>
      </Menu>
      <MobileMenuHeader open={showMobileMenu} setOpen={setShowMobileMenu} />
      <WhatsNewOverlay open={showWhatsNew} handleClose={() => setShowWhatsNew(false)} />
    </div>
  );
}
