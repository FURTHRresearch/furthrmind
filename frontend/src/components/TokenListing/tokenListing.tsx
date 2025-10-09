import { Box, Button, Typography } from '@mui/material';
import TokenListingTable from './tokenListingTable';
export default function TokenListing({ tokenList, handleGenerateTokenModal, handleDeleteToken }) {

    return (
        <Box mt={2}>
            <Box display='flex' justifyContent='space-between'>
                <Typography variant="subtitle1">Personal access token</Typography>
                <Button
                    variant='contained'
                    size='small'
                    disableElevation
                    onClick={handleGenerateTokenModal}
                >Generate Token</Button>
            </Box>
            <Box mt={3}>
                <TokenListingTable
                    rows={tokenList}
                    handleDeleteToken={handleDeleteToken} />
            </Box>
            <div style={{ marginTop: '16px', textAlign: 'right' }}>Use your token to access the <a href="https://app.swaggerhub.com/apis-docs/furthr-research/API2/1.0.0" target='_blank' rel='noreferrer'>
                FURTHRmind API
            </a>.</div>
        </Box>

    )
}
