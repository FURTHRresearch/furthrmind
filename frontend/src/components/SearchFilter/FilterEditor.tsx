import CheckBoxIcon from '@mui/icons-material/CheckBox';
import CheckBoxOutlineBlankIcon from '@mui/icons-material/CheckBoxOutlineBlank';
import {FormControl, InputLabel, MenuItem, Stack, TextField} from '@mui/material';
import Autocomplete from '@mui/material/Autocomplete';
import Button from "@mui/material/Button";
import Checkbox from '@mui/material/Checkbox';
import Select from "@mui/material/Select";
import React, {useCallback, useEffect, useMemo, useState} from "react";
import {useParams} from "react-router-dom";
import useSWR from "swr";
import FilterOverlay from "./FilterOverlay";
import classes from "./SearchFilter.module.css";


import {useFilterStore} from "../../zustand/filterStore";
import debounce from "lodash/debounce";
import Divider from "@mui/material/Divider";
import FormControlLabel from "@mui/material/FormControlLabel";
import Radio from "@mui/material/Radio";
import RadioGroup from "@mui/material/RadioGroup";

const icon = <CheckBoxOutlineBlankIcon fontSize="small"/>;
const checkedIcon = <CheckBoxIcon fontSize="small"/>;

function groupBy(xs, key) {
    return xs.reduce(function (rv, x) {
        (rv[x[key]] = rv[x[key]] || []).push(x);
        return rv;
    }, {});
}

const fetcher = url => fetch(url).then(res => res.json());

const FilterEditor = ({
                          open = false,
                          onClose,
                          editFilterId = null,
                          setOpenLoadOverlay,
                          dataView = false
                      }) => {
    let params = useParams();
    const {data: fields} = useSWR(
        `/web/projects/${params.project}/fields`,
        (url) => fetch(url).then((res) => res.json()),
        {dedupingInterval: 2000}
    );
    const initialFilter = useFilterStore(
        (state) => state.filterList.find((filter) => filter.id === editFilterId));

    const [field, setField] = useState(initialFilter?.field);

    const availableFields = useMemo(() => {
        if (!fields) return [];
        return [
            {
                id: 'name',
                name: 'Name',
                type: 'name'
            },
            {
                id: 'groups',
                name: 'Groups',
                type: 'groups'
            },
            {
                id: 'samples',
                name: 'Samples',
                type: 'samples'
            },
            {
                id: "experiments",
                name: "Experiments",
                type: 'experiments'
            },
            {
                id: 'items',
                name: 'ResearchItems',
                type: 'researchitems'
            },
            {
                id: "date_created",
                name: "Date created",
                type: "Date"
            },
            {
                id: "line",
                name: "----------------------------------------------------- Fields ----------------------------------------------------",
                type: "line"
            },
            ...fields.filter((field) => (field.type === "ComboBox") || (field.type === "Numeric") ||
                (field.type === "NumericRange") || (field.type === "Date") || (field.type === "SingleLine") ||
                (field.type === "CheckBox"))];
    }, [fields]);

    const selectedField = useMemo(() => availableFields.find((f) => f.name === field),
        [availableFields, field]);

    const [selectOpen, setSelectOpen] = useState(false);

    useEffect(() => {
        if (editFilterId) return;
        setField("");
        setSelectOpen(false);
    }, [open, editFilterId])

    return (
        open && <FilterOverlay onClose={onClose} setOpenLoadOverlay={setOpenLoadOverlay} dataView={dataView}>

            < div id="addFilter">
                <div className={classes.fieldWrap}>
                    <FormControl fullWidth style={{marginBottom: "20px"}}>
                        <InputLabel>Field</InputLabel>
                        <Select
                            value={field}
                            label="Field"
                            open={selectOpen}
                            onOpen={() => setSelectOpen(true)}
                            onClose={() => setSelectOpen(false)}
                            onChange={(e) => setField(e.target.value)}
                            disabled={editFilterId}
                        >
                            {availableFields.map(({name, id}) => (
                                ((id !== "line") ?
                                    <MenuItem value={name} key={id}>
                                        {name}
                                    </MenuItem> :
                                    <Divider style={{lineHeight: "10px"}}> Custom fields </Divider>)
                            ))}
                        </Select>
                    </FormControl>
                </div>
                {field && selectedField.type === 'ComboBox' &&
                    <ComboFilterEditor onConfirm={onClose} field={selectedField}/>}
                {field && selectedField.type === 'groups' && <GroupFilterEditor onConfirm={onClose}/>}
                {field && selectedField.type === 'samples' && <SampleFilterEditor onConfirm={onClose}/>}
                {field && selectedField.type === 'experiments' && <ExperimentFilterEditor onConfirm={onClose}/>}
                {field && selectedField.type === 'researchitems' && <ResearchItemFilterEditor onConfirm={onClose}/>}
                {field && (selectedField.type === 'Numeric' || selectedField.type === 'NumericRange') &&
                    <NumericFilterEditor onConfirm={onClose} field={selectedField}/>}
                {field && (selectedField.type === 'Date') &&
                    <DateFilterEditor onConfirm={onClose} field={selectedField}/>}
                {field && (selectedField.type === 'SingleLine') &&
                    <TextFilterEditor onConfirm={onClose} field={selectedField}/>}
                {field && (selectedField.type === 'name') &&
                    <NameFilterEditor onConfirm={onClose}/>}
                {field && (selectedField.type === 'CheckBox') &&
                    <CheckFilterEditor onConfirm={onClose} field={selectedField}/>}
            </div>
        </FilterOverlay>
    );
};

