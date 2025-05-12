# Imports
import Visualizations  
import streamlit as st 
import os
from dotenv import load_dotenv, find_dotenv  

# Load environment variables from .env file
dotenv_path = find_dotenv()  
if dotenv_path:
    load_dotenv(dotenv_path)
else:
    raise FileNotFoundError(".env file not found. Please ensure it's present in the project directory.")

# Get Etherscan API key from environment
Etherscan_API_Key = os.getenv("Etherscan_API_Key")

# Streamlit app title
st.title("Ethereum Wallet Behavior Explorer")

# Input field for Ethereum wallet address
Address = st.text_input("Enter Wallet Address:")

if Address:
    # Dropdown to choose between ETH and ERC-20 tokens
    asset_type = st.selectbox(
        "Select Asset Type",
        [None, "ETH", "ERC-20"],
        format_func=lambda x: "— select asset type —" if x is None else x,
        key="asset_type_select"
    )

    if asset_type is None:
        st.info("🔍 Please select an asset type above to continue.")
    else:
        # Dropdown to select value display format: USD or native token
        display_value = st.selectbox(
            "Display Values In",
            [None, "USD", "Token"],
            format_func=lambda x: "— select value format —" if x is None else x,
            key="display_value_select"
        )

        if display_value is None:
            st.info("🔍 Please select a value format above to load the charts.")
        else:
            # Render appropriate visualizations based on asset type and display value
            if asset_type == "ETH":
                if display_value == "USD":
                    Visualizations.USD_Charts(Address, Etherscan_API_Key)
                elif display_value == "Token":
                    Visualizations.ETH_Charts(Address, Etherscan_API_Key)
            elif asset_type == "ERC-20":
                if display_value == "USD":
                    Visualizations.ERC_20_Charts_USD(Address, Etherscan_API_Key)
                elif display_value == "Token":
                    Visualizations.ERC_20_Charts(Address, Etherscan_API_Key)
else:
    st.info("🔍 Please enter a valid Ethereum address above.")
