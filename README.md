# PinkCityEstate.in CRM Portal

**Real Estate CRM for Jaipur Properties**

## Features
- 🏠 Property Management (Flats, Plots, Villas, Commercial)
- 👤 Buyer Tracking with Requirements
- 🏢 Seller Management
- 🎁 Wrapper/Referral System with Rewards
- 🔍 Smart Search & Auto-Matching
- 📊 Dashboard Analytics
- 📥 Excel Export

## Local Setup

1. Install dependencies:
```bash
pip install streamlit pandas openpyxl
```

2. Run locally:
```bash
streamlit run app.py
```

## Deploy to Streamlit Cloud (Online)

### Step 1: Create GitHub Account
1. Go to https://github.com
2. Sign up with email
3. Create new repository named `pinkcityestate-crm`

### Step 2: Upload Files
Upload these files to your GitHub repo:
- `app.py`
- `requirements.txt`
- `.streamlit/config.toml`
- `README.md` (this file)

### Step 3: Deploy on Streamlit Cloud
1. Go to https://streamlit.io/cloud
2. Sign in with GitHub
3. Click "New app"
4. Select your `pinkcityestate-crm` repository
5. Click "Deploy"

### Step 4: Your App Will Be Live At:
```
https://pinkcityestate-crm-yourusername.streamlit.app
```

The browser tab will show: **"PinkCityEstate.in CRM Portal"**

## Data Storage
- Data is stored in JSON files (properties.json, buyers.json, etc.)
- In Streamlit Cloud, data persists between sessions
- Regular exports recommended for backup

## Support
For questions, contact PinkCityEstate.in
