<template>
  <div class="detail-deploy">
    <div class="space-container">
      <div class="card-layout">
        <div class="image-wrapper">
          <img class="left-align-image" src="/public/AAAA.jpg" alt="Button Image" />
        </div>
        <t-button class="styled-button" @click="onPrimayButtonClick">爬虫启动</t-button>
      </div>
      <div class="spacer"></div>
      <div class="center-content">
        <t-date-range-picker
          class="right-align"
          v-model="range2"
          :presets="presets"
          :disabled-date="disabledDate"
          @change="onDateRangeChange"
        />
      </div>
    </div>

    <t-card class="trading-card-container" :bordered="false">
      <div class="line-chart">
        <div id="lineChartContainer" style="width: 100%; height: 400px" />
      </div>
      <trading-diglog ref="tradingDigLog"></trading-diglog>
    </t-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue';
import * as echarts from 'echarts';
import dayjs from 'dayjs';
import TradingDiglog from './TradingDiglog.vue';

const tradingDigLog = ref();
const generateData = (days: number) => {
  const startDate = new Date();
  const data: { date: string; value: number }[] = [];

  for (let i = 0; i < days; i++) {
    const date = new Date(startDate);
    date.setDate(date.getDate() - i);
    const value = Math.floor(Math.random() * 1000) + 500;
    data.push({ date: dayjs(date).format('YYYY-MM-DD'), value });
  }

  return data.reverse();
};

const data = generateData(300);
const minDate = dayjs(data[0].date).toDate();
const maxDate = dayjs(data[data.length - 1].date).toDate();

const presets = ref({
  最近180天: [
    dayjs().subtract(179, 'day').startOf('day').isAfter(minDate)
      ? dayjs().subtract(179, 'day').startOf('day').toDate()
      : minDate,
    dayjs().endOf('day').isBefore(maxDate) ? dayjs().endOf('day').toDate() : maxDate,
  ],
  最近30天: [
    dayjs().subtract(29, 'day').startOf('day').isAfter(minDate)
      ? dayjs().subtract(29, 'day').startOf('day').toDate()
      : minDate,
    dayjs().endOf('day').isBefore(maxDate) ? dayjs().endOf('day').toDate() : maxDate,
  ],
});

const range2 = ref<[Date, Date] | null>([minDate, maxDate]);
const selectedDateRange = ref<[Date, Date] | null>([minDate, maxDate]);
let myChart: echarts.ECharts;

onMounted(() => {
  const chartDom = document.getElementById('lineChartContainer');
  if (chartDom) {
    myChart = echarts.init(chartDom);
    updateChart();
    chartDom.addEventListener('mousewheel', handleMouseWheel);
  }
});

const handleMouseWheel = (event: WheelEvent) => {
  event.preventDefault();
  const delta = event.deltaY;
  const [startDate, endDate] = selectedDateRange.value!;
  const step = 5;
  let newStartDate = dayjs(startDate);
  let newEndDate = dayjs(endDate);

  if (delta < 0) {
    newStartDate = newStartDate.add(step, 'day');
    newEndDate = newEndDate.subtract(step, 'day');
  } else {
    newStartDate = newStartDate.subtract(step, 'day');
    newEndDate = newEndDate.add(step, 'day');
  }

  if (newStartDate.isBefore(dayjs(minDate))) newStartDate = dayjs(minDate);
  if (newEndDate.isAfter(dayjs(maxDate))) newEndDate = dayjs(maxDate);

  if (newStartDate.isBefore(newEndDate)) {
    selectedDateRange.value = [newStartDate.toDate(), newEndDate.toDate()];
    range2.value = [newStartDate.toDate(), newEndDate.toDate()];
    updateChart();
  } else {
    console.warn('Invalid Range Update Attempted');
  }
};

const updateChart = () => {
  const filteredData = selectedDateRange.value
    ? data.filter((item) => {
        const itemDate = dayjs(item.date).startOf('day').toDate();
        const start = dayjs(selectedDateRange.value![0]).startOf('day').toDate();
        const end = dayjs(selectedDateRange.value![1]).endOf('day').toDate();
        return itemDate >= start && itemDate <= end;
      })
    : data;

  const targetLabelCount = 10;
  const interval = Math.max(1, Math.floor(filteredData.length / targetLabelCount));

  const option = {
    title: {
      text: '量化数据',
      left: 'center',
      textStyle: { color: '#333', fontSize: 16 },
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross',
        label: { backgroundColor: '#6a7985' },
      },
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '15%',
      containLabel: true,
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: filteredData.map((item) => item.date),
      axisLabel: {
        color: '#666',
        rotate: 0,
        margin: 10,
        interval,
      },
      axisLine: {
        lineStyle: { color: '#ccc' },
      },
    },
    yAxis: {
      type: 'value',
      axisLabel: { color: '#666' },
      axisLine: { lineStyle: { color: '#ccc' } },
      splitLine: { lineStyle: { color: '#eee' } },
    },
    series: [
      {
        name: 'Value',
        type: 'line',
        data: filteredData.map((item) => item.value),
        smooth: true,
        symbol: 'circle',
        symbolSize: 5,
        lineStyle: { color: '#00a4ff' },
        itemStyle: { color: '#00a4ff' },
        areaStyle: {
          color: {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [
              { offset: 0, color: 'rgba(0, 164, 255, 0.4)' },
              { offset: 1, color: 'rgba(0, 164, 255, 0)' },
            ],
            global: false,
          },
        },
      },
    ],
    animation: true,
    animationDuration: 1000,
    animationEasing: 'elasticOut',
    dataZoom: [
      { type: 'slider', start: 0, end: 100 },
      { type: 'inside' },
    ],
  };

  myChart.setOption(option);
};

watch(selectedDateRange, () => {
  updateChart();
});

const onDateRangeChange = (value: [Date, Date] | null) => {
  selectedDateRange.value = value;
  updateChart();
};

const onPrimayButtonClick = () => {
  tradingDigLog.value.onClick();
};

const disabledDate = (date: Date) => {
  return date < minDate || date > maxDate;
};
</script>

<style scoped>
.space-container {
  width: 100%;
  display: flex;
  align-items: center;
  padding-bottom: 10px;
  border-radius: 8px;
}

.card-layout {
  display: flex;
  align-items: center;
  background-color: white;
  padding: 10px 15px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.image-wrapper {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 60px;
  height: 60px;
  border-radius: 50%;
  overflow: hidden;
  border: 1px solid #e0e0e0;
  margin-right: 15px;
}

.left-align-image {
  max-width: 150%;
  max-height: 100%;
}

.styled-button {
  background-color: #0066cc;
  color: white;
  border: none;
  border-radius: 20px;
  padding: 8px 20px;
  box-shadow: 0 2px 4px rgba(0, 102, 204, 0.3);
  cursor: pointer;
  transition: background-color 0.2s, transform 0.2s;
}

.styled-button:hover {
  background-color: #004d99;
  transform: translateY(-2px); /* 按钮抬起效果 */
}

.spacer {
  flex-grow: 1;
}

.center-content {
  display: flex;
  align-items: center;
}

.line-chart {
  width: 100%;
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.trading-card-container {
  padding: var(--td-comp-paddingTB-xxl) var(--td-comp-paddingLR-xxl);
  :deep(.t-card__body) {
    padding: 0;
  }
}
</style>
