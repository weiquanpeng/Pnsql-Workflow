<template>
  <div>
    <t-drawer v-model:visible="visible" size="48%" header="工单状态" :on-confirm="onClickConfirm" :close-btn="true">
      <t-steps readonly>
        <t-step-item
          v-for="(step, index) in steps"
          :key="index"
          :title="step.title"
          :content="step.content"
          :status="step.status"
        >
          <template #icon>
            <!-- 动态显示自定义图标 -->
            <t-loading size="small" v-if="step.status === 'process'" />
          </template>
        </t-step-item>
      </t-steps>
    </t-drawer>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { MessagePlugin } from 'tdesign-vue-next';

// 在组合式API中，ref和相关逻辑直接使用
const visible = ref(false);

const steps = ref([
  {
    title: "已完成的步骤",
    content: "这里是提示文字",
    status: "finish",
  },
  {
    title: "已完成的步骤",
    content: "这里是提示文字",
    status: "finish",
  },
  {
    title: "执行中的步骤",
    content: "admin",
    status: "process",
  },
  {
    title: "错误的步骤",
    content: "这里是提示文字",
    status: "error",
  },
]);

const onClickConfirm = () => {
  MessagePlugin.info('数据保存中...', 1000);
  const timer = setTimeout(() => {
    clearTimeout(timer);
    visible.value = false;
    MessagePlugin.info('数据保存成功!');
  }, 1000);
};
const handleClick = (id) => {
  visible.value = true;
};

// defineExpose 用于暴露给父组件调用的函数
defineExpose({
  handleClick,
});
</script>
