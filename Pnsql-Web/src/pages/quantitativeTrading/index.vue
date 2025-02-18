<template>
  <div class="detail-deploy">
    <div class="space-container">
      <div class="card-layout">
        <div class="image-wrapper">
          <img class="left-align-image" src="/public/AAAA.jpg" alt="Button Image" />
        </div>
        <t-button class="styled-button" @click="onPrimayButtonClick">爬虫启动</t-button>
        <t-select
          v-model="selectedStock"
          :options="stockOptions"
          placeholder="请选择或输入股票代码"
          style="margin-left: 15px; width: 150px"
          filterable
          allow-input
          @change="handleStockChange"
          @input="handleInputChange"
          @blur="handleInputBlur"
        >
          <template #option="{ option }">
            <span>{{ option.value }}</span>
            <span class="option-comment"> - {{ option.label }}</span>
          </template>
        </t-select>
        <span style="margin-left: 10px; display: inline-block; width: 50px; text-align: center">
          {{ currentStockPosition }}/{{ totalStockCount }}
        </span>
        <div class="switch-container">
          <t-switch v-model="isFollowed" class="custom-switch" @change="handleSwitchChange" />
          <span class="switch-label">{{ isFollowed ? '已关注' : '未关注' }}</span>
        </div>
        <t-button style="margin-left: 10px" @click="prevStock"> < </t-button>
        <t-button style="margin-left: 5px; margin-right: 10px" @click="nextStock"> > </t-button>

        <!-- 将日期选择器和单选框放入到这个卡片中 -->
        <div class="additional-options">
          <t-date-picker
            v-model="selectedDate"
            placeholder="选择日期"
            style="margin-right: 10px"
            @change="handleDateChange"
          />
          <t-radio-group v-model="selectedCondition" variant="primary-filled" @change="handleCondition">
            <t-radio-button v-for="item in conditions" :key="item" :value="item">
              {{ item }}
            </t-radio-button>
          </t-radio-group>
        </div>
      </div>
      <t-loading v-if="isLoading" text="计算中..." size="small"></t-loading>
      <div class="spacer"></div>
      <div class="center-content">
        <t-button class="styled-button" @click="showPercentageView(50)">180日</t-button>
        <t-button class="styled-button" @click="showPercentageView(70)">365日</t-button>
        <t-button class="styled-button" @click="showPercentageView(100)">900日</t-button>
      </div>
    </div>

    <t-card class="trading-card-container" :bordered="false">
      <div class="line-chart">
        <div id="lineChartContainer" style="width: 100%; height: 630px"></div>
      </div>
      <trading-diglog ref="tradingDigLog"></trading-diglog>
    </t-card>
  </div>
</template>

<script setup lang="ts">
import * as echarts from 'echarts';
import { MessagePlugin } from 'tdesign-vue-next';
import { computed, onMounted, ref } from 'vue';

// eslint-disable-next-line camelcase
import {
  getAnnualMovingAverage,
  getDragon_queryDate,
  getFollowStock,
  getSixtyMovingAverage,
  getStockF0,
  uptFollowStatus,
} from '@/api/services/trading';

import TradingDiglog from './TradingDiglog.vue';

// 定义格式化日期的函数
const cacheSize = 10; // 每次缓存 10 支股票
const dataCache = new Map(); // 使用 Map 保存缓存数据

// 定义格式化日期的函数
function formatDate(date) {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
}

// 图表相关状态
const tradingDigLog = ref();
const loadingCounter = ref(0);
const isLoading = computed(() => loadingCounter.value > 0);
const stockData = ref([]);
let myChart: echarts.ECharts;

// 缩放状态管理
const dataZoomState = ref({ start: 0, end: 100 });

// 股票选择器相关状态
const stockOptions = ref<{ label: string; value: string; follow: number }[]>([]);
const selectedStock = ref('');
const selectedStockName = ref('');
const currentStockPosition = ref(1);
const totalStockCount = ref(0);
const isFollowed = ref(false);

// 新增的状态
const today = new Date();
const selectedDate = ref(today);
const selectedCondition = ref('');
const conditions = ['龙回头', '60 破均', '年线破均'];

