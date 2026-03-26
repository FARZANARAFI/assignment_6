const Example = artifacts.require('./Example.sol');

const ZERO_ADDRESS = "0x0000000000000000000000000000000000000000";


contract("Example_Unit_Test", (accounts) => {

  let example;

  beforeEach(async () => {
    example = await Example.new();
  })

  it("It should return admin address", async () => {
    // Should returns true as accounts[0] is deployer
    assert((await example.isAdministrator(accounts[0])) == true);

    // Should returns false as accounts[1] is not deployer
    assert((await example.isAdministrator(accounts[1])) == false);
    try {
      // Should returns false as accounts[1] is not deployer
      assert((await example.isAdministrator(accounts[1])) == true);
    } catch (error) { }
  })

});

