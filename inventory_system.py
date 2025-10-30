import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import os
from datetime import date
import matplotlib.pyplot as plt   # <-- Needed for charts

FILE_NAME = "inventory.xlsx"

# Load or create Excel file
if os.path.exists(FILE_NAME):
    xls = pd.ExcelFile(FILE_NAME)
    df_inventory = pd.read_excel(FILE_NAME, sheet_name="Inventory") if "Inventory" in xls.sheet_names else pd.DataFrame(columns=["Product", "Quantity", "Price", "Notes"])
    df_sales = pd.read_excel(FILE_NAME, sheet_name="Sales") if "Sales" in xls.sheet_names else pd.DataFrame(columns=["Date", "Product", "Quantity", "Total"])
    df_expenses = pd.read_excel(FILE_NAME, sheet_name="Expenses") if "Expenses" in xls.sheet_names else pd.DataFrame(columns=["Date", "Category", "Amount", "Note"])
else:
    df_inventory = pd.DataFrame(columns=["Product", "Quantity", "Price", "Notes"])
    df_sales = pd.DataFrame(columns=["Date", "Product", "Quantity", "Total"])
    df_expenses = pd.DataFrame(columns=["Date", "Category", "Amount", "Note"])


# Save all data
def save_all():
    try:
        with pd.ExcelWriter(FILE_NAME, engine="openpyxl", mode="w") as writer:
            df_inventory.to_excel(writer, sheet_name="Inventory", index=False)
            df_sales.to_excel(writer, sheet_name="Sales", index=False)
            df_expenses.to_excel(writer, sheet_name="Expenses", index=False)
        messagebox.showinfo("Saved", "All records saved successfully!")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to save file!\n{e}")


# ---------------- INVENTORY FUNCTIONS ----------------
def refresh_inventory():
    for row in tree_inventory.get_children():
        tree_inventory.delete(row)
    for _, row in df_inventory.iterrows():
        tree_inventory.insert("", "end", values=list(row))


def add_product():
    global df_inventory
    product = entry_product.get()
    qty = entry_qty.get()
    price = entry_price.get()
    note = entry_note.get()

    if product and qty and price:
        try:
            qty = int(qty)
            price = float(price)
            new_row = pd.DataFrame([{"Product": product, "Quantity": qty, "Price": price, "Notes": note}])
            df_inventory = pd.concat([df_inventory, new_row], ignore_index=True)
            save_all()
            refresh_inventory()
            clear_entries()
        except:
            messagebox.showerror("Error", "Quantity must be number and Price must be decimal!")
    else:
        messagebox.showwarning("Warning", "Fill all required fields!")


def update_stock():
    global df_inventory
    selected = tree_inventory.selection()
    if not selected:
        messagebox.showwarning("Warning", "Select a product to update")
        return

    product = tree_inventory.item(selected[0])["values"][0]
    change = entry_qty.get()

    try:
        change = int(change)
        df_inventory.loc[df_inventory["Product"] == product, "Quantity"] += change
        save_all()
        refresh_inventory()
        clear_entries()
    except:
        messagebox.showerror("Error", "Enter a valid quantity!")


def search_inventory():
    keyword = entry_search.get().lower()
    for row in tree_inventory.get_children():
        tree_inventory.delete(row)
    filtered = df_inventory[df_inventory["Product"].str.lower().str.contains(keyword)]
    for _, row in filtered.iterrows():
        tree_inventory.insert("", "end", values=list(row))


def clear_entries():
    entry_product.delete(0, tk.END)
    entry_qty.delete(0, tk.END)
    entry_price.delete(0, tk.END)
    entry_note.delete(0, tk.END)


