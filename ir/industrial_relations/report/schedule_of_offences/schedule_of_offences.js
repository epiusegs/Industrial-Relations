// Copyright (c) 2024, BuFf0k and contributors
// For license information, please see license.txt

frappe.query_reports["Schedule of Offences"] = {
    filters: [],

    onload: function(report) {
        // Set report settings to hide the index column
        report.datatable_options = {
            showIndexColumn: false
        };

        // Apply custom styling for header rows
        frappe.utils.add_custom_style(`
            @media print {
                .header-row {
                    font-weight: bold;
                    text-align: center;
                    background-color: #f0f0f0;
                }
            }
        `);
    },

    refresh: function() {
        setTimeout(() => {
            // Style header rows for web view
            $('.header-row').closest('tr').css({
                "font-weight": "bold",
                "text-align": "center",
                "background-color": "#f0f0f0"
            }).children('td').attr('colspan', 6);  // Adjust colspan to match columns
        }, 100);
    }
};
