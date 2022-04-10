import React, {useState, useContext} from 'react'

const DatatableContext = React.createContext()
const DatatableLoadingContext = React.createContext()
const PaginationContext = React.createContext()
const PaginationUpdatingContext = React.createContext()

export const useDatatableLoading = () => {
  return useContext(DatatableLoadingContext)
}

export const useDatatable = (initialData) => {
  return useContext(DatatableContext)
}


export const useDatatableValue = (initialData) => {
  const context = useContext(DatatableContext)
  const [, setDatatable] = context

  setDatatable(initialData)
  return context
}


export const useDatatableUpdate = () => {
  const [, setDatatable] = useContext(DatatableContext)

  return setDatatable
}

export const usePagination = () => {
  return useContext(PaginationContext)
}

export const usePaginationUpdate = () => {
  return useContext(PaginationUpdatingContext)
}

export const DatatableProvider = ({children}) => {
  const [isLoading, setLoading] = useState(false)

  const [itemsPerPage, setItemsPerPage] = useState(10)
  const [currentPage, setCurrentPage] = useState(1)
  const [totalItems, setTotalItems] = useState(0)

  const [datatable, setDatatable] = useState({
    columns: [],
    rows: [],
  })

  return (
    <PaginationContext.Provider value={[parseInt(currentPage), parseInt(itemsPerPage), parseInt(totalItems)]}>
      <PaginationUpdatingContext.Provider value={[setCurrentPage, setItemsPerPage, setTotalItems]}>
        <DatatableContext.Provider value={[datatable, setDatatable]}>
          <DatatableLoadingContext.Provider value={[isLoading, setLoading]}>
              {children}
          </DatatableLoadingContext.Provider>
        </DatatableContext.Provider>
      </PaginationUpdatingContext.Provider>
    </PaginationContext.Provider>
  );
}
