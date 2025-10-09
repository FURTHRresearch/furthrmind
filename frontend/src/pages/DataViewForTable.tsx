import SaveIcon from "@mui/icons-material/Save";
import { LoadingButton, Skeleton } from "@mui/lab";
import DataGrid, { SelectCellFormatter, TextEditor } from 'react-data-grid';
import CloseIcon from '@mui/icons-material/Close';
import IconButton from '@mui/material/IconButton';
import { Typography, Box } from "@mui/material";
import FormControl from "@mui/material/FormControl";
import Grid from "@mui/material/Grid";
import InputLabel from "@mui/material/InputLabel";
import MenuItem from "@mui/material/MenuItem";
import Paper from "@mui/material/Paper";
import Select from "@mui/material/Select";
import Stack from "@mui/material/Stack";
import axios from "axios";
import {
    Chart as ChartJS, Legend, LinearScale, LineElement, PointElement, Tooltip
} from "chart.js";
import { default as React, useMemo, useState } from "react";
import { Scatter } from "react-chartjs-2";
import { useNavigate, useParams } from "react-router-dom";
import useSWR from "swr";
import SideDrawer from "../components/SideDrawer";
import classes from "./DashboardStyle.module.css";

ChartJS.register(LinearScale, PointElement, LineElement, Tooltip, Legend);

const fetcher = (url) => fetch(url).then((res) => res.json());

const DataViewForTable = (props) => {

    const params = useParams();
    const [viewAll, setViewAll] = useState(false);
    const { data } = useSWR(`/web/units?project=${'project' in params ? params.project : ''}`, fetcher);
    const { data: charts } = useSWR(
        `/dataviews/${params.dataviewid}/charts`,
        fetcher
    );

    const chartData = useMemo(() => {
        if (charts && charts.length > 0) {
            return charts.find((chart) => chart.id === params.chartid);
        } else return undefined;
    }, [charts, params.chartid]);

    return (
        <>

            <Box px={7} py={4}>
                <Stack
                    justifyContent="space-between"
                    direction="row"
                    alignItems="flex-start"
                    my={3}
                >
                    <Stack direction="column" spacing={1}>
                        <div className={classes.heading}>
                            Creat chart
                            </div>
                        <Typography variant="subtitle1" mt={1} sx={{ color: "gray" }}>
                            Select x axis and y axis below to generate chart from the dataset.
                        </Typography>
                    </Stack>
                    <IconButton aria-label="close" onClick={props.onClose}>
                        <CloseIcon />
                    </IconButton>
                </Stack>
                <div>
                    <div>
                        <div style={{ overflowX: "auto", whiteSpace: "nowrap" }}>
                            {/* {chartData &&
                                <Paper
                                    sx={{
                                        padding: "16px",
                                        margin: "16px 16px 16px 0",
                                        width: "100%",
                                        display: "inline-block",
                                        border: '1px solid black'
                                    }}
                                >
                                    <DataViewChartEditor
                                        data={data}
                                        initialChart={chartData}
                                        editMode={true}
                                    />
                                </Paper>
                            } */}
                            {/* Adding new option should not be there  */}

                            <Paper
                                sx={{
                                    padding: "16px",
                                    margin: "16px 0",
                                    width: "750px",
                                    display: "inline-block",
                                    border: '1px solid black'
                                }}
                            >
                                <DataViewChartEditor data={data} editMode={true} columns={props.columns} />
                            </Paper>

                        </div>
                    </div>


                </div>
            </Box>

        </>
    );
};

export default DataViewForTable;

function DataViewChartEditor(props) {
    const { data, initialChart, editMode, columns } = props;
    const [xAxis, setXAxis] = React.useState(initialChart?.xAxis || "");
    const [yAxis, setYAxis] = React.useState(initialChart?.yAxis || "");
    const [savingChart, setSavingChart] = React.useState(false);
    const columnNames = columns || [];
    const params = useParams();
    const navigate = useNavigate();

    const saveChart = () => {
        setSavingChart(true);
        let route = initialChart?.id
            ? `/dataviewcharts/${initialChart.id}`
            : `/dataviews/${params.dataviewid}/charts`;
        axios
            .post(route, {
                name: `${xAxis} vs ${yAxis}`,
                xAxis: xAxis,
                yAxis: yAxis,
            })
            .then((r) => {
                setSavingChart(false);
                navigate(`/projects/${params.project}/dashboard`)
            });
    };

    return (
        <>
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
                                <MenuItem value={n.name}>{n.name}</MenuItem>
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
                                <MenuItem value={n.name} key={n.key}>{n.name}</MenuItem>
                            ))}
                        </Select>
                    </FormControl>
                </Grid>
                <Grid item xs={2}>
                    <LoadingButton
                        disabled={!(xAxis && yAxis)}
                        loading={savingChart}
                        onClick={saveChart}
                        variant="outlined"
                        color="primary"
                        startIcon={<SaveIcon />}
                        sx={{ height: "100%" }}
                    >
                        Save
          </LoadingButton>
                </Grid>
            </Grid>
            {xAxis && yAxis && data && (
                <ScatterChart data={data} chart={{ xAxis, yAxis }} />
            )}
        </>
    );
}

function ScatterChart({ chart, data }) {
    const { xAxis, yAxis } = chart;
    return (<Scatter
        data={{
            datasets: [
                {
                    label: `${xAxis} vs ${yAxis}`,
                    data: data.map((d) => {
                        return { x: d[xAxis], y: d[yAxis] };
                    }),
                    backgroundColor: "rgba(255, 99, 132, 1)",
                },
            ],
        }}
        options={{
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
        }}
    />)
}
