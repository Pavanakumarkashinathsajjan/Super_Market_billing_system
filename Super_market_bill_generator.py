import datetime
from PIL import Image, ImageDraw, ImageFont
import os
import re

# ---------------- STOCK REGISTER ---------------- #
stock = {
    1: {"name": "Rice (1kg)", "price": 60, "quantity": 20},
    2: {"name": "Sugar (1kg)", "price": 45, "quantity": 15},
    3: {"name": "Milk (1L)", "price": 30, "quantity": 25},
    4: {"name": "Bread", "price": 25, "quantity": 10},
    5: {"name": "Eggs (12 pcs)", "price": 70, "quantity": 12}
}

CGST_RATE = 0.025
SGST_RATE = 0.025


# ---------------- INPUT VALIDATION FUNCTIONS ---------------- #

def get_valid_name():
    while True:
        name = input("Enter Customer Name: ").strip()
        if name.replace(" ", "").isalpha():
            return name
        else:
            print("Name should contain only letters and spaces.")


def get_valid_phone():
    while True:
        phone = input("Enter Phone Number (10 digits): ").strip()
        if phone.isdigit() and len(phone) == 10:
            return phone
        else:
            print("Phone number must be exactly 10 digits.")


def get_valid_integer(prompt):
    while True:
        value = input(prompt)
        if value.isdigit():
            return int(value)
        else:
            print("Please enter a valid number.")


# ---------------- DISPLAY ITEMS ---------------- #

def display_items():
    print("\nAvailable Items:")
    print("-" * 60)
    print(f"{'ID':<5}{'Item':<20}{'Price':<10}{'Stock':<10}")
    print("-" * 60)

    for item_id, details in stock.items():
        print(f"{item_id:<5}{details['name']:<20}{details['price']:<10}{details['quantity']:<10}")

    print("-" * 60)


# ---------------- IMAGE BILL GENERATOR ---------------- #

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

    draw.text((10, y), "Item        Qty     Total", fill="black", font=font)
    y += 30

    for item in cart:
        name, price, qty = item
        total = price * qty
        draw.text((10, y), f"{name[:10]}   {qty}     {total}", fill="black", font=font)
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

    print(f"\n🧾 Bill saved at: {full_path}")


# ---------------- GENERATE BILL ---------------- #

def generate_bill(cart, customer_name, phone):
    print("\n" + "=" * 60)
    print("               SUPERMARKET BILL")
    print("=" * 60)

    subtotal = 0

    for item in cart:
        name, price, qty = item
        total = price * qty
        subtotal += total
        print(f"{name}  x{qty}  = {total}")

    cgst = subtotal * CGST_RATE
    sgst = subtotal * SGST_RATE
    grand_total = subtotal + cgst + sgst

    print("-" * 60)
    print(f"Subtotal: {subtotal:.2f}")
    print(f"CGST (2.5%): {cgst:.2f}")
    print(f"SGST (2.5%): {sgst:.2f}")
    print(f"Grand Total: {grand_total:.2f}")
    print("=" * 60)

    save_bill_as_image(cart, customer_name, phone, subtotal, cgst, sgst, grand_total)


# ---------------- ADMIN PANEL ---------------- #

def admin_panel():
    while True:
        print("\n------ ADMIN PANEL ------")
        print("1. Add New Item")
        print("2. Restock Existing Item")
        print("3. View Stock")
        print("4. Exit Admin Panel")

        choice = input("Enter choice: ")

        if choice == "1":
            new_id = max(stock.keys()) + 1
            name = input("Enter item name: ")
            price = get_valid_integer("Enter price: ")
            quantity = get_valid_integer("Enter quantity: ")

            stock[new_id] = {"name": name, "price": price, "quantity": quantity}
            print("New item added successfully!")

        elif choice == "2":
            display_items()
            item_id = get_valid_integer("Enter item ID to restock: ")
            if item_id in stock:
                qty = get_valid_integer("Enter quantity to add: ")
                stock[item_id]["quantity"] += qty
                print("Stock updated successfully!")
            else:
                print("Invalid Item ID")

        elif choice == "3":
            display_items()

        elif choice == "4":
            break

        else:
            print("Invalid choice!")


# ---------------- MAIN PROGRAM ---------------- #

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

                if choice not in stock:
                    print("Invalid Item ID!")
                    continue

                qty = get_valid_integer("Enter Quantity: ")

                if qty <= 0:
                    print("Quantity must be greater than 0.")
                    continue

                if qty > stock[choice]["quantity"]:
                    print("Out of Stock! Available:", stock[choice]["quantity"])
                    continue

                cart.append((stock[choice]["name"], stock[choice]["price"], qty))
                stock[choice]["quantity"] -= qty

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
