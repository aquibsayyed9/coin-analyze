import requests
import streamlit as st
import pandas as pd

# Function to get top coins from CoinGecko
def get_top_coins_gecko():
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        'vs_currency': 'usd',
        'order': 'market_cap_desc',
        'per_page': 10,
        'page': 1
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"An error occurred while fetching data: {e}")
        return []

# Function to get exchange-wise data from CoinGecko for a specific coin
def get_exchange_data_gecko(coin_id):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/tickers"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return data['tickers'] if 'tickers' in data else []
    except requests.exceptions.RequestException as e:
        st.error(f"An error occurred while fetching exchange data for coin {coin_id}: {e}")
        return []

# Function to aggregate exchange volumes for a coin
def aggregate_exchange_volumes(market_pairs, coin_name):
    exchange_volumes = []
    for pair in market_pairs:
        exchange = pair['market']['name']
        volume_24h = pair['volume']
        exchange_volumes.append({
            'coin': coin_name,
            'exchange': exchange,
            'volume_24h': volume_24h
        })
    return exchange_volumes

# Fetch top coins from CoinGecko
top_coins = get_top_coins_gecko()

if top_coins:
    # Create a dictionary mapping coin names to their CoinGecko IDs
    coin_info = {coin['name']: coin['id'] for coin in top_coins}

    # Display available coins for selection
    selected_coins = st.multiselect("Select Coins", list(coin_info.keys()), default=list(coin_info.keys())[:5])

    if selected_coins:
        st.write("Fetching exchange data for selected coins...")

        # Initialize a list to hold all exchange volume data
        all_exchange_volumes = []

        for coin in selected_coins:
            coin_id = coin_info[coin]
            coin_name = coin
            market_pairs = get_exchange_data_gecko(coin_id)
            if market_pairs:
                exchange_volumes = aggregate_exchange_volumes(market_pairs, coin_name)
                all_exchange_volumes.extend(exchange_volumes)

        # Convert to DataFrame
        if all_exchange_volumes:
            df = pd.DataFrame(all_exchange_volumes)

            # Get the list of exchanges
            all_exchanges = df['exchange'].unique().tolist()

            # Exchange selection
            selected_exchanges = st.multiselect("Select Exchanges", all_exchanges, default=all_exchanges[:5])

            # Filter the DataFrame based on selected exchanges
            if selected_exchanges:
                df = df[df['exchange'].isin(selected_exchanges)]
            else:
                st.write("No exchanges selected. Displaying all exchanges.")

            # Aggregate volume per exchange for each coin
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
