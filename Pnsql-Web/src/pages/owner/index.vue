<template>
  <t-card class="sit-card-container" :bordered="false">
    <div class="input-container">
      <t-button @click="onAddUser">新增用户</t-button>
      <t-input v-model="searchQuery" placeholder="查询用户" clearable style="max-width: 200px">
        <template #suffixIcon>
          <search-icon :style="{ cursor: 'pointer' }" />
        </template>
      </t-input>
    </div>
    <t-space direction="vertical" class="centered-content">
      <t-table
        row-key="id"
        :data="filteredData"
        :columns="columns"
        :stripe="stripe"
        :bordered="bordered"
        :hover="hover"
        :table-layout="tableLayout ? 'auto' : 'fixed'"
        :size="size"
        :pagination="pagination"
        :show-header="showHeader"
        :loading="loading"
        cell-empty-content="-"
        :resizable="true"
        lazy-load
        class="centered-table"
      >
        <br /><br />
      </t-table>
    </t-space>
    <owner-diglog ref="ownerDigLog" :on-refresh="initializeData"></owner-diglog>
    <reset-diglog ref="resetDigLog"></reset-diglog>
  </t-card>
</template>

<script lang="tsx" setup>
import { SearchIcon } from 'tdesign-icons-vue-next';
import { TableProps, MessagePlugin, Select } from 'tdesign-vue-next';
import { onMounted, ref, watch, markRaw } from 'vue';
import { getSysUserList, SysUptUser, SysDelUser, SysUptRoles } from '@/api/services/sysUser';
import OwnerDiglog from './OwnerDiglog.vue';
import ResetDiglog from './ResetDiglog.vue';

interface User {
  id: number;
  account: string;
  email: string;
  phone: string;
  roles: string[];
  enable: boolean;
}

const loading = ref(true);
const ownerDigLog = ref();
const resetDigLog = ref();
const originalData = ref<TableProps['data']>([]);
const filteredData = ref<TableProps['data']>([]);
const searchQuery = ref('');
const stripe = ref(true);
const bordered = ref(true);
const hover = ref(false);
const tableLayout = ref(false);
const size = ref<TableProps['size']>('medium');
const showHeader = ref(true);

const ROLE_OPTIONS = [
  { label: 'dba', value: 'dba' },
  { label: 'admin', value: 'admin' },
  { label: 'owner', value: 'owner' },
];

const columns = ref<TableProps['columns']>([
  { colKey: 'account', title: '用户', width: '200', align: 'center' },
  { colKey: 'email', title: '邮箱地址', width: '200', align: 'center', ellipsis: true },
  { colKey: 'phone', title: '电话号码', width: '200', align: 'center' },
  {
    colKey: 'roles',
    title: '用户权限',
    align: 'center',
    cell: (h, { row }) => row.roles.join('、'),
    edit: {
      keepEditMode: true,
      component: markRaw(Select),
      props: () => ({
        multiple: true,
        minCollapsedNum: 3,
        options: ROLE_OPTIONS,
      }),
      onEdited: async (context) => {
        const newData = [...filteredData.value];
        newData.splice(context.rowIndex, 1, context.newRowData);
        filteredData.value = newData;
        const response = await SysUptRoles(context.newRowData.id, context.newRowData.roles);
        if (response.code === 200) {
          MessagePlugin.success(`${context.newRowData.account} 权限更新成功`);
        }
      },
    },
  },
  {
    colKey: 'enable',
    title: '是否启用',
    align: 'center',
    width: '180',
    cell: (h, {row}) => (
      <div style={{display: 'flex', alignItems: 'center', justifyContent: 'center'}}>
        <t-switch v-model={row.enable} onChange={(val) => handleEnableChange(row, val)}/>
        <span style={{marginLeft: '8px'}}>{row.enable ? '启用' : '停用'}</span>
      </div>
    ),
  },
  {
    colKey: 'operation',
    title: '操作',
    align: 'center',
    cell: (h, {row}) => (
      <div style={{display: 'flex', gap: '8px', justifyContent: 'center'}}>
        <t-button theme="primary" size="small" style="padding: 4px 8px;" onClick={() => handleDetailClick(row)}>
          重置
        </t-button>
        <t-popconfirm
          theme="danger"
          content="确认删除该用户吗?"
          onConfirm={() => handleDelete(row)}
        >
          <t-button theme="danger" size="small" style="padding: 4px 8px;">
            删除
          </t-button>
        </t-popconfirm>
      </div>
    ),
    width: 200,
  },
]);

const pagination: TableProps['pagination'] = {
  defaultCurrent: 1,
  defaultPageSize: 5,
  total: 0,
};

// Function to initialize data
const initializeData = async () => {
  loading.value = true;
  try {
    const response = await getSysUserList();
    const users = response.data.users || [];
    originalData.value = users.map((user) => ({
      ...user,
      enable: user.enable === 1,
      roles: user.roles || [],
    }));
    filteredData.value = originalData.value;
    pagination.total = users.length;
  } catch (error) {
    console.error('Error fetching user data:', error);
  } finally {
    loading.value = false;
  }
};

// Call the initializeData function on component mounted
onMounted(() => {
  initializeData();
});

const onAddUser = () => {
  ownerDigLog.value.onOwnerClick();
};

watch(searchQuery, (newValue) => {
  if (newValue) {
    filteredData.value = originalData.value.filter((user) =>
      user.account.toLowerCase().includes(newValue.toLowerCase())
    );
  } else {
    filteredData.value = originalData.value;
  }
});

async function handleEnableChange(row: User, value: boolean) {
  try {
    const enableValue = value ? 1 : 0;
    const response = await SysUptUser(row.id, enableValue);
    if (response.code === 200) {
      const targetOriginal = originalData.value.find((user) => user.id === row.id);
      if (targetOriginal) targetOriginal.enable = value;
      const targetFiltered = filteredData.value.find((user) => user.id === row.id);
      if (targetFiltered) targetFiltered.enable = value;

      const message = value ? '已启用' : '已停用';
      await MessagePlugin.info({
        content: message,
        duration: 2000,
      });
    }
  } catch (error) {
    console.error('Error updating user enable status:', error);
  }
}

function handleDetailClick(row: any) {
  resetDigLog.value.onResetClick(row.id);
}

// 新的删除方法，通过气泡确认框
async function handleDelete(row: User) {
  try {
    const response = await SysDelUser(row.id);
    if (response.code === 200) {
      MessagePlugin.success('删除成功');
      initializeData(); // 重新加载数据
    }
  } catch (error) {
    MessagePlugin.error('删除失败');
    console.error('Error deleting user:', error);
  }
}
</script>

<style lang="less" scoped>
.sit-card-container {
  padding: var(--td-comp-paddingTB-xxl) var(--td-comp-paddingLR-xxl);

  :deep(.t-card__body) {
    padding: 0;
  }
}

.centered-content {
  display: flex;
  justify-content: center;
  align-items: center;
  flex-direction: column;
}

.centered-table {
  width: 100%;

  .t-table__cell {
    display: flex;
    justify-content: center;
    align-items: center;
  }
}

.input-container {
  display: flex;
  justify-content: space-between; /* 使元素两端对齐 */
  align-items: center;
  padding-bottom: 20px;
  width: 100%;
}

.input-container t-input {
  margin-left: auto;
}
</style>
