# -*- coding: utf-8 -*-
{
    'name': 'Tutorial 01 - CRUD Básico',
    'version': '17.0.1.0.0',
    'summary': 'Módulo de ejemplo: Gestión básica de una biblioteca',
    'description': """
        Tutorial de Odoo 17 - Módulo 01
        ================================
        Este módulo enseña:
        - Crear un modelo básico
        - Definir campos de diferentes tipos
        - Crear vistas (form, tree, search)
        - Crear menús y acciones
        - Configurar permisos básicos

        Ejemplo práctico: Sistema de gestión de libros para una biblioteca.
    """,
    'author': 'Tutorial Odoo',
    'website': '',
    'license': 'LGPL-3',
    'category': 'Tutorial',

    # Dependencias (base siempre es necesario)
    'depends': ['base'],

    # Archivos de datos que se cargan al instalar/actualizar
    # IMPORTANTE: El orden importa! Seguridad antes que vistas
    'data': [
        'security/ir.model.access.csv',
        'views/libro_views.xml',
        'views/menu_views.xml',
        'data/libro_data.xml',
    ],

    # Datos de demostración (solo se cargan si está habilitado demo data)
    'demo': [],

    # Es una aplicación principal (aparece con icono grande en Apps)
    'application': True,

    # Se puede instalar
    'installable': True,

    # No auto-instalar
    'auto_install': False,
}
