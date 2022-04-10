import React, { useEffect } from 'react';
import { useApiChartContext } from './contexts';
import { ChartCanvas, Chart } from "react-stockcharts";
import { CandlestickSeries } from "react-stockcharts/lib/series";
import { scaleTime } from "d3-scale";
import {timeIntervalBarWidth, last} from 'react-stockcharts/lib/utils'
import { utcDay, utcHour } from "d3-time";
import { XAxis, YAxis } from "react-stockcharts/lib/axes";
import { fitWidth } from "react-stockcharts/lib/helper";
import { discontinuousTimeScaleProvider } from "react-stockcharts/lib/scale";
import { format } from "d3-format";
import { withStyles } from "@material-ui/core";
import { HoverTooltip } from "react-stockcharts/lib/tooltip";
import {
	CrossHairCursor,
	MouseCoordinateX,
	MouseCoordinateY,
} from "react-stockcharts/lib/coordinates";

import dayjs from "dayjs";
import { timeFormat } from "d3-time-format";
import {
	OHLCTooltip,
	ToolTipText,
	SingleValueTooltip,
} from "react-stockcharts/lib/tooltip";
import {
	Annotate,
	SvgPathAnnotation,
	buyPath,
	sellPath,
} from "react-stockcharts/lib/annotation";
import {ema50, ema20, macdCalculator, ha, atr14, xScaleProvider} from './helpers'
import { apiGetTradeHistories } from 'api/Api';
const dateFormat = timeFormat("%Y-%m-%d");
const numberFormat = format(".2f");


function tooltipContent(symbol, ys) {
  let tradeData = []
	return ({ currentItem, xAccessor }) => {
    const loadData = async () => {
      await apiGetTradeHistories({symbol: symbol, date: currentItem.trade_date}).then(data => {
        tradeData = data
      })
    }

    loadData()

    return {
      x: `Ticker: ${symbol}`,
      y: tradeData
    }
		// return {
		// 	x: dateFormat(xAccessor(currentItem)),
		// 	y: currentItem.trade_data
		// 		.concat(
		// 			ys.map(each => ({
		// 				label: each.label,
		// 				value: each.value(currentItem),
		// 				stroke: each.stroke
		// 			}))
		// 		)
		// 		.filter(line => line.value)
		// };
	};
}


