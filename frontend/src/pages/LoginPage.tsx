import AlternateEmailIcon from "@mui/icons-material/AlternateEmail";
import LockIcon from "@mui/icons-material/Lock";
import {
    FormControl, InputAdornment, OutlinedInput
} from "@mui/material";
import { useEffect, useState } from "react";

import axios from "axios";
import { useNavigate } from "react-router";

import { LoadingButton } from "@mui/lab";
import { NavLink, useLocation } from "react-router-dom";
import ResetPasswordDialog from "../components/Overlays/ResetPasswordDialog";
import SetPasswordDialog from "../components/Overlays/SetPasswordDialog";
import Logo from "../images/FURTHRmind.png";
import classes from "./loginPageStyle.module.css";

import { useWindowWidth } from "@react-hook/window-size";
import useSWR from "swr";
import SignUpOverlay from "../components/Overlays/SignUpOverlay";

const fetcher = (url) => fetch(url).then((res) => res.json());

export default function LoginPage() {
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [invalidEmail, setInvalidEmail] = useState(false);
    const [loading, setLoading] = useState(false);
    const [showSignUp, setShowSignUp] = useState(false);
    const location = useLocation();
    const onlyWidth = useWindowWidth();
    const navigate = useNavigate();
    const [usernameText, setUsernameText] = useState("");



    const isValidEmail = (recipient) => {
        const regex = /^[\w._-]+[+]?[\w._-]+@[\w.-]+\.[a-zA-Z]{2,6}$/;
        return regex.test(recipient);
    }

    const { data: loginState, mutate: mutateLoginState } = useSWR(`/web/isloggedin`, fetcher);

    useEffect(() => {
        fetch(`/web/welcome-username-text`).then(res => res.text()).then(setUsernameText);
    }, []);

    const handleLogin = () => {

        setLoading(true);
        axios.post('/web/login', { email, password }).then(res => {
            mutateLoginState({ isLoggedIn: true });
            navigate("/");
        }).catch(err => {
            alert('Invalid email or password');
            setLoading(false);
        });

        // if (isValidEmail(email)) {
        //     setLoading(true);
        //     axios.post('/web/login', { email, password }).then(res => {
        //         mutateLoginState({ isLoggedIn: true });
        //         navigate("/");
        //     }).catch(err => {
        //         alert('Invalid email or password');
        //         setLoading(false);
        //     });
        // } else {
        //     setInvalidEmail(true);
        // }
    }


    return (
        <div className={classes.parentWrapper}>
            <div className={classes.leftPanelWrapper}>
                <div className={classes.leftPanelTextWrapper}>
                    <div>
                        <img src={Logo} className={classes.logoCss} alt="logo" />
                    </div>
                    <div className={classes.loginWrapper}>
                        <div className={classes.welcomeCss}>Welcome to FURTHRmind</div>
                        <FormControl
                            size={onlyWidth <= 1440 ? "small" : "medium"}
                            fullWidth sx={{ marginTop: "40px", minWidth: "300px" }}>
                            <OutlinedInput
                                id="outlined-adornment-amount"
                                value={email}
                                error={invalidEmail}
                                onChange={(e) => setEmail(e.target.value)}
                                notched={false}
                                placeholder={usernameText}
                                endAdornment={
                                    <InputAdornment position="end">
                                        <AlternateEmailIcon style={{ color: "#DCDCDC" }} />
                                    </InputAdornment>
                                }
                                label="Email"
                            />
                        </FormControl>
                        <FormControl
                            size={onlyWidth <= 1440 ? "small" : "medium"}
                            fullWidth sx={{ marginTop: "20px", minWidth: "300px" }}>
                            <OutlinedInput
                                id="outlined-adornment-amount"
                                type="password"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                notched={false}
                                placeholder="6+ strong character"
                                onKeyDown={(e) => (e.key === 'Enter') ? handleLogin() : null}
                                endAdornment={
                                    <InputAdornment position="end">
                                        <LockIcon style={{ color: "#DCDCDC" }} />
                                    </InputAdornment>
                                }
                                label="Password"
                            />
                        </FormControl>
                        <LoadingButton
                            variant="contained"
                            // size="medium"
                            sx={{
                                background: "#0171F8",
                                borderRadius: "4px",
                                marginTop: "30px",
                                height: onlyWidth <= 1440 ? "40px" : "50px"
                            }}
                            disableElevation
                            fullWidth
                            onClick={handleLogin}
                            loading={loading}
                        >
                            Login
                        </LoadingButton>
                        <div className={classes.footerActionButtonCss}>
                            <NavLink to="/signup" style={{ fontFamily: "Open sans" }}>
                                Sign up
                            </NavLink>
                            <NavLink
                                to="/password-reset"
                                style={{ color: "black", fontFamily: "Open sans" }}
                            >
                                Reset password
                            </NavLink>
                        </div>
                    </div>
                </div>
            </div>
            <div className={classes.rightPanelWrapper}>
                <div className={classes.textAreaCss}>
                    <div className={classes.subHeadingCss}>
                        Making Data Handling In Research
                    </div>
                    <div className={classes.heading}>
                        <span className={classes.headingText}>Simple</span>
                        <span className={classes.headingText}>Reliable &</span>
                        <span className={classes.headingText}>Transparent</span>
                    </div>
                </div>
                <div className={classes.loginVectorCss}>
                    {/* <img
                        src={LoginVector}
                        className={classes.loginVectorImage}
                        alt="login vector images"
                    /> */}
                </div>
            </div>
            <SignUpOverlay open={location.pathname === '/signup'} handleClose={() => navigate('/login')} />
            <SetPasswordDialog open={location.pathname === '/set-password'} handleClose={() => navigate('/login')} />
            <ResetPasswordDialog open={location.pathname === '/password-reset'} handleClose={() => navigate('/login')} />
        </div >
    );
}