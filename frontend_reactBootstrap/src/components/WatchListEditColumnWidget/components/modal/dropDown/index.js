import "./style.css";
import Select from 'react-select';
import { useEffect, useState } from "react";

const CustomDropDown = (props) => {
  const { nodes, onChange, inputvalue } = props;
  const [options, setOptions] = useState();
  const [selectedNode, setSelectedNode] = useState();

  useEffect(() => {
    let nodeOptions = [{
      label: "All",
      value: "All",
    }];
    nodes.map((node) => {
      if ("children" in node) {
        node.children.map((child) => {
          nodeOptions.push({
            value: child.value,
            label: child.label,
          });
        })
      }
    });

    setOptions(nodeOptions);

  }, [nodes]);

  return (
    <div className="dropdown-container">
      <Select
        ref={inputvalue}
        value={selectedNode}
        onChange={onChange}
        options={options}
        className="modal-filter-select-box"
        placeholder=""
      />
    </div>
  );
}

export default CustomDropDown;
