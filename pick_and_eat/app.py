import streamlit as st
import requests

BASE_URL = "http://127.0.0.1:8000"

# ---------------- SESSION ----------------
if "token" not in st.session_state:
    st.session_state.token = None

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Smart Grocery", layout="wide")

# ---------------- CUSTOM CSS ----------------
st.markdown("""
<style>
body {
    background-color: #f5f7fa;
}

.product-card {
    background-color: white;
    padding: 15px;
    border-radius: 15px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    margin-bottom: 20px;
    transition: 0.3s ease-in-out;
}
.product-card:hover {
    transform: translateY(-5px);
}

.product-image {
    height: 220px;
    width: 100%;
    object-fit: cover;
    border-radius: 10px;
    margin-bottom: 10px;
}

.price {
    font-size: 20px;
    font-weight: bold;
    color: #2e7d32;
}

.stock {
    font-size: 13px;
    color: gray;
    margin-bottom: 10px;
}

div.stButton > button {
    background-color: #ff4b4b;
    color: white;
    border-radius: 8px;
    width: 100%;
}
</style>
""", unsafe_allow_html=True)

# ---------------- PRODUCT DISPLAY FUNCTION ----------------
def display_product(product, key_prefix="view"):

    st.markdown('<div class="product-card">', unsafe_allow_html=True)

    # IMAGE
    if product.get("image_url"):
        st.markdown(
            f'<img src="{product["image_url"]}" class="product-image">',
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            '<div class="product-image" '
            'style="background:#eee; display:flex; align-items:center; justify-content:center;">'
            'No Image</div>',
            unsafe_allow_html=True
        )

    # DETAILS
    st.markdown(f"<h4>{product['name']}</h4>", unsafe_allow_html=True)
    st.markdown(f"<div class='price'>₹{product['price']}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='stock'>Stock: {product['stock']}</div>", unsafe_allow_html=True)

    quantity = st.number_input(
        "Quantity",
        min_value=1,
        max_value=product["stock"],
        step=1,
        key=f"{key_prefix}_qty_{product['id']}"
    )

    if st.button("Add to Cart", key=f"{key_prefix}_btn_{product['id']}"):

        headers = {
            "Authorization": f"Bearer {st.session_state.token}"
        }

        response = requests.post(
            f"{BASE_URL}/cart",
            json={
                "product_id": product["id"],
                "quantity": quantity
            },
            headers=headers
        )

        if response.status_code == 200:
            st.success("Added to cart!")
        else:
            st.error("Failed to add to cart.")

    st.markdown('</div>', unsafe_allow_html=True)


# ---------------- LOGIN / REGISTER ----------------
if st.session_state.token is None:

    st.title("🛒 Smart Grocery Store")

    tab1, tab2 = st.tabs(["Login", "Register"])

    # LOGIN
    with tab1:
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            response = requests.post(
                f"{BASE_URL}/login",
                data={
                    "username": username,
                    "password": password
                }
            )

            if response.status_code == 200:
                st.session_state.token = response.json()["access_token"]
                st.success("Login successful!")
                st.rerun()
            else:
                st.error("Invalid credentials")

    # REGISTER
    with tab2:
        new_username = st.text_input("New Username")
        new_email = st.text_input("Email")
        new_password = st.text_input("New Password", type="password")

        if st.button("Register"):
            response = requests.post(
                f"{BASE_URL}/register",
                json={
                    "username": new_username,
                    "email": new_email,
                    "password": new_password
                }
            )

            if response.status_code == 200:
                st.success("Registered successfully! Please login.")
            else:
                st.error("Registration failed")

    st.stop()

# ---------------- SIDEBAR ----------------
st.sidebar.title("Navigation")

menu = st.sidebar.selectbox(
    "Menu",
    ["View Products", "Search Products", "Checkout", "My Orders"]
)

if st.sidebar.button("Logout"):
    st.session_state.token = None
    st.rerun()

headers = {"Authorization": f"Bearer {st.session_state.token}"}

# ---------------- VIEW PRODUCTS ----------------
if menu == "View Products":

    st.header("🛍 Fresh Products")

    response = requests.get(f"{BASE_URL}/products")

    if response.status_code == 200:
        products = response.json()

        cols = st.columns(3)

        for index, product in enumerate(products):
            with cols[index % 3]:
                display_product(product, "view")

    else:
        st.error("Failed to fetch products")

# ---------------- SEARCH PRODUCTS ----------------
if menu == "Search Products":

    st.header("🔍 Search Products")

    keyword = st.text_input("Search by product name")

    if keyword.strip() != "":

        response = requests.get(
            f"{BASE_URL}/products/search",
            params={"name": keyword},
            
        )

        if response.status_code == 200:

            results = response.json()

            if results:
                cols = st.columns(3)
                for index, product in enumerate(results):
                    with cols[index % 3]:
                        display_product(product, "search")
            else:
                st.warning("No matching products found")

        else:
            st.error("Search request failed")
            st.write("Status Code:", response.status_code)

# ---------------- CHECKOUT ----------------
if menu == "Checkout":

    st.header("💳 Checkout")

    response = requests.get(f"{BASE_URL}/cart", headers=headers)

    if response.status_code == 200:
        cart_items = response.json()

        if cart_items:
            total = 0

            for item in cart_items:
                st.write(f"{item['product_name']} - ₹{item['price']} x {item['quantity']}")
                total += item["price"] * item["quantity"]

            st.subheader(f"Total: ₹{total}")

            if st.button("Place Order"):
                order_response = requests.post(f"{BASE_URL}/checkout", headers=headers)

                if order_response.status_code == 200:
                    st.success("Order placed successfully!")
                else:
                    st.error("Order failed")

        else:
            st.info("Your cart is empty")

# ---------------- MY ORDERS ----------------
if menu == "My Orders":

    st.header("📦 My Orders")

    response = requests.get(f"{BASE_URL}/my-orders", headers=headers)

    if response.status_code == 200:
        orders = response.json()

        if orders:
            for order in orders:
                st.write(order)
        else:
            st.info("No orders yet")

    else:
        st.error("Failed to fetch orders")