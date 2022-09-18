from scripts.helper import get_account
from scripts.deploy import deploy_dapp_and_farm

from web3 import Web3

amount_to_stake = Web3.toWei(1, "ether")

def rewardToken():
    account = get_account()
    token_farm, dapp_token = deploy_dapp_and_farm()
    approve_tx = dapp_token.approve(token_farm.address, amount_to_stake, {"from": account})
    approve_tx.wait(1)
    stake_tx = token_farm.stakeTokens(amount_to_stake, dapp_token.address, {"from": account})
    stake_tx.wait(1)
    userTotalValue = token_farm.rewardTokens({"from": account})
    print(userTotalValue)

def main():
    rewardToken()