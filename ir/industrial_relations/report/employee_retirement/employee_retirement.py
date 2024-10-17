# Copyright (c) 2024, BuFf0k and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import add_months, today, date_diff, add_years

def execute(filters=None):
    if not filters:
        filters = {}
    
    # Get current date and calculate future date based on X months filter
    current_date = today()
    future_date = add_months(current_date, filters.get("months") or 0)

    # Query to get employees who will retire within the next X months
    data = frappe.db.sql("""
        SELECT
            name AS document_name,
            company,
            employee,
            employee_name,
            designation,
            date_of_joining,
            branch,
            project,
            start_date,
            DATE_SUB(DATE_ADD(date_of_birth, INTERVAL retirement_age YEAR), INTERVAL 1 DAY) AS end_date
        FROM
            `tabContract of Employment`
        WHERE
            has_retirement = 1
            AND DATE_SUB(DATE_ADD(date_of_birth, INTERVAL retirement_age YEAR), INTERVAL 1 DAY) BETWEEN %s AND %s
    """, (current_date, future_date), as_dict=True)

    columns = [
        {"label": "Document Name", "fieldname": "document_name", "fieldtype": "Link", "options": "Contract of Employment", "width": 200},
        {"label": "Company", "fieldname": "company", "fieldtype": "Link", "options": "Company", "width": 150},
        {"label": "Employee", "fieldname": "employee", "fieldtype": "Link", "options": "Employee", "width": 150},
        {"label": "Employee Name", "fieldname": "employee_name", "fieldtype": "Data", "width": 150},
        {"label": "Designation", "fieldname": "designation", "fieldtype": "Data", "width": 150},
        {"label": "Date of Joining", "fieldname": "date_of_joining", "fieldtype": "Date", "width": 100},
        {"label": "Branch", "fieldname": "branch", "fieldtype": "Link", "options": "Branch", "width": 150},
        {"label": "Project", "fieldname": "project", "fieldtype": "Data", "width": 150},
        {"label": "Start Date", "fieldname": "start_date", "fieldtype": "Date", "width": 100},
        {"label": "End Date", "fieldname": "end_date", "fieldtype": "Date", "width": 100},
    ]

    return columns, data
