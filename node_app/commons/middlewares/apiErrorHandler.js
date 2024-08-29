const apiErrorHandler = (err, req, res, next) => {
  // JSON parse error
  if (err instanceof SyntaxError && err.status === 400 && 'body' in err) {
    err.status = 'fail';
    err.statusCode = 400;
    err.message = 'Invalid JSON format in request body';
  }

  if (err) {
    err.statusCode = err.statusCode || 500; // if no statusCode is defined, then use HTTP500
    // if no status is defined and statusCode starts with 4, then set status to 'fail'
    if (!err.status && err.statusCode.toString().startsWith('4')) {
      err.status = 'fail';
    } else {
      err.status = err.status || 'error';
    }

    // return error status and message to the requester
    res.status(err.statusCode).json({
      status: err.status,
      message: err.message,
    });
  } else {
    next();
  }
};

module.exports = apiErrorHandler;
