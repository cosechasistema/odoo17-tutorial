# -*- coding: utf-8 -*-
{
    'name': 'Tutorial 07 - Reportes QWeb',
    'version': '17.0.1.0.0',
    'summary': 'Generación de reportes PDF con QWeb',
    'description': """
        Tutorial de Odoo 17 - Módulo 07
        ================================
        Este módulo enseña:
        - Crear reportes PDF con QWeb
        - Templates QWeb (t-foreach, t-if, t-esc, t-field)
        - Estilos CSS en reportes
        - Reportes de un registro vs múltiples registros
        - Wizard para reportes con parámetros
        - Reportes con gráficos y tablas

        Reportes incluidos:
        - Ficha técnica de libro
        - Catálogo de libros disponibles
        - Reporte de préstamos por miembro
        - Carnet de miembro
    """,
    'author': 'Tutorial Odoo',
    'license': 'LGPL-3',
    'category': 'Tutorial',
    'depends': ['tutorial_02_relaciones', 'web'],
    'data': [
        'security/ir.model.access.csv',
        'report/report_paperformat.xml',
        'report/report_libro.xml',
        'report/report_catalogo.xml',
        'report/report_prestamos.xml',
        'report/report_carnet.xml',
        'wizard/wizard_reporte_prestamos_views.xml',
        'views/menu_views.xml',
    ],
    'assets': {
        'web.report_assets_common': [
            'tutorial_07_reportes/static/src/css/report_styles.css',
        ],
    },
    'installable': True,
    'application': False,
}