# ---------------- SALES FUNCTIONS ----------------
def record_sale():
    global df_sales, df_inventory
    product = entry_sale_product.get()
    qty = entry_sale_qty.get()

    if not product or not qty:
        messagebox.showwarning("Warning", "Fill all fields!")
        return

    try:
        qty = int(qty)
        if product not in df_inventory["Product"].values:
            messagebox.showerror("Error", "Product not found in inventory!")
            return
        if qty > int(df_inventory.loc[df_inventory["Product"] == product, "Quantity"].values[0]):
            messagebox.showerror("Error", "Not enough stock!")
            return

        price = float(df_inventory.loc[df_inventory["Product"] == product, "Price"].values[0])
        total = qty * price

        # Deduct from inventory
        df_inventory.loc[df_inventory["Product"] == product, "Quantity"] -= qty

        # Add to sales record
        new_row = pd.DataFrame([{"Date": date.today(), "Product": product, "Quantity": qty, "Total": total}])
        df_sales = pd.concat([df_sales, new_row], ignore_index=True)

        save_all()
        refresh_inventory()
        refresh_sales()
        refresh_trending()  # Update trending when new sale recorded
        entry_sale_product.delete(0, tk.END)
        entry_sale_qty.delete(0, tk.END)

    except:
        messagebox.showerror("Error", "Quantity must be a number!")


def refresh_sales():
    for row in tree_sales.get_children():
        tree_sales.delete(row)
    for _, row in df_sales.iterrows():
        tree_sales.insert("", "end", values=list(row))


# ---------------- EXPENSE FUNCTIONS ----------------
def record_expense():
    global df_expenses
    category = entry_exp_category.get()
    amount = entry_exp_amount.get()
    note = entry_exp_note.get()

    if not category or not amount:
        messagebox.showwarning("Warning", "Fill all required fields!")
        return

    try:
        amount = float(amount)
        new_row = pd.DataFrame([{"Date": date.today(), "Category": category, "Amount": amount, "Note": note}])
        df_expenses = pd.concat([df_expenses, new_row], ignore_index=True)
        save_all()
        refresh_expenses()
        entry_exp_category.delete(0, tk.END)
        entry_exp_amount.delete(0, tk.END)
        entry_exp_note.delete(0, tk.END)
    except:
        messagebox.showerror("Error", "Amount must be a number!")


def refresh_expenses():
    for row in tree_expenses.get_children():
        tree_expenses.delete(row)
    for _, row in df_expenses.iterrows():
        tree_expenses.insert("", "end", values=list(row))


# ---------------- PROFIT CALC ----------------
def show_profit():
    total_sales = df_sales["Total"].sum()
    total_expenses = df_expenses["Amount"].sum()
    profit = total_sales - total_expenses
    messagebox.showinfo("Profit Report", f"Total Sales: {total_sales}\nTotal Expenses: {total_expenses}\nProfit: {profit}")


# ---------------- TRENDING FUNCTIONS ----------------
def refresh_trending():
    for row in tree_trending.get_children():
        tree_trending.delete(row)
    if df_sales.empty:
        return
    trending = df_sales.groupby("Product")["Quantity"].sum().sort_values(ascending=False).reset_index()
    for _, row in trending.iterrows():
        tree_trending.insert("", "end", values=list(row))

def show_trending_chart():
    if df_sales.empty:
        messagebox.showinfo("Trending", "No sales data yet!")
        return
    trending = df_sales.groupby("Product")["Quantity"].sum().sort_values(ascending=False).head(5)
    trending.plot(kind="bar", title="Top 5 Best Selling Products")
    plt.ylabel("Total Sold Quantity")
    plt.show()


# ---------------- GUI ----------------
root = tk.Tk()
root.title("Wholesale Shop Management")
root.geometry("1000x650")

notebook = ttk.Notebook(root)
notebook.pack(fill="both", expand=True)

# -------- Inventory Tab --------
tab_inventory = tk.Frame(notebook)
notebook.add(tab_inventory, text="Inventory")

frame_top = tk.Frame(tab_inventory)
frame_top.pack(pady=10)

tk.Label(frame_top, text="Product:").grid(row=0, column=0, padx=5)
entry_product = tk.Entry(frame_top)
entry_product.grid(row=0, column=1)

tk.Label(frame_top, text="Quantity (+/-):").grid(row=0, column=2, padx=5)
entry_qty = tk.Entry(frame_top)
entry_qty.grid(row=0, column=3)

tk.Label(frame_top, text="Price:").grid(row=0, column=4, padx=5)
entry_price = tk.Entry(frame_top)
entry_price.grid(row=0, column=5)

tk.Label(frame_top, text="Notes:").grid(row=0, column=6, padx=5)
entry_note = tk.Entry(frame_top, width=20)
entry_note.grid(row=0, column=7)

tk.Button(frame_top, text="Add Product", command=add_product).grid(row=0, column=8, padx=5)
tk.Button(frame_top, text="Update Stock", command=update_stock).grid(row=0, column=9, padx=5)

