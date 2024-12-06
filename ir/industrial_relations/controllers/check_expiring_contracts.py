# Copyright (c) 2024, BuFf0k and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import today, add_days, getdate, get_url
from datetime import datetime, timedelta

def check_expiring_contracts():
    # Calculate the threshold date (4 weeks from today)
    threshold_date = getdate(today()) + timedelta(weeks=4)  # Use date object directly

    # Fetch contracts expiring by end_date (only those with a valid end_date)
    expiring_contracts_by_end_date = frappe.get_all(
        "Contract of Employment", 
        filters={
            "end_date": ["<=", threshold_date],  # Compare with date object
            "end_date": ["!=", None]  # Ensure end_date is not null
        },
        fields=["name", "employee", "employee_name", "end_date", "creation"]
    )

    # Filter out contracts that are superseded by a newer contract
    filtered_expiring_contracts = []
    for contract in expiring_contracts_by_end_date:
        # Get the latest contract for the same employee
        latest_contract = frappe.get_all(
            "Contract of Employment",
            filters={
                "employee": contract["employee"],
                "creation": [">", contract["creation"]]  # Find newer contracts based on creation date
            },
            fields=["name", "end_date"],
            order_by="creation desc",  # Order by creation to get the latest one
            limit_page_length=1
        )

        # If a newer contract exists, skip this one
        if latest_contract:
            continue
        
        # Add the contract to the list for notifications
        filtered_expiring_contracts.append(contract)

    # Get employees approaching retirement age (end_date can be None here)
    employees_approaching_retirement = frappe.db.sql("""
        SELECT co.name, co.employee, co.employee_name, co.end_date, co.retirement_age, e.date_of_birth
        FROM `tabContract of Employment` co
        JOIN `tabEmployee` e ON co.employee = e.name
        WHERE
            TIMESTAMPDIFF(YEAR, e.date_of_birth, %(threshold_date)s) >= co.retirement_age
    """, {
        'threshold_date': threshold_date
    }, as_dict=True)

    # Combine both lists and send notifications
    contracts_to_notify = filtered_expiring_contracts + employees_approaching_retirement

    for contract in contracts_to_notify:
        notify_expiry(contract)

def notify_expiry(contract):
    # Fetch all users with the "IR Manager" role
    ir_managers = frappe.get_all(
        'Has Role',
        filters={'role': 'IR Manager'},
        fields=['parent']
    )

    # Filter out invalid or non-user 'parent' fields (e.g., role groups)
    valid_ir_managers = [
        manager for manager in ir_managers
        if frappe.db.exists('User', manager['parent'])  # Check if 'parent' is a valid User
    ]

    for manager in valid_ir_managers:
        user = frappe.get_doc('User', manager['parent'])
        if user.enabled and user.email:
            first_name = user.first_name or "Manager"
            email = user.email

            # Generate the URL for the Contract of Employment document
            contract_url = get_url(f"/app/contract-of-employment/{contract['name']}")

            # Prepare subject and message for the email
            subject = f"Contract Notification: {contract.get('employee_name') or contract.get('employee')}"
            message = f"""
            <p>Dear {first_name},</p>
            <p>The following employee's contract requires your attention:</p>
            <ul>
                <li><b>Employee:</b> <a href="{contract_url}">{contract['employee']}</a></li>
                <li><b>Employee Name:</b> {contract.get('employee_name', 'N/A')}</li>
            """

            # Include expiry date if it exists, or note retirement notification
            if contract.get('end_date'):
                message += f"""
                <li><b>Contract Expiry Date:</b> {contract['end_date'].strftime('%Y-%m-%d')}</li>
                """
            else:
                message += f"""
                <li><b>Notification Type:</b> Approaching Retirement</li>
                """

            message += "</ul><p>Please take the necessary action.</p>"

            # Send email to the IR Manager
            frappe.sendmail(
                recipients=[email],
                subject=subject,
                message=message
            )
