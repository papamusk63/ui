/*eslint-disable*/
import React, { useEffect, useState } from "react";
import { useHistory } from "react-router-dom";
// nodejs library to set properties for components
import { PropTypes } from "prop-types";

// javascript plugin used to create scrollbars on windows
import PerfectScrollbar from "perfect-scrollbar";

// reactstrap components
import { Nav, NavLink as ReactstrapNavLink } from "reactstrap";
import {
  BackgroundColorContext,
} from "contexts/BackgroundColorContext";

import { Dropdown } from 'components/Dropdown/Dropdown'

var ps;

function Sidebar(props) {
  const history = useHistory();
  const sidebarRef = React.useRef(null);
  const [user] = useState(JSON.parse(localStorage.getItem('user-info')))
  const [userRole, setUserRole] = useState('');
  // verifies if routeName is the one active (in browser input)
  useEffect(() => {
    setUserRole(user?.role)
  }, [])
  React.useEffect(() => {
    if (navigator.platform.indexOf("Win") > -1) {
      ps = new PerfectScrollbar(sidebarRef.current, {
        suppressScrollX: true,
        suppressScrollY: false,
      });
    }
    // Specify how to clean up after this effect:
    return function cleanup() {
      if (navigator.platform.indexOf("Win") > -1) {
        ps.destroy();
      }
    };
  });
  
  const handleClick = (instance, pathname) => {
    handleInstanceChange(instance)
    const locationState = {
      initInstance: instance
    }
    if (pathname) {
      history.push({
        pathname: pathname,
        state: instance === 'stress_test'
        || instance === 'optimization'
        || instance === 'live_trading'
        ?  locationState: null
      })
    }
  }

  const { isAdminPage, routes, selectedInstance, handleSidebarChange, handleInstanceChange, subInstance } = props;
  
  return (
    <BackgroundColorContext.Consumer>
      {({ color }) => (
        <div className="sidebar hunter-sidebar" data={color}>
          <div className="sidebar-wrapper" ref={sidebarRef}>
            <div className="show-sidebar-button-area">
              <div className="show-sidebar-icon">
                <i className="tim-icons icon-align-left-2" onClick={handleSidebarChange}/>
              </div>
            </div>
            {isAdminPage ? (
              <Nav>
                {routes.map((prop, key) => {
                  return (
                    <li
                      className={
                        prop.instance === selectedInstance ? "active-instance hunter-select-instance" : "hunter-select-instance"
                      }
                      key={key}
                      onClick={() => {
                        handleInstanceChange(prop.instance)
                        if (prop.pathname) {
                          history.push({
                            pathname: prop.pathname
                          })
                        }
                      }}
                    >
                      <div
                        className="nav-link"
                      >
                        <i className={prop.icon} />
                        <p>{prop.name}</p>
                      </div>
                    </li>
                  );
                })}
              </Nav>  
            ) : (
              <Nav>
                {routes.map((prop, key) => {
                  if (!user.is_admin && !userRole.includes(prop.instance)) {
                    return (<></>)
                  }
                  return (
                    <li
                      className={
                        prop.instance === selectedInstance ? "active-instance hunter-select-instance" : "hunter-select-instance"
                      }
                      key={key}
                    >
                      {prop.items ? (
                        <div
                          className="nav-link"
                        >
                          <Dropdown 
                            title={prop.name}
                            icon={prop.icon}
                            items={prop.items}
                            instance={prop.instance}
                            subInstance={subInstance}
                            handleClick={handleClick}
                            isActive={prop.instance === selectedInstance}
                            key={`${prop.instance}`}
                          />
                        </div>
                      ) : (
                        <div
                          className="nav-link"
                          onClick={() => {
                            handleInstanceChange(prop.instance)
                            const locationState = {
                              initInstance: prop.instance
                            }
                            if (prop.pathname) {
                              history.push({
                                pathname: prop.pathname,
                                state: prop.instance === 'stress_test'
                                || prop.instance === 'optimization'
                                || prop.instance === 'live_trading'
                                ?  locationState: null
                              })
                            }
                          }}
                        >
                          <i className={prop.icon} />
                          <p className="hunter-ml-6" >{prop.name}</p>
                        </div>
                      )
                    }
                    </li>
                  );
                })}
              </Nav>
            )}
          </div>
        </div>
      )}
    </BackgroundColorContext.Consumer>
  );
}

Sidebar.defaultProps = {
  rtlActive: false,
  routes: [{}],
};

Sidebar.propTypes = {
  // if true, then instead of the routes[i].name, routes[i].rtlName will be rendered
  // insde the links of this component
  rtlActive: PropTypes.bool,
  routes: PropTypes.arrayOf(PropTypes.object),
  logo: PropTypes.shape({
    // innerLink is for links that will direct the user within the app
    // it will be rendered as <Link to="...">...</Link> tag
    innerLink: PropTypes.string,
    // outterLink is for links that will direct the user outside the app
    // it will be rendered as simple <a href="...">...</a> tag
    outterLink: PropTypes.string,
    // the text of the logo
    text: PropTypes.node,
    // the image src of the logo
    imgSrc: PropTypes.string,
  }),
};

export default Sidebar;
