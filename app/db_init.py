import os
import sqlite3
import logging
import random
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("DBInit")

def get_db_path():
    return os.getenv("AUTOMAINTAIN_DB_PATH", "./automaintain.db")

def init_db(force_reset=False):
    DB = get_db_path()

    try:
        if force_reset and os.path.exists(DB):
            os.remove(DB)
            logger.info("Existing database removed for reset")

        conn = sqlite3.connect(DB, timeout=15)
        c = conn.cursor()

        # Create tables with proper schema
        c.execute('''
            CREATE TABLE IF NOT EXISTS tenants (
                tenant_id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name TEXT NOT NULL,
                last_name TEXT,
                email TEXT UNIQUE,
                phone TEXT,
                unit_number TEXT NOT NULL,
                lease_start_date TEXT,
                emergency_contact TEXT,
                created_at TEXT NOT NULL
            )
        ''')

        c.execute('''
            CREATE TABLE IF NOT EXISTS vendors (
                vendor_id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_name TEXT NOT NULL,
                contact_person TEXT,
                email TEXT,
                phone TEXT,
                specialization TEXT,
                hourly_rate REAL,
                rating REAL,
                created_at TEXT NOT NULL
            )
        ''')

        c.execute('''
            CREATE TABLE IF NOT EXISTS solutions_database (
                solution_id INTEGER PRIMARY KEY AUTOINCREMENT,
                issue_category TEXT NOT NULL,
                problem_description TEXT NOT NULL,
                solution_steps TEXT NOT NULL,
                estimated_cost REAL,
                estimated_time TEXT,
                difficulty_level TEXT,
                created_at TEXT NOT NULL
            )
        ''')

        c.execute('''
            CREATE TABLE IF NOT EXISTS maintenance_requests (
                request_id INTEGER PRIMARY KEY AUTOINCREMENT,
                tenant_id INTEGER NOT NULL,
                category TEXT NOT NULL,
                subcategory TEXT,
                description TEXT NOT NULL,
                priority TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'Pending',
                urgency TEXT DEFAULT 'Normal',
                created_at TEXT NOT NULL,
                scheduled_date TEXT,
                completed_date TEXT,
                cost REAL,
                estimated_cost REAL,
                notes TEXT,
                assigned_vendor_id INTEGER,
                attachment_path TEXT,
                FOREIGN KEY (tenant_id) REFERENCES tenants(tenant_id),
                FOREIGN KEY (assigned_vendor_id) REFERENCES vendors(vendor_id)
            )
        ''')

        c.execute('''
            CREATE TABLE IF NOT EXISTS interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tenant_id INTEGER,
                question TEXT,
                ai_response TEXT,
                tools_used TEXT,
                created_at TEXT,
                FOREIGN KEY (tenant_id) REFERENCES tenants(tenant_id)
            )
        ''')

        # Create indexes
        c.execute("CREATE INDEX IF NOT EXISTS idx_requests_status ON maintenance_requests(status)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_requests_priority ON maintenance_requests(priority)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_requests_category ON maintenance_requests(category)")

        # Seed data only if empty
        c.execute("SELECT COUNT(*) FROM tenants")
        tenants_count = c.fetchone()[0]
        if tenants_count == 0:
            insert_sample_data(conn)

        conn.commit()
        conn.close()
        logger.info(f"Database initialized at {DB}")
    except sqlite3.Error as e:
        logger.error(f"Database initialization failed: {str(e)}")
        raise

