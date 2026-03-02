Python Supermarket Billing System

A console-based Supermarket Bill Generator built using Python.
This project simulates real-world supermarket billing with stock management, admin control, GST calculation, and image-based receipt generation.


Project Overview

This system allows:

Customers to purchase items

Admin to manage stock

Automatic GST calculation

Receipt generation in image format (.png)

Input validation for accurate data entry

The generated bill is stored in a specified local directory.


Features
Customer Mode

Enter validated customer name (letters only)

Enter validated 10-digit phone number

Select items and quantities

Prevents purchase beyond available stock

Calculates:

Subtotal

CGST (2.5%)

SGST (2.5%)

Grand Total

Generates bill receipt as an image file



Admin Mode

Add new items

Restock existing items

View current stock

Stock updates automatically after each purchase


Receipt Generation

Generates a structured supermarket bill

Saves receipt as .png image

Stored in:

/home/nineleaps/Downloads/Python /AIML Training Program

Unique filename with timestamp



Technologies Used

Python 3

Pillow (PIL) – for image generation

OS module – for file handling

Datetime module – for bill timestamp


Installation
Clone or Download the Project
git clone <your-repo-link>

OR download manually.


Install Required Library
pip install pillow
Run the Program
python filename.py


Project Structure
Supermarket-Billing-System/
│
├── main.py
├── README.md
└── Generated Bills (Saved in specified folder)


Input Validation Implemented

✔ Customer name must contain only letters
✔ Phone number must be exactly 10 digits
✔ Quantity must be positive
✔ Item ID must exist
✔ Prevents program crash from invalid inputs


Tax Structure
Tax Type	Rate
CGST	2.5%
SGST	2.5%
Total GST	5%


Sample Output

Console Bill Display

Image-based receipt saved locally