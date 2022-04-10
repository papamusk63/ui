import Axios from 'axios';

const http  = Axios.create({
  baseURL: process.env.REACT_APP_BACKEND_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

const request = async (req) => {
  const config = {
    method: req.method,
    url: req.path,
    params: req.params,
    data: req.body,
    headers: req.headers,
  }
  try {
    const response = await http.request(config);
    return {
      success: true,
      data: response.data,
    }
  } catch (err) {
    console.error(`request ${req.path}:`, err);
    return {
      success: false,
      data: err,
    }
  }
}

export const getStrategyListReq = async () => {
  const req = {
    method: 'GET',
    path: 'api/get_strategy_list'
  }

  return await request(req);
}

export const getTablesReq = async (strategy) => {
  const req = {
    method: 'POST',
    path: 'api/tables',
    body: {
      strategy,
    }
  }

  return await request(req);
}

export const getDataReq = async (body) => {
  const req = {
    method: 'POST',
    path: 'api/get_data',
    body,
  }

  return await request(req);
}

export const getDataSliceReq = async (body) => {
  const req = {
    method: 'POST',
    path: 'api/get_data_slice',
    body,
  }

  return await request(req);
}

export const getDataExtendedSliceReq = async (body) => {
  const req = {
    method: 'POST',
    path: 'api/get_data_extended_slice',
    body,
  }

  return await request(req);
}

export const getDataExtendedReq = async (body) => {
  const req = {
    method: 'POST',
    path: 'api/get_data_extended',
    body,
  }

  return await request(req);
}

export const getBacktestingResultReq = async (body) => {
  const req = {
    method: 'POST',
    path: 'api/get_backtesting_result',
    body,
  }

  return await request(req);
}

export const filterPriceData = async (symbol, timeFrame, tradeStartDate, tradeEndDate, currentPage, pageAmount) => {
  const requestOptions = {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
      'symbol': symbol,
      'time_frame': timeFrame,
      'start': tradeStartDate,
      'end': tradeEndDate,
      'page_num': currentPage,
      'page_mounts': pageAmount,
    })
  };

  return await fetch(process.env.REACT_APP_BACKEND_URL + "/api/get_table_candles", requestOptions)
    .then(response => response.json())
    .then(data => {
      const candles = []
      data.candles.forEach((x) => {
        candles.push({
          'o': x[1],
          'h': x[2],
          'c': x[3],
          'l': x[4],
          'v': x[5],
          'date': x[0].replace('T', ' '),
        })
      })
      return {
        candles,
        page_total: 0
      }
    })
}

export const filterTradesData = async (macroStrategy, microStrategy, tradeStartDate, tradeEndDate, currentPage, pageAmount) => {
  const requestOptions = {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
      'macroStrategy': macroStrategy,
      'microStrategy': microStrategy,
      'tradeStartDate': tradeStartDate,
      'tradeEndDate': tradeEndDate,
      'page_num': currentPage,
      'page_mounts': pageAmount,
    })
  };

  return await fetch(process.env.REACT_APP_BACKEND_URL + "/api/get_data_trades", requestOptions)
    .then(response => response.json())
    .then(data => {
      let trades_data = []
      data.trades_data.forEach((x) => {
        trades_data.push({
          'symbol': x.symbol,
          'strategy': `${x.macro_strategy} - ${x.micro_strategy}`,
          'side': x.side,
          'quantity': x.quantity,
          'date': (x.date.replace('T', ' ')).replace('Z', ''),
          'price': x.price
        })
      })
      return {
        trades_data,
        page_total: data.page_total
      }
    })
}

export const getAllSymbols = async () => {
  const requestOptions = {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
      'strategy': 'no_strategy'
    })
  };

  return await fetch(process.env.REACT_APP_BACKEND_URL + "/api/tables", requestOptions)
    .then(response => response.json())
    .then(data => {
      let temp_data = []
      data.tables.map((x) => {
        temp_data.push({
          value: x,
          label: x
        });
        return null
      })
      return temp_data
    })
}

