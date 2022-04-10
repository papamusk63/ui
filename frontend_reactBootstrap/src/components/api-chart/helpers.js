import { atr, ema, macd, heikinAshi } from "react-stockcharts/lib/indicator";
import { discontinuousTimeScaleProvider } from "react-stockcharts/lib/scale";

export const ema20 = ema()
			.id(0)
			.options({ windowSize: 13 })
			.merge((d, c) => { d.ema20 = c; })
			.accessor(d => d.ema20);

export const ema50 = ema()
  .id(2)
  .options({ windowSize: 50 })
  .merge((d, c) => { d.ema50 = c; })
  .accessor(d => d.ema50);

export const ha = heikinAshi();

export const macdCalculator = macd()
    .options({
      fast: 12,
      slow: 26,
      signal: 9,
    })
    .merge((d, c) => { d.macd = c; })
    .accessor(d => d.macd);

export const atr14 = atr()
  .options({ windowSize: 14 })
  .merge((d, c) => {d.atr14 = c;})
  .accessor(d => d.atr14);

export const xScaleProvider = discontinuousTimeScaleProvider.inputDateAccessor(d => d.date);

// export const {
//   data,
//   xScale,
//   xAccessor,
//   displayXAccessor,
// } = xScaleProvider(calculatedData);