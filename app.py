"""
PinkCityEstate.in - Real Estate CRM
====================================
Streamlit web application for property management
Features: Properties, Buyers, Sellers, Referrals, Reports, Search & Match
With Admin/User login system, Password change, CSV bulk upload, Public Inquiry
"""

import streamlit as st
import pandas as pd
import json
import os
import hashlib
from datetime import datetime
from io import BytesIO, StringIO

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
REFERRALS_FILE = os.path.join(DATA_DIR, "referrals.json")
CREDENTIALS_FILE = os.path.join(DATA_DIR, "credentials.json")
INQUIRIES_FILE = os.path.join(DATA_DIR, "inquiries.json")

# Ensure data directory exists
os.makedirs(DATA_DIR, exist_ok=True)

# Simple hash function for passwords
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Initialize session state for login
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_role' not in st.session_state:
    st.session_state.user_role = None
if 'username' not in st.session_state:
    st.session_state.username = None
if 'public_page' not in st.session_state:
    st.session_state.public_page = "🔍 Search Properties"

# Load or initialize credentials - works for both local and cloud
def load_credentials():
    # First check if credentials exist in session state (for cloud persistence during session)
    if 'credentials' in st.session_state:
        return st.session_state.credentials
    
    # Then check local file (for local development)
    if os.path.exists(CREDENTIALS_FILE):
        try:
            with open(CREDENTIALS_FILE, 'r') as f:
                return json.load(f)
        except:
            pass
    
    # Default credentials
    default_creds = {
        "admin": hash_password("admin123"),
        "user": hash_password("user123")
    }
    # Store in session state for cloud
    st.session_state.credentials = default_creds
    return default_creds

def save_credentials(creds):
    # Always update session state (works on cloud)
    st.session_state.credentials = creds
    # Also try to save to file (works on local)
    try:
        with open(CREDENTIALS_FILE, 'w') as f:
            json.dump(creds, f, indent=2)
    except:
        pass  # File write may fail on cloud, but session state will persist

def verify_credentials(username, password):
    creds = load_credentials()
    hashed_input = hash_password(password)
    return creds.get(username) == hashed_input

def update_password(username, new_password):
    creds = load_credentials()
    creds[username] = hash_password(new_password)
    save_credentials(creds)
    return True

# Load credentials
CREDENTIALS = load_credentials()

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
referrals = load_data(REFERRALS_FILE, [])
inquiries = load_data(INQUIRIES_FILE, [])

# Function to export to Excel
def to_excel(df, sheet_name="Sheet1"):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name=sheet_name, index=False)
    output.seek(0)
    return output

# ============== SIDEBAR NAVIGATION ==============
st.sidebar.title("🏠 PinkCityEstate.in")

# Show login status in sidebar
if st.session_state.logged_in:
    st.sidebar.markdown(f"**Welcome, {st.session_state.username}** ({st.session_state.user_role})")
    st.sidebar.markdown("---")
    
    # Logout button
    if st.sidebar.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.session_state.user_role = None
        st.session_state.username = None
        st.rerun()
    st.sidebar.markdown("---")
    
    # Admin Navigation
    if st.session_state.user_role == "admin":
        page = st.sidebar.radio(
            "Navigation",
            ["📋 Dashboard", "🏘️ Properties", "👤 Buyers", "🏢 Sellers", "🎁 Referrals", "📊 Reports", "🔍 Search & Match", "📞 Inquiries", "⚙️ Settings"]
        )
    else:
        # User Navigation (logged in but not admin)
        page = st.sidebar.radio(
            "Navigation",
            ["📝 Submit Property", "📝 Submit Requirement", "🔍 Search Properties", "📞 Contact Us"]
        )
else:
    # Not logged in - show public pages + Admin Login option
    st.sidebar.markdown("**Welcome, Guest**")
    st.sidebar.markdown("---")
    page = st.sidebar.radio(
        "Navigation",
        ["🔍 Search Properties", "📞 Contact Us", "🔐 Admin Login"]
    )

# ============== PUBLIC PAGES (No Login Required) ==============

# ----- PUBLIC SEARCH PROPERTIES -----
if page == "🔍 Search Properties":
    # HERO SECTION
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 2rem; border-radius: 10px; text-align: center; margin-bottom: 2rem;">
        <h1 style="color: white; font-size: 2.5rem; margin-bottom: 1rem;">Find Best Property Deals in Jaipur</h1>
        <p style="color: #e0e0e0; font-size: 1.2rem;">Flats • Plots • Villas • Commercial</p>
        <p style="color: #c0c0c0; font-size: 1rem;">Vaishali Nagar • Mansarovar • Jagatpura</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # QUICK FILTER CHIPS
    st.subheader("Quick Filters")
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        if st.button("🏠 All Properties", use_container_width=True):
            st.session_state.quick_filter = "All"
    with col2:
        if st.button("🏢 Flats", use_container_width=True):
            st.session_state.quick_filter = "Flat"
    with col3:
        if st.button("📐 Plots", use_container_width=True):
            st.session_state.quick_filter = "Plot"
    with col4:
        if st.button("🏡 Villas", use_container_width=True):
            st.session_state.quick_filter = "Villa"
    with col5:
        if st.button("🏪 Commercial", use_container_width=True):
            st.session_state.quick_filter = "Commercial"
    
    # DETAILED SEARCH
    with st.expander("🔍 Advanced Search", expanded=False):
        col1, col2, col3 = st.columns(3)
        with col1:
            prop_type = st.selectbox("Property Type", ["All", "Flat", "Plot", "Villa", "Commercial"], 
                                   index=["All", "Flat", "Plot", "Villa", "Commercial"].index(st.session_state.get('quick_filter', 'All')))
        with col2:
            min_price = st.number_input("Min Price (₹)", value=0)
        with col3:
            max_price = st.number_input("Max Price (₹)", value=50000000)
        
        location = st.text_input("Location (optional)", placeholder="e.g., Malviya Nagar, Jagatpura")
    
    # SEARCH BUTTON
    search_clicked = st.button("🔍 Search Properties", type="primary", use_container_width=True)
    
    # SHOW PROPERTIES
    if search_clicked or 'quick_filter' in st.session_state:
        if properties:
            available_props = [p for p in properties if p.get('status') == 'Available']
            results = available_props
            
            # Apply filters
            quick_filter = st.session_state.get('quick_filter', 'All')
            if quick_filter != "All":
                results = [p for p in results if p.get('type') == quick_filter]
            elif prop_type != "All":
                results = [p for p in results if p.get('type') == prop_type]
            
            if location and 'quick_filter' not in st.session_state:
                results = [p for p in results if location.lower() in p.get('location', '').lower()]
            
            # Price filter
            if search_clicked:
                results = [p for p in results if min_price <= p.get('price', 0) <= max_price]
            
            if results:
                st.success(f"Found {len(results)} properties")
                
                # PROPERTY CARDS GRID
                st.markdown("### 🏘️ Featured Properties")
                
                # Create rows of 3 cards each
                for i in range(0, len(results), 3):
                    cols = st.columns(3)
                    for j, col in enumerate(cols):
                        if i + j < len(results):
                            prop = results[i + j]
                            with col:
                                # Card styling
                                card_html = f"""
                                <div style="border: 1px solid #e0e0e0; border-radius: 10px; overflow: hidden; margin-bottom: 1rem; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                                    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); height: 120px; display: flex; align-items: center; justify-content: center; color: white; font-size: 2rem;">
                                        🏠
                                    </div>
                                    <div style="padding: 1rem;">
                                        <div style="display: inline-block; background: #667eea; color: white; padding: 2px 8px; border-radius: 12px; font-size: 0.75rem; margin-bottom: 0.5rem;">
                                            {prop.get('status', 'Available')}
                                        </div>
                                        <h4 style="margin: 0; font-size: 1.1rem; color: #333;">{prop.get('type', 'Property')}</h4>
                                        <p style="margin: 0.25rem 0; color: #666; font-size: 0.9rem;">📍 {prop.get('location', 'Location N/A')}</p>
                                        <p style="margin: 0.25rem 0; color: #666; font-size: 0.85rem;">
                                            🛏️ {prop.get('bedrooms', 'N/A')} | 📐 {prop.get('area_sqft', 'N/A')} sqft
                                        </p>
                                        <p style="margin: 0.5rem 0; font-size: 1.2rem; font-weight: bold; color: #667eea;">
                                            ₹{prop.get('price', 0):,}
                                        </p>
                                    </div>
                                </div>
                                """
                                st.markdown(card_html, unsafe_allow_html=True)
                                
                                # Inquiry button
                                if st.button("📞 Inquire Now", key=f"inquire_{prop.get('id')}", use_container_width=True):
                                    st.session_state.inquiry_property = prop
                                    st.info(f"Contact: {prop.get('owner_contact', 'N/A')}")
                
                # Clear quick filter after showing results
                if 'quick_filter' in st.session_state:
                    del st.session_state.quick_filter
                    
            else:
                st.warning("No properties found matching your criteria.")
                st.info("📞 Please send us your inquiry through the Contact Us page. Our team will get back to you within 24 hours.")
        else:
            st.info("No properties available at the moment.")
            st.info("📞 Please send us your inquiry through the Contact Us page. Our team will get back to you within 24 hours.")

