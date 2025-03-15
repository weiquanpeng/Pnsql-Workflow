<template>
  <div>
    <t-drawer
      v-model:visible="visible"
      size="60%"
      header="工单状态"
      :footer="false"
    >
      <!-- 步骤条 -->
      <t-skeleton :loading="isDataLoading" :rowCol="[1, 1, 1]">
        <div v-if="!isDataLoading" class="steps-container">
          <t-steps readonly class="steps-wrapper">
            <t-step-item
              v-for="(step, index) in steps"
              :key="index"
              :title="step.state === 'close' ? '工单已关闭' : step.title"
              :content="step.owner"
              :status="step.status"
            >
              <template #icon>
                <TimeFilledIcon v-if="step.state === 'tosplit'" size="small" class="icon-margin" />
                <PlayIcon v-else-if="step.state === 'todo'" size="small" class="icon-margin" />
                <t-loading v-else-if="step.state === 'doing'" size="small" />
                <CheckCircleIcon v-else-if="step.state === 'done'" size="small" class="icon-margin" />
                <ErrorCircleIcon v-else-if="step.state === 'error'" size="small" class="icon-margin" />
                <CloseOctagonIcon v-else-if="step.state === 'close'" size="small" class="icon-margin" />
              </template>
            </t-step-item>
          </t-steps>
        </div>
      </t-skeleton>

      <!-- 描述部分 -->
      <t-space direction="vertical" class="description-container">
        <t-row>
          <t-radio-group v-model="tableLayout"></t-radio-group>
        </t-row>
        <!-- 修正 size 属性 -->
        <t-descriptions bordered size="mini" :table-layout="tableLayout" style="text-align: center">
          <t-descriptions-item label="工单号" :span="1">
            <t-skeleton :loading="isDataLoading" :rowCol="[1]">
              {{ currentId }}
            </t-skeleton>
          </t-descriptions-item>
          <t-descriptions-item label="创建时间" :span="1">
            <t-skeleton :loading="isDataLoading" :rowCol="[1]">
              {{ currentStep.create_time }}
            </t-skeleton>
          </t-descriptions-item>
          <t-descriptions-item label="提交人" :span="1">
            <t-skeleton :loading="isDataLoading" :rowCol="[1]">
              {{ currentStep.owner }}
            </t-skeleton>
          </t-descriptions-item>
          <t-descriptions-item label="更新时间" :span="1">
            <t-skeleton :loading="isDataLoading" :rowCol="[1]">
              {{ currentStep.update_time }}
            </t-skeleton>
          </t-descriptions-item>
          <t-descriptions-item label="工单描述" :span="2">
            <t-skeleton :loading="isDataLoading" :rowCol="[1]">
              {{ currentStep.content }}
            </t-skeleton>
          </t-descriptions-item>
        </t-descriptions>
      </t-space>

      <!-- 日志显示部分 -->
      <div class="card-container">
        <t-card class="custom-card">
          <template #header>
            <div class="card-title">日志信息</div>
          </template>
          <t-loading
            v-if="isLogLoading"
            text="加载日志数据..."
            size="small"
            class="custom-loading"
          />
          <div v-else class="log-container" style="padding-top: 0;">
            <pre class="log-content">{{ logData }}</pre>
          </div>
        </t-card>
      </div>

      <!-- 底部按钮 -->
      <div class="footer-buttons">
        <t-button
          size="medium"
          theme="primary"
          @click="throttledHandleAction"
          :loading="isLoading"
        >
          {{ actionButtonLabel }}
        </t-button>
        <t-button
          size="medium"
          theme="danger"
          @click="throttledCloseDrawer"
          :loading="isLoading2"
        >
          关闭
        </t-button>
      </div>
    </t-drawer>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { MessagePlugin } from 'tdesign-vue-next';
import { getSubTaskConfigData, UptSubTaskData } from '@/api/services/taskConfig';
import { getJobLogData } from '@/api/services/jobLogData';
import { CheckCircleIcon, PlayIcon, ErrorCircleIcon, TimeFilledIcon, CloseOctagonIcon } from 'tdesign-icons-vue-next';

// 节流函数
const throttle = (func, limit) => {
  let inThrottle;
  return function () {
    const args = arguments;
    const context = this;
    if (!inThrottle) {
      func.apply(context, args);
      inThrottle = true;
      setTimeout(() => inThrottle = false, limit);
    }
  };
};

const tableLayout = ref('fixed');
const visible = ref(false);
const steps = ref([]);
const currentId = ref(null);
const currentStep = ref({});
const isLoading = ref(false);
const isLoading2 = ref(false);
const isDataLoading = ref(true);
const isLogLoading = ref(true);
const logData = ref(''); // 存储日志数据（字符串）
const emit = defineEmits(['refreshParent']);

