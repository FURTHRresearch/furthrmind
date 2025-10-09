import "bootstrap/dist/css/bootstrap.min.css";
import {Suspense} from 'react';
import {Navigate, Outlet, Route, Routes} from "react-router-dom";
import useSWR from 'swr';
import {useState} from "react";

import AdminPanelPage from "./pages/AdminPanelPage";
import DataBrowserPage from "./pages/DataBrowserPage";
import DataViewPage from "./pages/DataViewPage";
import ExperimentPage from "./pages/ExperimentPage";
import ResearchItemPage from "./pages/ResearchItemPage";
import SamplePage from "./pages/SamplePage";

import AppPage from "./pages/AppPage";
import LdapSignUpPage from "./pages/LdapSignUpPage";
import LoginPage from "./pages/LoginPage";
import NotebookPage from "./pages/NotebookPage";
import ProjectDashboard from './pages/ProjectDashboard';
import ProjectSettings from "./pages/ProjectSettings";
import Projects from "./pages/ProjectsPage";
import SpreadsheetEditorPage from "./pages/SpreadsheetEditorPage";
import UserProfilePage from "./pages/UserProfilePage";

const fetcher = (url) => fetch(url).then((res) => res.json());
// const [db, setDemo] = useState(false)
const demo = false

const App = () => {
    return (
        <>
            <Suspense fallback={<div>Loading...</div>}>
                <Routes>
                    <Route path="/" element={<Navigate to="/projects"/>}/>
                    <Route element={<ProtectedRoute/>}>
                        <Route path="/projects" element={<Projects/>}/>
                        <Route path="/projects/:project/experiments/:expid" element={<ExperimentPage/>}/>
                        <Route path="/projects/:project/samples/:sampleid" element={<SamplePage/>}/>
                        <Route path="/projects/:project/researchitems/:researchitemid" element={<ResearchItemPage/>}/>

                        <Route path="/admin" element={<AdminPanelPage/>}/>
                        <Route path="/projects/:project/:id/spreadsheeteditor"
                               element={<SpreadsheetEditorPage/>}/>
                        <Route path="/settings/*" element={<UserProfilePage/>}/>
                        <Route path="/projects/:project/data" element={<DataBrowserPage/>}/>
                        <Route path="/notebooks/:notebookId" element={<NotebookPage/>}/>
                        <Route path="/projects/:project/settings" element={<ProjectSettings/>}/>
                        <Route path="/projects/:project/apps" element={<AppPage/>}/>
                        <Route path="/projects/:project/dashboard" element={<ProjectDashboard/>}/>
                        <Route path="/projects/:project/dataviews/:dataviewid" element={<DataViewPage/>}/>

                    </Route>
                    <Route path="/ldap-signup" element={<LdapSignUpPage/>}/>
                    <Route path="/login" element={<LoginPage/>}/>
                    <Route path="/signup" element={<LoginPage/>}/>
                    <Route path="/set-password" element={<LoginPage/>}/>
                    <Route path="/password-reset" element={<LoginPage/>}/>
                    <Route path="/*" element={<Navigate to="/projects"/>}/>
                </Routes>
            </Suspense>
        </>
    );
};

export default App;

function ProtectedRoute() {
    const {data} = useSWR(`/web/isloggedin`, fetcher);
    const notLoggedIn = (data?.isLoggedIn === false);
    return (notLoggedIn ? <Navigate to={'/login'}/> : <Outlet/>)
}
