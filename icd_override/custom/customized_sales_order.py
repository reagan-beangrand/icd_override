import frappe
from erpnext.selling.doctype.sales_order.sales_order import SalesOrder

class CustomizedSalesOrder(SalesOrder):
    def on_trash(self):        
        pass#unlink_sales_order(self)


def unlink_sales_order(self):
    if not self.m_bl_no:
        return   