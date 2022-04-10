import React from "react";
import CheckboxTree from "react-checkbox-tree";
import { cloneDeep } from 'lodash';
import CustomDropDown from "./dropDown";
import "react-checkbox-tree/lib/react-checkbox-tree.css";
import "./style.css";

class Widget extends React.Component {
  state = {
    checkedAvailableItem: [],
    expandedAvailableItem: [],
    selectedNode: {
      value: "",
      label: "",
    },
    nodesFilteredAvailableItem: [],
    nodesAvailableItem: [],

    restoreAvailableItems: [],
    restoreCurrentItems: this.props.currentNodes,
    
    checkedCurrrentItem: [],
    expandedCurrrentItem: [],
    currentNodes: this.props.currentNodes,
  };

  constructor(props) {
    super(props);
    this.onCheckAvailableItem = this.onCheckAvailableItem.bind(this);
    this.onExpandAvailableItem = this.onExpandAvailableItem.bind(this);
    this.onFilterChangeAvailableItem = this.onFilterChangeAvailableItem.bind(this);

    this.onCheckCurrentItem = this.onCheckCurrentItem.bind(this);
    this.onExpandCurrentItem = this.onExpandCurrentItem.bind(this);

    this.onAddItems = this.onAddItems.bind(this);
    this.onRemoveItems = this.onRemoveItems.bind(this);
    this.onLoadDefaults = this.onLoadDefaults.bind(this);

    this.onMoveUp = this.onMoveUp.bind(this);
    this.onMoveDown = this.onMoveDown.bind(this);

    this.onRestoreClicked = this.onRestoreClicked.bind(this);
    this.onOkClicked = this.onOkClicked.bind(this);
    this.onCancelClicked = this.onCancelClicked.bind(this);

    this.onGetAvailabelNodes = this.onGetAvailabelNodes.bind(this);
    this.onLoadTotalNodes = this.onLoadTotalNodes.bind(this);
    this.isExistItem = this.isExistItem.bind(this);

  }

  onGetAvailabelNodes() {
    const currentItems = cloneDeep(this.state.currentNodes);
    const totalNodes = cloneDeep(this.props.totalNodes);

    let availableNodes = [];

    totalNodes.map((totalNode) => {
      let parentFlag = false;
      currentItems.map((totalCurrentNode) => {
        if (totalNode.value === totalCurrentNode.value) {
          parentFlag = true;
          if ("children" in totalCurrentNode && "children" in totalNode) {
            let totalCurrnetChildrens = [];
            totalCurrentNode.children.map((totalCurrentChild) => {
              totalCurrnetChildrens.push(totalCurrentChild.value);
            });
            totalNode.children.map((totalChild) => {
              if (!(totalCurrnetChildrens.includes(totalChild.value))) {
                let childFlag = false;
                availableNodes.map((availableNode, index) => {
                  if (availableNode.value === totalCurrentNode.value) {
                    availableNodes[index].children.push(totalChild);
                    childFlag = true;
                  }
                })

                if (!childFlag) {
                  availableNodes.push({ ...totalNode, children: [totalChild] });
                }
              }
            })
          }
        }
      });

      if (!parentFlag) {
        availableNodes.push(totalNode);
      }
    })

    this.setState({
      nodesAvailableItem: availableNodes,
      nodesFilteredAvailableItem: availableNodes,
      restoreAvailableItems: availableNodes,
    });
  }

  onCheckAvailableItem(checkedAvailableItem) {
    this.setState({ checkedAvailableItem });
  }

  onExpandAvailableItem(expandedAvailableItem) {
    this.setState({ expandedAvailableItem }, () => {
      console.log(this.state.expandedAvailableItem);
    });
  }

  onCheckCurrentItem(checkedCurrentItem) {
    this.setState({ checkedCurrentItem });
  }

  onExpandCurrentItem(expandedCurrentItem) {
    this.setState({ expandedCurrentItem }, () => {
      console.log(this.state.expandedCurrentItem);
    });
  }

  onFilterChangeAvailableItem(e) {
    this.setState({ selectedNode: e });
    let filteredNodes = [];
    if (e.value === "All") {
      filteredNodes = cloneDeep(this.state.nodesAvailableItem);
    } else {
      const availableNodes = cloneDeep(this.state.nodesAvailableItem);
      if (e.label.includes("parent")) {
        filteredNodes = availableNodes.filter((node) => node.label === e.label);
      } else {
        availableNodes.map((node) => {
          if ("children" in node) {
            node.children.map((childNode) => {
              if (childNode.label === e.label) {
                filteredNodes.push(node);
              }
            })
          }
        })
      }
    }
    
    this.setState({
      nodesFilteredAvailableItem: filteredNodes,
    })
  }

