import { MDBCard, MDBCardBody, MDBCardHeader, MDBNav, MDBNavItem } from 'mdbreact';
import React from 'react';
import DBCollectionList from 'components/DBManagement/CollectionList'
import {useThemeColors } from 'contexts/ThemeContext'
import DBControlBar from './ControlBar';
import { useActiveDatabase } from 'contexts/DBDashboardContext';
import DBDatabaseList from './DatabaseList';

function DBContent(props) {
  const colors = useThemeColors()
  const currentDb = useActiveDatabase()
  console.log('currentDb')
  console.log(currentDb)
  console.log(colors)
  return (
    <>
      <DBControlBar />
      <MDBCard style={{backgroundColor: colors.lightBlue}}>
        <MDBCardBody style={{ overflowY: 'auto' }}>
          {currentDb && <DBCollectionList />}
          {!currentDb && <DBDatabaseList />}
        </MDBCardBody>
      </MDBCard>
    </>
  );
}

export default DBContent;