// 处理日期更改事件
const handleDateChange = () => {
  // 重置单选框选中状态
  selectedCondition.value = '';
};

// 更新关注状态
const updateFollowStatus = (stockTicker: string) => {
  const selectedOption = stockOptions.value.find((option) => option.value === stockTicker);
  if (selectedOption) {
    isFollowed.value = selectedOption.follow === 1;
  }
};

// 处理开关状态变化
const handleSwitchChange = async () => {
  try {
    const response = await uptFollowStatus(selectedStock.value, isFollowed.value);
    const selectedOption = stockOptions.value.find((option) => option.value === selectedStock.value);
    if (selectedOption) {
      selectedOption.follow = isFollowed.value ? 1 : 0;
    }
  } catch (error) {
    console.error('更新关注状态失败', error);
    isFollowed.value = !isFollowed.value;
  }
};

// 根据X轴百分比调整视图显示范围
const showPercentageView = (percentage: number) => {
  dataZoomState.value = {
    start: 100 - percentage,
    end: 100,
  };
  updateChart();
};

// 获取当前可见数据
const getVisibleData = () => {
  const dataLength = stockData.value.length;
  const startIndex = Math.floor((dataZoomState.value.start / 100) * dataLength);
  const endIndex = Math.ceil((dataZoomState.value.end / 100) * dataLength);
  return stockData.value.slice(startIndex, endIndex);
};

