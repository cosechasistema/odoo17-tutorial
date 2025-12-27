# -*- coding: utf-8 -*-
{
    'name': 'Tutorial 08 - Importación/Exportación',
    'version': '17.0.1.0.0',
    'summary': 'Importar y exportar datos en Odoo',
    'description': """
        Tutorial de Odoo 17 - Módulo 08
        ================================
        Este módulo enseña:
        - Exportar datos a CSV/Excel desde vistas
        - Importar datos masivos desde CSV
        - Crear wizards de importación personalizados
        - Validación de datos durante importación
        - Manejo de errores y logs de importación
        - Exportación programática de datos

        Funcionalidades:
        - Wizard para importar libros desde CSV
        - Wizard para importar miembros desde CSV
        - Exportar catálogo completo
        - Log de importaciones realizadas
    """,
    'author': 'Tutorial Odoo',
    'license': 'LGPL-3',
    'category': 'Tutorial',
    'depends': ['tutorial_02_relaciones', 'base_import'],
    'data': [
        'security/ir.model.access.csv',
        'data/import_templates.xml',
        'wizard/wizard_importar_libros_views.xml',
        'wizard/wizard_importar_miembros_views.xml',
        'wizard/wizard_exportar_datos_views.xml',
        'views/import_log_views.xml',
        'views/menu_views.xml',
    ],
    'installable': True,
    'application': False,
}
