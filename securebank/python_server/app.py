
#*****************************************************************************************************************
#                                                EthereumContract                                                #
#*****************************************************************************************************************

from web3 import Web3
import json
class EthereumContract:
    def __init__(self, node_url, contract_address, abi):
        self.web3 = Web3(Web3.HTTPProvider(node_url))
        self.contract = self.web3.eth.contract(address=contract_address, abi=abi)
        self.caller = None
        self.private_key = None

    def connect(self):
        if self.web3.is_connected():
            print("-" * 50)
            print("Connection Successful")
            print("-" * 50)
        else:
            print("Connection Failed")

    def set_caller_credentials(self, caller, private_key):
        self.caller = caller
        self.private_key = private_key

    def get_nonce(self):
        return self.web3.eth.get_transaction_count(self.caller)

    def build_transaction(self, function_name, *args):
        nonce = self.get_nonce()
        call_function = getattr(self.contract.functions, function_name)(*args).build_transaction(
            {"chainId": self.web3.eth.chain_id, "from": self.caller, "nonce": nonce}
        )
        return call_function

    def sign_and_send_transaction(self, call_function):
        signed_tx = self.web3.eth.account.sign_transaction(call_function, private_key=self.private_key)
        send_tx = self.web3.eth.send_raw_transaction(signed_tx.rawTransaction)
        tx_receipt = self.web3.eth.wait_for_transaction_receipt(send_tx)
        print("Transaction successful")
        return tx_receipt

    def call_function_and_print_result(self, function_name, *args):
        result = getattr(self.contract.functions, function_name)(*args).call()
        print(f'The result of {function_name} is: {result}')
        return result


def read_abi_from_json(file_path):
    with open (file_path, 'r') as file:
        data = json.load(file)
        return data['abi']
    
#*****************************************************************************************************************

from flask import Flask, request, jsonify
from web3 import Web3
import json

app = Flask(__name__)

rpcUrl = 'http://127.0.0.1:7545'
contract_address = "0x67a018Caff98561922298941191494E43Fc8d766"
transaction_abi_path = r'C:\securebank\contract\build\contracts\TransactionContract.json'
caller_address = "0xDCEe66e7F559804F07d738bE6190422Ea4d201d7"
caller_privateKey = "0x24a0fbbfb52a0b59178a08ae2dd14362e20157a9cd42e4f8595c83df9a59f9ce"

transaction_abi = read_abi_from_json(transaction_abi_path)
transaction_contract = EthereumContract(rpcUrl, contract_address, transaction_abi)

transaction_contract.connect()
transaction_contract.set_caller_credentials(caller_address, caller_privateKey)

from datetime import datetime

@app.route('/addTransactionToBlockchain', methods=['POST'])
def addTransactionToBlockchain():
    try:
        data = request.get_json()
        transactionType = str(data.get('transactionType'))  
        amount = int(data.get('amount')) 
        recipientAccountNumber = str(data.get('recipientAccountNumber')) 
        timestamp = str(datetime.now()) 
        senderId = str(data.get('senderId')) 

        call_function_transaction = transaction_contract.build_transaction("addTransaction", transactionType, amount, recipientAccountNumber, timestamp, senderId)
        
        tx_receipt_transaction = transaction_contract.sign_and_send_transaction(call_function_transaction)

        response = {
            'status': 'success',
            'transaction_hash': tx_receipt_transaction['transactionHash'].hex()
        }
    except Exception as e:
        response = {'status': 'error', 'message': str(e)}

    return jsonify(response)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
