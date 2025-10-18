import streamlit as st
import pandas as pd
import ollama

# Import shared functions from shared module
from shared import load_product_data, call_api, get_categories, get_subcategories, get_article_types

# Try to import from src.utils.api, fallback to mock function if not available
try:
    from src.utils.api import get_recommended_products
except ImportError:
    def get_recommended_products(description, df, top_n=5):
        """Fallback function if src.utils.api is not available"""
        st.warning("Using fallback recommendation function")
        return df.head(top_n)

customer_pages = ["Home", "AI Search", "Browse", "Tags"]

def display_products(df, category=None, subcategory=None, article_type=None, tag=None):
    """Display products in a grid layout like an e-commerce shop page"""
    if df is None or df.empty:
        st.info("No products found.")
        return

    # Apply filters
    if category:
        df = df[df['masterCategory'] == category]
    if subcategory:
        df = df[df['subCategory'] == subcategory]
    if article_type:
        df = df[df['articleType'] == article_type]
    if tag:
        df = df[df['tags'].apply(lambda x: tag in x if isinstance(x, list) else False)]

    if df.empty:
        st.info("No products found with the selected criteria.")
        return

    # Show in grid 
    num_cols = 3
    for i in range(0, len(df), num_cols):
        cols = st.columns(num_cols)
        for j, product in enumerate(df.iloc[i:i+num_cols].iterrows()):
            _, prod = product
            with cols[j]:
                # Product image
                if 'link' in prod and isinstance(prod['link'], str) and prod['link'].strip():
                    if prod.get('link') and prod['link'] != 'undefined' and prod['link'].strip():
                        try:
                            st.image(prod['link'], width=200)
                        except:
                            st.image("https://via.placeholder.com/200x200?text=No+Image", width=200)
                    else:
                        st.image("https://via.placeholder.com/200x200?text=No+Image", width=200)

                # Product title
                st.markdown(f"**{prod.get('productDisplayName', 'Unnamed Product')}**")

                # Price 
                price = prod.get("price", None)
                if price:
                    st.write(f"💰 LKR {price:,.2f}")
                else:
                    st.write("💰 Price on request")

                 # Tags 
                if 'tags' in prod and isinstance(prod['tags'], list) and len(prod['tags']) > 0:
                    for i, t in enumerate(prod['tags']):
                        key = f"tag_{prod['id']}_{i}"
                        if st.button(f"#{t}", key=key):
                            st.session_state.selected_tag = t
                            st.session_state.customer_page = 'tag_products'
                            st.rerun()

                # View button
                if st.button("View Details", key=f"view_{prod['id']}"):
                    st.session_state.selected_product = prod.to_dict()
                    st.session_state.customer_page = 'product_detail'
                    st.rerun()

def generate_summary(description: str) -> str:
    """Generate summary using Ollama"""
    try:
        response = ollama.chat(
            model="gemma3:270m",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": f"Summarize this shopping request in 1-2 short sentences: {description}"}
            ]
        )
        return response.get("message", {}).get("content") or response.get("content") or "⚠️ Could not parse summary."
    except Exception as e:
        return f"⚠️ Could not generate summary ({e})"

def customer_home_page():
    """Customer home page"""
    st.title("🛍️ Welcome to Product AI")
    st.write("Discover the perfect products with AI-powered search and recommendations!")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔍 AI Search", use_container_width=True, help="Describe what you're looking for"):
            st.session_state.customer_page = 'ai_search'
            st.rerun()
    
    with col2:
        if st.button("📂 Browse Categories", use_container_width=True, help="Browse by product categories"):
            st.session_state.customer_page = 'browse'
            st.rerun()
    
    with col3:
        if st.button("🏷️ Popular Tags", use_container_width=True, help="Browse by popular tags"):
            st.session_state.customer_page = 'tags'
            st.rerun()
    
    st.markdown("---")
    st.subheader("🎯 Featured Products")
    
    df = load_product_data()
    if df is not None and not df.empty:
        # Show random sample of products
        sample_products = df.sample(min(6, len(df)))
        display_products(sample_products)
    else:
        st.info("No products available at the moment.")

