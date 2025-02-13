import { request } from '@/utils/request';

const Api = {
  TaskConfigGetList: '/TaskConfigGetList',
  TaskConfigGetMineList: '/TaskConfigGetMineList',
  TaskConfigGetApproveList: '/TaskConfigGetApproveList',
  TaskConfigAddData: '/TaskConfigAddData',
  SubTaskConfigList: '/SubTaskConfigList',
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
export function getSubTaskConfigData(id: number, type: string) {
  return request.post({
    url: `${Api.SubTaskConfigList}?dag_run_id=${id}`,
    data: {
      // eslint-disable-next-line camelcase
      type,
    },
  });
}
