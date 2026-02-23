# time_tracker/api/time_api.py
# ============================================================
# 🎯 TOPIC: Frappe Whitelisted Methods (REST API)
# ============================================================
# This is the MOST IMPORTANT file in this whole app.
# Every function here becomes a live REST API endpoint
# that you can call from:
#   ✅ JavaScript (frappe.call)
#   ✅ Postman
#   ✅ Mobile apps
#   ✅ External systems
#   ✅ Python (requests library)
# ============================================================

import frappe
from frappe import _
from frappe.utils import now_datetime, flt, today


# ============================================================
# LESSON 1: THE SIMPLEST WHITELISTED METHOD
# ============================================================
# @frappe.whitelist() is a Python DECORATOR.
# It tells Frappe: "This function is safe to call from outside."
# Without this decorator, calling the function via API gives 403 Forbidden.
#
# URL to call this: GET /api/method/time_tracker.api.time_api.hello_frappe
# ============================================================

@frappe.whitelist()
def hello_frappe():
    """
    The simplest possible API method.
    Returns a greeting. Use this to TEST that your app is working.

    Test in browser: yoursite.localhost/api/method/time_tracker.api.time_api.hello_frappe
    Test in Postman: GET http://yoursite.localhost/api/method/time_tracker.api.time_api.hello_frappe
    """

    # frappe.session.user → gives you the currently logged-in user
    # This is ALWAYS available in any whitelisted method
    current_user = frappe.session.user

    # Always return a DICT from whitelisted methods.
    # Frappe auto-converts it to JSON for the API response.
    # The response will look like: { "message": { "greeting": "...", "user": "..." } }
    return {
        "greeting": "Hello from Frappe!",
        "user": current_user,
        "timestamp": str(now_datetime())
    }


# ============================================================
# LESSON 2: ACCEPTING PARAMETERS
# ============================================================
# Parameters in whitelisted methods come from:
#   - GET: query string  → /api/method/...?project=PROJ-001
#   - POST: form data or JSON body
#
# IMPORTANT RULE: All parameters arrive as STRINGS.
# You must convert them manually (int(), float(), etc.)
# ============================================================

@frappe.whitelist()
def log_time(project, hours, description=None, log_date=None):
    """
    Logs working hours against a project.

    Parameters:
        project     (str, required): Project name e.g. "PROJ-001"
        hours       (str, required): Number of hours e.g. "3.5"  ← arrives as STRING!
        description (str, optional): What was done
        log_date    (str, optional): Date of work, defaults to today

    Returns:
        dict with the created Time Log name

    How to call from JS:
        frappe.call({
            method: 'time_tracker.api.time_api.log_time',
            args: {
                project: 'PROJ-001',
                hours: 3.5,
                description: 'Fixed login bug'
            },
            callback: function(r) {
                console.log(r.message);  // ← your return value is in r.message
            }
        });

    How to call from Postman:
        POST /api/method/time_tracker.api.time_api.log_time
        Body (form-data):
            project    = PROJ-001
            hours      = 3.5
            description = Fixed login bug
    """

    # ── STEP 1: VALIDATE INPUTS ─────────────────────────────
    # Always validate before doing anything.
    # frappe.throw() raises an exception AND sends error to API caller.
    # The _ function is for translation support (good practice).

    if not project:
        frappe.throw(_("Project is required"))

    # flt() = Frappe's safe float converter. Never use float() directly.
    # flt("abc") → 0.0 instead of crashing. Safe!
    hours = flt(hours)

    if hours <= 0:
        frappe.throw(_("Hours must be greater than 0"))

    if hours > 24:
        frappe.throw(_("Hours cannot exceed 24 in a day"))

    # ── STEP 2: CHECK PERMISSIONS ───────────────────────────
    # frappe.has_permission() checks if the current user can
    # read/write/create a specific DocType or document.
    # Always check permissions in API methods!

    if not frappe.has_permission("Time Log", "create"):
        frappe.throw(_("You don't have permission to create Time Logs"), frappe.PermissionError)

    # ── STEP 3: CHECK IF PROJECT EXISTS ─────────────────────
    # frappe.db.exists() → returns the name if found, else None
    # This is faster than fetching the full document just to check existence.

    if not frappe.db.exists("Project", project):
        frappe.throw(_("Project {0} does not exist").format(project))

    # ── STEP 4: CREATE THE DOCUMENT ─────────────────────────
    # frappe.get_doc() with a dict creates a NEW document in memory.
    # .insert() saves it to the database.

    time_log = frappe.get_doc({
        "doctype": "Time Log",          # ← which DocType to create
        "project": project,
        "hours": hours,
        "description": description or "",
        "log_date": log_date or today(),  # today() returns current date as string
        "logged_by": frappe.session.user  # auto-set to current user
    })

    # ignore_permissions=True means even if the DocType has submit workflow,
    # this insert will still work. Use carefully — only in trusted API methods.
    time_log.insert(ignore_permissions=False)

    # frappe.db.commit() saves the transaction to MySQL.
    # Without this, changes may not persist!
    frappe.db.commit()

    # ── STEP 5: RETURN RESPONSE ─────────────────────────────
    # Return a dict. Frappe sends it as: { "message": { ... } }
    return {
        "success": True,
        "time_log": time_log.name,          # e.g. "TL-2024-00001"
        "message": f"Logged {hours} hours for {project}"
    }


