// utils/debounce.js
export function debounce(func, delay) {
  let timer;
  return function (...args) {
    if (!timer) {
      func.apply(this, args); // 立即执行
    }
    clearTimeout(timer);
    timer = setTimeout(() => {
      timer = null; // 重置计时器
    }, delay);
  };
}
