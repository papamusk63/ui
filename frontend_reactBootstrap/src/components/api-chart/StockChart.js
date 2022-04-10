import React, { useEffect, useState } from 'react';
import axios from 'axios'
import {PropTypes} from 'prop-types'
import {rawData} from './api-data'
import { scaleTime } from "d3-scale";
import { ChartCanvas, Chart } from "react-stockcharts";
import { CandlestickSeries } from "react-stockcharts/lib/series";
import { XAxis, YAxis } from "react-stockcharts/lib/axes";
import { utcDay } from "d3-time";
import {fitWidth} from 'react-stockcharts/lib/helper'
import {timeIntervalBarWidth, last} from 'react-stockcharts/lib/utils'
import { discontinuousTimeScaleProvider } from "react-stockcharts/lib/scale";
import { atr, ema, macd, heikinAshi } from "react-stockcharts/lib/indicator";
import { Select, MenuItem } from '@material-ui/core';
import { withStyles } from "@material-ui/core/styles";
import { apiGetGoogleNews } from "api/Api"

let StockChart = (props) => {

  const [sym, setSym] = useState("TSLA")
  const [time, setTime] = useState("3ho")
  const [bar, setBar] = useState("150")
  const [close, setClose] = useState("false")
  const [ext, setExt] = useState("true")
  // const [sym, setSym] = useState("")
  // const [time, setTime] = useState("")
  // const [bar, setBar] = useState("")
  // const [close, setClose] = useState("")
  // const [ext, setExt] = useState("")

  const xAccessor = (d) => {
    if (d == undefined) return new Date()
    return d.date
  }

  const [isLoading, setLoading] = useState(false)
  const [chartData, setChartData] = useState([])

  let xExtents = false

  useEffect(() => {
    setLoading(true)
    const params = {
      symbol: sym,
      timeframe: time,
      bars: bar,
      close: close,
      extended_hours: ext,
    }

    apiGetGoogleNews(params).then(result => {
      setLoading(false)
      if (!sym || !time || !bar || !close || !ext) return;
      let data = []
      let rawData = result
      rawData['values'].map(row => data.push({date: new Date(row[0]), open: row[1], high: row[2], low: row[3], close: row[4], volume: row[6],}))

      setChartData(data)

      xExtents = [
        xAccessor(last(data)),
        xAccessor(data[data.length-100]),
      ];

    })
  }, [sym, time, bar, close, ext])




  const Placeholder = ({ children }) => {
    return <div style={{color: '#aaa'}}>{children}</div>;
  };




  const { type, width, ratio } = props;

  const selectStyles = {
    background: 'white',
    borderRadius: '5px',
    margin: '0 5px',
    padding: '0 0 0 15px'
  }




  return (
    <>
      <div className="stockchart-new-api">
        <div className="d-flex stockchart-new-api-filters">
          <Select displayEmpty style={selectStyles} placeholder="sym" value={sym} renderValue={
            sym !== "" ? undefined : () => <Placeholder>sym</Placeholder>
          } onChange={e => setSym(e.target.value)}>
            <MenuItem value="TSLA">TSLA</MenuItem>
            <MenuItem value="BCH">BCH</MenuItem>
            <MenuItem value="GOOG">GOOG</MenuItem>
            <MenuItem value="BTC">BTC</MenuItem>
          </Select>
          <Select displayEmpty style={selectStyles} placeholder="time" value={time} renderValue={
            time !== "" ? undefined : () => <Placeholder>time</Placeholder>
          } onChange={e => setTime(e.target.value)}>
            <MenuItem value="3ho">3ho</MenuItem>
          </Select>
          <Select displayEmpty style={selectStyles} placeholder="bar" value={bar} renderValue={
            bar !== "" ? undefined : () => <Placeholder>bar</Placeholder>
          } onChange={e => setBar(e.target.value)}>
            <MenuItem value={'100'}>100</MenuItem>
            <MenuItem value={'150'}>150</MenuItem>
            <MenuItem value={'200'}>200</MenuItem>
          </Select>
          <Select displayEmpty style={selectStyles} placeholder="close" value={close} renderValue={
            close !== "" ? undefined : () => <Placeholder>close</Placeholder>
          } onChange={e => setClose(e.target.value)}>
            <MenuItem value="false">false</MenuItem>
            <MenuItem value="true">true</MenuItem>
          </Select>
          <Select displayEmpty style={selectStyles} placeholder="ext_" value={ext} renderValue={
            ext !== "" ? undefined : () => <Placeholder>ext</Placeholder>
          } onChange={e => setExt(e.target.value)}>
            <MenuItem value="false">false</MenuItem>
            <MenuItem value="true">true</MenuItem>
          </Select>
        </div>
        {isLoading ? <div className="hunter-loadding-status-text">Loading...</div> :
          <>
            {xExtents && <ChartCanvas
              plotFull
              height={400}
              ratio={ratio}
              width={width}
              margin={{left: 50, right: 50, top: 10, bottom: 30}}
              type={type}
              seriesName="MSFT"
              xAccessor={xAccessor}
              xScale={1}
              xExtents={xExtents}
              data={chartData}
            >
              <Chart
                yExtents={(d) => [d.high, d.low]}
              >
                <XAxis axisAt="bottom" orient="bottom" ticks={6} />
                <YAxis axisAt="left" orient="left" ticks={5} />
                <CandlestickSeries width={timeIntervalBarWidth(utcDay)} />
              </Chart>
            </ChartCanvas>}
          </>
        }
      </div>
    </>
  );
};

StockChart.prototype = {
  data: PropTypes.array.isRequired,
  width: PropTypes.array.isRequired,
  ratio: PropTypes.array.isRequired,
  type: PropTypes.oneOf(['svg', 'hybrid']).isRequired,
}

StockChart.defaultProps = {
  type: 'svg',
  ratio: 1,

}
// StockChart = fitWidth(StockChart)
export default StockChart;