# ----- PUBLIC CONTACT US -----
elif page == "📞 Contact Us":
    st.title("📞 Contact Us / Send Inquiry")
    st.markdown("---")
    
    st.info("Have a question or need assistance? Fill out the form below and our team will get back to you within 24 hours.")
    
    # Entry Type Selection (matching CRM template format)
    entry_type = st.selectbox(
        "I want to:",
        ["🏠 List a Property (Sell/Rent)", "🔍 Buy/Rent a Property", "🤝 Refer a Property/Client", "💼 Become a Partner/Agent", "❓ General Inquiry"],
        key="contact_entry_type"
    )
    
    st.markdown("---")
    
    # Common Fields (All types)
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("Your Name *", key="contact_name")
        phone = st.text_input("Phone Number *", key="contact_phone")
        email = st.text_input("Email Address", key="contact_email")
    
    with col2:
        location = st.text_input("Location/Area", key="contact_location", placeholder="e.g., Malviya Nagar, Jaipur")
        preferred_contact = st.selectbox("Preferred Contact Method", ["Phone", "WhatsApp", "Email"], key="contact_pref")
    
    st.markdown("---")
    
    # Dynamic fields based on Entry Type
    if entry_type == "🏠 List a Property (Sell/Rent)":
        st.subheader("Property Details")
        col1, col2, col3 = st.columns(3)
        with col1:
            prop_type = st.selectbox("Property Type", ["Flat", "Plot", "Villa", "Commercial", "Office"])
            bedrooms = st.selectbox("Bedrooms", ["Studio", "1 BHK", "2 BHK", "3 BHK", "4 BHK", "5+ BHK", "N/A"])
        with col2:
            area_val = st.text_input("Area (sqft/Gaj)", placeholder="e.g., 1200 sqft or 200 Gaj")
            furnished = st.selectbox("Furnished", ["No", "Yes", "Semi"])
        with col3:
            expected_price = st.text_input("Expected Price", placeholder="e.g., 45L or 1.35Cr")
            purpose = st.selectbox("Purpose", ["Sale", "Rent"])
        
        remarks = st.text_area("Property Description", height=100, placeholder="Describe your property (floor, facing, amenities, etc.)")
        
    elif entry_type == "🔍 Buy/Rent a Property":
        st.subheader("Requirement Details")
        col1, col2, col3 = st.columns(3)
        with col1:
            req_type = st.selectbox("Looking For", ["Flat", "Plot", "Villa", "Commercial", "Office"])
            req_bedrooms = st.selectbox("Bedrooms Needed", ["Studio", "1 BHK", "2 BHK", "3 BHK", "4 BHK", "5+ BHK", "Any"])
        with col2:
            budget_min = st.text_input("Budget From", placeholder="e.g., 30L")
            budget_max = st.text_input("Budget To", placeholder="e.g., 80L")
        with col3:
            req_furnished = st.selectbox("Furnishing", ["Any", "Furnished", "Semi-Furnished", "Unfurnished"])
            urgency = st.selectbox("Urgency", ["Immediate", "Within 1 month", "Within 3 months", "Just exploring"])
        
        remarks = st.text_area("Additional Requirements", height=100, placeholder="Specific needs, preferred localities, etc.")
        
    elif entry_type == "🤝 Refer a Property/Client":
        st.subheader("Referral Details")
        col1, col2 = st.columns(2)
        with col1:
            referral_for = st.selectbox("Referral For", ["Property for Sale", "Property for Rent", "Buyer", "Seller"])
            ref_property_type = st.selectbox("Property Type", ["Flat", "Plot", "Villa", "Commercial", "N/A"])
        with col2:
            ref_location = st.text_input("Property/Client Location")
            ref_price = st.text_input("Price/Budget", placeholder="e.g., 45L")
        
        remarks = st.text_area("Referral Details", height=100, placeholder="Client details, property description, your commission expectation, etc.")
        
    elif entry_type == "💼 Become a Partner/Agent":
        st.subheader("Partner Details")
        col1, col2 = st.columns(2)
        with col1:
            partner_type = st.selectbox("Partner Type", ["Individual Agent", "Broker", "Builder", "Property Dealer", "Other"])
            experience = st.selectbox("Experience", ["0-1 years", "1-3 years", "3-5 years", "5+ years"])
        with col2:
            areas_operate = st.text_input("Areas You Operate", placeholder="e.g., Malviya Nagar, Vaishali Nagar")
        
        remarks = st.text_area("About You", height=100, placeholder="Tell us about your business, past deals, etc.")
        
    else:  # General Inquiry
        remarks = st.text_area("Your Message", height=150, placeholder="How can we help you?")
    
    st.markdown("---")
    
    # Submit Button
    if st.button("📤 Submit Inquiry", type="primary", use_container_width=True):
        if not name or not phone:
            st.error("❌ Please fill in Name and Phone Number")
        else:
            # Create inquiry record
            inquiry_data = {
                "id": f"INQ{len(inquiries)+1:03d}",
                "name": name,
                "contact": phone,
                "email": email,
                "location": location,
                "entry_type": entry_type,
                "preferred_contact": preferred_contact,
                "status": "New",
                "admin_remarks": "",
                "date_added": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "updated_date": "",
                "details": remarks if 'remarks' in locals() else ""
            }
            
            # Add type-specific data
            if entry_type == "🏠 List a Property (Sell/Rent)":
                inquiry_data.update({
                    "inquiry_subtype": "Seller Listing",
                    "property_type": prop_type if 'prop_type' in locals() else "",
                    "area": area_val if 'area_val' in locals() else "",
                    "price": expected_price if 'expected_price' in locals() else "",
                    "purpose": purpose if 'purpose' in locals() else ""
                })
            elif entry_type == "🔍 Buy/Rent a Property":
                inquiry_data.update({
                    "inquiry_subtype": "Buyer Requirement",
                    "property_type": req_type if 'req_type' in locals() else "",
                    "budget_min": budget_min if 'budget_min' in locals() else "",
                    "budget_max": budget_max if 'budget_max' in locals() else "",
                    "urgency": urgency if 'urgency' in locals() else ""
                })
            elif entry_type == "🤝 Refer a Property/Client":
                inquiry_data.update({
                    "inquiry_subtype": "Referral",
                    "referral_for": referral_for if 'referral_for' in locals() else "",
                    "property_type": ref_property_type if 'ref_property_type' in locals() else ""
                })
            elif entry_type == "💼 Become a Partner/Agent":
                inquiry_data.update({
                    "inquiry_subtype": "Partner/Agent",
                    "partner_type": partner_type if 'partner_type' in locals() else "",
                    "experience": experience if 'experience' in locals() else ""
                })
            
            inquiries.append(inquiry_data)
            save_data(INQUIRIES_FILE, inquiries)
            
            st.success("✅ Your inquiry has been submitted successfully!")
            st.info("📞 Our team will contact you within 24 hours.")
            st.balloons()

