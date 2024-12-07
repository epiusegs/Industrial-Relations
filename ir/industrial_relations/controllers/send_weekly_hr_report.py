# Copyright (c) 2024, buff0k and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import get_url
from datetime import timedelta, date

def send_weekly_hr_report():
    # Define reports to send
    reports = [
        {
            "report_name": "Contracts Expiring Soon",
            "role": "IR Manager"
        },
        {
            "report_name": "Employees Approaching Retirement",
            "role": "IR Manager"
        }
    ]

    for report in reports:
        # Get the recipients for the role
        recipients = frappe.get_all(
            "Has Role",
            filters={"role": report["role"]},
            fields=["parent"]
        )
        valid_recipients = [
            r["parent"] for r in recipients if frappe.db.exists("User", r["parent"])
        ]

        # Skip if no recipients
        if not valid_recipients:
            frappe.log_error(f"No recipients found for role {report['role']}", "Weekly HR Report")
            continue

        # Get the report data
        report_doc = frappe.get_doc("Report", report["report_name"])
        if not report_doc:
            frappe.log_error(f"Report {report['report_name']} not found", "Weekly HR Report")
            continue

        # Generate the report data
        try:
            result = report_doc.get_data(filters={}, as_dict=True)
            if not result:
                frappe.log_error(f"No data in report {report['report_name']}", "Weekly HR Report")
                continue
        except Exception as e:
            frappe.log_error(f"Error generating data for {report['report_name']}: {e}", "Weekly HR Report")
            continue

        # Construct email message
        message = f"""
            <p>Dear {report['role']}s,</p>
            <p>Please find attached the weekly HR report: <b>{report['report_name']}</b>.</p>
        """

        # Send the email
        frappe.sendmail(
            recipients=valid_recipients,
            subject=f"Weekly HR Report: {report['report_name']}",
            message=message,
            attachments=[{
                "fname": f"{report['report_name']}.csv",
                "fcontent": frappe.utils.csvutils.to_csv(result)
            }]
        )
        frappe.log(f"Weekly HR report '{report['report_name']}' sent successfully.")
