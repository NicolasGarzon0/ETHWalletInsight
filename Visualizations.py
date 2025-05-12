# Imports
import wallet_utils
import plotly.express as px
import streamlit as st
import time

# Display ETH transaction charts, net flow, and AI summary in USD
def USD_Charts(Address,Apikey):
    chart_data = wallet_utils.GetWalletTransactions(Address, Apikey)[
        ["Date", "Transaction Value", "Transaction Fee"]
    ]
    chart_data = chart_data.set_index("Date")
    
    # --- USD Wallet Balance ---
    Balance = wallet_utils.GetWalletBalance(Address, Apikey)*wallet_utils.GetCurrentUSDETHPrice(Apikey)
    st.subheader(f"Wallet Balance: :blue[${Balance:,.2f} USD] ")
    
    # --- AI Wallet Summary ---
    age = wallet_utils.GetWalletAge(Address, Apikey)
    activity = wallet_utils.Gettxperday(Address, Apikey)
    volume = wallet_utils.GetVolume(Address, Apikey)
    
    Summary = wallet_utils.classify_wallet_with_gemini(age, activity, volume)
    
    st.subheader("AI Powered Wallet Summary", divider="blue")
    st.text(Summary)
    
    # --- Charts ---
    st.subheader("Charts", divider="blue")

    # --- USD Line Chart ---
    CurrentExchangeRate = wallet_utils.GetCurrentUSDETHPrice(Apikey)
    usd_data = chart_data.copy()
    usd_data["Transaction Value"] *= CurrentExchangeRate
    usd_data["Transaction Fee"]     *= CurrentExchangeRate

    fig_usd = px.line(
    usd_data,
    x=usd_data.index,
    y=["Transaction Value", "Transaction Fee"],
    labels={
        "value": " USD Volume",
        "Date": " Date ",
    },
    title="Transaction Values and Fees (USD)"
    )
    
    fig_usd.data[0].hovertemplate = "Date: %{x}<br>Value: %{y:.4f} USD<extra></extra>"
    fig_usd.data[1].hovertemplate = "Date: %{x}<br>Fee: %{y:.6f} USD<extra></extra>"
    
    fig_usd.update_traces(mode="lines+markers")
    st.plotly_chart(fig_usd, use_container_width=True)

    # --- USD Net-Flow Bar Chart ---
    net_eth = wallet_utils.GetWalletNetFlow(Address, Apikey)["Transaction Value"]
    net_usd = net_eth * CurrentExchangeRate
    fig_usd_net = px.bar(
    x=net_usd.index,
    y=net_usd.values,
    labels={"x": "Date", "y": "Net USD Value"},
    title="Daily Net Flow (USD)"
    )
    st.plotly_chart(fig_usd_net, use_container_width=True)

    # --- USD Treemaps ---
    tab1, tab2 = st.tabs(["Receivers", "Senders"])
    with tab1:
        top_recv = (
            wallet_utils.WalletTopReceiversSenders(Address, Apikey)
            .nlargest(10, "Incoming Transaction Values")
            .copy() 
        )

        top_recv["Incoming Transaction Values"] *=CurrentExchangeRate
        fig_recv = px.treemap(
            top_recv,
            path=["Wallet"],
            values="Incoming Transaction Values",
            color="Incoming Transaction Values",
            hover_data={"Incoming Transaction Values": ":,.2f"},
            title="Top 10 Addresses by ETH Received (In USD)"
        )
        fig_recv.update_traces(
            texttemplate="Address: %{label}<br>USD Received: %{value:,.2f}",
            hovertemplate="",
            hoverinfo="none"
        )
        st.plotly_chart(fig_recv, use_container_width=True)

    with tab2:
        top_send = (
            wallet_utils.WalletTopReceiversSenders(Address, Apikey)
            .nlargest(10, "Outgoing Transaction Values")
            .copy()
        )
        top_send["Outgoing Transaction Values"] *=CurrentExchangeRate
        fig_send = px.treemap(
            top_send,
            path=["Wallet"],
            values="Outgoing Transaction Values",
            color="Outgoing Transaction Values",
            hover_data={"Outgoing Transaction Values": ":,.2f"},
            title="Top 10 Addresses by ETH Sent (In USD)"
        )
        fig_send.update_traces(
            texttemplate="Address: %{label}<br>USD Sent: %{value:,.2f}",
            hovertemplate="",
            hoverinfo="none"
        )
        st.plotly_chart(fig_send, use_container_width=True)

