# time_tracker/hooks.py
# ============================================================
# 🎯 TOPIC: Frappe Hooks — Auto-trigger your API methods
# ============================================================
# hooks.py is the "wiring" of your Frappe app.
# It tells Frappe WHEN to run your code automatically,
# without the user calling it manually.
# ============================================================

app_name = "time_tracker"
app_title = "Time Tracker"
app_publisher = "Your Software House"
app_description = "Project Time Tracking with REST API — Frappe Mastery App"
app_version = "1.0.0"


# ============================================================
# HOOK 1: doc_events
# ============================================================
# Run your Python function automatically when a document
# is created, updated, submitted, cancelled, etc.
#
# Common events:
#   "before_insert"   → runs BEFORE saving a new doc (can stop it)
#   "after_insert"    → runs AFTER a new doc is saved
#   "on_update"       → runs every time the doc is saved/updated
#   "on_submit"       → runs when doc is submitted (docstatus=1)
#   "on_cancel"       → runs when doc is cancelled
#   "before_delete"   → runs before deletion
# ============================================================

doc_events = {

    # When a Time Log is saved, auto-calculate billing
    "Time Log": {
        "before_insert": "time_tracker.api.time_api.validate_time_log",
        "after_insert":  "time_tracker.api.time_api.update_project_billing",
        "on_update":     "time_tracker.api.time_api.update_project_billing",
    },

    # When a Project is deleted, clean up related logs
    "Project": {
        "before_delete": "time_tracker.api.time_api.check_before_project_delete",
    }
}

# ── How to write a doc_event handler ────────────────────────
# In time_api.py, add:
#
# def validate_time_log(doc, method):
#     # doc    = the Time Log document being saved
#     # method = the event name e.g. "before_insert"
#     if doc.hours > 12:
#         frappe.throw("No single entry can exceed 12 hours")
#
# NOTE: doc_event handlers are NOT whitelisted — they are
# server-side only. The user never calls them directly.


# ============================================================
# HOOK 2: scheduler_events
# ============================================================
# Run code automatically on a SCHEDULE (like cron jobs).
# Perfect for: sending weekly reports, auto-billing, reminders.
# ============================================================

scheduler_events = {

    # Runs every day at midnight
    "daily": [
        "time_tracker.api.billing_api.generate_daily_billing_summary"
    ],

    # Runs every week (Monday midnight)
    "weekly": [
        "time_tracker.api.billing_api.send_weekly_timesheet_reminder"
    ],

    # Runs every hour
    "hourly": [
        "time_tracker.api.time_api.sync_external_time_tracker"
    ]
}


# ============================================================
# HOOK 3: override_whitelisted_methods
# ============================================================
# Replace a CORE ERPNext API method with your own version.
# Advanced use case — override standard behavior.
# ============================================================

# override_whitelisted_methods = {
#     "frappe.client.get_list": "time_tracker.api.time_api.custom_get_list"
# }


# ============================================================
# HOOK 4: fixtures
# ============================================================
# Export configuration data along with your app.
# When someone installs your app, these get imported automatically.
# Great for: custom fields, print formats, roles.
# ============================================================

fixtures = [
    # Export all Custom Fields added by this app
    {
        "doctype": "Custom Field",
        "filters": [["module", "=", "Time Tracker"]]
    },

    # Export specific Roles created by this app
    {
        "doctype": "Role",
        "filters": [["name", "in", ["Time Tracker User", "Time Tracker Manager"]]]
    }
]


# ============================================================
# HOOK 5: jinja_methods & jinja_filters
# ============================================================
# Expose Python functions to Jinja2 templates (Print Formats).
# ============================================================

jinja = {
    "methods": [
        "time_tracker.api.time_api.get_project_summary"
        # Now usable in Print Format Jinja as: {{ get_project_summary("PROJ-001") }}
    ]
}