export default FilterEditor;

function NumericFilterEditor({onConfirm = () => null, field}) {

    const initialFilter = useFilterStore(
        (state) => state.filterList.find((filter) => filter.id === field.id));

    const params = useParams();

    useEffect(() => {
        if (initialFilter) {
            let val = initialFilter.values[0];
            setFromValue(val.min);
            setToValue(val.max);
            setUnitId(val.unit);
        } else {
            setFromValue("");
            setToValue("");
            setUnitId('none');
        }
    }, [field, initialFilter]);


    const saveFilter = useFilterStore((state) => state.saveFilter);

    const handleSave = () => {
        saveFilter({
            id: field.id,
            field: field.name,
            values: [{
                name: `${fromValue} - ${toValue} ${units.find((unit) => unit.id === unitId)?.Name || ''}`,
                min: fromValue,
                max: toValue,
                unit: unitId
            }],
            type: 'numeric'
        });
        onConfirm();
    };

    const [fromValue, setFromValue] = useState("");
    const [toValue, setToValue] = useState("");
    const [unitId, setUnitId] = useState('none');

    const {data: units} = useSWR(`/web/units?project=${params.project}`, fetcher, {dedupingInterval: 10000});
    const groups = useMemo(() => units ? groupBy(units, 'category') : [], [units])

    return (
        <>
            <Stack direction='row' spacing={2}>
                <div className={classes.fieldWrap}>
                    <TextField
                        label={'Min'}
                        value={fromValue}
                        // @ts-ignore
                        onChange={(e) => setFromValue(e.target.value)}
                        type="number"
                        fullWidth
                    />
                </div>
                <div className={classes.fieldWrap}>
                    <TextField
                        label={'Max'}
                        value={toValue}
                        // @ts-ignore
                        onChange={(e) => setToValue(e.target.value)}
                        type="number"
                        fullWidth
                    />
                </div>
                <div className={classes.fieldWrap}>
                    <FormControl fullWidth>
                        <InputLabel>
                            Unit
                        </InputLabel>
                        <Select
                            label={'Unit'}
                            value={unitId}
                            onChange={(e) => setUnitId(e.target.value)}
                            native={true}
                            fullWidth
                        >
                            <option value='none'>no unit</option>
                            {Object.keys(groups).map((category) =>
                                <optgroup label={category}>
                                    {groups[category].map((unit) => <option value={unit.id}>{unit.Name}</option>)}
                                </optgroup>)}
                        </Select>
                    </FormControl>

                </div>
                <Button disableElevation variant="contained" onClick={handleSave}
                        style={{marginLeft: "20px"}}>
                    Filter
                </Button>
            </Stack>

        </>
    );
}

