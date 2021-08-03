var Web3 = require('web3');


async function main() {
    var abi = require('./StakeManager.json')

    var web3 = new Web3(new Web3.providers.HttpProvider('https://eth-mainnet.alchemyapi.io/v2/xxxx')); //archive node

    var contract = new web3.eth.Contract(abi, '0x5e3Ef299fDDf15eAa0432E6e66473ace8c13D908');
    const latest = await web3.eth.getBlockNumber()

    console.log("blocknumber,timestamp,totalStaked,totalRewards,")

    for(var i = 10342580; i < latest; i+= 5000) {
        contract.defaultBlock = i;
        var rewards = await contract.methods.totalRewards().call()
        var staked = await contract.methods.totalStaked().call()
        var timestamp = (await web3.eth.getBlock(i)).timestamp
        console.log(i + ',' + timestamp + ',' + staked + ',' + rewards + ',' )
    }

}

main().catch(e => {
    console.error(e)
    process.exit(1)
})