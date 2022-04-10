import { CSVLink } from "react-csv"
import { useCsvDownload } from "contexts/CsvDownloadContext"

const ButtonCsvDownload = (props) => {
  const dataset = useCsvDownload()
  return (
    <div className={"d-flex align-items-center"}>
      <CSVLink data={dataset} filename={props.filename} className={"btn btn-primary py-2 my-0 hunter-csv-download-button"}>Csv Download</CSVLink>
    </div>
  )
}

export default ButtonCsvDownload