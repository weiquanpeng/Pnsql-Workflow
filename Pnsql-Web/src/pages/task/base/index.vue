<template>
  <t-card class="sit-card-container" :bordered="false">
    <div class="input-container">
      <div class="button-group">
        <t-radio-group v-model="selectedOption" variant="default-filled">
          <t-radio-button value="small" @click="handleFetchMineTaskData">我的工单</t-radio-button>
          <t-radio-button value="medium" @click="handleFetchApproveTaskData">我的审批</t-radio-button>
          <t-radio-button value="large" @click="handleFetchTaskData">所有工单</t-radio-button>
        </t-radio-group>
      </div>
      <t-input-adornment :prepend="fieldSelect">
        <t-input v-model="searchTerm" placeholder="查询" clearable style="max-width: 200px">
          <template #suffixIcon>
            <search-icon :style="{ cursor: 'pointer' }" @click="handleSearch" />
          </template>
        </t-input>
      </t-input-adornment>
    </div>
    <t-space direction="vertical">
      <t-table
        row-key="id"
        :data="filteredTaskData"
        :columns="columns"
        :stripe="stripe"
        :bordered="bordered"
        :hover="hover"
        :table-layout="tableLayout ? 'auto' : 'fixed'"
        :size="size"
        :loading="loading"
        :pagination="pagination"
        :show-header="showHeader"
        cell-empty-content="-"
        :resizable="true"
        :lazy-load="true"
      />
    </t-space>
    <task-process ref="taskProcessRef"></task-process>
  </t-card>
</template>

<script setup lang="tsx">
import { onMounted, ref, computed } from 'vue';
import { getTaskConfigList, getMineTaskConfigList, getApproveTaskConfigList, getSubTaskConfigData } from '@/api/services/taskConfig';
import { SearchIcon, CheckCircleFilledIcon, LoadingIcon, TimeIcon, EllipsisIcon } from 'tdesign-icons-vue-next';
import { TableProps, InputAdornmentProps } from 'tdesign-vue-next';
import TaskProcess from '@/pages/task/base/TaskProcess.vue';
import { useUserStore } from '@/store';

const taskProcessRef = ref();
const user = useUserStore();
const loading = ref(true);
const taskData = ref<TableProps['data']>([]);
const searchTerm = ref('');
const selectedField = ref('id');
const selectedOption = ref('small');

const statusMapping = {
  todo: { label: '待审批', theme: 'default', icon: <TimeIcon /> },
  doing: { label: '审批中', theme: 'warning', icon: <EllipsisIcon /> },
  running: { label: '执行中', theme: 'primary', icon: <LoadingIcon /> },
  done: { label: '工单完成', theme: 'success', icon: <CheckCircleFilledIcon /> },
};

const columns = ref<TableProps['columns']>([
  {
    colKey: 'id',
    title: 'ID',
    align: 'center',
    width: '100',
    cell: (h, { row }) => (
      <span style="cursor: pointer; color: blue;" onClick={() => handleIdClick(row)}>{row.id}</span>
    ),
  },
  { colKey: 'title', title: '标题', align: 'center', width: '180' },
  { colKey: 'owner', title: '申请人', align: 'center', width: '200' },
  {
    colKey: 'status',
    title: '状态',
    align: 'center',
    width: '160',
    cell: (h, { row }) => {
      const statusInfo = statusMapping[row.status] || { label: '未知状态', theme: 'default', icon: null };
      return (
        <t-tag shape="round" theme={statusInfo.theme} variant="light-outline">
          {statusInfo.icon}
          {statusInfo.label}
        </t-tag>
      );
    }
  },
  { colKey: 'task_describe', title: '工单描述', align: 'center', ellipsis: true },
  { colKey: 'created_at', title: '创建时间', align: 'center', width: '240' },
  { colKey: 'updated_at', title: '更新时间', align: 'center', width: '240' },
  {
    colKey: 'operation',
    title: '操作',
    align: 'center',
    cell: (h, { row }) => (
      <div style={{ display: 'flex', gap: '8px', justifyContent: 'center' }}>
        <t-button theme="primary" size="small" style="padding: 4px 8px;" onClick={() => handleIdClick(row)}>view</t-button>
      </div>
    ),
    width: 100,
  },
]);

const handleIdClick = async (row: any) => {
  try {
    const response = await getSubTaskConfigData(row.id, row.type);
    if (response.code === 200) {
      console.log(response);
    }
    taskProcessRef.value.handleClick(row.id);
  } catch (error) {
    console.error('Error fetching sub task config data:', error);
  }
};

const stripe = ref(true);
const bordered = ref(true);
const hover = ref(false);
const tableLayout = ref(false);
const size = ref<TableProps['size']>('small');
const showHeader = ref(true);
const pagination: TableProps['pagination'] = {
  defaultCurrent: 1,
  defaultPageSize: 20,
  pageSizeOptions: [20, 50, 100, 200],
  total: taskData.value.length,
};

const fieldSelect = ref<InputAdornmentProps['prepend']>(() => (
  <t-select
    autoWidth
    options={[
      {label: 'ID', value: 'id'},
      {label: '标题', value: 'title'},
      {label: '申请人', value: 'owner'}
    ]}
    v-model={selectedField.value}  // 确保 selectedField 正确绑定
    default-value="id"
  />
));

const filteredTaskData = computed(() => {
  if (!searchTerm.value) return taskData.value;
  return taskData.value.filter(item => {
    const fieldValue = item[selectedField.value];
    return fieldValue && fieldValue.toString().toLowerCase().includes(searchTerm.value.toLowerCase());
  });
});

const handleSearch = () => {
  console.log(`Searching for "${searchTerm.value}" in field "${selectedField.value}"`);
};

const fetchData = async (apiFunction: any, params = {}) => {
  taskData.value = [];
  loading.value = true;
  try {
    const response = await apiFunction(params);
    taskData.value = response.data.data || [];
    pagination.total = taskData.value.length;
  } catch (error) {
    console.error('Error fetching task data:', error);
  } finally {
    loading.value = false;
  }
};

const handleFetchTaskData = () => fetchData(getTaskConfigList);
const handleFetchMineTaskData = () => fetchData(getMineTaskConfigList, { owner: user.userInfo.name });
const handleFetchApproveTaskData = () => fetchData(getApproveTaskConfigList, { approver: user.userInfo.name });

onMounted(() => {
  handleFetchMineTaskData();
});
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
  justify-content: space-between;
  align-items: center;
  padding-bottom: 20px;
}

.button-group {
  flex-grow: 1;
}

.id-click {
  cursor: pointer;
  color: blue;
}
</style>
