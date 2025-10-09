import Notebook from "../components/Notebook";
import { useParams } from "react-router";

const NotebookPage = () => {
  let params = useParams();

  return (
    <Notebook notebookId={params.notebookId} height="100vh" />
  );
}

export default NotebookPage;
