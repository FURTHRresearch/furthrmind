import Box from '@mui/material/Box';
import {CircularProgress, Typography} from "@mui/material";
import FormControl from "@mui/material/FormControl";
import Grid from "@mui/material/Grid";
import InputLabel from "@mui/material/InputLabel";
import MenuItem from "@mui/material/MenuItem";
import Paper from "@mui/material/Paper";
import Select from "@mui/material/Select";
import Stack from "@mui/material/Stack";
import TableContainer from "@mui/material/TableContainer";
import axios from "axios";
import {Chart as ChartJS, Legend, LinearScale, LineElement, PointElement, Tooltip} from "chart.js";
import {default as React, useEffect, useState} from "react";
import {Scatter} from "react-chartjs-2";
import {useLocation, useNavigate, useParams} from "react-router-dom";
import SideDrawer from "../components/SideDrawer";
import FilterBar from "../components/SearchBar/FilterBar";
import TableView from "../components/TableView/tableView";
import Button from "@mui/material/Button";
import useFilterStore from "../zustand/filterStore";
import EditIcon from "@mui/icons-material/Edit";
import {useWindowWidth} from "@react-hook/window-size";
import classes from './DataViewPage.module.css';
import excelSvg from "../images/excelPng.png";
import IconButton from "@mui/material/IconButton";
import useDebouncedEffect from "../hooks/useDebouncedEffect";
import usePageIndexDashboard from "../hooks/usePageIndexDashboard";


ChartJS.register(LinearScale, PointElement, LineElement, Tooltip, Legend);

const fetcher = (url) => fetch(url).then((res) => res.json());


