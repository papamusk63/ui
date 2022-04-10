import React, { useEffect, useState } from 'react';
import { Select, MenuItem } from '@material-ui/core';
import { useApiChartContext } from './contexts';
import { apiGetGoogleNews } from "api/Api"
import { format } from "d3-format";
import Autocomplete from '@mui/material/Autocomplete';
import TextField from '@mui/material/TextField';
import symbolListOptions from './master'


const Placeholder = ({ children }) => {
  return <div style={{color: '#aaa'}}>{children}</div>;
};

const selectStyles = {
  background: 'white',
  borderRadius: '5px',
  margin: '0 5px',
  padding: '0 0 0 15px'
}


const ChartOptions = () => {


  const {setLoading, setChartData} = useApiChartContext()
  const {sym, setSym, time, setTime, bar, setBar, close, setClose, ext, setExt} = useApiChartContext()

  useEffect(() =>  {
    const loadData =  () => {
      setLoading(true)

      if (!sym || !time || !bar || !close || !ext) return;

      const params = {
        symbol: sym,
        timeframe: time,
        bars: bar,
        close: close,
        extended_hours: ext,
      }

       apiGetGoogleNews(params).then(data => {
        setLoading(false)
        //
        // let data = []
        // rawData['values'].map(row => data.push({date: new Date(row[0]), open: +row[1], high: +row[2], low: +row[3], close: +row[4], volume: +row[6], haohx: 'Hoang Xuan Hao'}))

        setChartData(data)
      })
    }
    loadData()
  }, [sym, time, bar, close, ext])

  // const symbolList = [
  //   { label: 'BTC-USD', year: 1994 },
  //   { label: 'The Godfather', year: 1972 },
  //   { label: 'The Godfather: Part II', year: 1974 },
  // ]


  const [typingValue, setTypingValue] = useState('')


  return (
    <div className="d-flex stockchart-new-api-filters">
      {/* <Select displayEmpty style={selectStyles} placeholder="sym" value={sym} renderValue={
        sym !== "" ? undefined : () => <Placeholder>sym</Placeholder>
      } onChange={e => setSym(e.target.value)}>
        <MenuItem value="BTC-USD">BTC-USD</MenuItem>
        <MenuItem value="DOGE-USD">DOGE-USD</MenuItem>
        <MenuItem value="ETH-USD">ETH-USD</MenuItem>
        <MenuItem value="ADA-USD">ADA-USD</MenuItem>
        <MenuItem value="BCH-USD">BCH-USD</MenuItem>
      </Select> */}
      <Autocomplete
        className="stockchart-autocomplete"
        disablePortal={true}
        id={`autocomplete-`+Math.random()}
        options={symbolListOptions}
        renderInput={(params) => <TextField {...params} label="Symbols" variant={'filled'} />}
        value={sym}
        inputValue={typingValue}
        sx={{
          width: '150px'
        }}
        onChange={(event, newValue) => {
          console.log('onChange', newValue)
          if (!newValue) return
          setSym(newValue.value)
        }}
        onInputChange={(event, newInputValue) => {
          setTypingValue(newInputValue);
        }}
      />
      <Select displayEmpty style={selectStyles} placeholder="time" value={time} renderValue={
        time !== "" ? undefined : () => <Placeholder>time</Placeholder>
      } onChange={e => setTime(e.target.value)}>
        <MenuItem value="60mi">60mi</MenuItem>
        <MenuItem value="3ho">3ho</MenuItem>
        <MenuItem value="1da">1da</MenuItem>
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
  );
};

export default ChartOptions;