function SampleFilterEditor({onConfirm = () => null}) {

    const initialFilter = useFilterStore(
        (state) => state.filterList.find((filter) => filter.id === 'samples'));

    const [values, setValues] = useState(initialFilter?.values);
    const params = useParams();
    const [queryString, setQueryString] = useState("")

    const {data: valueOptions} = useSWR(`/web/projects/${params.project}/samples?${queryString}`,
        (url) => fetch(url).then((res) => res.json())
    );
    const [items, setItems] = React.useState([])

    useEffect(() => {
        if (valueOptions) {
            let allOption = {
                'id': "all",
                'Name': "All samples",
                'Category': "All",
                "DisplayedCategory": "All"
            }
            let options = [allOption]
            options.push(...valueOptions)
            setItems(options)
        }
    }, [valueOptions]);

    const saveFilter = useFilterStore((state) => state.saveFilter);

    const handleSave = () => {
        saveFilter({
            id: 'samples',
            field: 'Samples',
            values: values,
            type: 'samples'
        });
        onConfirm();
    };

    function createQueryString(input) {
        const url_options = new URLSearchParams({
            name: input
        }).toString()
        setQueryString(url_options)

    }

    function inputChange(e) {
        debouncedSetInput(e.target.value)
    }

    function autocompleteOnBlur() {
        debouncedSetInput("")
    }

    const debouncedSetInput = useCallback(debounce(createQueryString, 300), []);


    return (
        <>

            <div className={classes.fieldWrap} style={{display: 'flex'}}>
                <Autocomplete
                    multiple
                    onChange={(e, value) => setValues(value)}
                    options={items}
                    groupBy={(option) => option.DisplayedCategory}
                    disableCloseOnSelect
                    value={values}
                    disableClearable
                    onInputChange={(e) => inputChange(e)}
                    getOptionLabel={(option: any) => option.Name}
                    fullWidth
                    renderOption={(props, option: any, {selected}) => {
                        return (
                            <li {...props}>
                                <Checkbox
                                    icon={icon}
                                    checkedIcon={checkedIcon}
                                    style={{marginRight: 8}}
                                    checked={selected}
                                />
                                {option.Name}
                            </li>
                        )
                    }}
                    renderInput={(params) => (
                        <TextField {...params} label="Values"/>
                    )}
                />
                <Button disableElevation variant="contained" onClick={handleSave} style={{marginLeft: "20px"}}
                        disabled={!(values?.length > 0)}>
                    Filter
                </Button>
            </div>

        </>
    );
}

