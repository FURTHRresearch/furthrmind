import { Button, IconButton, Input, Switch, TextField } from "@mui/material";
import CategoryIcon from "@mui/icons-material/Category";
import Popover from "@mui/material/Popover";
import Card from "@mui/material/Card";
import FormGroup from "@mui/material/FormGroup";
import FormControlLabel from "@mui/material/FormControlLabel";
import React, { useEffect, useState } from "react";
import useFilterStore from "../../zustand/filterStore";
import ArrowForwardIcon from '@mui/icons-material/ArrowForward';
import { log } from "node:console";
import { debounce } from "lodash";
import useDebouncedEffect from "../../hooks/useDebouncedEffect";

function IncludeLinked() {

    const [anchorEl, setAnchorEl] = useState<HTMLButtonElement | null>(null);
    const [open, setOpen] = useState(false)
    const [wordingButton, setWordingButton] = useState("Linked Items: None")
    const [colorButton, setColorButton] = useState("primary")
    const [layerNumber, setLayerNumber] = useState(2)
    const [includeLinked, setIncludeLinked] = useState("none")

    function isValidInteger(value) {
        const parsed = parseInt(value, 10);
        return {isInt: !isNaN(parsed), layerNumber: parsed};
    }
    useEffect(() => {
        const {isInt, layerNumber} = isValidInteger(includeLinkedFilterStore);
        if (isInt === false) {
            setIncludeLinked(includeLinkedFilterStore)
        } else {
            setLayerNumber(layerNumber)
            setIncludeLinked("layer number")
        }

    }, [])

    const [options, setOptions] = useState([
        {
            name: "Direct",
            checked: false
        },
        {
            name: "All",
            checked: false
        },
        {
            name: "Set layer number",
            checked: false
        }
    ])

    const includeLinkedFilterStore = useFilterStore(
        (state) => state.includeLinked
    )

    const setIncludeLinkedFilterStore = useFilterStore(
        (state) => state.setIncludeLinked
    )


    function handleClose() {
        setAnchorEl(null);
        setOpen(false)
    }

    function handleSwitchChange(e) {
        const name = e.target.name;
        const checkedStatus = e.target.checked;
        if (checkedStatus) {
            if (name === "All") {
                setIncludeLinked("all")
            } else if (name === "Direct") {
                setIncludeLinked("direct")
            } else if (name === "Set layer number") {
                setIncludeLinked("layer number")
            }
        } else {
            setIncludeLinked("none")
        }

    }

    const handleClick = (event: React.MouseEvent<HTMLButtonElement>) => {
        setAnchorEl(event.currentTarget);
        setOpen(true)
    };


    useEffect(() => {
        console.log("IncludeLinked:", includeLinked)
        if (includeLinked === "all") {
            setWordingButton("Linked Items: All")
            options[0].checked = false  // disable direct
            options[1].checked = true  // enable all
            options[2].checked = false  // disable individually
            writeIncludeToFilterStore("all")
            setColorButton("error")

        } else if (includeLinked === "direct") {
            setWordingButton("Linked Items: Direct")
            options[1].checked = false  // disable all
            options[0].checked = true  // enable direct
            options[2].checked = false  // disable individually
            writeIncludeToFilterStore("direct")
            setColorButton("error")
        } else if (includeLinked === "layer number") {
            setWordingButton("Linked Items: Layer number: " + layerNumber)
            options[1].checked = false  // disable all
            options[0].checked = false  // disable direct
            options[2].checked = true  // enable individually
            writeIncludeToFilterStore(layerNumber)
            setColorButton("error")
        } else {
            setWordingButton("Linked Items: None")
            options[0].checked = false
            options[1].checked = false
            options[2].checked = false
            setColorButton("primary")
            writeIncludeToFilterStore("none")

        }
        setOptions(options)

    }, [includeLinked]);



    function writeIncludeToFilterStore(value) {
        if (includeLinkedFilterStore !== value) {
            setIncludeLinkedFilterStore(value)
        }
    }

    function setLayer(e) {
        setLayerNumber(parseInt(e.target.value))
        setWordingButton("Linked Items: Layer number: " + e.target.value)
    }

    useDebouncedEffect(() => {
        writeIncludeToFilterStore(layerNumber)
    }, 500, [layerNumber])

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
                startIcon={<CategoryIcon />}
                onClick={handleClick}
                color={colorButton}
            >
                {wordingButton}
            </Button>
            <Popover
                id={"linkedItems"}
                open={open}
                anchorEl={anchorEl}
                onClose={handleClose}
                anchorOrigin={{
                    vertical: "bottom",
                    horizontal: "left"
                }}
                style={{ overflowX: "hidden" }}
            >
                <Card sx={{
                    padding: "12px",
                    maxHeight: '500px',
                    overflowY: "scroll"
                }}>
                    <FormGroup>
                        {options.map((o) =>
                            <FormControlLabel
                                control={<Switch
                                    name={o.name}
                                    checked={o.checked}
                                    onChange={handleSwitchChange} />}
                                label={o.name} />)}
                    </FormGroup>
                    {(includeLinked === "layer number") && <div style={{
                        paddingTop: "10px", display: "flex", flexDirection: "row", justifyContent: "space-between",
                        margin: "auto"
                    }}>

                        <TextField
                            label={"Number of layer"}
                            variant="standard"
                            value={layerNumber}
                            onChange={(e) => setLayer(e)}
                            type="number"
                            fullWidth
                            inputProps={{ style: { textAlign: "center" } }}

                        // sx={{paddingRight: "10px"}}
                        />
                    </div>
                    }



                </Card>

            </Popover>
        </>
    )
}


export default IncludeLinked;