app_name = "icd_override"
app_title = "ICD Customization"
app_publisher = "BGCCL"
app_description = "ICD app customozation"
app_email = "dipak.s@bgccerp.com"
app_license = "mit"

# Apps
# ------------------

# required_apps = []

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "icd_override",
# 		"logo": "/assets/icd_override/logo.png",
# 		"title": "ICD Customization",
# 		"route": "/icd_override",
# 		"has_permission": "icd_override.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/icd_override/css/icd_override.css"
# app_include_js = "/assets/icd_override/js/icd_override.js"

# include js, css files in header of web template
# web_include_css = "/assets/icd_override/css/icd_override.css"
# web_include_js = "/assets/icd_override/js/icd_override.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "icd_override/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}
doctype_js = {
    "Container Movement Order" : "public/js/custom_container_movement_order.js",
    #"Sales Order" : "public/js/custom_sales_order.js",
    "Container Inspection" : "public/js/custom_container_inspection.js"
    }
doctype_list_js = {
    #"Sales Order": "public/js/custom_sales_order_list.js",
    #"Purchase Order": "public/js/custom_purchase_order_list.js",    
    }

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "icd_override/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "icd_override.utils.jinja_methods",
# 	"filters": "icd_override.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "icd_override.install.before_install"
# after_install = "icd_override.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "icd_override.uninstall.before_uninstall"
# after_uninstall = "icd_override.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "icd_override.utils.before_app_install"
# after_app_install = "icd_override.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "icd_override.utils.before_app_uninstall"
# after_app_uninstall = "icd_override.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "icd_override.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
    "Manifest": "icd_override.custom.custom_manifest.CustomManifest",
    "Gate Pass": "icd_override.custom.custom_gate_pass.CustomGatePass",
    "Service Order": "icd_override.custom.custom_service_order.CustomServiceOrder",
    "Container Inspection": "icd_override.custom.custom_container_inspection.CustomContainerInspection",
    "Container": "icd_override.custom.custom_container.CustomContainer",
    #"Sales Order": "icd_override.custom.customized_sales_order.CustomizedSalesOrder",
    #"Sales Invoice": "icd_override.custom.custom_sales_invoice.CustomSalesInvoice"
 }

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
# 	}
 "Sales Order": {        
        #"on_submit": "icd_override.custom.custom_sales_order.on_submit",
        #"on_trash": "icd_override.custom.custom_sales_order.on_trash",      
    },
 }

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"icd_override.tasks.all"
# 	],
# 	"daily": [
# 		"icd_override.tasks.daily"
# 	],
# 	"hourly": [
# 		"icd_override.tasks.hourly"
# 	],
# 	"weekly": [
# 		"icd_override.tasks.weekly"
# 	],
# 	"monthly": [
# 		"icd_override.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "icd_override.install.before_tests"

# Overriding Methods
# ------------------------------
#
override_whitelisted_methods = {
    #"icd_tz.icd_tz.doctype.container_movement_order.container_movement_order.get_manifest_details":"icd_override.custom.custom_whitelisted.get_manifest_details"
 	#"frappe.desk.doctype.event.event.get_events": "icd_override.event.get_events"   
}
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "icd_override.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["icd_override.utils.before_request"]
# after_request = ["icd_override.utils.after_request"]

# Job Events
# ----------
# before_job = ["icd_override.utils.before_job"]
# after_job = ["icd_override.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"icd_override.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

# Translation
# ------------
# List of apps whose translatable strings should be excluded from this app's translations.
# ignore_translatable_strings_from = []

fixtures =[
    #{"dt": "Custom Field", "filters": [["module", "=", "ICD Customization"]]},
    #{"dt": "Property Setter", "filters": [["module", "=", "ICD Customization"]]}, 
    #{"doctype": "Custom DocPerm", "filters": [["parent", "in", ["Container Movement Order"]]]}  
    #{"doctype": "DocPerm", "filters": {"parent": "Container Movement Order"}}
    #{"doctype":"Global Search Settings"},
    #{"doctype":"IMDG Classification"},
    #{"doctype":"Nomination Type"},
    #{"doctype":"IMDG Code"},
    #{"doctype":"Purchase Order BL Detail"},
    #{"dt": "Workspace", "filters": [["name", "=", "ICD"]]},
]
