import {Button, Switch} from "@mui/material";
import CategoryIcon from "@mui/icons-material/Category";
import Popover from "@mui/material/Popover";
import Card from "@mui/material/Card";
import FormGroup from "@mui/material/FormGroup";
import FormControlLabel from "@mui/material/FormControlLabel";
import React, {useEffect, useState} from "react";
import useSWR from "swr";
import useFilterStore from "../../zustand/filterStore";
import {useParams} from "react-router-dom";
import hash from "stable-hash";

const fetcher = (url) => fetch(url).then((res) => res.json());

function DisplayedCategories(props) {

    const [anchorEl, setAnchorEl] = useState<HTMLButtonElement | null>(null);
    const [open, setOpen] = useState(false)
    const [categoryList, setCategoryList] = useState([
        {name: "Experiments", id: 1, show: true}, {name: "Samples", id: 2, show: true}
    ])
    const [allChecked, setAllChecked] = useState(true)
    const [wordingButton, setWordingButton] = useState("Categories: All")
    const [colorButton, setColorButton] = useState("primary")


    const displayedCategories = useFilterStore(
        (state) => state.displayedCategories
    )

    

    const setDisplayedCategories = useFilterStore(
        (state) => state.setDisplayedCategories
    )

    const params = useParams()

    const {
        data: categories,
        mutate: mutateResearchCategory
    } = useSWR('/web/projects/' + params.project + '/categories', fetcher);

    useEffect(() => {
        const cats = [...categoryList]
        if (categories) {
            categories.map((c) => {
                c.show = true
                cats.push(c)
            })
        }
        setCategoryList(cats)
    }, [categories]);

    useEffect(() => {
        console.log("displayedCategories", displayedCategories)
        if (categoryList.length > 0) {
            if (hash(displayedCategories) === hash(["all"])) {
                const catList = [...categoryList]
                catList.map((c) => {
                    c.show = true
                })
                setCategoryList(catList)
                setWordingButton("Categories: All")
                setColorButton("primary")
                setAllChecked(true)
            } else {
                const catList = [...categoryList]
                console.log("catList", catList)
                catList.map((c) => {
                    c.show = displayedCategories.includes(c.name)
                    console.log("c.show", c.show, c.name)
                })
                setCategoryList(catList)
                setWordingButton("Categories: Selected")
                setColorButton("error")
                setAllChecked(false)
            }
        }

    }, [displayedCategories]);

    function handleClose() {
        setAnchorEl(null);
        setOpen(false)
    }

    function handleSwitchChange(e) {
        const name = e.target.name;
        const checkedStatus = e.target.checked;

        const catList = categoryList.slice();
        if (name === "All") {
            catList.map((cat) => {
                cat.show = checkedStatus
                setAllChecked(checkedStatus)
            })
        } else {
            const indexToBeUpdated = catList.findIndex((cat) => cat.name === name);
            catList[indexToBeUpdated] = {
                ...catList[indexToBeUpdated],
                show: checkedStatus
            }
        }

        const catListTrue = []
        const all = catList.map((cat) => {
            if (cat.show === true) {
                catListTrue.push(cat.name)
            }
            return cat.show === true
        })
        const allTrue = all.every(value => value === true)

        setAllChecked(allTrue)
        setCategoryList(catList)
        if (allTrue === true) {
            setDisplayedCategories(["all"])
            setWordingButton("Categories: All")
            setColorButton("primary")
        } else {
            setDisplayedCategories(catListTrue)
            setWordingButton("Categories: Selected")
            setColorButton("error")
        }
    }

    const handleClick = (event: React.MouseEvent<HTMLButtonElement>) => {
        setAnchorEl(event.currentTarget);
        setOpen(true)
    };


    return (
        <>
            <Button
                sx={{
                    fontWeight: 600,
                    fontFamily: "Roboto",
                    padding: "6px 10px",
                    marginRight: "20px",
                }}
                variant="outlined"
                startIcon={<CategoryIcon/>}
                onClick={handleClick}
                color={colorButton}
            >
                {wordingButton}
            </Button>
            <Popover
                id={"diplayMenu"}
                open={open}
                anchorEl={anchorEl}
                onClose={handleClose}
                anchorOrigin={{
                    vertical: "bottom",
                    horizontal: "left"
                }}
            >
                <Card sx={{
                    padding: "12px",
                    maxHeight: '500px',
                    overflowY: "scroll"
                }}>
                    <FormGroup>
                        <FormControlLabel
                            control={<Switch
                                name={"All"}
                                checked={allChecked}
                                onChange={handleSwitchChange}/>}
                            label={"All"}/>
                        <hr/>
                        {categoryList.map((cat) =>
                            <FormControlLabel
                                control={<Switch
                                    name={cat.name}
                                    checked={cat.show}
                                    onChange={handleSwitchChange}/>}
                                label={cat.name}/>)}
                    </FormGroup>
                </Card>

            </Popover>
        </>
    )
}


export default DisplayedCategories;