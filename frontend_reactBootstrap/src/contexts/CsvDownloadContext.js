import React, {useState, useContext} from 'react'

export const CsvDownloadContext = React.createContext()
export const CsvDownloadUpdateContext = React.createContext()

export function useCsvDownload() {
  return useContext(CsvDownloadContext)
}

export function useCsvDownloadUpdate() {
  return useContext(CsvDownloadUpdateContext)
}

export function CsvDownloadProvider({children}) {
  const [dataset, setDataset] = useState([{}])

  const updateCsvDownload = function(data) {
    setDataset(data)
  }

  return (
    <CsvDownloadContext.Provider value={dataset}>
      <CsvDownloadUpdateContext.Provider value={updateCsvDownload}>
        {children}
      </CsvDownloadUpdateContext.Provider>
    </CsvDownloadContext.Provider>
  )
}