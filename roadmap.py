# ============================================================
# 🗺️  YOUR LEARNING ROADMAP — Intermediate → Advanced
# ============================================================
# Follow these steps IN ORDER. Each step builds on the last.
# Don't skip steps!
# ============================================================

ROADMAP = """
╔══════════════════════════════════════════════════════════════╗
║          FRAPPE REST API MASTERY — STEP BY STEP              ║
╚══════════════════════════════════════════════════════════════╝

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
WEEK 1: Install the App & Call Your First API
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
□ Step 1: Install this app on your ERPNext bench
          bench new-app time_tracker
          bench --site yoursite install-app time_tracker

□ Step 2: Call hello_frappe in your browser
          Open: yoursite/api/method/time_tracker.api.time_api.hello_frappe
          You should see JSON response with your username

□ Step 3: Set up Postman and hit the same endpoint with API key auth

□ Step 4: Create 2 Test Projects in ERPNext manually (UI)
          Use: "PROJ-001" and "PROJ-002" as names

□ Step 5: Call log_time via Postman to create a time entry
          Verify: Check Time Log list in ERPNext — your entry should appear


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
WEEK 2: JavaScript Integration
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
□ Step 6: Create a Client Script on Project form
          ERPNext → Customize → Client Script → New
          Trigger: frappe.call() to log_time on button click

□ Step 7: Display get_project_summary() result on the Project form
          Show total hours in a dialog using frappe.msgprint()

□ Step 8: Use frappe.xcall() with async/await (modern pattern)


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
WEEK 3: Hooks & Automation
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
□ Step 9:  Add validate_time_log() to hooks.py (before_insert)
           Test: try creating a Time Log > 24 hours — should be blocked

□ Step 10: Add update_project_billing() to after_insert
           Auto-calculate billing amount when log is saved

□ Step 11: Set up a daily scheduler event
           bench execute time_tracker.api.billing_api.generate_daily_billing_summary
           (This runs the job manually to test it)


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
WEEK 4: Advanced Patterns
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
□ Step 12: Build bulk_log_time() integration
           Pass a JSON array from Postman, verify all records created

□ Step 13: Test generate_invoice() with role restriction
           Create a test user WITHOUT Time Tracker Manager role
           Verify they get 403 error

□ Step 14: Test the CSV download endpoint
           Call download_timesheet_csv() from Postman
           Verify you get a .csv file download

□ Step 15: Test frappe.enqueue() background job
           Call export_annual_report()
           Check: ERPNext → Scheduled Job Log


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
WEEK 5: Production-Ready Code
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
□ Step 16: Add frappe.log_error() to every method
           Deliberately cause an error, check Error Log in ERPNext

□ Step 17: Write Unit Tests
           bench --site yoursite run-tests --app time_tracker

□ Step 18: Document your API (update this README)
           Other developers should be able to use your API from docs alone

□ Step 19: Build a React/Vue frontend that uses only your REST API
           No ERPNext UI — pure external frontend calling Frappe

□ Step 20: Deploy to production bench
           bench --site yoursite migrate
           supervisor restart frappe


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DEBUGGING COMMANDS (Use These Daily)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
bench --site yoursite console                # Python shell with Frappe loaded
bench --site yoursite mariadb               # Direct database access
bench --site yoursite migrate               # Apply schema changes
bench logs                                  # Watch live logs
bench --site yoursite clear-cache           # Clear all caches
bench build                                 # Rebuild JS/CSS assets

# Run a function directly (great for testing schedulers):
bench --site yoursite execute time_tracker.api.time_api.hello_frappe

# Check error logs:
# ERPNext → Setup → Error Log


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
YOU ARE ADVANCED WHEN YOU CAN:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Write a whitelisted method from scratch with proper validation
✅ Control who can call it using roles and permissions
✅ Call it from JavaScript using frappe.call() and frappe.xcall()
✅ Call it from external apps using API key authentication
✅ Use hooks.py to auto-trigger methods on doc events
✅ Run heavy tasks in background with frappe.enqueue()
✅ Handle and log errors properly
✅ Write and run unit tests for your methods
✅ Return file downloads from API methods
"""

print(ROADMAP)