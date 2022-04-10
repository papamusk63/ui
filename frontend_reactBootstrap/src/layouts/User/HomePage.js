import React from "react";
import { useLocation, useHistory } from "react-router-dom";
import {
  Button
} from "reactstrap";
// javascript plugin used to create scrollbars on windows
import PerfectScrollbar from "perfect-scrollbar";

import Sidebar from "components/Sidebar/Sidebar.js";

import { routes } from "routes.js";

import { BackgroundColorContext } from "contexts/BackgroundColorContext";
import HeiknStockChart from "components/HeiknStockChart"
import HeiknStockChartItem from "components/ItemChart"
import HeiknStockSlicedChart from "components/HeiknStockSlicedChart"
import ChartWithNewApi from "components/api-chart/ChartWithNewApi";

var ps;

function HomePage() {
  const history = useHistory();
  const initInstance = history.location.state ? history.location.state.initInstance : null;
  const [viewType, setViewType] = React.useState(0);
  const [isShowSidebar, setShowSidebar] = React.useState(false);
  const [selectedInstance, setSelectedInstance] = React.useState(
    initInstance ? initInstance : 'forward_test'
  );
  const location = useLocation();
  const mainPanelRef = React.useRef(null);

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

  const handleSidebarChange = () => {
    setShowSidebar(!isShowSidebar);
  };

  const handleInstanceChange = (instance) => {
    setSelectedInstance(instance)
  }

  const handleChartRedirect = (flag) => {
    setViewType(flag)
  }

  const renderChart = (isShowSidebar, color) => {
    let result = ''
    switch (viewType) {
      case 0:
        result = <div className={`main-panel ${!isShowSidebar ? 'full-width' : ''}`} ref={mainPanelRef} data={color}>
          <HeiknStockChart selectedInstance={selectedInstance} handleChartRedirect={handleChartRedirect}/>
        </div>
        break;
      case 1:
        result = <div className={`main-panel ${!isShowSidebar ? 'full-width' : ''}`} ref={mainPanelRef} data={color}>
        <HeiknStockChartItem selectedInstance={selectedInstance} handleChartRedirect={handleChartRedirect}/>
       </div>
        break;
      case 2:
        result = <div className={`main-panel ${!isShowSidebar ? 'full-width' : ''}`} ref={mainPanelRef} data={color}>
          <HeiknStockSlicedChart selectedInstance={selectedInstance} handleChartRedirect={handleChartRedirect}/>
        </div>
        break;
      case 3:
        result = <div className={`main-panel ${!isShowSidebar ? 'full-width' : ''}`} ref={mainPanelRef} data={color}>
         <ChartWithNewApi selectedInstance={selectedInstance} handleChartRedirect={handleChartRedirect}></ChartWithNewApi>
        </div>
        break;
    }
    return result
  }

  return (
    <BackgroundColorContext.Consumer>
      {({ color }) => (
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
                subInstance={'view'}
                isAdminPage={false}
                routes={routes}
                selectedInstance={selectedInstance}
                handleSidebarChange={handleSidebarChange}
                handleInstanceChange={handleInstanceChange}
              />
            )}
            {renderChart(isShowSidebar, color)}

          </div>
        </React.Fragment>
      )}
    </BackgroundColorContext.Consumer>
  );
}

export default HomePage;