# ============================================================
# LESSON 3: FETCHING DATA — The Right Way
# ============================================================
# You'll often need to fetch lists or summaries.
# Learn the difference between frappe.db methods:
#   frappe.db.get_value()  → one value from one row
#   frappe.db.get_list()   → multiple rows (safe, respects permissions)
#   frappe.db.sql()        → raw SQL (powerful but use carefully)
# ============================================================

@frappe.whitelist()
def get_project_summary(project):
    """
    Returns total hours and billing amount for a project.

    This teaches you how to READ data via API.

    Call from JS:
        frappe.call({
            method: 'time_tracker.api.time_api.get_project_summary',
            args: { project: 'PROJ-001' },
            callback: (r) => console.log(r.message)
        })
    """

    if not frappe.db.exists("Project", project):
        frappe.throw(_("Project not found: {0}").format(project))

    # ── frappe.db.get_list() ─────────────────────────────────
    # Safe way to query. Respects user permissions automatically.
    # filters   → list of [doctype, field, operator, value]
    # fields    → which columns to fetch
    # order_by  → sort order
    # limit     → max rows (always set a limit!)

    logs = frappe.db.get_list(
        "Time Log",                          # DocType name
        filters={"project": project},        # WHERE project = 'PROJ-001'
        fields=["name", "hours", "log_date", "logged_by", "description"],
        order_by="log_date desc",
        limit=100
    )

    # ── frappe.db.get_value() ────────────────────────────────
    # Gets a SINGLE value from a single row. Fastest for simple lookups.
    # Syntax: frappe.db.get_value(doctype, name_or_filters, fieldname)

    project_billing_rate = frappe.db.get_value(
        "Project",          # DocType
        project,            # document name (the filter)
        "billing_rate"      # field to fetch
    ) or 0

    # Calculate totals in Python
    total_hours = sum(flt(log.hours) for log in logs)
    total_amount = total_hours * flt(project_billing_rate)

    return {
        "project": project,
        "total_hours": total_hours,
        "billing_rate": project_billing_rate,
        "total_amount": total_amount,
        "log_count": len(logs),
        "logs": logs   # list of dicts, auto-serialized to JSON
    }


# ============================================================
# LESSON 4: allow_guest=True — PUBLIC APIs (No Login Needed)
# ============================================================
# By default, whitelisted methods need the user to be logged in.
# Adding allow_guest=True makes the endpoint PUBLIC.
# Use for: webhooks, public status pages, health checks.
# ⚠️  NEVER expose sensitive data in guest methods!
# ============================================================

@frappe.whitelist(allow_guest=True)
def app_status():
    """
    Public endpoint — no login required.
    Good for health checks from monitoring tools.

    Test: GET /api/method/time_tracker.api.time_api.app_status
    Even works when NOT logged in to ERPNext.
    """

    # frappe.session.user is "Guest" when not logged in
    return {
        "status": "ok",
        "app": "Time Tracker",
        "version": "1.0.0",
        "caller": frappe.session.user   # will show "Guest" if not logged in
    }


# ============================================================
# LESSON 5: ROLE-BASED ACCESS in API
# ============================================================
# Sometimes @frappe.whitelist() alone isn't enough.
# You want only MANAGERS to call certain methods.
# Use frappe.only_for() or check roles manually.
# ============================================================

