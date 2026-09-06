import base64
import requests
import pandas as pd
import streamlit as st

# ---------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------
# Paste your Ximilar API Key between the quotes below
XIMILAR_API_TOKEN = "516125a196dc7b21ea312ddef4a60d05a3c0d4d8"
XIMILAR_ENDPOINT = "https://api.ximilar.com/collectibles/v2/sport_id"

# ---------------------------------------------------------
# MOBILE-FRIENDLY UI SETUP
# ---------------------------------------------------------
st.set_page_config(page_title="Card Scanner", layout="centered")

st.title("⚾ Sports Card Scanner & Price Finder")
st.write("Take a photo of a card to identify it and check eBay comps!")

# Camera input lets your son snap a photo directly on his phone
uploaded_file = st.camera_input("Take a picture of the card")

# If camera isn't preferred, allow photo selection from camera roll
if not uploaded_file:
    uploaded_file = st.file_uploader("...or upload from Photos", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # Read the image directly from memory
    bytes_data = uploaded_file.getvalue()
    encoded_string = base64.b64encode(bytes_data).decode("utf-8")

    if st.button("🔍 Scan & Get Comps", use_container_width=True):
        with st.spinner("Identifying card details..."):
            headers = {
                "Authorization": f"Token {XIMILAR_API_TOKEN}",
                "Content-Type": "application/json"
            }
            payload = {"records": [{"_base64": encoded_string}]}

            try:
                response = requests.post(XIMILAR_ENDPOINT, headers=headers, json=payload)
                raw_data = response.json()

                # Parse card details from Ximilar response
                obj = raw_data["records"][0]["_objects"][0]
                ident = obj["_identification"]
                match = ident.get("best_match", ident)

                player = match.get("name", "Unknown Player")
                year = match.get("year", "N/A")
                set_name = match.get("set_name", "N/A")
                card_num = match.get("card_number", "N/A")

                st.success(f"Identified: {player}")

                # Display card info in a compact table
                st.table(pd.DataFrame({
                    "Detail": ["Player", "Year", "Set", "Card #"],
                    "Info": [player, year, set_name, card_num]
                }))

                # Generate direct link to filtered eBay completed/sold sales
                query = f"{player} {year} {set_name} {card_num} sold".replace(" ", "+")
                ebay_url = f"https://www.ebay.com/sch/i.html?_nkw={query}&LH_Complete=1&LH_Sold=1"

                st.markdown("### 📊 Pricing Comps")
                st.link_button("👉 View Recent eBay Sold Listings", ebay_url)

            except Exception as e:
                st.error("Could not read card clearly. Try re-taking with better lighting.")
