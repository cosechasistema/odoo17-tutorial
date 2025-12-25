# -*- coding: utf-8 -*-
{
    'name': 'Tutorial 03 - Campos Calculados',
    'version': '17.0.1.0.0',
    'summary': 'Campos computed, onchange y constraints avanzados',
    'description': """
        Tutorial de Odoo 17 - Módulo 03
        ================================
        Este módulo enseña:
        - Campos computed con @api.depends
        - Campos computed con store=True
        - Campos computed editables con inverse
        - @api.onchange para reactividad en formularios
        - @api.constrains para validaciones
        - Campos related avanzados

        Ejemplo: Sistema de inventario con cálculo automático de stock.
    """,
    'author': 'Tutorial Odoo',
    'license': 'LGPL-3',
    'category': 'Tutorial',
    'depends': ['tutorial_02_relaciones'],
    'data': [
        'security/ir.model.access.csv',
        'views/inventario_views.xml',
        'views/menu_views.xml',
    ],
    'installable': True,
    'auto_install': False,
}
