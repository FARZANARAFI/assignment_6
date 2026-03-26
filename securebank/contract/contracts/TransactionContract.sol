// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract TransactionContract {
    struct Transaction {
        string transactionType;
        uint256 amount;
        string recipientAccountNumber;
        string timestamp;
        string senderId;
    }

    mapping(uint256 => Transaction) transactions;
    uint256 public transactionCount;

    event TransactionAdded(uint256 transactionId);

    function addTransaction(
        string memory _transactionType,
        uint256 _amount,
        string memory _recipientAccountNumber,
        string memory _timestamp,
        string memory _senderId
    ) public {
        transactionCount++;
        transactions[transactionCount] = Transaction({
            transactionType: _transactionType,
            amount: _amount,
            recipientAccountNumber: _recipientAccountNumber,
            timestamp: _timestamp,
            senderId: _senderId
        });
        emit TransactionAdded(transactionCount);
    }

    function getTransactionDetails(uint256 _transactionId) public view returns (Transaction memory) {
        require(_transactionId > 0 && _transactionId <= transactionCount, "Invalid transactionId");
        return transactions[_transactionId];
    }
}
