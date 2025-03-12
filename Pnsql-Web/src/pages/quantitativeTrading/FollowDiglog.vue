<template>
  <t-space>
    <t-dialog
      v-model:visible="visible"
      header="爬虫确认"
      width="40%"
      :confirm-on-enter="loading"
      :on-cancel="onCancel"
      :on-esc-keydown="onEscKeydown"
      :on-close-btn-click="onCloseBtnClick"
      :on-overlay-click="onOverlayClick"
      :on-close="close"
      :on-confirm="onConfirmAnother"
      :confirm-loading="loading"
      style="--td-comp-paddingTB-xxl: 40px; --td-comp-paddingLR-xxl: 40px"
    >
      <t-space direction="vertical" style="width: 100%">
        <div>
          <p>确认是否增量爬取，这将通过增量获取并计算今天的股票数据</p>
        </div>
      </t-space>
    </t-dialog>
  </t-space>
</template>
<script setup>
import { NotifyPlugin } from 'tdesign-vue-next';
import { ref } from 'vue';

import { addTaskConfigData } from '@/api/services/taskConfig';
import { useUserStore } from '@/store';

const user = useUserStore();
const visible = ref(false);

const loading = ref(false);
const onClick = () => {
  visible.value = true;
};

const getCurrentDate = () => {
  const today = new Date();
  const year = today.getFullYear().toString();
  const month = (today.getMonth() + 1).toString().padStart(2, '0');
  const day = today.getDate().toString().padStart(2, '0');
  return `${year}${month}${day}`;
};

const task = {
  title: '增量任务',
  owner: user.userInfo.name,
  approver: 'admin',
  status: 'tosplit',
  task_describe: '增量爬虫任务',
  type: ' FollowStockDag',
  paras: {
    day: getCurrentDate(),
  },
};

const onConfirmAnother = async () => {
  loading.value = true;
  try {
    const response = await addTaskConfigData(task);
    if (response.code === 200) {
      NotifyPlugin.info({ title: '操作成功', content: '爬虫工单: ' });
    }
  } catch (error) {
    console.error('Error addTaskConfigData data:', error);
  } finally {
    loading.value = false;
  }
  visible.value = false;
};
const close = (context) => {
  console.log('关闭弹窗，点击关闭按钮、按下ESC、点击蒙层等触发', context);
};
const onCancel = (context) => {
  console.log('点击了取消按钮', context);
};
const onEscKeydown = (context) => {
  console.log('按下了ESC', context);
};
const onCloseBtnClick = (context) => {
  console.log('点击了关闭按钮', context);
};
const onOverlayClick = (context) => {
  console.log('点击了蒙层', context);
};
defineExpose({
  onClick,
});
</script>

<style scoped>
.trading-card-container {
  --td-comp-paddingTB-xxl: 40px;
  --td-comp-paddingLR-xxl: 0px;
  padding: var(--td-comp-paddingTB-xxl) var(--td-comp-paddingLR-xxl);
}
</style>