def customer_ai_search_page():
    st.title("🔍 AI Product Search")

    if st.button("← Back to Home"):
        st.session_state.customer_page = 'home'
        st.rerun()

    description = st.text_area(
        "Describe what you're looking for:",
        placeholder="e.g., 'I need comfortable blue jeans for casual wear'",
        height=100
    )

    if st.button("Find Products", type="primary"):
        if not description:
            st.warning("Please enter a product description.")
            return

        # Check cache first for faster response
        cache_key = f"search_{description}"
        if cache_key in st.session_state:
            st.success("Found matching products! (from cache)")
            recommended_df = st.session_state[cache_key]
        else:
            # Skip all heavy processing for instant response
            summary_text = description

            st.session_state.product_data = summary_text
            st.success("Found matching products!")

            # Display summary
            st.subheader("📝 Customer Request Summary")
            st.write(summary_text)

            # Load products and get recommendations using ORIGINAL query for better accuracy
            df = load_product_data()
            
            recommended_df = get_recommended_products(description, df, top_n=2)  # Minimal results for speed
            
            # Cache the results
            st.session_state[cache_key] = recommended_df

        if recommended_df.empty:
            st.info("No recommended products found.")
        else:
            # Separate exact matches and other recommendations
            exact_matches = recommended_df[recommended_df.get('match_type', 'related') == 'exact']
            other_recommendations = recommended_df[recommended_df.get('match_type', 'related') == 'related']
            
            # Display Exact Matches
            if not exact_matches.empty:
                st.subheader("🎯 Exactly Match Your Search")
                st.markdown("*Products that match both color and type from your search*")
                
                for idx, row in exact_matches.iterrows():
                    name = row.get("productDisplayName") or "Unnamed Product"
                    article_type = row.get("articleType") or ""
                    colour = row.get("baseColour") or ""
                    usage = row.get("usage") or ""
                    link = row.get("link") or ""
                    filename = row.get("filename") or ""

                    # Create a container for each product
                    with st.container():
                        col1, col2 = st.columns([1, 2])
                        
                        with col1:
                            # Display image
                            if link and isinstance(link, str) and link.strip():
                                try:
                                    st.image(link, use_container_width=True)
                                except Exception:
                                    st.image("https://via.placeholder.com/200x250?text=Product+Image", use_container_width=True)
                            else:
                                st.image("https://via.placeholder.com/200x250?text=No+Image", use_container_width=True)
                        
                        with col2:
                            st.markdown(f"**{name}**")
                            details = " | ".join(filter(None, [article_type, colour, usage]))
                            if details:
                                st.write(details)
                            st.success("✅ Exact Match")
                        
                        st.markdown("---")
                
            # Display Other Recommendations
            if not other_recommendations.empty:
                st.subheader("💡 Other Recommendations")
                st.markdown("*Related products you might also like*")
                
                for idx, row in other_recommendations.iterrows():
                    name = row.get("productDisplayName") or "Unnamed Product"
                    article_type = row.get("articleType") or ""
                    colour = row.get("baseColour") or ""
                    usage = row.get("usage") or ""
                    link = row.get("link") or ""
                    filename = row.get("filename") or ""

                    # Create a container for each product
                    with st.container():
                        col1, col2 = st.columns([1, 2])
                        
                        with col1:
                            # Display image
                            if link and isinstance(link, str) and link.strip():
                                try:
                                    st.image(link, use_container_width=True)
                                except Exception:
                                    st.image("https://via.placeholder.com/200x250?text=Product+Image", use_container_width=True)
                            else:
                                st.image("https://via.placeholder.com/200x250?text=No+Image", use_container_width=True)
                        
                        with col2:
                            st.markdown(f"**{name}**")
                            details = " | ".join(filter(None, [article_type, colour, usage]))
                            if details:
                                st.write(details)
                            st.info("💡 Related Product")
                        
                        st.markdown("---")
            
            # Summary
            total_exact = len(exact_matches)
            total_related = len(other_recommendations)
            st.info(f"📊 Found {total_exact} exact matches and {total_related} related recommendations")

