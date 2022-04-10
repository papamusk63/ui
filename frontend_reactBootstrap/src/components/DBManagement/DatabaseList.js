import React, { useEffect, useState } from 'react';
import { useDBDashboardLoading, useDBDashboard, useDeleteDatabase, useExportDatabase } from 'contexts/DBDashboardContext'
import DBDatabase from './Database';
import { MDBTable, MDBTableBody, MDBTableHead } from 'mdbreact';
import Spinner from 'components/Spinner'

function DBDatabaseList() {
  const databases = useDBDashboard()

  const handleDelete = useDeleteDatabase()
  const handleBackup = useExportDatabase()
  const isLoading = useDBDashboardLoading()

  let index = 1

  return (
    <>
      <MDBTable className="table table-hover">
        <MDBTableHead>
          <tr>
            <th width="2%">#</th>
            <th>Database Name</th>
            <td width="5%"></td>
          </tr>
        </MDBTableHead>
        <MDBTableBody>
          {isLoading && <Spinner color="info" />}
          {databases && databases.map((databaseName) => {
            return (
              <DBDatabase index={index++} key={databaseName} name={databaseName}
                onDeleteClick={() => handleDelete(databaseName)}
                onSaveClick={() => handleBackup(databaseName)}
              />
            )
          })}
        </MDBTableBody>
      </MDBTable>
    </>
  );
}

export default DBDatabaseList