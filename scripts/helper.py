from brownie import network, config, accounts, MockWeth, Contract, MockV3Aggregator

LOCAL_TEST = ["development", "ganache-local"]

from web3 import Web3

DECIMALS = 18
INITIAL_PRICE = 2000000000000000000000

contract_to_mock = {
    "eth_usd_price_feed": MockV3Aggregator,
    "dai_usd_price_feed": MockV3Aggregator,
    "weth_token": MockWeth
}

def get_account():
    if(network.show_active() in LOCAL_TEST):
        return accounts[0]
    else:
        return accounts.add(config["wallets"]["from_key"])


def get_contract(contract_name):
    contract_type = contract_to_mock[contract_name]
    if(network.show_active() in LOCAL_TEST):
        if len(contract_type) <= 0:
            deploy_mocks()
        contract = contract_type[-1]
    else:
        contract_address = config["networks"][network.show_active()][contract_name]
        contract = Contract.from_abi(contract_type._name, contract_address, contract_type.abi)
    return contract

def deploy_mocks():
    account = get_account()
    MockV3Aggregator.deploy(DECIMALS, INITIAL_PRICE, {"from": account})
    MockWeth.deploy({"from": account})