# Display ETH transaction charts, net flow, and AI summary in ETH
def ETH_Charts(Address,Apikey):
    chart_data = wallet_utils.GetWalletTransactions(Address, Apikey)[
        ["Date", "Transaction Value", "Transaction Fee"]
    ]
    chart_data = chart_data.set_index("Date")
    
    # --- ETH Wallet Balance ---
    Balance = wallet_utils.GetWalletBalance(Address, Apikey)
    st.subheader(f"Wallet Balance: :blue[{Balance:,.6f} ETH] ")
    
    # --- AI Wallet Summary ---
    age = wallet_utils.GetWalletAge(Address, Apikey)
    activity = wallet_utils.Gettxperday(Address, Apikey)
    volume = wallet_utils.GetVolume(Address, Apikey)
    
    Summary = wallet_utils.classify_wallet_with_gemini(age, activity, volume)
    
    st.subheader("AI Powered Wallet Summary", divider="blue")
    st.text(Summary)
    
    # --- Charts ---
    st.subheader("Charts", divider="blue")
    
    # --- ETH Line Chart ---
    fig_eth = px.line(
    chart_data,
    x=chart_data.index,
    y=["Transaction Value", "Transaction Fee"],
    labels={
        "value": " ETH Volume",
        "Date": " Date ",
    },
    title="Transaction Values and Fees (ETH)"
    )
    
    fig_eth.data[0].hovertemplate = "Date: %{x}<br>Value: %{y:.4f} ETH<extra></extra>"
    fig_eth.data[1].hovertemplate = "Date: %{x}<br>Fee: %{y:.6f} ETH<extra></extra>"
    
    fig_eth.update_traces(mode="lines+markers")
    st.plotly_chart(fig_eth, use_container_width=True)

    # --- ETH Net-Flow Bar Chart ---
    net = wallet_utils.GetWalletNetFlow(Address, Apikey)
    fig_eth_net = px.bar(
    x=net.index,
    y=net["Transaction Value"],
    labels={"x": "Date", "y": "Net ETH Value"},
    title="Daily Net Flow (ETH)"
    )
    st.plotly_chart(fig_eth_net, use_container_width=True)

    # --- ETH Treemaps ---
    tab1, tab2 = st.tabs(["Receivers", "Senders"])
    with tab1:
        top_recv = (
            wallet_utils.WalletTopReceiversSenders(Address, Apikey)
            .nlargest(10, "Incoming Transaction Values")
            .copy()
        )
        fig_recv = px.treemap(
            top_recv,
            path=["Wallet"],
            values="Incoming Transaction Values",
            color="Incoming Transaction Values",
            hover_data={"Incoming Transaction Values": ":,.6f"},
            title="Top 10 Addresses by ETH Received (In ETH)"
        )
        fig_recv.update_traces(
            texttemplate="Address: %{label}<br>ETH Received: %{value:.6f}",
            hovertemplate="",
            hoverinfo="none"
        )
        st.plotly_chart(fig_recv, use_container_width=True)

    with tab2:
        top_send = (
            wallet_utils.WalletTopReceiversSenders(Address, Apikey)
            .nlargest(10, "Outgoing Transaction Values")
            .copy()
        )
        fig_send = px.treemap(
            top_send,
            path=["Wallet"],
            values="Outgoing Transaction Values",
            color="Outgoing Transaction Values",
            hover_data={"Outgoing Transaction Values": ":,.6f"},
            title="Top 10 Addresses by ETH Sent (In ETH)"
        )
        fig_send.update_traces(
            texttemplate="Address: %{label}<br>ETH Sent: %{value:,.6f}",
            hovertemplate="",
            hoverinfo="none"
        )
        st.plotly_chart(fig_send, use_container_width=True)

