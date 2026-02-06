import sqlite3
import random
from datetime import datetime, timedelta
import os

FIRST_NAMES = [
    "James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael", "Linda",
    "William", "Elizabeth", "David", "Barbara", "Richard", "Susan", "Joseph", "Jessica",
    "Thomas", "Sarah", "Charles", "Karen", "Christopher", "Nancy", "Daniel", "Lisa",
    "Matthew", "Betty", "Anthony", "Margaret", "Mark", "Sandra", "Donald", "Ashley",
    "Steven", "Kimberly", "Paul", "Emily", "Andrew", "Donna", "Joshua", "Michelle",
    "Kenneth", "Dorothy", "Kevin", "Carol", "Brian", "Amanda", "George", "Melissa",
    "Edward", "Deborah", "Ronald", "Stephanie", "Timothy", "Rebecca", "Jason", "Sharon"
]

LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
    "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson",
    "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson",
    "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson", "Walker",
    "Young", "Allen", "King", "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores"
]

CITIES = [
    ("New York", "NY"), ("Los Angeles", "CA"), ("Chicago", "IL"), ("Houston", "TX"),
    ("Phoenix", "AZ"), ("Philadelphia", "PA"), ("San Antonio", "TX"), ("San Diego", "CA"),
    ("Dallas", "TX"), ("San Jose", "CA"), ("Austin", "TX"), ("Jacksonville", "FL"),
    ("Fort Worth", "TX"), ("Columbus", "OH"), ("Charlotte", "NC"), ("San Francisco", "CA"),
    ("Indianapolis", "IN"), ("Seattle", "WA"), ("Denver", "CO"), ("Boston", "MA"),
    ("Portland", "OR"), ("Miami", "FL"), ("Atlanta", "GA"), ("Las Vegas", "NV")
]

PRODUCT_CATEGORIES = {
    "Electronics": [
        ("Wireless Bluetooth Headphones", 79.99, 149.99),
        ("Smart Watch Pro", 199.99, 349.99),
        ("Portable Charger 10000mAh", 24.99, 49.99),
        ("USB-C Hub Adapter", 34.99, 59.99),
        ("Wireless Mouse", 19.99, 39.99),
        ("Mechanical Keyboard", 89.99, 159.99),
        ("4K Webcam", 99.99, 179.99),
        ("Noise Cancelling Earbuds", 129.99, 249.99),
        ("Tablet Stand Holder", 29.99, 49.99),
        ("Smart Home Speaker", 49.99, 99.99),
    ],
    "Home & Kitchen": [
        ("Stainless Steel Cookware Set", 149.99, 299.99),
        ("Air Fryer XL", 89.99, 159.99),
        ("Coffee Maker Programmable", 49.99, 99.99),
        ("Vacuum Cleaner Cordless", 199.99, 399.99),
        ("Instant Pot Multi-Cooker", 79.99, 149.99),
        ("Blender Professional", 59.99, 119.99),
        ("Toaster 4-Slice", 39.99, 79.99),
        ("Electric Kettle", 29.99, 59.99),
        ("Food Storage Container Set", 24.99, 49.99),
        ("Kitchen Scale Digital", 19.99, 39.99),
    ],
    "Clothing": [
        ("Cotton T-Shirt Classic", 14.99, 29.99),
        ("Denim Jeans Slim Fit", 39.99, 79.99),
        ("Running Shoes", 69.99, 129.99),
        ("Winter Jacket Waterproof", 89.99, 179.99),
        ("Casual Sneakers", 49.99, 99.99),
        ("Wool Sweater", 44.99, 89.99),
        ("Sports Shorts", 24.99, 49.99),
        ("Leather Belt", 19.99, 39.99),
        ("Cotton Socks 6-Pack", 14.99, 29.99),
        ("Baseball Cap", 12.99, 24.99),
    ],
    "Books": [
        ("Python Programming Guide", 29.99, 49.99),
        ("Data Science Handbook", 39.99, 69.99),
        ("Machine Learning Basics", 34.99, 59.99),
        ("Web Development Complete", 44.99, 79.99),
        ("Business Strategy 101", 24.99, 44.99),
        ("Leadership Skills", 19.99, 34.99),
        ("Financial Planning Guide", 29.99, 49.99),
        ("Cooking Masterclass", 34.99, 59.99),
        ("Fitness and Health", 24.99, 44.99),
        ("Travel Photography", 39.99, 69.99),
    ],
    "Sports & Outdoors": [
        ("Yoga Mat Premium", 29.99, 59.99),
        ("Dumbbell Set Adjustable", 149.99, 299.99),
        ("Resistance Bands Kit", 19.99, 39.99),
        ("Camping Tent 4-Person", 129.99, 249.99),
        ("Hiking Backpack 40L", 79.99, 149.99),
        ("Water Bottle Insulated", 24.99, 44.99),
        ("Fitness Tracker Band", 49.99, 99.99),
        ("Jump Rope Speed", 14.99, 29.99),
        ("Foam Roller", 19.99, 39.99),
        ("Sports Sunglasses", 29.99, 59.99),
    ],
}

ORDER_STATUSES = ["pending", "processing", "shipped", "delivered", "cancelled"]
PAYMENT_METHODS = ["credit_card", "debit_card", "paypal", "apple_pay", "google_pay"]


