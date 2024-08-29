// dateUtils.js
const { DateTime } = require('luxon');

function formatDateToYYYYMMDD(date) {
  return DateTime.fromJSDate(date).toFormat('yyyy-MM-dd');
}

function getDateInTimeZone(timeZone) {
  return DateTime.now().setZone(timeZone).toFormat('yyyy-MM-dd');
}

function getDate() {
  return DateTime.now().setZone('Asia/Taipei').toFormat('yyyy-MM-dd');
}

module.exports = { formatDateToYYYYMMDD, getDateInTimeZone, getDate };