function ExperimentFilterEditor({onConfirm = () => null}) {

    const initialFilter = useFilterStore(
        (state) => state.filterList.find((filter) => filter.id === 'experiments'));

    const [values, setValues] = useState(initialFilter?.values);
    const params = useParams();
    const [queryString, setQueryString] = useState("")

    const {data: valueOptions} = useSWR(`/web/projects/${params.project}/experiments?${queryString}`,
        (url) => fetch(url).then((res) => res.json())
    );
    const [items, setItems] = React.useState([])

    useEffect(() => {
        if (valueOptions) {
            let allOption = {
                'id': "all",
                'Name': "All experiments",
                'Category': "All",
                "DisplayedCategory": "All"
            }
            let options = [allOption]
            options.push(...valueOptions)

            setItems(options)
        }
    }, [valueOptions]);

    const saveFilter = useFilterStore((state) => state.saveFilter);

    const handleSave = () => {
        saveFilter({
            id: 'experiments',
            field: 'Experiments',
            values: values,
            type: 'experiments'
        });
        onConfirm();
    };

    function createQueryString(input) {
        const url_options = new URLSearchParams({
            name: input
        }).toString()
        setQueryString(url_options)

    }

    function inputChange(e) {
        debouncedSetInput(e.target.value)
    }


    const debouncedSetInput = useCallback(debounce(createQueryString, 300), []);

    return (
        <>


            <div className={classes.fieldWrap} style={{display: 'flex'}}>
                <Autocomplete
                    multiple
                    onChange={(e, value) => setValues(value)}
                    options={items}
                    groupBy={(option) => option.DisplayedCategory}
                    disableCloseOnSelect
                    value={values}
                    disableClearable
                    onInputChange={(e) => inputChange(e)}
                    getOptionLabel={(option: any) => option.Name}
                    fullWidth
                    renderOption={(props, option: any, {selected}) => {
                        return (
                            <li {...props}>
                                <Checkbox
                                    icon={icon}
                                    checkedIcon={checkedIcon}
                                    style={{marginRight: 8}}
                                    checked={selected}
                                />
                                {option.Name}
                            </li>
                        )
                    }}
                    renderInput={(params) => (
                        <TextField {...params} label="Values"/>
                    )}
                />
                <Button disableElevation variant="contained" onClick={handleSave} style={{marginLeft: "20px"}}
                        disabled={!(values?.length > 0)}>
                    Filter
                </Button>
            </div>
        </>
    );
}

function ResearchItemFilterEditor({onConfirm = () => null}) {

    const initialFilter = useFilterStore(
        (state) => state.filterList.find((filter) => filter.id === 'researchitems'));

    const [values, setValues] = useState(initialFilter?.values);
    const params = useParams();
    const [queryString, setQueryString] = useState("")

    const {data: valueOptions} = useSWR(`/web/projects/${params.project}/researchitems?${queryString}`,
        (url) => fetch(url).then((res) => res.json())
    );
    const [items, setItems] = React.useState([])

    const saveFilter = useFilterStore((state) => state.saveFilter);

    const handleSave = () => {
        saveFilter({
            id: 'researchitems',
            field: 'Items',
            values: values,
            type: 'researchitems'
        });
        onConfirm();
    };

    useEffect(() => {
        if (valueOptions) {
            let allOption = {
                'id': "all",
                'Name': "All researchitems",
                'Category': "All",
                "DisplayedCategory": "All"
            }
            let options = [allOption]
            options.push(...valueOptions)
            setItems(options)
        }
    }, [valueOptions]);

    function createQueryString(input) {
        const url_options = new URLSearchParams({
            name: input
        }).toString()
        setQueryString(url_options)

    }

    function inputChange(e) {
        debouncedSetInput(e.target.value)
    }

    function autocompleteOnBlur() {
        debouncedSetInput("")
    }

    const debouncedSetInput = useCallback(debounce(createQueryString, 300), []);

    return (
        <>


            <div className={classes.fieldWrap} style={{display: "flex"}}>
                <Autocomplete
                    multiple
                    onChange={(e, value) => setValues(value)}
                    // options={valueOptions.sort((a, b) => a.Category.localeCompare(b.Category))}
                    options={items}
                    groupBy={(option) => option.DisplayedCategory}
                    disableCloseOnSelect
                    fullWidth
                    value={values}
                    onInputChange={(e) => inputChange(e)}
                    disableClearable
                    getOptionLabel={(option: any) => option.Name}
                    renderOption={(props, option: any, {selected}) => {
                        return (
                            <li {...props}>
                                <Checkbox
                                    icon={icon}
                                    checkedIcon={checkedIcon}
                                    style={{marginRight: 8}}
                                    checked={selected}
                                />
                                {option.Name}
                            </li>
                        )
                    }}
                    renderInput={(params) => (
                        <TextField {...params} label="Values"/>
                    )}
                />
                <Button disableElevation variant="contained" onClick={handleSave} style={{marginLeft: "20px"}}
                        disabled={!(values?.length > 0)}>
                    Filter
                </Button>
            </div>
        </>
    );
}


