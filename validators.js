const parse = require('csv-parse');
const fs = require('fs');
const Web3 = require('web3');


 
const processFile = async () => {
    const web3 = new Web3(new Web3.providers.HttpProvider('https://eth-mainnet.alchemyapi.io/v2/xxx'));
    var validators = [];
    const latestBlock = await web3.eth.getBlockNumber()
    const parser = fs
  .createReadStream(`./tokenHolders.csv`)
  .pipe(parse());
  for await (const record of parser) {
    validator = Object();
    validator.rewards = [];
    validator.totalWithdrawn = [];
    validator.totalRewards = [];
    validator.id = parseInt(record[1]);
    
    validator.startBlock = parseInt(record[0]);
    validator.endBlock = record[2] === "0" ? latestBlock : parseInt(record[2]);
    validators.push(validator)
  }
  return validators;
  
}
(async () => {
  const records = await processFile()
  var json = JSON.stringify(records);
  fs.writeFileSync('validators.json', json, 'utf8');

  console.info(records);
})()


