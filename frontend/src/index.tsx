import { registerLicense } from '@syncfusion/ej2-base';
import React from 'react';
import ReactDOM from 'react-dom';
import App from './App';
import './index.css';

// import "@fontsource/lato/400.css";
// import "@fontsource/lato/700.css";
// import "@fontsource/montserrat/600.css";
// import "@fontsource/montserrat/700.css";
// import "@fontsource/open-sans/variable-full.css";
// import '@fontsource/pt-sans/400.css';
// import '@fontsource/pt-sans/700.css';
// import '@fontsource/roboto/400.css';
// import '@fontsource/roboto/500.css';
// import '@fontsource/roboto/700.css';


import {
  BrowserRouter
} from "react-router-dom";

registerLicense('MzQ0OTUyMEAzMjMwMmUzNDJlMzBOR0k0OTUydE9wU3VBM1EwdUF4NUxnb3pxVHVFc291S21GMGQ5NmRFQzdVPQ==;MzQ0OTUyMUAzMjMwMmUzNDJlMzBJbWhydmhyWDJJTUJ5OU9DVk1TWHZRcVh1eHloNU9VdlB2WnpIenJiaWFJPQ==;Mgo+DSMBaFt/QHRqVVhjVFpFdEBBXHxAd1p/VWJYdVt5flBPcDwsT3RfQFljQXxbd0RiW35bcXFUQA==;Mgo+DSMBPh8sVXJ0S0J+XE9HflRDX3xKf0x/TGpQb19xflBPallYVBYiSV9jS3pTfkdrWH5fcnVQR2ZbUw==;ORg4AjUWIQA/Gnt2VVhkQlFadVdJXGFWfVJpTGpQdk5xdV9DaVZUTWY/P1ZhSXxXdk1hUX5fcXZUQ2FaVkY=;NRAiBiAaIQQuGjN/V0Z+WE9EaFxKVmJLYVB3WmpQdldgdVRMZVVbQX9PIiBoS35RckVrW3dfcXVXR2VdWUZ/;MzQ0OTUyNkAzMjMwMmUzNDJlMzBWai9LNWFqTGx6RDF6S3V4bFlMYUVoT1BRRkpnYzNubmtkcURBbmRWWUc4PQ==;MzQ0OTUyN0AzMjMwMmUzNDJlMzBYZ0JvNmYvSXkybDFKQ2c4amR0ZmFaUHFmakh4Mjk1R3dtR2pXTkloT29jPQ==;Mgo+DSMBMAY9C3t2VVhkQlFadVdJXGFWfVJpTGpQdk5xdV9DaVZUTWY/P1ZhSXxXdk1hUX5fcXZUQ2JbVkQ=;MzQ0OTUyOUAzMjMwMmUzNDJlMzBtTUFmSCtwNlBZYno0VjJONjg3L25nUDQxNFJqYW1GRkEzS1BTck5mdU04PQ==;MzQ0OTUzMEAzMjMwMmUzNDJlMzBRRi9FWVB3ZFEzbDNGSS82QTJaZ0RXSmxDQkkxQXZFMFg2M1NRODNRU25rPQ==;MzQ0OTUzMUAzMjMwMmUzNDJlMzBWai9LNWFqTGx6RDF6S3V4bFlMYUVoT1BRRkpnYzNubmtkcURBbmRWWUc4PQ==');
ReactDOM.render(
  <React.StrictMode>
    <BrowserRouter>
      <App />
    </BrowserRouter>
  </React.StrictMode>,
  document.getElementById('root')
);