def customer_browse_page():
    """Customer Browse by Category page (shop-style grid)"""
    st.title("🛍 Browse by Category")

    df = load_product_data()
    if df is None or df.empty:
        st.info("No products available.")
        return

    # --- Filter bar ---
    with st.container():
        st.markdown("### 🔎 Filter Products")
        col1, col2, col3, col4 = st.columns(4)

        # Category filter
        categories = sorted(df['masterCategory'].dropna().unique().tolist())
        selected_category = col1.selectbox("Category", ["All"] + categories)

        # Color filter
        available_colors = sorted(df['baseColour'].dropna().unique().tolist())
        selected_color = col4.selectbox("Color", ["All"] + available_colors)

    # --- Apply filters ---
    if selected_category != "All":
        df = df[df['masterCategory'] == selected_category]
    
    if selected_color != "All":
        df = df[df['baseColour'] == selected_color]

    st.markdown("---")

    # --- Show products in grid (3 per row) ---
    if df.empty:
        st.info("No products found.")
        return

    num_cols = 3
    for i in range(0, len(df), num_cols):
        cols = st.columns(num_cols)
        for j, product in enumerate(df.iloc[i:i+num_cols].iterrows()):
            _, prod = product
            with cols[j]:
                # Product image
                if 'link' in prod and isinstance(prod['link'], str) and prod['link'].strip():
                    if prod.get('link') and prod['link'] != 'undefined' and prod['link'].strip():
                        try:
                            st.image(prod['link'], width=200)
                        except:
                            st.image("https://via.placeholder.com/200x200?text=No+Image", width=200)
                    else:
                        st.image("https://via.placeholder.com/200x200?text=No+Image", width=200)

                # Product title
                st.markdown(f"**{prod.get('productDisplayName', 'Unnamed Product')}**")

                # Price
                price = prod.get("price", None)
                if price:
                    st.write(f"💰 LKR {price:,.2f}")
                else:
                    st.write("💰 Price on request")
                
                 # Tags (inside grid card)
                if 'tags' in prod and isinstance(prod['tags'], list) and len(prod['tags']) > 0:
                    for i, t in enumerate(prod['tags']):
                        key = f"tag_{prod['id']}_{i}"
                        if st.button(f"#{t}", key=key):
                            st.session_state.selected_tag = t
                            st.session_state.customer_page = 'tag_products'
                            st.rerun()

                # View details button
                if st.button("View Details", key=f"view_{prod['id']}"):
                    st.session_state.selected_product = prod.to_dict()
                    st.session_state.customer_page = 'product_detail'
                    st.rerun()

def customer_tags_page():
    """Browse popular tags"""
    st.title("🏷️ Popular Tags")
    
    if st.button("← Back to Home"):
        st.session_state.customer_page = 'home'
        st.rerun()
    
    df = load_product_data()
    
    # Extract popular tags
    all_tags = []
    for tags in df['tags']:
        if isinstance(tags, list):
            all_tags.extend(tags)
    
    tag_counts = pd.Series(all_tags).value_counts()
    
    st.subheader("Most Popular Tags")
    cols = st.columns(4)
    for i, (tag, count) in enumerate(tag_counts.head(20).items()):
        col_idx = i % 4
        if cols[col_idx].button(f"{tag} ({count})", key=f"popular_{tag}"):
            st.session_state.selected_tag = tag
            st.session_state.customer_page = 'tag_products'
            st.rerun()

