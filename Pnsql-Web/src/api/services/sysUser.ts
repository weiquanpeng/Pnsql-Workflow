import { request } from '@/utils/request';

const Api = {
  SysUserByAccount: '/public/login',
  SysUserGetList: '/SysGetUserList',
  SysUptUserEnable: '/SysUptUser',
};

export function getSysUserList() {
  return request.post({
    url: Api.SysUserGetList,
  });
}

export function getSysUserByAccount(account: string, password: string) {
  return request.post({
    url: Api.SysUserByAccount,
    data: {
      account,
      password,
    },
  });
}

export function SysUptUser(id: number, enable: number) {
  return request.post({
    url: Api.SysUptUserEnable,
    data: {
      id,
      enable,
    },
  });
}
