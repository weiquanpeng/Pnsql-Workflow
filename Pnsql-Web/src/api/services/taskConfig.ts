import { request } from '@/utils/request';

const Api = {
  TaskConfigGetList: '/TaskConfigGetList',
  TaskConfigGetMineList: '/TaskConfigGetMineList',
  TaskConfigGetApproveList: '/TaskConfigGetApproveList',
  TaskConfigAddData: '/TaskConfigAddData',
  SubTaskConfigList: '/SubTaskConfigList',
  UptSubTaskData: '/UptSubTaskData',
};

export function getTaskConfigList() {
  return request.post({
    url: Api.TaskConfigGetList,
  });
}

export function getMineTaskConfigList(data: Record<string, any>) {
  return request.post({
    url: Api.TaskConfigGetMineList,
    data,
  });
}

export function getApproveTaskConfigList(data: Record<string, any>) {
  return request.post({
    url: Api.TaskConfigGetApproveList,
    data,
  });
}

export function addTaskConfigData(data: Record<string, any>) {
  return request.post({
    url: Api.TaskConfigAddData,
    data,
  });
}

// eslint-disable-next-line camelcase
export function getSubTaskConfigData(task_id: number) {
  return request.post({
    url: Api.SubTaskConfigList,
    data: {
      // eslint-disable-next-line camelcase
      task_id,
    },
  });
}

export function UptSubTaskData(id: number, status: string) {
  return request.post({
    url: Api.UptSubTaskData,
    data: {
      id,
      status,
    },
  });
}
