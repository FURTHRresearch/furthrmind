import { Button } from "@mui/material";
import React, { useState } from "react";
import KeyImage from "../images/key.png";
import classes from "./ApiPageStyle.module.css";

import useSWR from "swr";
import GenerateToken from "../components/Overlays/GenerateApiToken";
import TokenListing from '../components/TokenListing/tokenListing';

const fetcher = (url) => fetch(url).then((res) => res.json());

export default function ApiPage() {
  const [showGenerateTokenModal, setShowGenerateTokenModal] = useState(false);
  const [tokenList, setTokenList] = useState([]);
  const handleGenerateToken = () => {
    setShowGenerateTokenModal(true);
  };

  const { data: keys } = useSWR('/web/apikeys', fetcher);

  const handleGenerateTokenModal = () => {
    setShowGenerateTokenModal(true);
  }

  const handleDeleteToken = () => {
    setTokenList([])
  }

  return (
    <React.Fragment>
      <div className={classes.boxWrapper2}>
        {(!keys || keys.length === 0) && (
          <div className={classes.apiWrapper}>
            <img src={KeyImage} width="400px" height="200px" alt="token" />
            <div className={classes.apiTitle}>Personal Access Token</div>
            <div className={classes.apiSubTitle}>
              Personal access tokens function like a combined name and password
              for API Authentication. Generate an Access Token to access the <a className={classes.brand} href="https://app.swaggerhub.com/apis-docs/furthr-research/API2/1.0.0" target='_blank' rel='noreferrer'>
                FURTHRmind API
              </a>.
            </div>

            <Button
              variant="contained"
              disableElevation
              sx={{
                backgroundColor: "#23A6F0",
                paddingLeft: "50px",
                paddingRight: "50px",
                marginTop: "20px",
              }}
              onClick={handleGenerateToken}
            >
              Generate New Token
            </Button>
          </div>
        )}

        {keys && keys.length > 0 && <TokenListing
          handleGenerateTokenModal={handleGenerateTokenModal}
          handleDeleteToken={handleDeleteToken}
          tokenList={tokenList} />}
      </div>
      {showGenerateTokenModal && (
        <GenerateToken
          open={showGenerateTokenModal}
          setOpen={setShowGenerateTokenModal}
        />
      )}
    </React.Fragment>
  );
}