frame_search = tk.Frame(tab_inventory)
frame_search.pack(pady=5)

tk.Label(frame_search, text="Search:").pack(side=tk.LEFT, padx=5)
entry_search = tk.Entry(frame_search)
entry_search.pack(side=tk.LEFT, padx=5)
tk.Button(frame_search, text="Go", command=search_inventory).pack(side=tk.LEFT, padx=5)
tk.Button(frame_search, text="Show All", command=refresh_inventory).pack(side=tk.LEFT, padx=5)

cols = ["Product", "Quantity", "Price", "Notes"]
tree_inventory = ttk.Treeview(tab_inventory, columns=cols, show="headings", height=15)
for col in cols:
    tree_inventory.heading(col, text=col)
    tree_inventory.column(col, width=150)
tree_inventory.pack(pady=10, fill="x")

# -------- Sales Tab --------
tab_sales = tk.Frame(notebook)
notebook.add(tab_sales, text="Sales")

frame_sale = tk.Frame(tab_sales)
frame_sale.pack(pady=10)

tk.Label(frame_sale, text="Product:").grid(row=0, column=0, padx=5)
entry_sale_product = tk.Entry(frame_sale)
entry_sale_product.grid(row=0, column=1)

tk.Label(frame_sale, text="Quantity:").grid(row=0, column=2, padx=5)
entry_sale_qty = tk.Entry(frame_sale)
entry_sale_qty.grid(row=0, column=3)

tk.Button(frame_sale, text="Record Sale", command=record_sale).grid(row=0, column=4, padx=5)

tree_sales = ttk.Treeview(tab_sales, columns=["Date", "Product", "Quantity", "Total"], show="headings", height=15)
for col in ["Date", "Product", "Quantity", "Total"]:
    tree_sales.heading(col, text=col)
    tree_sales.column(col, width=150)
tree_sales.pack(pady=10, fill="x")

# -------- Expenses Tab --------
tab_expenses = tk.Frame(notebook)
notebook.add(tab_expenses, text="Expenses")

frame_exp = tk.Frame(tab_expenses)
frame_exp.pack(pady=10)

tk.Label(frame_exp, text="Category:").grid(row=0, column=0, padx=5)
entry_exp_category = tk.Entry(frame_exp)
entry_exp_category.grid(row=0, column=1)

tk.Label(frame_exp, text="Amount:").grid(row=0, column=2, padx=5)
entry_exp_amount = tk.Entry(frame_exp)
entry_exp_amount.grid(row=0, column=3)

tk.Label(frame_exp, text="Note:").grid(row=0, column=4, padx=5)
entry_exp_note = tk.Entry(frame_exp)
entry_exp_note.grid(row=0, column=5)

tk.Button(frame_exp, text="Record Expense", command=record_expense).grid(row=0, column=6, padx=5)

tree_expenses = ttk.Treeview(tab_expenses, columns=["Date", "Category", "Amount", "Note"], show="headings", height=15)
for col in ["Date", "Category", "Amount", "Note"]:
    tree_expenses.heading(col, text=col)
    tree_expenses.column(col, width=150)
tree_expenses.pack(pady=10, fill="x")

# -------- Profit Tab --------
tab_profit = tk.Frame(notebook)
notebook.add(tab_profit, text="Profit Report")

tk.Button(tab_profit, text="Show Profit Report", font=("Arial", 14), command=show_profit).pack(pady=50)

# -------- Trending Tab --------
tab_trending = tk.Frame(notebook)
notebook.add(tab_trending, text="Trending Products")

tk.Button(tab_trending, text="Refresh Trending List", command=refresh_trending).pack(pady=5)
tk.Button(tab_trending, text="Show Trending Chart", command=show_trending_chart).pack(pady=5)

tree_trending = ttk.Treeview(tab_trending, columns=["Product", "Total Sold"], show="headings", height=15)
for col in ["Product", "Total Sold"]:
    tree_trending.heading(col, text=col)
    tree_trending.column(col, width=200)
tree_trending.pack(pady=10, fill="x")

# Bottom Save Button
tk.Button(root, text="Save All Records", command=save_all).pack(pady=5)

refresh_inventory()
refresh_sales()
refresh_expenses()
refresh_trending()

root.mainloop()