export const createSignUpLink = async (roles) => {
  const requestOptions = {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
      roles: roles,
      link: process.env.REACT_APP_BACKEND_URL + '/signup/'
    })
  };
  let res = []
  await fetch(process.env.REACT_APP_BACKEND_URL + "/links", requestOptions)
    .then(response => response.json())
    .then(async data => {
      if (data.success === "create link") {
        await fetch(process.env.REACT_APP_BACKEND_URL + "/links")
        .then(response => response.json())
        .then(data => {
          res = data
        })
      }
    })
  return res
}

export const getActiveLinks = async () => {
  return await fetch(process.env.REACT_APP_BACKEND_URL + "/links")
    .then(response => response.json())
    .then(data => {
      return data;
    })
}

export const sendSignUpLink = async (email, link) => {
  const requestOptions = {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
      email,
      link
    })
  };

  return await fetch(process.env.REACT_APP_BACKEND_URL + "/send-signup-link", requestOptions)
    .then(response => response.json())
    .then(data => {
      return true
    })
}

export const forgotPassword = async (email) => {
  const requestOptions = {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
      email,
      url: process.env.REACT_APP_BACKEND_URL
    })
  };

  return await fetch(process.env.REACT_APP_BACKEND_URL + "/password_reset/", requestOptions)
    .then(response => response.json())
    .then(data => {
      return data
    })
}

export const getStrategyOptions = async () => {
  return await fetch(process.env.REACT_APP_BACKEND_URL + "/api/get_strategies")
    .then(response => response.json())
    .then(data => {
      return data
    })
}

export const passwordConfirmReset = async (password1, password2, pathname) => {
  const requestOptions = {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
      password1,
      password2,
      pathname: pathname
    })
  };

  return await fetch(process.env.REACT_APP_BACKEND_URL + "/password_reset_confirm/", requestOptions)
    .then(response => response.json())
    .then(data => {
      return data
    })
}

export const getScriptFileNames = async() => {
  return await fetch(process.env.REACT_APP_BACKEND_URL + "/api/get_script_files")
    .then(response => response.json())
    .then(data => {
      return data
    })
}

export const getModuleTypeNames = async() => {
  return await fetch(process.env.REACT_APP_BACKEND_URL + "/strategy/parameter_list/")
    .then(response => response.json())
    .then(data => {
      return data
    })
}

export const getFileTypeNames = async(moduleType) => {
  const requestOptions = {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
      param_type: moduleType
    })
  };
  return await fetch(process.env.REACT_APP_BACKEND_URL + "/strategy/parameter_detail_list/", requestOptions)
    .then(response => response.json())
    .then(data => {
      return data
    })
}

export const createScriptFile = async(filename, content, isUpdate) => {
  const requestOptions = {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
      filename,
      content,
    })
  };

  const api = isUpdate ? '/api/update_script_file' : '/api/create_script_file';

  return await fetch(process.env.REACT_APP_BACKEND_URL + api, requestOptions)
    .then(response => response.json())
    .then(data => {
      return data
    })
}

const convertArraytoString = (src) => {
  if (!src) {
    return ''
  }

  let dest = ''
  let comma = ''

  src.forEach(o => {
    dest = dest + comma + o.value
    comma = ','
  })
  return dest
}

const convertStringtoArray = (src) => {
  if (!src || !src.length) {
    return null
  }

  const dest = src.split(',')
  return dest.map((o) => ({
    value: o,
    label: o
  }))
}

const convertStringtoHourObject = (src) => {
  return {
    value: src === true || src === 'true' ? true : false,
    label: src === true || src === 'true' ? 'true' : 'false',
  }
}

const transformingProcessConfigToQuery = (settings) => {
  return {
    name: settings.name,
    indicator: convertArraytoString(settings.indicator),
    watchlist: convertArraytoString(settings.watchlist),
    position_sizing: convertArraytoString(settings.position_sizing),
    order_routing: convertArraytoString(settings.order_routing),
    data_source: convertArraytoString(settings.data_source),
    live_trading: convertArraytoString(settings.live_trading),
    starting_cash: settings.starting_cash,
    extended_hours: convertArraytoString(settings.extended_hours),
    macro_strategy: convertArraytoString(settings.macro_strategy),
    indicator_signalling: convertArraytoString(settings.indicator_signalling),
    asset_class: convertArraytoString(settings.asset_class),
  };
}

