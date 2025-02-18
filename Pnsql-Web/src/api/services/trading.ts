import { request } from '@/utils/request';

const Api = {
  stock_f0: '/stock_f0',
  FollowStock: '/FollowStock',
  UpdateFollow: '/UpdateFollow',
  dragon_query: '/dragon_query',
  annual_moving_average: '/annual_moving_average',
  sixty_moving_average: '/sixty_moving_average',
  FollowedList: '/FollowedList',
};

export function getStockF0(f0Id: string) {
  return request.post({
    url: Api.stock_f0,
    data: {
      f0Id,
    },
  });
}

export function getFollowStock() {
  return request.post({
    url: Api.FollowStock,
  });
}

// eslint-disable-next-line camelcase
export function uptFollowStatus(stock_ticker: string, follow: number) {
  return request.post({
    url: Api.UpdateFollow,
    data: {
      // eslint-disable-next-line camelcase
      stock_ticker,
      follow,
    },
  });
}

// eslint-disable-next-line camelcase
export function getDragon_queryDate(date: string) {
  return request.post({
    url: Api.dragon_query,
    data: {
      date,
    },
  });
}

export function getAnnualMovingAverage(date: string) {
  return request.post({
    url: Api.annual_moving_average,
    data: {
      date,
    },
  });
}

export function getSixtyMovingAverage(date: string) {
  return request.post({
    url: Api.sixty_moving_average,
    data: {
      date,
    },
  });
}

export function getFollowedList() {
  return request.post({
    url: Api.FollowedList,
  });
}
