class BaseSource {
  // Define the abstract methods
  sourceUrl(keyword, page) {
    throw new Error('Method "sourceUrl" must be implemented.');
  }

  parseSourceJob(baseUrl, html = null, job = null) {
    throw new Error('Method "parseSourceJob" must be implemented.');
  }
}

module.exports = BaseSource;
