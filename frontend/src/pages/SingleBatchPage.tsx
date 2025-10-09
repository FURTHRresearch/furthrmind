import { Skeleton } from "@mui/material";
import { useParams } from "react-router";
import useSWR from "swr";

import { BatchCard } from "./InventoryBatchPage";

var fetcher = (url: string) => fetch(url).then(r => r.json());

const Batch = () => {
  const { batchId } = useParams();

  const { data: batch } = useSWR("/web/inventory/batches/" + batchId, fetcher);

  return (
    <>
      {batch ? <BatchCard batch={batch} /> : <Skeleton height={600} />}
    </>
  );
}

export default Batch;