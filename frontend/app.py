import streamlit as st
import requests
import pandas as pd
import os
from datetime import datetime

# Import the separated modules
from customer import render_customer_view, customer_pages
from admin import render_admin_view, admin_pages

# Import shared functions
from shared import load_product_data, call_api, get_categories, get_subcategories, get_article_types

# Initialize session state
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'customer_home'
if 'customer_page' not in st.session_state:
    st.session_state.customer_page = 'home'
if 'admin_page' not in st.session_state:
    st.session_state.admin_page = 'dashboard'
if 'selected_category' not in st.session_state:
    st.session_state.selected_category = None
if 'selected_subcategory' not in st.session_state:
    st.session_state.selected_subcategory = None
if 'selected_article_type' not in st.session_state:
    st.session_state.selected_article_type = None
if 'selected_tag' not in st.session_state:
    st.session_state.selected_tag = None
if 'search_results' not in st.session_state:
    st.session_state.search_results = None
if 'product_data' not in st.session_state:
    st.session_state.product_data = None
if 'admin_data' not in st.session_state:
    st.session_state.admin_data = None
if 'agent_results' not in st.session_state:
    st.session_state.agent_results = {}
if 'relevant_products' not in st.session_state:
    st.session_state.relevant_products = None

def main():
    """Main application router"""
    # Sidebar navigation
    with st.sidebar:
        st.title("🛍️ Product AI")
        st.markdown("---")
        
        # Main navigation
        view_type = st.radio("Select View", ["Customer", "Admin"])
        
        if view_type == "Customer":
            st.session_state.current_page = 'customer_home'
            # Customer sub-navigation
            st.markdown("### Customer Pages")
            selected_customer_page = st.radio("Go to", customer_pages, key="customer_nav")
            
            if selected_customer_page == "Home":
                st.session_state.customer_page = 'home'
            elif selected_customer_page == "AI Search":
                st.session_state.customer_page = 'ai_search'
            elif selected_customer_page == "Browse":
                st.session_state.customer_page = 'browse'
            elif selected_customer_page == "Tags":
                st.session_state.customer_page = 'tags'
                
        else:
            st.session_state.current_page = 'admin_dashboard'
            # Admin sub-navigation
            st.markdown("### Admin Pages")
            selected_admin_page = st.radio("Go to", admin_pages, key="admin_nav")
            
            if selected_admin_page == "Dashboard":
                st.session_state.admin_page = 'dashboard'
        
            elif selected_admin_page == "Analytics":
                st.session_state.admin_page = 'analytics'
            
            elif selected_admin_page == "Add Product":
                st.session_state.admin_page = 'add_product'
        
        st.markdown("---")
        st.write("**API Status:**")
        try:
            from shared import API_BASE_URL
            health = requests.get(f"{API_BASE_URL}/health", timeout=5).json()
            st.success("✅ API Connected")
            st.caption(f"Model: {health.get('model', 'Unknown')}")
        except:
            st.error("❌ API Offline")
            st.info("Running in demo mode with sample data")
        
        # Data status
        st.write("**Data Status:**")
        try:
            df = load_product_data()
            st.success(f"✅ Loaded {len(df)} products")
            st.caption(f"Categories: {df['masterCategory'].nunique()}")
        except:
            st.error("❌ Data load failed")
        
        st.markdown("---")
        st.caption(f"© {datetime.now().year} Product AI System")

    # Render the appropriate view
    if st.session_state.current_page == 'customer_home':
        render_customer_view()
    else:
        render_admin_view()

if __name__ == "__main__":
    main()