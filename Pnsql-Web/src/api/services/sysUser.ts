import { request } from '@/utils/request';

const Api = {
  SysUserByAccount: '/public/login',
  SysUserGetList: '/SysGetUserList',
  SysUptUserEnable: '/SysUptUser',
  SysAddUser: '/SysAddUser',
  SysDelUser: '/SysDelUser',
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

export function SysAddUser(data: Record<string, any>) {
  return request.post({
    url: Api.SysAddUser,
    data,
  });
}

export function SysDelUser(id: number) {
  return request.post({
    url: Api.SysDelUser,
    data: {
      id,
    },
  });
}

export function SysUptPassword(id: number, password: string) {
  return request.post({
    url: Api.SysUptUserEnable,
    data: {
      id,
      password,
    },
  });
}

export function SysUptRoles(id: number, roles: unknown[]) {
  return request.post({
    url: Api.SysUptUserEnable,
    data: {
      id,
      roles,
    },
  });
}
