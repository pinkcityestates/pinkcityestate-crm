"""
PinkCityEstate.in - Real Estate CRM
====================================
Streamlit web application for property management
Features: Properties, Buyers, Sellers, Wrappers, Search & Match
"""

import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime

# Page config
st.set_page_config(
    page_title="PinkCityEstate.in CRM Portal",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Data files
DATA_DIR = r"c:\Users\ashok\OneDrive\Documents\Automation Test 1\PinkCityEstate.in\data"
PROPERTIES_FILE = os.path.join(DATA_DIR, "properties.json")
BUYERS_FILE = os.path.join(DATA_DIR, "buyers.json")
SELLERS_FILE = os.path.join(DATA_DIR, "sellers.json")
WRAPPERS_FILE = os.path.join(DATA_DIR, "wrappers.json")

# Ensure data directory exists
os.makedirs(DATA_DIR, exist_ok=True)

# Initialize data
def load_data(file_path, default_data):
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            return json.load(f)
    return default_data

def save_data(file_path, data):
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2)

# Load all data
properties = load_data(PROPERTIES_FILE, [])
buyers = load_data(BUYERS_FILE, [])
sellers = load_data(SELLERS_FILE, [])
wrappers = load_data(WRAPPERS_FILE, [])

# Sidebar navigation
st.sidebar.title("🏠 PinkCityEstate.in")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigation",
    ["📋 Dashboard", "🏘️ Properties", "👤 Buyers", "🏢 Sellers", "🎁 Wrappers", "🔍 Search & Match"]
)

# Dashboard Page
if page == "📋 Dashboard":
    st.title("📋 Dashboard")
    st.markdown("---")
    
    # Stats cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Properties", len(properties))
    with col2:
        active_buyers = len([b for b in buyers if b.get('status') == 'Active'])
        st.metric("Active Buyers", active_buyers)
    with col3:
        active_sellers = len([s for s in sellers if s.get('status') == 'Active'])
        st.metric("Active Sellers", active_sellers)
    with col4:
        total_wrappers = len(wrappers)
        st.metric("Total Wrappers", total_wrappers)
    
    st.markdown("---")
    
    # Recent properties
    st.subheader("🏘️ Recent Properties")
    if properties:
        df_props = pd.DataFrame(properties[-5:])  # Last 5
        st.dataframe(df_props, use_container_width=True)
    else:
        st.info("No properties added yet.")
    
    # Active buyers
    st.subheader("👤 Active Buyers")
    if buyers:
        df_buyers = pd.DataFrame([b for b in buyers if b.get('status') == 'Active'])
        if not df_buyers.empty:
            st.dataframe(df_buyers, use_container_width=True)
        else:
            st.info("No active buyers.")
    else:
        st.info("No buyers added yet.")

