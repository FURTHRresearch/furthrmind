import React, {useEffect, useState} from 'react';
import Box from '@mui/material/Box';
import Checkbox from '@mui/material/Checkbox';
import Paper from '@mui/material/Paper';
import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableContainer from '@mui/material/TableContainer';
import TableHead from '@mui/material/TableHead';
import TableRow from '@mui/material/TableRow';
import TableSortLabel from '@mui/material/TableSortLabel';
import {visuallyHidden} from '@mui/utils';
import {useMultiSelectStore} from '../../zustand/multiSelectStore';
import GroupPropertiesCard from '../GroupPropertiesCard';
import ViewColumnIcon from '@mui/icons-material/ViewColumn';
import Button from '@mui/material/Button';
import Popover from "@mui/material/Popover";
import Typography from "@mui/material/Typography";
import FormGroup from '@mui/material/FormGroup';
import FormControlLabel from '@mui/material/FormControlLabel';
import OutlinedInput from '@mui/material/OutlinedInput';
import InputAdornment from '@mui/material/InputAdornment';
import IconButton from '@mui/material/IconButton';
import SearchIcon from '@mui/icons-material/Search';
import Switch from '@mui/material/Switch'
import ClearIcon from '@mui/icons-material/Clear';
import Card from '@mui/material/Card';
import axios from "axios";
import {useParams} from "react-router-dom";
import {Link, Pagination} from "@mui/material";
import ResearchItemOverlay from "../Overlays/ResearchItemOverlay";
import {useFilterStore} from "../../zustand/filterStore";

function EnhancedTableHead(props) {
    const {
        columnsList,
        setColumnsList,
        showSelector,
        displayedColumns, setDisplayedColumns,
        orderDict, setOrderDict,
        setAddedColumn

    } =
        props;

    const createSortHandler = (field_name) => (event) => {
        const newOrderDict = {"direction": "asc", "orderBy": "", "numeric": false}
        if (field_name === 'Name') {
            newOrderDict.orderBy = "name"
        } else if (field_name === 'Type') {
            newOrderDict.orderBy = "type"
        } else {
            columnListToShow.map((column) => {
                if (column.label === field_name) {
                    newOrderDict.orderBy = column.id;
                    if (column.numeric === true) {
                        newOrderDict.numeric = true
                    }
                }
            })
        }
        if (orderDict.direction === 'asc') {
            newOrderDict.direction = 'desc'
        } else {
            newOrderDict.direction = 'asc'
        }
        setOrderDict(newOrderDict)
    }


    const [anchorEl, setAnchorEl] = useState<HTMLButtonElement | null>(null);
    const [searchInput, setSearchInput] = useState('');
    const [columnListToShow, setColumnListToShow] = useState([]);

    const handleClick = (event: React.MouseEvent<HTMLButtonElement>) => {
        setAnchorEl(event.currentTarget);
    };

    const handleClose = () => {
        setAnchorEl(null);
    };


    const handleSwitchChange = (e) => {
        const standardNameList = {"Name": "", "Type": "", "Short ID": ""}
        const name = e.target.name;
        const checkedStatus = e.target.checked;

        const colList = columnsList.slice();
        const indexToBeUpdated = colList.findIndex((col) => col.label === name);

        colList[indexToBeUpdated] = {
            ...colList[indexToBeUpdated],
            show: checkedStatus
        }
        setColumnsList(colList)

        const tempDisplayedColumns = [...displayedColumns]
        if (checkedStatus) {
            if (!tempDisplayedColumns.includes(name)) {
                tempDisplayedColumns.push(name)
                setDisplayedColumns(tempDisplayedColumns)
                setAddedColumn(name)
            }
        } else {
            if (tempDisplayedColumns.includes(name)) {
                let index = tempDisplayedColumns.indexOf(name)
                tempDisplayedColumns.splice(index, 1)
                setDisplayedColumns(tempDisplayedColumns)
                setAddedColumn("")
            }
        }
    }

    const searchInputHandler = (e) => {

        setSearchInput(e.target.value);
    }

    const handleSearchClear = () => {

        setSearchInput('')
    }


    useEffect(() => {
        const columnListImprint = columnsList.slice();
        const result = columnListImprint.filter((col) => {
            if (displayedColumns.includes(col.label)) {
                col.show = true;
            } else {
                col.show = false;
            }
            const label = String(col.label).toLowerCase();
            const searchInputLowerCase = String(searchInput).toLowerCase()
            const a = String(label).includes(searchInputLowerCase)
            return String(label).includes(searchInputLowerCase);

        });
        setColumnListToShow([...result]);

    }, [columnsList, searchInput, displayedColumns]);

    const open = Boolean(anchorEl);
    const id = open ? 'simple-popover' : undefined;

    return (
        <TableHead>
            <TableRow>
                <Button
                    sx={{
                        marginTop: "16px",
                        marginLeft: "16px"
                    }}
                    variant="outlined"
                    startIcon={<ViewColumnIcon/>}
                    onClick={handleClick}
                >
                    Columns
                </Button>
            </TableRow>
            <Popover
                id={id}
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
                    overflow: 'scroll'
                }}>
                    <OutlinedInput
                        id="outlined-adornment-password"
                        // type={values.showPassword ? 'text' : 'password'}
                        value={searchInput}
                        onChange={(e) => searchInputHandler(e)}
                        notched={false}
                        endAdornment={
                            <InputAdornment position="end">
                                <IconButton
                                    aria-label="toggle password visibility"
                                    // onClick={handleClickShowPassword}
                                    // onMouseDown={handleMouseDownPassword}
                                    edge="end"
                                >
                                    {searchInput.length === 0 ? <SearchIcon/> : <ClearIcon
                                        onClick={handleSearchClear}
                                    />}
                                </IconButton>
                            </InputAdornment>
                        }
                        label="Password"
                    />
                    <FormGroup>
                        {columnListToShow.length > 0 && columnListToShow.map((column) => <FormControlLabel
                            control={<Switch
                                name={column.label}
                                checked={column.show}
                                onChange={handleSwitchChange}/>}
                            label={column.label}/>)}
                        {columnListToShow.length === 0 &&
                            <Typography className="mt-2">No result found !</Typography>}
                    </FormGroup>
                </Card>

            </Popover>
            <TableRow>
                {showSelector &&
                    <TableCell padding="checkbox">
                    </TableCell>
                }
                {columnsList.map((headCell) => (
                    <>
                        {headCell.show ?
                            <TableCell
                                key={headCell.id}
                                align="center"
                                padding={headCell.disablePadding ? 'none' : 'normal'}
                                sortDirection={orderDict["direction"]}
                            >
                                <TableSortLabel
                                    active={orderDict["orderBy"] === headCell.label}
                                    direction={orderDict["direction"]}
                                    onClick={createSortHandler(headCell.label)}
                                >
                                    {headCell.label}
                                    {orderDict["orderBy"] === headCell.label ? (
                                        <Box component="span" sx={visuallyHidden}>
                                            {orderDict["direction"] === 'desc' ? 'sorted descending' : 'sorted ascending'}
                                        </Box>
                                    ) : null}
                                </TableSortLabel>
                            </TableCell> : null}
                    </>
                ))}
            </TableRow>
        </TableHead>
    );
}