def create_database(db_path: str = "data/ecommerce.db"):
    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone TEXT,
            city TEXT,
            state TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            product_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            price REAL NOT NULL,
            cost REAL NOT NULL,
            stock_quantity INTEGER DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            order_id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER NOT NULL,
            order_date DATETIME NOT NULL,
            status TEXT DEFAULT 'pending',
            payment_method TEXT,
            shipping_address TEXT,
            total_amount REAL DEFAULT 0,
            FOREIGN KEY (customer_id) REFERENCES customers (customer_id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS order_items (
            item_id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            unit_price REAL NOT NULL,
            FOREIGN KEY (order_id) REFERENCES orders (order_id),
            FOREIGN KEY (product_id) REFERENCES products (product_id)
        )
    """)

    conn.commit()
    return conn


def populate_customers(conn, num_customers: int = 150):
    cursor = conn.cursor()

    customers = []
    used_emails = set()

    for i in range(num_customers):
        first_name = random.choice(FIRST_NAMES)
        last_name = random.choice(LAST_NAMES)

        email_base = f"{first_name.lower()}.{last_name.lower()}"
        email = f"{email_base}@email.com"
        counter = 1
        while email in used_emails:
            email = f"{email_base}{counter}@email.com"
            counter += 1
        used_emails.add(email)

        city, state = random.choice(CITIES)
        phone = f"+1-{random.randint(200,999)}-{random.randint(100,999)}-{random.randint(1000,9999)}"

        days_ago = random.randint(1, 730)
        created_at = datetime.now() - timedelta(days=days_ago)

        customers.append((first_name, last_name, email, phone, city, state, created_at))

    cursor.executemany("""
        INSERT INTO customers (first_name, last_name, email, phone, city, state, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, customers)

    conn.commit()
    print(f"Inserted {num_customers} customers")


def populate_products(conn):
    cursor = conn.cursor()

    products = []
    for category, items in PRODUCT_CATEGORIES.items():
        for name, cost, price in items:
            stock = random.randint(10, 500)
            days_ago = random.randint(30, 365)
            created_at = datetime.now() - timedelta(days=days_ago)
            products.append((name, category, price, cost, stock, created_at))

    cursor.executemany("""
        INSERT INTO products (name, category, price, cost, stock_quantity, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, products)

    conn.commit()
    print(f"Inserted {len(products)} products")


def populate_orders(conn, num_orders: int = 600):
    cursor = conn.cursor()

    cursor.execute("SELECT customer_id FROM customers")
    customer_ids = [row[0] for row in cursor.fetchall()]

    cursor.execute("SELECT product_id, price FROM products")
    products = [(row[0], row[1]) for row in cursor.fetchall()]

    for _ in range(num_orders):
        customer_id = random.choice(customer_ids)

        days_ago = random.randint(1, 365)
        order_date = datetime.now() - timedelta(days=days_ago, hours=random.randint(0, 23))

        if days_ago < 3:
            status = random.choice(["pending", "processing"])
        elif days_ago < 7:
            status = random.choices(["processing", "shipped", "delivered"], weights=[0.2, 0.5, 0.3])[0]
        else:
            status = random.choices(["delivered", "cancelled"], weights=[0.9, 0.1])[0]

        payment_method = random.choice(PAYMENT_METHODS)
        city, state = random.choice(CITIES)
        shipping_address = f"{random.randint(100, 9999)} Main St, {city}, {state}"

        cursor.execute("""
            INSERT INTO orders (customer_id, order_date, status, payment_method, shipping_address)
            VALUES (?, ?, ?, ?, ?)
        """, (customer_id, order_date, status, payment_method, shipping_address))

        order_id = cursor.lastrowid

        num_items = random.randint(1, 5)
        order_products = random.sample(products, min(num_items, len(products)))

        total_amount = 0
        for product_id, price in order_products:
            quantity = random.randint(1, 3)
            cursor.execute("""
                INSERT INTO order_items (order_id, product_id, quantity, unit_price)
                VALUES (?, ?, ?, ?)
            """, (order_id, product_id, quantity, price))
            total_amount += price * quantity

        cursor.execute("""
            UPDATE orders SET total_amount = ? WHERE order_id = ?
        """, (round(total_amount, 2), order_id))

    conn.commit()

    cursor.execute("SELECT COUNT(*) FROM order_items")
    num_items = cursor.fetchone()[0]

    print(f"Inserted {num_orders} orders with {num_items} order items")


def main():
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "ecommerce.db")

    if os.path.exists(db_path):
        os.remove(db_path)
        print(f"Removed existing database: {db_path}")

    print("Creating database...")
    conn = create_database(db_path)

    print("Populating customers...")
    populate_customers(conn, num_customers=150)

    print("Populating products...")
    populate_products(conn)

    print("Populating orders...")
    populate_orders(conn, num_orders=600)

    cursor = conn.cursor()
    print("\n=== Database Summary ===")

    for table in ["customers", "products", "orders", "order_items"]:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"{table}: {count} rows")

    cursor.execute("SELECT COUNT(*) FROM customers UNION ALL SELECT COUNT(*) FROM products UNION ALL SELECT COUNT(*) FROM orders UNION ALL SELECT COUNT(*) FROM order_items")
    total = sum(row[0] for row in cursor.fetchall())
    print(f"\nTotal rows: {total}")

    conn.close()
    print(f"\nDatabase created successfully at: {db_path}")


if __name__ == "__main__":
    main()
