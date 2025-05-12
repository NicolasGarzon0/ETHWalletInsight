# Imports
import requests
import pandas as pd
import re
import os
import time
from datetime import datetime
from google import genai
from google.genai import types
from dotenv import load_dotenv, find_dotenv

# Load environment variables from .env file
dotenv_path = find_dotenv()  
if dotenv_path:
    load_dotenv(dotenv_path)
else:
    raise FileNotFoundError(".env file not found. Please ensure it's present in the project directory.")

# Retrieve API keys from environment
Gemini_API_Key = os.getenv("Gemini_API_Key")
CoinMarketCap_API_Key = os.getenv("CoinMarketCap_API_Key")

# Use Gemini to classify wallet type and generate a reputation summary
def classify_wallet_with_gemini(age, activity, volume):
    if not Gemini_API_Key:
        raise ValueError("Missing Gemini API Key")

    client = genai.Client(api_key=Gemini_API_Key)

    prompt = f"""
    You are analyzing an Ethereum wallet using the following metrics:
    - Wallet age: {age} days
    - Average transactions per day: {activity:.2f}
    - Total ETH volume moved: {volume:.2f} ETH

    Classify the wallet using the following rules:
    - HODLer: Tx/Day < 1
    - Trader: Volume between 1000 and 8000 ETH or Tx/Day between 1 and 50
    - Whale: Volume > 8000 ETH or Tx/Day > 50  
    
    If the metrics fall near the edges of these categories, use your best judgment to decide the most appropriate label based on the overall behavior.

    Assign a reputation score from 0 to 100 based on wallet age, activity, and ETH volume.

    Write a concise summary (1-2 sentences) that includes:
    - The wallet type
    - The reputation score
    - A brief explanation of why the wallet was classified that way
    Use clear and human-friendly language.
    - Don't use bold letters
    - Dont add on your summary the wallet age, Average transactions per day, nor the Total ETH volume moved
    """

    contents = [
        types.Content(
            role="user",
            parts=[types.Part.from_text(text=prompt)]
        )
    ]

    config = types.GenerateContentConfig(
        temperature=0,
        max_output_tokens=500,
        response_mime_type="text/plain"
    )

    response = client.models.generate_content(
        model="gemini-1.5-flash",
        contents=contents,
        config=config,
    )

    return response.candidates[0].content.parts[0].text

# Get the ETH balance of a wallet
def GetWalletBalance(Address, Apikey):
    r = requests.get(f"https://api.etherscan.io/api?module=account&action=balance&address={Address}&tag=latest&apikey={Apikey}")
    return float(r.json()["result"])/ 1e18

# Get the current ETH-USD exchange rate
def GetCurrentUSDETHPrice(Apikey):
    r = requests.get(f"https://api.etherscan.io/api?module=stats&action=ethprice&apikey={Apikey}")
    return float(r.json()["result"]["ethusd"])

# Retrieve normal ETH transactions
def GetWalletTransactions(Address, Apikey):
    WalletTransactions = []
    page = 1
    max_txs = 10000  

    while True:
        url = (
            f"https://api.etherscan.io/api?module=account&action=txlist"
            f"&address={Address}&startblock=0&endblock=99999999"
            f"&page={page}&offset={max_txs}&sort=asc&apikey={Apikey}"
        )
        r = requests.get(url)
        
        if r.status_code != 200:
            print("API request failed:", r.status_code)
            return None

        transactions = r.json().get("result", [])
        
        if not transactions:
            break

        for tx in transactions:
            if tx["input"] == "0x" and tx["value"] != "0":
                WalletTransactions.append({
                    'Transaction Hash': tx['hash'],
                    'From': tx['from'],
                    'To': tx['to'],
                    'Transaction Value': int(tx['value']) / 1e18,
                    'Transaction Fee': (int(tx['gasPrice']) * int(tx['gasUsed'])) / 1e18,
                    'Date': pd.to_datetime(int(tx['timeStamp']), unit='s').strftime('%Y-%m-%d')
                })

        if len(transactions) < max_txs:
            break

        page += 1
        time.sleep(0.25)  

    return pd.DataFrame(WalletTransactions)

