<template>
  <div>
    <t-drawer
      v-model:visible="visible"
      size="48%"
      header="工单状态"
      :on-confirm="onClickConfirm"
      :close-btn="true"
    >
      <t-steps readonly>
        <t-step-item
          v-for="(step, index) in steps"
          :key="index"
          :title="getChineseTitle(step.title)"
          :content="step.content"
          :status="step.status"
        >
          <template #icon>
            <t-loading v-if="step.state === 'running' && !step.title.includes('Approval')" size="small" />
            <PlayIcon v-else-if="step.state !== 'failed' && step.state !== 'success' && step.title.includes('Approval')" size="small" class="icon-margin" />
            <CheckCircleIcon v-else-if="step.state === 'success'" size="small" class="icon-margin" />
            <CloseCircleIcon v-else-if="step.state === 'failed'" size="small" class="icon-margin" />
            <TimeFilledIcon v-else size="small" class="icon-margin" />
          </template>
        </t-step-item>
      </t-steps>
    </t-drawer>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { MessagePlugin } from 'tdesign-vue-next';
import { getSubTaskConfigData } from '@/api/services/taskConfig';
import { taskOrder, titleMappings } from './taskOrder';
import { CheckCircleIcon, PlayIcon, CloseCircleIcon, TimeFilledIcon } from 'tdesign-icons-vue-next';

const visible = ref(false);
const steps = ref([]);

const getChineseTitle = (title) => {
  return titleMappings[title] || title;
};

const onClickConfirm = () => {
  MessagePlugin.info('数据保存中...', 1000);
  const timer = setTimeout(() => {
    clearTimeout(timer);
    visible.value = false;
    MessagePlugin.info('数据保存成功!');
  }, 1000);
};

const handleClick = async (id, type) => {
  visible.value = true;
  const response = await getSubTaskConfigData(id, type);

  if (response.code === 200) {
    console.log(response.data.task_instances);

    const sortedInstances = response.data.task_instances.sort((a, b) => {
      const indexA = taskOrder.indexOf(a.task_id);
      const indexB = taskOrder.indexOf(b.task_id);
      if (indexA === -1 && indexB === -1) return 0;
      if (indexA === -1) return 1;
      if (indexB === -1) return -1;
      return indexA - indexB;
    });

    steps.value = sortedInstances.map((instance) => {
      const title = instance.task_id;
      let content = '';
      let status = '';

      if (!instance.state || instance.state === 'upstream_failed') {
        content = '待执行';
        status = 'default';
      } else if (title === 'ownerApproval') {
        content = `审批人: ${response.data.approver}`;
      } else if (title === 'submitWork') {
        content = `提交人: ${response.data.owner}`;
      } else {
        content = instance.state;
      }

      if (title.includes('Approval') && instance.state !== 'failed') {
        status = 'process';
      } else {
        switch (instance.state) {
          case 'success':
            status = 'finish';
            break;
          case 'failed':
            status = 'error';
            break;
          case 'running':
            status = 'process';
            break;
          default:
            status = 'default';
            break;
        }
      }

      return {
        title: title,
        content: content,
        status: status,
        state: instance.state,
      };
    });
  }
};

defineExpose({
  handleClick,
});
</script>
