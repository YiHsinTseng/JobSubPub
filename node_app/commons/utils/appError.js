class AppError extends Error {
  constructor(statusCode, message,detail) {
    super(message);

    this.statusCode = statusCode;
    this.status = `${statusCode}`.startsWith('4') ? 'fail' : 'error';
    this.isOperational = true;
    this.detail = detail || message;
    Error.captureStackTrace(this, this.constructor);
  }
}
module.exports = AppError;
