# 🗃️ Pharmacy Management System – Database Schema

This system uses a **MySQL relational database** to manage pharmacy inventory, billing, suppliers, customers, and user authentication.

Below is the complete schema of all tables used in the system:

---

## 🧾 `bill_items`

| Column Name   | Data Type |
|---------------|-----------|
| amount        | decimal   |
| bill_id       | varchar   |
| item_id       | int       |
| medicine_id   | varchar   |
| price         | decimal   |
| quantity      | int       |

---

## 📊 `bill_summary`

| Column Name      | Data Type |
|------------------|-----------|
| bill_date        | date      |
| bill_id          | varchar   |
| customer_contact | varchar   |
| customer_id      | varchar   |
| customer_name    | varchar   |
| item_count       | bigint    |
| subtotal         | decimal   |
| tax              | decimal   |
| total            | decimal   |
| total_items      | decimal   |

---

## 🧾 `bills`

| Column Name  | Data Type |
|--------------|-----------|
| bill_date    | date      |
| bill_id      | varchar   |
| created_at   | timestamp |
| customer_id  | varchar   |
| subtotal     | decimal   |
| tax          | decimal   |
| total        | decimal   |

---

## 👤 `customers`

| Column Name  | Data Type |
|--------------|-----------|
| address      | text      |
| contact      | varchar   |
| created_at   | timestamp |
| customer_id  | varchar   |
| email        | varchar   |
| name         | varchar   |
| updated_at   | timestamp |

---

## 💊 `medicine_inventory`

| Column Name     | Data Type |
|-----------------|-----------|
| description     | text      |
| expiry_date     | date      |
| inventory_value | decimal   |
| location        | varchar   |
| medicine_id     | varchar   |
| name            | varchar   |
| price           | decimal   |
| quantity        | int       |
| supplier_name   | varchar   |

---

## 💊 `medicines`

| Column Name  | Data Type |
|--------------|-----------|
| created_at   | timestamp |
| description  | text      |
| expiry_date  | date      |
| location     | varchar   |
| medicine_id  | varchar   |
| name         | varchar   |
| price        | decimal   |
| quantity     | int       |
| supplier_id  | varchar   |
| updated_at   | timestamp |

---

## 🧑‍💼 `suppliers`

| Column Name  | Data Type |
|--------------|-----------|
| address      | text      |
| contact      | varchar   |
| created_at   | timestamp |
| email        | varchar   |
| name         | varchar   |
| supplier_id  | varchar   |
| updated_at   | timestamp |

---

## 📦 `supplies`

| Column Name  | Data Type |
|--------------|-----------|
| amount       | decimal   |
| created_at   | timestamp |
| medicine_id  | varchar   |
| quantity     | int       |
| supplier_id  | varchar   |
| supply_date  | date      |
| supply_id    | int       |

---

## 📦 `supply_summary`

| Column Name    | Data Type |
|----------------|-----------|
| first_supply   | date      |
| last_supply    | date      |
| supplier_id    | varchar   |
| supplier_name  | varchar   |
| supply_count   | bigint    |
| total_amount   | decimal   |
| total_quantity | decimal   |

---

## 🔐 `users`

| Column Name | Data Type |
|-------------|-----------|
| password    | varchar   |
| username    | varchar   |

---