  sortNodes(nodes) {
    let sortedNodes = nodes;
    // let suffixA, suffixB;
    
    // sortedNodes.map((node) => {
    //   if ("children" in node) {
    //     node.children.sort(function (a, b) {
    //       suffixA = parseInt(a.value.split("_")[3]);
    //       suffixB = parseInt(b.value.split("_")[3]);
    //       return suffixA - suffixB;
    //     });
    //   }
    // })

    // sortedNodes.sort(function (a, b) {
    //   suffixA = parseInt(a.value.split("_")[2]);
    //   suffixB = parseInt(b.value.split("_")[2]);
    //   return suffixA - suffixB;
    // });

    return sortedNodes;
  }

  onAddItems() {
    const checkedItems = cloneDeep(this.state.checkedAvailableItem);
    const availableItems = cloneDeep(this.state.nodesAvailableItem);
    const totalNodes = cloneDeep(this.props.totalNodes);

    let availableNodes = [];
    let newCurrentNodes = [];

    if (checkedItems) {
      checkedItems.map((value) => {
        availableItems.map((availableItem) => {
          if (value.includes("child")) {
            let currentChildItems = [];
            if ("children" in availableItem) {
              availableItem.children.map((childItem) => {
                if (childItem.value === value) {
                  currentChildItems.push(childItem);
                }
              })
    
              if (currentChildItems.length > 0) {
                newCurrentNodes.push({ ...availableItem, children: currentChildItems });
              }
            }
          } else {
            if (availableItem.value === value) {
              newCurrentNodes.push(availableItem);
            }
          }
        })
      });

      
      // merge the new current nodes into original current nodes
      const originCurrentNodes = cloneDeep(this.state.currentNodes);
      let totalNewCurrentNodes = [];
      newCurrentNodes.map((newCurrentNode) => {
        let exist = false;
        originCurrentNodes.map((currentNode) => {
          if (currentNode.value === newCurrentNode.value) {
            let currentChildItems = currentNode.children;
            newCurrentNode.children.map((newChildItem) => {
              currentChildItems.push(newChildItem);
            });
            // totalNewCurrentNodes.push({...currentNode})
            // totalNewCurrentNodes.push({ ...currentNode, children: currentChildItems });
            exist = true;
          }
        })
        
        if (!exist) {
          let parentExist = false;
          totalNewCurrentNodes.map((node, index) => {
            if (node.value === newCurrentNode.value) {
              totalNewCurrentNodes[index].children.push(newCurrentNode.children[0]);
              parentExist = true;
            }
          })
          if (!parentExist) {
            totalNewCurrentNodes.push(newCurrentNode);
          }
        }
      })
      
      let totalCurrentNodes = totalNewCurrentNodes;
      originCurrentNodes.map((originNode) => {
        let exist = false;
        totalNewCurrentNodes.map((newNode) => {
          if (originNode.value === newNode.value) {
            exist = true;
          }
        })
        if (!exist) {
          totalCurrentNodes.push(originNode);
        }
      });

  
      totalNodes.map((totalNode) => {
        let parentFlag = false;
        totalCurrentNodes.map((totalCurrentNode) => {
          if (totalNode.value === totalCurrentNode.value) {
            parentFlag = true;
            if ("children" in totalCurrentNode && "children" in totalNode) {
              let totalCurrnetChildrens = [];
              totalCurrentNode.children.map((totalCurrentChild) => {
                totalCurrnetChildrens.push(totalCurrentChild.value);
              });
              totalNode.children.map((totalChild) => {
                if (!(totalCurrnetChildrens.includes(totalChild.value))) {
                  let childFlag = false;
                  availableNodes.map((availableNode, index) => {
                    if (availableNode.value === totalCurrentNode.value) {
                      availableNodes[index].children.push(totalChild);
                      childFlag = true;
                    }
                  })
  
                  if (!childFlag) {
                    availableNodes.push({ ...totalNode, children: [totalChild] });
                  }
                }
              })
            }
          }
        });
  
        if (!parentFlag) {
          availableNodes.push(totalNode);
        }
      })

      this.setState({
        currentNodes: totalCurrentNodes,
        nodesAvailableItem: availableNodes,
        nodesFilteredAvailableItem: availableNodes,
      });
      
    }
  }

