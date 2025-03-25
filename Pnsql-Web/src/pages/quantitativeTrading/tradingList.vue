<template>
  <div class="container">
    <div class="date-picker-container">
      <span class="date-picker-label">自选:</span>
      <t-date-picker
        v-model="selectedDate"
        placeholder="选择日期"
        @change="handleDateChange"
        :value="new Date()"
        class="custom-date-picker"
      />
      <span class="date-picker-label" style="padding-left: 50px">龙回头上次记录时间点:</span>
      <t-date-picker
        v-model="dragonLastRecordDate"
        placeholder="选择日期"
        @change="handleDragonLastRecordDateChange"
        class="custom-date-picker"
      />
      <span class="date-picker-label" style="padding-left: 50px">均线上次记录时间点:</span>
      <t-date-picker
        v-model="averageLastRecordDate"
        placeholder="选择日期"
        @change="handleAverageLastRecordDateChange"
        class="custom-date-picker"
      />
      <span class="date-picker-label" style="padding-left: 50px">黄金线上次记录时间点:</span>
      <t-date-picker
        v-model="goleLastRecordDate"
        placeholder="选择日期"
        @change="handleGoleLastRecordDateChange"
        class="custom-date-picker"
      />
    </div>
    <div class="card-container">
      <t-card
        v-for="(data, index) in allData"
        :key="index"
        class="custom-card"
      >
        <template #header>
          <div class="card-title">{{ cardTitles[index] }}</div>
          <!-- 仅在“我的自选”卡片中添加清除按钮 -->
          <template v-if="cardTitles[index] === '我的自选'">
            <t-button
              theme="danger"
              size="small"
              @click="clearData"
              class="clear-button"
            >
              清除
            </t-button>
          </template>
          <t-button
            theme="primary"
            size="small"
            @click="copyData(index)"
            class="copy-button"
          >
            复制
          </t-button>
        </template>
        <t-loading
          v-if="loadingStatus[index]"
          text="加载数据..."
          size="small"
          class="custom-loading"
        />
        <div v-else class="log-container">
          <div class="log-content">
            {{ data.length > 0 ? data.map((item) => item.stock_ticker).join('\n') : '暂时数据......' }}
          </div>
        </div>
      </t-card>
    </div>
    <textarea id="hiddenTextArea" class="hidden-textarea"></textarea>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import {
  getDragon_queryDate,
  getAnnualMovingAverage,
  getSixtyMovingAverage,
  getFollowedList
} from '@/api/services/trading';
import { MessagePlugin } from 'tdesign-vue-next';
import { ResetAllFollows, getRecordDay, updateDragonTime, updateAverageTime, updateGoldTime } from '@/api/services/trading';

// 初始化日期为当天
const selectedDate = ref<Date | null>(new Date());
const dragonLastRecordDate = ref<Date | null>(null);
const averageLastRecordDate = ref<Date | null>(null);
const goleLastRecordDate = ref<Date | null>(null);

// 各个卡片的加载状态
const loadingStatus = ref([true, true, true, true]);

// 存储四个方法的数据
const dragonData = ref([]);
const annualData = ref([]);
const sixtyData = ref([]);
const followedData = ref([]);

// 组合所有数据
const allData = computed(() => [
  dragonData.value,
  annualData.value,
  sixtyData.value,
  followedData.value,
]);

// 卡片标题
const cardTitles = ['龙回头数据', '黄金线数据', '60破均数据', '我的自选'];

// 日期变化处理函数
const handleDateChange = (date: Date | string) => {
  if (!date) {
    console.error('No date selected');
    return;
  }
  if (typeof date === 'string') {
    date = new Date(date);
  }
  selectedDate.value = date;
  const formattedDate = formatDate(selectedDate.value);

  // 分别处理每个接口的请求和加载状态
  loadingStatus.value[0] = true;
  getDragon_queryDate(formattedDate)
    .then((response) => {
      dragonData.value = response.data.data || [];
    })
    .catch((error) => {
      console.error('Error fetching dragon data:', error);
    })
    .finally(() => {
      loadingStatus.value[0] = false;
    });

  loadingStatus.value[1] = true;
  getAnnualMovingAverage(formattedDate)
    .then((response) => {
      annualData.value = response.data.data || [];
    })
    .catch((error) => {
      console.error('Error fetching annual data:', error);
    })
    .finally(() => {
      loadingStatus.value[1] = false;
    });

  loadingStatus.value[2] = true;
  getSixtyMovingAverage(formattedDate)
    .then((response) => {
      sixtyData.value = response.data.data || [];
    })
    .catch((error) => {
      console.error('Error fetching sixty data:', error);
    })
    .finally(() => {
      loadingStatus.value[2] = false;
    });

  loadingStatus.value[3] = true;
  getFollowedList()
    .then((response) => {
      followedData.value = response.data.data || [];
    })
    .catch((error) => {
      console.error('Error fetching followed list data:', error);
    })
    .finally(() => {
      loadingStatus.value[3] = false;
    });
};

const handleDragonLastRecordDateChange = async (date: Date | string) => {
  if (date) {
    if (typeof date === 'string') {
      date = new Date(date);
    }
    const response = await updateDragonTime(formatDate(date));
    if (response.code === 200) {
      MessagePlugin.info({ content: response.msg, duration: 1000 });
    }
    dragonLastRecordDate.value = date;
  }
};