# Display ERC-20 balances and transaction charts by token in native units
def ERC_20_Charts(Address,Apikey):
    # --- ERC-20 Wallet Balance ---
    st.subheader("Wallet Balance Per Token")

    Tokens = wallet_utils.GetWalletERC20Transactions(Address, Apikey)
    token_df = Tokens[["Token Symbol", "Token Name", "Token Decimal", "Contract Address"]].drop_duplicates()

    cols = st.columns(2)  # You can increase to 3 or more if needed
    i = 0

    for _, token in token_df.iterrows():
        value = wallet_utils.Geterc_20WalletBalance(Address, token["Contract Address"], token["Token Decimal"], Apikey)
        time.sleep(0.25)
        if value != 0:
            with cols[i % len(cols)]:
                st.markdown(f"**{token['Token Name']}**  \n:blue[{value:,.6f} {token['Token Symbol']}]")
            i += 1
            
    # --- AI Wallet Summary ---
    age = wallet_utils.GetWalletAge(Address, Apikey)
    activity = wallet_utils.Gettxperday(Address, Apikey)
    volume = wallet_utils.GetVolume(Address, Apikey)
    
    Summary = wallet_utils.classify_wallet_with_gemini(age, activity, volume)
    
    st.subheader("AI Powered Wallet Summary", divider="blue")
    st.text(Summary)
    
    # --- Charts ---
    st.subheader("Charts", divider="blue")
            
    # --- ERC-20 Token Selector ---
    selected_token = st.selectbox("Select Token", Tokens["Token Symbol"].unique())
    df_filtered = Tokens[Tokens["Token Symbol"] == selected_token]        
            
    # --- ERC-20 Line Chart ---
    df = df_filtered[df_filtered["Transaction Value"] > 0].copy()
    df = df.set_index("Date")

    fig_erc_20 = px.line(
    df,
    x=df.index,
    y=["Transaction Value", "Transaction Fee"],
    labels={
        "value": f"{selected_token} Volume",
        "Date": " Date ",
    },
    title=f"Daily {selected_token} Token Transaction Volume"
    )
    
    fig_erc_20.data[0].hovertemplate = "Date: %{x}<br>Value: %{y:.4f}<extra></extra>" + f" {selected_token}"
    fig_erc_20.data[1].hovertemplate = "Date: %{x}<br>Fee: %{y:.6f} ETH<extra></extra>"
    
    fig_erc_20.update_traces(mode="lines+markers")
    st.plotly_chart(fig_erc_20, use_container_width=True)
    
    # --- ERC-20 Net-Flow Bar Chart ---
    net = wallet_utils.GetWalletERC20NetFlow(Address, Apikey)[[selected_token]] 
    fig_eth_net = px.bar(
    x=net.index,
    y=net[selected_token], 
    labels={"x": "Date", "y": f"Net {selected_token} Value"},
    title=f"Daily Net Flow ({selected_token})"
    )
    st.plotly_chart(fig_eth_net, use_container_width=True)
    
    # --- ERC-20 Treemaps ---
    tab1, tab2 = st.tabs(["Receivers", "Senders"])
    with tab1:
        top_recv = (
            wallet_utils.WalletERC20TopReceiversSenders(Address, Apikey, selected_token)
            .nlargest(10, "Incoming Transaction Values")
            .copy()
        )
        fig_recv = px.treemap(
            top_recv,
            path=["Wallet"],
            values="Incoming Transaction Values",
            color="Incoming Transaction Values",
            hover_data={"Incoming Transaction Values": ":,.6f"},
            title=f"Top 10 Addresses by {selected_token} Received (In {selected_token})"
        )
        fig_recv.update_traces(
            texttemplate="Address: %{label}<br>" + f"{selected_token}" + " Received: %{value:.6f}",
            hovertemplate="",
            hoverinfo="none"
        )
        st.plotly_chart(fig_recv, use_container_width=True)

    with tab2:
        top_send = (
            wallet_utils.WalletERC20TopReceiversSenders(Address, Apikey, selected_token)
            .nlargest(10, "Outgoing Transaction Values")
            .copy()
        )
        fig_send = px.treemap(
            top_send,
            path=["Wallet"],
            values="Outgoing Transaction Values",
            color="Outgoing Transaction Values",
            hover_data={"Outgoing Transaction Values": ":,.6f"},
            title=f"Top 10 Addresses by {selected_token} Sent (In {selected_token})"
        )
        fig_send.update_traces(
            texttemplate="Address: %{label}<br>" + f"{selected_token}" + " Sent: %{value:,.6f}",
            hovertemplate="",
            hoverinfo="none"
        )
        st.plotly_chart(fig_send, use_container_width=True)
    
