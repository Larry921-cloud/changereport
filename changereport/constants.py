"""Shared constants: column mappings, color palette, enums."""

# Canonical column names after normalization
COLUMNS = [
    "id", "assignee", "customer_name", "subject",
    "reason_benefit", "type_of_change", "category",
    "start_date", "start_time", "end_date", "end_time",
    "system_application", "impact_description",
    "regions_affected", "pre_checks", "mop",
    "rollback_plan", "post_change_testing",
    "standard_change_list",
]

# Maps raw header text (lowered/stripped) to canonical column name
HEADER_ALIASES = {
    "id": "id",
    "assignee": "assignee",
    "customer name": "customer_name",
    "subject": "subject",
    "reason / benefit of change": "reason_benefit",
    "type of change": "type_of_change",
    "cm: category": "category",
    "start date": "start_date",
    "start time (hh:mm)": "start_time",
    "end date": "end_date",
    "end time (hh:mm)": "end_time",
    "name of system / application worked or config applied on?": "system_application",
    "impact description": "impact_description",
    "regions affected ( list all separated by a comma)": "regions_affected",
    "regions affected (list all separated by a comma)": "regions_affected",
    "pre-checks / activities": "pre_checks",
    "mop - ( attach if necessary ) ps!- max 2mb allowed via this form.": "mop",
    "mop - (attach if necessary) ps!- max 2mb allowed via this form.": "mop",
    "rollback plan ( attach if necessary )": "rollback_plan",
    "rollback plan (attach if necessary)": "rollback_plan",
    "post change testing ( attach if necessary )": "post_change_testing",
    "post change testing (attach if necessary)": "post_change_testing",
    "standard change list (only for std changes)": "standard_change_list",
}

CHANGE_TYPES = ["Standard change", "CAB change", "Work Order"]

CATEGORIES = [
    "Radio Network", "IP Core", "Packet Core",
    "Transmission Network", "Systems and IT",
    "Software Engineering", "Cyber Security",
    "Billing and Revenue",
]

IMPACT_LEVELS = [
    "No Impact", "Site Down", "Users Disconnected",
    "Degradation in Service",
    "Application Unavailable / Reset / Restart",
]

# Colorblind-friendly chart palette
CHART_COLORS = [
    "#2196F3", "#4CAF50", "#FF9800", "#F44336",
    "#9C27B0", "#00BCD4", "#795548", "#607D8B",
    "#E91E63", "#3F51B5", "#009688", "#FFC107",
]

# PDF styling
PDF_PRIMARY_COLOR = "#1a237e"
PDF_HEADER_BG = "#1a237e"
PDF_HEADER_TEXT = "#ffffff"
PDF_ALT_ROW = "#f5f5f5"
PDF_GRID_COLOR = "#e0e0e0"
