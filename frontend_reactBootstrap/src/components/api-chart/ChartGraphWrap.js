import React from 'react';
import ChartGraph from './ChartGraph';
import { useApiChartContext } from './contexts';

import { fitWidth } from "react-stockcharts/lib/helper";

let ChartGraphWrap = (props) => {
  const {chartData} = useApiChartContext()
  const chartColumn = props.chartColumn

  const displayChart = () => {
    return <ChartGraph data={chartData} chartColumn={props.chartColumn} />
  }
  return (
    <>
      {(chartColumn === 1) && displayChart()}
      {(chartColumn === 2) && displayChart()}
      {(chartColumn === 4) && displayChart()}
      {(chartColumn === 6) && displayChart()}
    </>
  );
};

ChartGraphWrap = fitWidth(ChartGraphWrap)

export default ChartGraphWrap;