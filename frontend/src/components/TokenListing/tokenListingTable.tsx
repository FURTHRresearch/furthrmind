import DeleteIcon from '@mui/icons-material/Delete';
import Box from '@mui/material/Box';
import IconButton from '@mui/material/IconButton';
import Paper from '@mui/material/Paper';
import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableContainer from '@mui/material/TableContainer';
import TableHead from '@mui/material/TableHead';
import TableRow from '@mui/material/TableRow';
import axios from 'axios';
import { zonedTimeToUtc } from 'date-fns-tz';
import formatDistanceToNow from 'date-fns/formatDistanceToNow';
import * as React from 'react';
import useSWR from 'swr';
import classes from './tokenListingStyle.module.css';

const fetcher = (url) => fetch(url).then((res) => res.json());

function Row(props) {
    const { tokenName, scope, tokenData, handleDeleteToken } = props;

    return (
        <React.Fragment>
            <TableRow sx={{ '& > *': { borderBottom: 'none' } }}>

                <TableCell component="th" scope="row">
                    {tokenName}
                </TableCell>
                <TableCell align="left">
                    <div className={classes.chipsWrapper}>
                        {scope.write && <div className={classes.chips}>Write</div>}
                        {scope.read && <div className={classes.chips}>Read</div>}
                    </div>
                </TableCell>
                <TableCell align='center'>
                    {tokenData.creationTime && formatDistanceToNow(zonedTimeToUtc(tokenData.creationTime, 'UTC')) + ' ago'}
                </TableCell>

                <TableCell align="right">
                    <Box display="flex" flexDirection='row' justifyContent='flex-end'>
                        <IconButton
                            aria-label="expand row"
                            size="small"
                            onClick={handleDeleteToken}>
                            <DeleteIcon sx={{ color: 'red' }} />
                        </IconButton>
                    </Box>
                </TableCell>
            </TableRow>
        </React.Fragment>
    );
}



export default function CollapsibleTable({ rows, handleDeleteToken }) {

    const { data: keys, mutate: mutateKeys } = useSWR('/web/apikeys', fetcher);
    const deleteToken = (id) => {
        axios.delete('/web/apikeys/' + id);
        mutateKeys(keys.filter(key => key.id !== id), false);
    }
    return (
        <TableContainer component={Paper} sx={{ maxHeight: 350 }}>
            <Table stickyHeader aria-label="sticky table">
                <TableHead>
                    <TableRow>
                        <TableCell>Name</TableCell>
                        <TableCell align="left">Scope</TableCell>
                        <TableCell align="center">Created</TableCell>
                        <TableCell />
                    </TableRow>
                </TableHead>
                <TableBody>
                    {keys.map((key, i) => (
                        <Row
                            tokenName={key.name}
                            tokenData={key}
                            scope={{
                                read: true,
                                write: true
                            }}
                            key={i}
                            handleDeleteToken={() => deleteToken(key.id)}
                        />
                    ))}
                </TableBody>
            </Table>
        </TableContainer>
    );
}