// 更新图表配置
const updateChart = () => {
  if (!myChart || stockData.value.length === 0) return;

  const visibleData = getVisibleData();
  if (visibleData.length === 0) return;

  const yAxisRange = calculateDynamicYAxis(visibleData);
  const boxplotData = visibleData.map((item) => {
    const boxplotValue = [item.f5, item.f2, (item.f2 + item.f3) / 2, item.f3, item.f4];
    const itemStyle = {
      borderColor: item.f2 > item.f3 ? '#008000' : '#d14a61',
      color: item.f2 > item.f3 ? '#008000' : '#d14a61',
      borderWidth: 1.5,
    };
    return { value: boxplotValue, itemStyle };
  });

  const option = {
    title: {
      text: `${selectedStockName.value}`,
      left: 'center',
      textStyle: {
        color: '#333',
        fontSize: 16,
      },
    },
    animation: false,
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross',
        label: {
          backgroundColor: '#6a7985',
        },
      },
      formatter: (params) => {
          const date = params[0].axisValue;
          const dataIndex = params[0].dataIndex;
          const currentData = stockData.value[dataIndex];

          let html = `
            <div style="
              padding: 8px;
              background: #fff;
              border-radius: 4px;
              box-shadow: 0 2px 8px rgba(0,0,0,0.1);
              min-width: 180px;
            ">
              <div style="
                color: #333;
                font-weight: 500;
                border-bottom: 1px solid #eee;
                padding-bottom: 6px;
                margin-bottom: 6px;
              ">
                ${date}
              </div>
          `;

          // 显示均线数据
          params.forEach((param) => {
            if (param.seriesType === 'line') {
              html += `
                <div style="
                  display: flex;
                  align-items: center;
                  margin: 4px 0;
                  font-size: 13px;
                ">
                  <span style="
                    display: inline-block;
                    width: 10px;
                    height: 10px;
                    background: ${param.color};
                    margin-right: 8px;
                    border-radius: 2px;
                  "></span>
                  <span style="color: #666">
                    ${param.seriesName.replace('k-', '')}日均线:
                    <span style="
                      color: #333;
                      font-weight: 600;
                      margin-left: 4px;
                    ">
                      ${param.value?.toFixed(2) || '--'}
                    </span>
                  </span>
                </div>
              `;
            }
          });
          if (currentData?.f9 !== undefined) {
            const changeValue = Number(currentData.f9);
            const isPositive = changeValue >= 0;

            html += `
              <div style="
                margin-top: 8px;
                padding-top: 8px;
                border-top: 1px solid #eee;
              ">
                <div style="
                  display: flex;
                  align-items: center;
                  justify-content: space-between;
                ">
                  <span style="color: #666; font-size: 13px">涨跌幅：</span>
                  <span style="
                    color: ${isPositive ? '#cf1322' : '#009900'};
                    font-weight: 600;
                    font-size: 13px;
                  ">
                    ${isPositive ? '↑' : '↓'}
                    ${(changeValue * 100).toFixed(2)}%
                  </span>
                </div>
              </div>
            `;
          }
          html += `</div>`; // 关闭最外层div
          return html;
        }
    },
    legend: {
      data: ['k-5', 'k-10', 'k-20', 'k-30', 'k-60', 'k-120', 'k-250'],
      top: '5%',
      orient: 'horizontal',
      padding: [10, 50],
      itemGap: 20,
      selected: {
        'k-5': true,
        'k-10': false,
        'k-20': false,
        'k-30': true,
        'k-60': true,
        'k-120': true,
        'k-250': true,
      },
    },
    toolbox: {
      feature: {
        dataZoom: {
          yAxisIndex: 'none'
        }
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '15%',
      containLabel: true,
    },
    xAxis: {
      type: 'category',
      boundaryGap: true,
      data: visibleData.map((item) => item.f1),
      axisLabel: {
        color: '#666',
        rotate: 0,
        margin: 10,
      },
      axisLine: {
        lineStyle: {
          color: '#ccc',
        },
      },
    },
    yAxis: {
      type: 'value',
      min: yAxisRange.min,
      max: yAxisRange.max,
      axisLabel: {
        color: '#666',
        formatter: (value: number) => value.toFixed(1),
      },
      axisLine: { lineStyle: { color: '#ccc' } },
      splitLine: { lineStyle: { color: '#eee' } },
    },
    series: [
      // 保留所有均线系列配置
      {
        name: 'k-5',
        type: 'line',
        data: visibleData.map((item) => item.f12),
        smooth: true,
        symbol: 'none',
        lineStyle: { color: '#0c0a0a', width: 1 },
      },
      {
        name: 'k-10',
        type: 'line',
        data: visibleData.map((item) => item.f13),
        smooth: true,
        symbol: 'none',
        lineStyle: { color: '#efd632', width: 1 },
      },
      {
        name: 'k-20',
        type: 'line',
        data: visibleData.map((item) => item.f14),
        smooth: true,
        symbol: 'none',
        lineStyle: { color: '#e522e2', width: 1 },
      },
      {
        name: 'k-30',
        type: 'line',
        data: visibleData.map((item) => item.f15),
        smooth: true,
        symbol: 'none',
        lineStyle: { color: '#529d0d', width: 1 },
      },
      {
        name: 'k-60',
        type: 'line',
        data: visibleData.map((item) => item.f16),
        smooth: true,
        symbol: 'none',
        lineStyle: { color: '#1E90FF', width: 1 },
      },
      {
        name: 'k-120',
        type: 'line',
        data: visibleData.map((item) => item.f17),
        smooth: true,
        symbol: 'none',
        lineStyle: { color: '#e522e2', width: 1 },
      },
      {
        name: 'k-250',
        type: 'line',
        data: visibleData.map((item) => item.f18),
        smooth: true,
        symbol: 'none',
        lineStyle: { color: '#ff0000', width: 1 },
      },
      // K线图配置（隐藏提示）
      {
        name: 'Boxplot',
        type: 'boxplot',
        data: boxplotData,
        boxWidth: 2,
        tooltip: { show: false }, // 禁用提示
        emphasis: { disabled: true },
      }
    ],
    dataZoom: [
      {
        type: 'slider',
        start: dataZoomState.value.start,
        end: dataZoomState.value.end,
        realtime: true,
        filterMode: 'filter',
        zoomLock: false,
      },
      { type: 'inside' },
    ],
  };

  myChart.setOption(option, {
    replaceMerge: ['yAxis', 'xAxis', 'series', 'dataZoom', 'legend'],
  });
};

