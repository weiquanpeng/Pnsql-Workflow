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
    >
      <t-space direction="vertical" style="width: 100%">
        <div>
          <p>是否确认生成爬虫工单，这将通过流程量化抓取所有A股数据...</p>
        </div>
      </t-space>
    </t-dialog>
  </t-space>
</template>
<script setup>
import { ref } from 'vue';
import { useUserStore } from '@/store';
import { addTaskConfigData } from '@/api/services/taskConfig';
import { NotifyPlugin } from 'tdesign-vue-next';

const user = useUserStore();
const visible = ref(false);

const loading = ref(false);
const onClick = () => {
  visible.value = true;
};
const task = {
  title: '爬虫任务',
  owner: user.userInfo.name,
  approver: 'admin',
  status: 'todo',
  task_describe: '爬虫抓取股票任务',
  type: 'fabric_stock_dag',
};

const onConfirmAnother = async () => {
  loading.value = true;
  try {
    const response = await addTaskConfigData(task);
    if (response.code === 200) {
      NotifyPlugin.info({ title: '操作成功',content:"爬虫工单地址: " });
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
