// dateUtils.js
// 需要用UTC時區還是轉成台北時區
const { DateTime } = require('luxon');


function getcurrentDate() {
  const currentDate = new Date();
  const currentDateOnly = new Date(currentDate.getFullYear(), currentDate.getMonth(), currentDate.getDate());
  return currentDateOnly;
}

function getTime2ISO(date) {
  return DateTime.fromJSDate(date).toUTC().toISO();
}

function getTime2ISO(date) {
  return DateTime.fromJSDate(date).toUTC().toISO();
}


function isDateString(dateString){
  const date = new Date(dateString); 
  return !isNaN(date.getTime()); 
}

module.exports = { getTime2ISO,isDateString,getcurrentDate };