# Properties Page
elif page == "🏘️ Properties":
    st.title("🏘️ Properties Management")
    st.markdown("---")
    
    # Add new property form
    with st.expander("➕ Add New Property", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            prop_id = st.text_input("Property ID", value=f"PROP{len(properties)+1:03d}")
            prop_type = st.selectbox("Property Type", ["Flat", "Plot", "Villa", "Commercial", "Office"])
            location = st.text_input("Location")
            area_sqft = st.number_input("Area (sq ft)", min_value=0, value=1000)
            
        with col2:
            price = st.number_input("Price (₹)", min_value=0, value=5000000)
            bedrooms = st.selectbox("Bedrooms", ["Studio", "1 BHK", "2 BHK", "3 BHK", "4 BHK", "5+ BHK"])
            furnished = st.selectbox("Furnished", ["Yes", "No", "Semi"])
            status = st.selectbox("Status", ["Available", "Sold", "Rented", "Under Negotiation"])
        
        owner_name = st.text_input("Owner Name")
        owner_contact = st.text_input("Owner Contact")
        wrapper_name = st.text_input("Wrapper/Referrer Name (if any)")
        wrapper_reward = st.number_input("Wrapper Reward (₹)", min_value=0, value=0)
        remarks = st.text_area("Remarks")
        
        if st.button("💾 Save Property", type="primary"):
            new_property = {
                "id": prop_id,
                "type": prop_type,
                "location": location,
                "area_sqft": area_sqft,
                "price": price,
                "bedrooms": bedrooms,
                "furnished": furnished,
                "status": status,
                "owner_name": owner_name,
                "owner_contact": owner_contact,
                "wrapper_name": wrapper_name,
                "wrapper_reward": wrapper_reward,
                "remarks": remarks,
                "date_added": datetime.now().strftime("%Y-%m-%d")
            }
            properties.append(new_property)
            save_data(PROPERTIES_FILE, properties)
            st.success(f"✅ Property {prop_id} added successfully!")
            st.rerun()
    
    st.markdown("---")
    
    # View all properties
    st.subheader("📋 All Properties")
    if properties:
        df = pd.DataFrame(properties)
        
        # Filters
        col1, col2, col3 = st.columns(3)
        with col1:
            type_filter = st.multiselect("Filter by Type", options=df['type'].unique() if 'type' in df.columns else [])
        with col2:
            status_filter = st.multiselect("Filter by Status", options=df['status'].unique() if 'status' in df.columns else [])
        with col3:
            location_filter = st.text_input("Search Location")
        
        # Apply filters
        filtered_df = df.copy()
        if type_filter:
            filtered_df = filtered_df[filtered_df['type'].isin(type_filter)]
        if status_filter:
            filtered_df = filtered_df[filtered_df['status'].isin(status_filter)]
        if location_filter:
            filtered_df = filtered_df[filtered_df['location'].str.contains(location_filter, case=False, na=False)]
        
        st.dataframe(filtered_df, use_container_width=True)
        
        # Export
        if st.button("📥 Export to Excel"):
            excel_path = os.path.join(DATA_DIR, f"properties_{datetime.now().strftime('%Y%m%d')}.xlsx")
            filtered_df.to_excel(excel_path, index=False)
            st.success(f"Exported to {excel_path}")
    else:
        st.info("No properties added yet. Click 'Add New Property' above.")

# Buyers Page
elif page == "👤 Buyers":
    st.title("👤 Buyers Management")
    st.markdown("---")
    
    # Add new buyer
    with st.expander("➕ Add New Buyer", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            buyer_id = st.text_input("Buyer ID", value=f"BUY{len(buyers)+1:03d}")
            buyer_name = st.text_input("Buyer Name")
            buyer_contact = st.text_input("Contact Number")
            buyer_email = st.text_input("Email")
            
        with col2:
            budget_min = st.number_input("Budget Min (₹)", min_value=0, value=3000000)
            budget_max = st.number_input("Budget Max (₹)", min_value=0, value=10000000)
            type_needed = st.selectbox("Property Type Needed", ["Flat", "Plot", "Villa", "Commercial", "Any"])
            preferred_location = st.text_input("Preferred Location")
        
        requirements = st.text_area("Requirements (BHK, Area, etc.)")
        status = st.selectbox("Status", ["Active", "Closed", "On Hold"])
        follow_up_date = st.date_input("Follow-up Date")
        remarks = st.text_area("Remarks")
        
        if st.button("💾 Save Buyer", type="primary"):
            new_buyer = {
                "id": buyer_id,
                "name": buyer_name,
                "contact": buyer_contact,
                "email": buyer_email,
                "budget_min": budget_min,
                "budget_max": budget_max,
                "type_needed": type_needed,
                "preferred_location": preferred_location,
                "requirements": requirements,
                "status": status,
                "follow_up_date": follow_up_date.strftime("%Y-%m-%d"),
                "remarks": remarks,
                "date_added": datetime.now().strftime("%Y-%m-%d")
            }
            buyers.append(new_buyer)
            save_data(BUYERS_FILE, buyers)
            st.success(f"✅ Buyer {buyer_name} added successfully!")
            st.rerun()
    
    st.markdown("---")
    
    # View buyers
    st.subheader("📋 All Buyers")
    if buyers:
        df = pd.DataFrame(buyers)
        
        # Filters
        col1, col2 = st.columns(2)
        with col1:
            status_filter = st.multiselect("Filter by Status", options=df['status'].unique() if 'status' in df.columns else [])
        with col2:
            type_filter = st.multiselect("Filter by Type Needed", options=df['type_needed'].unique() if 'type_needed' in df.columns else [])
        
        filtered_df = df.copy()
        if status_filter:
            filtered_df = filtered_df[filtered_df['status'].isin(status_filter)]
        if type_filter:
            filtered_df = filtered_df[filtered_df['type_needed'].isin(type_filter)]
        
        st.dataframe(filtered_df, use_container_width=True)
    else:
        st.info("No buyers added yet.")

# Sellers Page
elif page == "🏢 Sellers":
    st.title("🏢 Sellers Management")
    st.markdown("---")
    
    # Add new seller
    with st.expander("➕ Add New Seller", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            seller_id = st.text_input("Seller ID", value=f"SEL{len(sellers)+1:03d}")
            seller_name = st.text_input("Seller Name")
            seller_contact = st.text_input("Contact Number")
            seller_email = st.text_input("Email")
            
        with col2:
            property_type = st.selectbox("Property Type to Sell", ["Flat", "Plot", "Villa", "Commercial", "Multiple"])
            location = st.text_input("Property Location")
            expected_price = st.number_input("Expected Price (₹)", min_value=0, value=5000000)
            urgency = st.selectbox("Urgency", ["High", "Medium", "Low"])
        
        status = st.selectbox("Status", ["Active", "Sold", "On Hold"])
        remarks = st.text_area("Remarks")
        
        if st.button("💾 Save Seller", type="primary"):
            new_seller = {
                "id": seller_id,
                "name": seller_name,
                "contact": seller_contact,
                "email": seller_email,
                "property_type": property_type,
                "location": location,
                "expected_price": expected_price,
                "urgency": urgency,
                "status": status,
                "remarks": remarks,
                "date_added": datetime.now().strftime("%Y-%m-%d")
            }
            sellers.append(new_seller)
            save_data(SELLERS_FILE, sellers)
            st.success(f"✅ Seller {seller_name} added successfully!")
            st.rerun()
    
    st.markdown("---")
    
    # View sellers
    st.subheader("📋 All Sellers")
    if sellers:
        df = pd.DataFrame(sellers)
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No sellers added yet.")

# Wrappers Page
elif page == "🎁 Wrappers":
    st.title("🎁 Wrapper/Referral Management")
    st.markdown("---")
    
    # Add new wrapper
    with st.expander("➕ Add New Wrapper", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            wrapper_id = st.text_input("Wrapper ID", value=f"WRP{len(wrappers)+1:03d}")
            wrapper_name = st.text_input("Wrapper Name")
            wrapper_contact = st.text_input("Contact Number")
            
        with col2:
            properties_referred = st.number_input("Properties Referred", min_value=0, value=1)
            total_reward = st.number_input("Total Reward Earned (₹)", min_value=0, value=0)
            status = st.selectbox("Status", ["Active", "Inactive"])
        
        remarks = st.text_area("Remarks")
        
        if st.button("💾 Save Wrapper", type="primary"):
            new_wrapper = {
                "id": wrapper_id,
                "name": wrapper_name,
                "contact": wrapper_contact,
                "properties_referred": properties_referred,
                "total_reward": total_reward,
                "status": status,
                "remarks": remarks,
                "date_added": datetime.now().strftime("%Y-%m-%d")
            }
            wrappers.append(new_wrapper)
            save_data(WRAPPERS_FILE, wrappers)
            st.success(f"✅ Wrapper {wrapper_name} added successfully!")
            st.rerun()
    
    st.markdown("---")
    
    # View wrappers
    st.subheader("📋 All Wrappers")
    if wrappers:
        df = pd.DataFrame(wrappers)
        st.dataframe(df, use_container_width=True)
        
        # Summary
        total_rewards = sum([w.get('total_reward', 0) for w in wrappers])
        st.metric("Total Rewards Paid", f"₹{total_rewards:,.0f}")
    else:
        st.info("No wrappers added yet.")

# Search & Match Page
elif page == "🔍 Search & Match":
    st.title("🔍 Search & Match")
    st.markdown("---")
    
    # Search type selection
    search_type = st.radio("Search Type", ["🏘️ Search Properties", "👤 Match Buyers", "🏢 View Seller Properties"], horizontal=True)
    
    if search_type == "🏘️ Search Properties":
        st.subheader("🏘️ Search Properties")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            prop_type = st.selectbox("Property Type", ["All", "Flat", "Plot", "Villa", "Commercial"])
        with col2:
            min_price = st.number_input("Min Price (₹)", value=0)
        with col3:
            max_price = st.number_input("Max Price (₹)", value=50000000)
        
        location = st.text_input("Location (optional)")
        
        if st.button("🔍 Search", type="primary"):
            if properties:
                results = [p for p in properties]
                
                if prop_type != "All":
                    results = [p for p in results if p.get('type') == prop_type]
                
                results = [p for p in results if min_price <= p.get('price', 0) <= max_price]
                
                if location:
                    results = [p for p in results if location.lower() in p.get('location', '').lower()]
                
                if results:
                    st.success(f"Found {len(results)} properties")
                    st.dataframe(pd.DataFrame(results), use_container_width=True)
                else:
                    st.warning("No properties found matching criteria.")
            else:
                st.info("No properties in database.")
    
    elif search_type == "👤 Match Buyers":
        st.subheader("👤 Match Buyers with Properties")
        
        if buyers and properties:
            # Select buyer
            buyer_names = [f"{b.get('name')} ({b.get('id')})" for b in buyers if b.get('status') == 'Active']
            if buyer_names:
                selected_buyer = st.selectbox("Select Buyer", buyer_names)
                
                if st.button("🔍 Find Matching Properties", type="primary"):
                    # Get buyer details
                    buyer_id = selected_buyer.split('(')[-1].replace(')', '')
                    buyer = next((b for b in buyers if b.get('id') == buyer_id), None)
                    
                    if buyer:
                        st.write(f"**Buyer:** {buyer.get('name')}")
                        st.write(f"**Budget:** ₹{buyer.get('budget_min', 0):,.0f} - ₹{buyer.get('budget_max', 0):,.0f}")
                        st.write(f"**Type Needed:** {buyer.get('type_needed')}")
                        st.write(f"**Preferred Location:** {buyer.get('preferred_location')}")
                        
                        # Find matches
                        matches = []
                        for prop in properties:
                            if prop.get('status') != 'Available':
                                continue
                            
                            # Check budget
                            price = prop.get('price', 0)
                            if not (buyer.get('budget_min', 0) <= price <= buyer.get('budget_max', float('inf'))):
                                continue
                            
                            # Check type (if not 'Any')
                            if buyer.get('type_needed') != 'Any' and prop.get('type') != buyer.get('type_needed'):
                                continue
                            
                            # Check location
                            if buyer.get('preferred_location') and buyer.get('preferred_location').lower() not in prop.get('location', '').lower():
                                continue
                            
                            matches.append(prop)
                        
                        if matches:
                            st.success(f"Found {len(matches)} matching properties!")
                            st.dataframe(pd.DataFrame(matches), use_container_width=True)
                        else:
                            st.warning("No matching properties found.")
            else:
                st.info("No active buyers available.")
        else:
            st.info("Add buyers and properties first to use matching.")
    
    elif search_type == "🏢 View Seller Properties":
        st.subheader("🏢 View All Properties by Seller")
        
        if sellers:
            seller_names = [f"{s.get('name')} ({s.get('id')})" for s in sellers]
            selected_seller = st.selectbox("Select Seller", seller_names)
            
            if st.button("🔍 Show Properties", type="primary"):
                seller_id = selected_seller.split('(')[-1].replace(')', '')
                seller = next((s for s in sellers if s.get('id') == seller_id), None)
                
                if seller:
                    st.write(f"**Seller:** {seller.get('name')}")
                    st.write(f"**Location:** {seller.get('location')}")
                    st.write(f"**Expected Price:** ₹{seller.get('expected_price', 0):,.0f}")
                    
                    # Find properties (by owner name matching seller name)
                    seller_properties = [p for p in properties if seller.get('name').lower() in p.get('owner_name', '').lower()]
                    
                    if seller_properties:
                        st.success(f"Found {len(seller_properties)} properties")
                        st.dataframe(pd.DataFrame(seller_properties), use_container_width=True)
                    else:
                        st.warning("No properties found for this seller.")
        else:
            st.info("No sellers in database.")

# Footer
st.sidebar.markdown("---")
st.sidebar.info("PinkCityEstate.in CRM v1.0")
st.sidebar.caption("© 2026 All rights reserved.")
