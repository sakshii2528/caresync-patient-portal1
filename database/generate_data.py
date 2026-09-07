# generate_data.py
# CareSync Sample Data Generator
#
# This script populates the CareSync database with realistic test data.
# It is SAFE TO RUN MULTIPLE TIMES.
# Each run clears the previously generated data and creates fresh data.
#
# Required libraries:
#   pip install mysql-connector-python
#   pip install Faker

import mysql.connector
import random
from faker import Faker
from datetime import date, timedelta

# Create a Faker instance set to India
fake = Faker('en_IN')

# ─── DATABASE CONNECTION ────────────────────────────────────────────────────

connection = mysql.connector.connect(
    host='localhost',
    port=3306,
    user='root',
    password='',
    database='caresync'
)

cursor = connection.cursor()

print('Connected to MySQL successfully.')

# ─── CONSTANTS ──────────────────────────────────────────────────────────────

NUM_DOCTORS      = 40
NUM_PATIENTS     = 500
NUM_APPOINTMENTS = 3000
NUM_BILLS        = 2500

BILL_REJECT_LOW  = 0.08
BILL_REJECT_HIGH = 0.12

SPECIALISATIONS = [
    'Cardiology',
    'General Medicine',
    'Orthopaedics',
    'Gynaecology',
    'Paediatrics',
    'Neurology',
    'Dermatology',
    'Ophthalmology',
    'ENT',
    'Psychiatry',
    'Oncology',
    'Urology',
    'Endocrinology'
]

BLOOD_GROUPS = [
    'A+', 'A-', 'B+', 'B-',
    'O+', 'O-', 'AB+', 'AB-'
]

DIAGNOSES = [
    'Hypertension',
    'Type 2 Diabetes',
    'Upper Respiratory Infection',
    'Migraine',
    'Lumbar Spondylosis',
    'Anxiety Disorder',
    'Anaemia',
    'Hypothyroidism',
    'Gastritis',
    'Urinary Tract Infection',
    'Dengue Fever',
    'Viral Fever',
    'Asthma',
    'Arthritis',
    'Obesity',
    'Iron Deficiency',
    'Vitamin D Deficiency',
    'Sinusitis',
    'Eczema'
]

REJECTION_REASONS = [
    'Insurance claim limit exceeded for this policy year.',
    'Procedure not covered under current insurance plan.',
    'Pre-authorisation was not obtained before treatment.',
    'Patient not eligible under submitted insurance policy number.',
    'Duplicate claim submitted for the same service date.',
    'Medical documents submitted are incomplete.',
    'Claim submitted after the deadline specified by insurer.'
]

# ─── STEP 0: CLEAR OLD GENERATED DATA ───────────────────────────────────────

print()
print('Clearing previous generated data...')

# Delete child/dependent tables FIRST.
# This prevents foreign-key constraint errors.

tables_to_clear = [
    'billing',
    'appointment',
    'patient',
    'doctor'
]

for table in tables_to_clear:
    try:
        cursor.execute(f'DELETE FROM {table}')
        print(f'  Cleared {table}.')
    except mysql.connector.Error as err:
        print(f'  Could not clear {table}: {err}')

connection.commit()

print('Previous data cleared successfully.')

# ─── STEP 1: INSERT DOCTORS ─────────────────────────────────────────────────

print()
print(f'Inserting {NUM_DOCTORS} doctors...')

doctor_ids = []

for i in range(NUM_DOCTORS):

    name = 'Dr. ' + fake.name()

    spec = random.choice(SPECIALISATIONS)

    phone = '9' + str(
        random.randint(100000000, 999999999)
    )

    # Unique because i is unique
    email = f'doctor{i + 1}@caresync.in'

    # Unique licence number
    lic = f'MCI-{2000 + i:04d}'

    cursor.execute(
        '''
        INSERT INTO doctor
            (full_name, specialisation, phone, email, licence_number)
        VALUES
            (%s, %s, %s, %s, %s)
        ''',
        (name, spec, phone, email, lic)
    )

    doctor_ids.append(cursor.lastrowid)

connection.commit()

print(f'  Done. Inserted {len(doctor_ids)} doctors.')

# ─── STEP 2: INSERT PATIENTS ────────────────────────────────────────────────

print()
print(f'Inserting {NUM_PATIENTS} patients...')

patient_ids = []

for i in range(NUM_PATIENTS):

    name = fake.name()

    dob = fake.date_of_birth(
        minimum_age=5,
        maximum_age=85
    )

    gender = random.choice([
        'Male',
        'Female'
    ])

    phone = '9' + str(
        random.randint(100000000, 999999999)
    )

    # Unique email
    email = f'patient{i + 1}@example.com'

    address = fake.address().replace(
        '\n',
        ', '
    )

    blood = random.choice(BLOOD_GROUPS)

    ec_name = fake.name()

    ec_phone = '9' + str(
        random.randint(100000000, 999999999)
    )

    cursor.execute(
        '''
        INSERT INTO patient
            (
                full_name,
                date_of_birth,
                gender,
                phone,
                email,
                address,
                blood_group,
                emergency_contact_name,
                emergency_contact_phone
            )
        VALUES
            (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        ''',
        (
            name,
            dob,
            gender,
            phone,
            email,
            address,
            blood,
            ec_name,
            ec_phone
        )
    )

    patient_ids.append(cursor.lastrowid)

connection.commit()

print(f'  Done. Inserted {len(patient_ids)} patients.')

