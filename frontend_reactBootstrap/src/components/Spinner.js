import React from "react";

const Spinner = (props) => {
  // props.color: primary,success,danger,warning,info
  const color = props.color?props.color:'primary'

  return (
    <>
      <div className={"spinner-border text-" + color} role="status">
        <span className="sr-only">Loading...</span>
      </div>
    </>
  );
}

export default Spinner;