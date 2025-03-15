import { request } from '@/utils/request';

const Api = {
  read_log: '/read_log',
};

export function getJobLogData(jobid: number) {
  return request.post({
    url: Api.read_log,
    data: {
      jobid,
    },
  });
}