function GroupFilterEditor({onConfirm = () => null}) {

    const initialFilter = useFilterStore(
        (state) => state.filterList.find((filter) => filter.id === 'groups'));


    const [values, setValues] = useState(initialFilter?.values);
    const params = useParams();
    const [queryString, setQueryString] = useState("")

    const {data: valueOptions} = useSWR(`/web/projects/${params.project}/groups?${queryString}`,
        (url) => fetch(url).then((res) => res.json()),
        {dedupingInterval: 2000}
    );

    const saveFilter = useFilterStore((state) => state.saveFilter);

    const [items, setItems] = React.useState([])

    const handleSave = () => {
        saveFilter({
            id: 'groups',
            field: 'Groups',
            values: values,
            type: 'groups'
        });
        onConfirm();
    };

    useEffect(() => {
        if (valueOptions) {
            let allOption = {
                'id': "all",
                'Name': "All groups",
                'Category': "All",
                "DisplayedCategory": "All"
            }
            let options = [allOption]
            options.push(...valueOptions)
            setItems(options)
        }
    }, [valueOptions]);

    function createQueryString(input) {
        const url_options = new URLSearchParams({
            name: input
        }).toString()
        setQueryString(url_options)

    }

    function inputChange(e) {
        debouncedSetInput(e.target.value)
    }


    const debouncedSetInput = useCallback(debounce(createQueryString, 300), []);


    return (
        <>
            <div className={classes.fieldWrap} style={{display: "flex"}}>
                <Autocomplete
                    multiple
                    onChange={(e, value) => setValues(value)}
                    options={items}
                    groupBy={(option) => option.DisplayedCategory}
                    disableCloseOnSelect
                    value={values}
                    disableClearable
                    onInputChange={(e) => inputChange(e)}
                    getOptionLabel={(option: any) => option.Name}
                    fullWidth
                    renderOption={(props, option: any, {selected}) => {
                        return (
                            <li {...props}>
                                <Checkbox
                                    icon={icon}
                                    checkedIcon={checkedIcon}
                                    style={{marginRight: 8}}
                                    checked={selected}
                                />
                                {option.Name}
                            </li>
                        )
                    }}
                    renderInput={(params) => (
                        <TextField {...params} label="Values"/>
                    )}
                />
                <Button disableElevation variant="contained" onClick={handleSave} style={{marginLeft: "20px"}}
                        disabled={!(values?.length > 0)}>
                    Filter
                </Button>
            </div>


        </>
    );
}

function ComboFilterEditor({onConfirm = () => null, field}) {

    const [values, setValues] = useState([]);
    const {data: valueOptions} = useSWR(field?.id ?
            `/web/comboboxentries/${field.id}/entries` : null,
        (url) => fetch(url).then((res) => res.json()),
        {dedupingInterval: 2000}
    );

    const initialFilter = useFilterStore(
        (state) => state.filterList.find((filter) => filter.id === field.id));

    useEffect(() => {
        if (initialFilter && initialFilter.field === field.name) {
            setValues(initialFilter.values);
        } else setValues([]);
    }, [field, initialFilter]);

    const saveFilter = useFilterStore((state) => state.saveFilter);

    const handleSave = () => {
        saveFilter({
            id: field.id,
            field: field.name,
            values: values,
            type: 'combobox'
        });
        onConfirm();
    };

    return (
        <>
            {(valueOptions) ?
                <>
                    <div className={classes.fieldWrap} style={{display: "flex"}}>
                        <Autocomplete
                            multiple
                            onChange={(e, value) => setValues(value)}
                            options={valueOptions}
                            disableCloseOnSelect
                            value={values}
                            disableClearable
                            getOptionLabel={(option: any) => option.name}
                            fullWidth
                            renderOption={(props, option: any, {selected}) => {
                                return (
                                    <li {...props}>
                                        <Checkbox
                                            icon={icon}
                                            checkedIcon={checkedIcon}
                                            style={{marginRight: 8}}
                                            checked={selected}
                                        />
                                        {option.name}
                                    </li>
                                )
                            }}
                            renderInput={(params) => (
                                <TextField {...params} label="Values"/>
                            )}
                        />
                        <Button disableElevation variant="contained" onClick={handleSave} style={{marginLeft: "20px"}}
                                disabled={!(values?.length > 0)}>
                            Filter
                        </Button>
                    </div>

                </> : field && 'Loading...'}
        </>
    );
}