@frappe.whitelist()
def get_all_employees_hours(month=None, year=None):
    """
    Admin-only: Get a summary of ALL employees' hours.
    Regular users should NOT see this — only HR/Managers.

    Teaches: role-based API security
    """

    # ── frappe.only_for() ────────────────────────────────────
    # Throws PermissionError if the current user does NOT have this role.
    # Roles are defined in ERPNext under Setup > Roles.
    # "System Manager" is the superadmin role.

    frappe.only_for(["HR Manager", "System Manager"])
    # If the user doesn't have these roles, execution STOPS here with 403.

    # Use current month/year if not provided
    import datetime
    today_date = datetime.date.today()
    month = month or today_date.month
    year = year or today_date.year

    # ── frappe.db.sql() ──────────────────────────────────────
    # Raw SQL — use when frappe.db.get_list() isn't powerful enough.
    # ALWAYS use %s placeholders, NEVER string format for user input → SQL injection risk!
    # as_dict=True → returns list of dicts instead of list of tuples

    results = frappe.db.sql("""
        SELECT
            tl.logged_by,
            SUM(tl.hours) AS total_hours,
            COUNT(tl.name) AS entries,
            tl.project
        FROM `tabTime Log` tl
        WHERE
            MONTH(tl.log_date) = %s
            AND YEAR(tl.log_date) = %s
            AND tl.docstatus != 2
        GROUP BY tl.logged_by, tl.project
        ORDER BY total_hours DESC
    """, (month, year), as_dict=True)   # ← (month, year) are safe placeholders

    return {
        "month": month,
        "year": year,
        "data": results
    }


# ============================================================
# LESSON 6: CALLING THIS API FROM JAVASCRIPT
# ============================================================
# This is a reference — not Python code.
# Save this as a Client Script on any Form in ERPNext.
# ============================================================

JAVASCRIPT_REFERENCE = """
// ── Method 1: frappe.call() — The Standard Way ──────────────
// Use this for most cases. Handles CSRF tokens automatically.

frappe.call({
    method: 'time_tracker.api.time_api.log_time',
    args: {
        project: frm.doc.project,
        hours: 3.5,
        description: 'Completed API module'
    },
    // freeze = shows loading spinner on the page
    freeze: true,
    freeze_message: 'Logging time...',

    callback: function(response) {
        // response.message = whatever your Python function returned
        if (response.message.success) {
            frappe.msgprint('Time logged: ' + response.message.time_log);
            frm.reload_doc();  // refresh the form
        }
    }
});

// ── Method 2: frappe.xcall() — Promise-based (Modern) ────────
// Same as frappe.call but returns a Promise. Use with async/await.

async function logMyTime() {
    try {
        const result = await frappe.xcall(
            'time_tracker.api.time_api.log_time',
            { project: 'PROJ-001', hours: 2 }
        );
        console.log(result);   // result = r.message directly
    } catch (error) {
        frappe.msgprint('Error: ' + error.message);
    }
}

// ── Method 3: fetch() / Postman / External System ────────────
// When calling FROM OUTSIDE ERPNext (e.g., mobile app, Python script)
// You need API key + secret for authentication.

// Get your keys: ERPNext → Settings → My Account → API Access → Generate Keys
// Then pass as header:
//   Authorization: token api_key:api_secret

fetch('http://yoursite.localhost/api/method/time_tracker.api.time_api.get_project_summary?project=PROJ-001', {
    headers: {
        'Authorization': 'token abc123:xyz789'
    }
})
.then(r => r.json())
.then(data => console.log(data.message));
"""


# ============================================================
# LESSON 7: HANDLING ERRORS PROPERLY
# ============================================================
# Never let errors silently fail in APIs.
# Always give the caller a clear message.
# ============================================================

@frappe.whitelist()
def safe_update_hours(time_log_name, new_hours):
    """
    Update hours on an existing Time Log.
    Teaches proper error handling patterns.
    """

    new_hours = flt(new_hours)

    # ── Pattern: try/except with frappe.log_error() ──────────
    # frappe.log_error() saves the error to Error Log in ERPNext.
    # You can see them at: ERPNext → Setup → Error Log
    # This is your debugging best friend in production!

    try:
        # frappe.get_doc(doctype, name) → fetches an EXISTING document
        doc = frappe.get_doc("Time Log", time_log_name)

        # Check if the current user is the owner of this log
        # frappe.session.user → current logged-in user email
        if doc.logged_by != frappe.session.user:
            # Only System Manager can edit others' logs
            if not frappe.has_permission("Time Log", "write", doc=doc):
                frappe.throw(
                    _("You can only edit your own time logs"),
                    frappe.PermissionError
                )

        # Store old value for the response message
        old_hours = doc.hours

        # Update the field
        doc.hours = new_hours

        # .save() updates an existing document (vs .insert() for new ones)
        doc.save(ignore_permissions=False)
        frappe.db.commit()

        return {
            "success": True,
            "time_log": time_log_name,
            "old_hours": old_hours,
            "new_hours": new_hours,
            "message": f"Updated from {old_hours} to {new_hours} hours"
        }

    except frappe.PermissionError:
        # Re-raise permission errors (don't hide them)
        raise

    except frappe.DoesNotExistError:
        frappe.throw(_("Time Log {0} not found").format(time_log_name))

    except Exception as e:
        # Log unexpected errors to Error Log (visible in ERPNext UI)
        frappe.log_error(
            title="Time Tracker: Failed to update hours",
            message=frappe.get_traceback()  # full Python traceback
        )
        frappe.throw(_("Something went wrong. Check Error Log for details."))