def insert_sample_data(conn):
    random.seed(42)
    c = conn.cursor()

    # Insert 25+ tenants as required
    sample_tenants = [
        ("John", "Smith", "john.smith@example.com", "555-0101", "Apt 1A"),
        ("Emma", "Johnson", "emma.johnson@example.com", "555-0102", "Apt 1B"),
        ("Michael", "Williams", "michael.williams@example.com", "555-0103", "Apt 2A"),
        ("Sophia", "Brown", "sophia.brown@example.com", "555-0104", "Apt 2B"),
        ("William", "Jones", "william.jones@example.com", "555-0105", "Apt 3A"),
        ("Olivia", "Garcia", "olivia.garcia@example.com", "555-0106", "Apt 3B"),
        ("James", "Miller", "james.miller@example.com", "555-0107", "Apt 4A"),
        ("Isabella", "Davis", "isabella.davis@example.com", "555-0108", "Apt 4B"),
        ("Benjamin", "Rodriguez", "benjamin.rodriguez@example.com", "555-0109", "Apt 5A"),
        ("Mia", "Martinez", "mia.martinez@example.com", "555-0110", "Apt 5B"),
        ("Lucas", "Hernandez", "lucas.hernandez@example.com", "555-0111", "Apt 6A"),
        ("Charlotte", "Lopez", "charlotte.lopez@example.com", "555-0112", "Apt 6B"),
        ("Henry", "Gonzalez", "henry.gonzalez@example.com", "555-0113", "Apt 7A"),
        ("Amelia", "Wilson", "amelia.wilson@example.com", "555-0114", "Apt 7B"),
        ("Alexander", "Anderson", "alexander.anderson@example.com", "555-0115", "Apt 8A"),
        ("Harper", "Thomas", "harper.thomas@example.com", "555-0116", "Apt 8B"),
        ("Sebastian", "Taylor", "sebastian.taylor@example.com", "555-0117", "Apt 9A"),
        ("Evelyn", "Moore", "evelyn.moore@example.com", "555-0118", "Apt 9B"),
        ("Jack", "Jackson", "jack.jackson@example.com", "555-0119", "Apt 10A"),
        ("Abigail", "Martin", "abigail.martin@example.com", "555-0120", "Apt 10B"),
        ("Owen", "Lee", "owen.lee@example.com", "555-0121", "Apt 11A"),
        ("Emily", "Perez", "emily.perez@example.com", "555-0122", "Apt 11B"),
        ("Liam", "Thompson", "liam.thompson@example.com", "555-0123", "Apt 12A"),
        ("Elizabeth", "White", "elizabeth.white@example.com", "555-0124", "Apt 12B"),
        ("Noah", "Harris", "noah.harris@example.com", "555-0125", "Apt 13A"),
        ("Sofia", "Sanchez", "sofia.sanchez@example.com", "555-0126", "Apt 13B"),
        ("Mason", "Clark", "mason.clark@example.com", "555-0127", "Apt 14A")
    ]

    for tenant in sample_tenants:
        c.execute(
            "INSERT INTO tenants (first_name, last_name, email, phone, unit_number, created_at) VALUES (?,?,?,?,?,?)",
            (*tenant, datetime.now().isoformat())
        )

    # Insert vendors with different specializations
    sample_vendors = [
        ("QuickFix Plumbing", "Bob Plumber", "bob@quickfixplumbing.com", "555-1001", "Plumbing", 85.0, 4.7),
        ("Sparky Electrical", "Alice Electrician", "alice@sparkyelectrical.com", "555-1002", "Electrical", 95.0, 4.8),
        ("CoolBreeze HVAC", "Charlie Technician", "charlie@coolbreezehvac.com", "555-1003", "HVAC", 90.0, 4.6),
        ("BuildRight Construction", "Dave Builder", "dave@buildright.com", "555-1004", "Structural", 110.0, 4.5),
        ("AppliancePro Service", "Eve Technician", "eve@appliancepro.com", "555-1005", "Appliance", 75.0, 4.3),
        ("General Maintenance", "Frank Handyman", "frank@maintenancepros.com", "555-1006", "General", 65.0, 4.4),
        ("Elite Plumbing", "Grace Plumber", "grace@eliteplumbing.com", "555-1007", "Plumbing", 95.0, 4.9),
        ("PowerFix Electric", "Henry Electrician", "henry@powerfix.com", "555-1008", "Electrical", 88.0, 4.6)
    ]

    for vendor in sample_vendors:
        c.execute(
            "INSERT INTO vendors (company_name, contact_person, email, phone, specialization, hourly_rate, rating, created_at) VALUES (?,?,?,?,?,?,?,?)",
            (*vendor, datetime.now().isoformat())
        )

    # Insert comprehensive solutions database
    sample_solutions = [
        ("Plumbing", "Leaking faucet", "1. Turn off water supply under sink. 2. Remove faucet handle carefully. 3. Replace worn washer or O-ring. 4. Reassemble faucet and test for leaks.", 25.0, "30 minutes", "Easy"),
        ("Plumbing", "Clogged drain", "1. Try plunging first. 2. Use drain snake if plunging fails. 3. Apply chemical drain cleaner as last resort. 4. Call professional if blockage persists.", 40.0, "45 minutes", "Medium"),
        ("Plumbing", "Running toilet", "1. Check flapper seal in tank. 2. Adjust chain length if needed. 3. Replace flapper if warped. 4. Adjust float if water level is wrong.", 20.0, "20 minutes", "Easy"),
        ("Electrical", "Outlet not working", "1. Check circuit breaker panel. 2. Reset any tripped breakers. 3. Test GFCI outlets and reset if needed. 4. Call electrician if problem persists.", 40.0, "15 minutes", "Easy"),
        ("Electrical", "Light switch not working", "1. Turn off power at breaker. 2. Remove switch plate and check connections. 3. Test switch with multimeter. 4. Replace switch if faulty.", 35.0, "30 minutes", "Medium"),
        ("Electrical", "Flickering lights", "1. Check if bulb is loose. 2. Replace bulb if needed. 3. Check circuit load. 4. Call electrician if flickering continues.", 15.0, "10 minutes", "Easy"),
        ("HVAC", "AC not cooling", "1. Check thermostat settings. 2. Replace air filter if dirty. 3. Check outdoor condenser unit for blockages. 4. Verify power supply to unit.", 75.0, "1 hour", "Medium"),
        ("HVAC", "Heating not working", "1. Check thermostat and batteries. 2. Verify gas supply (if gas system). 3. Check air filter. 4. Reset system if needed.", 60.0, "45 minutes", "Medium"),
        ("HVAC", "Poor airflow", "1. Replace dirty air filter. 2. Check all vents are open. 3. Inspect ductwork for blockages. 4. Clean vents and returns.", 30.0, "30 minutes", "Easy"),
        ("Structural", "Crack in wall", "1. Determine if crack is growing. 2. Clean crack area. 3. Apply mesh tape and joint compound for small cracks. 4. Consult professional for large cracks.", 50.0, "2 hours", "Medium"),
        ("Structural", "Squeaky door", "1. Apply lubricant to hinges. 2. Tighten hinge screws. 3. Check door alignment. 4. Replace hinges if severely worn.", 15.0, "15 minutes", "Easy"),
        ("Structural", "Sticking window", "1. Clean window tracks. 2. Lubricate tracks and hardware. 3. Check for paint buildup. 4. Adjust window if needed.", 25.0, "30 minutes", "Easy"),
        ("Appliance", "Refrigerator not cooling", "1. Check temperature settings. 2. Clean condenser coils. 3. Ensure adequate clearance around unit. 4. Check door seals.", 80.0, "1 hour", "Medium"),
        ("Appliance", "Washing machine not draining", "1. Check for kinks in drain hose. 2. Clean lint filter. 3. Check for clogs in drain. 4. Verify drain hose height.", 60.0, "45 minutes", "Medium"),
        ("Appliance", "Dishwasher not cleaning", "1. Check spray arms for clogs. 2. Clean filter at bottom. 3. Use proper detergent amount. 4. Check water temperature.", 40.0, "30 minutes", "Easy")
    ]

    for solution in sample_solutions:
        c.execute(
            "INSERT INTO solutions_database (issue_category, problem_description, solution_steps, estimated_cost, estimated_time, difficulty_level, created_at) VALUES (?,?,?,?,?,?,?)",
            (*solution, datetime.now().isoformat())
        )

    # Insert maintenance requests with various scenarios
    categories = ["Plumbing", "Electrical", "HVAC", "Structural", "Appliance", "Other"]
    priorities = ["High", "Medium", "Low"]
    statuses = ["Pending", "In Progress", "Resolved", "Rejected"]
    urgencies = ["Normal", "Urgent", "Emergency"]

    request_descriptions = [
        "Kitchen sink is leaking under the cabinet, water pooling on floor",
        "Bathroom light switch not working, no power to fixture",
        "Air conditioning not cooling properly, warm air coming out",
        "Crack appeared in living room wall near window",
        "Refrigerator making loud noises and not cooling",
        "Toilet keeps running after flushing",
        "Outlet in bedroom not working, tried resetting breaker",
        "Heating system not turning on despite thermostat setting",
        "Door handle is loose and difficult to turn",
        "Washing machine not draining water after cycle",
        "Ceiling light flickering intermittently",
        "Hot water running out quickly in shower",
        "Window in bedroom won't close properly",
        "Garbage disposal not working and making noise",
        "Smoke detector beeping constantly",
        "Dishwasher leaving spots on dishes and not cleaning well",
        "Bathroom fan not working, no ventilation",
        "Thermostat display is blank and unresponsive",
        "Kitchen faucet has very low water pressure",
        "Closet door is sticking and hard to open"
    ]

    for i in range(len(request_descriptions)):
        tenant_id = random.randint(1, len(sample_tenants))
        category = random.choice(categories)
        priority = random.choice(priorities)
        status = random.choice(statuses)
        urgency = random.choice(urgencies)
        created_at = (datetime.now() - timedelta(days=random.randint(0, 30))).strftime("%Y-%m-%d %H:%M:%S")
        estimated_cost = round(random.uniform(50, 500), 2)

        scheduled_date = (datetime.now() + timedelta(days=random.randint(0, 7))).strftime("%Y-%m-%d %H:%M:%S")

        assigned_vendor_id = random.randint(1, len(sample_vendors)) if random.choice([True, False]) else None

        c.execute(
            '''INSERT INTO maintenance_requests
            (tenant_id, category, description, priority, status, urgency, created_at, estimated_cost, scheduled_date, assigned_vendor_id)
            VALUES (?,?,?,?,?,?,?,?,?,?)''',
            (tenant_id, category, request_descriptions[i % len(request_descriptions)], priority, status, urgency, created_at, estimated_cost, scheduled_date, assigned_vendor_id)
        )

    logger.info("Sample data inserted successfully - 25+ tenants, multiple vendors, comprehensive solutions database")

if __name__ == "__main__":
    init_db(force_reset=True)