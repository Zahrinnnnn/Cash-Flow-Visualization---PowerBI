# generate_sample_data.py
# Generates a realistic Malaysian business cash flow transaction dataset
# Output: data/transactions_sample.csv
# Run: python scripts/generate_sample_data.py

import csv
import random
from datetime import date, timedelta

# ---------------------------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------------------------

OUTPUT_FILE   = "data/transactions_sample.csv"
START_DATE    = date(2025, 1, 1)
END_DATE      = date(2025, 12, 31)
TARGET_ROWS   = 750          # total transactions to generate
LARGE_TX_FLAG = 50_000.00    # threshold (MYR) to flag as Large Transaction
RANDOM_SEED   = 42           # fix seed for reproducible output

random.seed(RANDOM_SEED)

# ---------------------------------------------------------------------------
# REFERENCE DATA - Malaysian context
# ---------------------------------------------------------------------------

BANK_ACCOUNTS = [
    "Maybank",
    "CIMB",
    "Hong Leong Bank",
    "RHB Bank",
]

# Each entry: (Category, Sub-Category, Type, Description template, Counterparty pool, Amount range)
TRANSACTION_TYPES = [

    # --- INFLOWS ---
    (
        "Revenue", "Client Payment", "Inflow",
        "Client payment - invoice {inv}",
        [
            "Petronas Dagangan Sdn Bhd",
            "Telekom Malaysia Berhad",
            "Sime Darby Property Berhad",
            "IHH Healthcare Berhad",
            "Hartalega Holdings Berhad",
            "Maxis Berhad",
            "YTL Corporation Berhad",
            "Axiata Group Berhad",
            "MISC Berhad",
            "Gamuda Berhad",
        ],
        (5_000, 80_000),
        0.22,   # weight: proportion of total transactions
    ),
    (
        "Revenue", "Project Payment", "Inflow",
        "Project milestone payment - {proj}",
        [
            "Sunway Group",
            "IJM Corporation Berhad",
            "UEM Sunrise Berhad",
            "Malaysian Resources Corporation Berhad",
            "Eco World Development Group",
        ],
        (15_000, 120_000),
        0.10,
    ),
    (
        "Revenue", "Retainer Fee", "Inflow",
        "Monthly retainer - {month}",
        [
            "Kenanga Investment Bank",
            "AmBank Group",
            "Public Bank Berhad",
            "Hong Leong Financial Group",
            "Alliance Bank Malaysia",
        ],
        (3_000, 12_000),
        0.08,
    ),
    (
        "Revenue", "Consulting Fee", "Inflow",
        "Consulting fee - {desc}",
        [
            "KPMG Malaysia",
            "Deloitte Malaysia",
            "Ernst & Young Malaysia",
            "PwC Malaysia",
            "Crowe Malaysia",
        ],
        (2_000, 30_000),
        0.05,
    ),

    # --- OUTFLOWS ---
    (
        "Payroll", "Salary", "Outflow",
        "Staff salary - {month}",
        ["Payroll - Internal"],
        (18_000, 35_000),
        0.10,
    ),
    (
        "Payroll", "EPF Contribution", "Outflow",
        "EPF employer contribution - {month}",
        ["Kumpulan Wang Simpanan Pekerja (KWSP)"],
        (2_500, 5_000),
        0.05,
    ),
    (
        "Payroll", "SOCSO & EIS", "Outflow",
        "SOCSO and EIS contribution - {month}",
        ["PERKESO"],
        (300, 800),
        0.04,
    ),
    (
        "Operating Expenses", "Office Rent", "Outflow",
        "Office rental - {month}",
        [
            "IGB Real Estate Investment Trust",
            "Pavilion REIT",
            "CapitaLand Malaysia Mall Trust",
        ],
        (4_500, 8_000),
        0.04,
    ),
    (
        "Operating Expenses", "Utilities", "Outflow",
        "Electricity & water bill - {month}",
        ["Tenaga Nasional Berhad (TNB)", "Syabas Puncak Niaga"],
        (400, 1_200),
        0.05,
    ),
    (
        "Operating Expenses", "Telecommunications", "Outflow",
        "Internet & phone - {month}",
        ["Telekom Malaysia (TM)", "Maxis Business", "TIME dotCom"],
        (300, 900),
        0.04,
    ),
    (
        "Operating Expenses", "Office Supplies", "Outflow",
        "Office supplies purchase",
        [
            "Stabilo Malaysia",
            "MPH Bookstores",
            "Jaya Grocer",
            "Harvey Norman Malaysia",
        ],
        (150, 1_500),
        0.04,
    ),
    (
        "Operating Expenses", "Professional Services", "Outflow",
        "Professional services - {desc}",
        [
            "Messrs Ranjit Singh & Yeoh",
            "Lee Hishammuddin Allen & Gledhill",
            "Skrine Advocates & Solicitors",
        ],
        (1_500, 10_000),
        0.03,
    ),
    (
        "Cost of Goods", "Materials & Supplies", "Outflow",
        "Materials purchase - PO {inv}",
        [
            "Nippon Paint Malaysia",
            "CSC Steel Holdings Berhad",
            "Ann Joo Resources Berhad",
            "Cahya Mata Sarawak Berhad",
        ],
        (3_000, 40_000),
        0.05,
    ),
    (
        "Cost of Goods", "Subcontractor", "Outflow",
        "Subcontractor payment - {proj}",
        [
            "WCT Holdings Berhad",
            "Mudajaya Group Berhad",
            "Protasco Berhad",
        ],
        (8_000, 60_000),
        0.04,
    ),
    (
        "Tax", "SST Payment", "Outflow",
        "Sales & Service Tax - {month}",
        ["Lembaga Hasil Dalam Negeri (LHDN)"],
        (1_000, 8_000),
        0.03,
    ),
    (
        "Tax", "Income Tax Instalment", "Outflow",
        "Income tax instalment CP500 - {month}",
        ["Lembaga Hasil Dalam Negeri (LHDN)"],
        (2_000, 12_000),
        0.03,
    ),
    (
        "CAPEX", "Equipment Purchase", "Outflow",
        "Equipment purchase - {desc}",
        [
            "Hewlett-Packard Malaysia",
            "Dell Technologies Malaysia",
            "Canon Marketing Malaysia",
            "Brother International Malaysia",
        ],
        (2_000, 25_000),
        0.02,
    ),
    (
        "CAPEX", "Software & Licences", "Outflow",
        "Software licence - {desc}",
        [
            "Microsoft Malaysia",
            "Adobe Systems Malaysia",
            "SAP Malaysia",
            "Oracle Malaysia",
        ],
        (500, 15_000),
        0.02,
    ),
    (
        "Loan Repayment", "Bank Loan", "Outflow",
        "Term loan repayment - {month}",
        ["Maybank Business Banking", "CIMB Business Loan"],
        (3_500, 12_000),
        0.03,
    ),
    (
        "Loan Repayment", "Hire Purchase", "Outflow",
        "Vehicle hire purchase - {month}",
        ["Maybank Hire Purchase", "RHB Hire Purchase"],
        (800, 2_500),
        0.02,
    ),
]