const transformingProcessConfigFromParam = (settings) => {
  return {
    name: settings.name,
    indicator: convertStringtoArray(settings.indicator),
    watchlist: convertStringtoArray(settings.watchlist),
    position_sizing: convertStringtoArray(settings.position_sizing),
    order_routing: convertStringtoArray(settings.order_routing),
    data_source: convertStringtoArray(settings.data_source),
    live_trading: convertStringtoArray(settings.live_trading),
    starting_cash: settings.starting_cash,
    extended_hours: convertStringtoHourObject(settings.extended_hours),
    macro_strategy: convertStringtoArray(settings.macro_strategy),
    indicator_signalling: convertStringtoArray(settings.indicator_signalling),
    asset_class: convertStringtoArray(settings.asset_class),
  };
}

export const saveConfigFile = async(settings) => {


  const data = transformingProcessConfigToQuery(settings)
  const requestOptions = {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
      config_collection: 'bot_configs',
      config: data
    })
  };

  const api = '/strategy/create_one_config_detail/';

  return await fetch(process.env.REACT_APP_BACKEND_URL + api, requestOptions)
    .then(response => response.json())
    .then(data => {
      return data
    })
}

export const saveScriptFile = async(filename, contents, isUpdate) => {
  const requestOptions = {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
      name: filename,
      contents,
    })
  };

  const api = '/strategy/save_other_parameters/';

  return await fetch(process.env.REACT_APP_BACKEND_URL + api, requestOptions)
    .then(response => response.json())
    .then(data => {
      return data
    })
}

export const getScriptFile = async(filename) => {
  const requestOptions = {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
      filename,
    })
  };
  return await fetch(process.env.REACT_APP_BACKEND_URL + "/api/get_script_file", requestOptions)
    .then(response => response.json())
    .then(data => {
      return data
    })
}

/** User Management Api*/
export const getUserList = async () => {
  return await fetch(process.env.REACT_APP_BACKEND_URL + "/get_user_list")
    .then(response => response.json())
    .then(data => {
      return data
    })
}

export const updateUserRole = async (id, role) => {
  const requestOptions = {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
      id,
      role
    })
  };
  return await fetch(process.env.REACT_APP_BACKEND_URL + "/update_user_role", requestOptions)
    .then(response => response.json())
    .then(data => {
      return data
    })
}

export const deleteUser = async (id) => {
  const requestOptions = {
    method: 'PUT',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
      id,
    })
  };

  return await fetch(process.env.REACT_APP_BACKEND_URL + "/delete_user/", requestOptions)
    .then(response => response.json())
    .then(data => {
      return data
    })
}

export const getConfigFileList = async (collection) => {
  const requestOptions = {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
      config_collection: collection,
    })
  };
  return await fetch(process.env.REACT_APP_BACKEND_URL + "/strategy/config_detail_names/", requestOptions)
    .then(response => response.json())
    .then(data => {
      return data
    })
}

export const getBotConfigFileList = async (collection) => {
  const requestOptions = {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
      config_collection: collection,
    })
  };

  return await fetch(process.env.REACT_APP_BACKEND_URL + "/strategy/config_detail_names/", requestOptions)
    .then(response => response.json())
    .then(data => {
      return data
    })
}

export const getConfigFileDetail = async (collection, name) => {
  const requestOptions = {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
      config_collection: collection,
      name,
    })
  };
  const res = await fetch(process.env.REACT_APP_BACKEND_URL + "/strategy/config_item_detail/", requestOptions)
    .then(response => response.json())
    .then(data => {
      return data
    })

  return transformingProcessConfigFromParam(res.result)
}

export const getBotStatusList = async () => {
  const requestOptions = {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
      "config_collection": "bot_status"
    })
  };

  return await fetch(process.env.REACT_APP_BACKEND_URL + "/strategy/bot_status_list/", requestOptions)
    .then(response => response.json())
    .then(data => {
      return data
    })
}

