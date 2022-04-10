import React from 'react';
import { MDBLink, MDBIcon } from 'mdbreact';
import { useThemeColors } from 'contexts/ThemeContext'

function DBDatabase(props) {
  const colors = useThemeColors()
  const buttonStyle = {
    color: colors.actionButtonColor,
    backgroundColor: colors.actionButtonBg,
  }

  const textStyle = {
    color: colors.tableTextColor,
  }

  const rowStyle = {
    backgroundColor: colors.white,
  }

  return (
    <>
      <tr style={rowStyle}>
        <td><span style={textStyle}>{props.index}.</span></td>
        <td><span style={textStyle}>{props.name}</span></td>
        <td>
          <div class="d-flex">
            <MDBLink onClick={(e) => {e.preventDefault(); props.onDeleteClick(); }} style={{...buttonStyle, color: colors.red}}><MDBIcon icon="trash" /></MDBLink>
            <MDBLink onClick={(e) => {e.preventDefault(); props.onSaveClick(); }} style={buttonStyle}><MDBIcon icon="file-export" /></MDBLink>
          </div>
        </td>
      </tr>
    </>
  )
}

export default DBDatabase