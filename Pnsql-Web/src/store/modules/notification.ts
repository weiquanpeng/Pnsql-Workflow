import { defineStore } from 'pinia';

import type { NotificationItem } from '@/types/interface';

const msgData = [
  {
    content: 'PnSql-Workflow-Server 后端正式发布！',
    type: '后端板块',
    status: true,
    collected: false,
    date: '2025-01-15',
    quality: 'high',
  },
  {
    content: 'PnSql-Workflow-Web 前端正式发布！',
    type: '前端板块',
    status: true,
    collected: false,
    date: '2025-01-10',
    quality: 'low',
  },
];

type MsgDataType = typeof msgData;

export const useNotificationStore = defineStore('notification', {
  state: () => ({
    msgData,
  }),
  actions: {
    setMsgData(data: MsgDataType) {
      this.msgData = data;
    },
  },
  persist: true,
});
