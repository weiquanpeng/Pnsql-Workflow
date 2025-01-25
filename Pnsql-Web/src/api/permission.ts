import menuListData from '../../mock/menuList.json'; // 导入本地数据

export function getMenuList() {
  return Promise.resolve(menuListData); // 确保返回的是 Promise
}
