import React, { useCallback, useEffect, useState, useMemo } from 'react'
import { Button, Input } from 'reactstrap'
import Modal from 'react-bootstrap/Modal'
// import BarChart from 'components/FinancialDashboard/SmallBarChart';
import { MDBTable, MDBTableBody, MDBTableHead } from 'mdbreact';
import WatchListEditColumnWidget from 'components/WatchListEditColumnWidget/WatchListEditColumnWidget'
import './WatchListItem.css'
import Select from 'react-select'

import { useCsvDownloadUpdate } from "contexts/CsvDownloadContext"

import { defaultFields, defaultItmes } from '../WatchListEditColumnWidget/components/modal/nodes'
import ButtonCsvDownload from 'components/ButtonCsvDownload'
import { useDatatableLoading, useDatatable, usePagination, usePaginationUpdate } from "contexts/DatatableContext"
import {
  getSearchingData
} from 'api/Api';

import { CSVLink } from "react-csv"

import { MDBDataTableV5 } from 'mdbreact';

const WatchListItem = (props) => {
  const [isLoadedWatchListOptions, setIsLoadedWatchListOptions] = useState(true)
  const [selectedColumns, setSelectedColumns] = useState(
    []
  );

  const [isLoading, setIsLoading] = useState(false);
  const [isOpenedEditColumnWidget, setIsOpenedEditColumnWidget] = useState(false)
  const [isUpdatedCols, setIsUpdatedCols] = useState(false)
  const [columnItems, setColumnItems] = useState([])
  const [totalHeader, setTotalHeader] = useState([])
  const [searchKey, setSearchKey] = useState('')
  const [csvData, setCsvData] = useState([])


  const handleColumnsChange = () => {
    setIsOpenedEditColumnWidget(true)
  }

  const handleSearching = () => {
    // console.log(searchKey)
    // console.log(selectedColumns)
    loadSearchingData(searchKey)
  }

  const handleModalClose = () => {
    setIsOpenedEditColumnWidget(false)
  }

  useEffect(() => {
    setIsLoadedWatchListOptions(true)
    loadTableData(NaN)
  }, [])

  const loadTableData = async (cols) => {
    const result = await getSearchingData();
    if (!result.success || result.data == undefined) return;
    setTotalHeader(result.data.header)
    let headerData = filterTableData(defaultFields)
    if (cols) {
      headerData = cols
    }
    const tableHeader = hearder_columns(headerData);
    let bodyData = result.data.rows
    bodyData.forEach(function (row, index) {
      for (let item in row) {
        if (!headerData.includes(item)) {
          delete bodyData[index][item]
        }
      }
    });
    setCsvData(bodyData)
    setDatatable({
      columns: tableHeader,
      rows: bodyData
    })

  }

  const loadSearchingData = async (keyString) => {
    if (keyString == '') {
      loadTableData(NaN);
      return
    }
    const result = await getSearchingData();
    if (!result.success || result.data == undefined) return;
    let headerData = columnItems
    if (headerData.length == 0) {
      headerData = filterTableData(defaultFields)
    }
    const tableHeader = hearder_columns(headerData);
    let bodyData = result.data.rows
    let searchingBody = []
    bodyData.forEach(function (row, index) {
      for (let item in row) {
        if (row[item].includes(keyString)) {
          searchingBody.push(row)
          break
        }
      }
    });
    setCsvData(searchingBody)
    setDatatable({
      columns: tableHeader,
      rows: searchingBody
    })

  }

  const filterTableData = (filterData) => {
    let filterItems = []
    filterData.forEach(function (itemTree, index) {
      if (itemTree.default) {
        itemTree.children.forEach(function (item, index) {
          filterItems.push(item.label)
        });
      }
    });
    return filterItems
  }

  const [datatable, setDatatable] = React.useState({
    columns: [],
    rows: []
  })


  const hearder_columns = (headerData) => {
    let table_header = []
    headerData.map(item => {
      if (item == 'Avg # Bars In Losing Trades: All') {
        table_header.push({
          label: 'Avg # Bars In Losing Trades: All',
          field: 'Avg # Bars In Losing Trades: All',
          width: 300,
          attributes: {
            'aria-controls': 'DataTable',
            'aria-label': 'Avg # Bars In Losing Trades: All',
          }
        })
      } else {
        table_header.push({
          label: item,
          field: item,
          width: 300,
        })
      }
    })

    return table_header
  }

  useEffect(() => {
    const getScannerAvailableFields = async () => {
      setSelectedColumns(defaultFields)
    }

    console.log(defaultFields)

    if (isLoadedWatchListOptions) {
      getScannerAvailableFields()
    }

  }, [isLoadedWatchListOptions])


  const handleColumnSet = (columns) => {
    let cols = []
    let temps = []
    let colObjects = []
    Object.keys(columns).forEach((key) => {
      columns[key].children.forEach((col) => {
        cols.push(col.label)
        temps.push(col.label)
      })

      colObjects.push({
        [columns[key].label]: temps
      })
      temps = []
    })
    setIsUpdatedCols(!isUpdatedCols)
    setColumnItems(cols)
    setSelectedColumns(columns)
    loadTableData(cols)

  }


  return (
    <div className="watch-list-item-container">
      <Modal show={isOpenedEditColumnWidget} className="hunter-widget-modal" onHide={() => handleModalClose()}>
        <WatchListEditColumnWidget
          handleModalClose={handleModalClose}
          setColumns={handleColumnSet}
          selectedColumns={selectedColumns}
        />
      </Modal>
      <div className="watch-list-item-wrap hunter-watch-list-item-wrap">
        <div className="watch-list-item-header">
          <Input placeholder="Search.." onChange={(event) => setSearchKey(event.target.value)} />
          <Button
            className=""
            onClick={() => { handleSearching() }}
          >
            <i class="fa fa-search"></i>
          </Button>
          <Button
            size="sm"
            className=""
            onClick={() => { handleColumnsChange() }}
          >
            change columns
          </Button>

        </div>
        <div className={"d-flex align-items-center"}>
          <CSVLink data={csvData} filename="search_result.csv" className={"btn btn-primary py-2 my-0 hunter-csv-download-button"}>Csv Download</CSVLink>
        </div>
        <div>
          <MDBDataTableV5 hover entriesOptions={[10, 15, 20, 25, 30]} entries={10} pagesAmount={4} data={datatable} fullPagination />
        </div>
      </div>
    </div>
  )
}

export default WatchListItem;