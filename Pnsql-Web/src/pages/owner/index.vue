<template>
  <t-card class="sit-card-container" :bordered="false">
    <div class="input-container">
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
  </t-card>
</template>

<script lang="tsx" setup>
import { SearchIcon } from 'tdesign-icons-vue-next';
import {TableProps, Message, MessagePlugin} from 'tdesign-vue-next';
import { onMounted, ref, watch } from 'vue';

import { getSysUserByAccount, getSysUserList, SysUptUser } from '@/api/services/sysUser';

interface User {
  id: number;
  account: string;
  email: string;
  phone: string;
  roles: string[];
  enable: boolean;
}

// 加载状态
const loading = ref(true);

// 原始数据
const originalData = ref<TableProps['data']>([]);

// 过滤后的数据
const filteredData = ref<TableProps['data']>([]);

const searchQuery = ref('');

const stripe = ref(true);
const bordered = ref(true);
const hover = ref(false);
const tableLayout = ref(false);
const size = ref<TableProps['size']>('medium');
const showHeader = ref(true);

const columns = ref<TableProps['columns']>([
  { colKey: 'account', title: '用户', width: '100', align: 'center' },
  { colKey: 'email', title: '邮箱地址', align: 'center' },
  { colKey: 'phone', title: '电话号码', align: 'center' },
  { colKey: 'roles', title: '权限', align: 'center' },
  {
    colKey: 'enable',
    title: '是否启用',
    align: 'center',
    cell: (h, { row }) => (
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <t-switch v-model={row.enable} onChange={(val) => handleEnableChange(row, val)} />
        <span style={{ marginLeft: '8px' }}>{row.enable ? '启用' : '停用'}</span>
      </div>
    ),
  },
  {
    colKey: 'operation',
    title: '操作',
    align: 'center',
    cell: (h, { row }) => (
      <div style={{ display: 'flex', gap: '8px', justifyContent: 'center' }}>
        <t-button theme="primary" size="small" style="padding: 4px 8px;" onClick={() => handleDetailClick(row)}>
          重置
        </t-button>
        <t-button theme="default" size="small" style="padding: 4px 8px;" onClick={() => handleApplyAgainClick(row)}>
          删除
        </t-button>
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

// 初始化数据
onMounted(async () => {
  try {
    const response = await getSysUserList();
    const users = response.data.users || [];
    originalData.value = users.map((user) => ({
      ...user,
      enable: user.enable === 1,
    }));
    filteredData.value = originalData.value;
    pagination.total = users.length;
  } catch (error) {
    console.error('Error fetching user data:', error);
  } finally {
    loading.value = false;
  }
});

// 监听搜索框的输入变化
watch(searchQuery, (newValue) => {
  if (newValue) {
    filteredData.value = originalData.value.filter((user) =>
      user.account.toLowerCase().includes(newValue.toLowerCase()),
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
      // 更新本地数据
      const targetOriginal = originalData.value.find((user) => user.id === row.id);
      if (targetOriginal) {
        targetOriginal.enable = value;
      }
      const targetFiltered = filteredData.value.find((user) => user.id === row.id);
      if (targetFiltered) {
        targetFiltered.enable = value;
      }
      // 给出提醒
      const message = value ? '用户已启用' : '用户已停用';
      await MessagePlugin.info({
        content: message,
        duration: 2000,
      });
    }
  } catch (error) {
    console.error('Error updating user enable status:', error);
  }
}

function handleDetailClick(row: User) {
  console.log('查看详情:', row);
}

function handleApplyAgainClick(row: User) {
  console.log('再次申请:', row);
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
  justify-content: flex-end;
  align-items: center;
  padding-bottom: 20px;
}
</style>