# ---------------------------------------------------------------------------
# HELPER DATA
# ---------------------------------------------------------------------------

MONTHS_MY = [
    "Jan 2025", "Feb 2025", "Mac 2025", "Apr 2025",
    "Mei 2025", "Jun 2025", "Jul 2025", "Ogos 2025",
    "Sep 2025", "Okt 2025", "Nov 2025", "Dis 2025",
]

INVOICE_PREFIXES = ["INV", "SO", "PO", "OR"]

PROJECT_NAMES = [
    "Office Renovation Phase 1",
    "IT Infrastructure Upgrade",
    "Digital Transformation Initiative",
    "Warehouse Expansion",
    "ERP Implementation",
    "Website Redevelopment",
]

EQUIPMENT_NAMES = [
    "laptop units (x5)",
    "colour laser printer",
    "server rack upgrade",
    "UPS battery replacement",
    "surveillance camera system",
]

SOFTWARE_NAMES = [
    "Microsoft 365 annual renewal",
    "Adobe Creative Cloud",
    "Xero accounting subscription",
    "AutoCAD licence",
    "antivirus - annual",
]

CONSULTING_DESCS = [
    "digital strategy review",
    "financial due diligence",
    "HR audit and benchmarking",
    "ISO 9001 gap assessment",
    "process improvement workshop",
]

NOTES_POOL = [
    "",  # most rows have no notes - keep it realistic
    "",
    "",
    "Approved by CFO",
    "Urgent payment",
    "Revised amount per credit note",
    "Partial payment - balance next month",
    "Direct debit",
    "Recurring monthly",
    "One-off purchase",
]

# ---------------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------------

