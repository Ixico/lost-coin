# Custom Cryptocurrency Implementation
> **Note**: This project is currently under development.

This project is a Python-based implementation of a custom cryptocurrency, designed to operate within a distributed network. It uses a **proof-of-work** consensus mechanism to validate transactions and secure the network. 
## About

The aim of project is to introduce our own cryptocurrency System - LostCoin.

### Digital Identity
A digital identity is data stored on computer systems relating to an individual, organization, application, or device. For individuals, it involves the collection of personal data that is essential for facilitating automated access to digital services, confirming one's identity on the internet, and allowing digital systems to manage interactions between different parties. It is a component of a person's social identity in the digital realm, often referred to as their online identity.


### Simple blockchain
 
In the second milestone we've introduced block creation mechanism. Blocks are created by miner(s). 

### Transaction protocol

### Test Scenarios
1.  1 miner

### Requirements for 3rd milestone
1. Create transactions, e.g. in json format (the first transaction in the list should be a coinbase transaction creating new ‘coins’)
2. Reaching consensus (proof-of-work method)
3. Validation of transactions for double-spending
4. Calculation of current account balances



### Approach of transaction validation
1. Transaction have to be signed by the sender, then signature is verified by the public key by the recipent
2. Id field is needed to provide uniqueness of the transaction, 
### To do

1. Think about the better way to store and gather id, maybe from the previous block
2. Mechanism to prevent double spending is needed
3. Proof of work method, to reach consensus