export default function DataViewPage(props) {

    const params = useParams();

    const [name, setName] = useState();
    const [dataview, setDataView] = useState(undefined);
    const [dataViewLoaded, setDataViewLoaded] = useState(false);
    const [reloadChart, setReloadChart] = useState(0);
    const [plotData, setPlotData] = useState([]);
    const [plotDataLoading, setPlotDataLoading] = useState(false);
    const [savingDone, setSavingDone] = useState(false)
    const [displayedColumns, setDisplayedColumns] = useState([]);
    const [filterApplied, setFilterApplied] = useState(false);

    const [xAxis, setXAxis] = useState('');
    const [yAxis, setYAxis] = useState('');
    const [chartName, setChartName] = useState('');
    const [chartLoaded, setChartLoaded] = useState(false);

    const location = useLocation();
    const resetFilter = location.state.resetFilter
    const filterStore = useFilterStore();

    const filterList = useFilterStore(
        (state) => state.filterList
    );

    const nameFilter = useFilterStore(
        (state) => state.nameFilter
    );

    const includeLinked = useFilterStore(
        (state) => state.includeLinked
    );

    const displayedCategories = useFilterStore(
        (state) => state.displayedCategories
    );

    const pageItemIndex = usePageIndexDashboard(params.dataviewid)

    useEffect(() => {
        axios.get(`/dataviews/${params.dataviewid}`).then(
            (response) => {
                const data = response.data
                setDataView(data);
                setName(data.Name);

                setDisplayedColumns(data.DisplayedColumns);
                if (resetFilter === true) {
                    filterStore.resetFilter();
                    data.FilterList.map((filter) => {
                        filterStore.saveFilter(filter)
                    })
                    filterStore.setNameFilter(data.NameFilter)
                    filterStore.setIncludeLinked(data.IncludeLinked)
                    filterStore.setDisplayedCategories(data.DisplayedCategories)
                }
                setDataViewLoaded(true);
            })

    }, []);

    useEffect(() => {
        if (dataViewLoaded) {
            axios.get(`/dataviews/${dataview.id}/charts`).then((response) => {
                setXAxis(response.data.xAxis);
                setYAxis(response.data.yAxis);
                setChartName(response.data.name);
                setChartLoaded(true)
            })
        }
    }, [dataViewLoaded])

    useDebouncedEffect(() => {
            if (dataViewLoaded) {
                setSavingDone(false);
                axios.post(`/dataviews/${dataview.id}`, {
                    name,
                    displayedColumns
                }).then((res) => {
                    setSavingDone(true)
                    axios.get(`/dataviews/${dataview.id}`).then(
                        (response) => {
                            setDataView(response.data);
                        })
                    // axios.get(`/dataviews/${dataview.id}/data`).then((res) => {
                    //     setPlotData(res.data)
                    // })

                })
            }
        }, 500, [name, displayedColumns]
    )


    useDebouncedEffect(() => {
            if (dataViewLoaded) {
                setSavingDone(false);
                axios.post(`/dataviews/${dataview.id}`, {
                    filterList,
                }).then((res) => {
                    setSavingDone(true)
                    axios.get(`/dataviews/${dataview.id}`).then(
                        (response) => {
                            setDataView(response.data);
                        })
                    // axios.get(`/dataviews/${dataview.id}/data`).then((res) => {
                    //     setPlotData(res.data)
                    // })

                })
            }
        }, 500, [filterList]
    )

    useDebouncedEffect(() => {
            if (dataViewLoaded) {
                setSavingDone(false);
                axios.post(`/dataviews/${dataview.id}`, {
                    nameFilter,
                }).then((res) => {
                    setSavingDone(true)
                    axios.get(`/dataviews/${dataview.id}`).then(
                        (response) => {
                            setDataView(response.data);
                        })
                    // axios.get(`/dataviews/${dataview.id}/data`).then((res) => {
                    //     setPlotData(res.data)
                    // })

                })
            }
        }, 500, [nameFilter]
    )

    useDebouncedEffect(() => {
            if (dataViewLoaded) {
                setSavingDone(false);
                axios.post(`/dataviews/${dataview.id}`, {
                    includeLinked,
                }).then((res) => {
                    setSavingDone(true)
                    axios.get(`/dataviews/${dataview.id}`).then(
                        (response) => {
                            setDataView(response.data);
                        })
                    // axios.get(`/dataviews/${dataview.id}/data`).then((res) => {
                    //     setPlotData(res.data)
                    // })

                })
            }
        }, 500, [includeLinked]
    )

    useDebouncedEffect(() => {
            if (dataViewLoaded) {
                setSavingDone(false);
                axios.post(`/dataviews/${dataview.id}`, {
                    displayedCategories,
                }).then((res) => {
                    setSavingDone(true)
                    axios.get(`/dataviews/${dataview.id}`).then(
                        (response) => {
                            setDataView(response.data);
                        })
                    // axios.get(`/dataviews/${dataview.id}/data`).then((res) => {
                    //     setPlotData(res.data)
                    // })

                })
            }
        }, 500, [displayedCategories]
    )

    // useEffect(() => {
    //         if (dataViewLoaded) {
    //             axios.get(`/dataviews/${dataview.id}/data`).then((res) => {
    //                 setPlotData(res.data)
    //             })
    //
    //         }
    //     }
    //     ,
    //     [dataViewLoaded]
    // )

    useEffect(() => {
        setPlotDataLoading(true)
        if (chartLoaded !== false) {
            let route = `/dataviews/${params.dataviewid}/charts`
            setChartName(`${xAxis} vs ${yAxis}`)
            axios.post(route, {
                name: `${xAxis} vs ${yAxis}`,
                xAxis: xAxis,
                yAxis: yAxis,
            }).then(() => {
                    setReloadChart(reloadChart + 1)
                    // axios.get(`/dataviews/${dataview.id}/data`).then((res) => {
                    //     setPlotData(res.data)
                    // })
                }
            )
        }


    }, [xAxis, yAxis])

    useDebouncedEffect(() => {
        if (dataViewLoaded && pageItemIndex) {
            setPlotDataLoading(true)
            axios.get(`/dataviews/${dataview.id}/data`).then((res) => {
                setPlotData(res.data)
                setPlotDataLoading(false)
            })
        }
    }, 500, [pageItemIndex, dataViewLoaded, chartLoaded, reloadChart]);

    function openSpreadSheet() {
        const a = document.createElement('a')
        a.href = "/web/onlyoffice/dataview/" + params.dataviewid;
        document.body.appendChild(a)
        a.setAttribute('target', '_blank');
        a.click()
        document.body.removeChild(a)
    }

    useEffect(() => {
        if (filterList.length === 0 && nameFilter === "") {
            setFilterApplied(false)
        } else {
            setFilterApplied(true)
        }
    }, [filterList, nameFilter]);


    return (
        <>
            <div className={classes.pageStyle} style={{minHeight: "10vh"}}>
                <SideDrawer/>
                <div className={classes.pageInnerWrapper}>
                    <Box sx={{
                        maxWidth: "50%", background: "white", borderRadius: "8px", margin: "20px 0px",
                        padding: "16px",
                    }}>
                        {dataViewLoaded &&
                            <UpdateName
                                name={name}
                                setName={setName}
                                savingDone={savingDone}
                                openSpreadSheet={openSpreadSheet}
                            ></UpdateName>
                        }
                        <Typography> Specify a name for your data analysis view to save it permenatly and to open it
                            from the
                            dashboard overview
                        </Typography>

                        {/*<LoadingButton*/}
                        {/*    // disabled={!(xAxis && yAxis)}*/}
                        {/*    // loading={savingChart}*/}
                        {/*    // onClick={saveChart}*/}
                        {/*    variant="outlined"*/}
                        {/*    color="primary"*/}
                        {/*    startIcon={<SaveIcon/>}*/}
                        {/*    sx={{height: "100%"}}*/}
                        {/*>*/}
                        {/*    Save*/}
                        {/*</LoadingButton>*/}
                    </Box>
                    <div>
                        <div>
                            <div style={{overflowX: "auto", whiteSpace: "nowrap"}}>
                                {chartLoaded} {
                                <Paper
                                    sx={{
                                        padding: "16px",
                                        margin: "16px 16px 16px 0",
                                        width: "50%",
                                        display: "inline-block",
                                    }}
                                >
                                    <div className={classes.heading}>
                                        {params.chartid ? `Editing chart ` : "Data analysis chart"}
                                        <Typography>
                                            Numeric values will be displayed in SI units
                                        </Typography>
                                    </div>
                                    <Typography variant="subtitle1" mt={1}
                                                sx={{color: "gray", marginBottom: "30px"}}>
                                        {chartName}
                                    </Typography>
                                    <DataViewChartEditor
                                        data={plotData}
                                        xAxis={xAxis}
                                        yAxis={yAxis}
                                        setXAxis={setXAxis}
                                        setYAxis={setYAxis}
                                        editMode={true}
                                        chartName={chartName}
                                        loading={plotDataLoading}
                                        // setReloadChart={setReloadChart}
                                    />
                                </Paper>
                            }

                                {/* Adding new option should not be there  */}
                                {/*{!params.chartid && (*/}
                                {/*    <Paper*/}
                                {/*        sx={{*/}
                                {/*            padding: "16px",*/}
                                {/*            margin: "16px 0",*/}
                                {/*            width: "50%",*/}
                                {/*            display: "inline-block",*/}
                                {/*        }}*/}
                                {/*    >*/}
                                {/*        <DataViewChartEditor data={plotData} editMode={true}/>*/}
                                {/*    </Paper>*/}
                                {/*)}*/}
                            </div>
                        </div>
                        {/*<div>*/}
                        {/*    <Stack my={3}>*/}
                        {/*        <Grid container mt={2} spacing={2}>*/}
                        {/*            {charts && tableData &&*/}
                        {/*                charts.map((chart, index) => (*/}
                        {/*                    <Grid md={3} item>*/}
                        {/*                        <Paper>*/}
                        {/*                            <a href={`/projects/${params.project}/dataviews/${params.dataviewid}/charts/${chart.id}`}*/}
                        {/*                               target={'_blank'} rel='noreferrer'>*/}
                        {/*                                <ScatterChart*/}
                        {/*                                    data={tableData}*/}
                        {/*                                    chart={chart}*/}
                        {/*                                />*/}
                        {/*                            </a>*/}
                        {/*                        </Paper>*/}
                        {/*                    </Grid>*/}
                        {/*                ))}*/}
                        {/*        </Grid>*/}
                        {/*    </Stack>*/}
                        {/*</div>*/}


                        <Stack my={5}>
                            <Stack direction="column" spacing={1} mb={3}>
                                <div className={classes.heading}>Selected Data</div>
                                <Typography variant="subtitle1" mt={1} sx={{color: "gray"}}>
                                    Table generated from the data you selected
                                </Typography>
                            </Stack>
                            {dataViewLoaded &&
                                <FilterBar filterList={dataview.FilterList}
                                           nameFilter={dataview.NameFilter}
                                           displayedColumns={displayedColumns}
                                           setDisplayedColumns={setDisplayedColumns}
                                           dataView={true}/>
                            }
                            {(filterApplied) ?
                                (<TableContainer component={Paper}>
                                    {/*<Table>*/}
                                    {/*    <TableHead>*/}
                                    {/*        <TableRow>*/}
                                    {/*            {Object.entries(data[0]).map(([k, v]) => (*/}
                                    {/*                <TableCell key={k}>{k}</TableCell>*/}
                                    {/*            ))}*/}
                                    {/*        </TableRow>*/}
                                    {/*    </TableHead>*/}
                                    {/*    <TableBody>*/}
                                    {/*        {data.slice(0, 100).map((r, i) => (*/}
                                    {/*            <TableRow*/}
                                    {/*                key={i}*/}
                                    {/*                sx={{*/}
                                    {/*                    "&:last-child td, &:last-child th": {border: 0},*/}
                                    {/*                }}*/}
                                    {/*            >*/}
                                    {/*                {Object.entries(r).map(([k, v]) => (*/}
                                    {/*                    <TableCell key={k}>{v}</TableCell>*/}
                                    {/*                ))}*/}
                                    {/*            </TableRow>*/}
                                    {/*        ))}*/}
                                    {/*    </TableBody>*/}
                                    {/*</Table>*/}
                                    {dataViewLoaded && <TableView
                                        group={undefined}
                                        project={params.project}
                                        showGroupProperties={false}
                                        showSelector={false}
                                        displayedColumns={displayedColumns}
                                        setDisplayedColumns={setDisplayedColumns}
                                        setCurrentGroup={null}
                                        items={null}
                                        maxPageAndPageItemMapping={pageItemIndex}
                                        dataViewId={dataview.id}
                                        groups={null}
                                        mutateGroups={null}
                                    />
                                    }

                                </TableContainer>) :
                                (
                                    <div style={{marginLeft: "auto", marginRight: "auto"}}>
                                        <Typography variant={"h6"}> No Filter applied. Please apply a filter to show
                                            your data. </Typography>
                                    </div>
                                )
                            }

                            {/*<div style={{textAlign: 'center', margin: '2em', fontWeight: 'bold'}}>*/}
                            {/*    {Math.max(activeResearchItems.length - 100, 0)} rows hidden*/}
                            {/*</div>*/}
                        </Stack>

                    </div>
                </div>
            </div>
        </>
    );
};

