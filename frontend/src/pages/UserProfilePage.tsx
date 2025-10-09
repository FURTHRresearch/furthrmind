import CloudDoneOutlinedIcon from '@mui/icons-material/CloudDoneOutlined';
import GroupsOutlinedIcon from '@mui/icons-material/GroupsOutlined';
import MemoryOutlinedIcon from '@mui/icons-material/MemoryOutlined';
import ScienceOutlinedIcon from '@mui/icons-material/ScienceOutlined';
import { LoadingButton } from '@mui/lab';
import { Avatar, OutlinedInput } from "@mui/material";
import Uppy from '@uppy/core';
import '@uppy/core/dist/style.css';
import '@uppy/drag-drop/dist/style.css';
import '@uppy/progress-bar/dist/style.css';
import { DragDrop, ProgressBar, useUppy } from '@uppy/react';
import XHRUpload from '@uppy/xhr-upload';
import axios from 'axios';
import { format } from "date-fns";
import React, { useEffect, useState } from 'react';
import { useLocation } from 'react-router';
import useSWR from "swr";
import MetricsCard from "../components/Cards/MetricsCard";
import Header from "../components/Header/Header";
import AuthenticationDialog from '../components/Overlays/AuthenticationDialog';
import classes from "./UserProfileStyle.module.css";

import { useNavigate } from 'react-router';
import ApiPage from './ApiPage';


const fetcher = url => fetch(url).then(res => res.json());

const initData = {
  firstName: "",
  lastName: "",
  email: "",
  confirmEmail: "",
  password: "",
  confirmPassword: "",
  bio: "",
  initialized: false,
}
const EditProfile = () => {
  const [data, setData] = useState(initData);
  const [activeTab, setActiveTab] = useState('info');
  const [showValidateUserModal, setShowValidateUserModal] = useState(false);
  const { data: user, mutate: mutateUser } = useSWR("/web/user", fetcher);
  const [saving, setSaving] = useState(false);


  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    if (user && !data.initialized) {
      setData({
        ...data,
        firstName: user.firstName,
        lastName: user.lastName,
        email: user.email,
        confirmEmail: user.email,
        initialized: true,
      })
    }
  }, [user, data])

  const handleChange = (name, e) => {
    const { target: { value } } = e;
    setData(prev => {
      return {
        ...prev,
        [name]: value
      }
    })
  }

  const handleAuthConfirmed = (password) => {
    setShowValidateUserModal(false);
    let reqdata = {
      firstName: data.firstName,
      lastName: data.lastName,
      password
    }
    if (user.email !== data.email) reqdata['email'] = data.email;
    if (data.password) reqdata['newPassword'] = data.password;
    axios.post('/web/user', reqdata).then(r => {
      if (user.email !== data.email) alert('Please confirm your new email address. We have mailed you the instructions.')
      setSaving(false);
      mutateUser({ ...user, firstName: data.firstName, lastName: data.lastName });
    }).catch(e => {
      alert('Error saving profile');
      setSaving(false);
    })
  }

  const handleSubmit = () => {
    if (data.password || data.email !== user.email) {
      setSaving(true);
      setShowValidateUserModal(true);
    } else if (data.firstName !== user.firstName || data.lastName !== user.lastName) {
      setSaving(true);
      axios.post('/web/user', { firstName: data.firstName, lastName: data.lastName }).then(r => {
        setSaving(false);
        mutateUser({ ...user, firstName: data.firstName, lastName: data.lastName });
      });
    }
  }


  return (
    <React.Fragment>
      <div className={classes.titleText}>User Settings</div>
      <div className={classes.tabWrapper}>
        <div className={classes.tabs} onClick={() => navigate('/settings/profile')} style={{ color: location.pathname !== '/settings/profile' ? '#6F7A7D' : 'black', borderBottom: location.pathname !== '/settings/profile' ? 'none' : '1px solid #23a6f0' }}>
          User Info
        </div>
        <div className={classes.tabs} onClick={() => navigate('/settings/apikeys')} style={{ color: location.pathname !== '/settings/apikeys' ? '#6F7A7D' : 'black', borderBottom: location.pathname !== '/settings/apikeys' ? 'none' : '1px solid #23a6f0' }}>
          API Keys
        </div>
      </div>
      {location.pathname === '/settings/apikeys' ?
        <ApiPage /> :
        <div className={classes.boxWrapper}>
          <div className={classes.inputRowWrapper}>
            <div className={classes.inputWithLabel}>
              <label className={classes.labelText}>First name</label>
              <OutlinedInput id="outlined-basic"
                label="First name"
                notched={false}
                placeholder="First name"
                onChange={(e) => handleChange("firstName", e)}
                value={data.firstName}
                size="small" />
            </div>
            <div className={classes.inputWithLabel}>
              <label className={classes.labelText}>Last name</label>
              <OutlinedInput id="outlined-basic"
                notched={false}
                label='Last name'
                onChange={(e) => handleChange("lastName", e)}
                value={data.lastName}
                placeholder="Last name"
                size="small" />
            </div>
          </div>
          <div className={classes.inputRowWrapper}>
            <div className={classes.inputWithLabel}>
              <label className={classes.labelText}>Email</label>
              <OutlinedInput
                id="outlined-basic"
                label="Email"
                placeholder="Email"
                error={data.email !== data.confirmEmail}
                autoComplete="off"
                onChange={(e) => handleChange("email", e)}
                value={data.email}
                notched={false}
                size="small" />
            </div>
            <div className={classes.inputWithLabel}>
              <label className={classes.labelText}>Confirm email</label>
              <OutlinedInput
                id="outlined-basic"
                label="Confirm email"
                autoComplete="off"
                notched={false}
                onChange={(e) => handleChange("confirmEmail", e)}
                value={data.confirmEmail}
                error={data.email !== data.confirmEmail}
                placeholder="Confirm email"
                size="small" />
            </div>
          </div>
          <div className={classes.inputRowWrapper}>
            <div className={classes.inputWithLabel}>
              <label className={classes.labelText}>Password</label>
              <OutlinedInput
                label="New password"
                onChange={(e) => handleChange("password", e)}
                notched={false}
                placeholder="(unchanged)"
                error={data.password !== data.confirmPassword}
                autoComplete="new-password"
                type="password"
                size="small" />
            </div>
            <div className={classes.inputWithLabel}>
              <label className={classes.labelText}>Confirm password</label>
              <OutlinedInput id="outlined-basic"
                label="Confirm password"
                onChange={(e) => handleChange("confirmPassword", e)}
                notched={false}
                placeholder="(unchanged)"
                error={data.password !== data.confirmPassword}
                autoComplete="new-password"
                type="password"
                size="small" />
            </div>
          </div>
          {/* <div className={classes.bioWrapper}>
          <label className={classes.labelText}>Bio</label>
          <TextField id="outlined-basic" label="" variant="outlined" size="small"
            multiline
            InputLabelProps={{
              shrink: false
            }}
            onChange={(e) => handleChange("bio", e)}
            rows={4}
            maxRows={7} />
        </div> */}
          <div className={classes.updateInfoButtonWrapper}>
            <LoadingButton
              variant="contained"
              disableElevation
              loading={saving}
              disabled={data.password !== data.confirmPassword || data.email !== data.confirmEmail}
              sx={{ backgroundColor: "#23A6F0", paddingLeft: "50px", paddingRight: "50px" }}
              onClick={handleSubmit}
            >
              Update Info
            </LoadingButton>
          </div>
        </div>}
      {showValidateUserModal && <AuthenticationDialog callback={handleAuthConfirmed} open={showValidateUserModal} setOpen={setShowValidateUserModal} />}
    </React.Fragment>
  )
}

