export const getStockFinancialFields = async () => {
  const apiUrl = '/scanner/ticker_details_fields/'

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

export const getIndicatorFields = async () => {
  const apiUrl = '/scanner/indicators_fields/'

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

export const getTickerNewsFields = async () => {
  const apiUrl = '/scanner/ticker_news_fields/'

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

export const getTickerDetailFields = async () => {
  const apiUrl = '/scanner/ticker_details_fields/'

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