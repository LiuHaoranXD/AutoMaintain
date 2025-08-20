import sqlite3
import os
from app.utils import get_db_path

def init_db():
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # Tenants
    c.execute("""
    CREATE TABLE IF NOT EXISTS tenants (
        tenant_id INTEGER PRIMARY KEY AUTOINCREMENT,
        first_name TEXT NOT NULL,
        last_name TEXT,
        email TEXT,
        unit_number TEXT,
        phone TEXT,
        lease_start_date TEXT,
        emergency_contact TEXT,
        created_at TEXT NOT NULL
    )
    """)

    # Vendors
    c.execute("""
    CREATE TABLE IF NOT EXISTS vendors (
        vendor_id INTEGER PRIMARY KEY AUTOINCREMENT,
        company_name TEXT,
        contact_person TEXT,
        email TEXT,
        phone TEXT,
        specialization TEXT,
        hourly_rate REAL,
        rating REAL,
        created_at TEXT NOT NULL
    )
    """)

    # Requests
    c.execute("""
    CREATE TABLE IF NOT EXISTS maintenance_requests (
        request_id INTEGER PRIMARY KEY AUTOINCREMENT,
        tenant_id INTEGER NOT NULL,
        category TEXT,
        subcategory TEXT,
        description TEXT,
        priority TEXT,
        status TEXT DEFAULT 'pending',
        created_at TEXT NOT NULL,
        scheduled_date TEXT,
        completed_date TEXT,
        cost REAL,
        notes TEXT,
        assigned_vendor_id INTEGER,
        FOREIGN KEY(tenant_id) REFERENCES tenants(tenant_id),
        FOREIGN KEY(assigned_vendor_id) REFERENCES vendors(vendor_id)
    )
    """)

    conn.commit()
    conn.close()