def random_date(start: date, end: date) -> date:
    delta = (end - start).days
    return start + timedelta(days=random.randint(0, delta))


def random_amount(low: float, high: float) -> float:
    # Skew toward lower end so large values are less common
    raw = random.triangular(low, high, low + (high - low) * 0.3)
    # Round to nearest 50 sen (realistic for Malaysian invoices)
    return round(raw * 2, 0) / 2


def fill_description(template: str, tx_date: date) -> str:
    month_str = tx_date.strftime("%b %Y")
    inv       = "{}-{:04d}".format(random.choice(INVOICE_PREFIXES), random.randint(1000, 9999))
    proj      = random.choice(PROJECT_NAMES)
    desc_pool = EQUIPMENT_NAMES + SOFTWARE_NAMES + CONSULTING_DESCS
    desc      = random.choice(desc_pool)
    return (
        template
        .replace("{month}", month_str)
        .replace("{inv}",   inv)
        .replace("{proj}",  proj)
        .replace("{desc}",  desc)
    )


def build_weights(tx_types: list) -> list:
    """Extract the weight field and normalise to sum to 1."""
    weights = [t[6] for t in tx_types]
    total   = sum(weights)
    return [w / total for w in weights]

# ---------------------------------------------------------------------------
# GENERATION
# ---------------------------------------------------------------------------

def generate_transactions(n: int) -> list[dict]:
    weights = build_weights(TRANSACTION_TYPES)
    rows    = []

    for i in range(1, n + 1):
        tx_id = f"TXN-{i:05d}"

        # Pick a transaction type according to weights
        tx_type = random.choices(TRANSACTION_TYPES, weights=weights, k=1)[0]
        category, sub_category, flow_type, desc_template, counterparties, amount_range, _ = tx_type

        tx_date      = random_date(START_DATE, END_DATE)
        description  = fill_description(desc_template, tx_date)
        counterparty = random.choice(counterparties)
        account      = random.choice(BANK_ACCOUNTS)
        amount       = random_amount(*amount_range)
        note         = random.choice(NOTES_POOL)

        # Large transaction flag
        if amount >= LARGE_TX_FLAG:
            flag = "Large Transaction"
        else:
            flag = ""

        rows.append({
            "Transaction ID":  tx_id,
            "Date":            tx_date.strftime("%Y-%m-%d"),
            "Description":     description,
            "Category":        category,
            "Sub-Category":    sub_category,
            "Account":         account,
            "Type":            flow_type,
            "Amount":          f"{amount:.2f}",
            "Counterparty":    counterparty,
            "Notes":           note,
            "Flag":            flag,
        })

    # Sort by date so the file reads chronologically
    rows.sort(key=lambda r: r["Date"])
    return rows


def write_csv(rows: list[dict], filepath: str) -> None:
    fieldnames = [
        "Transaction ID", "Date", "Description", "Category",
        "Sub-Category", "Account", "Type", "Amount",
        "Counterparty", "Notes", "Flag",
    ]
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

# ---------------------------------------------------------------------------
# SUMMARY REPORT - printed to console after generation
# ---------------------------------------------------------------------------

def print_summary(rows: list[dict]) -> None:
    total        = len(rows)
    inflows      = [r for r in rows if r["Type"] == "Inflow"]
    outflows     = [r for r in rows if r["Type"] == "Outflow"]
    large        = [r for r in rows if r["Flag"] == "Large Transaction"]

    total_in     = sum(float(r["Amount"]) for r in inflows)
    total_out    = sum(float(r["Amount"]) for r in outflows)
    net          = total_in - total_out

    print("\n=== Sample Dataset Summary ===")
    print(f"  Total transactions : {total:,}")
    print(f"  Inflow rows        : {len(inflows):,}  (MYR {total_in:,.2f})")
    print(f"  Outflow rows       : {len(outflows):,}  (MYR {total_out:,.2f})")
    print(f"  Net cash flow      : MYR {net:,.2f}")
    print(f"  Large transactions : {len(large):,}  (>= MYR {LARGE_TX_FLAG:,.2f})")
    print(f"\n  Output saved to    : {OUTPUT_FILE}")
    print("==============================\n")

# ---------------------------------------------------------------------------
# ENTRY POINT
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print(f"Generating {TARGET_ROWS} transactions ({START_DATE} to {END_DATE})...")

    rows = generate_transactions(TARGET_ROWS)
    write_csv(rows, OUTPUT_FILE)
    print_summary(rows)