const handleAverageLastRecordDateChange = async (date: Date | string) => {
  if (date) {
    if (typeof date === 'string') {
      date = new Date(date);
    }
    const response = await updateAverageTime(formatDate(date));
    if (response.code === 200) {
      MessagePlugin.info({ content: response.msg, duration: 1000});
    }
    averageLastRecordDate.value = date;
  }
};

const handleGoleLastRecordDateChange = async (date: Date | string) => {
  if (date) {
    if (typeof date === 'string') {
      date = new Date(date);
    }
    const response = await updateGoldTime(formatDate(date));
    if (response.code === 200) {
      MessagePlugin.info({ content: response.msg, duration: 1000});
    }
    goleLastRecordDate.value = date;
  }
};

// 日期格式化函数
function formatDate(date: Date): string {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
}

// 备用的复制到剪贴板方法
const useFallbackCopyTextToClipboard = (text: string): boolean => {
  const textArea = document.getElementById(
    'hiddenTextArea'
  ) as HTMLTextAreaElement;
  textArea.value = text;
  textArea.focus();
  textArea.select();
  try {
    const successful = document.execCommand('copy');
    return successful;
  } catch (err) {
    console.error('Fallback copy failed', err);
    return false;
  }
};

// 复制数据函数
const copyData = (index: number) => {
  const data = allData.value[index];
  if (!data) {
    MessagePlugin.error({ content: '复制失败：暂无数据', duration: 2000 });
    return;
  }
  const textToCopy = data.map((item) => item.stock_ticker).join('\n');
  if (navigator.clipboard && navigator.clipboard.writeText) {
    navigator.clipboard
      .writeText(textToCopy)
      .then(() => {
        MessagePlugin.info({ content: '复制成功', duration: 2000 });
      })
      .catch((error) => {
        console.error('复制错误:', error);
        const success = useFallbackCopyTextToClipboard(textToCopy);
        if (success) {
          MessagePlugin.info({ content: '复制成功', duration: 2000 });
        } else {
          MessagePlugin.error({ content: '复制失败', duration: 2000 });
        }
      });
  } else {
    const success = useFallbackCopyTextToClipboard(textToCopy);
    if (success) {
      MessagePlugin.info({ content: '复制成功', duration: 2000 });
    } else {
      MessagePlugin.error({
        content: '复制失败：浏览器不支持剪贴板功能',
        duration: 2000,
      });
    }
  }
};

// 清除按钮点击处理函数
const clearData = async () => {
  const response = await ResetAllFollows();
  if (response.code === 200) {
    MessagePlugin.info({ content: '清理成功', duration: 2000 });
    handleDateChange(selectedDate.value);
  }
};

// 请求上次记录时间点并赋值
const fetchLastRecordDates = async () => {
  try {
    const response = await getRecordDay();
    dragonLastRecordDate.value = new Date(response.data.dragon_time);
    averageLastRecordDate.value = new Date(response.data.average_time);
    goleLastRecordDate.value = new Date(response.data.gold_time);
  } catch (error) {
    console.error('Error fetching last record dates:', error);
  }
};

// 当组件加载时调用 handleDateChange 和 fetchLastRecordDates
onMounted(async () => {
  if (selectedDate.value) {
    handleDateChange(selectedDate.value);
  }
  await fetchLastRecordDates();
});
</script>

<style scoped>
.container {
  padding: 20px;
  max-width: 1600px;
  margin: 0 auto;
}

.date-picker-container {
  margin-bottom: 20px;
  display: flex;
  gap: 10px;
  align-items: center;
}

.date-picker-label {
  font-size: 14px;
  font-weight: 600;
  color: #333;
}

.custom-date-picker {
  width: 200px;
}

.card-container {
  display: flex;
  gap: 20px;
  margin-top: 20px;
  flex-wrap: wrap;
}

.custom-card {
  width: 350px; /* 固定宽度 */
  border-radius: 12px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  transition: transform 0.2s, box-shadow 0.2s;
  position: relative;
}

.custom-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
}

.card-title {
  font-size: 18px;
  font-weight: 600;
  color: #333;
}

.custom-loading {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 45vh;
}

.log-container {
  width: 100%;
  height: 60vh;
  min-height: 300px;
  font-family: 'Courier New', Courier, monospace;
  font-size: 14px;
  line-height: 1.5;
  color: #333;
  background-color: #f9f9f9;
  border: 1px solid #d9d9d9;
  border-radius: 8px;
  padding: 12px;
  overflow-y: auto;
}

.log-content {
  white-space: pre-wrap; /* 保留换行符 */
}

.log-container::-webkit-scrollbar {
  width: 8px;
}

.log-container::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

.log-container::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 4px;
}

.log-container::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

.copy-button {
  position: absolute;
  top: 10px;
  right: 10px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  padding: 5px 10px;
  font-size: 14px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.copy-button:hover {
  background-color: #0056b3;
}

.clear-button {
  position: absolute;
  top: 10px;
  right: 70px;
  background-color: #dc3545;
  color: white;
  border: none;
  border-radius: 4px;
  padding: 5px 10px;
  font-size: 14px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.clear-button:hover {
  background-color: #c82333;
}

/* 隐藏 textarea */
.hidden-textarea {
  position: fixed;
  top: 0;
  left: 0;
  width: 1px;
  height: 1px;
  opacity: 0;
}
</style>