// export default DataViewPage;

function DataViewChartEditor(props) {
    const {data, name, xAxis, yAxis, setXAxis, setYAxis, loading} = props;


    const [columnNames, setColumnNames] = useState([])
    const [getAllFieldsStatus, setGetAllFieldsStatus] = useState(false)

    const getAllFields = () => {
        axios.get('/web/projects/' + params.project + '/fields').then(function (axiosTestResult) {
            const result_list = []
            axiosTestResult.data.map(field => {
                    if (field.type == "Numeric") {
                        result_list.push(field.name)
                    }

                }
            )
            setGetAllFieldsStatus(true)
            setColumnNames(result_list)

        })
    }

    useEffect(() => {
        getAllFields()
    }, [])

    const params = useParams();
    const navigate = useNavigate();


    return (
        <>  {getAllFieldsStatus &&
            <Grid container spacing={3} wrap="wrap" px={3}>
                <Grid item xs={5} md={4}>
                    <FormControl fullWidth>
                        <InputLabel>x axis</InputLabel>
                        <Select
                            value={xAxis}
                            label="x axis"
                            onChange={(e) => setXAxis(e.target.value)}
                        >
                            {columnNames.map((n) => (
                                <MenuItem value={n}>{n}</MenuItem>
                            ))}
                        </Select>

                    </FormControl>
                </Grid>
                <Grid item xs={5} md={4}>
                    <FormControl fullWidth>
                        <InputLabel>y axis</InputLabel>
                        <Select
                            value={yAxis}
                            label="y axis"
                            onChange={(e) => setYAxis(e.target.value)}
                        >
                            {columnNames.map((n) => (
                                <MenuItem value={n}>{n}</MenuItem>
                            ))}
                        </Select>
                    </FormControl>
                </Grid>
                <Grid item xs={5} md={4}>
                    {(loading) && <CircularProgress style={{marginLeft: "10px"}}></CircularProgress>}
                </Grid>

            </Grid>
        }
            {xAxis && yAxis && data && (
                <ScatterChart data={data} chart={{xAxis, yAxis}}/>
            )}
        </>
    );
}


