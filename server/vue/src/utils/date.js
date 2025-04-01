export function formatDate(date, fmt) {
    if (/(y+)/.test(fmt)) {
      fmt = fmt.replace(RegExp.$1, (date.getFullYear() + '').substr(4 - RegExp.$1.length));
    }
    let o = {
      'M+': date.getMonth() + 1,
      'd+': date.getDate(),
      'h+': date.getHours(),
      'm+': date.getMinutes(),
      's+': date.getSeconds()
    };
    for (let k in o) {
      if (new RegExp(`(${k})`).test(fmt)) {
        let str = o[k] + '';
        fmt = fmt.replace(RegExp.$1, (RegExp.$1.length === 1) ? str : padLeftZero(str));
      }
    }
    return fmt;
  }
  
  function padLeftZero(str) {
    return ('00' + str).substr(str.length);
  }
  
  export function str2Date(dateStr, separator = '-') {
    let dateArr = dateStr.split(separator);
    let year = parseInt(dateArr[0]);
    let month = dateArr[1].startsWith('0') ? parseInt(dateArr[1].substring(1)) : parseInt(dateArr[1]);
    let day = parseInt(dateArr[2]);
    return new Date(year, month - 1, day);
  }
  