// EnhancedTableHead.propTypes = {
//     numSelected: PropTypes.number.isRequired,
//     onRequestSort: PropTypes.func.isRequired,
//     onSelectAllClick: PropTypes.func.isRequired,
//     order: PropTypes.oneOf(['asc', 'desc']).isRequired,
//     orderBy: PropTypes.string.isRequired,
//     rowCount: PropTypes.number.isRequired,
//     headCells: PropTypes.array
// };


function EnhancedTable({
                           group, project,
                           showGroupProperties, showSelector,
                           displayedColumns, setDisplayedColumns, setCurrentGroup,
                           items, maxPageAndPageItemMapping, dataViewId, groups, mutateGroups
                       }) {
    const params = useParams();
    const maxItems = 100
    const [researchItemData, setResearchItemData] = useState([]);
    const [getAllFieldsStatus, setGetAllFieldsStatus] = useState(false)
    const [columnData, setColumnData] = useState({})
    const [columnsList, setColumnsList] = useState([{
        label: "Name",
        key: "name",
        show: false,
        // show: true,
        numeric: false,
        disablePadding: true,
        id: 1
    },
        {
            label: "Type",
            key: "type",
            show: false,
            // show: true,
            numeric: true,
            disablePadding: false,
            id: 2
        },
        {
            label: "Short ID",
            key: "short_id",
            show: false,
            // show: true,
            numeric: true,
            disablePadding: false,
            id: 3
        },
    ])


    const [showItemOverlay, setShowItemOverlay] = React.useState(false);
    const [clickedItem, setClickedItem] = React.useState({
        id: "",
        group_id: "",
        type: ""
    });

    const [maxIndex, setMaxIndex] = React.useState(1);
    const [index, setIndex] = React.useState(1);

    const includeLinked = useFilterStore(
            (state) => state.includeLinked
        );

    function getAllFields() {
        axios.get('/web/projects/' + params.project + '/fields').then(function (axiosTestResult) {
            const columnsListCopy = [...columnsList]
            axiosTestResult.data.map(field => {

                    const object = {
                        label: field.name,
                        key: field.name,
                        show: false,
                        numeric: false,
                        disablePadding: true,
                        id: field.id
                    }
                    if (field.type == 'Numeric') {
                        object["numeric"] = true
                    }
                    const arrayLength = columnsListCopy.length;
                    let trigger = false

                    for (var i = 0; i < arrayLength; i++) {
                        if (columnsListCopy[i].label == object.label) {
                            trigger = true
                        }
                    }
                    if (trigger == false) {
                        columnsListCopy.push(object)
                    }

                }
            )
            setColumnsList(columnsListCopy)
            setGetAllFieldsStatus(true)

        })
    }

    useEffect(() => {
        if (!getAllFieldsStatus) {
            getAllFields()
        }


    }, [columnsList])

    const multiSelectStore = useMultiSelectStore();

    const isSelected = (id) => multiSelectStore.selected.includes(id);
    const [orderDict, setOrderDict] = useState({
        "orderBy": "name", "direction": "asc", "numeric": false
    })

    const [addedColumn, setAddedColumn] = React.useState("")

    function descendingComparator(a, b, orderDict) {

        let orderBy = orderDict["orderBy"]
        let numeric = orderDict["numeric"]
        let columnDataA = {}
        if (a.id in columnData) {
            columnDataA = {...columnData[a.id]}
        }
        let columnDataB = {}
        if (b.id in columnData) {
            columnDataB = {...columnData[b.id]}
        }
        if (!(orderBy in a) && !(orderBy in columnDataA)) {
            return 1;
        }
        if (!(orderBy in b) && !(orderBy in columnDataB)) {
            return -1;
        }

        let valueA = null
        if (orderBy in a) {
            valueA = a[orderBy]
        } else if (orderBy in columnDataA) {
            if (numeric) {
                valueA = columnDataA[orderBy].si_value
            } else {
                valueA = columnDataA[orderBy].value
            }
        }
        let valueB = null
        if (orderBy in b) {
            valueB = b[orderBy]
        } else if (orderBy in columnDataB) {
            if (numeric) {
                valueB = columnDataB[orderBy].si_value
            } else {
                valueB = columnDataB[orderBy].value
            }
        }
        if (valueB < valueA) {
            return -1;
        }
        if (valueB > valueA) {
            return 1;
        }
        return 0;
    }

    function getComparator(orderDict) {
        let order = orderDict["direction"]
        return order === 'desc'
            ? (a, b) => descendingComparator(a, b, orderDict)
            : (a, b) => -descendingComparator(a, b, orderDict);
    }

    useEffect(() => {
        const rsCopy = [...researchItemData]
        const rs = applySorting(rsCopy)
        setResearchItemData(rs)
    }, [orderDict]);

    function applySorting(items) {
        const rs = items.slice().sort(getComparator(orderDict))
        return rs
    }

    useEffect(() => {

        if (items) {
            setMaxIndex(Math.ceil(items.length / maxItems))
            let start = (index - 1) * maxItems
            let end = (index) * maxItems + 1
            setResearchItemData(items.slice(start, end))

        } else if (maxPageAndPageItemMapping) {
            if (maxPageAndPageItemMapping)
                setMaxIndex(maxPageAndPageItemMapping.maxPage)

            let itemIdList = maxPageAndPageItemMapping.pageItemMapping[index]
            if (itemIdList) {
                let queryString = new URLSearchParams({
                    items: JSON.stringify(itemIdList)
                }).toString()

                axios.get(`/dataviews/${dataViewId}/items?${queryString}`).then((res) => {
                    setResearchItemData(res.data)
                })
            } else {
                setResearchItemData([])
            }

        }
    }, [index, items, maxPageAndPageItemMapping]);

    // useEffect(() => {
    //     console.log(pageItemIndex)
    // }, []);

    useEffect(() => {
        load_data()

    }, [displayedColumns, researchItemData, columnsList])

    const load_data = () => {

        const idList = []
        researchItemData.forEach((item) => {
            idList.push(item.id)
        })

        let fieldIDList = []

        columnsList.map((column) => {
            if (displayedColumns.includes(column.label)) {
                let fieldId = String(column.id)
                if (fieldId.length === 24) {
                    fieldIDList.push(fieldId)
                }
            }
        })

        let itemIdstring = idList.join()
        let fieldIdString = fieldIDList.join()

        if (fieldIdString && itemIdstring) {
            axios.post(`/web/items/field-value`,
                {
                    item_id_list: idList,
                    field_id_list: fieldIDList,
                    include_linked: includeLinked
                }
                ).then(
                (res) => {
                    setColumnData(res.data)
                })

        }
    }

    function nameClicked(item) {
        setShowItemOverlay(true)
        setClickedItem(item)
    }

    function handlePageChange(e, newValue) {
        setIndex(newValue)
    }


    return (
        <Box sx={{width: '98%', marginRight: "20px"}}>
            {showGroupProperties && <div style={{margin: "10px 0px"}}>
                <GroupPropertiesCard groupId={group.id} groups={groups}
                                     mutateGroups={mutateGroups}
                                     setCurrentGroup={setCurrentGroup}/>
            </div>
            }

            <Paper sx={{width: '100%', mb: 2}}>
                <TableContainer>
                    <Table
                        sx={{minWidth: 750}}
                        aria-labelledby="tableTitle"
                        size={'medium'}
                    >
                        {getAllFieldsStatus == true && (
                            <EnhancedTableHead
                                columnsList={columnsList}
                                setColumnsList={setColumnsList}
                                showSelector={showSelector}
                                displayedColumns={displayedColumns}
                                setDisplayedColumns={setDisplayedColumns}
                                setOrderDict={setOrderDict}
                                orderDict={orderDict}
                                setAddedColumn={setAddedColumn}
                            />
                        )}
                        <TableBody>
                            {researchItemData && researchItemData.map((item, index) => {
                                if (item) {
                                    const isItemSelected = isSelected(item.id);
                                    const labelId = `enhanced-table-checkbox-${index}`;
                                    return (
                                        <TableRow
                                            hover
                                            role="checkbox"
                                            aria-checked={isItemSelected}
                                            tabIndex={-1}
                                            key={item.id}
                                            selected={isItemSelected}
                                        >
                                            {showSelector &&
                                                <TableCell padding="checkbox">
                                                    <Checkbox
                                                        color="primary"
                                                        checked={isItemSelected}
                                                        onClick={(event) => multiSelectStore.toggleSelected(item.id)}
                                                        inputProps={{
                                                            'aria-labelledby': labelId,
                                                        }}
                                                    />
                                                </TableCell>
                                            }
                                            {columnsList.map((column, index) => {
                                                if (column.key === "name") {
                                                    return (
                                                        <TableCell
                                                            component="th"
                                                            scope="row"
                                                            padding="none"
                                                            align="center"
                                                            height={"40px"}
                                                        >
                                                            <Link onClick={() => nameClicked(item)}
                                                                  style={{cursor: "pointer"}}>
                                                                {(column["key"] in item) && item[column["key"]]}
                                                                {(item.id in columnData) && (column.id in columnData[item.id]) &&
                                                                    columnData[item.id][column.id]["value"]}
                                                            </Link>


                                                        </TableCell>

                                                    )
                                                } else {
                                                    return (
                                                        <React.Fragment key={index}>
                                                            {(column.key === "name")}
                                                            {(column.show) ? <TableCell
                                                                component="th"
                                                                scope="row"
                                                                padding="none"
                                                                align="center"
                                                                height={"40px"}
                                                            >
                                                                {(column["key"] in item) && item[column["key"]]}
                                                                {(item.id in columnData) && (column.id in columnData[item.id]) &&
                                                                    columnData[item.id][column.id]["value"]}

                                                            </TableCell> : null}
                                                        </React.Fragment>
                                                    )
                                                }

                                            })}

                                        </TableRow>
                                    );
                                }
                            })}
                        </TableBody>
                    </Table>
                </TableContainer>
            </Paper>
            <ResearchItemOverlay
                show={showItemOverlay !== false}
                onClose={() => setShowItemOverlay(false)}
                onExited={() => setShowItemOverlay(false)}
                group={group}
                project={project}
                groups={groups}
                mutateGroups={mutateGroups}
                data={[{
                    id: clickedItem.id,
                    group_id: clickedItem.group_id,
                    type: clickedItem.type.toLowerCase()
                }]}
            />
            <div style={{
                marginTop: "20px", marginBottom: "20px", marginLeft: "auto", marginRight: "auto",
                display: "flex"
            }}>

                {(maxIndex > 1) && <Pagination count={maxIndex} size={"small"} onChange={handlePageChange}
                    // siblingCount={siblingCount} boundaryCount={boundaryCount}
                                               showFirstButton={false}
                                               showLastButton={false}
                                               style={{marginRight: "auto", marginLeft: "auto"}}
                />}
            </div>
        </Box>

    );
}

export default EnhancedTable