import NotebookOverlay from '../Overlays/NotebookOverlay';

import Button from '@mui/material/Button';
import Stack from '@mui/material/Stack';
import { useState } from 'react';
import classes from './DataCalcFieldStyle.module.css';
import FieldMenu from './FieldMenu';
import Tooltip from "@mui/material/Tooltip";

const NotebookField = ({ notebookId, label, initialTeaser = ' ', ...other }) => {
  const [showNotebook, setShowNotebook] = useState(false);

  return (
    <>
      <div className={classes.parentWrapper}>
          <Tooltip title={label} placement={"left"} enterDelay={400} enterNextDelay={400}>
              <Stack direction="row" spacing={2} alignItems="center" justifyContent='space-between'>
                  <div className={classes.labelCss}>{label}</div>
                  <Button size='small' onClick={() => setShowNotebook(true)}>Show Notebook</Button>
              </Stack>
          </Tooltip>


        {showNotebook ?
          <NotebookOverlay
            onClose={() => setShowNotebook(false)}
            show={showNotebook}
            notebookId={notebookId}
          /> : null}
      </div>
      {!other.menuDisabled && <FieldMenu label={label} {...other} />}
    </>
  );
}

export default NotebookField;
