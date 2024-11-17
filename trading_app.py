import streamlit as st
import numpy as np
import pandas as pd
from pycaret.classification import *

MODEL = load_model("spread_model")
HEDGE_RATIO = 0.39423664753972604
HISTORICAL_DF = pd.read_csv("MODEL_HISTORICAL")
print("Loaded Dataframe")
HISTORICAL_DF['date'] = pd.to_datetime(HISTORICAL_DF['date'], errors='coerce')
HISTORICAL_DF = HISTORICAL_DF.set_index('date').sort_index()
print(HISTORICAL_DF.head())

STATES = {
    1: {
        -1: "The spread is expanding, and is negative. Go short spread, or hold a short spread position",
        1: "The spread is expanding, and is positive. Go long spread, or hold a long spread position"
    },
    0: {
        -1: "The spread is contracting, and is negative. Go long spread, or hold a long spread position",
        1: "The spread is contracting, and is positive. Go short spread, or hold a short spread position"
    }
}

def create_row(asset_1_price, asset_2_price):

    new_row = pd.DataFrame({"XLP": [asset_1_price], "XLV": [asset_2_price]}, index=[pd.to_datetime("2024-11-16")])
    test_df = pd.concat([HISTORICAL_DF, new_row])

    asset1 = "XLP"
    asset2 = "XLV"

    # Calculate the spread
    test_df["spread"] = test_df[asset1] - HEDGE_RATIO * test_df[asset2]

    # Calculate the log price spread
    test_df["log_price_spread"] = np.log(test_df[asset1]) - np.log(test_df[asset2])

    # Calculate the price ratio
    test_df["price_ratio"] = test_df[asset1] / test_df[asset2]

    # Calculate the rolling correlation
    test_df["rolling_corr"] = test_df[asset1].rolling(window=30).corr(test_df[asset2])

    # Calculate the rolling mean of the spread
    test_df["rolling_spread_mean"] = test_df["spread"].rolling(window=30).mean()

    # Calculate the rolling standard deviation of the spread
    test_df["rolling_spread_std"] = test_df["spread"].rolling(window=30).std()

    return test_df.iloc[29:]



# Function to predict next values and generate trading signals
def predict_next_value(asset1, asset2):
    
    # Calculate the predicted spread
    predicted_spread = asset1 - HEDGE_RATIO * asset2

    next_spread = MODEL.predict(create_row(asset1, asset2))[0].astype(int)

    signal = STATES[next_spread][predicted_spread/predicted_spread]

    return predicted_spread, signal

# Streamlit App
def main():
    st.title("Pair Trading Signal Generator")
    st.markdown("""
    This app predicts calculates the current spread and predicts future spread direction of the XLP and XLV (S&P 500 Healthcare and Consumer Staples Sectors), and provides a trading signal.
    """)
    st.text(f"The latest date is {HISTORICAL_DF.index.max()}, and thus \nplease input predictions for the next day.")

    # Input fields for current asset values and hedge ratio
    asset1 = st.number_input("Enter the predicted value of XLP:", value=HISTORICAL_DF.loc[HISTORICAL_DF.index.max()].XLP)
    asset2 = st.number_input("Enter the predicted value of XLV:", value=HISTORICAL_DF.loc[HISTORICAL_DF.index.max()].XLV)

    # Predict next values and generate trading signal
    if st.button("Generate Signal"):
        predicted_spread, signal = predict_next_value(
            asset1, asset2
        )

        # Display results
        st.subheader("Prediction Results")
        st.write(f"Predicted Spread: {predicted_spread:.2f}")
        st.write(f"Trading Signal: **{signal}**")

if __name__ == "__main__":
    main()