function DateFilterEditor({onConfirm = () => null, field}) {

    const initialFilter = useFilterStore(
        (state) => state.filterList.find((filter) => filter.id === field.id));

    const params = useParams();

    useEffect(() => {
        if (initialFilter) {
            let val = initialFilter.values[0];
            if (val.option !== "Custom") {
                val.min = getDateToday()
                val.max = getDateToday(false)
            }
            setFromValue(val.min);
            setToValue(val.max);
            setSelectedOption(val.option)
        } else {
            setFromValue(getDateToday());
            setToValue(getDateToday(false));
            setSelectedOption("Today")
        }
    }, [field, initialFilter]);


    const saveFilter = useFilterStore((state) => state.saveFilter);

    const handleSave = () => {
        let from = ""
        let till = ""
        let name = ""
        if (selectedOption === "Custom") {
            from = fromValue
            till = toValue
            name = `${fromValue} - ${toValue}`
        } else {
            from = ""
            till = ""
            name = selectedOption
        }

        saveFilter({
            id: field.id,
            field: field.name,
            values: [{
                name: name,
                min: from,
                max: till,
                option: selectedOption
            }],
            type: 'date'
        });
        onConfirm();
    };

    const options = [
        "Today", "Yesterday", "This week", "Last week", "This month", "Last month", "This year", "Custom"
    ]

    const [selectedOption, setSelectedOption] = useState("Today");
    const [fromValue, setFromValue] = useState(getDateToday());
    const [toValue, setToValue] = useState(getDateToday(false));

    function getDateToday(start = true) {
        const today = new Date();
        let todayString = today.toISOString()
        if (start === true) {
            todayString = `${todayString.split("T")[0]}T00:00`
        } else {
            todayString = `${todayString.split("T")[0]}T23:59`

        }
        return todayString
    }

    return (
        <>

            <Stack direction='row' spacing={2}>
                <Select variant={"outlined"} fullWidth value={selectedOption} native={true}
                        onChange={(e) => setSelectedOption(e.target.value)}>
                    {options.map(opt => <option key={opt} value={opt}>{opt}</option>)}

                </Select>
                {(selectedOption == "Custom") &&
                    <div className={classes.fieldWrap} style={{width: '60%', display: "flex"}}>
                        <TextField
                            label={'From'}
                            value={fromValue}
                            // @ts-ignore
                            onChange={(e) => setFromValue(e.target.value)}
                            type="datetime-local"
                            fullWidth
                            disabled={selectedOption !== "Custom"}

                        />
                        <TextField
                            label={'Till'}
                            value={toValue}
                            // @ts-ignore
                            onChange={(e) => setToValue(e.target.value)}
                            type="datetime-local"
                            style={{marginLeft: "30px"}}
                            fullWidth
                            disabled={selectedOption !== "Custom"}

                        />
                    </div>}
                <Button disableElevation variant="contained" onClick={handleSave}>
                    Filter
                </Button>
            </Stack>
        </>
    )
        ;
}

