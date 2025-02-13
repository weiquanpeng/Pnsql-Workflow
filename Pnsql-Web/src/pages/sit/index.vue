<template>
  <t-card class="steps-card-container" :bordered="false">
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
  </t-card>
</template>

<script>
import { ref } from 'vue';

export default {
  setup() {
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

    return {
      steps,
    };
  },
};
</script>

<style scoped>
.steps-card-container {
  padding: var(--td-comp-paddingTB-xxl) var(--td-comp-paddingLR-xxl);
}

:deep(.t-card__body) {
  padding: 0;
}
</style>
