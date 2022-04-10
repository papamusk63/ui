import { MDBBox, MDBContainer } from 'mdbreact';
import DBDatabaseActions from './DatabaseActions';
import DBPathway from './Pathway';
import {useThemeColors} from 'contexts/ThemeContext'

function DBControlBar(props) {
  const colors = useThemeColors()
  return (
    <MDBBox class="d-flex justify-content-between align-items-center" style={{backgroundColor: colors.darkBlue}}>
      <DBPathway />
      <DBDatabaseActions />
    </MDBBox>
  );
}

export default DBControlBar;