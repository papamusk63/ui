import DBContent from "./Content"
import DBSidebar from "./Sidebar"
import { useBackupStatus, useExportDatabase } from 'contexts/DBDashboardContext'
import { useThemeColors } from 'contexts/ThemeContext'
import Spinner from 'components/Spinner'
import { MDBBtn } from 'mdbreact'

const { MDBContainer, MDBRow, MDBCol } = require("mdbreact")


const DBDashboard = () => {
  const isBackupRunning = useBackupStatus()
  const [, stopBackup] = useExportDatabase()
  console.log('isBackupRunning')
  console.log(isBackupRunning)

  const colors = useThemeColors()

  return (
    <>
      <MDBContainer fluid={true}>
        <MDBRow>
          <MDBCol><div className="hunter-data-table-title">DB Management</div></MDBCol>
        </MDBRow>
        <MDBRow>
          <MDBCol size="3"><DBSidebar /></MDBCol>
          <MDBCol><DBContent /></MDBCol>
        </MDBRow>
      </MDBContainer>

      {isBackupRunning &&
        (<div className="d-flex position-fixed align-items-center justify-content-center" style={{
            left: 0,
            right: 0,
            top: 0,
            bottom: 0,
            background: 'rgba(0,0,0,0.9)',
            zIndex: 9999,
          }}>
            <div class="d-flex flex-column align-items-center justify-content-center px-5 py-3 pt-5 rounded rounded-5" style={{background: colors.white}}>
              <div className="mb-5"><Spinner>Loading</Spinner><span class="ml-2" style={{color: colors.darkBlue}}>Processing...</span></div>
              <MDBBtn color="red" onClick={(e) => {e.preventDefault(); stopBackup(); }}>Stop</MDBBtn>
            </div>
        </div>)
      }
    </>
  )
}

export default DBDashboard