
const SimpleStorage = artifacts.require("SimpleStorage.sol");
const TransactionContract = artifacts.require("TransactionContract.sol");

module.exports = async function (deployer, network, accounts) {
  

  await deployer.deploy(SimpleStorage);
  const example = await SimpleStorage.deployed();

  await deployer.deploy(TransactionContract);
  const example1 = await TransactionContract.deployed();

};


