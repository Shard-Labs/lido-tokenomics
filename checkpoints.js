const Web3 = require('web3');
const abi = require('./Checkpoint.json')
const fs = require('fs');

async function main() {


    const web3 = new Web3(new Web3.providers.HttpProvider('https://mainnet.infura.io/v3/4ef3b365c6b141ee81e8d8ae0c6a4bed'));
    const contract = new web3.eth.Contract(abi, '0x86E4Dc95c7FBdBf52e33D563BbDB00823894C287');
    const latestBlock = await web3.eth.getBlockNumber();
    const startBlock = 10167725;
    var rewards = []
    var lastReward = web3.utils.toBN('0');
    for(var block = startBlock; block < latestBlock; block += 50000)
    {
        console.log("Getting events...");
        const pastEvents = await contract.getPastEvents('NewHeaderBlock', {fromBlock: block, toBlock: Math.min(block + 50000, latestBlock)});
        var blcs = []
        var rs = []
        for(e of pastEvents) {

            const reward = web3.utils.toBN(e['returnValues']['reward']);
            const totalReward = lastReward.add(reward);
            const blockNumber = parseInt(e['blockNumber']);

            blcs.push(web3.eth.getBlock(blockNumber))
            rs.push([blockNumber, reward.toString(), totalReward.toString()]);
            lastReward = totalReward;
        }

        console.log("Getting blocks...");

        blcs = await Promise.all(blcs);

        for(var i = 0; i < blcs.length; i++) {
            const [blockNumber, reward, totalReward] = rs[i];
            const timestamp = blcs[i].timestamp
            console.log(blockNumber, timestamp, reward, totalReward);
            rewards.push([blockNumber, timestamp, reward, totalReward])
        }

        await new Promise(resolve => setTimeout(resolve, 100));
    }
    
    console.log(rewards);
    var json = JSON.stringify(rewards);
    fs.writeFileSync('all-rewards.json', json, 'utf8');

}

main().catch(e => {
    console.error(e)
    process.exit(1)
})