// 计算动态Y轴范围
const calculateDynamicYAxis = (data: typeof stockData.value) => {
  if (data.length === 0) return { min: 0, max: 100 };

  const f12Values = data.map((item) => item.f12).filter((value) => value != null && value !== 0);
  const f13Values = data.map((item) => item.f13).filter((value) => value != null && value !== 0);
  const f14Values = data.map((item) => item.f14).filter((value) => value != null && value !== 0);
  const f15Values = data.map((item) => item.f15).filter((value) => value != null && value !== 0);
  const f16Values = data.map((item) => item.f16).filter((value) => value != null && value !== 0);
  const f17Values = data.map((item) => item.f17).filter((value) => value != null && value !== 0);
  const f18Values = data.map((item) => item.f18).filter((value) => value != null && value !== 0);
  const boxplotValues = data.flatMap((item) => [item.f5, item.f2, item.f3, item.f4]).filter((value) => value !== 0);
  const allValues = f12Values.concat(f13Values, f14Values, f15Values, f16Values, f17Values, f18Values, boxplotValues);

  const minValue = Math.min(...allValues);
  const maxValue = Math.max(...allValues);

  if (minValue === maxValue) {
    const offset = Math.abs(minValue * 0.1);
    return { min: minValue - offset, max: maxValue + offset };
  }

  return {
    min: minValue - (maxValue - minValue) * 0.005,
    max: maxValue + (maxValue - minValue) * 0.01,
  };
};

// 条件单选框点击处理
const handleCondition = async () => {
  let date = selectedDate.value;
  loadingCounter.value++; // 启动加载计数器

  try {
    if (typeof date === 'string') {
      date = new Date(date);
      if (isNaN(date.getTime())) {
        console.error('Invalid date string:', selectedDate.value);
        loadingCounter.value--; // 确保在错误情境下也能减值
        return;
      }
    }

    let response;
    const formattedDate = formatDate(date);

    if (formattedDate) {
      if (selectedCondition.value === '龙回头') {
        response = await getDragon_queryDate(formattedDate);
      } else if (selectedCondition.value === '60 破均') {
        response = await getSixtyMovingAverage(formattedDate);
      } else if (selectedCondition.value === '年线破均') {
        response = await getAnnualMovingAverage(formattedDate);
      }

      if (response && response.data.data && response.data.data.length) {
        stockOptions.value = response.data.data.map((item) => ({
          label: `${item.stock_ticker} (${item.stock_name})`,
          value: item.stock_ticker,
          follow: 0, // 初始关注状态为未关注
        }));

        totalStockCount.value = stockOptions.value.length;

        if (stockOptions.value.length > 0) {
          selectedStock.value = stockOptions.value[0].value;
          selectedStockName.value = stockOptions.value[0].label.split(' (')[1].slice(0, -1);
          currentStockPosition.value = 1;
          updateFollowStatus(selectedStock.value);
          await loadStockData(selectedStock.value);

          // 预加载前缓存数据
          await preloadStockData(stockOptions.value, 0, cacheSize);
        }
      } else {
        MessagePlugin.info({ content: '当天无策略数据', duration: 2000 });
        // 清空选择器数据
        stockOptions.value = [];
        selectedStock.value = '';
        selectedStockName.value = '';
        currentStockPosition.value = 0;
        totalStockCount.value = 0;
        isFollowed.value = false;
        stockData.value = [];
        updateChart();
      }
    }
  } catch (error) {
    console.error('请求过程中出现错误:', error);
  } finally {
    loadingCounter.value--; // 加载完成关闭
  }
};

