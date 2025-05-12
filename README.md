# 📊 ETHWalletInsight - Ethereum Wallet Behavior Explorer

An interactive Ethereum wallet analytics dashboard built with **Python**, **Streamlit**, and **Plotly**.

This app enables users to explore Ethereum wallet activity, visualize ETH and ERC-20 token flows, and view AI-generated wallet summaries. It integrates data from public blockchain APIs and provides flexible, up-to-date insights.



## 🚀 Features

- 🔍 **Wallet Address Search** — Analyze any Ethereum wallet  
- 💸 **ETH & ERC-20 Token Support** — Token-specific charts and balances  
- 💱 **USD or Native Token Views** — Switch between price formats  
- 📈 **Interactive Visualizations** — Line charts, bar charts, and treemaps  
- 🧠 **AI-Powered Wallet Classification** — Classify wallets using Google Gemini  
- 🌐 **Live Token Pricing** — Uses CoinMarketCap API  
- 📊 **Top Receiver/Sender Treemaps** — View high-volume counterparties



## 🎥 Project Walkthrough

Example walkthrough using the “Bitfinex 2” wallet:
`0x742d35Cc6634C0532925a3b844Bc454e4438f44e`

![](assets/walkthrough.gif)

> **Note:** Due to the high transaction volume in this wallet, some charts may appear visually compressed or less readable. Chart behavior will vary depending on the nature of the wallet analyzed.



## 🛠️ Technologies Used

- `Python`  
- `Streamlit`  
- `Pandas`  
- `Plotly`  
- `Etherscan API`  
- `CoinMarketCap API`  
- `Google Gemini API`



## 📦 Setup

1. **Clone the repository**
```bash
git clone https://github.com/NicolasGarzon0/eth-wallet-explorer.git
cd eth-wallet-explorer
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Set up environment variables**
    
Create a .env file:
```bash
Etherscan_API_Key=your_etherscan_api_key
CoinMarketCap_API_Key=your_coinmarketcap_api_key
Gemini_API_Key=your_gemini_api_key
```

4. **Run the Streamlit app**
```bash
streamlit run main.py
```

---

## 🧪 Example Wallets
* Vitalik Buterin: `0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045`

* Robinhood: `0x40B38765696e3d5d8d9d834D8AaD4bB6e418E489` 

## 📄 License

This project is licensed under the [MIT License](LICENSE).
