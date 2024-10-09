import requests
import streamlit as st
import pandas as pd

API_KEY = "xxxxxx"

# Step 1: Get top 10 coins by market cap from CoinMarketCap
def get_top_coins_cmc():
    url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest"
    headers = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': API_KEY,
    }
    params = {
        'start': '1',
        'limit': '10',
        'convert': 'USD'
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        if 'data' in data:
            return data['data']
        else:
            st.error("Unexpected data format received from CoinMarketCap API.")
            return []
    except requests.exceptions.RequestException as e:
        st.error(f"An error occurred while fetching data: {e}")
        return []

# Step 2: Get exchange-wise data for a coin
def get_exchange_data(coin_id):
    url = f"https://pro-api.coinmarketcap.com/v1/cryptocurrency/market-pairs/latest"
    headers = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': API_KEY,
    }
    params = {
        'id': coin_id,
        'limit': 100  # Max limit is 100
    }
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        if 'data' in data and 'market_pairs' in data['data']:
            return data['data']['market_pairs']
        else:
            st.error(f"Unexpected data format for coin ID {coin_id}")
            return []
    except requests.exceptions.RequestException as e:
        st.error(f"An error occurred while fetching exchange data for coin ID {coin_id}: {e}")
        return []

# Step 3: Aggregate exchange volumes for a coin
def aggregate_exchange_volumes(market_pairs, coin_name):
    exchange_volumes = []
    for pair in market_pairs:
        exchange = pair['exchange']['name']
        volume_24h = pair['quote']['USD']['volume_24h']
        exchange_volumes.append({
            'coin': coin_name,
            'exchange': exchange,
            'volume_24h': volume_24h
        })
    return exchange_volumes

# Step 4: Fetch top coins for selection
top_coins = get_top_coins_cmc()

if top_coins:
    # Create a dictionary mapping coin names to their data
    coin_info = {coin['name']: coin for coin in top_coins}

    # Display available coins for selection
    selected_coins = st.multiselect("Select Coins", list(coin_info.keys()), default=list(coin_info.keys())[:5])

    if selected_coins:
        st.write("Fetching exchange data for selected coins...")

        # Initialize a list to hold all exchange volume data
        all_exchange_volumes = []

        for coin in selected_coins:
            coin_id = coin_info[coin]['id']
            coin_name = coin
            market_pairs = get_exchange_data(coin_id)
            if market_pairs:
                exchange_volumes = aggregate_exchange_volumes(market_pairs, coin_name)
                all_exchange_volumes.extend(exchange_volumes)

        # Convert to DataFrame
        if all_exchange_volumes:
            df = pd.DataFrame(all_exchange_volumes)

            # Get the list of exchanges
            all_exchanges = df['exchange'].unique().tolist()

            # Step 5: Allow users to select specific exchanges
            selected_exchanges = st.multiselect("Select Exchanges", all_exchanges, default=all_exchanges[:5])

            # Filter the DataFrame based on selected exchanges
            if selected_exchanges:
                df = df[df['exchange'].isin(selected_exchanges)]
            else:
                st.write("No exchanges selected. Displaying all exchanges.")

            # Step 6: Aggregate volume per exchange for each coin
            pivot_table = df.pivot_table(values='volume_24h', index='exchange', columns='coin', aggfunc='sum')

            # Visualize the data using a stacked bar chart
            st.write("### Exchange-wise 24h Trading Volume for Selected Coins")
            st.bar_chart(pivot_table)

            # Optionally, display the raw data
            st.write("#### Detailed Exchange Volume Data")
            st.dataframe(df)
        else:
            st.write("No exchange data available for the selected coins.")
else:
    st.error("No coin data available for selection.")
