// Copyright (c) 2024, BuFf0k and contributors
// For license information, please see license.txt

frappe.query_reports["Fixed Term Contract Expiry"] = {
	"filters": [
        {
            "fieldname": "months",
            "label": __("Contracts expiring in these many months from Today"),
            "fieldtype": "Int",
            "default": 1,
            "reqd": 1
        }
    ]
};