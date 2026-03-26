# Introduction

Well, you have come to the right place. Just clone this repository, make a few modifications and you
will be ready to start with the development of the project without spending more time on the initial setups.

The repository got some strict styling and linter rule to maintain
the code standard and to detect security risks of the contracts to some extent.

Currently, the truffle config and ganache support the following manner and test networks and only support
Nownodes RPC JSON endpoints out of the box. One can add/modify them as per their requirements.

- Ethereum
- Binance Smart Chain
- Polygon
- SmartBch

## Content

1. [Prerequisite](./README.md#1-prerequisite)
2. [Setup](./README.md#2-setup)
3. [Usage](./README.md#3-Usage)
4. [Dependencies & Plugins](./README.md#4-dependencies--plugins)
5. [Additional Info](/README.md#5-Additional--Info)

## 1. Prerequisite

You should have already installed the following things beforehand:

- [Node JS](https://nodejs.org/en/)
- Truffle & Ganache-cli

  ```node
  npm i -g truffle ganache
  ```

- [Git Bash](https://git-scm.com/downloads)
- Visual Studio Code [(VS Code)](https://code.visualstudio.com/)

## 2. Setup

- In `package.json`, change the following items.

  ```json
  {
  "name": "solidity-project-template",
  "description": "Add your project description here",
   "repository": {
    "type": "git",
    "url": "https://github.com/akshay-na/solidity-project-template.git"
  },
  }
  ```

- Make a copy of ``.env example`` and rename it into ``.env``
- Open the .env and fill up the given variables.
- You can get your [Nownodes](https://nownodes.io/) or
  [Tatum](https://tatum.io/) API's from their website.
- The mnemonics from the .env will be used for truffle console and creating local development blockchain using ganache.
- The reason behind using same mnemonics is to connect metamask or any DeFi
  application to the local forked blockchain to test your applications locally.
- You can adjust the gas, gas price and other network parameters directly on `truffle-config.js`

**_Disclaimer_:** Make sure that you use your test/dev mnemonics. Don't use your investment wallet or wallet/mnemonics that has large
number of crypto assets in it on any of the mainnets. You will be solely responsible if you loose your crypto asset

## 3. Usage

- Once you have completed all the steps from the [setup section](./README.md#2-setup), go ahead and install the rest of the dependencies.

  ```node
  npm install
  ```

- This will install all the other dependencies listed on `package.json`
- The file `ganache` in this repo is a custom shell script to fork any
  mentioned networks from the `.env`. Also it will use the mnemonics from `.env`
  to facilitate easier testing environment for your project.
- One can easily fork a given network by executing `./ganache -n polygon` from   the
  git bash terminal
- Ganache help page

  ```bash
  Custom Ganache script to easily fork any chain from .env file.

  Syntax: ./ganache [option] [args]

  [options]

  -n     Networks: eth, bsc, polygon, smartbch
         For testnets add _testnet. Example: bsc_testnet
  -h     Print this Help.
  -u     unlocks the given accounts.
  ```

- To compile and test the contract, the following scripts can be used. It will
  run the styler and linter before compiling or testing the contracts.

  ```java
  // For compiling the contracts.
  npm start

  // For testing the contracts.
  npm test
  ```

- To remove styler and linter, one can just make the following changes in `package.json`

  ```json
  From:

  "test": "npm run prettier && npm run solhint && npx truffle test --stacktrace",
  "start": "npm run prettier && npm run solhint && npx truffle compile",
  "migrate": "npm run prettier && npm run solhint && npx truffle migrate",

  To:

  "test": "npx truffle test --stacktrace",
  "start": "npx truffle compile",
  "migrate": "npx truffle migrate",
  ```

## 4. Dependencies & Plugins

### 1. Truffle-verify-plugin

- This plugin helps us to verify the deployed contracts on any public testnets
  or mainnets
  directly from the terminal.
- make sure you have added your API from etherscan or bscscan.
- Refer
  [truffle-verify-plugin
  docs](https://www.npmjs.com/package/truffle-plugin-verify) for more
  customization options.

### 2. Solidity-coverage

- This help us in testing the contract.
- It will give out a detailed report on how much of the contract is tested and
  need to be tested.
_ Refer [solidity-coverage
docs](https://www.npmjs.com/package/@davidqhr/solidity-coverage) for more
customization options.

### 3. Solhint & Prettier-plugin-solidity

- These will help us in linting and styling the code base.
- Works upon the rules specified on `.solhint.json` and `.prettierrc` files.
- Refer [solhint docs](https://www.npmjs.com/package/solhint) & [prettier-plugin-solidity docs](prettier-plugin-solidity) for more
customization options.

### 4. Truffle-contract-size

- Returns the size of each contracts.
- This is helpful while working with chains that has a code limit of 24kb

```node
npx truffle run contract-size
```

- For mor information refer [truffle-contract-size docs](https://www.npmjs.com/package/truffle-contract-size)

### 5. Husky (git hook)

- In an ideal world, we’d always remember to run our linter and formatter before pushing code to our team’s codebase.

- Fortunately for us, we can automate this process with Git Hooks. These are tiny scripts that always run before or after Git events like commits, pushes, or receives.

```json
// package.json
{
  "husky": {
    "hooks": {
       "pre-push": "npm run prettier:solidity"
    }
  }
}
```

- For more information refer [husky docs](https://www.npmjs.com/package/husky).

## 5. Additional Info

There are some extension, plugin and dependencies that are already setup and
works right out of the box. You can always refer respective docs and customize
the things to your requirements.

If you have any issues, please feel free to point them out or pull the repo [here](https://github.com/akshay-na/solidity-project-template/issues) or feel free to fork the repo to improve it furthermore