function ScatterChart({
                          chart, data
                      }) {
    const {xAxis, yAxis} = chart;
    let options = {
        scales: {
            y: {
                title: {
                    display: true,
                    text: yAxis,
                },
            },
            x: {
                title: {
                    display: true,
                    text: xAxis,
                },
            },
        },
        plugins: {
            tooltip: {
                callbacks: {
                    label: function (ctx) {
                        let label = ctx.raw['name'];
                        label += " (" + ctx.parsed.x + ", " + ctx.parsed.y + ")";
                        return label;
                    }
                }
            }
        }
    }

    return (<Scatter
        data={{
            labels: data.map((d) => {
                d['name']
            }),
            datasets: [
                {
                    label: `${xAxis} vs ${yAxis}`,
                    data: data.map((d) => {
                        return {x: d[xAxis], y: d[yAxis], name: d['name']};
                    }),
                    backgroundColor: "rgba(255, 99, 132, 1)",
                },
            ],
        }}
        options={options}
    />)
}


const UpdateName = ({name, setName, savingDone, openSpreadSheet}) => {
    const onlyWidth = useWindowWidth();
    const [editMode, setEditMode] = React.useState(false);
    const [tempName, setTempName] = React.useState(name);

    function save() {
        setName(tempName);
    }

    useEffect(() => {
        if (savingDone) {
            setEditMode(false);
        }

    }, [savingDone]);

    return (
        <div className={classes.parentWrap}>
            <div className={classes.fieldWrap}>
                <div className={classes.heading}>
                    Data analysis name:
                </div>
                <div className={classes.textFieldOuterWrap}>
                    <div className={classes.textField}>
                        <input
                            type="text"
                            placeholder="Name"
                            className={!editMode ? classes.inputFieldReadOnly : classes.inputField}
                            value={tempName}
                            readOnly={!editMode}
                            onChange={(e) => {
                                setTempName(e.target.value)
                            }}
                        />
                        {!editMode &&
                            <EditIcon sx={{fontSize: onlyWidth < 576 ? "14px" : "18px", cursor: "pointer"}}
                                      onClick={() => setEditMode(true)}
                            />
                        }
                    </div>
                    {
                        editMode &&
                        <div className={classes.editStateWrap}>
                            <Button
                                variant="outlined"
                                size="small"
                                onClick={() => setEditMode(false)}
                            >Cancel</Button>
                            <Button variant="contained" size="small" onClick={save}>Save</Button>
                        </div>
                    }
                </div>
                <div style={{marginLeft: "auto", marginRight: "0px"}}>
                    <IconButton sx={{color: "black"}} onClick={openSpreadSheet}>
                        <img src={excelSvg} alt={""}/>
                    </IconButton>
                </div>


            </div>


        </div>

    )
}

