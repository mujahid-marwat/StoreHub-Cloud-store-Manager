# General Store Management System - Python GUI

## Features

✨ **Professional & Modern UI**
- Clean, intuitive interface using PyQt5
- Responsive design across all devices
- Professional color scheme with smooth interactions

🛍️ **Complete Store Management**
- User authentication (Signup/Login)
- Inventory management (Add, Update, Delete, Search)
- Point-of-Sale system with cart checkout
- Real-time profit tracking (Daily, Monthly, Yearly)
- Receipt generation and printing

## Setup & Installation

### Step 1: Install Python
Make sure you have Python 3.7 or higher installed. Download from [python.org](https://www.python.org/downloads/)

### Step 2: Install Dependencies
Open a terminal/PowerShell in this folder and run:

```bash
pip install -r requirements.txt
```

Or install PyQt5 directly:

```bash
pip install PyQt5
```

### Step 3: Run the Application

```bash
python store_gui.py
```

## How to Use

### First Time Setup
1. Click **Signup** to create a new account
2. Enter username and password
3. Click **Login** with your credentials

### Inventory Management
- Go to the **Inventory** tab
- Use **Add Item** to create new products
- Use **Update Item** to modify prices/stock
- Use **Delete Item** to remove products
- Use **Search** to find items by name

### Making a Sale
- Go to the **Sales** tab
- Select an item from the dropdown
- Enter quantity and optional discount
- Click **Add to Cart** to add items to the sale
- Click **Complete Sale** to finalize and generate receipt
- Click **Print Receipt** to print the transaction

### View Profits
- Go to the **Profit** tab
- See Daily, Monthly, and Yearly profits
- Profits reset automatically at day/month/year boundaries

## Data Files

The application uses CSV files for data persistence:
- `users.csv` - User accounts
- `items.csv` - Inventory
- `profit_data.csv` - Profit tracking
- `manager_receipts.csv` - Transaction history
- `temp_receipt.txt` - Latest receipt

## System Requirements

- **OS**: Windows, macOS, or Linux
- **Python**: 3.7+
- **RAM**: 512 MB minimum
- **Disk**: ~50 MB for PyQt5 and application

## Support

The original console application (`store.cpp`) is still available if you need the command-line version.
