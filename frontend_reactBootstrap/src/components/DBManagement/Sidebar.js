import { MDBSpinner, MDBCard, MDBCardBody, MDBCardHeader, MDBIcon, MDBNav, MDBNavItem, MDBNavLink } from "mdbreact"
import { useActiveDatabase, useDBDashboard, useDBDashboardLoading } from "contexts/DBDashboardContext"
import Spinner from 'components/Spinner'

const DBSidebar = () => {
  const activeDatabase = useActiveDatabase()
  const databases = useDBDashboard()
  const isLoading = useDBDashboardLoading()

  return (
    <>
      <MDBCard style={{backgroundColor: '#343a40'}}>
        <MDBCardHeader>DATABASES</MDBCardHeader>
        <MDBCardBody style={{ overflowY: 'auto'}}>
          <MDBNav>
            <MDBNavItem>
              {isLoading && <Spinner color="info" />}
              {databases && databases.map(name => {
                return (
                  <MDBNavLink key={name} disabled={name === activeDatabase} to={'#'+name} style={(name===activeDatabase)?{color: 'lightgray'}:{color: 'white'}}>
                    <MDBIcon icon="database" />{" "}{name}
                  </MDBNavLink>
                )
              })}
            </MDBNavItem>
          </MDBNav>
        </MDBCardBody>
      </MDBCard>
    </>
  )
}

export default DBSidebar