  onRemoveItems() {
    const checkedItems = cloneDeep(this.state.checkedCurrentItem);
    const currentItems = cloneDeep(this.state.currentNodes);
    const totalNodes = cloneDeep(this.props.totalNodes);

    
    let availableNodes = [];
    let newCurrentNodes = [];
    
    if (checkedItems) {
      checkedItems.map((value) => {
        currentItems.map((availableItem) => {
          if (value.includes("child")) {
            let currentChildItems = [];
            if ("children" in availableItem) {
              availableItem.children.map((childItem) => {
                if (childItem.value === value) {
                  currentChildItems.push(childItem);
                }
              })
              
              if (currentChildItems.length > 0) {
                let filteredNode = newCurrentNodes.filter(node => node.value === availableItem.value)
                if (filteredNode.length) {
                  filteredNode[0].children.push( ...currentChildItems );
                } else {
                  newCurrentNodes.push({ ...availableItem, children: currentChildItems });
                }
              }
            }
          } else {
            if (availableItem.value === value) {
              newCurrentNodes.push(availableItem);
            }
          }
        })
      });
      
      // merge the new current nodes into original current nodes

      const originCurrentNodes = cloneDeep(this.state.nodesAvailableItem);
      let totalNewCurrentNodes = [];
      newCurrentNodes.map((newCurrentNode) => {
        let exist = false;
        let currentChildItems
        originCurrentNodes.map((currentNode) => {
          
          if (currentNode.value === newCurrentNode.value) {
            currentChildItems = currentNode.children;
            newCurrentNode.children.map((newChildItem) => {
              currentChildItems.push(newChildItem);
            });
            totalNewCurrentNodes.push({ ...currentNode, children: currentChildItems });
            exist = true;
          }
        })
  
        if (!exist) {
          let parentExist = false;
          totalNewCurrentNodes.map((node, index) => {
            if (node.value === newCurrentNode.value) {
              totalNewCurrentNodes[index].children.push(newCurrentNode.children[0]);
              parentExist = true;
            }
          })
          if (!parentExist) {
            totalNewCurrentNodes.push(newCurrentNode);
          }
        }
      })

      let totalCurrentNodes = totalNewCurrentNodes;
      originCurrentNodes.map((originNode) => {
        let exist = false;
        totalNewCurrentNodes.map((newNode) => {
          if (originNode.value === newNode.value) {
            exist = true;
          }
        })
        if (!exist) {
          totalCurrentNodes.push(originNode);
        }
      });
  
      totalNodes.map((totalNode) => {
        let parentFlag = false;
        totalCurrentNodes.map((totalCurrentNode) => {
          if (totalNode.value === totalCurrentNode.value) {
            parentFlag = true;
            if ("children" in totalCurrentNode && "children" in totalNode) {
              let totalCurrnetChildrens = [];
              totalCurrentNode.children.map((totalCurrentChild) => {
                totalCurrnetChildrens.push(totalCurrentChild.value);
              });
              totalNode.children.map((totalChild) => {
                if (!(totalCurrnetChildrens.includes(totalChild.value))) {
                  let childFlag = false;
                  availableNodes.map((availableNode, index) => {
                    if (availableNode.value === totalCurrentNode.value) {
                      availableNodes[index].children.push(totalChild);
                      childFlag = true;
                    }
                  })
  
                  if (!childFlag) {
                    availableNodes.push({ ...totalNode, children: [totalChild] });
                  }
                }
              })
            }
          }
        });
  
        if (!parentFlag) {
          availableNodes.push(totalNode);
        }
      })
  
      this.setState({
        currentNodes: availableNodes,
        nodesAvailableItem: totalCurrentNodes,
        nodesFilteredAvailableItem: totalCurrentNodes,
      });
    }
  }

  isExistItem(key, item, currentNodes) {
    let isExist = false
    currentNodes.forEach((current) => {
      if (current.value === key) {
        current.children.forEach((child) => {
          if (child.value === item.value) {
            isExist = true
            return
          }
        })
      }
    })
    return isExist  
  }

