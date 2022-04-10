import React, { useState } from 'react'
import { Range } from 'rc-slider';
import Form from 'react-bootstrap/Form'
import Row from 'react-bootstrap/Row'
import Col from 'react-bootstrap/Col'
import moment from 'moment'

import 'rc-slider/assets/index.css';

export default (props) => {
  const { selectDateRange } = props
  const startedDate = moment().subtract(365, 'days').format("YYYY-MM-DD")
  const endedDate = moment().format("YYYY-MM-DD")
  const [tradeStartDate, setTradeStartDate] = useState(startedDate);
  const [tradeEndDate, setTradeEndDate ] = useState(endedDate)
  
  const handleDateRangeChange = (rangeValue, isFlag) => {
    const startDate = moment(startedDate, "YYYY-MM-DD").add(rangeValue[0], 'days').format("YYYY-MM-DD")
    const endDate = moment(startedDate, "YYYY-MM-DD").add(rangeValue[1], 'days').format("YYYY-MM-DD")
    setTradeStartDate(startDate)
    setTradeEndDate(endDate)

    if ( isFlag ) {
      selectDateRange(startDate, endDate)  
    }
  }
  
  return (
    <Form.Group as={Row} className="hunter-multi-range-area">
      <input 
        type='text'
        className="hunter-form-control-input"
        value={tradeStartDate}
        disabled
      />
      <Range
        min={0}
        max={365}
        defaultValue={[0, 365]}
        step={1}
        onChange={(value) => {
          handleDateRangeChange(value, false)
        }}
        onAfterChange={(value) => {
          handleDateRangeChange(value, true)
        }}
      />
      <input 
        type='text'
        className="hunter-form-control-input"
        value={tradeEndDate}
        disabled
      />    
    </Form.Group>
)};