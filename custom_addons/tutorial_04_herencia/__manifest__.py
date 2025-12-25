# -*- coding: utf-8 -*-
{
    'name': 'Tutorial 04 - Herencia',
    'version': '17.0.1.0.0',
    'summary': 'Tipos de herencia en Odoo: _inherit, _inherits, vistas',
    'description': """
        Tutorial de Odoo 17 - Módulo 04
        ================================
        Este módulo enseña:
        - _inherit: Extender modelo existente (agregar campos)
        - _inherits: Herencia delegada (composición)
        - Herencia de vistas XML
        - Sobrescribir métodos
        - Llamar a super()

        Ejemplo: Extender res.partner para agregar campos de autor.
    """,
    'author': 'Tutorial Odoo',
    'license': 'LGPL-3',
    'category': 'Tutorial',
    'depends': ['tutorial_01_basico', 'contacts'],
    'data': [
        'security/ir.model.access.csv',
        'views/partner_views.xml',
        'data/partner_data.xml',
    ],
    'installable': True,
}
