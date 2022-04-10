import React, { useState, useEffect } from 'react'
import AdminNavbar from "components/Navbars/AdminNavbar";
import { routes } from "routes.js";
import Sidebar from "components/Sidebar/Sidebar";
import DBDashboard from "components/DBManagement/Dashboard";
import {
  Button
} from "reactstrap";
import { useHistory } from "react-router-dom";
import { DBDashboardProvider } from 'contexts/DBDashboardContext'

const DashboardWrapper = () => {
  const history = useHistory();
  const [isShowSidebar, setShowSidebar] = React.useState(false);
  const [selectedInstance, setSelectedInstance] = React.useState('admin_tab');
  const [user] = useState(JSON.parse(localStorage.getItem('user-info')));


  const handleSidebarChange = () => {
    setShowSidebar(!isShowSidebar);
  };

  const handleInstanceChange = (instance) => {
    setSelectedInstance(instance)
  }

  useEffect (() => {
    console.log('user.is_admin???', user.is_admin)
    if (!user.is_admin) {
      history.pushState('/')
    }
  }, [user, history])

  return (
    <DBDashboardProvider>
      <React.Fragment>
        <AdminNavbar nav="true"/>
        <div className="dashboard-wrapper">
            {!isShowSidebar && (
              <Button
                className ={"show-sidebar-toggle-area show-sidebar-icon"}
                onClick={handleSidebarChange}
              >
                <i className="tim-icons icon-align-left-2"/>
              </Button>
            )}
            {isShowSidebar && (
              <Sidebar
                isAdminPage={false}
                routes={routes}
                subInstance={'systemfilemanager'}
                handleSidebarChange={handleSidebarChange}
                selectedInstance={selectedInstance}
                handleInstanceChange={handleInstanceChange}
              />
            )}
            <div className="col-sm-12 hunter-data-table-container">
              <DBDashboard></DBDashboard>
            </div>
        </div>
      </React.Fragment>
    </DBDashboardProvider>
  )
}

export default DashboardWrapper