function TextFilterEditor({onConfirm = () => null, field}) {

    const initialFilter = useFilterStore(
        (state) => state.filterList.find((filter) => filter.id === field.id));

    const [value, setValue] = useState("");

    useEffect(() => {
        if (initialFilter) {
            let val = initialFilter.values[0].value;
            setValue(val);
        } else {
            setValue("");
        }
    }, [field, initialFilter]);


    const saveFilter = useFilterStore((state) => state.saveFilter);

    const handleSave = () => {
        saveFilter({
            id: field.id,
            field: field.name,
            values: [{
                name: value,
                value: value
            }],
            type: 'text'
        });
        onConfirm();
    };

    return (
        <>
            <div className={classes.fieldWrap} style={{display: "flex"}}>
                <TextField
                    label={'Search'}
                    value={value}
                    // @ts-ignore
                    onChange={(e) => setValue(e.target.value)}
                    // type="text"
                    fullWidth
                />
                <Button disableElevation variant="contained" onClick={handleSave} style={{marginLeft: "20px"}}>
                    Filter
                </Button>
            </div>
        </>
    );
}

function NameFilterEditor({onConfirm = () => null}) {

    const initialFilter = useFilterStore(
        (state) => state.nameFilter);

    const setNameFilter = useFilterStore(
        (state) => state.setNameFilter
    )

    const [value, setValue] = useState("");

    useEffect(() => {
        if (initialFilter) {
            let val = initialFilter;
            setValue(val);
        } else {
            setValue("");
        }
    }, [initialFilter]);

    ;

    const handleSave = () => {
        setNameFilter(value)
        onConfirm();
    };

    return (
        <>
            <div className={classes.fieldWrap} style={{display: "flex"}}>
                <TextField
                    label={'Search'}
                    value={value}
                    // @ts-ignore
                    onChange={(e) => setValue(e.target.value)}
                    // type="text"
                    fullWidth
                />
                <Button disableElevation variant="contained" onClick={handleSave} style={{marginLeft: "20px"}}>
                    Filter
                </Button>
            </div>
        </>
    );
}

function CheckFilterEditor({onConfirm = () => null, field}) {

    const initialFilter = useFilterStore(
        (state) => state.filterList.find((filter) => filter.id === field.id));

    const [value, setValue] = useState(true);
    const [valueString, setValueString] = useState("true");

    useEffect(() => {
        if (initialFilter) {

            let val = initialFilter.values[0].value;
            setValueString(String(val))
            setValue(val);
        } else {
            setValue(true);
        }
    }, [field, initialFilter]);


    const saveFilter = useFilterStore((state) => state.saveFilter);

    const handleSave = () => {
        saveFilter({
            id: field.id,
            field: field.name,
            values: [{
                name: String(value),
                value: value
            }],
            type: 'checkbox'
        });
        onConfirm();
    };


    function handleRadioChange(event) {
        if (event.target.value === "true") {
            setValue(true);
            setValueString("true");
        } else {
            setValue(false);
            setValueString("false");
        }

    }

    return (
        <>
            <div className={classes.fieldWrap} style={{display: "flex"}}>
                <div className={classes.fieldWrap}>
                    <RadioGroup
                        aria-labelledby="checkbox-group-label"
                        value={valueString}
                        name="radio-buttons-group"
                        onChange={handleRadioChange}
                    >
                        <div>

                            <FormControlLabel value="true" control={<Radio/>} label="True"
                                              style={{marginLeft: "0px"}}/>
                            <FormControlLabel value="false" control={<Radio/>} label="False"
                                              style={{marginLeft: "40px"}}/>
                        </div>


                    </RadioGroup>
                </div>
                <Button disableElevation variant="contained" onClick={handleSave}
                        style={{ marginLeft: "auto"}}>
                    Filter
                </Button>
            </div>
        </>
    );
}