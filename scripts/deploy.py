from tokenize import Token
from scripts.helper import get_account, get_contract
from brownie import DappToken, TokenFarm
from web3 import Web3

def deploy_dapp_and_farm():
    account = get_account()
    dapp_token = DappToken.deploy({"from": account})
    token_farm = TokenFarm.deploy(dapp_token.address, {"from": account})
    tx = dapp_token.transfer(token_farm.address, dapp_token.totalSupply() - Web3.toWei(100, "ether"), {"from": account})
    tx.wait(1)
    weth_token = get_contract("weth_token")
    allowed_tokens = {
        weth_token: get_contract("eth_usd_price_feed"), # mock
        dapp_token: get_contract("dai_usd_price_feed")
    }
    add_allowed_tokens(token_farm, allowed_tokens, account )
    return token_farm, dapp_token

def add_allowed_tokens(token_farm, allowed_tokens, account):
    for token in allowed_tokens:
        add_tx = token_farm.addAllowedTokens(token.address, {"from": account})
        add_tx.wait(1)
        set_tx = token_farm.setPriceFeedContract(token.address, allowed_tokens[token], {"from": account})
        set_tx.wait(1)
    #return token_farm

def main():
    deploy_dapp_and_farm()