# ============================================================
# LESSON 8: BULK OPERATIONS
# ============================================================
# How to handle multiple records in one API call
# ============================================================

@frappe.whitelist()
def bulk_log_time(logs):
    """
    Log multiple time entries in one API call.

    IMPORTANT: When you pass a list/dict from JavaScript,
    it arrives as a JSON STRING in Python.
    You MUST parse it with frappe.parse_json() or json.loads()

    JS call:
        frappe.call({
            method: '...bulk_log_time',
            args: {
                logs: [                          ← JS array
                    {project: 'P1', hours: 2},
                    {project: 'P2', hours: 3}
                ]
            }
        })
    """

    # ── CRITICAL: Parse JSON string back to Python list ──────
    # In JS you pass an array, but Python receives it as a string!
    # Always use frappe.parse_json() for safety (handles both string and dict).
    logs = frappe.parse_json(logs)

    if not isinstance(logs, list):
        frappe.throw(_("logs must be a list"))

    created = []
    errors = []

    for idx, log_data in enumerate(logs):
        try:
            # Validate each item
            if not log_data.get("project"):
                raise ValueError(f"Item {idx+1}: project is required")

            hours = flt(log_data.get("hours", 0))
            if hours <= 0:
                raise ValueError(f"Item {idx+1}: hours must be > 0")

            doc = frappe.get_doc({
                "doctype": "Time Log",
                "project": log_data["project"],
                "hours": hours,
                "description": log_data.get("description", ""),
                "log_date": log_data.get("log_date") or today(),
                "logged_by": frappe.session.user
            })
            doc.insert(ignore_permissions=False)
            created.append(doc.name)

        except Exception as e:
            # Collect errors but continue processing the rest
            errors.append({"index": idx, "error": str(e)})

    frappe.db.commit()

    return {
        "created": created,
        "created_count": len(created),
        "errors": errors,
        "error_count": len(errors)
    }


# ============================================================
# QUICK REFERENCE CHEAT SHEET
# ============================================================
#
# READ DATA:
#   frappe.db.get_value("DocType", name, "field")          → single value
#   frappe.db.get_list("DocType", filters={}, fields=[])   → list of dicts
#   frappe.db.sql("SELECT ...", (args,), as_dict=True)     → raw SQL
#   frappe.db.exists("DocType", name)                      → check existence
#
# WRITE DATA:
#   doc = frappe.get_doc({...})  → new doc (in memory)
#   doc.insert()                 → save NEW doc to DB
#   doc = frappe.get_doc("DocType", name)  → fetch existing
#   doc.field = value; doc.save()          → update existing
#   frappe.db.set_value("DocType", name, "field", value)   → quick update
#   frappe.db.commit()           → always commit after writes!
#
# SECURITY:
#   @frappe.whitelist()               → logged-in users only
#   @frappe.whitelist(allow_guest=True) → public, no login needed
#   frappe.only_for(["Role Name"])    → restrict to specific roles
#   frappe.has_permission(...)        → check before acting
#
# USER INFO:
#   frappe.session.user               → current user email
#   frappe.get_roles(frappe.session.user)  → list of their roles
#
# ERRORS:
#   frappe.throw(_("message"))        → user-visible error
#   frappe.log_error(title, message)  → save to Error Log
#   frappe.get_traceback()            → full Python traceback string
#
# UTILS:
#   flt(value)          → safe float conversion
#   frappe.parse_json() → parse JSON string to Python object
#   today()             → current date as "YYYY-MM-DD"
#   now_datetime()      → current datetime object
# ============================================================