# Compute daily ETH net flow (inflow - outflow)
def GetWalletNetFlow(Address, Apikey):
    Df_WalletTransactions = pd.DataFrame(GetWalletTransactions(Address, Apikey))

    Df_WalletTransactions['Date'] = pd.to_datetime(Df_WalletTransactions['Date'])
    out = (Df_WalletTransactions
        .loc[Df_WalletTransactions['From'].str.lower()==Address.lower()]
        .groupby(Df_WalletTransactions['Date'].dt.date)
        .sum(numeric_only=True))
    inc = (Df_WalletTransactions
        .loc[Df_WalletTransactions['To'].str.lower()==Address.lower()]
        .groupby(Df_WalletTransactions['Date'].dt.date)
        .sum(numeric_only=True))
    
    out.index = pd.to_datetime(out.index)
    inc.index = pd.to_datetime(inc.index)
    
    diff = out.subtract(inc, fill_value=0)
    
    return diff[['Transaction Value']]

# Get top senders and receivers of ETH
def WalletTopReceiversSenders(Address, Apikey):
    Df_WalletTransactions = GetWalletTransactions(Address, Apikey).loc[:, ["From", "To", "Transaction Value"]]

    out = (Df_WalletTransactions
            .loc[Df_WalletTransactions['From'].str.lower()==Address.lower()]
            .groupby(Df_WalletTransactions['To'])
            .sum(numeric_only=True).reset_index())

    inc = (Df_WalletTransactions
            .loc[Df_WalletTransactions['To'].str.lower()==Address.lower()]
            .groupby(Df_WalletTransactions['From'])
            .sum(numeric_only=True).reset_index())

    inc = inc.rename(columns={'From': 'Wallet', 'Transaction Value': 'Incoming Transaction Values'})
    out = out.rename(columns={'To': 'Wallet', 'Transaction Value': 'Outgoing Transaction Values'})

    MergedTransactions = pd.merge(out, inc, on='Wallet', how='outer')
    MergedTransactions = MergedTransactions.fillna(0)
    
    return MergedTransactions

# Get ERC-20 token balance of a specific contract for a wallet
def Geterc_20WalletBalance(Address, TokenAddress, TokenDecimal, Apikey):
    r = requests.get(f"https://api.etherscan.io/api?module=account&action=tokenbalance&contractaddress={TokenAddress}&address={Address}&tag=latest&apikey={Apikey}")
    return float(r.json()["result"]) / (10 ** int(TokenDecimal))

# Get live token-to-USD price using CoinMarketCap
def GetTokenToUSDPrice(symbol):
    if not symbol or not re.match(r'^[A-Za-z0-9]+$', symbol):
        print(f"Skipping invalid token symbol: {symbol}")
        return None

    url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest"
    parameters = {
        'symbol': symbol.upper(),
        'convert': 'USD'
    }
    headers = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': CoinMarketCap_API_Key,
    }

    response = requests.get(url, headers=headers, params=parameters)
    data = response.json()

    try:
        price = data['data'][symbol.upper()]['quote']['USD']['price']
        return round(float(price), 6) if price is not None else None
    except KeyError:
        print("Error in response:", data)
        return None

