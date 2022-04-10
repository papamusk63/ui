import { MDBBtn, MDBIcon } from 'mdbreact'
import React from 'react'
import {useThemeColors} from 'contexts/ThemeContext'
import { useActiveDatabase, useBackupStatus, useDeleteDatabase, useExportDatabase } from 'contexts/DBDashboardContext'

export default function DBDatabaseActions() {
  const dbName = useActiveDatabase()
  const colors = useThemeColors()

  const handleDelete = useDeleteDatabase()
  const [handleBackup, ] = useExportDatabase()
  const isBackupRunning = useBackupStatus()

  return (
    <>
      {dbName &&
      <div class="d-flex">
        <MDBBtn color="white" onClick={(e) => {e.preventDefault(); handleDelete(dbName); }}><MDBIcon icon="trash" style={{color: colors.white}} /></MDBBtn>
        <MDBBtn disabled={isBackupRunning} className="d-flex flex-nowrap align-items-center" color="primary" onClick={(e) => {e.preventDefault(); handleBackup(dbName); }}>
          <MDBIcon icon="file-export" style={{color: colors.white}} /> <span class="ml-1">Backup</span>
          {isBackupRunning && <span class="ml-1 spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>}
        </MDBBtn>
      </div>}
    </>
  )
}
