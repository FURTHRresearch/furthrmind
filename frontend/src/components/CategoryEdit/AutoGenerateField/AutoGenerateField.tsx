import {
    Grid,
    IconButton,
    Stack,
    Tooltip,
    Box,
    OutlinedInput,
    useMediaQuery,
} from "@mui/material";
import React, { useState, useEffect, useCallback } from "react";
import { useTheme } from "@mui/material/styles";
import CustomAutoComplete from "../AutoComplete/AutoComplete";
import AddCircleRoundedIcon from "@mui/icons-material/AddCircleRounded";
import RemoveCircleRoundedIcon from "@mui/icons-material/RemoveCircleRounded";
const operandList = [
    {
        title: "/",
    },
    {
        title: "*",
    },
    {
        title: "^",
    },
];
const AutoGenerateField = ({
    type,
    definitionList,
    addNewData,
    refresh,
    initValue,
    editData,
    editMode,
}) => {
    const theme = useTheme();
    const largeScreen = useMediaQuery(theme.breakpoints.up("md"));
    const [values, setValues] = useState(["r"]);
    const [data, setData] = useState({});

    const addNewOperand = () => {
        // this is to generate new field
        const imprintValues = values.slice();
        imprintValues.push("tt");
        setValues([...imprintValues]);
    };

    const updateNewlyAddedValue = (data) => {
        // when there is onChange event occur
        // we call this to update parent state
        if (Object.keys(data).length > 0) {
            let units = [];
            let isNew = false;
            for (const [key, value] of Object.entries(data)) {
                let valueToPush;
                if (Object(value).hasOwnProperty("exponent")) {
                    valueToPush =
                        value["title"] + "$" + (value["exponent"] ? value["exponent"] : 1);
                } else {
                    valueToPush = value["title"];
                }
                units.push(valueToPush);
                isNew = value["isNew"];
            }
            const dataToUpdate = units.join("_");
            addNewData({ title: dataToUpdate }, type, isNew);
        }
    };

    const isOperand = (_title) => {
        // if the string length is 1 we assume it is operand
        // we will write a regex here to validate that
        // based on that we will add exponent else not
        const operand = ["*", "^", "/"];
        return _title.length === 1 && operand.includes(_title);
    };

    const addNewDataHandler = (value, type, isNew) => {
        //to handle the case of nul when value get cleared
        const titleValue = value ? value.title : "";
        const dataImprint = { ...data };

        dataImprint[type] = {
            ...dataImprint[type],
            title: titleValue,
            isNew: isNew,
            ...(isOperand(titleValue) && {
                exponent: Object(dataImprint[type]).hasOwnProperty("exponent")
                    ? dataImprint[type]["exponent"]
                    : 1,
            }),

            // to make sure exponent is present every time
            // default value 1
        };
        setData({ ...dataImprint });
        updateNewlyAddedValue(dataImprint);
    };

    useEffect(() => {
        if (editMode) {
            let unitDef = editData[type].title;
            unitDef = unitDef.split("_");
            let resultObj = {};
            unitDef.forEach((unit, index) => {
                const typeOfInput = `${type}-${index}`;
                const [title, exponent] = unit.split("$");

                resultObj[typeOfInput] = {
                    title: title,
                    isNew: editData[type].isNew,
                    ...(isOperand(title) && { exponent: exponent }),
                };
            });
            setData({ ...resultObj });
            setValues([...unitDef]);
        }
    }, [editMode, editData]);

    const parseData = (_data) => {
        // parse the value in desrired form
        // to push to our parent handler
        let units = [];
        let isNew = false;
        for (const [key, value] of Object.entries(_data)) {
            let valueToPush;
            if (Object(value).hasOwnProperty("exponent")) {
                valueToPush =
                    value["title"] + "$" + (value["exponent"] ? value["exponent"] : "1");
            } else {
                valueToPush = value["title"];
            }
            units.push(valueToPush);
            isNew = value["isNew"];
        }
        const dataToUpdate = units.join("_");
        addNewData({ title: dataToUpdate }, type, isNew);
    };

    // to remove unit key and its associated value
    const removeUnitHandler = (index, typeL) => {
        let imprintValues = values.slice();
        imprintValues.splice(index, 1);

        setValues([...imprintValues]);

        const dataImprint = Object.assign({}, data);
        delete dataImprint[typeL];
        setData({ ...dataImprint });
        parseData(dataImprint);
    };

    // this handler is responsible for setting
    // exponent to respective unit
    const handleExponentChange = (e, type) => {
        const dataImprint = { ...data };
        dataImprint[type] = {
            ...dataImprint[type],
            exponent: e.target.value,
        };

        parseData(dataImprint);
        setData(dataImprint);
    };

    return (
        <Stack
            direction={largeScreen ? "row" : "column"}
            spacing={1}
            alignItems="flex-start"
        >
            {values.map((val, index) => {

                // typeOfInput is being used as a unique key
                // to store the value of AutoGenerateField

                const typeOfInput = `${type}-${index}`;
                return (
                    <Grid item md={4} xs={12}>
                        {/* not using this approach,i.e exponent at 
                        second position only as of now keeping it for future */}
                        {/* {(index + 1) % 2 !== 0 &&
                                <Stack direction='column' spacing={1}>
                                    <CustomAutoComplete
                                        list={index <= 0 ? definitionList : [...operandList, ...definitionList]}
                                        type={typeOfInput}
                                        addNewData={addNewDataHandler}
                                        refresh={refresh}
                                        label="definition"
                                        editData={data}
                                        editMode={editMode}
                                    />
                                    {index > 0 &&
                                        <Tooltip title='Remove unit and associate exponent'>
                                            <Box display='flex' alignItems='center' justifyContent='center'>
                                                <IconButton

                                                    sx={{ color: 'tomato' }}
                                                    onClick={() => removeUnitHandler(index, typeOfInput)}
                                                >
                                                    <RemoveCircleRoundedIcon />
                                                </IconButton>
                                            </Box>
                                        </Tooltip>
                                    }
                                </Stack>
                            } */}
                        {
                            <Stack direction="row" spacing={1}>
                                <Grid item md={8} xs={12}>
                                    <Stack direction="column" spacing={1}>
                                        <CustomAutoComplete
                                            list={
                                                index <= 0
                                                    ? definitionList
                                                    : [...operandList, ...definitionList]
                                            }
                                            type={typeOfInput}
                                            addNewData={addNewDataHandler}
                                            refresh={refresh}
                                            label="definition"
                                            editData={data}
                                            editMode={editMode}
                                        />

                                        {/* index >0 has been set explicity to avoid deletion of first input */}
                                        {index > 0 && (
                                            <Tooltip title="Remove unit and associate exponent">
                                                <Box
                                                    display="flex"
                                                    alignItems="center"
                                                    justifyContent="center"
                                                >
                                                    <IconButton
                                                        sx={{ color: "tomato" }}
                                                        onClick={() =>
                                                            removeUnitHandler(index, typeOfInput)
                                                        }
                                                    >
                                                        <RemoveCircleRoundedIcon />
                                                    </IconButton>
                                                </Box>
                                            </Tooltip>
                                        )}
                                    </Stack>
                                </Grid>
                                <Grid md={4} xs={12}>
                                    <OutlinedInput
                                        placeholder="exponent"
                                        label="exponent"
                                        type="number"
                                        notched={false}
                                        value={
                                            Object(data[typeOfInput]).hasOwnProperty("exponent")
                                                ? data[typeOfInput]["exponent"]
                                                : "1"
                                        }
                                        onChange={(e) => handleExponentChange(e, typeOfInput)}
                                    />
                                </Grid>
                            </Stack>
                        }
                    </Grid>
                );
            })}
            {/* To allow only 4 auto generate field */}
            {values.length <= 3 && (
                <Tooltip title="Add operand">
                    <IconButton
                        color="primary"
                        onClick={addNewOperand}
                        style={{ marginTop: "10px" }}
                    >
                        <AddCircleRoundedIcon />
                    </IconButton>
                </Tooltip>
            )}
        </Stack>
    );
};

export default AutoGenerateField;
