import AddIcon from "@mui/icons-material/Add";
import {useState} from "react";
import {useParams} from "react-router";
import useSWR from "swr";

import AppCard from "../components/Cards/AppCard";
import SearchBar from "../components/SearchBar/SearchBar";
import SideDrawer from "../components/SideDrawer";
import classes from "./AppPageStyle.module.css";
import axios from "axios";

const fetcher = (url) => fetch(url).then((res) => res.json());

export default function AppPage() {
    const params = useParams();
    const [searchActivated, setSearchActivated] = useState(false);
    const [searchInput, setSearchInput] = useState("");

    const handleChange = (val) => {
        setSearchInput(val);
    };

    const {data: apps} = useSWR(`/web/projects/${params.project}/apps`, fetcher);
    return (
        <div className={classes.pageStyle}>
            <SideDrawer
            />
            <div className={classes.pageInnerWrapper}>
                <SearchBar
                    searchActivated={searchActivated}
                    setSearchActivated={setSearchActivated}
                    handleChange={handleChange}
                    searchInput={searchInput}
                    isLoading={false}
                    withButton={false}
                    buttonText=""
                    buttonClickHandler={() => null}
                    buttonIcon={<AddIcon/>}
                />
                <div className={classes.appCardOuterWrapper}>
                    {apps ? apps.map(option => <AppCard key={option.name} data={option}/>
                    ) : <>Loading ....</>}
                </div>
            </div>
        </div>
    );
}


