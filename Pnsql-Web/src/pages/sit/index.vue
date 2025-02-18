<template>
  <div id="main" style="width: 100%; height: 400px;"></div>
</template>

<script>
import * as echarts from 'echarts';

export default {
  mounted() {
    // Get the chart DOM element
    var chartDom = document.getElementById('main');
    // Initialize the chart
    var myChart = echarts.init(chartDom);

    // Generate random data for demo
    function randomData() {
      const baseValue = Math.random() * 300;
      return Array.from({ length: 30 }, () => (Math.random() * 50) + baseValue);
    }

    let timeData = Array.from({ length: 30 }, (v, i) => `09/${i+1}`);

    const option = {
      title: {
        text: 'Rainfall vs Evaporation',
        left: 'center'
      },
      tooltip: {
        trigger: 'axis',
        axisPointer: {
          animation: false
        }
      },
      legend: {
        data: ['Evaporation', 'Rainfall'],
        left: 10
      },
      toolbox: {
        feature: {
          dataZoom: {
            yAxisIndex: 'none'
          }
        }
      },
      dataZoom: [
        {
          show: true,
          realtime: true,
          start: 30,
          end: 70,
          xAxisIndex: [0, 1]
        },
        {
          type: 'inside',
          realtime: true,
          start: 30,
          end: 70,
          xAxisIndex: [0, 1]
        }
      ],
      grid: [
        {
          left: 60,
          right: 50,
          height: '35%'
        },
        {
          left: 60,
          right: 50,
          top: '55%',
          height: '35%'
        }
      ],
      xAxis: [
        {
          type: 'category',
          boundaryGap: false,
          axisLine: { onZero: true },
          data: timeData
        },
        {
          gridIndex: 1,
          type: 'category',
          boundaryGap: false,
          axisLine: { onZero: true },
          data: timeData,
          position: 'top'
        }
      ],
      yAxis: [
        {
          name: 'Evaporation(m³/s)',
          type: 'value',
          max: 500
        },
        {
          gridIndex: 1,
          name: 'Rainfall(mm)',
          type: 'value',
          inverse: true
        }
      ],
      series: [
        {
          name: 'Evaporation',
          type: 'line',
          symbolSize: 8,
          data: randomData()
        },
        {
          name: 'Rainfall',
          type: 'line',
          xAxisIndex: 1,
          yAxisIndex: 1,
          symbolSize: 8,
          data: randomData()
        }
      ]
    };

    // Set the option for the chart
    myChart.setOption(option);
  }
}
</script>

<style>
#main {
  width: 100%;
  height: 400px;
}
</style>
