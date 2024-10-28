// Copyright (c) 2024, BuFf0k and contributors
// For license information, please see license.txt

frappe.query_reports["Employee Retirement"] = {
	"filters": [
        {
            "fieldname": "months",
            "label": __("Enter the number of months in the future to check for retiring employees"),
            "fieldtype": "Int",
            "reqd": 1,
            "default": 3
        }
    ]
};