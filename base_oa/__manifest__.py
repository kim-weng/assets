# -*- coding: utf-8 -*-

{
    "name": "Base OA",
    "version": "12.0.1",
    "category" : "",
    "summary": "OA",
    "description": """OA
    """,
    "author": "Kim",
    "website": "http://www.oscg.cn",
    "depends": ["base"],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",

        "views/menu.xml",
        "views/oa_process_type_view.xml",
        "views/oa_process_view.xml",
        "views/oa_task_view.xml",

    ],
    "installable": True,
    "application": False,
}
