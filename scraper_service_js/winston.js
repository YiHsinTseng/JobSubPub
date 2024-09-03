const winston = require('winston');

const customFormat = winston.format.printf(({
  level, message, timestamp, source,
}) => {
  const colorizer = winston.format.colorize();
  return `${timestamp} ${colorizer.colorize(level, `[${source ? `${source}_` : ''}${level}]`)}: ${message}`;
});

const logger = winston.createLogger({
  level: 'info',
  format: winston.format.combine(
    winston.format.timestamp(),
    customFormat,
  ),
  transports: [
    new winston.transports.Console({
      level: 'info',
    }),
    new winston.transports.File({
      filename: 'combined.log',
      level: 'warn',
      format: winston.format.combine(
        winston.format.timestamp(),
        winston.format.json(),
      ),
    }),
  ],
});

module.exports = logger;
