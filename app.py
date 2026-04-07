import streamlit as st
import csv
from datetime import datetime
from pathlib import Path
import pandas as pd

# Page configuration
st.set_page_config(
    page_title="StoreHub - Cloud Store Manager",
    page_icon="🏬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
        .main {
            padding: 0rem 1rem;
        }
        .stMetric {
            padding: 1rem;
            border-radius: 0.5rem;
            margin: 0.5rem 0;
            background-color: var(--background-color);
            border: 1px solid var(--secondary-background-color);
        }
    </style>
""", unsafe_allow_html=True)

# ==================== DATA CLASSES ====================
class Item:
    def __init__(self, id, name, buyPrice, sellPrice, quantity):
        self.id = id
        self.name = name
        self.buyPrice = buyPrice
        self.sellPrice = sellPrice
        self.quantity = quantity

class User:
    def __init__(self, username, password):
        self.username = username
        self.password = password

# ==================== STORE MANAGER ====================
class StoreManager:
    def __init__(self):
        self.items = []
        self.users = []
        self.currentUser = ""
        self.dailyProfit = 0.0
        self.monthlyProfit = 0.0
        self.yearlyProfit = 0.0
        self.lastDay = -1
        self.lastMonth = -1
        self.lastYear = -1
        
        self.loadUsers()
        self.loadItems()
        self.loadProfit()
        self.refreshCurrentDate()
        self.checkDateBoundary()

    def refreshCurrentDate(self):
        now = datetime.now()
        self.currentDay = now.day
        self.currentMonth = now.month
        self.currentYear = now.year

    def checkDateBoundary(self):
        if self.lastDay != -1 and self.currentDay != self.lastDay:
            self.dailyProfit = 0.0
        if self.lastMonth != -1 and self.currentMonth != self.lastMonth:
            self.monthlyProfit = 0.0
        if self.lastYear != -1 and self.currentYear != self.lastYear:
            self.yearlyProfit = 0.0
        self.lastDay = self.currentDay
        self.lastMonth = self.currentMonth
        self.lastYear = self.currentYear
        self.saveProfit()

    def login(self, username, password):
        for user in self.users:
            if user.username == username and user.password == password:
                self.currentUser = username
                return True
        return False

    def signup(self, username, password):
        if not username or not password:
            return False
        for user in self.users:
            if user.username == username:
                return False
        self.users.append(User(username, password))
        self.saveUser(User(username, password))
        return True

    def getItems(self):
        return self.items

    def getDailyProfit(self):
        return self.dailyProfit

    def getMonthlyProfit(self):
        return self.monthlyProfit

    def getYearlyProfit(self):
        return self.yearlyProfit

    def addItem(self, name, buyPrice, sellPrice, quantity):
        if not name or quantity <= 0 or buyPrice < 0 or sellPrice < 0:
            return False
        newId = self.items[-1].id + 1 if self.items else 1
        item = Item(newId, name, buyPrice, sellPrice, quantity)
        self.items.append(item)
        self.saveItem(item)
        return True

    def updateItem(self, itemId, buyPrice, sellPrice, addQuantity):
        for item in self.items:
            if item.id == itemId:
                item.buyPrice = buyPrice
                item.sellPrice = sellPrice
                item.quantity += addQuantity
                self.saveItemsFile()
                return True
        return False

    def deleteItem(self, itemId):
        for i, item in enumerate(self.items):
            if item.id == itemId:
                self.items.pop(i)
                self.saveItemsFile()
                return True
        return False

    def searchItems(self, query):
        results = []
        for item in self.items:
            if query.lower() in item.name.lower():
                results.append(item)
        return results

    def sellProduct(self, itemId, quantity, discountPercent):
        self.refreshCurrentDate()
        for item in self.items:
            if item.id == itemId and item.quantity >= quantity:
                lineTotal = item.sellPrice * quantity
                discount = lineTotal * (discountPercent / 100.0)
                lineTotal -= discount
                profit = (item.sellPrice - item.buyPrice) * quantity
                item.quantity -= quantity
                self.dailyProfit += profit
                self.monthlyProfit += profit
                self.yearlyProfit += profit
                self.saveItemsFile()
                self.saveProfit()
                return True, lineTotal, profit, item.name
        return False, 0, 0, ""

    # ==================== FILE OPERATIONS ====================
    def loadUsers(self):
        filepath = Path("users.csv")
        if not filepath.exists():
            return
        with open(filepath, 'r') as f:
            reader = csv.reader(f)
            next(reader, None)
            for row in reader:
                if row and len(row) >= 2:
                    self.users.append(User(row[0], row[1]))

    def saveUser(self, user):
        filepath = Path("users.csv")
        mode = 'a' if filepath.exists() else 'w'
        with open(filepath, mode, newline='') as f:
            writer = csv.writer(f)
            if mode == 'w':
                writer.writerow(['Username', 'Password'])
            writer.writerow([user.username, user.password])

    def loadItems(self):
        filepath = Path("items.csv")
        if not filepath.exists():
            return
        with open(filepath, 'r') as f:
            reader = csv.reader(f)
            next(reader, None)
            for row in reader:
                if row and len(row) >= 5:
                    try:
                        item = Item(int(row[0]), row[1], float(row[2]), float(row[3]), int(row[4]))
                        self.items.append(item)
                    except ValueError:
                        continue

    def saveItem(self, item):
        filepath = Path("items.csv")
        mode = 'a' if filepath.exists() else 'w'
        with open(filepath, mode, newline='') as f:
            writer = csv.writer(f)
            if mode == 'w':
                writer.writerow(['ID', 'Name', 'BuyPrice', 'SellPrice', 'Quantity'])
            writer.writerow([item.id, item.name, item.buyPrice, item.sellPrice, item.quantity])

    def saveItemsFile(self):
        with open("items.csv", 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['ID', 'Name', 'BuyPrice', 'SellPrice', 'Quantity'])
            for item in self.items:
                writer.writerow([item.id, item.name, item.buyPrice, item.sellPrice, item.quantity])

    def loadProfit(self):
        filepath = Path("profit_data.csv")
        if not filepath.exists():
            return
        with open(filepath, 'r') as f:
            reader = csv.reader(f)
            next(reader, None)
            for row in reader:
                if row and len(row) >= 6:
                    try:
                        self.lastDay = int(row[0])
                        self.lastMonth = int(row[1])
                        self.lastYear = int(row[2])
                        self.dailyProfit = float(row[3])
                        self.monthlyProfit = float(row[4])
                        self.yearlyProfit = float(row[5])
                    except ValueError:
                        continue

    def saveProfit(self):
        with open("profit_data.csv", 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Day', 'Month', 'Year', 'DailyProfit', 'MonthlyProfit', 'YearlyProfit'])
            writer.writerow([self.lastDay, self.lastMonth, self.lastYear, 
                            self.dailyProfit, self.monthlyProfit, self.yearlyProfit])

    def saveManagerReceipt(self, receiptText):
        with open("manager_receipts.csv", 'a', newline='') as f:
            f.write(receiptText + "\n")


# ==================== STREAMLIT APP ====================
@st.cache_resource
def get_manager():
    return StoreManager()

manager = get_manager()

if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.username = ""
    st.session_state.cart = []

if not st.session_state.authenticated:
    st.markdown("# 🏬 StoreHub")
    st.markdown("## Cloud Store Management for everyone")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("### User Authentication")
        tab1, tab2 = st.tabs(["Login", "Signup"])
        with tab1:
            username = st.text_input("Username", key="login_user")
            password = st.text_input("Password", type="password", key="login_pass")
            if st.button("🔐 Login", use_container_width=True):
                if manager.login(username, password):
                    st.session_state.authenticated = True
                    st.session_state.username = username
                    st.success("✅ Login successful!")
                    st.rerun()
                else:
                    st.error("❌ Invalid username or password")
        with tab2:
            new_user = st.text_input("Create Username", key="signup_user")
            new_pass = st.text_input("Create Password", type="password", key="signup_pass")
            if st.button("✍️ Sign Up", use_container_width=True):
                if manager.signup(new_user, new_pass):
                    st.success("✅ Account created! Please login.")
                else:
                    st.error("❌ Username exists or fields are empty")
else:
    col1, col2 = st.columns([0.8, 0.2])
    with col1:
        st.markdown("# 🏬 StoreHub")
        st.markdown(f"👤 **Logged in as:** {st.session_state.username}")
    with col2:
        if st.button("🚪 Logout"):
            st.session_state.authenticated = False
            st.session_state.username = ""
            st.session_state.cart = []
            st.rerun()
    st.divider()
    tab1, tab2, tab3, tab4 = st.tabs(["📦 Inventory", "🛒 Sales", "💰 Profit", "📊 Reports"])
    with tab1:
        st.markdown("### Inventory Management")
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("➕ Add New Item", use_container_width=True):
                st.session_state.show_add = True
        with col2:
            search_query = st.text_input("🔍 Search item by name", "")
        with col3:
            if st.button("🔄 Refresh", use_container_width=True):
                st.rerun()
        if st.session_state.get("show_add", False):
            st.warning("### Add New Item")
            with st.form("add_item_form"):
                item_name = st.text_input("Item Name")
                col1, col2 = st.columns(2)
                with col1:
                    buy_price = st.number_input("Buy Price", min_value=0.0, step=0.01)
                with col2:
                    sell_price = st.number_input("Sell Price", min_value=0.0, step=0.01)
                quantity = st.number_input("Quantity", min_value=1, step=1)
                if st.form_submit_button("✅ Add Item"):
                    if manager.addItem(item_name, buy_price, sell_price, quantity):
                        st.success("✅ Item added successfully!")
                        st.session_state.show_add = False
                        st.rerun()
                    else:
                        st.error("❌ Failed to add item")
        st.divider()
        items = manager.getItems()
        if search_query:
            items = manager.searchItems(search_query)
        if items:
            df_data = []
            for item in items:
                df_data.append({
                    "ID": item.id,
                    "Name": item.name,
                    "Buy Price": f"{item.buyPrice:.2f} PKR",
                    "Sell Price": f"{item.sellPrice:.2f} PKR",
                    "Quantity": item.quantity,
                    "Profit/Unit": f"{(item.sellPrice - item.buyPrice):.2f} PKR"
                })
            df = pd.DataFrame(df_data)
            st.dataframe(df, use_container_width=True, hide_index=True)
            st.divider()
            st.markdown("### Update or Delete Item")
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("#### Update Item")
                item_id = st.number_input("Item ID to update", min_value=1)
                new_buy_price = st.number_input("New Buy Price", min_value=0.0, step=0.01, key="update_buy")
                new_sell_price = st.number_input("New Sell Price", min_value=0.0, step=0.01, key="update_sell")
                add_qty = st.number_input("Add Quantity", min_value=0, step=1, key="update_qty")
                if st.button("💾 Update Item", use_container_width=True):
                    if manager.updateItem(item_id, new_buy_price, new_sell_price, add_qty):
                        st.success("✅ Item updated!")
                        st.rerun()
                    else:
                        st.error("❌ Item not found")
            with col2:
                st.markdown("#### Delete Item")
                delete_id = st.number_input("Item ID to delete", min_value=1, key="delete_id")
                if st.button("🗑️ Delete Item", use_container_width=True):
                    if manager.deleteItem(delete_id):
                        st.success("✅ Item deleted!")
                        st.rerun()
                    else:
                        st.error("❌ Item not found")
        else:
            st.info("📭 No items in inventory. Add your first item!")
    with tab2:
        st.markdown("### Point of Sale")
        items = manager.getItems()
        if items:
            col1, col2, col3 = st.columns(3)
            with col1:
                item_options = {f"{item.name} ({item.sellPrice:.2f} PKR)": item.id for item in items}
                selected_item = st.selectbox("Select Item", list(item_options.keys()))
                item_id = item_options[selected_item]
            with col2:
                qty = st.number_input("Quantity", min_value=1, step=1, value=1, key="sale_qty")
            with col3:
                discount = st.number_input("Discount %", min_value=0, max_value=100, step=1, key="discount")
            if st.button("🛒 Add to Cart", use_container_width=True):
                item = next((i for i in items if i.id == item_id), None)
                if item and qty <= item.quantity:
                    st.session_state.cart.append({
                        'id': item_id,
                        'name': item.name,
                        'qty': qty,
                        'price': item.sellPrice,
                        'discount': discount
                    })
                    st.success("✅ Added to cart!")
                    st.rerun()
                else:
                    st.error("❌ Insufficient stock!")
            st.divider()
            if st.session_state.cart:
                st.markdown("### 🛒 Shopping Cart")
                cart_data = []
                total_bill = 0
                for cart_item in st.session_state.cart:
                    line_total = cart_item['price'] * cart_item['qty']
                    discount_amount = line_total * (cart_item['discount'] / 100)
                    line_total -= discount_amount
                    total_bill += line_total
                    cart_data.append({
                        "Item": cart_item['name'],
                        "Qty": cart_item['qty'],
                        "Price": f"{cart_item['price']:.2f} PKR",
                        "Discount": f"{cart_item['discount']}%",
                        "Total": f"{line_total:.2f} PKR"
                    })
                df_cart = pd.DataFrame(cart_data)
                st.dataframe(df_cart, use_container_width=True, hide_index=True)
                st.markdown(f"### **Total Bill: {total_bill:.2f} PKR**")
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button("✅ Complete Sale", use_container_width=True):
                        # Generate receipt ID
                        receipt_id = datetime.now().strftime('%Y%m%d%H%M%S')
                        
                        # Calculate totals
                        subtotal = sum(cart_item['price'] * cart_item['qty'] for cart_item in st.session_state.cart)
                        total_discount = sum((cart_item['price'] * cart_item['qty']) * (cart_item['discount'] / 100) for cart_item in st.session_state.cart)
                        grand_total = subtotal - total_discount
                        
                        # Build professional receipt
                        receipt = "=" * 40 + "\n"
                        receipt += "       Mujahid khan general store\n"
                        receipt += "=" * 40 + "\n"
                        receipt += f"Receipt #: {receipt_id}\n"
                        receipt += f"Date: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n"
                        receipt += f"Cashier: {st.session_state.username}\n"
                        receipt += "-" * 40 + "\n"
                        receipt += f"{'Item':<20} {'Qty':<5} {'Price':<8} {'Disc%':<6} {'Total':<8}\n"
                        receipt += "-" * 40 + "\n"
                        
                        sale_successful = True
                        for cart_item in st.session_state.cart:
                            success, line_total, profit, item_name = manager.sellProduct(
                                cart_item['id'], cart_item['qty'], cart_item['discount']
                            )
                            if success:
                                receipt += f"{item_name:<20} {cart_item['qty']:<5} {cart_item['price']:<7.2f} PKR {cart_item['discount']:<6}% {line_total:<7.2f} PKR\n"
                            else:
                                sale_successful = False
                        
                        if sale_successful:
                            receipt += "-" * 40 + "\n"
                            receipt += f"{'Subtotal:':<30} {subtotal:<7.2f} PKR\n"
                            receipt += f"{'Total Discount:':<30} {total_discount:<7.2f} PKR\n"
                            receipt += f"{'Grand Total:':<30} {grand_total:<7.2f} PKR\n"
                            receipt += "=" * 40 + "\n"
                            receipt += "Thank you for shopping with us!\n"
                            receipt += "=" * 40 + "\n"
                            
                            # Save receipt for manager
                            manager.saveManagerReceipt(receipt)
                            
                            st.session_state.cart = []
                            st.success("✅ Sale completed!")
                            
                            # Display receipt professionally
                            st.markdown("### 🧾 Customer Receipt")
                            
                            # Create beautiful HTML receipt
                            html_receipt = f"""
                            <div style="border: 2px solid #333; padding: 20px; margin: 20px 0; background-color: #f9f9f9; font-family: 'Courier New', monospace; max-width: 400px;">
                                <h2 style="text-align: center; margin: 0; color: #333;">Mujahid Khan General Store</h2>
                                <p style="text-align: center; margin: 5px 0; font-size: 14px;">Your Trusted Store for Quality Goods</p>
                                <hr style="border: 1px solid #333;">
                                <p><strong>Receipt #:</strong> {receipt_id}</p>
                                <p><strong>Date:</strong> {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</p>
                                <p><strong>Cashier:</strong> {st.session_state.username}</p>
                                <hr style="border: 1px solid #333;">
                                <table style="width: 100%; border-collapse: collapse;">
                                    <thead>
                                        <tr style="background-color: #e0e0e0;">
                                            <th style="border: 1px solid #333; padding: 5px; text-align: left;">Item</th>
                                            <th style="border: 1px solid #333; padding: 5px; text-align: center;">Qty</th>
                                            <th style="border: 1px solid #333; padding: 5px; text-align: right;">Price</th>
                                            <th style="border: 1px solid #333; padding: 5px; text-align: center;">Disc%</th>
                                            <th style="border: 1px solid #333; padding: 5px; text-align: right;">Total</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                            """
                            
                            for cart_item in st.session_state.cart:
                                html_receipt += f"""
                                        <tr>
                                            <td style="border: 1px solid #333; padding: 5px;">{cart_item['name']}</td>
                                            <td style="border: 1px solid #333; padding: 5px; text-align: center;">{cart_item['qty']}</td>
                                            <td style="border: 1px solid #333; padding: 5px; text-align: right;">{cart_item['price']:.2f} PKR</td>
                                            <td style="border: 1px solid #333; padding: 5px; text-align: center;">{cart_item['discount']}%</td>
                                            <td style="border: 1px solid #333; padding: 5px; text-align: right;">{cart_item['price'] * cart_item['qty'] * (1 - cart_item['discount']/100):.2f} PKR</td>
                                        </tr>
                            """
                            
                            html_receipt += f"""
                                    </tbody>
                                </table>
                                <hr style="border: 1px solid #333;">
                                <p style="text-align: right;"><strong>Subtotal:</strong> {subtotal:.2f} PKR</p>
                                <p style="text-align: right;"><strong>Total Discount:</strong> {total_discount:.2f} PKR</p>
                                <p style="text-align: right; font-size: 18px; color: #d9534f;"><strong>Grand Total: {grand_total:.2f} PKR</strong></p>
                                <hr style="border: 1px solid #333;">
                                <p style="text-align: center; font-style: italic;">Thank you for shopping with us!</p>
                                <p style="text-align: center; font-size: 12px;">Visit us again at Mujahid Khan General Store</p>
                            </div>
                            """
                            
                            st.markdown(html_receipt, unsafe_allow_html=True)
                            
                            # Print button for receipt
                            if st.button("🖨️ Print Receipt", key="print_receipt"):
                                st.markdown("""
                                <script>
                                window.print();
                                </script>
                                """, unsafe_allow_html=True)
                                st.success("Print dialog opened!")
                            
                            st.rerun()
                        else:
                            st.error("❌ Sale failed!")
                with col2:
                    if st.button("🗑️ Clear Cart", use_container_width=True):
                        st.session_state.cart = []
                        st.rerun()
            else:
                st.info("🛒 Your cart is empty. Add items to the sale first!")
        else:
            st.warning("❌ No items available for sale. Add inventory first.")
    with tab3:
        st.markdown("### 💰 Profit Summary")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(label="Daily Profit", value=f"{manager.getDailyProfit():.2f} PKR")
        with col2:
            st.metric(label="Monthly Profit", value=f"{manager.getMonthlyProfit():.2f} PKR")
        with col3:
            st.metric(label="Yearly Profit", value=f"{manager.getYearlyProfit():.2f} PKR")
        st.divider()
        profit_data = {
            "Period": ["Today", "This Month", "This Year"],
            "Profit": [manager.getDailyProfit(), manager.getMonthlyProfit(), manager.getYearlyProfit()]
        }
        df_profit = pd.DataFrame(profit_data)
        col1, col2 = st.columns(2)
        with col1:
            st.bar_chart(df_profit.set_index("Period"))
        with col2:
            st.dataframe(df_profit, use_container_width=True, hide_index=True)
    with tab4:
        st.markdown("### 📊 Reports & Analytics")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### Inventory Value")
            total_inv_value = sum(item.quantity * item.buyPrice for item in manager.getItems())
            total_inv_sell = sum(item.quantity * item.sellPrice for item in manager.getItems())
            st.metric("Total Inventory Cost", f"{total_inv_value:.2f} PKR")
            st.metric("Total Inventory Value", f"{total_inv_sell:.2f} PKR")
        with col2:
            st.markdown("#### Stock Overview")
            total_items = len(manager.getItems())
            total_qty = sum(item.quantity for item in manager.getItems())
            st.metric("Total Products", total_items)
            st.metric("Total Items in Stock", total_qty)
        st.divider()
        st.markdown("#### Low Stock Alert")
        low_stock_items = [item for item in manager.getItems() if item.quantity < 5]
        if low_stock_items:
            low_stock_data = []
            for item in low_stock_items:
                low_stock_data.append({
                    "ID": item.id,
                    "Name": item.name,
                    "Quantity": item.quantity,
                    "Status": "🔴 Critical" if item.quantity < 2 else "🟠 Low"
                })
            df_low = pd.DataFrame(low_stock_data)
            st.dataframe(df_low, use_container_width=True, hide_index=True)
        else:
            st.success("✅ All items have sufficient stock!")
    st.divider()
    st.markdown("---")
    st.markdown("<p style='text-align: center; color: gray; font-size: 12px;'>StoreHub | Cloud Store Manager</p>", unsafe_allow_html=True)