// 初始化图表
onMounted(async () => {
  const chartDom = document.getElementById('lineChartContainer');
  if (chartDom) {
    myChart = echarts.init(chartDom);
    myChart.on('dataZoom', (params) => {
      if (Array.isArray(params)) {
        params.forEach((p) => {
          dataZoomState.value = {
            start: Math.round(p.start),
            end: Math.round(p.end),
          };
        });
      } else {
        dataZoomState.value = {
          start: Math.round(params.start),
          end: Math.round(params.end),
        };
      }
      updateChart();
    });
  }

  loadingCounter.value++; // 开始加载，计数器加 1
  try {
    const StockList = await getFollowStock();
    if (StockList?.data?.data) {
      stockOptions.value = StockList.data.data.map((item) => ({
        label: `${item.stock_ticker} (${item.stock_name})`,
        value: item.stock_ticker,
        follow: item.follow,
      }));

      totalStockCount.value = stockOptions.value.length;
      if (stockOptions.value.length > 0) {
        selectedStock.value = stockOptions.value[0].value;
        selectedStockName.value = stockOptions.value[0].label.split(' (')[1].slice(0, -1);
        updateFollowStatus(selectedStock.value);

        // 加载并显示第一个股票数据
        await loadStockData(selectedStock.value);
        updateChart(); // 确保初始数据显示在图表上

        // 对更大范围进行预加载
        await preloadStockData(stockOptions.value, 0, cacheSize); // 从列表起始位置预加载
      }
    }
  } catch (error) {
    console.error('Failed to fetch stock data', error);
  } finally {
    loadingCounter.value--; // 加载结束，计数器减 1
  }
});

// 预加载股票数据，并保存到缓存
const preloadStockData = async (stockList: Array<any>, startIndex: number, batchSize: number) => {
  loadingCounter.value++; // 开始预加载，计数器加 1
  const loadPromises = [];

  for (let i = startIndex; i < Math.min(stockList.length, startIndex + batchSize); i++) {
    const ticker = stockList[i].value;
    if (!dataCache.has(ticker)) {
      loadPromises.push(loadStockData(ticker, false)); // 传递一个标志位，表示不需要更新图表
    }
  }

  await Promise.all(loadPromises);
  loadingCounter.value--; // 预加载结束，计数器减 1
};

// 加载股票数据
const loadStockData = async (stockTicker: string, updateChartFlag = true) => {
  // 只有需要更新图表时才做股票校验
  if (updateChartFlag && selectedStock.value !== stockTicker) return;
  // 预加载分支：直接缓存数据不更新图表
  if (!updateChartFlag) {
    if (dataCache.has(stockTicker)) return;
    try {
      const response = await getStockF0(stockTicker);
      if (response?.data?.data) {
        const newData = processData(response.data.data);
        dataCache.set(stockTicker, newData); // 静默缓存
      }
    } catch (error) {
      console.error('预加载失败', stockTicker, error);
    }
    return;
  }

  // 主显示分支：正常处理当前股票
  if (dataCache.has(stockTicker)) {
    stockData.value = dataCache.get(stockTicker);
    dataZoomState.value = { start: 0, end: 100 }; // 重置缩放状态
    updateChart();
    return;
  }

  try {
    const response = await getStockF0(stockTicker);
    if (response?.data?.data) {
      const newData = processData(response.data.data);
      stockData.value = newData;
      dataCache.set(stockTicker, newData);
      dataZoomState.value = { start: 0, end: 100 }; // 重置缩放状态
      updateChart();
    }
  } catch (error) {
    console.error('加载失败', error);
  }
};

// 新增数据处理函数
const processData = (rawData: any[]) => {
  return rawData.map((item) => ({
    // 直接保留原始值的字段
    f1: item.f1, // 日期
    f2: item.f2, // 开盘价
    f3: item.f3, // 收盘价
    f4: item.f4, // 最高价
    f5: item.f5, // 最低价
    f9: item.f9, // 新增涨跌幅字段

    // 需要处理零值的移动平均线字段
    f12: item.f12 === 0 ? null : item.f12, // 5日均线
    f13: item.f13 === 0 ? null : item.f13, // 10日均线
    f14: item.f14 === 0 ? null : item.f14, // 20日均线
    f15: item.f15 === 0 ? null : item.f15, // 30日均线
    f16: item.f16 === 0 ? null : item.f16, // 60日均线
    f17: item.f17 === 0 ? null : item.f17, // 120日均线
    f18: item.f18 === 0 ? null : item.f18, // 250日均线
  }));
};

