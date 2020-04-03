# -*- coding: utf-8 -*-

{
    "name": "Base Assets",
    "version": "12.0",
    "category" : "account",
    "summary": "account",
    "description": """固定资产
    """,
    "author": "Kim",
    "website": "http://www.oscg.cn",
    "depends": ["base", "account", "hr", "stock", "purchase", "purchase_stock", "base_oa"],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",

        "data/ir_sequence_data.xml",

        "views/res_users_view.xml",
        "views/res_company_view.xml",
        "views/asset_category_view.xml",
        "views/res_asset_view.xml",
        "views/menu.xml",
        "views/product_template_view.xml",
        "views/purchase_order_view.xml",
        "views/stock_picking_view.xml",
        "views/asset_picking_order_view.xml",
        "views/asset_move_line_view.xml",
        "views/asset_inventory_order_view.xml",

        "report/asset_report_view.xml",
    ],
    "installable": True,
    "application": False,
}