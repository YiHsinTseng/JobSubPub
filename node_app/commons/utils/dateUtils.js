// dateUtils.js
// 需要用UTC時區還是轉成台北時區
const { DateTime } = require('luxon');


function getcurrentDate() {
  const currentDate = new Date().setHours(0, 0, 0, 0);
  return currentDate;
}

function getTime2ISO(date) {
  return DateTime.fromJSDate(date).toUTC().toISO();
}

function isDateString(dateString){
  const date = new Date(dateString); 
  return !isNaN(date.getTime()); 
}

module.exports = { getTime2ISO,isDateString,getcurrentDate };
