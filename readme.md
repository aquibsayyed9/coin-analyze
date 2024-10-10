# Coin-Compare

This project provides an easy-to-use web application for comparing cryptocurrency trading volumes across multiple exchanges. It leverages both the **CoinMarketCap API** (Pro version recommended) and the **Binance API**, with the option to bypass region-based restrictions using **ScraperAPI**.

### Features:
- Compare cryptocurrency trading volumes across multiple exchanges.
- Visualize data through bar charts, pie charts, and detailed tables.
- Option to use **ScraperAPI** for Binance data to avoid region blocks.
- Fetch exchange-specific trading data from **CoinMarketCap** (Pro API key required).

---

## Screenshot

![App Screenshot](./assets/screenshot.png)

---

## Getting Started

### Prerequisites
To run this project locally, you’ll need the following:
- **Python 3.8+**
- **Streamlit** for building the web app
- API keys for:
  - [CoinMarketCap](https://pro.coinmarketcap.com/signup/)
  - [ScraperAPI](https://www.scraperapi.com/) (if Binance API is blocked in your region)

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-repo/coin-compare.git
   cd coin-compare
   ```
2. **Install the required dependencies**: 
    Ensure you have pip installed, then run:
    ```
    pip install -r requirements.txt
    
    ```
3. **Set up secrets**: 
    Create a secrets.toml file in the .streamlit/ folder. If the folder doesn't exist, create it.
    example
    ```
    [coinmarketcap]
    api_key = "your_coinmarketcap_api_key_here"

    [scraper]
    api_key = "your_scraperapi_key_here"
    ```

### Running the app
    After installing dependencies and setting up your API keys, run the Streamlit app using the following command:
    ```
    streamlit run binance-api.py

    ```
    You should see an output similar to:
    ```
        You can now view your Streamlit app in your browser.
  
        Local URL: http://localhost:8501
        Network URL: http://your_network_ip:8501

    ```
    Open the local URL in your browser to access the app.

### Usage
    Select Coins: Choose the cryptocurrencies you want to compare from the dropdown menu.

    Select Exchanges: After selecting coins, you can pick the exchanges you want to compare. If no exchange is selected, data for all exchanges will be displayed.

    Enable ScraperAPI (Optional): If Binance API is blocked in your region, enable the ScraperAPI option to bypass the restriction.

    Visualizations:

    Bar Chart: Compare the 24-hour trading volume across exchanges.
    Pie Chart: View the distribution of trading volumes by coin for each exchange.
    Data Table: Explore the raw data in a detailed table.
