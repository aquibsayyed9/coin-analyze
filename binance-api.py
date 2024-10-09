import requests
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Get API keys from Streamlit secrets
API_KEY = st.secrets["coinmarketcap"]["api_key"]
SCRAPER_API_KEY = st.secrets["scraper"]["api_key"]

# Function to get top coins from CoinMarketCap
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

# Function to get exchange-wise trading volume for a specific coin from CoinMarketCap
def get_exchange_data_cmc(coin_id):
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

# Function to get trading volume from Binance using ScraperAPI
def get_binance_trading_volume(symbol, use_scraperapi=False):
    if use_scraperapi:
        # Use ScraperAPI to proxy the Binance request
        scraperapi_url = "http://api.scraperapi.com"
        target_url = f"https://api.binance.com/api/v3/ticker/24hr?symbol={symbol}"
        params = {
            'api_key': SCRAPER_API_KEY,  # ScraperAPI key
            'url': target_url  # Binance API target URL
        }
    else:
        # Direct request to Binance API
        url = "https://api.binance.com/api/v3/ticker/24hr"
        params = {
            'symbol': symbol
        }
    
    try:
        # Handle both direct and ScraperAPI requests
        if use_scraperapi:
            response = requests.get(scraperapi_url, params=params)
        else:
            response = requests.get(url, params=params)

        response.raise_for_status()
        data = response.json()
        return data['volume']  # 24-hour trading volume
    except requests.exceptions.RequestException as e:
        st.error(f"An error occurred while fetching data for {symbol}: {e}")
        return None

# Function to aggregate exchange volumes for a coin from CMC
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

# Mapping for Binance pairs (fallback if CMC Pro is unavailable)
binance_pairs = {
    'Bitcoin': 'BTCUSDT',
    'Ethereum': 'ETHUSDT',
    'Tether USDt': 'BTCUSDT',  # Using BTCUSDT for Tether
    'Binance Coin': 'BNBUSDT',
    'Solana': 'SOLUSDT'
}

# Fetch top coins for selection from CoinMarketCap
top_coins = get_top_coins_cmc()

if top_coins:
    # Create a dictionary mapping coin names to their data
    coin_info = {coin['name']: coin for coin in top_coins}

    # Display available coins for selection
    selected_coins = st.multiselect("Select Coins", list(coin_info.keys()), default=list(coin_info.keys())[:5])

    if selected_coins:
        st.write("Fetching data for selected coins...")

        # Allow users to decide if they want to use ScraperAPI
        use_scraper = st.checkbox("Use ScraperAPI for Binance requests (if region blocked)?", value=False)

        # Initialize a list to hold all trading volume data
        all_volumes = []

        for coin in selected_coins:
            coin_name = coin
            coin_id = coin_info[coin_name]['id']

            # If using CMC Pro, fetch exchange-specific data
            market_pairs = get_exchange_data_cmc(coin_id)
            if market_pairs:
                exchange_volumes = aggregate_exchange_volumes(market_pairs, coin_name)
                all_volumes.extend(exchange_volumes)
            else:
                # Fallback to Binance if CMC Pro is not available
                binance_pair = binance_pairs.get(coin_name, None)
                if binance_pair:
                    volume = get_binance_trading_volume(binance_pair, use_scraperapi=use_scraper)
                    if volume:
                        all_volumes.append({
                            'coin': coin_name,
                            'exchange': 'Binance',
                            'volume_24h': float(volume)  # Convert to float for plotting
                        })

        # Convert to DataFrame
        if all_volumes:
            df = pd.DataFrame(all_volumes)

            # Get the list of exchanges
            all_exchanges = df['exchange'].unique().tolist()

            # Exchange selection
            selected_exchanges = st.multiselect("Select Exchanges", all_exchanges, default=all_exchanges[:5])

            # Filter the DataFrame based on selected exchanges
            if selected_exchanges:
                df = df[df['exchange'].isin(selected_exchanges)]
            else:
                st.write("No exchanges selected. Displaying all exchanges.")

            # Bar Chart: Exchange-wise 24h Trading Volume for Selected Coins
            st.write("### Exchange-wise 24h Trading Volume for Selected Coins")
            st.bar_chart(df.pivot_table(values='volume_24h', index='exchange', columns='coin', aggfunc='sum'))

            # Pie Chart: Volume Distribution by Coin (per exchange)
            st.write("### Volume Distribution by Coin and Exchange")
            for exchange in selected_exchanges:
                fig, ax = plt.subplots()
                df[df['exchange'] == exchange].set_index('coin')['volume_24h'].plot.pie(autopct="%.1f%%", ax=ax)
                ax.set_ylabel('')
                st.pyplot(fig)

            # Display the raw data as a table
            st.write("#### Detailed Trading Volume Data")
            st.dataframe(df)

        else:
            st.write("No volume data available for the selected coins.")
else:
    st.error("No coin data available for selection.")
