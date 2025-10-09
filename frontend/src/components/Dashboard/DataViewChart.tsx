import React, {memo, useEffect, useState} from "react";
import axios from "axios";
import {Scatter} from "react-chartjs-2";
import Skeleton from "@mui/material/Skeleton";

function DataViewChart({dataview, refreshChart, setRefreshChart}) {
    const {id, xAxis, yAxis} = dataview;
    const [data, setData] = useState([]);


    useEffect(() => {
        axios.get(`/dataviews/${dataview.id}/data_not_generated`).then(r => {
            setData(r.data);
        })
    }, []);


    useEffect(() => {
        if (refreshChart === dataview.id) {
            axios.get(`/dataviews/${dataview.id}/data`).then(r => {
                setData(r.data);
                setRefreshChart("")
            })
        }

    }, [refreshChart]);

    let options = {
        maintainAspectRatio: false,
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
    return (
        <>
            {data ? <Scatter data={{
                datasets: [
                    {
                        label: `${xAxis} vs ${yAxis}`,
                        data: data.map((d) => {
                            return {x: d[xAxis], y: d[yAxis], name: d['name']}
                        }),
                        backgroundColor: 'rgba(255, 99, 132, 1)',
                    }
                ]
            }}
                             options={options}/> : <Skeleton width="100%" height="100%"/>}
        </>
    )
}

export default memo(DataViewChart);