<template>
  <t-card class="sit-card-container" :bordered="false">
    <div class="input-container">
      <!-- 左侧按钮组 -->
      <div class="button-group">
        <t-radio-group v-model="size" variant="default-filled">
          <t-radio-button value="small">我的工单</t-radio-button>
          <t-radio-button value="medium">我的审批</t-radio-button>
          <t-radio-button value="large">所有工单</t-radio-button>
        </t-radio-group>
      </div>

      <!-- 右侧搜索输入框 -->
      <t-input placeholder="查询" clearable style="max-width: 200px">
        <template #suffixIcon>
          <search-icon :style="{ cursor: 'pointer' }" />
        </template>
      </t-input>
    </div>

    <t-space direction="vertical">
      <t-table
        row-key="index"
        :data="data"
        :columns="columns"
        :stripe="stripe"
        :bordered="bordered"
        :hover="hover"
        :table-layout="tableLayout ? 'auto' : 'fixed'"
        :size="size"
        :pagination="pagination"
        :show-header="showHeader"
        cell-empty-content="-"
        resizable
        lazy-load
      >
      </t-table>
    </t-space>
  </t-card>
</template>

<script lang="tsx" setup>
import {
  CheckCircleFilledIcon,
  CloseCircleFilledIcon,
  ErrorCircleFilledIcon,
  SearchIcon,
} from 'tdesign-icons-vue-next';
import { TableProps } from 'tdesign-vue-next';
import { ref } from 'vue';

const statusNameListMap = {
  0: { label: '审批通过', theme: 'success', icon: <CheckCircleFilledIcon /> },
  1: { label: '审批失败', theme: 'danger', icon: <CloseCircleFilledIcon /> },
  2: { label: '审批过期', theme: 'warning', icon: <ErrorCircleFilledIcon /> },
};

const data: TableProps['data'] = [];
const total = 28;
for (let i = 0; i < total; i++) {
  data.push({
    index: i + 1,
    applicant: ['贾明', '张三', '王芳'][i % 3],
    status: i % 3,
    channel: ['电子签署', '纸质签署', '纸质签署'][i % 3],
    detail: { email: ['w.cezkdudy@lhll.au', 'r.nmgw@peurezgn.sl', 'p.cumx@rampblpa.ru'][i % 3] },
    matters: ['宣传物料制作费用', 'algolia 服务报销', '相关周边制作费', '激励奖品快递费'][i % 4],
    time: [2, 3, 1, 4][i % 4],
    createTime: ['2022-01-01', '2022-02-01', '2022-03-01', '2022-04-01', '2022-05-01'][i % 4],
  });
}

const stripe = ref(true);
const bordered = ref(true);
const hover = ref(false);
const tableLayout = ref(false);
const size = ref<TableProps['size']>('medium');
const showHeader = ref(true);

const columns = ref<TableProps['columns']>([
  { colKey: 'applicant', title: '申请人', width: '100', align: 'center' },
  {
    colKey: 'status',
    title: '申请状态',
    align: 'center',
    cell: (h, { row }) => (
      <t-tag shape="round" theme={statusNameListMap[row.status].theme} variant="light-outline">
        {statusNameListMap[row.status].icon}
        {statusNameListMap[row.status].label}
      </t-tag>
    ) },
  { colKey: 'channel', title: '签署方式', align: 'center' },
  { colKey: 'detail.email', title: '邮箱地址', ellipsis: true, align: 'center' },
  { colKey: 'createTime', title: '申请时间', align: 'center' },
]);

const pagination: TableProps['pagination'] = {
  defaultCurrent: 1,
  defaultPageSize: 5,
  total,
};
</script>

<style lang="less" scoped>
.sit-card-container {
  padding: var(--td-comp-paddingTB-xxl) var(--td-comp-paddingLR-xxl);
  :deep(.t-card__body) {
    padding: 0;
  }
}

.input-container {
  display: flex;
  justify-content: space-between; /* 空间在按钮组和输入框之间分配 */
  align-items: center; /* 垂直居中对齐 */
  padding-bottom: 20px;
}

.button-group {
  flex-grow: 1; /* 让按钮组填充左侧空间 */
}
</style>
