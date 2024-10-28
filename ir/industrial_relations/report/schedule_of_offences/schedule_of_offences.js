// Copyright (c) 2024, BuFf0k and contributors
// For license information, please see license.txt

frappe.query_reports["Schedule of Offences"] = {
	"filters": [

	],
    onload: function(report) {
        report.chart_options = {};  // Ensure no chart interferes

        report.data = report.data.map(row => {
            if (row.is_header) {
                row.offence_description = `<span class="header-row">${row.offence_description}</span>`;
                row.name = "";  // Blank out other columns for full-width effect
                row.sanction_on_first_offence = "";
                row.sanction_on_second_offence = "";
                row.sanction_on_third_offence = "";
                row.sanction_on_fourth_offence = "";
            }
            return row;
        });
    },
    refresh: function() {
        setTimeout(() => {
            // Apply custom CSS to header rows based on class
            $('.header-row').closest('tr').css({
                "font-weight": "bold",
                "text-align": "center",
                "background-color": "#f0f0f0"
            }).children('td').attr('colspan', 6);  // Adjust colspan to match columns
        }, 100);
    }
};