import streamlit as st
import pandas as pd
import plotly.express as px
import re
import os

# Import shared functions from shared module
from shared import load_product_data, call_api, get_categories, get_subcategories, get_article_types

admin_pages = ["Dashboard", "Analytics", "Add Product"]

def admin_dashboard_page():
    """Admin dashboard overview"""
    st.title("👨‍💼 Admin Dashboard")
    st.write("Welcome to the admin panel. Manage your product catalog efficiently.")
    
    # Load data
    if st.session_state.admin_data is None:
        st.session_state.admin_data = load_product_data()
    
    df = st.session_state.admin_data
    
    # Quick stats
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Products", len(df))
    with col2:
        st.metric("Categories", df['masterCategory'].nunique())
    with col3:
        st.metric("Subcategories", df['subCategory'].nunique())
    
    # Recent activity section
    st.subheader("📊 Quick Actions")
    
    action_cols = st.columns(3)
    
    with action_cols[0]:
        if st.button("📈 Analytics", use_container_width=True):
            st.session_state.admin_page = 'analytics'
            st.rerun()
    
    with action_cols[1]:
        if st.button("➕ Add Product", use_container_width=True):
            st.session_state.admin_page = 'add_product'
            st.rerun()
    
    with action_cols[2]:
        if st.button("🔄 Refresh Data", use_container_width=True, help="Reload product data from source"):
            st.session_state.admin_data = load_product_data()
            st.session_state.search_results = None
            st.success("Data refreshed!")
    
    # Recent products
    st.subheader("🆕 Recent Products")
    if not df.empty:
        recent_products = df.head(5)
        for _, product in recent_products.iterrows():
            st.write(f"**{product.get('productDisplayName', 'Unnamed')}** - {product.get('masterCategory', 'Unknown')}")
    else:
        st.info("No products available")

def admin_analytics_page():
    """Admin analytics page"""
    st.title("📈 Analytics & Insights")
    
    if st.button("← Back to Dashboard"):
        st.session_state.admin_page = 'dashboard'
        st.rerun()
    
    df = st.session_state.admin_data
    
    # Visualizations
    col1, col2 = st.columns(2)
    
    with col1:
        # Category distribution
        if 'masterCategory' in df:
            category_counts = df['masterCategory'].value_counts()
            fig = px.pie(values=category_counts.values, names=category_counts.index, 
                         title="Product Distribution by Category")
            st.plotly_chart(fig)
    
    with col2:
        # Gender distribution
        if 'gender' in df:
            gender_counts = df['gender'].value_counts()
            fig = px.pie(values=gender_counts.values, names=gender_counts.index, 
                         title="Product Distribution by Gender")
            st.plotly_chart(fig)
    
    col3, col4 = st.columns(2)
    
    with col3:
        # Season distribution
        if 'season' in df:
            season_counts = df['season'].value_counts()
            fig = px.bar(x=season_counts.index, y=season_counts.values, 
                        title="Products by Season", labels={'x': 'Season', 'y': 'Count'})
            st.plotly_chart(fig)
    
    with col4:
        # Usage distribution
        if 'usage' in df:
            usage_counts = df['usage'].value_counts()
            fig = px.bar(x=usage_counts.index, y=usage_counts.values, 
                        title="Products by Usage", labels={'x': 'Usage', 'y': 'Count'})
            st.plotly_chart(fig)

