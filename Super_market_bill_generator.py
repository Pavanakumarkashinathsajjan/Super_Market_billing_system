import datetime
from PIL import Image, ImageDraw, ImageFont
import os
import mysql.connector

# ---------------- DATABASE CONNECTION ---------------- #

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Pavan@123",
    database="supermarket"
)

cursor = db.cursor(dictionary=True)

CGST_RATE = 0.025
SGST_RATE = 0.025


# ---------------- INPUT VALIDATION ---------------- #

def get_valid_name():
    while True:
        name = input("Enter Customer Name: ").strip()
        if name.replace(" ", "").isalpha():
            return name.title()
        else:
            print("Name should contain only letters and spaces.")


def get_valid_phone():
    while True:
        phone = input("Enter Phone Number (10 digits): ").strip()

        if not phone.isdigit():
            print("Phone number must contain only digits.")
            continue

        if len(phone) != 10:
            print("Phone number must be exactly 10 digits.")
            continue

        if phone[0] not in ['6', '7', '8', '9']:
            print("Phone number must start with 6, 7, 8, or 9.")
            continue

        return phone


def get_valid_integer(prompt):
    while True:
        value = input(prompt)
        if value.isdigit()>=1:
            return int(value)
        else:
            print("Please enter a valid number.")


def get_valid_item_name():
    while True:
        name = input("Enter item name: ").strip()

        if not name:
            print("Item name cannot be empty.")
            continue

        if not all(char.isalnum() or char.isspace() for char in name):
            print("Item name should not contain special characters.")
            continue

        if name.replace(" ", "").isdigit():
            print("Item name cannot be only numbers.")
            continue

        return name.title()


# ---------------- DISPLAY ITEMS (FROM DATABASE) ---------------- #

def display_items():
    cursor.execute("SELECT * FROM items")
    items = cursor.fetchall()

    print("\nAvailable Items:")
    print("-" * 60)
    print(f"{'ID':<5}{'Item':<20}{'Price':<10}{'Stock':<10}")
    print("-" * 60)

    for item in items:
        print(f"{item['item_id']:<5}{item['name']:<20}{item['price']:<10}{item['quantity']:<10}")

    print("-" * 60)


# ---------------- IMAGE BILL ---------------- #

def save_bill_as_image(cart, customer_name, phone, subtotal, cgst, sgst, grand_total):

    width = 400
    height = 600
    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)

    try:
        font = ImageFont.truetype("arial.ttf", 16)
    except:
        font = ImageFont.load_default()

    y = 20

    draw.text((100, y), "SUPERMARKET BILL", fill="black", font=font)
    y += 40

    draw.text((10, y), f"Customer: {customer_name}", fill="black", font=font)
    y += 25
    draw.text((10, y), f"Phone: {phone}", fill="black", font=font)
    y += 25
    draw.text((10, y), f"Date: {datetime.datetime.now().strftime('%d-%m-%Y %H:%M')}", fill="black", font=font)
    y += 40

    for item in cart:
        name, price, qty = item
        total = price * qty
        draw.text((10, y), f"{name[:12]}  {qty}  {total}", fill="black", font=font)
        y += 25

    y += 20
    draw.text((10, y), f"Subtotal: {subtotal:.2f}", fill="black", font=font)
    y += 25
    draw.text((10, y), f"CGST: {cgst:.2f}", fill="black", font=font)
    y += 25
    draw.text((10, y), f"SGST: {sgst:.2f}", fill="black", font=font)
    y += 25
    draw.text((10, y), f"Grand Total: {grand_total:.2f}", fill="black", font=font)

    save_directory = "/home/nineleaps/Downloads/Python /AIML Training Program"
    os.makedirs(save_directory, exist_ok=True)

    filename = f"Bill_{customer_name}_{datetime.datetime.now().strftime('%H%M%S')}.png"
    full_path = os.path.join(save_directory, filename)

    image.save(full_path)

    print("Bill saved at:", full_path)


# ---------------- GENERATE BILL + STORE IN DB ---------------- #

def generate_bill(cart, customer_name, phone):

    subtotal = sum(price * qty for _, price, qty in cart)
    cgst = subtotal * CGST_RATE
    sgst = subtotal * SGST_RATE
    grand_total = subtotal + cgst + sgst

    # -------- PRINT RECEIPT IN TERMINAL -------- #

    print("\n" + "=" * 60)
    print("                 SUPERMARKET BILL")
    print("=" * 60)
    print(f"Customer Name : {customer_name}")
    print(f"Phone Number  : {phone}")
    print(f"Date          : {datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S')}")
    print("-" * 60)
    print(f"{'Item':<20}{'Price':<10}{'Qty':<10}{'Total':<10}")
    print("-" * 60)

    for name, price, qty in cart:
        total = price * qty
        print(f"{name:<20}{price:<10}{qty:<10}{total:<10}")

    print("-" * 60)
    print(f"{'Subtotal':<40}{subtotal:.2f}")
    print(f"{'CGST (2.5%)':<40}{cgst:.2f}")
    print(f"{'SGST (2.5%)':<40}{sgst:.2f}")
    print("-" * 60)
    print(f"{'Grand Total':<40}{grand_total:.2f}")
    print("=" * 60)

    # -------- STORE IN DATABASE -------- #

    cursor.execute(
        "INSERT INTO customers (name, phone) VALUES (%s, %s)",
        (customer_name, phone)
    )
    db.commit()

    customer_id = cursor.lastrowid

    cursor.execute(
        """INSERT INTO bills 
           (customer_id, subtotal, cgst, sgst, grand_total, bill_date)
           VALUES (%s, %s, %s, %s, %s, NOW())""",
        (customer_id, subtotal, cgst, sgst, grand_total)
    )
    db.commit()

    bill_id = cursor.lastrowid

    for name, price, qty in cart:
        total = price * qty
        cursor.execute(
            """INSERT INTO bill_items 
               (bill_id, item_name, price, quantity, total)
               VALUES (%s, %s, %s, %s, %s)""",
            (bill_id, name, price, qty, total)
        )

    db.commit()

    # -------- SAVE IMAGE -------- #

    save_bill_as_image(cart, customer_name, phone, subtotal, cgst, sgst, grand_total)

    print("\nBill stored in database successfully")