export const updateBotStatus = async (botName, botAction) => {
  const requestOptions = {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
      "config_collection": "bot_configs",
      "name": botName
    })
  };

  const apiUrl = botAction === 'start'
    ? '/strategy/bot_run/'
    : botAction === 'pause'
    ? '/strategy/bot_pause/'
    : '/strategy/bot_stop/'

  try {
    return await fetch(process.env.REACT_APP_BACKEND_URL + apiUrl, requestOptions)
      .then(response => response.json())
      .then(data => {
        return data
      })
  } catch (e) {
    return {
      success: false,
      message: e
    }
  }
}

export const getBotConfigList = async () => {
  const requestOptions = {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
      "config_collection": "bot_configs",
    })
  };

  const apiUrl = '/strategy/config_details/'

  try {
    return await fetch(process.env.REACT_APP_BACKEND_URL + apiUrl, requestOptions)
      .then(response => response.json())
      .then(data => {
        return data
      })
  } catch (e) {
    return {
      success: false,
      message: e
    }
  }
}

export const getNewsFinancialData = async (symbol) => {
  const requestOptions = {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
      'symbol': symbol,
    })
  };

  const apiUrl = '/news/symbol_news/'

  try {
    return await fetch(process.env.REACT_APP_BACKEND_URL + apiUrl, requestOptions)
      .then(response => response.json())
      .then(data => {
        return data
      })
  } catch (e) {
    return {
      success: false,
      message: e
    }
  }
}

export const getIncomeStatement = async (symbol) => {
  const requestOptions = {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
      'symbol': symbol,
    })
  };

  return await fetch(process.env.REACT_APP_BACKEND_URL + "/financials/income_statement/", requestOptions)
    .then(response => response.json())
    .then(data => {
      return data
    })
}
export const getBalanceSheet = async (symbol) => {
  const requestOptions = {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
      'symbol': symbol,
    })
  };

  return await fetch(process.env.REACT_APP_BACKEND_URL + "/financials/balance_sheet/", requestOptions)
    .then(response => response.json())
    .then(data => {
      return data
    })
}

export const getCashStatement = async (symbol) => {
  const requestOptions = {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
      'symbol': symbol,
    })
  };

  return await fetch(process.env.REACT_APP_BACKEND_URL + "/financials/cash_statement/", requestOptions)
    .then(response => response.json())
    .then(data => {
      return data
    })
}

export const getFinancialTotalData = async (symbol) => {
  const requestOptions = {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
      'symbol': symbol,
    })
  };

  return await fetch(process.env.REACT_APP_BACKEND_URL + "/financials/financial_total_data/", requestOptions)
    .then(response => response.json())
    .then(data => {
      return data
    })
}

export const getStockModalData = async () => {
  const apiUrl = '/scanner/available_items/'

  try {
    return await fetch(process.env.REACT_APP_BACKEND_URL + apiUrl)
      .then(response => response.json())
      .then(data => {
        return data
      })
  } catch (e) {
    return {
      success: false,
      message: e
    }
  }
}

export const getMultiFinancials = async (symbols, statement_type) => {
  const requestOptions = {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
      'symbols': symbols,
      'financial_part': statement_type,
    })
  };

  const apiURL = '/scanner/multi_financials/'
  try {
    return await fetch(process.env.REACT_APP_BACKEND_URL + apiURL, requestOptions)
      .then(response => response.json())
      .then(data => {
        return data.results
      })
  } catch (e) {
    return {
      success: false,
      message: e
    }
  }
}

export const saveScannerView = async (chart_number, symbols, fields) => {
  const requestOptions = {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
      'chart_number': chart_number,
      'symbols': symbols,
      'fields': fields,
    })
  };

  const apiURL = '/scanner/save_scanner_views/'
  try {
    return await fetch(process.env.REACT_APP_BACKEND_URL + apiURL, requestOptions)
      .then(response => response.json())
      .then(data => {
        return data.results
      })
  } catch (e) {
    return {
      success: false,
      message: e
    }
  }
}

export const getScannerViewData = async (chart_number) => {
  const requestOptions = {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
      'chart_number': chart_number,
    })
  };

  const apiURL = '/scanner/scanner_views/'
  try {
    return await fetch(process.env.REACT_APP_BACKEND_URL + apiURL, requestOptions)
    .then(response => response.json())
    .then(data => {
        return data.result
      })
  } catch (e) {
    return {
      success: false,
      message: e
    }
  }
}

