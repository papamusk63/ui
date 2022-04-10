import React, { useEffect, useState } from 'react';
import { apiGetCollections, apiDeleteCollection } from "api/Api"
import { useActiveDatabase } from 'contexts/DBDashboardContext'
import DBCollection from './Collection';
import { MDBTable, MDBTableBody, MDBTableHead } from 'mdbreact';
import Spinner from 'components/Spinner'

function DBCollectionList() {
  const [collections, setCollections] = useState([])
  const dbName = useActiveDatabase()

  const [isLoading, setLoading] = useState(true)


  useEffect(() => {
    setLoading(true)
    setCollections([])
    apiGetCollections(dbName).then((response) => {
      setCollections(response.data)
      setLoading(false)
    })
  }, [useActiveDatabase()])

  const deleteCollection = (collectionName) => {
    const confirmed = window.confirm(`Are you sure to delete the collection "${collectionName}"?`);

    if (confirmed) {
      apiDeleteCollection(dbName, collectionName).then((response) => {
        const updatedCollections = collections.filter((filteredCollection) => {
          return filteredCollection != collectionName
        });
        setCollections(updatedCollections)
      })
    }
  }


  let index = 1


  return (
    <>
      <MDBTable className="table table-hover">
        <MDBTableHead>
          <tr>
            <th width="2%">#</th>
            <th>Collection Name</th>
            <td width="5%"></td>
          </tr>
        </MDBTableHead>
        <MDBTableBody>
          {isLoading && <Spinner color="info" />}
          {collections && collections.map((collectionName) => {
            return (
              <DBCollection index={index++} key={collectionName} dbname={dbName} name={collectionName}
                onDeleteClick={() => deleteCollection(collectionName)}
              />
            )
          })}
        </MDBTableBody>
      </MDBTable>
    </>
  );
}

export default DBCollectionList