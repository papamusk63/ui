import React, { useState, useEffect } from 'react'
import AdminNavbar from "components/Navbars/AdminNavbar";
import { routes } from "routes.js";
import Sidebar from "components/Sidebar/Sidebar";
import TextEditor from 'components/TextEditor/Editor';
import {
  Button
} from "reactstrap";
import { useHistory } from "react-router-dom";

export default function FileManager(){
  const history = useHistory();
  const [isShowSidebar, setShowSidebar] = React.useState(true);
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

  return(
    <React.Fragment>        
      <AdminNavbar/>
      <div className="wrapper hunter-wrapper">
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
          <TextEditor/>
        </div>
    </React.Fragment>
  );  
}