export const getScannerDetails = async (exchange='', industry='', sector='', currentPage, pageAmount) => {

  const requestOptions = {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
      'exchange': exchange,
      'industry': industry,
      'sector': sector,
      'page_num': currentPage,
      'page_mounts': pageAmount,
    })
  };

  const apiURL = '/scanner/ticker_details_list/'

  try {
    return await fetch(process.env.REACT_APP_BACKEND_URL + apiURL, requestOptions)
    .then(response => response.json())
    .then(data => {
      return data
    })
  } catch (e) {
    return {
      success: false,
      message: e
    }
  }
}

export const getTickerScannerOptions = async () => {
  const apiUrl = '/scanner/ticker_details_filter_options/'

  try {
    return await fetch(process.env.REACT_APP_BACKEND_URL + apiUrl)
      .then(response => response.json())
      .then(data => {
        return data
      })
  } catch (e) {
    return {
      success: false,
      message: e
    }
  }
}

export const getFloatsFilterOptions = async () => {
  const apiUrl = '/floats/float_details_filter_options/'

  try {
    return await fetch(process.env.REACT_APP_BACKEND_URL + apiUrl)
      .then(response => response.json())
      .then(data => {
        return data
      })
  } catch (e) {
    return {
      success: false,
      message: e
    }
  }
}

export const getFloatsDetails = async (pageNumber, pageAmount, exchange='', industry='', sector='') => {

  const requestOptions = {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
      'page_num': pageNumber,
      'page_mounts': pageAmount,
      'exchange': exchange,
      'industry': industry,
      'sector': sector,
    })
  };

  const apiURL = '/floats/float_details_list/'

  try {
    return await fetch(process.env.REACT_APP_BACKEND_URL + apiURL, requestOptions)
    .then(response => response.json())
    .then(data => {
      return data.results
    })
  } catch (e) {
    return {
      success: false,
      message: e
    }
  }
}

export const saveScannerAllViewData = async (allViewData) => {
  const requestOptions = {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify(allViewData)
  };

  const apiURL = '/scanner/save_all_views/'
  try {
    return await fetch(process.env.REACT_APP_BACKEND_URL + apiURL, requestOptions)
      .then(response => response.json())
      .then(data => {
        return {
          success: true,
          data: data.results
        }
      })
  } catch (e) {
    return {
      success: false,
      message: e
    }
  }
}

export const getScannerAllViewData = async (chart_number) => {
  const requestOptions = {
    method: 'GET',
    headers: {'Content-Type': 'application/json'},
  };

  const apiURL = '/scanner/load_all_views/'
  try {
    return await fetch(process.env.REACT_APP_BACKEND_URL + apiURL, requestOptions)
    .then(response => response.json())
    .then(data => {
        return {
          success: true,
          data: data.result,
        }
      })
  } catch (e) {
    return {
      success: false,
      message: e
    }
  }
}

export const getSearchingData = async () => {
  const requestOptions = {
    method: 'GET',
    headers: {'Content-Type': 'application/json'},
  };

  const apiURL = '/scanner/get_searching_data/'
  try {
    return await fetch(process.env.REACT_APP_BACKEND_URL + apiURL, requestOptions)
    .then(response => response.json())
    .then(data => {
        return {
          success: true,
          data: data.result,
        }
      })
  } catch (e) {
    return {
      success: false,
      message: e
    }
  }
}

export const getSymbolsByMicroStrategy = async (macroStrat, microStrat) => {
  const requestOptions = {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
      'macro': macroStrat,
      'micro': microStrat
    })
  };

  const apiURL = '/api/micro_strategy_symbols'

  try {
    return await fetch(process.env.REACT_APP_BACKEND_URL + apiURL, requestOptions)
      .then(response => response.json())
      .then(data => {
        return {
          success: true,
          data: data.result
        }
      })
  } catch (e) {
    return {
      success: false,
      message: e
    }
  }
}