# ─── STEP 3: INSERT APPOINTMENTS ────────────────────────────────────────────

print()
print(f'Inserting {NUM_APPOINTMENTS} appointments...')

appointment_ids = []

# Generate appointments over the past 2 years
start_date = date.today() - timedelta(days=730)
end_date = date.today()

hour_options = list(range(9, 17))
minute_options = [0, 15, 30, 45]

for _ in range(NUM_APPOINTMENTS):

    p_id = random.choice(patient_ids)

    d_id = random.choice(doctor_ids)

    appt_dt = start_date + timedelta(
        days=random.randint(0, 730)
    )

    appt_tm = (
        f'{random.choice(hour_options):02d}:'
        f'{random.choice(minute_options):02d}:00'
    )

    reason = (
        'Patient complaints of ' +
        random.choice(DIAGNOSES).lower()
    )

    diag = random.choice(DIAGNOSES)

    # 80% Completed
    # 10% Scheduled
    # 10% Cancelled

    status = random.choices(
        [
            'Completed',
            'Scheduled',
            'Cancelled'
        ],
        weights=[
            80,
            10,
            10
        ]
    )[0]

    cursor.execute(
        '''
        INSERT INTO appointment
            (
                patient_id,
                doctor_id,
                appointment_date,
                appointment_time,
                reason,
                diagnosis,
                status
            )
        VALUES
            (%s, %s, %s, %s, %s, %s, %s)
        ''',
        (
            p_id,
            d_id,
            appt_dt,
            appt_tm,
            reason,
            diag,
            status
        )
    )

    appointment_ids.append(cursor.lastrowid)

connection.commit()

print(
    f'  Done. Inserted {len(appointment_ids)} appointments.'
)

# ─── STEP 4: INSERT BILLS ───────────────────────────────────────────────────

print()
print(f'Inserting {NUM_BILLS} bills...')

# Only completed appointments can have bills

cursor.execute(
    '''
    SELECT appointment_id, patient_id
    FROM appointment
    WHERE status = %s
    ''',
    ('Completed',)
)

completed_appointments = cursor.fetchall()

if len(completed_appointments) < NUM_BILLS:

    print(
        f'  Note: Only {len(completed_appointments)} '
        f'completed appointments available.'
    )

    print(
        f'  Will create one bill per completed appointment.'
    )

    bills_to_create = completed_appointments

else:

    bills_to_create = random.sample(
        completed_appointments,
        NUM_BILLS
    )

# Rejection rate between 8% and 12%

reject_rate = random.uniform(
    BILL_REJECT_LOW,
    BILL_REJECT_HIGH
)

print(
    f'  Bill rejection rate for this run: '
    f'{reject_rate * 100:.1f}%'
)

bills_inserted = 0

for appt_id, p_id in bills_to_create:

    # Consultation fee between ₹300 and ₹3000
    total = round(
        random.uniform(300, 3000),
        2
    )

    rand_val = random.random()

    # ── REJECTED ────────────────────────────────────────────────────────────

    if rand_val < reject_rate:

        status = 'Rejected'

        amount_paid = 0.00

        discount = 0.00

        reject_reason = random.choice(
            REJECTION_REASONS
        )

    # ── PARTIALLY PAID ─────────────────────────────────────────────────────

    elif rand_val < reject_rate + 0.10:

        status = 'Partially Paid'

        paid_pct = random.uniform(
            0.30,
            0.70
        )

        amount_paid = round(
            total * paid_pct,
            2
        )

        discount = 0.00

        reject_reason = None

    # ── PENDING ─────────────────────────────────────────────────────────────

    elif rand_val < reject_rate + 0.15:

        status = 'Pending'

        amount_paid = 0.00

        discount = 0.00

        reject_reason = None

    # ── PAID ────────────────────────────────────────────────────────────────

    else:

        status = 'Paid'

        discount = round(
            total * random.uniform(0, 0.05),
            2
        )

        amount_paid = round(
            total - discount,
            2
        )

        reject_reason = None

    # Get appointment date

    cursor.execute(
        '''
        SELECT appointment_date
        FROM appointment
        WHERE appointment_id = %s
        ''',
        (appt_id,)
    )

    row = cursor.fetchone()

    appt_date = row[0]

    bill_date = (
        appt_date +
        timedelta(days=random.randint(0, 2))
    )

    due_date = (
        bill_date +
        timedelta(days=30)
    )

    cursor.execute(
        '''
        INSERT INTO billing
            (
                appointment_id,
                patient_id,
                total_amount,
                amount_paid,
                discount,
                status,
                rejection_reason,
                bill_date,
                due_date
            )
        VALUES
            (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        ''',
        (
            appt_id,
            p_id,
            total,
            amount_paid,
            discount,
            status,
            reject_reason,
            bill_date,
            due_date
        )
    )

    bills_inserted += 1

connection.commit()

print(
    f'  Done. Inserted {bills_inserted} bills.'
)

# ─── STEP 5: VERIFY ROW COUNTS ──────────────────────────────────────────────

print()
print('=== FINAL ROW COUNTS ===')

for table in [
    'doctor',
    'patient',
    'appointment',
    'billing',
    'activity_log'
]:

    cursor.execute(
        f'SELECT COUNT(*) FROM {table}'
    )

    count = cursor.fetchone()[0]

    print(
        f'  {table:20s}: {count} rows'
    )

# ─── CLEANUP ────────────────────────────────────────────────────────────────

cursor.close()
connection.close()

print()
print('Done. Database is ready for use.')
