import { MDBBox, MDBBreadcrumb, MDBBreadcrumbItem, MDBLink } from 'mdbreact';
import React from 'react';
import { useActiveDatabase } from 'contexts/DBDashboardContext'

function DBPathway(props) {
  const dbName = useActiveDatabase()
  return (
    <>
      <MDBBreadcrumb style={{backgroundColor: 'transparent'}} className="mb-0">
        <MDBBreadcrumbItem>
            Databases
        </MDBBreadcrumbItem>
        <MDBBreadcrumbItem active>
            {dbName}
        </MDBBreadcrumbItem>
      </MDBBreadcrumb>
    </>
  );
}

export default DBPathway;