export const getIndicators = async () => {
  const requestOptions = {
    method: 'GET',
    headers: {'Content-Type': 'application/json'},
  };

  const apiURL = '/api/indicator_list'
  try {
    return await fetch(process.env.REACT_APP_BACKEND_URL + apiURL, requestOptions)
    .then(response => response.json())
    .then(data => {
        return {
          success: true,
          data: data.result,
        }
      })
  } catch (e) {
    return {
      success: false,
      message: e
    }
  }
}

export const getIndicatorSignallingList = async () => {
  const requestOptions = {
    method: 'GET',
    headers: {'Content-Type': 'application/json'},
  };

  const apiURL = '/api/get_indicator_signalling_list'
  try {
    return await fetch(process.env.REACT_APP_BACKEND_URL + apiURL, requestOptions)
    .then(response => response.json())
    .then(data => {
        return {
          success: true,
          data: data.result,
        }
      })
  } catch (e) {
    return {
      success: false,
      message: e
    }
  }
}

export const apiGetDatabases = async() => {
  const requestOptions = {
    method: 'GET',
    header: {'Content-Type': 'application/json'},
  }

  const apiURL = '/api/get_databases'
  try {
    return await fetch(process.env.REACT_APP_BACKEND_URL + apiURL, requestOptions)
    .then(response => response.json())
    .then(data => {
      return data
    })
  } catch (e) {
    return {
      success: false,
      message: e
    }
  }
}

export const apiGetCollections = async(dbName) => {
  const requestOptions = {
    method: 'GET',
    header: {'Content-Type': 'application/json'},
  }

  let apiURL = new URL(process.env.REACT_APP_BACKEND_URL + '/api/get_collections')
  apiURL.search = new URLSearchParams({db_name: dbName}).toString()

  try {
    return await fetch(apiURL, requestOptions)
      .then(response => response.json())
      .then(data => {
        return data
      })
  } catch (e) {
    return {
      success: false,
      message: e
    }
  }
}

export const apiDeleteCollection = async(dbName, collectionName) => {
  const requestOptions = {
    method: 'GET',
    header: {'Content-Type': 'application/json'},
  }

  let apiURL = new URL(process.env.REACT_APP_BACKEND_URL + '/api/delete_collection')
  apiURL.search = new URLSearchParams({db_name: dbName, collection_name: collectionName}).toString()

  try {
    return await fetch(apiURL, requestOptions)
      .then(response => response.json())
      .then(data => {
        return data
      })
  } catch (e) {
    return {
      success: false,
      message: e
    }
  }
}


export const apiDeleteDatabase = async(dbName) => {
  const requestOptions = {
    method: 'GET',
    header: {'Content-Type': 'application/json'},
  }

  let apiURL = new URL(process.env.REACT_APP_BACKEND_URL + '/api/delete_database')
  apiURL.search = new URLSearchParams({db_name: dbName}).toString()

  try {
    return await fetch(apiURL, requestOptions)
      .then(response => response.json())
      .then(data => {
        return data
      })
  } catch (e) {
    return {
      success: false,
      message: e
    }
  }
}


export const apiExportDatabase = async(dbName) => {
  const requestOptions = {
    method: 'GET',
    header: {'Content-Type': 'application/json'},
  }

  let apiURL = new URL(process.env.REACT_APP_BACKEND_URL + '/api/export_database')
  apiURL.search = new URLSearchParams({db_name: dbName}).toString()

  try {
    return await fetch(apiURL, requestOptions)
      .then(response => {
        response.blob().then(blob => {
          let url = window.URL.createObjectURL(blob);
          let a = document.createElement("a");
          a.href = url;
          a.download = `${dbName}.zip`;
          a.click();
        })
      })
  } catch (e) {
    return {
      success: false,
      message: e
    }
  }
}


export const apiExportCollection = async(dbName, collectionName) => {
  const requestOptions = {
    method: 'GET',
    header: {'Content-Type': 'application/json'},
  }

  let apiURL = new URL(process.env.REACT_APP_BACKEND_URL + '/api/export_collection')
  apiURL.search = new URLSearchParams({db_name: dbName, collection_name: collectionName}).toString()

  try {
    return await fetch(apiURL, requestOptions)
      .then(response => {
        response.blob().then(blob => {
          let url = window.URL.createObjectURL(blob);
          let a = document.createElement("a");
          a.href = url;
          a.download = `${dbName}_${collectionName}.csv`;
          a.click();
        })
      })
  } catch (e) {
    return {
      success: false,
      message: e
    }
  }
}