# Get all ERC-20 token transfers with pagination
def GetWalletERC20Transactions(Address, Apikey):
    WalletERC20Transactions = []
    page = 1
    max_txs = 10000  

    while True:
        url = (
            f"https://api.etherscan.io/api?module=account&action=tokentx"
            f"&address={Address}&page={page}&offset={max_txs}"
            f"&startblock=0&endblock=99999999&sort=asc&apikey={Apikey}"
        )
        r = requests.get(url)

        if r.status_code != 200:
            print("API request failed:", r.status_code)
            return None

        transactions = r.json().get("result", [])

        if not transactions:
            break

        for tx in transactions:
            if tx["value"] != "0":
                WalletERC20Transactions.append({
                    'Transaction Hash': tx['hash'],
                    'From': tx['from'],
                    'To': tx['to'],
                    'Token Symbol': tx['tokenSymbol'],
                    'Token Name': tx['tokenName'],
                    'Token Decimal': tx['tokenDecimal'],
                    'Contract Address': tx['contractAddress'],
                    'Transaction Value': int(tx['value']) / (10 ** int(tx['tokenDecimal'])),
                    'Transaction Fee': (int(tx['gasPrice']) * int(tx['gasUsed'])) / 1e18,
                    'Date': pd.to_datetime(int(tx['timeStamp']), unit='s').strftime('%Y-%m-%d')
                })

        if len(transactions) < max_txs:
            break

        page += 1
        time.sleep(0.25)  

    return pd.DataFrame(WalletERC20Transactions)

# Compute ERC-20 net flow by token symbol
def GetWalletERC20NetFlow(Address, Apikey):
    df = GetWalletERC20Transactions(Address, Apikey)
    if df is None or df.empty:
        return pd.DataFrame()

    df['Date'] = pd.to_datetime(df['Date'])
    addr = Address.lower()

    out = (
        df[df['From'].str.lower() == addr]
        .groupby([df['Date'].dt.date, 'Token Symbol'])['Transaction Value']
        .sum()
        .unstack(fill_value=0)
    )

    inc = (
        df[df['To'].str.lower() == addr]
        .groupby([df['Date'].dt.date, 'Token Symbol'])['Transaction Value']
        .sum()
        .unstack(fill_value=0)
    )

    out.index = pd.to_datetime(out.index)
    inc.index = pd.to_datetime(inc.index)

    net_flow = out.subtract(inc, fill_value=0)

    return net_flow

# Get top receivers/senders of a specific ERC-20 token
def WalletERC20TopReceiversSenders(Address, Apikey, token):
    df = GetWalletERC20Transactions(Address, Apikey)
    if df is None or df.empty: 
        return pd.DataFrame(columns=['Wallet','Outgoing Transaction Values','Incoming Transaction Values'])
    df = df[df['Token Symbol']==token]
    addr = Address.lower()
    out = df[df['From'].str.lower()==addr] \
        .groupby('To')['Transaction Value'].sum() \
        .nlargest(10) \
        .reset_index(name='Outgoing Transaction Values') \
        .rename(columns={'To':'Wallet'})
    inc = df[df['To'].str.lower()==addr] \
        .groupby('From')['Transaction Value'].sum() \
        .nlargest(10) \
        .reset_index(name='Incoming Transaction Values') \
        .rename(columns={'From':'Wallet'})
    return pd.merge(out, inc, on='Wallet', how='outer').fillna(0)

# Get wallet age in days based on first transaction timestamp
def GetWalletAge(Address, Apikey):
    r = requests.get(
        f"https://api.etherscan.io/api?module=account&action=txlist"
        f"&address={Address}&startblock=0&endblock=99999999"
        f"&page=1&offset=1&sort=asc&apikey={Apikey}"
    )
    transaction = r.json()["result"]
    
    if not transaction:
        return 0

    creation_time = datetime.fromtimestamp(int(transaction[0]['timeStamp']))
    
    Age = (datetime.now() - creation_time).days

    return Age

# Calculate average number of transactions per day
def Gettxperday(Address, Apikey):
    num_txns = (len(GetWalletTransactions(Address, Apikey)))
    wallet_age_days = GetWalletAge(Address, Apikey) 
    if wallet_age_days > 0:
        return num_txns / wallet_age_days
    else:
        return 0
    
# Calculate total ETH volume moved by the wallet
def GetVolume(Address, Apikey):
    return GetWalletTransactions(Address, Apikey)['Transaction Value'].sum()

