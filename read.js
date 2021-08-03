const Web3 = require('web3');
const abi = require('./StakeManager.json')
const infoAbi = require('./StakeInfo.json');
const fs = require('fs');
const validator = require('./validators.json');


function calculateCorrection(validator, block) {

    
    validator.totalWithdrawn.sort((a, b) => {
        return a[0] - b[0];
    });
    var correction = (validator.totalWithdrawn[0] === undefined ? 0 : validator.totalWithdrawn[0][1]);
    for(var i = 0; i < validator.totalWithdrawn.length; i++) {
        [currentBlock, amount] = validator.totalWithdrawn[i];
        if(currentBlock > block) {
            return correction;
        }
        else {
            correction = amount;
        }
    }
    return correction
}


async function main() {


    const web3 = new Web3(new Web3.providers.HttpProvider('https://api.archivenode.io/xxx'));

    const contract = new web3.eth.Contract(abi, '0x5e3Ef299fDDf15eAa0432E6e66473ace8c13D908');
    const infoContract = new web3.eth.Contract(infoAbi, '0xa59C847Bd5aC0172Ff4FE912C5d29E5A71A7512B');


    const startBlock = 12120000;
    const latestBlock = await web3.eth.getBlockNumber();
    
    for(var i = startBlock; i < latestBlock; i+= 5000) {
        console.log("Processing block " + i);
        contract.defaultBlock = i;
        var promises = [];
        for(var j = 0; j < validator.length; j++) {
            if(i > validator[j].startBlock && i < validator[j].endBlock) {
                var reward = contract.methods.validatorReward(validator[j].id).call();
                var stake = contract.methods.validatorStake(validator[j].id).call();
                promises.push([validator[j].id, i, stake, reward]);
                await new Promise(resolve => setTimeout(resolve, 110));
            }
        }
        for(var j = 0; j < promises.length; j++) {
            await Promise.all(promises[j]).then(values => {
                [id, block, stake, reward] = values;
                for(var k = 0; k < validator.length; k++) {
                    if(validator[k].id === id) {
                        console.log("Processed validator: " + [id, block, stake, reward]);
                        validator[k].rewards.push([block, stake, reward]);
                        break;
                    }
                }
            })
        }
        var json = JSON.stringify(validator);
        fs.writeFileSync('validators-populated.json', json, 'utf8');
        console.log("--------------------------------------------");
    }
    
    var promises = []
    for(var i = 0; i < validator.length; i++) {
        promises.push([i, infoContract.getPastEvents('ClaimRewards', {filter: {'validatorId': i}, fromBlock: startBlock, toBlock: latestBlock})]);
        await new Promise(resolve => setTimeout(resolve, 250));
    }

    for(var i = 0; i < promises.length; i++) {
        await Promise.all(promises[i]).then(values => {
            console.log("Processing validator: " + validator[i].id);
            var [id, pastEvents] = values;
            pastEvents.forEach(event => {
                validator[id].totalWithdrawn.push([event['blockNumber'], event['returnValues']['totalAmount']]);
            });

        })
        var json = JSON.stringify(validator);
        fs.writeFileSync('validators-populated.json', json, 'utf8');
    }


    for(var i = 0; i < validator.length; i++) {
        for(var j = 0; j < validator[i].rewards.length; j++) {
            const [block, stake, reward] = validator[i].rewards[j];
            const total = web3.utils.toBN(reward).add(web3.utils.toBN(calculateCorrection(validator[i], block)));
            validator[i].totalRewards.push([block, web3.utils.fromWei(stake, 'ether'), web3.utils.fromWei(total, 'ether')]);
        }
    }

    var json = JSON.stringify(validator);
    fs.writeFileSync('validators-populated.json', json, 'utf8');
}

main().catch(e => {
    console.error(e)
    process.exit(1)
})



