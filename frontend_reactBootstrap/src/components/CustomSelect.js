import React, { Component } from "react"
import Select from 'react-select'

class CustomSelect extends React.Component {
  render() {
    const {
      isValid
    } = this.props

    const customStyles = {
      control: (base, state) => ({
        ...base,
        // state.isFocused can display different borderColor if you need it
        borderColor: state.isFocused ?
          '#ddd' : isValid ?
          '#ddd' : 'red',
        // overwrittes hover style
        '&:hover': {
          borderColor: state.isFocused ?
            '#ddd' : isValid ?
            '#ddd' : 'red'
        }
      })
    }
    return <Select styles={ customStyles } {...this.props}/>
  }
}

export default CustomSelect;