let ChartGraph = (props) => {
  const {isLoading} = useApiChartContext()
  const {sym} = useApiChartContext()


  // extract props
  const { type, data: initialData, width, ratio, chartColumn, extendMarketTime } = props;

  if (isLoading || initialData == null || !Array.isArray(initialData)) {
    return <div className="text-white">Loading...</div>
  }

  initialData.forEach(line => {
    line.date = dayjs(line.date).toDate();
  });

  const isFullChart = (chartColumn === 1 || chartColumn === 2);


  const calculateHeight = () => {
		if (chartColumn==6) {
			return 350;
		}
		if (chartColumn==4) {
			return 350;
		}
		if (chartColumn==2) {
			return 650;
		}
		if (chartColumn==1) {
			return 650;
		}
	}

  const calculatedData = macdCalculator((ha(atr14(initialData))));

  const xScaleProvider = discontinuousTimeScaleProvider
			.inputDateAccessor(d => d.date);
  const {
    data,
    xScale,
    xAccessor,
    displayXAccessor,
  } = xScaleProvider(calculatedData);


  // xExtents
  const start = xAccessor(last(data));
	const end = xAccessor(data[Math.max(0, data.length - 150)]);
	const xExtents = [start, end];

  const defaultAnnotationProps = {
    onClick: console.log.bind(console),
  };

  const longAnnotationProps = {
    ...defaultAnnotationProps,
    y: ({ yScale, datum }) => { return yScale(datum.low) - this.calculateTooltipOffset0(isFullChart) },
    fill: "#006517",
    path: buyPath,
    tooltip: (e) => {
      const contents = e.trades.map((trade) => `${trade.longShort === 'LONG' ? 'Buy:' : 'Sell:'} Price: ${trade.price} Date: ${trade.trade_date.replace('T', ' ')}\n`)
      return contents
    },
  };

  const shortAnnotationProps = {
    ...defaultAnnotationProps,
    y: ({ yScale, datum }) => { return yScale(datum.high) - this.calculateTooltipOffset1(isFullChart)},
    fill: "#FF0000",
    path: sellPath,
    tooltip: (e) => {
      const contents = e.trades.map((trade) => `${trade.longShort === 'LONG' ? 'Buy:' : 'Sell:'} Price: ${trade.price} Trade Date: ${trade.trade_date.replace('T', ' ')}\n`)
      return contents
    }
  };

  const xDisplayFormatProps = {
    xDisplayFormat: timeFormat("%Y-%m-%d : %H-%M-%S"),
    ohlcFormat: () => "",
    volumeFormat: () => "",
    percentFormat: () => "",
    displayTexts: {
      d: "Date: ",
    },

  }
  const xDisplayFormatProps1 = {
    xDisplayFormat: timeFormat(""),
    displayTexts: {
      o: " O: ",
      h: " H: ",
      l: " L: ",
      c: " C: ",
      v: " Vol: ",
      na: "n/a"
    },
  }
  const xDisplayFormatProps2 = {
    xDisplayFormat: timeFormat(""),
    ohlcFormat: () => "",
    volumeFormat: () => sym,
    percentFormat: () => "",
    displayTexts: {
      v: " Symbol: ",
    },
  }

  const SMATooltipProps = {
    valueFill: '#ffffff'
  }

  const isIncludeIndicators = (indicator) => {
		if (props.indicators) {
			return props.indicators.filter((e) => e.value === indicator).length;
		}
		return 0;
	}

  return (
    <>
      {
        isLoading || data==null?
          <div className="hunter-loadding-status-text color-white">Loading...</div>
        :
          <>
              <ChartCanvas
                height={calculateHeight()}
                width={width}
                ratio={ratio}
                margin={{left: 50, right: 50, top: 10, bottom: 30}}
                type={'svg'}
                seriesName="MSFT"
                data={data}
                xAccessor={xAccessor}
                displayXAccessor={displayXAccessor}
                xScale={xScale}
                xExtents={xExtents}
              >
                <Chart id={1}

                  yExtents={d => [d.high, d.low]}>
                  <XAxis axisAt="bottom" orient="bottom"  stroke="white" tickStroke="white" />
                  <YAxis axisAt="right" orient="right" ticks={5} stroke="white" tickStroke="white" />

                  <MouseCoordinateX
                    at="bottom"
                    orient="bottom"
                    displayFormat={timeFormat("%Y-%m-%d")} />
                  <MouseCoordinateY
                    at="right"
                    orient="right"
                    displayFormat={format(".2f")} />

                  <CandlestickSeries
                    stroke={d => d.close > d.open ? "#6BA583" : "#DB0000"}
                    wickStroke={d => d.close > d.open ? "#6BA583" : "#DB0000"}
                    fill={d => d.close > d.open ? "#6BA583" : "#DB0000"}
                  />

                  <OHLCTooltip
                    origin={[-50, -5]}
                    {...xDisplayFormatProps}
                  />

                  <OHLCTooltip
                    origin={[-50, 20]}
                    {...xDisplayFormatProps1}
                  />

                  <OHLCTooltip
                    origin={[100, 0]}
                    {...xDisplayFormatProps2}
                  />

                  <Annotate with={SvgPathAnnotation} when={ d =>
                    {
                      return props.selectedInstance !== 'live_trading'
                      && d.trades
                      && d.trades[0].strategy === `${props.strategy.value}-${props.microStrategy}-trades`
                      && d.trades[0].longShort === "LONG"
                    }}
                    usingProps={longAnnotationProps} />
                  <Annotate with={SvgPathAnnotation} when={d =>
                    props.selectedInstance !== 'live_trading'
                    && d.trades
                    && d.trades[0].strategy === `${props.strategy.value}-${props.microStrategy}-trades`
                    && d.trades[0].longShort === "SHORT" }
                    usingProps={shortAnnotationProps} />

                  <HoverTooltip
                    yAccessor={ema50.accessor()}
                    tooltipContent={tooltipContent(sym, [

                    ])}
                    fontSize={12}
                  />
                </Chart>
                <CrossHairCursor />
              </ChartCanvas>
          </>
      }
    </>
  );
};

ChartGraph = fitWidth(ChartGraph);

export default withStyles({
	CandleChart_type_date: {
	  fontSize: "12px",
	  fill: "#AEC6EE"
	},
	CandleChart: {
	  borderRadius: "2px"
	},
	CandleChart_type_value: {
	  fontSize: "16px",
	  fontWeight: 500
	},
	deal_green_shadowed: {
	  textShadow: "0 0 3px yellowgreen"
	},
	deal_red_shadowed: {
	  textShadow: "0 0 3px fuchsia"
	}
})(fitWidth(ChartGraph));
