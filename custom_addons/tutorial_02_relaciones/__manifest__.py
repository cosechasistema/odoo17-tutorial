# -*- coding: utf-8 -*-
{
    'name': 'Tutorial 02 - Relaciones',
    'version': '17.0.1.0.0',
    'summary': 'Módulo de ejemplo: Relaciones entre modelos (Many2one, One2many, Many2many)',
    'description': """
        Tutorial de Odoo 17 - Módulo 02
        ================================
        Este módulo enseña:
        - Many2one: Relación muchos a uno
        - One2many: Relación uno a muchos (inversa de Many2one)
        - Many2many: Relación muchos a muchos
        - Cómo navegar entre registros relacionados
        - Dominios en campos relacionales

        Ejemplo práctico: Sistema de préstamos de biblioteca con:
        - Miembros (Many2one al modelo res.partner)
        - Préstamos (Many2one a libro y miembro)
        - Libros con historial de préstamos (One2many)
        - Categorías de libros (Many2many)
    """,
    'author': 'Tutorial Odoo',
    'license': 'LGPL-3',
    'category': 'Tutorial',

    # Este módulo depende del módulo anterior
    'depends': ['tutorial_01_basico'],

    'data': [
        'security/ir.model.access.csv',
        'views/categoria_views.xml',
        'views/miembro_views.xml',
        'views/prestamo_views.xml',
        'views/libro_views_extend.xml',
        'views/menu_views.xml',
        'data/categoria_data.xml',
    ],

    'application': False,  # Es una extensión, no una app principal
    'installable': True,
    'auto_install': False,
}
