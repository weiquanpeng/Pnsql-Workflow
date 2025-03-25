import { request } from '@/utils/request';

const Api = {
  stock_f0: '/stock_f0',
  FollowStock: '/FollowStock',
  UpdateFollow: '/UpdateFollow',
  dragon_query: '/dragon_query',
  annual_moving_average: '/annual_moving_average',
  annual_moving_average2: '/annual_moving_average2',
  sixty_moving_average: '/sixty_moving_average',
  FollowedList: '/FollowedList',
  ResetAllFollows: '/ResetAllFollows',
  get_record_by_id: '/get_record_by_id',
  update_dragon_time: '/update_dragon_time',
  update_average_time: '/update_average_time',
  update_gold_time: '/update_gold_time',
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

export function getAnnualMovingAverage2(date: string) {
  return request.post({
    url: Api.annual_moving_average2,
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

export function ResetAllFollows() {
  return request.post({
    url: Api.ResetAllFollows,
  });
}

export function getRecordDay() {
  return request.post({
    url: Api.get_record_by_id,
  });
}

// eslint-disable-next-line camelcase
export function updateDragonTime(dragon_time: string) {
  return request.post({
    url: Api.update_dragon_time,
    data: {
      id: 1,
      // eslint-disable-next-line camelcase
      dragon_time,
    },
  });
}

// eslint-disable-next-line camelcase
export function updateAverageTime(average_time: string) {
  return request.post({
    url: Api.update_average_time,
    data: {
      id: 1,
      // eslint-disable-next-line camelcase
      average_time,
    },
  });
}

// eslint-disable-next-line camelcase
export function updateGoldTime(gold_time: string) {
  return request.post({
    url: Api.update_gold_time,
    data: {
      id: 1,
      // eslint-disable-next-line camelcase
      gold_time,
    },
  });
}