def admin_add_product_page():
    """Admin add new product page with MongoDB integration"""
    st.title("➕ Add New Product")
    
    if st.button("← Back to Dashboard"):
        st.session_state.admin_page = 'dashboard'
        st.rerun()
    
    st.subheader("Product Information")
    
    # Custom CSS to remove borders and style like the image
    st.markdown("""
    <style>
    .stForm {
        border: none !important;
        box-shadow: none !important;
    }
    .stForm > div {
        border: none !important;
        padding: 0 !important;
    }
    .stTextInput > div > div > input {
        border: 1px solid #ddd !important;
        border-radius: 4px !important;
    }
    .stTextArea > div > div > textarea {
        border: 1px solid #ddd !important;
        border-radius: 4px !important;
    }
    .stButton > button {
        background-color: #007bff !important;
        color: white !important;
        border: none !important;
        border-radius: 4px !important;
        padding: 8px 16px !important;
        font-weight: 500 !important;
    }
    .stButton > button:hover {
        background-color: #0056b3 !important;
    }
    .product-card {
        border: 1px solid #ddd;
        border-radius: 8px;
        padding: 16px;
        margin: 8px 0;
        background-color: #f9f9f9;
    }
    .product-table {
        margin-top: 20px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    with st.form("add_product_form"):
        # Product Name (Required)
        product_name = st.text_input("Product Name*", placeholder="e.g., Nike Men Black T-shirt", help="Enter the name of the product")
        
        # Product Description (Required)
        product_description = st.text_area("Product Description*", placeholder="Describe the product (color, gender, category, subcategory, brand, usage, type).\nExample: 'Men black cotton T-shirt by Nike for casual wear, apparel/topwear.'", help="Describe the product features and details", height=100)
        
        # Image URL (Optional)
        image_url = st.text_input("Image URL", placeholder="https://.../image.jpg(optional)", help="Optional: Enter the URL of the product image")
        
        submitted = st.form_submit_button("Add Product with AI Categorization", type="primary")
    
    if submitted:
        if not product_name or not product_description:
            st.error("Product name and description are required!")
        else:
            # Use AI to process the product description and extract attributes
            with st.spinner("🤖 AI is analyzing the product description and extracting attributes..."):
                # Call the orchestrator API to get AI-generated attributes
                ai_result = call_api("/orchestrator/process", {"description": product_description})
                
                if ai_result:
                    # Extract AI-generated attributes
                    classification = ai_result.get('classification', {})
                    attributes = ai_result.get('attributes', {}).get('attributes', {})
                    
                    # Helper function to extract values from nested structure
                    def extract_value(attr_dict, key):
                        if isinstance(attr_dict, dict):
                            if key in attr_dict:
                                value = attr_dict[key]
                                if isinstance(value, dict) and 'value' in value:
                                    return value['value']
                                return value
                        return ''
                    
                    # Enhanced fallback function to extract basic info from description and entities
                    def extract_from_description(desc, name, entities=None):
                        desc_lower = desc.lower()
                        name_lower = name.lower()
                        
                        # Combine description and entities for better extraction
                        all_text = desc_lower
                        if entities:
                            all_text += ' ' + ' '.join(entities).lower()
                        
                        # Extract gender - improved logic with word boundaries
                        gender = 'Unisex' 
                        
                        # Check for men indicators
                        men_words = ['men', 'male', 'man', 'mens', 'guy', 'boys', 'boy', 'men\'s', 'mens\'', 'guys\'', 'boys\'']
                        women_words = ['women', 'female', 'woman', 'womens', 'lady', 'ladies', 'girls', 'girl', 'women\'s', 'womens\'', 'ladies\'', 'girls\'', 'females']
                        
                        # Use word boundaries to avoid substring matches
                        men_count = sum(1 for word in men_words if re.search(r'\b' + re.escape(word) + r'\b', all_text))
                        women_count = sum(1 for word in women_words if re.search(r'\b' + re.escape(word) + r'\b', all_text))
                        
                        if men_count > women_count:
                            gender = 'Men'
                        elif women_count > men_count:
                            gender = 'Women'
                        elif men_count > 0 and women_count > 0:
                            gender = 'Unisex'  
                        else:
                            # Check product name as well
                            name_men_count = sum(1 for word in men_words if re.search(r'\b' + re.escape(word) + r'\b', name_lower))
                            name_women_count = sum(1 for word in women_words if re.search(r'\b' + re.escape(word) + r'\b', name_lower))
                            
                            if name_men_count > name_women_count:
                                gender = 'Men'
                            elif name_women_count > name_men_count:
                                gender = 'Women'
                            else:
                                gender = 'Unisex'  
                        
                        # Extract color
                        colors = ['black', 'white', 'blue', 'red', 'green', 'yellow', 'pink', 'purple', 'brown', 'gray', 'grey', 'orange', 'navy', 'beige', 'tan', 'silver', 'gold']
                        color = ''
                        for c in colors:
                            if c in all_text:
                                color = c.title()
                                break
                        
                        # Extract category
                        if any(word in all_text for word in ['shoe', 'shoes', 'footwear', 'sneaker', 'boot', 'sandal']):
                            category = 'Footwear'
                            subcategory = 'Shoes'
                        elif any(word in all_text for word in ['shirt', 't-shirt', 'tshirt', 'top', 'blouse', 'dress', 'pants', 'jeans', 'trouser', 'shorts', 'skirt']):
                            category = 'Apparel'
                            if any(word in all_text for word in ['shirt', 't-shirt', 'tshirt', 'top', 'blouse']):
                                subcategory = 'Topwear'
                            elif any(word in all_text for word in ['pants', 'jeans', 'trouser', 'shorts', 'skirt']):
                                subcategory = 'Bottomwear'
                            else:
                                subcategory = 'Topwear'
                        elif any(word in all_text for word in ['watch', 'bag', 'hat', 'cap', 'belt', 'accessory', 'jewelry']):
                            category = 'Accessories'
                            subcategory = 'Watches' if 'watch' in all_text else 'Bags'
                        else:
                            category = 'Apparel'  # Default
                            subcategory = 'Topwear'
                        
                        # Extract article type
                        if 'shoe' in all_text or 'sneaker' in all_text or 'boot' in all_text:
                            article_type = 'Shoes'
                        elif 'shirt' in all_text or 't-shirt' in all_text:
                            article_type = 'Shirts'
                        elif 'pants' in all_text or 'jeans' in all_text:
                            article_type = 'Pants'
                        elif 'dress' in all_text:
                            article_type = 'Dresses'
                        elif 'shorts' in all_text:
                            article_type = 'Shorts'
                        elif 'skirt' in all_text:
                            article_type = 'Skirts'
                        elif 'watch' in all_text:
                            article_type = 'Watches'
                        elif 'bag' in all_text:
                            article_type = 'Bags'
                        else:
                            article_type = 'Shoes' if category == 'Footwear' else 'Shirts'
                        
                        # Extract usage
                        if any(word in all_text for word in ['casual', 'everyday', 'daily']):
                            usage = 'Casual'
                        elif any(word in all_text for word in ['sport', 'sports', 'athletic', 'running', 'gym', 'fitness']):
                            usage = 'Sports'
                        elif any(word in all_text for word in ['formal', 'business', 'office', 'dress']):
                            usage = 'Formal'
                        elif any(word in all_text for word in ['party', 'evening', 'night']):
                            usage = 'Party'
                        else:
                            usage = 'Casual'  
                        
                        # Extract season
                        if any(word in all_text for word in ['summer', 'hot', 'warm']):
                            season = 'Summer'
                        elif any(word in all_text for word in ['winter', 'cold', 'warm']):
                            season = 'Winter'
                        elif any(word in all_text for word in ['spring', 'fall', 'autumn']):
                            season = 'Spring' if 'spring' in all_text else 'Fall'
                        else:
                            season = 'All Season'
                        
                        return {
                            'gender': gender,
                            'color': color,
                            'category': category,
                            'subcategory': subcategory,
                            'article_type': article_type,
                            'usage': usage,
                            'season': season
                        }
                    
                    # Get AI results
                    ai_gender = extract_value(attributes, 'gender')
                    ai_category = classification.get('category', '')
                    ai_subcategory = classification.get('subcategory', '')
                    ai_article_type = extract_value(attributes, 'articleType')
                    ai_color = extract_value(attributes, 'baseColour')
                    ai_usage = extract_value(attributes, 'usage')
                    
                    # Get entities from AI result for better extraction
                    entities = ai_result.get('attributes', {}).get('entities', [])
                    
                    # Get fallback results using entities
                    fallback = extract_from_description(product_description, product_name, entities)
                    
                    # Use AI results if available and not "Unknown", otherwise use fallback
                    product_data = {
                        "productDisplayName": product_name,
                        "description": product_description,
                        "gender": ai_gender if ai_gender and ai_gender != 'Unknown' else fallback['gender'],
                        "masterCategory": ai_category if ai_category and ai_category != 'Unknown' else fallback['category'],
                        "subCategory": ai_subcategory if ai_subcategory and ai_subcategory != 'Unknown' else fallback['subcategory'],
                        "articleType": ai_article_type if ai_article_type and ai_article_type != 'Unknown' else fallback['article_type'],
                        "baseColour": ai_color if ai_color and ai_color != 'Unknown' else fallback['color'],
                        "season": extract_value(attributes, 'season') if extract_value(attributes, 'season') != 'Unknown' else fallback['season'],
                        "year": extract_value(attributes, 'year') or 2025,
                        "usage": ai_usage if ai_usage and ai_usage != 'Unknown' else fallback['usage'],
                        "link": image_url if image_url else '',
                        "filename": f"{product_name.replace(' ', '_').lower()}.jpg" if not image_url else ""
                    }
                    
                    # Call API to add product to MongoDB
                    result = call_api("/products/add", product_data)
                    
                    if result and result.get("success"):
                        st.success(f"✅ Product added successfully! ID: {result.get('product_id')}")
                        
                        # Show the added product details
                        st.subheader("🎉 Product Added Successfully!")
                        added_product = result.get("product", {})
                        
                        # Display in a nice format
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown("**📋 Product Details:**")
                            st.write(f"**ID:** {added_product.get('id')}")
                            st.write(f"**Name:** {added_product.get('productDisplayName')}")
                            st.write(f"**Description:** {product_description}")
                            st.write(f"**Gender:** {added_product.get('gender') or 'Not specified'}")
                            st.write(f"**Category:** {added_product.get('masterCategory') or 'Not specified'}")
                        
                        with col2:
                            st.markdown("**🏷️ AI-Generated Attributes:**")
                            st.write(f"**Subcategory:** {added_product.get('subCategory') or 'Not specified'}")
                            st.write(f"**Type:** {added_product.get('articleType') or 'Not specified'}")
                            st.write(f"**Color:** {added_product.get('baseColour') or 'Not specified'}")
                            st.write(f"**Season:** {added_product.get('season') or 'Not specified'}")
                            st.write(f"**Usage:** {added_product.get('usage') or 'Not specified'}")
                            st.write(f"**Year:** {added_product.get('year') or 'Not specified'}")
                        
                        # Show AI confidence if available
                        if classification.get('confidence'):
                            st.info(f"🤖 AI Classification Confidence: {classification.get('confidence', 0):.1%}")
                        
                        # Store the added product in session state for display
                        if 'added_products' not in st.session_state:
                            st.session_state.added_products = []
                        st.session_state.added_products.append(added_product)
                        
                        # Show success toast
                        st.toast("🎉 Product added successfully!", icon="✅")
                        
                        if st.button("➕ Add Another Product"):
                            st.rerun()
                    else:
                        st.error(f"❌ Failed to add product: {result.get('detail', 'Unknown error') if result else 'No response from server'}")
                else:
                    st.error("❌ Failed to process product description with AI. Please try again.")
    
    # Display recently added products in a table
    if 'added_products' in st.session_state and st.session_state.added_products:
        st.markdown("---")
        st.subheader("📋 Recently Added Products")
        st.markdown('<div class="product-table">', unsafe_allow_html=True)
        
        # Create a DataFrame for better display
        products_df = pd.DataFrame(st.session_state.added_products)
        
        # Select relevant columns for display
        display_columns = ['productDisplayName', 'masterCategory', 'subCategory', 'articleType', 'gender', 'baseColour', 'usage']
        available_columns = [col for col in display_columns if col in products_df.columns]
        
        if available_columns:
            st.dataframe(
                products_df[available_columns],
                use_container_width=True,
                hide_index=True
            )
        
        # Show individual product cards
        st.subheader("📦 Product Details")
        for i, product in enumerate(st.session_state.added_products):
            with st.expander(f"Product {i+1}: {product.get('productDisplayName', 'Unnamed Product')}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**ID:** {product.get('id', 'N/A')}")
                    st.write(f"**Name:** {product.get('productDisplayName', 'N/A')}")
                    st.write(f"**Description:** {product.get('description', 'N/A')}")
                    st.write(f"**Gender:** {product.get('gender', 'N/A')}")
                    st.write(f"**Category:** {product.get('masterCategory', 'N/A')}")
                
                with col2:
                    st.write(f"**Subcategory:** {product.get('subCategory', 'N/A')}")
                    st.write(f"**Type:** {product.get('articleType', 'N/A')}")
                    st.write(f"**Color:** {product.get('baseColour', 'N/A')}")
                    st.write(f"**Season:** {product.get('season', 'N/A')}")
                    st.write(f"**Usage:** {product.get('usage', 'N/A')}")
                    st.write(f"**Year:** {product.get('year', 'N/A')}")
                
                # Show image if available
                if product.get('link'):
                    try:
                        st.image(product['link'], width=200, caption="Product Image")
                    except:
                        st.write("Image not available")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Clear products button
        if st.button("🗑️ Clear Product History"):
            st.session_state.added_products = []
            st.rerun()

def render_admin_view():
    """Render the appropriate admin page"""
    if st.session_state.admin_page == 'dashboard':
        admin_dashboard_page()
    elif st.session_state.admin_page == 'analytics':
        admin_analytics_page()
    elif st.session_state.admin_page == 'add_product':
        admin_add_product_page()