const ProfileDetails = () => {
  const { data: user, mutate: mutateUser } = useSWR("/web/user", fetcher);
  const avatarChangedref = React.useRef((rs) => null);
  avatarChangedref.current = React.useCallback((rs) => {
    mutateUser({ ...user, avatar: '/web/files/' + rs.response.body.fileId })
  }, [user, mutateUser])
  const uppy = useUppy(() => {
    return new Uppy({
      autoProceed: true,
    }).use(XHRUpload, {
      endpoint: '/web/user/avatar',
    }).on('complete', result => {
      result.successful.map(rs => avatarChangedref.current(rs))
    })
  });

  return (
    <div className={classes.profileDetailWrapper}>
      <div className={classes.profileInfoCard}>
        <div className={classes.userName}>{user && user.firstName} {user && user.lastName} </div>
        <div className={classes.userShortName}>{user && user.email} </div>
        <div className={classes.profileImageWrapper}>
          <Avatar
            sx={{ width: "120px", height: "120px" }}
            src={(user && user.avatar) ? user.avatar : ''}
          ></Avatar>
        </div>
        {/* <div className={classes.buttonWrapper}>
          <Button
            variant="contained"
            disableElevation
            sx={{ backgroundColor: "#23A6F0" }}
            endIcon={<FileUploadOutlinedIcon />}
          >
            Upload New Photo
          </Button>
        </div> */}
        {/* <div className={classes.uploadInfoWrapper}>
          <span>
            Upload a new avatar Large image will be resized automatically{" "}
          </span>
          <div className={classes.uploadInfoSubText}>
            Maxium upload size is
            <span className={classes.uploadInfoNumber}> 1MB</span>
          </div>
        </div> */}
        <div className={classes.uppyWrapper}>
          <DragDrop
            width="100%"
            locale={{
              strings: {
                dropHereOr: 'Drop a new avatar here or %{browse}',
                browse: 'browse',
              },
            }}
            uppy={uppy}
          />
          <ProgressBar
            uppy={uppy}
            fixed
            hideAfterFinish
          />
        </div>
        <div className={classes.joinedInfo}>
          Member Since <span className={classes.joinedDateCss}>{user && format(new Date(user.memberSince), 'dd. MMMM, yyyy')}</span>
        </div>
      </div>
      <div className={classes.profileEditInfoCard}>
        <EditProfile />
      </div>
    </div>
  );
};

const Metrics = () => {
  return (
    <div className={classes.metricWrapper}>
      <MetricsCard
        avatarBgColor={"#E65B8D"}
        icon={<MemoryOutlinedIcon sx={{ fontSize: "30px" }} />}
        title="2 GB"
        subTitle="Available Storage"
      />
      <MetricsCard
        avatarBgColor={"#53B781"}
        icon={<ScienceOutlinedIcon sx={{ fontSize: "30px" }} />}
        title="01 +"
        subTitle="Research Items"
      />
      <MetricsCard
        avatarBgColor={"#5B68DC"}
        icon={<GroupsOutlinedIcon sx={{ fontSize: "30px" }} />}
        title="00 +"
        subTitle="Collaborators "
      />
      <MetricsCard
        avatarBgColor={"#E91E62"}
        icon={<CloudDoneOutlinedIcon sx={{ fontSize: "30px" }} />}
        title="00 MB"
        subTitle="Storage Used"
      />
    </div>
  );
};
const UserProfilePage = () => {
  return (
    <div className={classes.pageStyle}>
      <Header />
      <div className={classes.pageInnerWrapper}>
        <div className={classes.profileWrapper}>
          <ProfileDetails />
          {/* <Metrics /> */}
        </div>
      </div>
    </div>
  );
};

export default UserProfilePage;