# ---------------- ADMIN PANEL ---------------- #

def admin_panel():
    while True:
        print("\n------ ADMIN PANEL ------")
        print("1. Add New Item")
        print("2. Restock Existing Item")
        print("3. Update Item Name And Price")
        print("4. Delete Item")
        print("5. View Stock")
        print("6. View All Bills")
        print("7. Exit")

        choice = input("Enter choice: ")

        if choice == "1":
            name = get_valid_item_name()
            price = get_valid_integer("Enter price: ")
            quantity = get_valid_integer("Enter quantity: ")

            cursor.execute(
                "INSERT INTO items (name, price, quantity) VALUES (%s, %s, %s)",
                (name, price, quantity)
            )
            db.commit()
            print("Item added successfully!")

        elif choice == "2":
            display_items()
            item_id = get_valid_integer("Enter item ID to restock: ")

            cursor.execute("SELECT quantity FROM items WHERE item_id = %s", (item_id,))
            item = cursor.fetchone()

            if not item:
                print("Invalid Item ID")
                continue

            qty = get_valid_integer("Enter quantity to add: ")

            if qty <= 0:
                print("Quantity must be greater than 0.")
                continue

            new_quantity = item['quantity'] + qty

            cursor.execute(
                "UPDATE items SET quantity = %s WHERE item_id = %s",
                (new_quantity, item_id)
            )
            db.commit()

            print("Stock updated successfully!")

        elif choice == "3":
            display_items()
            item_id = get_valid_integer("Enter item ID to update: ")

            cursor.execute("SELECT * FROM items WHERE item_id = %s", (item_id,))
            item = cursor.fetchone()

            if not item:
                print("Invalid Item ID")
                continue

            print("Leave field empty if you don't want to change it.")

            new_name = input("Enter new item name: ").strip()
            new_price = input("Enter new price: ").strip()

            if new_name:
                if not all(char.isalnum() or char.isspace() for char in new_name):
                    print("Invalid name format.")
                    continue
            else:
                new_name = item['name']

            if new_price:
                if not new_price.isdigit():
                    print("Price must be numeric.")
                    continue
                new_price = int(new_price)
            else:
                new_price = item['price']

            cursor.execute(
                "UPDATE items SET name = %s, price = %s WHERE item_id = %s",
                (new_name.title(), new_price, item_id)
            )
            db.commit()

            print("Item updated successfully!")

        elif choice == "4":
            display_items()
            item_id = get_valid_integer("Enter item ID to delete: ")

            cursor.execute("SELECT * FROM items WHERE item_id = %s", (item_id,))
            item = cursor.fetchone()

            if item:
                cursor.execute("DELETE FROM items WHERE item_id = %s", (item_id,))
                db.commit()
                print("Item deleted successfully!")
            else:
                print("Invalid Item ID")

        elif choice == "5":
            display_items()

        
        elif choice == "6":
            cursor.execute("""
                SELECT b.bill_id, c.name, c.phone, b.grand_total, b.bill_date
                FROM bills b
                JOIN customers c ON b.customer_id = c.id
                ORDER BY b.bill_date DESC
            """)
            bills = cursor.fetchall()

            print("\nAll Bills:")
            print("-" * 80)
            print(f"{'Bill ID':<10}{'Customer':<20}{'Phone':<15}{'Total':<10}{'Date'}")
            print("-" * 80)

            for bill in bills:
                print(f"{bill['bill_id']:<10}{bill['name']:<20}{bill['phone']:<15}{bill['grand_total']:<10}{bill['bill_date']}")
                
        elif choice == "7":
            break

        else:
            print("Invalid choice!")


# ---------------- MAIN ---------------- #

def main():
    while True:
        print("\n===== PYTHON SUPERMARKET =====")
        print("1. Customer")
        print("2. Admin")
        print("3. Exit")

        role = input("Select role: ")

        if role == "1":
            customer_name = get_valid_name()
            phone = get_valid_phone()
            cart = []

            while True:
                display_items()
                choice = get_valid_integer("Enter Item ID: ")
                qty = get_valid_integer("Enter Quantity: ")

                if qty <= 0:
                    print("Quantity must be greater than 0.")
                    continue

                cursor.execute("SELECT * FROM items WHERE item_id = %s", (choice,))
                item = cursor.fetchone()

                if not item:
                    print("Invalid Item ID!")
                    continue

                if qty > item['quantity']:
                    print("Out of Stock! Available:", item['quantity'])
                    continue

                cart.append((item['name'], float(item['price']), qty))

                new_quantity = item['quantity'] - qty
                cursor.execute(
                    "UPDATE items SET quantity = %s WHERE item_id = %s",
                    (new_quantity, choice)
                )
                db.commit()

                next_action = input("Press 'c' to continue or 'b' to bill: ").lower()
                if next_action == "b":
                    break

            generate_bill(cart, customer_name, phone)

        elif role == "2":
            admin_panel()

        elif role == "3":
            print("Thank you!")
            break

        else:
            print("Invalid choice!")

main()