// 股票选择器切换事件
const handleStockChange = async (value: string) => {
  const selectedOption = stockOptions.value.find((option) => option.value === value);

  if (selectedOption) {
    selectedStockName.value = selectedOption.label.split(' (')[1].slice(0, -1);
    const index = stockOptions.value.indexOf(selectedOption);
    currentStockPosition.value = index + 1;
    updateFollowStatus(value);
    await loadStockData(value);
    await preloadStockData(stockOptions.value, index, cacheSize);
  }
};

// 切换到上一个股票
const prevStock = async () => {
  const currentIndex = stockOptions.value.findIndex((option) => option.value === selectedStock.value);
  if (currentIndex > 0) {
    loadingCounter.value++; // 开始操作，计数器加 1
    const prevOption = stockOptions.value[currentIndex - 1];
    selectedStock.value = prevOption.value;
    selectedStockName.value = prevOption.label.split(' (')[1].slice(0, -1);
    currentStockPosition.value = currentIndex;
    updateFollowStatus(prevOption.value);
    await loadStockData(prevOption.value);
    // 预加载前面的股票，保证起始索引不小于 0
    const startIndex = Math.max(0, currentIndex - cacheSize);
    await preloadStockData(stockOptions.value, startIndex, cacheSize);
    loadingCounter.value--; // 操作结束，计数器减 1
  }
};

// 切换到下一个股票
const nextStock = async () => {
  const currentIndex = stockOptions.value.findIndex((option) => option.value === selectedStock.value);
  if (currentIndex < stockOptions.value.length - 1) {
    loadingCounter.value++; // 开始操作，计数器加 1
    const nextOption = stockOptions.value[currentIndex + 1];
    selectedStock.value = nextOption.value;
    selectedStockName.value = nextOption.label.split(' (')[1].slice(0, -1);
    currentStockPosition.value = currentIndex + 2;
    updateFollowStatus(nextOption.value);
    await loadStockData(nextOption.value);
    // 预加载后面的股票，保证结束索引不超过数组长度
    const startIndex = Math.min(stockOptions.value.length - 1, currentIndex + 1);
    await preloadStockData(stockOptions.value, startIndex, cacheSize);
    loadingCounter.value--; // 操作结束，计数器减 1
  }
};

// 处理输入变化
const handleInputChange = (value: string) => {
  selectedStock.value = value;
};

// 处理输入框失去焦点
const handleInputBlur = async () => {
  const exactMatch = stockOptions.value.find((option) => option.value === selectedStock.value);
  if (!exactMatch) {
    await loadStockData(selectedStock.value);
  }
};

// 其他方法保持不变
const onPrimayButtonClick = () => {
  tradingDigLog.value.onClick();
};
</script>

<style scoped>
.space-container {
  width: 100%;
  display: flex;
  align-items: center;
  padding-bottom: 10px;
  border-radius: 8px;
  gap: 10px;
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
  border-radius: 4px;
  padding: 8px 20px;
  box-shadow: 0 2px 4px rgba(0, 102, 204, 0.3);
  cursor: pointer;
  transition:
    background-color 0.2s,
    transform 0.2s;
}

.styled-button.active {
  background-color: #004d99;
}

.styled-button:hover {
  transform: translateY(-2px);
}

.spacer {
  flex-grow: 1;
}

.center-content {
  display: flex;
  align-items: center;
  gap: 10px;
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
  --td-comp-paddingTB-xxl: 10px;
  --td-comp-paddingLR-xxl: 0px;
  padding: var(--td-comp-paddingTB-xxl) var(--td-comp-paddingLR-xxl);
}

.trading-card-container :deep(.t-card__body) {
  padding: 0;
}

/* 控制注释的字体大小和颜色 */
.option-comment {
  font-size: 12px;
  color: #999;
  margin-left: 5px;
}

/* 开关状态和标签的容器样式 */
.switch-container {
  display: flex;
  align-items: center;
  margin-left: 10px;
}

/* 自定义开关样式 */
.custom-switch {
}

/* 开关标签样式 */
.switch-label {
  margin-left: 5px;
  font-size: 14px;
  color: #666;
}

/* 额外选项样式 */
.additional-options {
  display: flex;
  align-items: center;
}

.right-content {
  display: flex;
}
</style>
