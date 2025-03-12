<template>
  <div>
    <t-drawer
      v-model:visible="visible"
      size="60%"
      header="工单状态"
      :footer="false"
    >
      <t-steps readonly>
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

      <!-- 自定义按钮部分 -->
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

<script setup>
import { ref, computed } from 'vue';
import { MessagePlugin } from 'tdesign-vue-next';
import { getSubTaskConfigData, UptSubTaskData } from '@/api/services/taskConfig';
import { CheckCircleIcon, PlayIcon, ErrorCircleIcon, TimeFilledIcon, CloseOctagonIcon } from 'tdesign-icons-vue-next';

// 节流函数
const throttle = (func, limit) => {
  let inThrottle;
  return function() {
    const args = arguments;
    const context = this;
    if (!inThrottle) {
      func.apply(context, args);
      inThrottle = true;
      setTimeout(() => inThrottle = false, limit);
    }
  };
};

const visible = ref(false);
const steps = ref([]);
const currentId = ref(null);
const isLoading = ref(false);
const isLoading2 = ref(false);
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
  const response = await getSubTaskConfigData(id);

  if (response.code === 200) {
    steps.value = response.data.data.map((task) => {
      let status = '';

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
      };
    });
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
</style>
