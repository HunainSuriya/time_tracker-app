# time_tracker/api/billing_api.py
# ============================================================
# 🎯 TOPIC: Advanced API Patterns — Billing & Reports
# ============================================================

import frappe
from frappe import _
from frappe.utils import flt, today, getdate, add_months


# ============================================================
# ADVANCED LESSON: Chaining Whitelisted Methods
# ============================================================
# Real-world APIs often need to call OTHER whitelisted methods.
# You can call them directly as Python functions — no HTTP needed!
# ============================================================

@frappe.whitelist()
def generate_invoice(project, month=None, year=None):
    """
    Generate a billing invoice for a project for a given month.

    This is an ADVANCED method that:
    1. Fetches time logs
    2. Calculates billing
    3. Creates an invoice document
    4. Returns the invoice details

    Teaches: multi-step API operations, document creation chains
    """

    import datetime
    today_date = datetime.date.today()
    month = int(month or today_date.month)
    year = int(year or today_date.year)

    # ── Check roles ──────────────────────────────────────────
    frappe.only_for(["Time Tracker Manager", "System Manager"])

    # ── Fetch billing rate from Project ──────────────────────
    # get_value with multiple fields → pass a list
    project_data = frappe.db.get_value(
        "Project",
        project,
        ["project_name", "billing_rate", "customer"],   # fetch multiple fields
        as_dict=True                                     # return as dict
    )

    if not project_data:
        frappe.throw(_("Project {0} not found").format(project))

    billing_rate = flt(project_data.billing_rate)
    if not billing_rate:
        frappe.throw(_("Billing rate not set for project {0}").format(project))

    # ── Fetch all time logs for this month ───────────────────
    logs = frappe.db.sql("""
        SELECT
            name,
            hours,
            log_date,
            logged_by,
            description
        FROM `tabTime Log`
        WHERE
            project = %(project)s
            AND MONTH(log_date) = %(month)s
            AND YEAR(log_date) = %(year)s
            AND docstatus = 0
        ORDER BY log_date
    """, {
        "project": project,
        "month": month,
        "year": year
    }, as_dict=True)
    # ↑ Using named parameters %(name)s instead of %s for readability

    if not logs:
        frappe.throw(_("No time logs found for {0} in {1}/{2}").format(project, month, year))

    total_hours = sum(flt(log.hours) for log in logs)
    total_amount = total_hours * billing_rate

    # ── Build invoice data ───────────────────────────────────
    invoice_data = {
        "project": project,
        "customer": project_data.customer,
        "month": month,
        "year": year,
        "total_hours": total_hours,
        "billing_rate": billing_rate,
        "total_amount": total_amount,
        "logs": [dict(log) for log in logs],  # convert Row objects to plain dicts
        "generated_on": today(),
        "generated_by": frappe.session.user
    }

    return invoice_data


# ============================================================
# ADVANCED LESSON: Using frappe.enqueue() for Heavy Tasks
# ============================================================
# If an API method takes too long (>30 seconds), the browser times out.
# Solution: run it in the BACKGROUND using frappe.enqueue()
# ============================================================

@frappe.whitelist()
def export_annual_report(year):
    """
    Heavy report — runs in background to avoid timeout.
    Teaches: background jobs with frappe.enqueue()
    """

    year = int(year)

    # ── frappe.enqueue() — run in background ─────────────────
    # Instead of running the heavy function NOW, schedule it.
    # The user gets an immediate response, and the job runs in background.
    frappe.enqueue(
        method="time_tracker.api.billing_api._generate_annual_report_job",
        queue="long",            # "short"(5min), "default"(1hr), "long"(no limit)
        timeout=1800,            # 30 minutes max
        now=False,               # False = background, True = run immediately (for testing)
        year=year,               # ← extra kwargs passed to the function
        requested_by=frappe.session.user
    )

    return {
        "message": f"Annual report for {year} is being generated.",
        "tip": "Check Scheduled Job Log in ERPNext when complete."
    }


def _generate_annual_report_job(year, requested_by):
    """
    This runs in the background (not whitelisted — users don't call this directly).
    Naming convention: prefix with _ to signal it's internal.
    """
    # ... heavy computation here ...
    # When done, you can send an email notification:
    frappe.sendmail(
        recipients=[requested_by],
        subject=f"Annual Report {year} Ready",
        message=f"Your annual time tracking report for {year} has been generated."
    )


# ============================================================
# ADVANCED LESSON: Returning File Downloads from API
# ============================================================

@frappe.whitelist()
def download_timesheet_csv(project, month, year):
    """
    Returns a CSV file for download via API.
    Teaches: file response from whitelisted method
    """

    frappe.only_for(["Time Tracker Manager", "System Manager"])

    logs = frappe.db.get_list(
        "Time Log",
        filters={
            "project": project,
            "log_date": ["between", [f"{year}-{month:02d}-01", f"{year}-{month:02d}-28"]]
        },
        fields=["log_date", "logged_by", "hours", "description"]
    )

    # Build CSV content
    lines = ["Date,Employee,Hours,Description"]
    for log in logs:
        lines.append(f"{log.log_date},{log.logged_by},{log.hours},{log.description or ''}")

    csv_content = "\n".join(lines)

    # ── frappe.response — control the HTTP response directly ──
    # Set this to make Frappe return a file download instead of JSON.
    frappe.response['filename'] = f"timesheet_{project}_{year}_{month}.csv"
    frappe.response['filecontent'] = csv_content
    frappe.response['type'] = 'download'
    # No return value needed — frappe.response handles it


# ============================================================
# TESTING YOUR API — Complete Postman Guide
# ============================================================
POSTMAN_GUIDE = """
=== SETTING UP POSTMAN FOR FRAPPE API ===

1. GET YOUR API KEYS:
   ERPNext → top-right menu → My Settings → API Access
   Click "Generate Keys" — copy api_key and api_secret

2. SET AUTHORIZATION IN POSTMAN:
   In Headers tab, add:
   Key:   Authorization
   Value: token your_api_key:your_api_secret

3. BASE URL:
   http://yoursite.localhost  (local)
   https://yourcompany.erpnext.com  (cloud)

4. TEST ENDPOINTS:

   ── Hello (no args) ──────────────────────────
   GET /api/method/time_tracker.api.time_api.hello_frappe

   ── Log Time (POST with form data) ───────────
   POST /api/method/time_tracker.api.time_api.log_time
   Body → form-data:
     project     = PROJ-001
     hours       = 3.5
     description = Fixed authentication bug

   ── Project Summary (GET with query param) ───
   GET /api/method/time_tracker.api.time_api.get_project_summary?project=PROJ-001

   ── Generate Invoice (POST) ──────────────────
   POST /api/method/time_tracker.api.billing_api.generate_invoice
   Body → form-data:
     project = PROJ-001
     month   = 12
     year    = 2024

5. RESPONSE FORMAT:
   All Frappe API responses look like:
   {
     "message": <your_return_value>   ← this is what you return
   }
   
   Errors look like:
   {
     "exc_type": "ValidationError",
     "exc": "...traceback...",
     "_server_messages": "[{\\"message\\":\\"Your error message\\"}]"
   }

=== PYTHON REQUESTS EXAMPLE ===
import requests

BASE = "http://yoursite.localhost"
AUTH = ("your_api_key", "your_api_secret")

# Log time
response = requests.post(
    f"{BASE}/api/method/time_tracker.api.time_api.log_time",
    data={"project": "PROJ-001", "hours": 3.5},
    auth=AUTH
)
print(response.json()["message"])
"""