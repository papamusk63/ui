import React, { useEffect, useState } from 'react';

import Widget from './components/modal/Widget';

import { getStockModalData } from 'api/Api';

const WatchListEditColumnWidget = (props) => {
  const [totalNodes, setTotalNodes] = useState([]);
  const [currentNodes, setCurrentNodes] = useState(props.selectedColumns);
  
  const handleCurrentNodesChanged = (nodes) => {
    setCurrentNodes(nodes);
    props.setColumns(nodes)
  };

  const handleVisible = (visibleStatus) => {
    props.handleModalClose()
  };

  useEffect(() => {
    let nodes = [];
    let childNodes = [];

    const getModalData = async () => {
      let res = await getStockModalData();
      if (res.result) {
        const avgBars = res.result.avg_bars;
        const avgLosingTrade = res.result.avg_losing_trade;
        const avgTrade = res.result.avg_trade;
        const buyHold = res.result.buy_hold;

        // Avg # Bars
        childNodes = [];
        avgBars.total.map((node, index) => {
          childNodes.push({
            label: node,
            value: 'child_value_1_' + (index + 1),
            default: avgBars.defaults.includes(node) ? true : false,
          });
        });

        if (childNodes.length > 0) {
          nodes.push({
            label: 'Avg # Bars',
            value: 'parent_value_1',
            children: childNodes,
            default: true,
          });
        } 

        // Avg Losing Trade
        childNodes = [];
        avgLosingTrade.total.map((node, index) => {
          childNodes.push({
            label: node,
            value: 'child_value_2_' + (index + 1),
            default: avgLosingTrade.defaults.includes(node) ? true : false,
          });
        });

        if (childNodes.length > 0) {
          nodes.push({
            label: 'Avg Losing Trade',
            value: 'parent_value_2',
            children: childNodes,
            default: true,
          });
        } else {
          nodes.push({
            label: 'Avg Losing Trade',
            value: 'parent_value_2',
            default: false,
          });
        }

        // Avg Trade
        childNodes = [];
        avgTrade.total.map((node, index) => {
          childNodes.push({
            label: node,
            value: 'child_value_4_' + (index + 1),
            default: avgTrade.defaults.includes(node) ? true : false,
          });
        });

        if (childNodes.length > 0) {
          nodes.push({
            label: 'Avg Trade',
            value: 'parent_value_4',
            children: childNodes,
            default: false,
          });
        }

        // Buy Hold
        childNodes = [];
        buyHold.total.map((node, index) => {
          childNodes.push({
            label: node,
            value: 'child_value_5_' + (index + 1),
            default: buyHold.defaults.includes(node) ? true : false,
          });
        });

        if (childNodes.length > 0) {
          nodes.push({
            label: 'Buy & Hold',
            value: 'parent_value_5',
            children: childNodes,
            default: true,
          });
        } 

        const commission_paid = res.result.commission_paid;
        childNodes = [];
        commission_paid.total.map((node, index) => {
          childNodes.push({
            label: node,
            value: 'child_value_6_' + (index + 1),
            default: commission_paid.defaults.includes(node) ? true : false,
          });
        });

        if (childNodes.length > 0) {
          nodes.push({
            label: 'Commission Paid:',
            value: 'parent_value_6',
            children: childNodes,
            default: true,
          });
        }

        const gross_loss = res.result.gross_loss;
        childNodes = [];
        gross_loss.total.map((node, index) => {
          childNodes.push({
            label: node,
            value: 'child_value_7_' + (index + 1),
            default: gross_loss.defaults.includes(node) ? true : false,
          });
        });

        if (childNodes.length > 0) {
          nodes.push({
            label: 'Gross Loss',
            value: 'parent_value_7',
            children: childNodes,
            default: true,
          });
        } 

        const gross_profit = res.result.gross_profit;
        childNodes = [];
        gross_profit.total.map((node, index) => {
          childNodes.push({
            label: node,
            value: 'child_value_8_' + (index + 1),
            default: gross_profit.defaults.includes(node) ? true : false,
          });
        });

        if (childNodes.length > 0) {
          nodes.push({
            label: 'Gross Profit',
            value: 'parent_value_8',
            children: childNodes,
            default: true,
          });
        }

        // const losing_trade = res.result.losing_trade;
        // childNodes = [];
        // losing_trade.total.map((node, index) => {
        //   childNodes.push({
        //     label: node,
        //     value: 'child_value_9_' + (index + 1),
        //     default: losing_trade.defaults.includes(node) ? true : false,
        //   });
        // });

        // if (childNodes.length > 0) {
        //   nodes.push({
        //     label: 'Losing Trade',
        //     value: 'parent_value_9',
        //     children: childNodes,
        //     default: true,
        //   });
        // } 

        const largest = res.result.largest;
        childNodes = [];
        largest.total.map((node, index) => {
          childNodes.push({
            label: node,
            value: 'child_value_10_' + (index + 1),
            default: largest.defaults.includes(node) ? true : false,
          });
        });

        if (childNodes.length > 0) {
          nodes.push({
            label: 'Largest',
            value: 'parent_value_10',
            children: childNodes,
            default: true,
          });
        } 

        const margin_calls = res.result.margin_calls;
        childNodes = [];
        margin_calls.total.map((node, index) => {
          childNodes.push({
            label: node,
            value: 'child_value_11_' + (index + 1),
            default: margin_calls.defaults.includes(node) ? true : false,
          });
        });

        if (childNodes.length > 0) {
          nodes.push({
            label: 'Margin Calls',
            value: 'parent_value_11',
            children: childNodes,
            default: true,
          });
        } 

        const max = res.result.max;
        childNodes = [];
        max.total.map((node, index) => {
          childNodes.push({
            label: node,
            value: 'child_value_12_' + (index + 1),
            default: max.defaults.includes(node) ? true : false,
          });
        });

        if (childNodes.length > 0) {
          nodes.push({
            label: 'Max',
            value: 'parent_value_12',
            children: childNodes,
            default: true,
          });
        }

        const net = res.result.net;
        childNodes = [];
        net.total.map((node, index) => {
          childNodes.push({
            label: node,
            value: 'child_value_13_' + (index + 1),
            default: net.defaults.includes(node) ? true : false,
          });
        });

        if (childNodes.length > 0) {
          nodes.push({
            label: 'Net',
            value: 'parent_value_13',
            children: childNodes,
            default: true,
          });
        } 

        const number = res.result.number;
        childNodes = [];
        number.total.map((node, index) => {
          childNodes.push({
            label: node,
            value: 'child_value_14_' + (index + 1),
            default: number.defaults.includes(node) ? true : false,
          });
        });

        if (childNodes.length > 0) {
          nodes.push({
            label: 'Number',
            value: 'parent_value_14',
            children: childNodes,
            default: true,
          });
        } 

        const open = res.result.open;
        childNodes = [];
        open.total.map((node, index) => {
          childNodes.push({
            label: node,
            value: 'child_value_15_' + (index + 1),
            default: open.defaults.includes(node) ? true : false,
          });
        });

        if (childNodes.length > 0) {
          nodes.push({
            label: 'Open',
            value: 'parent_value_15',
            children: childNodes,
            default: true,
          });
        }

        const percent_profitable = res.result.percent_profitable;
        childNodes = [];
        percent_profitable.total.map((node, index) => {
          childNodes.push({
            label: node,
            value: 'child_value_16_' + (index + 1),
            default: percent_profitable.defaults.includes(node) ? true : false,
          });
        });

        if (childNodes.length > 0) {
          nodes.push({
            label: 'Percent Profitable',
            value: 'parent_value_16',
            children: childNodes,
            default: true,
          });
        } 

        const profit_factor = res.result.profit_factor;
        childNodes = [];
        profit_factor.total.map((node, index) => {
          childNodes.push({
            label: node,
            value: 'child_value_17_' + (index + 1),
            default: profit_factor.defaults.includes(node) ? true : false,
          });
        });

        if (childNodes.length > 0) {
          nodes.push({
            label: 'Profit Factor',
            value: 'parent_value_17',
            children: childNodes,
            default: true,
          });
        }  

        const ratio_avg_win = res.result.ratio_avg_win;
        childNodes = [];
        ratio_avg_win.total.map((node, index) => {
          childNodes.push({
            label: node,
            value: 'child_value_18_' + (index + 1),
            default: ratio_avg_win.defaults.includes(node) ? true : false,
          });
        });

        if (childNodes.length > 0) {
          nodes.push({
            label: 'Ratio Avg Win',
            value: 'parent_value_18',
            children: childNodes,
            default: true,
          });
        }   

        const sharpe_ratio = res.result.sharpe_ratio;
        childNodes = [];
        sharpe_ratio.total.map((node, index) => {
          childNodes.push({
            label: node,
            value: 'child_value_19_' + (index + 1),
            default: sharpe_ratio.defaults.includes(node) ? true : false,
          });
        });

        if (childNodes.length > 0) {
          nodes.push({
            label: 'Sharpe Ratio',
            value: 'parent_value_19',
            children: childNodes,
            default: true,
          });
        }    

        const take_at = res.result.take_at;
        childNodes = [];
        take_at.total.map((node, index) => {
          childNodes.push({
            label: node,
            value: 'child_value_20_' + (index + 1),
            default: take_at.defaults.includes(node) ? true : false,
          });
        });

        if (childNodes.length > 0) {
          nodes.push({
            label: 'Take At',
            value: 'parent_value_20',
            children: childNodes,
            default: true,
          });
        }    

        const comment = res.result.comment;
        childNodes = [];
        comment.total.map((node, index) => {
          childNodes.push({
            label: node,
            value: 'child_value_21_' + (index + 1),
            default: comment.defaults.includes(node) ? true : false,
          });
        });

        if (childNodes.length > 0) {
          nodes.push({
            label: 'Comment',
            value: 'parent_value_21',
            children: childNodes,
            default: true,
          });
        } 

      }
      setTotalNodes(nodes);
    };
    getModalData();
  }, []);

  return (
    <div className="watch-list-edit-column-widget">
      {totalNodes.length > 0 && (
        <Widget
          totalNodes={totalNodes}
          currentNodes={currentNodes}
          handleCurrentNodesChanged={handleCurrentNodesChanged}
          handleVisible={handleVisible}
        />
      )}
    </div>
  );
};

export default WatchListEditColumnWidget;
