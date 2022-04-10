import React from 'react';
import ChartGraphWrap from './ChartGraphWrap';
import ChartOptions from './ChartOptions';
import { ApiChartProvider } from './contexts';

import { fitWidth } from "react-stockcharts/lib/helper";
let TradeChart = (props) => {
  return (
    <ApiChartProvider>
      <ChartOptions />
      <ChartGraphWrap chartColumn={props.chartColumn.value} />
    </ApiChartProvider>
  );
};

TradeChart = fitWidth(TradeChart)
export default TradeChart;