  onLoadTotalNodes() {
    const totalNodes = this.props.totalNodes;
    let availableNodes = [];

    if (!this.props.currentNodes) {
      return
    }

    totalNodes.map((item) => {
      let pushItem = {...item};
      if ("children" in pushItem) {
        if (pushItem.children.length > 0) {
          let availableChildItems = [];
          pushItem.children.map((childItem) => {
            if (!this.isExistItem(pushItem.value, childItem, this.props.currentNodes)) {
              availableChildItems.push(childItem);
            }
          });

          if (availableChildItems.length > 0) {
            availableNodes.push({...pushItem, children: availableChildItems});
          }
        }
      }
    });
    this.setState({
      nodesAvailableItem: availableNodes,
      nodesFilteredAvailableItem: availableNodes,
    });
  }

  onLoadDefaults() {
    const totalNodes = this.props.totalNodes;
    let defaultNodes = [];
    let availableNodes = [];
    totalNodes.map((item) => {
      let pushItem = {...item};
      if (pushItem.default) {
        if ("children" in pushItem) {
          if (pushItem.children.length > 0) {
            let currentChildItems = [];
            let availableChildItems = [];
            pushItem.children.map((childItem) => {
              if (childItem.default) {
                currentChildItems.push(childItem);
              } else {
                availableChildItems.push(childItem);
              }
            });

            if (currentChildItems.length > 0) {
              defaultNodes.push({...pushItem, children: currentChildItems});
            }

            if (availableChildItems.length > 0) {
              availableNodes.push({...pushItem, children: availableChildItems});
            }
          } else {
            defaultNodes.push(pushItem);
          }
        } else {
          defaultNodes.push(pushItem);
        }
      } else {
        availableNodes.push(pushItem);
      }
    });
    this.setState({
      currentNodes: defaultNodes,
      nodesAvailableItem: availableNodes,
      nodesFilteredAvailableItem: availableNodes,
    });
  }

  moveItem(direction) {
    const checkedItems = cloneDeep(this.state.checkedCurrentItem);
    const currentNodes = cloneDeep(this.state.currentNodes);

    if (checkedItems && Array.isArray(checkedItems)) {
      let moveEnable = true;
      checkedItems.sort();
      let parentSuffix = [];
      let childFlag = false;
      checkedItems.map((item) => {
        if (item.includes("child")) {
          parentSuffix.push(item.split("_")[2]); // push child
          childFlag = true;
        }
        if (item.includes("parent")) {
          if (parentSuffix.length > 0) {
            alert ("Please select one node");
            moveEnable = false;
          } else {
            parentSuffix.push(item.split("_")[2]); // push parent
          }
        }
      });
      const uniqParentSuffix = [...new Set(parentSuffix)];
      if (uniqParentSuffix.length !== 1) {
        alert ("Please select one node");
        moveEnable = false;
      } else {
        let parentValue = '';
        parentValue = "parent_value_" + uniqParentSuffix[0];
        let nodeIndex;
        currentNodes.map((node, index) => {
          if (node.value === parentValue) {
            if (childFlag) {
              if (node.children.length === checkedItems.length) {
                nodeIndex = {
                  status: 'parent',
                  parentIndex: index,
                  childIndex: null,
                };
              } else {
                if (checkedItems.length !== 1) {
                  alert ("Please select one node");
                  moveEnable = false;
                } else {
                  node.children.map((child, childIndex) => {
                    if (child.value === checkedItems[0]) {
                      nodeIndex = {
                        status: 'child',
                        parentIndex: index,
                        childIndex: childIndex,
                      };
                    }
                  })
                }
              }
            } else {
              nodeIndex = {
                status: 'parent',
                parentIndex: index,
                childIndex: null,
              };
            }
          }
        })
        
        if (moveEnable) {
          if (direction === 'up') {
            if (nodeIndex.status === 'parent') {
              if (nodeIndex.parentIndex > 0) {
                const temp = currentNodes[nodeIndex.parentIndex - 1];
                currentNodes[nodeIndex.parentIndex - 1] = currentNodes[nodeIndex.parentIndex];
                currentNodes[nodeIndex.parentIndex] = temp;
              }
            } else {
              if (nodeIndex.childIndex > 0) {
                const temp = currentNodes[nodeIndex.parentIndex].children[nodeIndex.childIndex - 1];
                currentNodes[nodeIndex.parentIndex].children[nodeIndex.childIndex - 1] = currentNodes[nodeIndex.parentIndex].children[nodeIndex.childIndex];
                currentNodes[nodeIndex.parentIndex].children[nodeIndex.childIndex] = temp;
              }
            }
          } else {
            if (nodeIndex.status === 'parent') {
              if (nodeIndex.parentIndex < currentNodes.length - 1) {
                const temp = currentNodes[nodeIndex.parentIndex + 1];
                currentNodes[nodeIndex.parentIndex + 1] = currentNodes[nodeIndex.parentIndex];
                currentNodes[nodeIndex.parentIndex] = temp;
              }
            } else {
              if (nodeIndex.childIndex < currentNodes[nodeIndex.parentIndex].children.length - 1) {
                const temp = currentNodes[nodeIndex.parentIndex].children[nodeIndex.childIndex + 1];
                currentNodes[nodeIndex.parentIndex].children[nodeIndex.childIndex + 1] = currentNodes[nodeIndex.parentIndex].children[nodeIndex.childIndex];
                currentNodes[nodeIndex.parentIndex].children[nodeIndex.childIndex] = temp;
              }
            }
          }
        }

        this.setState({
          currentNodes: currentNodes,
        });
      }
    } else {
      alert ("You didn't select the node");
    }
  }

