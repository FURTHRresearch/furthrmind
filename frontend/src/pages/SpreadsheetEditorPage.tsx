import { useParams } from 'react-router-dom';
import SideDrawer from '../components/SideDrawer';
import classes from './DashboardStyle.module.css';


export default function SpreadsheetEditorPage() {
  const params = useParams();

  return (
    <>
      <div className={classes.pageStyle} style={{ minHeight: '100vh' }}>
        <SideDrawer />
        <div className={classes.pageInnerWrapper} style={{ minHeight: '100vh', overflow: 'hidden', margin: '0 0 0 73px' }}>
          <div style={{ height: '100vh' }}>
            <iframe src={`/web/onlyoffice/${params.id}/None`} style={{ width: '100%', height: '100%' }} title={`Item ${params.id}`} />
          </div>
        </div>
      </div>
    </>
  );
}