export const getWatchListAll = async () => {
  const requestOptions = {
    method: 'GET',
    headers: {'Content-Type': 'application/json'},
  };

  const apiURL = '/scanner/watchlists_all/'
  try {
    return await fetch(process.env.REACT_APP_BACKEND_URL + apiURL, requestOptions)
    .then(response => response.json())
    .then(data => {
        return {
          success: true,
          result: data.result,
        }
      })
  } catch (e) {
    return {
      success: false,
      message: e
    }
  }
}



export const apiCreateBackup = async(dbName, collectionName = '') => {
  const requestOptions = {
    method: 'GET',
    header: {'Content-Type': 'application/json'},
  }

  let apiURL = new URL(process.env.REACT_APP_BACKEND_URL + '/api/create_backup')
  apiURL.search = new URLSearchParams({db_name: dbName, collection_name: collectionName}).toString()

  try {
    return await fetch(apiURL, requestOptions)
      .then(response => response.json())
      .then(result => result['data'])
  } catch (e) {
    return {
      success: false,
      message: e
    }
  }
}


export const apiExecuteBackup = async(data) => {
  const requestOptions = {
    method: 'GET',
    header: {'Content-Type': 'application/json'},
  }

  let apiURL = new URL(process.env.REACT_APP_BACKEND_URL + '/api/execute_backup')
  apiURL.search = new URLSearchParams({backup_id: data['id']}).toString()

  try {
    let filename = `${data['database']}.zip`
    if (data['collection']) {
      filename = `${data['database']}_${data['collection']}.csv`
    }
    return await fetch(apiURL, requestOptions)
      .then(response => {
        const contentType = response.headers.get("content-type");
        if (contentType && contentType.indexOf("application/json") !== -1) {
          console.log('Json object response')
        } else {
          response.blob().then(blob => {
            let url = window.URL.createObjectURL(blob);
            let a = document.createElement("a");
            a.href = url;
            a.download = filename;
            a.click();
          })
        }

        // console.log('response')
        // console.log(response)


      })
  } catch (e) {
    return {
      success: false,
      message: e
    }
  }
}


export const apiStopBackup = async(data) => {
  const requestOptions = {
    method: 'GET',
    header: {'Content-Type': 'application/json'},
  }

  let apiURL = new URL(process.env.REACT_APP_BACKEND_URL + '/api/stop_backup')
  apiURL.search = new URLSearchParams({backup_id: data['id']}).toString()

  try {
    return await fetch(apiURL, requestOptions)
      .then(response => response.json())
      .then(result => result['data'])
  } catch (e) {
    return {
      success: false,
      message: e
    }
  }
}


export const apiGetGoogleNews = async (params) => {
  // const req = {
  //   method: 'GET',
  //   path: 'api/get_google_news'
  // }

  // return await request(req);


  const requestOptions = {
    method: 'GET',
    header: {'Content-Type': 'application/json'},
  }

  let apiURL = new URL(process.env.REACT_APP_BACKEND_URL + '/api/get_google_news')
  apiURL.search = new URLSearchParams(params).toString()

  try {
    return await fetch(apiURL, requestOptions)
      .then(response => response.json())
      .then(result => result['data'])
  } catch (e) {
    return {
      success: false,
      message: e
    }
  }
}
export const apiGetTradeHistories = async (params) => {
  const requestOptions = {
    method: 'GET',
    header: {'Content-Type': 'application/json'},
  }

  let apiURL = new URL(process.env.REACT_APP_BACKEND_URL + '/api/get_trade_histories')
  apiURL.search = new URLSearchParams(params).toString()

  try {
    return await fetch(apiURL, requestOptions)
      .then(response => response.json())
      .then(result => result['data'])
  } catch (e) {
    return {
      success: false,
      message: e
    }
  }
}