def customer_category_products_page():
    """Show products for a specific category"""
    st.title(f"📂 Products in: {st.session_state.selected_category}")
    
    if st.button("← Back to Browse"):
        st.session_state.customer_page = 'browse'
        st.session_state.selected_category = None
        st.session_state.selected_subcategory = None
        st.session_state.selected_article_type = None
        st.rerun()
    
    df = load_product_data()
    
    # Subcategory filter
    subcategories = get_subcategories(st.session_state.selected_category)
    selected_subcategory = st.selectbox("Filter by subcategory", ["All"] + subcategories)
    
    if selected_subcategory and selected_subcategory != "All":
        st.session_state.selected_subcategory = selected_subcategory
        
        # Article type filter
        article_types = get_article_types(selected_subcategory)
        selected_article_type = st.selectbox("Filter by type", ["All"] + article_types)
        
        if selected_article_type and selected_article_type != "All":
            st.session_state.selected_article_type = selected_article_type
            display_products(df, category=st.session_state.selected_category, 
                           subcategory=st.session_state.selected_subcategory,
                           article_type=st.session_state.selected_article_type)
        else:
            display_products(df, category=st.session_state.selected_category, 
                           subcategory=st.session_state.selected_subcategory)
    else:
        display_products(df, category=st.session_state.selected_category)

def customer_tag_products_page():
    """Show products with a specific tag"""
    st.title(f"🏷️ Products with tag: #{st.session_state.selected_tag}")
    
    if st.button("← Back"):
        st.session_state.customer_page = 'tags'
        st.session_state.selected_tag = None
        st.rerun()
    
    df = load_product_data()
    display_products(df, tag=st.session_state.selected_tag)

def customer_product_detail_page():
    """Show detailed product information"""
    if 'selected_product' not in st.session_state:
        st.error("No product selected")
        st.session_state.customer_page = 'home'
        st.rerun()
        return
    
    product = st.session_state.selected_product
    st.title(f"📦 {product.get('productDisplayName', 'Product Details')}")
    
    if st.button("← Back to Results"):
        st.session_state.customer_page = 'home'
        st.rerun()
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Product Details")
        st.write(f"**Name:** {product.get('productDisplayName', 'No name')}")
        
        if 'masterCategory' in product:
            st.write(f"**Category:** {product.get('masterCategory', 'Unknown')}")
        if 'subCategory' in product:
            st.write(f"**Subcategory:** {product.get('subCategory', 'Unknown')}")
        if 'articleType' in product:
            st.write(f"**Type:** {product.get('articleType', 'Unknown')}")
        if 'baseColour' in product:
            st.write(f"**Color:** {product.get('baseColour', 'Unknown')}")
        if 'gender' in product:
            st.write(f"**Gender:** {product.get('gender', 'Unknown')}")
        if 'season' in product:
            st.write(f"**Season:** {product.get('season', 'Unknown')}")
        if 'usage' in product:
            st.write(f"**Usage:** {product.get('usage', 'Unknown')}")
        if 'year' in product and pd.notna(product['year']):
            st.write(f"**Year:** {int(product['year'])}")
        
        # Display tags if available
        if 'tags' in product and pd.notna(product['tags']):
            st.write("**Tags:**")
            tags = product['tags']
            
            if isinstance(tags, list):
                for tag in tags:
                    if st.button(f"#{tag}", key=f"detail_tag_{tag}"):
                        st.session_state.selected_tag = tag
                        st.session_state.customer_page = 'tag_products'
                        st.rerun()
    
    with col2:
        # Display product image if available
        if 'link' in product and pd.notna(product['link']):
            st.image(product['link'], use_container_width=True, caption="Product Image")
        elif 'filename' in product and pd.notna(product['filename']):
            st.image(f"https://via.placeholder.com/300x400?text=Product+Image", 
                    use_container_width=True, caption="Image not available")
        
        st.subheader("Actions")
        if st.button("Add to Cart", type="primary"):
            st.success("Added to cart!")
        
        if st.button("Save for Later"):
            st.info("Product saved!")

def render_customer_view():
    """Render the appropriate customer page"""
    if st.session_state.customer_page == 'home':
        customer_home_page()
    elif st.session_state.customer_page == 'ai_search':
        customer_ai_search_page()
    elif st.session_state.customer_page == 'browse':
        customer_browse_page()
    elif st.session_state.customer_page == 'tags':
        customer_tags_page()
    elif st.session_state.customer_page == 'category_products':
        customer_category_products_page()
    elif st.session_state.customer_page == 'tag_products':
        customer_tag_products_page()
    elif st.session_state.customer_page == 'product_detail':
        customer_product_detail_page()