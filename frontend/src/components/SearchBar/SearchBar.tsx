
import ClearIcon from "@mui/icons-material/Clear";
import SearchIcon from "@mui/icons-material/Search";
import { Button } from "@mui/material";
import Skeleton from '@mui/material/Skeleton';
import {
    useWindowWidth
} from '@react-hook/window-size';
import React from "react";
import classes from "./style.module.css";
const SearchBar = ({
    searchActivated,
    setSearchActivated,
    handleChange,
    searchInput,
    withButton = false,
    buttonText = '',
    buttonClickHandler = () => null,
    buttonIcon = null,
    isLoading,
    btnDisabled = false,
    onSearch = (text) => null
}) => {
    const onlyWidth = useWindowWidth()
    const clearSearchInput = () => {
        handleChange("");
        onSearch("");
    };

    const handleBlur = () => {
        //to make sure on close click happen (just a hack)
        setTimeout(() => {
            setSearchActivated(false);
        }, 100);
    };

    return (
        <div className={classes.searchBarWrapper}>
            {isLoading &&
                <React.Fragment>
                    <Skeleton variant="rectangular"
                        animation="wave"
                        style={{ margin: "20px 0px" }}
                        width={150} height={30}>
                    </Skeleton>
                    <Skeleton
                        animation="wave"
                        variant="rectangular"
                        width={150} height={30}></Skeleton>
                </React.Fragment>
            }
            {!isLoading && <React.Fragment>
                <div
                    className={classes.searchBarInputWrapper}
                    style={{ width: searchActivated ? "100%" : null }}
                >
                    <input
                        type="text"
                        onFocus={() => setSearchActivated(true)}
                        onBlur={handleBlur}
                        onChange={(e) => handleChange(e.target.value)}
                        className={[classes.searchInput].join("")}
                        value={searchInput}
                        placeholder={onlyWidth < 576 ? "" : "Search"}
                        onKeyDown={(e) => (e.key === 'Enter') ? onSearch(searchInput) : null}
                    />
                    <SearchIcon className={classes.searchIcon} sx={{ color: "#737373" }}
                        onClick={() => setSearchActivated(true)} />
                    {searchInput.length > 0 && (
                        <ClearIcon className={classes.clearIcon} onClick={clearSearchInput} />
                    )}
                </div>
                {!searchActivated && withButton && (
                    <Button
                        disableElevation
                        disabled={btnDisabled}
                        sx={{
                            fontWeight: 600,
                            fontFamily: "Roboto",
                            padding: "6px 10px",
                        }}
                        variant="contained"
                        onClick={buttonClickHandler}
                        startIcon={buttonIcon}
                    >
                        {buttonText}
                    </Button>
                )}
            </React.Fragment>}

        </div>
    );
};

export default SearchBar;
