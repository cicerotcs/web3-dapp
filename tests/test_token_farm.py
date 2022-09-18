import pytest
from brownie import exceptions, network, accounts
from scripts.helper import LOCAL_TEST, get_account, get_contract
from scripts.deploy import deploy_dapp_and_farm
from web3 import Web3 

amount_to_stake = Web3.toWei(1, "ether")

def test_token_farm():
    if(network.show_active() not in LOCAL_TEST):
        pytest.skip("Only for local testing")
    account = get_account()
    another_account = accounts[1]
    token_farm, dapp_token = deploy_dapp_and_farm()
    price_feed = get_contract("dai_usd_price_feed")
    token_farm.setPriceFeedContract(dapp_token.address, price_feed, {"from": account})
    assert token_farm.tokenPriceFeedMappiing(dapp_token.address) == price_feed
    # testing if another account can call the setPriceFeed
    with pytest.raises(AttributeError):
        token_farm.setPriceFeedContract(dapp_token.address, price_feed, {"from": another_account})

def test_stake_tokens():
    account = get_account()
    token_farm, dapp_token = deploy_dapp_and_farm()
    approve_tx = dapp_token.approve(token_farm.address, amount_to_stake, {"from": account})
    approve_tx.wait(1)
    stake_tx = token_farm.stakeTokens(amount_to_stake, dapp_token.address, {"from": account})
    stake_tx.wait(1)
    assert token_farm.stakingBalance(dapp_token.address, account.address) == amount_to_stake
    #testing require > 0
    #with pytest.raises(AttributeError):
    #    token_farm.stakeTokens(0, dapp_token.address, {"from": account})
    assert token_farm.uniqueTokensStaked(account.address) == 1
    assert token_farm.stakers(0) == account.address
    return token_farm, dapp_token

def test_unstake_tokens():
    account = get_account()
    token_farm, dapp_token = test_stake_tokens()
    unstake_tx = token_farm.unstakeTokens(dapp_token.address, {"from": account})
    unstake_tx.wait(1)
    assert token_farm.stakingBalance(dapp_token, account.address) == 0
    assert token_farm.uniqueTokensStaked(account.address) == 0

def test_reward_tokens():
    account = get_account()
    token_farm, dapp_token = test_stake_tokens()
    initialBalance = dapp_token.balanceOf(account.address)
    token_farm.rewardTokens({"from": account})
    assert dapp_token.balanceOf(account.address) == initialBalance + 2000000000000000000000