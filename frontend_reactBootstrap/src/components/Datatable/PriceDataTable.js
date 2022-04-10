import React, { useState, useEffect, useMemo } from "react";
import Select from 'react-select'
import { Link } from "react-router-dom";
import "react-datetime/css/react-datetime.css";
import {
  Collapse,
  DropdownToggle,
  DropdownMenu,
  DropdownItem,
  UncontrolledDropdown,
  NavLink,
  Nav,
} from "reactstrap";
import { useHistory } from "react-router-dom";

import { useAuth } from 'contexts/authContext';
import { getAllSymbols, filterPriceData } from 'api/Api'
import { currentDateString } from 'utils/helper'
import MultiRangeSlider from 'components/MultiRangeSlider/MultiRangeSliderNumber'
import { useCsvDownloadUpdate } from "contexts/CsvDownloadContext"
import ButtonCsvDownload from 'components/ButtonCsvDownload'
import {useDatatableLoading, useDatatable, usePagination, usePaginationUpdate} from "contexts/DatatableContext"
import HeiknDatatable from 'components/HeiknDatatablePrice'

const PriceDataTable = () => {
  const auth = useAuth();
  const history = useHistory();
  const [collapseOpen,] = React.useState(false)
  const [symbol, setSymbol] = React.useState({value: "GOOG", label: "GOOG"})
  const [timeFrame, setTimeFrame] = useState({ value: "1mi", label: "1m"});
  const [tradeStartDate, setTradeStartDate] = useState('2021-01-01')
  const [tradeEndDate, setTradeEndDate] = useState(currentDateString())
  const [optionsSymbol, setOptionsSymbol] = useState([])
  const [optionsTimeFrame] = useState([
    { value: "1mi", label: "1m" },
    { value: "1ho", label: "1h" },
    { value: "1da", label: "1d" }
  ])

  // handle pagination state
  const [currentPage, itemsPerPage,] = usePagination()
  const [, , setTotalItems] = usePaginationUpdate()

  const hearder_columns = useMemo(() => {
    return [
    {
      label: 'O',
      field: 'o',
      width: 200,
      attributes: {
        'aria-controls': 'DataTable',
        'aria-label': 'symbol',
      },
    },
    {
      label: 'H',
      field: 'h',
      width: 200,
    },
    {
      label: 'C',
      field: 'c',
      width: 200,
    },
    {
      label: 'L',
      field: 'l',
      width: 200,
    },
    {
      label: 'V',
      field: 'v',
      width: 200,
    },
    {
      label: 'Date',
      field: 'date',
      sort: 'price',
    },
  ]}, [])

  const [, setLoadingData] = useDatatableLoading()

  const [, setDatatable] = useDatatable({
    columns: hearder_columns,
    rows: [
    ],
  });

  const updateCsvDownload = useCsvDownloadUpdate();


  // updating datatable of price
  const getPriceTrades = async (symbol, timeFrame, tradeStartDate, tradeEndDate) => {
    setLoadingData(true)

    const trades_data = await filterPriceData(symbol, timeFrame, tradeStartDate, tradeEndDate, currentPage, itemsPerPage);

    setDatatable({
      columns: hearder_columns,
      rows: trades_data.candles
    })
    updateCsvDownload([...trades_data.candles])
    setTotalItems(trades_data.page_total)

    setLoadingData(false)
  }

  useEffect(() => {
    getPriceTrades(symbol.value, timeFrame.value, tradeStartDate, tradeEndDate)
  }, [symbol, timeFrame, hearder_columns, tradeStartDate, tradeEndDate, itemsPerPage, currentPage])


  useEffect(() => {
    const getSymbols = async () => {
      const res = await getAllSymbols()
      setOptionsSymbol(res)
    }
    getSymbols()
  }, [setOptionsSymbol])


  const handleSignout = () => {
    auth.signout()
    history.push('/login')
  }

  const handleSymbolChange = (e) => {
    setSymbol(e)
  }

  const handleTimeFrameChange = (e) => {
    setTimeFrame(e)
  }

  const selectDateRange = (startDate, endDate) => {
    setTradeStartDate(startDate)
    setTradeEndDate(endDate)
  }

  return (
    <div className="hunter-chart-container">
      <nav className="navbar navbar-expand navbar-dark bg-dark hunter-nav-bar">
        <div className="logo-title">
          <a href="/chart" className="hunter-navbar-brand">
            Search Engine
          </a>
        </div>
        <div className="navbar-nav mr-auto">
          <li className="nav-item">
            <Link to={"/chart"} className="nav-link"></Link>
          </li>
        </div>
        <Collapse navbar isOpen={collapseOpen}>
            <Nav className="ml-auto" navbar>
              <UncontrolledDropdown nav>
                <DropdownToggle
                  caret
                  color="default"
                  nav
                  onClick={(e) => e.preventDefault()}
                >
                  <div className="photo">
                    <img
                      alt="..."
                      src={require("assets/img/anime3.png").default}
                    />
                  </div>
                  <p className="d-lg-none">Log out</p>
                </DropdownToggle>
                <DropdownMenu className="dropdown-navbar" right tag="ul">
                  <DropdownItem divider tag="li" />
                  <NavLink tag="li">
                    <DropdownItem className="nav-item" onClick={() => {handleSignout()}}>Log out</DropdownItem>
                  </NavLink>
                </DropdownMenu>
              </UncontrolledDropdown>
              <li className="separator d-lg-none" />
            </Nav>
          </Collapse>
      </nav>
      <div className="col-sm-12 hunter-data-table-container">
        <div className="hunter-data-table-title">
          Price Data Table
        </div>
        <div className="hunter-search-filter-area">
          <div className="select-option">
            <Select
              value={symbol}
              onChange={handleSymbolChange}
              options={optionsSymbol}
              placeholder="Symbol"
            />
          </div>
          <div className="select-option">
            <Select
              value={timeFrame}
              onChange={handleTimeFrameChange}
              options={optionsTimeFrame}
              placeholder="Time Frame"
            />
          </div>
          <div className='input-group date hunter-date-time-picker' id='datetimepicker1'>
            {/* <MultiRangeSlider
              selectDateRange={selectDateRange}
            /> */}
            <ButtonCsvDownload filename={"price.csv"}>Csv Download</ButtonCsvDownload>
          </div>
        </div>
        <HeiknDatatable />
      </div>
    </div>
  );
};

export default PriceDataTable;