# Display ERC-20 balances and transaction charts by token in USD
def ERC_20_Charts_USD(Address, Apikey):

    st.subheader("Wallet Balance Per Token (in USD)")

    Tokens = wallet_utils.GetWalletERC20Transactions(Address, Apikey)
    token_df = Tokens[["Token Symbol", "Token Name", "Token Decimal", "Contract Address"]].drop_duplicates()

    valid_tokens = []
    cols = st.columns(2)
    i = 0

    for _, token in token_df.iterrows():
        symbol = token["Token Symbol"]
        price = wallet_utils.GetTokenToUSDPrice(symbol)
        if price is None:
            continue

        value = wallet_utils.Geterc_20WalletBalance(Address, token["Contract Address"], token["Token Decimal"], Apikey)
        time.sleep(0.25)
        if value != 0:
            usd_value = value * price
            with cols[i % len(cols)]:
                st.markdown(f"**{token['Token Name']}**  \n:blue[${usd_value:,.2f} ({value:,.6f} {symbol})]")
            i += 1
            valid_tokens.append(symbol)

    if not valid_tokens:
        st.warning("No ERC-20 tokens with valid USD pricing found.")
        return

    # --- AI Wallet Summary ---
    age = wallet_utils.GetWalletAge(Address, Apikey)
    activity = wallet_utils.Gettxperday(Address, Apikey)
    volume = wallet_utils.GetVolume(Address, Apikey)
    
    Summary = wallet_utils.classify_wallet_with_gemini(age, activity, volume)
    
    st.subheader("AI Powered Wallet Summary", divider="blue")
    st.text(Summary)
    
    # --- Charts ---
    st.subheader("Charts", divider="blue")
    
    # --- ERC-20 (in USD) Token Selector ---
    selected_token = st.selectbox("Select Token", valid_tokens)
    price_usd = wallet_utils.GetTokenToUSDPrice(selected_token)
    df_filtered = Tokens[Tokens["Token Symbol"] == selected_token].copy()

    # --- ERC-20 (in USD) Line Chart ---
    df = df_filtered[df_filtered["Transaction Value"] > 0].copy()
    df["Transaction Value"] *= price_usd
    df["Transaction Fee"] *= price_usd
    df = df.set_index("Date")

    fig_erc_20 = px.line(
        df,
        x=df.index,
        y=["Transaction Value", "Transaction Fee"],
        labels={"value": f"{selected_token} in USD", "Date": "Date"},
        title=f"Daily {selected_token} Transaction Volume (in USD)"
    )

    fig_erc_20.data[0].hovertemplate = "Date: %{x}<br>Value: $%{y:,.2f}<extra></extra>"
    fig_erc_20.data[1].hovertemplate = "Date: %{x}<br>Fee: $%{y:,.2f}<extra></extra>"
    fig_erc_20.update_traces(mode="lines+markers")
    st.plotly_chart(fig_erc_20, use_container_width=True)

    # --- ERC-20 (in USD) Net-Flow Bar Chart ---
    net = wallet_utils.GetWalletERC20NetFlow(Address, Apikey)[[selected_token]].copy()
    net[selected_token] *= price_usd
    fig_eth_net = px.bar(
        x=net.index,
        y=net[selected_token],
        labels={"x": "Date", "y": f"Net {selected_token} Flow (USD)"},
        title=f"Daily Net Flow ({selected_token}) in USD"
    )
    st.plotly_chart(fig_eth_net, use_container_width=True)

    # --- ERC-20 (in USD) Treemaps ---
    tab1, tab2 = st.tabs(["Receivers", "Senders"])
    with tab1:
        top_recv = (
            wallet_utils.WalletERC20TopReceiversSenders(Address, Apikey, selected_token)
            .nlargest(10, "Incoming Transaction Values")
            .copy()
        )
        top_recv["Incoming Transaction Values"] *= price_usd
        fig_recv = px.treemap(
            top_recv,
            path=["Wallet"],
            values="Incoming Transaction Values",
            color="Incoming Transaction Values",
            hover_data={"Incoming Transaction Values": ":,.2f"},
            title=f"Top 10 Addresses by {selected_token} Received (in USD)"
        )
        fig_recv.update_traces(
            texttemplate="Address: %{label}<br>Received: $%{value:,.2f}",
            hovertemplate="",
            hoverinfo="none"
        )
        st.plotly_chart(fig_recv, use_container_width=True)

    with tab2:
        top_send = (
            wallet_utils.WalletERC20TopReceiversSenders(Address, Apikey, selected_token)
            .nlargest(10, "Outgoing Transaction Values")
            .copy()
        )
        top_send["Outgoing Transaction Values"] *= price_usd
        fig_send = px.treemap(
            top_send,
            path=["Wallet"],
            values="Outgoing Transaction Values",
            color="Outgoing Transaction Values",
            hover_data={"Outgoing Transaction Values": ":,.2f"},
            title=f"Top 10 Addresses by {selected_token} Sent (in USD)"
        )
        fig_send.update_traces(
            texttemplate="Address: %{label}<br>Sent: $%{value:,.2f}",
            hovertemplate="",
            hoverinfo="none"
        )
        st.plotly_chart(fig_send, use_container_width=True)

