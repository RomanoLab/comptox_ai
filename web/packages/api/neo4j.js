const neo4j = require('neo4j-driver');

const driver = neo4j.driver('bolt://165.123.13.192:7687');

module.exports = function(req, res, next) {
  req.driver = driver;
  console.log(driver);

  next();
};