<template>
  <t-drawer v-model:visible="visible" size="60%" header="header" :on-confirm="onClickConfirm" :close-btn="true">
    <p>This is a controlled drawer with ID: {{ drawerId }}</p>
  </t-drawer>
</template>

<script setup>
import { ref } from 'vue';
import { MessagePlugin } from 'tdesign-vue-next';

// 控制抽屉显示的状态
const visible = ref(false);

// 存储传入的ID
const drawerId = ref(null);

const handleClick = (id) => {
  visible.value = true;
};

const onClickConfirm = () => {
  MessagePlugin.info('数据保存中...', 1000);
  const timer = setTimeout(() => {
    clearTimeout(timer);
    visible.value = false;
    MessagePlugin.info('数据保存成功!');
  }, 1000);
};

defineExpose({
  handleClick,
});
</script>
