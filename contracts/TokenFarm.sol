// stake tokens
// unstake tokens
// issue tokens
// add allowed tokens
// get eth value

//SPDX-License-Identifier: MIT

pragma solidity ^0.8.0;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@chainlink/contracts/src/v0.8/interfaces/AggregatorV3Interface.sol";

contract TokenFarm is Ownable{

    address[] public allowedTokens; // list of allowed tokens
    address[] public stakers;
    IERC20 public dappToken;
    mapping(address => mapping(address => uint)) public stakingBalance; //mapping token address => staker address => amount
    mapping(address => uint) public uniqueTokensStaked;
    mapping(address => address) public tokenPriceFeedMappiing;

    constructor(address _dappToken) public {
        dappToken = IERC20(_dappToken); 
    }

    function stakeTokens(uint _amount, address _token) public {
        require(_amount > 0, "You can't stake zero tokens");
        require(checkTokens(_token), "Token not allowed");
        IERC20(_token).transferFrom(msg.sender, address(this), _amount); // from, to, amount
        updateUniqueTokensStaked(msg.sender, _token);
        stakingBalance[_token][msg.sender] = stakingBalance[_token][msg.sender] + _amount;
        if(uniqueTokensStaked[msg.sender] == 1){ // it means the user has alwarey staked
            stakers.push(msg.sender); // so add this user to the stakers list
        }
    }

    function unstakeTokens(address _token) public {
        uint balance = stakingBalance[_token][msg.sender]; // checking balance
        require(balance > 0, "You do not have any amount to unstake");
        IERC20(_token).transfer(msg.sender, balance);
        stakingBalance[_token][msg.sender] = 0;
        uniqueTokensStaked[msg.sender] = uniqueTokensStaked[msg.sender] - 1;
    }

    function setPriceFeedContract(address _token, address _priceFeed) public onlyOwner{
         // I have to go trough all the addresses of price feeds
         tokenPriceFeedMappiing[_token] = _priceFeed;
     }

    function rewardTokens() public onlyOwner {
        // loop through all stakers
        for(uint stakersIndex = 0; stakersIndex < stakers.length; stakersIndex++){
            address recipient = stakers[stakersIndex];
            uint userTotalValue = getUserTotalValue(recipient);
            dappToken.transfer(recipient, userTotalValue);
            //send them a token reward
            //dappToken.transfer(recipient, )
            //based on their total value locked

        }
    }

    function getUserTotalValue(address _user) public view returns(uint){
        uint totalValue = 0;
        require(uniqueTokensStaked[_user] > 0, "You do not have any token staked!");
        for(uint allowedTokensIndex = 0; allowedTokensIndex < allowedTokens.length; allowedTokensIndex++){
            totalValue = totalValue + getUserSingleTokenValue(_user, allowedTokens[allowedTokensIndex]);
        }
        return totalValue;
    }

    function getUserSingleTokenValue(address _user, address _token) public view returns(uint){
        // I need to get the value of this person has into a specific token
        if(uniqueTokensStaked[_user] <= 0){
            return 0;
        }
        // price of the token * stakingBalance[_token[_user]
        (uint price, uint decimals) = getTokenValue(_token);
        return (stakingBalance[_token][_user] * price / (10**decimals));
    }

    function updateUniqueTokensStaked(address _user, address _token) internal {
        // how many unique tokens a determined user has
        if(stakingBalance[_token][_user] <= 0){ // if the user has 0 tokens staked
            uniqueTokensStaked[_user] = uniqueTokensStaked[_user] + 1;
        }
        
    }

    function getTokenValue(address _token) public view returns(uint, uint){
        address priceFeedAddress = tokenPriceFeedMappiing[_token];
        AggregatorV3Interface priceFeed = AggregatorV3Interface(priceFeedAddress);
        (,int price,,,) = priceFeed.latestRoundData();
        uint decimals = uint(priceFeed.decimals());
        return (uint(price), decimals);
    }

    function addAllowedTokens(address _token) public onlyOwner{
        allowedTokens.push(_token);
    }

    function checkTokens(address _token) public view returns (bool) {
        // let's loop through the allowedToken list and see if the passed address is in there
        for(uint tokenIndex = 0; tokenIndex < allowedTokens.length; tokenIndex++){
            if(_token == allowedTokens[tokenIndex]){
                return true;
            }
        }
        return false;   
    }
}