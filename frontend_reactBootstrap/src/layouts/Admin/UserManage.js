import React, { useEffect, useState } from "react";
import { useLocation } from "react-router-dom";
import Select from 'react-select'
import { useHistory } from "react-router-dom";
import {
  Button
} from "reactstrap";
// javascript plugin used to create scrollbars on windows
import PerfectScrollbar from "perfect-scrollbar";

// core components
import AdminNavbar from "components/Navbars/AdminNavbar.js";
import Sidebar from "components/Sidebar/Sidebar.js";

import { adminRoutes } from "routes.js";

import { BackgroundColorContext } from "contexts/BackgroundColorContext";
import Modal from 'react-bootstrap/Modal';
import { MDBBtn, MDBTable, MDBTableBody, MDBTableHead  } from 'mdbreact';
import { getUserList, updateUserRole, deleteUser } from 'api/Api';

var ps;

function UserManage() {
  const history = useHistory();
  const [isRequest, setIsRequest] = useState(true)
  const [error, setError] = useState(-1)
  const [isLoading, setIsLoading] = useState(false)
  const [message, setMessage] = useState('')
  const [isShowSidebar, setShowSidebar] = React.useState(true);
  const location = useLocation();
  const mainPanelRef = React.useRef(null);
  const [isShowUpdateRoleModal, setIsShowUpdateRoleModal] = useState(false);
  const [roles, setRoles] = useState([]);
  const [userlist, setUserList] = useState([])
  const [selectedUserId, setSelectedUserId] = useState(null);
  const [sidebarOpened, setsidebarOpened] = React.useState(
    document.documentElement.className.indexOf("nav-open") !== -1
  );
  const [selectedInstance, setSelectedInstance] = React.useState('usermanage');
  const optionsRole = [
    { value: 'forward_test', label: 'Forward Test' },
    // { value: 'stress_test', label: 'Stress Test' },
    // { value: 'optimization', label: 'Optimization' },
    { value: 'live_trading', label: 'Live Trade' },
    { value: 'search_engine', label: 'Market' },
    { value: 'scanner', label: 'Scanner' },
    { value: 'trade_data', label: 'Trade Data' },
    { value: 'hybrid_view', label: 'Hybrid View' },
    { value: 'financial_data', label: 'Financial Data' },
    { value: 'floats', label: 'Floats' },
  ]
  const [user] = useState(JSON.parse(localStorage.getItem('user-info')));

  useEffect(() => {
    if (!user.is_admin) {
      history.push('/')
    }
  }, [user, history])

  React.useEffect(() => {
    if (navigator.platform.indexOf("Win") > -1) {
      document.documentElement.className += " perfect-scrollbar-on";
      document.documentElement.classList.remove("perfect-scrollbar-off");
      ps = new PerfectScrollbar(mainPanelRef.current, {
        suppressScrollX: true,
      });
      let tables = document.querySelectorAll(".table-responsive");
      for (let i = 0; i < tables.length; i++) {
        ps = new PerfectScrollbar(tables[i]);
      }
    }
    // Specify how to clean up after this effect:
    return function cleanup() {
      if (navigator.platform.indexOf("Win") > -1) {
        ps.destroy();
        document.documentElement.classList.add("perfect-scrollbar-off");
        document.documentElement.classList.remove("perfect-scrollbar-on");
      }
    };
  });
  React.useEffect(() => {
    if (navigator.platform.indexOf("Win") > -1) {
      let tables = document.querySelectorAll(".table-responsive");
      for (let i = 0; i < tables.length; i++) {
        ps = new PerfectScrollbar(tables[i]);
      }
    }
    document.documentElement.scrollTop = 0;
    document.scrollingElement.scrollTop = 0;
    if (mainPanelRef.current) {
      mainPanelRef.current.scrollTop = 0;
    }
  }, [location]);

  useEffect(() => {
    const fetchUserList = async () => {
      const list = await getUserList();
      const users = list.map((user, index) => {
        return {
          id: index,
          username: user.username,
          email: user.email,
          role: user.is_superuser ? 'Super User' : user.role,
          active: 'active',
          action: <div className="hunter-user-manage-button-area">
            {/* <MDBBtn color="blue" size="sm" onClick={
            () => {
              setRoles([]);
              setSelectedUserId(user.id);
              showUpdateUserRoleModal();
            }}
            >Update Role</MDBBtn> */}
            <MDBBtn color="blue" size="sm" onClick={
            async () => {
              if (window.confirm("Do you really want to delete this user?")) {
                const res = await deleteUser(user.id)
                setIsRequest(true);
                alert(res.message)
              }
            }}
          >Delete User</MDBBtn>
          </div>
        }
      })
       setUserList(users)
    };
    if (isRequest) {
      fetchUserList();
      setIsRequest(false);
    }
  }, [isRequest])

  const showUpdateUserRoleModal = () => {
    setIsShowUpdateRoleModal(true);
  }

  // this function opens and closes the sidebar on small devices
  const toggleSidebar = () => {
    document.documentElement.classList.toggle("nav-open");
    setsidebarOpened(!sidebarOpened);
  };

  const handleSidebarChange = () => {
    setShowSidebar(!isShowSidebar);
  };

  const getBrandText = (path) => {
    for (let i = 0; i < adminRoutes.length; i++) {
      if (location.pathname.indexOf(adminRoutes[i].layout + adminRoutes[i].path) !== -1) {
        return adminRoutes[i].name;
      }
    }
    return "Brand";
  };
  const handleInstanceChange = (instance) => {
    setSelectedInstance(instance)
  }

  const columns= [
    {
      label: '#',
      field: 'id',
    },
    {
      label: 'name',
      field: 'username',
    },
    {
      label: 'email',
      field: 'email',
    },
    {
      label: 'Role',
      field: 'role',
    },
    {
      label: 'Active',
      field: 'active',
    },
    {
      action: 'Action',
      field: 'action',
    }
  ];

  const handleRolesChange = (options) => {
    setRoles(options);
  }

  const handleUpdateRoleModalClose = () => {
    setIsShowUpdateRoleModal(false)
  }

  const transformUserRole = (roles) => {
    let roleValues = ''
    let coma = ''
    roles.forEach(role => {
      roleValues = roleValues + coma + role.value
      coma = ','
    })
    return roleValues;
  }

  const handleUserRoleUpdate = async () => {
    setIsLoading(true)
    const res = await updateUserRole(selectedUserId, transformUserRole(roles));
    setIsLoading(false)
    if ( res.success ) {
      setIsRequest(true);
      setError(0)
      setMessage(res.message)
      return;
    }
    setError(1)
    setMessage(res.message)
    return
  }

  const handleModalClose = () => {
    setError(-1);
    setMessage('');
    setIsShowUpdateRoleModal(false)
  }

  return (
    <BackgroundColorContext.Consumer>
      {({ color, changeColor }) => (
        <React.Fragment>
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
              isAdminPage={true}
              routes={adminRoutes}
              handleSidebarChange={handleSidebarChange}
              selectedInstance={selectedInstance}
              handleInstanceChange={handleInstanceChange}
            />
          )}
          <Modal show={isShowUpdateRoleModal} className="hunter-modal" onHide={handleUpdateRoleModalClose}>
            <Modal.Header closeButton>
              <Modal.Title>Update User Role</Modal.Title>
            </Modal.Header>
            <Modal.Body>
              <div className="select-multi-option">
                <Select
                  name="filters"
                  placeholder="Roles"
                  value={roles}
                  onChange={handleRolesChange}
                  options={optionsRole}
                  isMulti={true}
                />
              </div>
            </Modal.Body>
            <Modal.Footer className="hunter-modal-footer">
              <Button variant="primary" onClick={handleUserRoleUpdate}>
                {isLoading && (
                  <span className="spinner-border spinner-border-sm hunter-spinner-button" role="status" aria-hidden="true"></span>
                )}
                Update Role
              </Button>
            </Modal.Footer>
            {error !== -1 &&
              <div className="alert alert-primary" role="alert">
                <div className="alert-container">
                  <div className="alert-content">
                    {message}
                  </div>
                  <button type="button" className="btn btn-primary modal-close-button hunter-modal-small-button" onClick={() => { handleModalClose() }}>Close</button>
                </div>
              </div>
            }
          </Modal>
            <div className={`main-panel ${!isShowSidebar ? 'full-width' : ''}`} ref={mainPanelRef} data={color}>
              <AdminNavbar
                brandText={getBrandText(location.pathname)}
                toggleSidebar={toggleSidebar}
                sidebarOpened={sidebarOpened}
              />
              <div className="hunter-page-container">
                <div className="hunter-page-title">
                  <h3>User Manage</h3>
                </div>
                <div className="col-sm-8 hunter-mdb-table-container">
                  <MDBTable btn>
                    <MDBTableHead columns={columns} color="dark"/>
                    <MDBTableBody rows={userlist} className="hunter-mdb-table-body"/>
                  </MDBTable>
                </div>
              </div>
            </div>
          </div>
        </React.Fragment>
      )}
    </BackgroundColorContext.Consumer>
  );
}

export default UserManage;