  onMoveUp() {
    this.moveItem('up');
  }

  onMoveDown() {
    this.moveItem('down');
  }

  onRestoreClicked() {
    this.setState({
      nodesAvailableItem: this.state.restoreAvailableItems,
      currentNodes: this.state.restoreCurrentItems,
    });
  }

  onOkClicked() {
    this.props.handleCurrentNodesChanged(this.state.currentNodes);
    this.props.handleVisible(false);
  }

  onCancelClicked() {
    this.setState({
      nodesAvailableItem: this.state.restoreAvailableItems,
      currentNodes: this.state.restoreCurrentItems,
    });
    this.props.handleVisible(false);
  }

  componentDidMount() {
    this.onGetAvailabelNodes();
    this.onLoadTotalNodes();
  }

  render() {
    const { checkedAvailableItem, expandedAvailableItem, nodesFilteredAvailableItem } = this.state;

    return (
      <div className="widget-container">
        <div className="modal-main">
          <div className="filter-container left-group">
            <div className="left-box-header">
              <span>Available Items</span>
            </div>
            <div className="items-area">
              <CustomDropDown
                nodes={this.state.nodesAvailableItem}
                onChange={this.onFilterChangeAvailableItem}
              />
              <CheckboxTree
                checked={checkedAvailableItem}
                expanded={expandedAvailableItem}
                nodes={nodesFilteredAvailableItem}
                onCheck={this.onCheckAvailableItem}
                onExpand={this.onExpandAvailableItem}
              />
            </div>
            <div className="left-box-footer">
              <div className="modal-btn btn-exchange" onClick={this.onAddItems}>
                <span>{"Add Item(s) >>"}</span>
              </div>
            </div>
          </div>
          <div className="filter-container right-group">
            <div className="right-box-header">
              <span>Available Items</span>
            </div>
            <div className="items-container">
              <div>
                <div className="items-area">
                  <CheckboxTree
                    checked={this.state.checkedCurrentItem}
                    expanded={this.state.expandedCurrentItem}
                    nodes={this.state.currentNodes}
                    onCheck={this.onCheckCurrentItem}
                    onExpand={this.onExpandCurrentItem}
                  />
                </div>
              </div>
              <div className="right-box-btn-group">
                <div className="right-top-btn">
                  <div className="modal-btn" onClick={this.onLoadDefaults}>
                    <span>Load Defaults</span>
                  </div>
                </div>
                <div className="right-bottom-btn">
                  <div className="modal-btn" onClick={this.onMoveUp}>
                    <span>Move Up</span>
                  </div>
                  <div className="modal-btn" onClick={this.onMoveDown}>
                    <span>Move Down</span>
                  </div>
                </div>
              </div>
            </div>
            <div className="right-box-footer">
              <div className="modal-btn btn-exchange" onClick={this.onRemoveItems}>
                <span>{"<< Remove Item(s)"}</span>
              </div>
            </div>
          </div>
        </div>
        <div className="modal-footer">
          <div className="modal-footer-left-button-group">
            <div className="modal-btn restore-btn" onClick={this.onRestoreClicked}>
              <span>Restore</span>
            </div>
          </div>
          <div className="modal-footer-right-button-group">
            <div className="modal-btn ok-btn" onClick={this.onOkClicked}>
              <span>Ok</span>
            </div>
            <div className="modal-btn cancel-btn" onClick={this.onCancelClicked}>
              <span>Cancel</span>
            </div>
          </div>
        </div>
      </div>
    );
  }
}

export default Widget;
