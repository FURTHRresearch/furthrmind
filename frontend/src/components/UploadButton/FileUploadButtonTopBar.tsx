import S3FileUploadButton from "./S3FileUploadButtonTopBar";
import TUSFileUploadButton from "./TUSFileUploadButtonTopBar";

import useSWRImmutable from 'swr/immutable';
const fetcher = url => fetch(url).then(res => res.json());

export default function ({ onUploaded }) {

  const { data: s3config } = useSWRImmutable('/web/s3', fetcher);

  return (
    (s3config && s3config.enabled) ? <S3FileUploadButton onUploaded={onUploaded} /> : <TUSFileUploadButton onUploaded={onUploaded} />
  )
}