# ----- ADMIN LOGIN -----
elif page == "🔐 Admin Login":
    if not st.session_state.logged_in:
        st.title("🔐 Admin Login")
        st.markdown("---")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            st.subheader("🔐 Login")
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            
            if st.button("Login", type="primary", use_container_width=True):
                if username == "admin" and verify_credentials("admin", password):
                    st.session_state.logged_in = True
                    st.session_state.user_role = "admin"
                    st.session_state.username = username
                    st.success("✅ Admin login successful!")
                    st.rerun()
                elif username == "user" and verify_credentials("user", password):
                    st.session_state.logged_in = True
                    st.session_state.user_role = "user"
                    st.session_state.username = username
                    st.success("✅ User login successful!")
                    st.rerun()
                else:
                    st.error("❌ Invalid username or password")
            
            st.info("**Demo Credentials:**\n- Admin: admin / admin123\n- User: user / user123")
    else:
        st.title("✅ Already Logged In")
        st.markdown("---")
        st.success(f"You are already logged in as **{st.session_state.username}** ({st.session_state.user_role})")
        if st.button("Go to Dashboard"):
            st.rerun()

# ============== ADMIN PAGES (Login Required) ==============
if st.session_state.logged_in and st.session_state.user_role == "admin":
    
    # ----- DASHBOARD -----
    if page == "📋 Dashboard":
        st.title("📋 Dashboard")
        st.markdown("---")
        
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
            total_referrals = len(referrals)
            st.metric("Total Referrals", total_referrals)
        
        st.markdown("---")
        
        # Show pending inquiries alert
        pending_inquiries = len([i for i in inquiries if i.get('status') == 'New'])
        if pending_inquiries > 0:
            st.warning(f"🔔 You have {pending_inquiries} new inquiry(s) waiting for response!")
        
        st.markdown("---")
        
        st.subheader("🏘️ Recent Properties")
        if properties:
            df_props = pd.DataFrame(properties[-5:])
            st.dataframe(df_props, use_container_width=True)
        else:
            st.info("No properties added yet.")
        
        st.subheader("👤 Active Buyers")
        if buyers:
            df_buyers = pd.DataFrame([b for b in buyers if b.get('status') == 'Active'])
            if not df_buyers.empty:
                st.dataframe(df_buyers, use_container_width=True)
            else:
                st.info("No active buyers.")
        else:
            st.info("No buyers added yet.")

    # ----- PROPERTIES -----
    elif page == "🏘️ Properties":
        st.title("🏘️ Properties Management")
        st.markdown("---")
        
        # BULK IMPORT SECTION
        st.subheader("📥 Bulk Import Properties")
        
        import_type = st.radio("Import Type", ["📊 Excel/CSV File", "� Unified CRM Template", "�💬 WhatsApp Messages"], horizontal=True)
        
        if import_type == "📊 Excel/CSV File":
            with st.expander("Upload Excel/CSV with Flexible Column Mapping", expanded=True):
                st.info("Upload your Excel or CSV file. Map your column names to our fields in the preview.")
                
                uploaded_file = st.file_uploader("Choose Excel/CSV file", type=["csv", "xlsx", "xls"])
                
                if uploaded_file is not None:
                    try:
                        # Read file
                        if uploaded_file.name.endswith('.csv'):
                            df_upload = pd.read_csv(uploaded_file)
                        else:
                            df_upload = pd.read_excel(uploaded_file)
                        
                        st.write("**📋 Preview of your data:**")
                        st.dataframe(df_upload.head(10), use_container_width=True)
                        
                        st.write("**🔧 Map your columns:**")
                        st.caption("Select which column in your file matches each field")
                        
                        df_columns = ['(Not mapped)'] + list(df_upload.columns)
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            type_col = st.selectbox("Property Type", df_columns, key="map_type")
                            location_col = st.selectbox("Location", df_columns, key="map_location")
                            area_col = st.selectbox("Area (sqft)", df_columns, key="map_area")
                            price_col = st.selectbox("Price", df_columns, key="map_price")
                            
                        with col2:
                            bedrooms_col = st.selectbox("Bedrooms", df_columns, key="map_bedrooms")
                            furnished_col = st.selectbox("Furnished", df_columns, key="map_furnished")
                            status_col = st.selectbox("Status", df_columns, key="map_status")
                            owner_name_col = st.selectbox("Owner Name", df_columns, key="map_owner")
                            
                        with col3:
                            owner_contact_col = st.selectbox("Owner Contact", df_columns, key="map_contact")
                            referral_col = st.selectbox("Referral Name", df_columns, key="map_referral")
                            reward_col = st.selectbox("Referral Reward", df_columns, key="map_reward")
                            remarks_col = st.selectbox("Remarks", df_columns, key="map_remarks")
                        
                        # Default values for unmapped fields
                        st.write("**📝 Default values for missing columns:**")
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            default_type = st.selectbox("Default Type", ["Flat", "Plot", "Villa", "Commercial", "Office"], key="def_type")
                            default_status = st.selectbox("Default Status", ["Available", "Sold", "Rented", "Under Negotiation"], key="def_status")
                        with col2:
                            default_bedrooms = st.selectbox("Default BHK", ["Studio", "1 BHK", "2 BHK", "3 BHK", "4 BHK", "5+ BHK"], key="def_bhk")
                            default_furnished = st.selectbox("Default Furnished", ["No", "Yes", "Semi"], key="def_furn")
                        with col3:
                            default_area = st.number_input("Default Area", value=1000, key="def_area")
                            default_price = st.number_input("Default Price", value=5000000, key="def_price")
                        
                        # Preview mapped data
                        if st.button("👁️ Preview Mapped Data", type="secondary"):
                            preview_data = []
                            for idx, row in df_upload.head(5).iterrows():
                                mapped_row = {
                                    "type": str(row.get(type_col, default_type)) if type_col != '(Not mapped)' else default_type,
                                    "location": str(row.get(location_col, '')) if location_col != '(Not mapped)' else '',
                                    "area_sqft": int(row.get(area_col, default_area)) if area_col != '(Not mapped)' and pd.notna(row.get(area_col)) else default_area,
                                    "price": int(row.get(price_col, default_price)) if price_col != '(Not mapped)' and pd.notna(row.get(price_col)) else default_price,
                                    "bedrooms": str(row.get(bedrooms_col, default_bedrooms)) if bedrooms_col != '(Not mapped)' else default_bedrooms,
                                    "furnished": str(row.get(furnished_col, default_furnished)) if furnished_col != '(Not mapped)' else default_furnished,
                                    "status": str(row.get(status_col, default_status)) if status_col != '(Not mapped)' else default_status,
                                    "owner_name": str(row.get(owner_name_col, '')) if owner_name_col != '(Not mapped)' else '',
                                    "owner_contact": str(row.get(owner_contact_col, '')) if owner_contact_col != '(Not mapped)' else '',
                                    "referral_name": str(row.get(referral_col, '')) if referral_col != '(Not mapped)' else '',
                                    "referral_reward": int(row.get(reward_col, 0)) if reward_col != '(Not mapped)' and pd.notna(row.get(reward_col)) else 0,
                                    "remarks": str(row.get(remarks_col, '')) if remarks_col != '(Not mapped)' else ''
                                }
                                preview_data.append(mapped_row)
                            
                            st.write("**📋 Preview of mapped properties:**")
                            st.dataframe(pd.DataFrame(preview_data), use_container_width=True)
                        
                        # Import button
                        if st.button("📥 Import All Properties", type="primary"):
                            success_count = 0
                            for idx, row in df_upload.iterrows():
                                try:
                                    new_property = {
                                        "id": f"PROP{len(properties)+idx+1:03d}",
                                        "type": str(row.get(type_col, default_type)) if type_col != '(Not mapped)' else default_type,
                                        "location": str(row.get(location_col, '')) if location_col != '(Not mapped)' else '',
                                        "area_sqft": int(float(str(row.get(area_col, default_area)).replace(',', ''))) if area_col != '(Not mapped)' and pd.notna(row.get(area_col)) else default_area,
                                        "price": int(float(str(row.get(price_col, default_price)).replace(',', ''))) if price_col != '(Not mapped)' and pd.notna(row.get(price_col)) else default_price,
                                        "bedrooms": str(row.get(bedrooms_col, default_bedrooms)) if bedrooms_col != '(Not mapped)' else default_bedrooms,
                                        "furnished": str(row.get(furnished_col, default_furnished)) if furnished_col != '(Not mapped)' else default_furnished,
                                        "status": str(row.get(status_col, default_status)) if status_col != '(Not mapped)' else default_status,
                                        "owner_name": str(row.get(owner_name_col, '')) if owner_name_col != '(Not mapped)' else '',
                                        "owner_contact": str(row.get(owner_contact_col, '')) if owner_contact_col != '(Not mapped)' else '',
                                        "referral_name": str(row.get(referral_col, '')) if referral_col != '(Not mapped)' else '',
                                        "referral_reward": int(float(str(row.get(reward_col, 0)).replace(',', ''))) if reward_col != '(Not mapped)' and pd.notna(row.get(reward_col)) else 0,
                                        "remarks": str(row.get(remarks_col, '')) if remarks_col != '(Not mapped)' else '',
                                        "date_added": datetime.now().strftime("%Y-%m-%d"),
                                        "import_source": "excel"
                                    }
                                    properties.append(new_property)
                                    success_count += 1
                                except Exception as e:
                                    st.error(f"Error on row {idx+1}: {e}")
                            
                            save_data(PROPERTIES_FILE, properties)
                            st.success(f"✅ Successfully imported {success_count} properties!")
                            st.rerun()
                            
                    except Exception as e:
                        st.error(f"❌ Error reading file: {e}")
        
        elif import_type == "🔄 Unified CRM Template":
            with st.expander("Upload Unified CRM Template (Property + Buyer + Seller + Referral)", expanded=True):
                st.info("Upload the unified template where one row can create Property, Buyer, Seller, and Referral entries simultaneously.")
                st.caption("Use flags (Yes/No) to control what gets created from each row")
                
                unified_file = st.file_uploader("Choose Unified CSV file", type=["csv"], key="unified_upload")
                
                if unified_file is not None:
                    try:
                        df_unified = pd.read_csv(unified_file)
                        
                        st.write(f"**📋 Preview of {len(df_unified)} entries:**")
                        st.dataframe(df_unified.head(10), use_container_width=True)
                        
                        # Summary of what will be created
                        st.write("**🎯 Summary of what will be imported:**")
                        
                        if 'is_buyer_requirement' in df_unified.columns:
                            buyer_count = df_unified[df_unified['is_buyer_requirement'].astype(str).str.lower() == 'yes'].shape[0]
                            st.write(f"- Buyers to create: {buyer_count}")
                        
                        if 'is_seller_listing' in df_unified.columns:
                            seller_count = df_unified[df_unified['is_seller_listing'].astype(str).str.lower() == 'yes'].shape[0]
                            st.write(f"- Sellers to create: {seller_count}")
                        
                        if 'is_referral' in df_unified.columns:
                            referral_count = df_unified[df_unified['is_referral'].astype(str).str.lower() == 'yes'].shape[0]
                            st.write(f"- Referrals to create: {referral_count}")
                        
                        # Preview first row details
                        if st.button("👁️ Preview First Entry Details", type="secondary"):
                            if len(df_unified) > 0:
                                row = df_unified.iloc[0]
                                st.write("**Entry Type:**", row.get('entry_type', 'N/A'))
                                
                                cols = st.columns(4)
                                with cols[0]:
                                    st.write("**Property Info:**")
                                    st.write(f"- Type: {row.get('property_type', 'N/A')}")
                                    st.write(f"- Location: {row.get('location', 'N/A')}")
                                    st.write(f"- Price: ₹{row.get('price', 'N/A')}")
                                
                                with cols[1]:
                                    if str(row.get('is_buyer_requirement', '')).lower() == 'yes':
                                        st.write("**Buyer Info:**")
                                        st.write(f"- Name: {row.get('buyer_name', 'N/A')}")
                                        st.write(f"- Budget: ₹{row.get('buyer_budget_min', 'N/A')} - ₹{row.get('buyer_budget_max', 'N/A')}")
                                
                                with cols[2]:
                                    if str(row.get('is_seller_listing', '')).lower() == 'yes':
                                        st.write("**Seller Info:**")
                                        st.write(f"- Name: {row.get('seller_name', 'N/A')}")
                                        st.write(f"- Expected: ₹{row.get('seller_expected_price', 'N/A')}")
                                
                                with cols[3]:
                                    if str(row.get('is_referral', '')).lower() == 'yes':
                                        st.write("**Referral Info:**")
                                        st.write(f"- Name: {row.get('referral_name', 'N/A')}")
                                        st.write(f"- Reward: ₹{row.get('referral_reward_amount', 'N/A')}")
                        
                        # Import button
                        if st.button("📥 Import All Unified Data", type="primary"):
                            prop_count = 0
                            buyer_count = 0
                            seller_count = 0
                            referral_count = 0
                            
                            for idx, row in df_unified.iterrows():
                                try:
                                    # Extract property data if present
                                    has_property = any([
                                        pd.notna(row.get('property_type')),
                                        pd.notna(row.get('location')),
                                        pd.notna(row.get('price'))
                                    ])
                                    
                                    if has_property:
                                        # Parse price (handle string formats)
                                        price_val = row.get('price', 0)
                                        if isinstance(price_val, str):
                                            price_val = price_val.replace(',', '').replace('₹', '')
                                            if 'cr' in price_val.lower():
                                                price_val = float(price_val.lower().replace('cr', '').strip()) * 10000000
                                            elif 'lac' in price_val.lower() or 'lakh' in price_val.lower():
                                                price_val = float(price_val.lower().replace('lac', '').replace('lakh', '').strip()) * 100000
                                            else:
                                                try:
                                                    price_val = float(price_val)
                                                except:
                                                    price_val = 0
                                        
                                        # Parse area
                                        area_val = row.get('area_sqft', 0)
                                        if isinstance(area_val, str):
                                            area_str = area_val.lower()
                                            if 'gaj' in area_str or 'sq yard' in area_str:
                                                # Extract number and convert (1 Gaj = 9 sqft)
                                                import re
                                                num_match = re.search(r'[\d.]+', area_str)
                                                if num_match:
                                                    area_val = float(num_match.group()) * 9
                                            else:
                                                try:
                                                    area_val = float(area_val.replace(',', ''))
                                                except:
                                                    area_val = 1000
                                        
                                        new_property = {
                                            "id": f"PROP{len(properties)+prop_count+1:03d}",
                                            "type": str(row.get('property_type', 'Flat')),
                                            "location": str(row.get('location', '')),
                                            "area_sqft": int(area_val) if area_val else 1000,
                                            "price": int(price_val) if price_val else 0,
                                            "bedrooms": str(row.get('bedrooms', '2 BHK')),
                                            "furnished": str(row.get('furnished', 'No')),
                                            "status": str(row.get('property_status', 'Available')),
                                            "owner_name": str(row.get('property_owner_name', row.get('buyer_name', ''))),
                                            "owner_contact": str(row.get('property_owner_contact', row.get('buyer_contact', ''))),
                                            "referral_name": str(row.get('referral_name', '')),
                                            "referral_reward": int(row.get('referral_reward_amount', 0)) if pd.notna(row.get('referral_reward_amount')) else 0,
                                            "remarks": str(row.get('property_remarks', '')),
                                            "date_added": datetime.now().strftime("%Y-%m-%d"),
                                            "import_source": "unified_template"
                                        }
                                        properties.append(new_property)
                                        prop_count += 1
                                    
                                    # Create Buyer if flagged
                                    if str(row.get('is_buyer_requirement', '')).lower() == 'yes':
                                        budget_min = row.get('buyer_budget_min', 0)
                                        budget_max = row.get('buyer_budget_max', 0)
                                        if isinstance(budget_min, str):
                                            budget_min = budget_min.replace(',', '').replace('₹', '')
                                            try:
                                                budget_min = float(budget_min)
                                            except:
                                                budget_min = 0
                                        if isinstance(budget_max, str):
                                            budget_max = budget_max.replace(',', '').replace('₹', '')
                                            try:
                                                budget_max = float(budget_max)
                                            except:
                                                budget_max = 0
                                        
                                        new_buyer = {
                                            "id": f"BUY{len(buyers)+buyer_count+1:03d}",
                                            "name": str(row.get('buyer_name', '')),
                                            "contact": str(row.get('buyer_contact', '')),
                                            "email": str(row.get('buyer_email', '')),
                                            "budget_min": int(budget_min) if budget_min else 0,
                                            "budget_max": int(budget_max) if budget_max else 0,
                                            "type_needed": str(row.get('buyer_property_type', 'Any')),
                                            "preferred_location": str(row.get('buyer_location_preference', '')),
                                            "requirements": f"{row.get('buyer_bedrooms', '')}, {row.get('buyer_furnished', '')}",
                                            "status": "Active",
                                            "follow_up_date": (datetime.now().replace(day=datetime.now().day + 7)).strftime("%Y-%m-%d"),
                                            "remarks": str(row.get('buyer_remarks', '')),
                                            "date_added": datetime.now().strftime("%Y-%m-%d"),
                                            "urgency": str(row.get('buyer_urgency', 'Medium'))
                                        }
                                        buyers.append(new_buyer)
                                        buyer_count += 1
                                    
                                    # Create Seller if flagged
                                    if str(row.get('is_seller_listing', '')).lower() == 'yes':
                                        exp_price = row.get('seller_expected_price', 0)
                                        if isinstance(exp_price, str):
                                            exp_price = exp_price.replace(',', '').replace('₹', '')
                                            try:
                                                exp_price = float(exp_price)
                                            except:
                                                exp_price = 0
                                        
                                        new_seller = {
                                            "id": f"SEL{len(sellers)+seller_count+1:03d}",
                                            "name": str(row.get('seller_name', '')),
                                            "contact": str(row.get('seller_contact', '')),
                                            "email": str(row.get('seller_email', '')),
                                            "property_type": str(row.get('seller_property_type', '')),
                                            "location": str(row.get('seller_location', '')),
                                            "expected_price": int(exp_price) if exp_price else 0,
                                            "urgency": "Medium",
                                            "status": str(row.get('seller_status', 'Active')),
                                            "remarks": str(row.get('seller_remarks', '')),
                                            "date_added": datetime.now().strftime("%Y-%m-%d")
                                        }
                                        sellers.append(new_seller)
                                        seller_count += 1
                                    
                                    # Create Referral if flagged
                                    if str(row.get('is_referral', '')).lower() == 'yes':
                                        reward = row.get('referral_reward_amount', 0)
                                        if isinstance(reward, str):
                                            reward = reward.replace(',', '').replace('₹', '')
                                            try:
                                                reward = float(reward)
                                            except:
                                                reward = 0
                                        
                                        new_referral = {
                                            "id": f"REF{len(referrals)+referral_count+1:03d}",
                                            "name": str(row.get('referral_name', '')),
                                            "contact": str(row.get('referral_contact', '')),
                                            "properties_referred": 1,
                                            "total_reward": int(reward) if reward else 0,
                                            "status": str(row.get('referral_status', 'Active')),
                                            "remarks": str(row.get('referral_remarks', '')),
                                            "date_added": datetime.now().strftime("%Y-%m-%d"),
                                            "type": str(row.get('referral_type', 'Agent'))
                                        }
                                        referrals.append(new_referral)
                                        referral_count += 1
                                    
                                except Exception as e:
                                    st.error(f"Error on row {idx+1}: {e}")
                            
                            # Save all data
                            if prop_count > 0:
                                save_data(PROPERTIES_FILE, properties)
                            if buyer_count > 0:
                                save_data(BUYERS_FILE, buyers)
                            if seller_count > 0:
                                save_data(SELLERS_FILE, sellers)
                            if referral_count > 0:
                                save_data(REFERRALS_FILE, referrals)
                            
                            st.success(f"✅ Import Complete!")
                            st.write(f"- {prop_count} Properties imported")
                            st.write(f"- {buyer_count} Buyers imported")
                            st.write(f"- {seller_count} Sellers imported")
                            st.write(f"- {referral_count} Referrals imported")
                            st.rerun()
                            
                    except Exception as e:
                        st.error(f"❌ Error reading unified template: {e}")
        
        else:  # WhatsApp Messages Import
            with st.expander("💬 Import from WhatsApp Messages", expanded=True):
                st.info("Paste WhatsApp chat messages here. The system will extract property details.")
                st.caption("Format: Each property should be separated by a blank line or new message")
                
                whatsapp_text = st.text_area("Paste WhatsApp messages", height=300, placeholder="""Example formats:

Location: Malviya Nagar
Type: 2 BHK Flat
Area: 1200 sqft
Price: 45 Lakhs
Owner: Rajesh
Contact: 9876543210

OR

Malviya Nagar, 2 BHK, 1200 sqft, 45 Lakhs, Contact: 9876543210""")
                
                if whatsapp_text:
                    # Parse WhatsApp messages
                    parsed_properties = []
                    
                    # Split by double newlines or single newlines
                    messages = whatsapp_text.split('\n\n') if '\n\n' in whatsapp_text else whatsapp_text.split('\n')
                    
                    for msg in messages:
                        if not msg.strip():
                            continue
                            
                        prop_data = {
                            "raw_text": msg.strip(),
                            "type": "Flat",
                            "location": "",
                            "area_sqft": 0,
                            "price": 0,
                            "bedrooms": "2 BHK",
                            "furnished": "No",
                            "status": "Available",
                            "owner_name": "",
                            "owner_contact": "",
                            "remarks": ""
                        }
                        
                        # Extract data using patterns
                        import re
                        
                        # Location patterns
                        location_patterns = [
                            r'(?:Location|Area|Locality|Place)[\s:]*([^\n,]+)',
                            r'(?:in|at)\s+([A-Za-z\s]+(?:Nagar|Colony|Road|Street|Area|City))',
                            r'(?:Malviya|Vaishali|Jagatpura|Tonk|Durgapura|C-Scheme|Bapu|Mansarovar|Shyam)[\s\w]*'
                        ]
                        for pattern in location_patterns:
                            match = re.search(pattern, msg, re.IGNORECASE)
                            if match:
                                prop_data["location"] = match.group(1).strip() if match.groups() else match.group(0).strip()
                                break
                        
                        # Property type patterns
                        type_patterns = [
                            r'(\d+)\s*BHK',
                            r'(Flat|Plot|Villa|Commercial|Office|Shop|Apartment)',
                            r'(Residential|Commercial)'
                        ]
                        for pattern in type_patterns:
                            match = re.search(pattern, msg, re.IGNORECASE)
                            if match:
                                if 'BHK' in msg.upper():
                                    prop_data["bedrooms"] = match.group(0).strip()
                                prop_data["type"] = match.group(1).capitalize() if match.group(1).lower() in ['flat', 'plot', 'villa', 'commercial', 'office', 'shop'] else prop_data["type"]
                                break
                        
                        # Area patterns
                        area_match = re.search(r'(\d+)\s*(?:sq\s*ft|sqft|sf|sq\.\s*ft)', msg, re.IGNORECASE)
                        if area_match:
                            prop_data["area_sqft"] = int(area_match.group(1))
                        
                        # Price patterns (handle lakhs and crores)
                        price_patterns = [
                            r'(?:Price|Rs|₹)\s*[.:]*\s*(\d+(?:\.\d+)?)\s*(?:L|Lakh|Lakhs)',
                            r'(\d+(?:\.\d+)?)\s*(?:L|Lakh|Lakhs)',
                            r'(?:Price|Rs|₹)\s*[.:]*\s*(\d+(?:\.\d+)?)\s*(?:Cr|Crore|Crores)',
                            r'(\d+(?:\.\d+)?)\s*(?:Cr|Crore|Crores)',
                            r'(?:Price|Rs|₹)\s*[.:]*\s*(\d{7,})',
                        ]
                        for pattern in price_patterns:
                            match = re.search(pattern, msg, re.IGNORECASE)
                            if match:
                                price_val = float(match.group(1))
                                if 'cr' in msg.lower() or 'crore' in msg.lower():
                                    prop_data["price"] = int(price_val * 10000000)
                                else:
                                    prop_data["price"] = int(price_val * 100000)
                                break
                        
                        # Contact patterns
                        contact_match = re.search(r'(\d{10})', msg)
                        if contact_match:
                            prop_data["owner_contact"] = contact_match.group(1)
                        
                        # Owner name patterns
                        owner_match = re.search(r'(?:Owner|Contact Person|Name)[\s:]*([A-Za-z\s]+?)(?:\n|,|\d|$)', msg, re.IGNORECASE)
                        if owner_match:
                            prop_data["owner_name"] = owner_match.group(1).strip()
                        
                        parsed_properties.append(prop_data)
                    
                    if parsed_properties:
                        st.write(f"**📋 Found {len(parsed_properties)} properties:**")
                        
                        # Editable preview
                        edited_properties = []
                        for idx, prop in enumerate(parsed_properties):
                            with st.expander(f"Property {idx+1}: {prop['location'] or 'Unknown Location'} - {prop['bedrooms']}", expanded=(idx==0)):
                                st.text(f"Original: {prop['raw_text'][:100]}...")
                                
                                col1, col2 = st.columns(2)
                                with col1:
                                    prop['type'] = st.selectbox(f"Type {idx}", ["Flat", "Plot", "Villa", "Commercial", "Office"], 
                                                               index=["Flat", "Plot", "Villa", "Commercial", "Office"].index(prop['type']) if prop['type'] in ["Flat", "Plot", "Villa", "Commercial", "Office"] else 0)
                                    prop['location'] = st.text_input(f"Location {idx}", value=prop['location'])
                                    prop['area_sqft'] = st.number_input(f"Area (sqft) {idx}", value=prop['area_sqft'])
                                    prop['price'] = st.number_input(f"Price (₹) {idx}", value=prop['price'])
                                    prop['bedrooms'] = st.selectbox(f"BHK {idx}", ["Studio", "1 BHK", "2 BHK", "3 BHK", "4 BHK", "5+ BHK"],
                                                                   index=["Studio", "1 BHK", "2 BHK", "3 BHK", "4 BHK", "5+ BHK"].index(prop['bedrooms']) if prop['bedrooms'] in ["Studio", "1 BHK", "2 BHK", "3 BHK", "4 BHK", "5+ BHK"] else 2)
                                with col2:
                                    prop['furnished'] = st.selectbox(f"Furnished {idx}", ["No", "Yes", "Semi"],
                                                                   index=["No", "Yes", "Semi"].index(prop['furnished']) if prop['furnished'] in ["No", "Yes", "Semi"] else 0)
                                    prop['status'] = st.selectbox(f"Status {idx}", ["Available", "Sold", "Rented", "Under Negotiation"])
                                    prop['owner_name'] = st.text_input(f"Owner Name {idx}", value=prop['owner_name'])
                                    prop['owner_contact'] = st.text_input(f"Owner Contact {idx}", value=prop['owner_contact'])
                                    prop['remarks'] = st.text_area(f"Remarks {idx}", value=prop['remarks'])
                                
                                edited_properties.append(prop)
                        
                        if st.button("📥 Import All Parsed Properties", type="primary"):
                            success_count = 0
                            for idx, prop in enumerate(edited_properties):
                                new_property = {
                                    "id": f"PROP{len(properties)+idx+1:03d}",
                                    "type": prop['type'],
                                    "location": prop['location'],
                                    "area_sqft": prop['area_sqft'],
                                    "price": prop['price'],
                                    "bedrooms": prop['bedrooms'],
                                    "furnished": prop['furnished'],
                                    "status": prop['status'],
                                    "owner_name": prop['owner_name'],
                                    "owner_contact": prop['owner_contact'],
                                    "referral_name": "",
                                    "referral_reward": 0,
                                    "remarks": prop['remarks'],
                                    "date_added": datetime.now().strftime("%Y-%m-%d"),
                                    "import_source": "whatsapp"
                                }
                                properties.append(new_property)
                                success_count += 1
                            
                            save_data(PROPERTIES_FILE, properties)
                            st.success(f"✅ Successfully imported {success_count} properties from WhatsApp!")
                            st.rerun()
                    else:
                        st.warning("No properties could be parsed from the text. Please check the format.")
        
        st.markdown("---")
        
        # Add New Property
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
            referral_name = st.text_input("Referral Name (if any)")
            referral_reward = st.number_input("Referral Reward (₹)", min_value=0, value=0)
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
                    "referral_name": referral_name,
                    "referral_reward": referral_reward,
                    "remarks": remarks,
                    "date_added": datetime.now().strftime("%Y-%m-%d")
                }
                properties.append(new_property)
                save_data(PROPERTIES_FILE, properties)
                st.success(f"✅ Property {prop_id} added successfully!")
                st.rerun()
        
        st.markdown("---")
        
        # All Properties with Delete
        st.subheader("📋 All Properties")
        if properties:
            df = pd.DataFrame(properties)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                type_filter = st.multiselect("Filter by Type", options=df['type'].unique() if 'type' in df.columns else [])
            with col2:
                status_filter = st.multiselect("Filter by Status", options=df['status'].unique() if 'status' in df.columns else [])
            with col3:
                location_filter = st.text_input("Search Location")
            
            filtered_df = df.copy()
            if type_filter:
                filtered_df = filtered_df[filtered_df['type'].isin(type_filter)]
            if status_filter:
                filtered_df = filtered_df[filtered_df['status'].isin(status_filter)]
            if location_filter:
                filtered_df = filtered_df[filtered_df['location'].str.contains(location_filter, case=False, na=False)]
            
            st.dataframe(filtered_df, use_container_width=True)
            
            # Delete Property
            st.markdown("---")
            st.subheader("🗑️ Delete Property")
            st.warning("⚠️ This action cannot be undone!")
            
            prop_to_delete = st.selectbox(
                "Select Property to Delete", 
                [f"{p.get('id')} - {p.get('location', 'Unknown')} ({p.get('type', 'N/A')})" for p in properties]
            )
            
            col1, col2 = st.columns(2)
            with col1:
                confirm_delete = st.checkbox("I confirm I want to delete this property")
            with col2:
                if st.button("🗑️ Delete Property", type="secondary"):
                    if confirm_delete:
                        prop_id = prop_to_delete.split(' - ')[0]
                        properties = [p for p in properties if p.get('id') != prop_id]
                        save_data(PROPERTIES_FILE, properties)
                        st.success(f"✅ Property {prop_id} deleted successfully!")
                        st.rerun()
                    else:
                        st.error("❌ Please check the confirmation checkbox first")
        else:
            st.info("No properties added yet.")

    # ----- BUYERS -----
    elif page == "👤 Buyers":
        st.title("👤 Buyers Management")
        st.markdown("---")
        
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
        
        st.subheader("📋 All Buyers")
        if buyers:
            df = pd.DataFrame(buyers)
            
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
            
            # Delete Buyer
            st.markdown("---")
            st.subheader("🗑️ Delete Buyer")
            st.warning("⚠️ This action cannot be undone!")
            
            buyer_to_delete = st.selectbox(
                "Select Buyer to Delete", 
                [f"{b.get('id')} - {b.get('name', 'Unknown')} ({b.get('contact', 'N/A')})" for b in buyers]
            )
            
            col1, col2 = st.columns(2)
            with col1:
                confirm_delete = st.checkbox("I confirm I want to delete this buyer")
            with col2:
                if st.button("🗑️ Delete Buyer", type="secondary"):
                    if confirm_delete:
                        buyer_id = buyer_to_delete.split(' - ')[0]
                        buyers = [b for b in buyers if b.get('id') != buyer_id]
                        save_data(BUYERS_FILE, buyers)
                        st.success(f"✅ Buyer {buyer_id} deleted successfully!")
                        st.rerun()
                    else:
                        st.error("❌ Please check the confirmation checkbox first")
        else:
            st.info("No buyers added yet.")

    # ----- SELLERS -----
    elif page == "🏢 Sellers":
        st.title("🏢 Sellers Management")
        st.markdown("---")
        
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
        
        st.subheader("📋 All Sellers")
        if sellers:
            df = pd.DataFrame(sellers)
            st.dataframe(df, use_container_width=True)
            
            # Delete Seller
            st.markdown("---")
            st.subheader("🗑️ Delete Seller")
            st.warning("⚠️ This action cannot be undone!")
            
            seller_to_delete = st.selectbox(
                "Select Seller to Delete", 
                [f"{s.get('id')} - {s.get('name', 'Unknown')} ({s.get('contact', 'N/A')})" for s in sellers]
            )
            
            col1, col2 = st.columns(2)
            with col1:
                confirm_delete = st.checkbox("I confirm I want to delete this seller")
            with col2:
                if st.button("🗑️ Delete Seller", type="secondary"):
                    if confirm_delete:
                        seller_id = seller_to_delete.split(' - ')[0]
                        sellers = [s for s in sellers if s.get('id') != seller_id]
                        save_data(SELLERS_FILE, sellers)
                        st.success(f"✅ Seller {seller_id} deleted successfully!")
                        st.rerun()
                    else:
                        st.error("❌ Please check the confirmation checkbox first")
        else:
            st.info("No sellers added yet.")

    # ----- REFERRALS -----
    elif page == "🎁 Referrals":
        st.title("🎁 Referral Management Program")
        st.markdown("---")
        
        with st.expander("➕ Add New Referral", expanded=False):
            col1, col2 = st.columns(2)
            
            with col1:
                referral_id = st.text_input("Referral ID", value=f"REF{len(referrals)+1:03d}")
                referral_name = st.text_input("Referral Name")
                referral_contact = st.text_input("Contact Number")
                
            with col2:
                properties_referred = st.number_input("Properties Referred", min_value=0, value=1)
                total_reward = st.number_input("Total Reward Earned (₹)", min_value=0, value=0)
                status = st.selectbox("Status", ["Active", "Inactive"])
            
            remarks = st.text_area("Remarks")
            
            if st.button("💾 Save Referral", type="primary"):
                new_referral = {
                    "id": referral_id,
                    "name": referral_name,
                    "contact": referral_contact,
                    "properties_referred": properties_referred,
                    "total_reward": total_reward,
                    "status": status,
                    "remarks": remarks,
                    "date_added": datetime.now().strftime("%Y-%m-%d")
                }
                referrals.append(new_referral)
                save_data(REFERRALS_FILE, referrals)
                st.success(f"✅ Referral {referral_name} added successfully!")
                st.rerun()
        
        st.markdown("---")
        
        st.subheader("📋 All Referrals")
        if referrals:
            df = pd.DataFrame(referrals)
            st.dataframe(df, use_container_width=True)
            
            total_rewards = sum([r.get('total_reward', 0) for r in referrals])
            st.metric("Total Rewards Paid", f"₹{total_rewards:,.0f}")
        else:
            st.info("No referrals added yet.")

    # ----- REPORTS -----
    elif page == "📊 Reports":
        st.title("📊 Reports & Analytics")
        st.markdown("---")
        
        # Buyers Report
        st.subheader("📥 Download Buyers Report")
        if buyers:
            df_buyers = pd.DataFrame(buyers)
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("📊 Download All Buyers Excel"):
                    excel_data = to_excel(df_buyers, "Buyers")
                    st.download_button(
                        label="📥 Click to Download",
                        data=excel_data,
                        file_name=f"buyers_report_{datetime.now().strftime('%Y%m%d')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
            
            with col2:
                status_filter = st.selectbox("Filter by Status", ["All", "Active", "Closed", "On Hold"], key="buyer_status")
                if status_filter != "All":
                    filtered_buyers = df_buyers[df_buyers['status'] == status_filter]
                    if st.button(f"📊 Download {status_filter} Buyers"):
                        excel_data = to_excel(filtered_buyers, f"{status_filter}_Buyers")
                        st.download_button(
                            label="📥 Click to Download",
                            data=excel_data,
                            file_name=f"{status_filter.lower()}_buyers_{datetime.now().strftime('%Y%m%d')}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
        else:
            st.info("No buyers data available.")
        
        st.markdown("---")
        
        # Sellers Report
        st.subheader("📥 Download Sellers Report")
        if sellers:
            df_sellers = pd.DataFrame(sellers)
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("📊 Download All Sellers Excel"):
                    excel_data = to_excel(df_sellers, "Sellers")
                    st.download_button(
                        label="📥 Click to Download",
                        data=excel_data,
                        file_name=f"sellers_report_{datetime.now().strftime('%Y%m%d')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
            
            with col2:
                status_filter = st.selectbox("Filter Sellers by Status", ["All", "Active", "Sold", "On Hold"], key="seller_status")
                if status_filter != "All":
                    filtered_sellers = df_sellers[df_sellers['status'] == status_filter]
                    if st.button(f"📊 Download {status_filter} Sellers"):
                        excel_data = to_excel(filtered_sellers, f"{status_filter}_Sellers")
                        st.download_button(
                            label="📥 Click to Download",
                            data=excel_data,
                            file_name=f"{status_filter.lower()}_sellers_{datetime.now().strftime('%Y%m%d')}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
        else:
            st.info("No sellers data available.")
        
        st.markdown("---")
        
        # Properties Report
        st.subheader("📥 Download Properties Report")
        if properties:
            df_props = pd.DataFrame(properties)
            
            if st.button("📊 Download All Properties Excel"):
                excel_data = to_excel(df_props, "Properties")
                st.download_button(
                    label="📥 Click to Download",
                    data=excel_data,
                    file_name=f"properties_report_{datetime.now().strftime('%Y%m%d')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
        else:
            st.info("No properties data available.")

    # ----- SEARCH & MATCH -----
    elif page == "🔍 Search & Match":
        st.title("🔍 Search & Match")
        st.markdown("---")
        
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
                buyer_names = [f"{b.get('name')} ({b.get('id')})" for b in buyers if b.get('status') == 'Active']
                if buyer_names:
                    selected_buyer = st.selectbox("Select Buyer", buyer_names)
                    
                    if st.button("🔍 Find Matching Properties", type="primary"):
                        buyer_id = selected_buyer.split('(')[-1].replace(')', '')
                        buyer = next((b for b in buyers if b.get('id') == buyer_id), None)
                        
                        if buyer:
                            st.write(f"**Buyer:** {buyer.get('name')}")
                            st.write(f"**Budget:** ₹{buyer.get('budget_min', 0):,.0f} - ₹{buyer.get('budget_max', 0):,.0f}")
                            st.write(f"**Type Needed:** {buyer.get('type_needed')}")
                            st.write(f"**Preferred Location:** {buyer.get('preferred_location')}")
                            
                            matches = []
                            for prop in properties:
                                if prop.get('status') != 'Available':
                                    continue
                                
                                price = prop.get('price', 0)
                                if not (buyer.get('budget_min', 0) <= price <= buyer.get('budget_max', float('inf'))):
                                    continue
                                
                                if buyer.get('type_needed') != 'Any' and prop.get('type') != buyer.get('type_needed'):
                                    continue
                                
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
                        
                        seller_properties = [p for p in properties if seller.get('name').lower() in p.get('owner_name', '').lower()]
                        
                        if seller_properties:
                            st.success(f"Found {len(seller_properties)} properties")
                            st.dataframe(pd.DataFrame(seller_properties), use_container_width=True)
                        else:
                            st.warning("No properties found for this seller.")
            else:
                st.info("No sellers in database.")

    # ----- INQUIRIES (Admin View) -----
    elif page == "📞 Inquiries":
        st.title("📞 Customer Inquiries")
        st.markdown("---")
        
        if inquiries:
            df_inquiries = pd.DataFrame(inquiries)
            
            # Filters
            col1, col2 = st.columns(2)
            with col1:
                status_filter = st.selectbox("Filter by Status", ["All", "New", "In Progress", "Resolved", "Closed"])
            with col2:
                inquiry_type_filter = st.selectbox("Filter by Type", ["All", "General", "Property", "Buy", "Sell", "Other"])
            
            filtered_df = df_inquiries.copy()
            if status_filter != "All":
                filtered_df = filtered_df[filtered_df['status'] == status_filter]
            if inquiry_type_filter != "All":
                filtered_df = filtered_df[filtered_df['inquiry_type'] == inquiry_type_filter]
            
            st.dataframe(filtered_df, use_container_width=True)
            
            # Delete Inquiry
            st.markdown("---")
            st.subheader("🗑️ Delete Inquiry")
            st.warning("⚠️ This action cannot be undone!")
            
            inquiry_to_delete = st.selectbox(
                "Select Inquiry to Delete", 
                [f"{i.get('id')} - {i.get('name', 'Unknown')} ({i.get('inquiry_type', 'N/A')})" for i in inquiries]
            )
            
            col1, col2 = st.columns(2)
            with col1:
                confirm_delete = st.checkbox("I confirm I want to delete this inquiry")
            with col2:
                if st.button("🗑️ Delete Inquiry", type="secondary"):
                    if confirm_delete:
                        inquiry_id = inquiry_to_delete.split(' - ')[0]
                        inquiries = [i for i in inquiries if i.get('id') != inquiry_id]
                        save_data(INQUIRIES_FILE, inquiries)
                        st.success(f"✅ Inquiry {inquiry_id} deleted successfully!")
                        st.rerun()
                    else:
                        st.error("❌ Please check the confirmation checkbox first")
            
            st.markdown("---")
            st.subheader("🔄 Update Inquiry Status")
            inquiry_ids = [f"{i.get('id')} - {i.get('name', 'Unknown')}" for i in inquiries]
            if inquiry_ids:
                selected_inquiry = st.selectbox("Select Inquiry", inquiry_ids)
                new_status = st.selectbox("New Status", ["New", "In Progress", "Resolved", "Closed"])
                admin_remarks = st.text_area("Admin Remarks/Notes")
                
                if st.button("💾 Update Status", type="primary"):
                    inquiry_id = selected_inquiry.split(' - ')[0]
                    for inquiry in inquiries:
                        if inquiry.get('id') == inquiry_id:
                            inquiry['status'] = new_status
                            inquiry['admin_remarks'] = admin_remarks
                            inquiry['updated_date'] = datetime.now().strftime("%Y-%m-%d")
                            break
                    save_data(INQUIRIES_FILE, inquiries)
                    st.success(f"✅ Inquiry {inquiry_id} updated successfully!")
                    st.rerun()
            
            # Export inquiries
            st.markdown("---")
            if st.button("📊 Download All Inquiries Excel"):
                excel_data = to_excel(df_inquiries, "Inquiries")
                st.download_button(
                    label="📥 Click to Download",
                    data=excel_data,
                    file_name=f"inquiries_report_{datetime.now().strftime('%Y%m%d')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
        else:
            st.info("No inquiries received yet.")
            st.info("Users can submit inquiries from the 'Contact Us' page.")

    # ----- SETTINGS (Password Change - Admin Only) -----
    elif page == "⚙️ Settings":
        st.title("⚙️ Settings")
        st.markdown("---")
        
        st.subheader("🔐 Change Password")
        
        current_password = st.text_input("Current Password", type="password")
        new_password = st.text_input("New Password", type="password")
        confirm_password = st.text_input("Confirm New Password", type="password")
        
        if st.button("💾 Update Password", type="primary"):
            if not current_password or not new_password or not confirm_password:
                st.error("❌ Please fill all fields")
            elif not verify_credentials(st.session_state.username, current_password):
                st.error("❌ Current password is incorrect")
            elif new_password != confirm_password:
                st.error("❌ New passwords do not match")
            elif len(new_password) < 6:
                st.error("❌ Password must be at least 6 characters")
            else:
                update_password(st.session_state.username, new_password)
                st.success(f"✅ Password updated successfully for {st.session_state.username}!")
                st.info("Please logout and login again with your new password.")

# ============== USER PAGES (Login Required - Submit Property/Requirement) ==============
if st.session_state.logged_in and st.session_state.user_role == "user":
    
    # ----- SUBMIT PROPERTY -----
    if page == "📝 Submit Property":
        st.title("📝 Submit Your Property")
        st.markdown("---")
        st.info("Fill in your property details below. Our team will review and contact you.")
        
        col1, col2 = st.columns(2)
        
        with col1:
            prop_type = st.selectbox("Property Type", ["Flat", "Plot", "Villa", "Commercial", "Office"])
            location = st.text_input("Location")
            area_sqft = st.number_input("Area (sq ft)", min_value=0, value=1000)
            
        with col2:
            price = st.number_input("Expected Price (₹)", min_value=0, value=5000000)
            bedrooms = st.selectbox("Bedrooms", ["Studio", "1 BHK", "2 BHK", "3 BHK", "4 BHK", "5+ BHK"])
            furnished = st.selectbox("Furnished", ["Yes", "No", "Semi"])
        
        owner_name = st.text_input("Your Name")
        owner_contact = st.text_input("Your Contact Number")
        remarks = st.text_area("Additional Details")
        
        if st.button("📤 Submit Property", type="primary"):
            new_property = {
                "id": f"PROP{len(properties)+1:03d}",
                "type": prop_type,
                "location": location,
                "area_sqft": area_sqft,
                "price": price,
                "bedrooms": bedrooms,
                "furnished": furnished,
                "status": "Under Review",
                "owner_name": owner_name,
                "owner_contact": owner_contact,
                "referral_name": "",
                "referral_reward": 0,
                "remarks": remarks,
                "date_added": datetime.now().strftime("%Y-%m-%d"),
                "submitted_by": st.session_state.username
            }
            properties.append(new_property)
            save_data(PROPERTIES_FILE, properties)
            st.success("✅ Property submitted successfully! Our team will contact you soon.")
    
    # ----- SUBMIT REQUIREMENT -----
    elif page == "📝 Submit Requirement":
        st.title("📝 Submit Your Requirement")
        st.markdown("---")
        st.info("Tell us what you're looking for. We'll find matching properties for you.")
        
        col1, col2 = st.columns(2)
        
        with col1:
            buyer_name = st.text_input("Your Name")
            buyer_contact = st.text_input("Contact Number")
            buyer_email = st.text_input("Email")
            
        with col2:
            budget_min = st.number_input("Budget Min (₹)", min_value=0, value=3000000)
            budget_max = st.number_input("Budget Max (₹)", min_value=0, value=10000000)
            type_needed = st.selectbox("Property Type Needed", ["Flat", "Plot", "Villa", "Commercial", "Any"])
        
        preferred_location = st.text_input("Preferred Location")
        requirements = st.text_area("Specific Requirements (BHK, Area, etc.)")
        
        if st.button("📤 Submit Requirement", type="primary"):
            new_buyer = {
                "id": f"BUY{len(buyers)+1:03d}",
                "name": buyer_name,
                "contact": buyer_contact,
                "email": buyer_email,
                "budget_min": budget_min,
                "budget_max": budget_max,
                "type_needed": type_needed,
                "preferred_location": preferred_location,
                "requirements": requirements,
                "status": "Active",
                "follow_up_date": datetime.now().strftime("%Y-%m-%d"),
                "remarks": "",
                "date_added": datetime.now().strftime("%Y-%m-%d"),
                "submitted_by": st.session_state.username
            }
            buyers.append(new_buyer)
            save_data(BUYERS_FILE, buyers)
            st.success("✅ Requirement submitted successfully! We'll find matching properties for you.")

# Footer
st.sidebar.markdown("---")
if st.session_state.logged_in:
    st.sidebar.info("PinkCityEstate.in CRM v2.0")
else:
    st.sidebar.info("PinkCityEstate.in - Public Access")
st.sidebar.caption("© 2026 All rights reserved.")
