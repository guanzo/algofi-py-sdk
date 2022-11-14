# This sample is provided for demonstration purposes only.
# It is not intended for production use.
# This example does not constitute trading advice.


def print_market_state(market):
    market.update_global_state()
    print("underlying_cash =", market.get_underlying_cash())
    print("bank_circulation =", market.get_bank_circulation())
    print("active_collateral =", market.get_active_collateral())
    print("underlying_borrowed =", market.get_underlying_borrowed())
    print("total_borrow_interest_rate =", market.get_total_borrow_interest_rate())


def print_user_state(client, symbol, address):
    user_state = client.get_user_state(address)
    for key, value in user_state["manager"].items():
        print(key, "=", value)
    for key, value in user_state[symbol].items():
        print(key, "=", value)
    asset = client.get_market(symbol).get_asset()
    print(
        "user_balance_asset =",
        client.get_user_balance(asset.get_underlying_asset_id())
        / 10 ** asset.get_underlying_asset_info()["decimals"],
    )
    print(
        "user_balance_bank_asset =",
        client.get_user_balance(asset.get_bank_asset_id())
        / 10 ** asset.get_bank_asset_info()["decimals"],
    )


def print_staking_contract_state(client, staking_contract_name, address):
    staking_contract = client.get_staking_contract(staking_contract_name)
    staking_contract.update_global_state()
    print("staked =", staking_contract.get_staked())
    staking_contact_user_state = staking_contract.get_user_state(address)
    print("user_staked =", staking_contact_user_state["staked"])