// 计算按钮标签
const actionButtonLabel = computed(() => {
  const hasErrorOrClosed = steps.value.some(step => step.state === 'error' || step.state === 'close');
  return hasErrorOrClosed ? '重试' : '通过';
});

// 处理按钮点击逻辑
const handleAction = async () => {
  const hasErrorOrClosed = steps.value.some(step => step.state === 'error' || step.state === 'close');
  const firstTodoStep = steps.value.find(step => step.state === 'todo' || step.state === 'error' || step.state === 'close');

  if (!firstTodoStep) {
    MessagePlugin.error({ content: '不可操作', duration: 1000 });
    return;
  }

  isLoading.value = true;
  try {
    const response = await UptSubTaskData(firstTodoStep.id, hasErrorOrClosed ? 'todo' : 'done');
    if (response.code === 200) {
      MessagePlugin.info({ content: hasErrorOrClosed ? '已重试' : '审批通过', duration: 1000 });
      visible.value = false;
    }
  } catch (error) {
    MessagePlugin.error({ content: '操作失败', duration: 1000 });
  } finally {
    isLoading.value = false;
    emit('refreshParent');
  }
};

const closeDrawer = async () => {
  const firstTodoStep = steps.value.find(step => step.state === 'todo' || step.state === 'error');
  if (!firstTodoStep) {
    MessagePlugin.error({ content: '不可操作', duration: 1000 });
    return;
  }

  isLoading2.value = true;
  try {
    const response = await UptSubTaskData(firstTodoStep.id, 'close');
    if (response.code === 200) {
      MessagePlugin.info({ content: '关闭工单', duration: 1000 });
      visible.value = false;
    }
  } catch (error) {
    MessagePlugin.error({ content: '操作失败', duration: 1000 });
  } finally {
    isLoading2.value = false;
    emit('refreshParent');
  }
};

// 节流处理后的点击函数
const throttledHandleAction = throttle(handleAction, 2000);
const throttledCloseDrawer = throttle(closeDrawer, 2000);

const handleClick = async (id) => {
  currentId.value = id;
  visible.value = true;

  isDataLoading.value = true;
  isLogLoading.value = true;

  try {
    const logResponse = await getJobLogData(currentId.value);

    // 确保 logResponse.data 是字符串
    logData.value = typeof logResponse.data === 'string' ? logResponse.data : JSON.stringify(logResponse.data);

    const configResponse = await getSubTaskConfigData(id);
    if (configResponse.code === 200) {
      steps.value = configResponse.data.data.map((task) => {
        let status;
        switch (task.status) {
          case 'done':
            status = 'finish';
            break;
          case 'todo':
            status = 'process';
            break;
          case 'close':
            status = 'error';
            break;
          case 'doing':
            status = 'process';
            break;
          case 'error':
            status = 'error';
            break;
          default:
            status = 'default';
            break;
        }
        return {
          id: task.id,
          title: task.title,
          owner: task.approver,
          content: task.task_describe,
          status: status,
          state: task.status,
          create_time: task.create_time,
          update_time: task.update_time,
        };
      });

      if (steps.value.length > 0) {
        currentStep.value = steps.value[0];
      }
    }
  } catch (error) {
    MessagePlugin.error('数据加载失败');
  } finally {
    isDataLoading.value = false;
    isLogLoading.value = false;
  }
};

defineExpose({
  handleClick,
});
</script>

<style scoped>
.footer-buttons {
  position: absolute;
  bottom: 16px;
  left: 16px;
  display: flex;
  gap: 8px;
}

.description-container {
  margin-top: 16px;
}

.icon-margin {
  margin-right: 8px;
}

.card-container {
  display: flex;
  gap: 20px;
  margin-top: 20px;
  flex-wrap: wrap;
}

.custom-card {
  width: 100%;
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
  height: 200px;
}

.log-container {
  width: 100%;
  height: 50vh;
  min-height: 150px;
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

/* 步骤条容器样式 */
.steps-container {
  width: 100%;
  overflow-x: auto; /* 允许水平滚动 */
  padding-bottom: 16px; /* 避免滚动条遮挡内容 */
}

.steps-wrapper {
  display: inline-flex; /* 使步骤条水平排列 */
  min-width: max-content; /* 确保步骤条宽度足够 */
  white-space: nowrap; /* 防止步骤换行 */
}

/* 为步骤项添加最小宽度 */
.steps-wrapper .t-step-item {
  min-width: 150px;
}
</style>
