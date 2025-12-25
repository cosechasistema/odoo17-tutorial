# -*- coding: utf-8 -*-
"""
Modelo de Categoría - Tutorial 02

Demuestra el uso de Many2many: una categoría puede tener muchos libros
y un libro puede pertenecer a muchas categorías.
"""

from odoo import models, fields, api


class Categoria(models.Model):
    """
    Categoría de libros para clasificación.

    RELACIÓN MANY2MANY:
    Una categoría tiene muchos libros, un libro puede estar en muchas categorías.
    Odoo crea automáticamente una tabla intermedia (biblioteca_libro_categoria_rel).
    """

    _name = 'biblioteca.categoria'
    _description = 'Categoría de Libro'
    _order = 'name'

    # =====================================================
    # CAMPOS BÁSICOS
    # =====================================================

    name = fields.Char(
        string='Nombre',
        required=True,
    )

    descripcion = fields.Text(
        string='Descripción',
    )

    color = fields.Integer(
        string='Color',
        help='Color para mostrar en vistas kanban',
    )

    # =====================================================
    # RELACIÓN MANY2MANY
    # =====================================================

    # Many2many define una relación bidireccional muchos a muchos
    libro_ids = fields.Many2many(
        comodel_name='biblioteca.libro',  # Modelo relacionado
        relation='biblioteca_libro_categoria_rel',  # Nombre de tabla intermedia
        column1='categoria_id',  # Columna que referencia a este modelo
        column2='libro_id',  # Columna que referencia al otro modelo
        string='Libros',
    )

    # =====================================================
    # CAMPOS CALCULADOS
    # =====================================================

    # Contar libros en esta categoría
    libro_count = fields.Integer(
        string='Cantidad de Libros',
        compute='_compute_libro_count',
    )

    @api.depends('libro_ids')
    def _compute_libro_count(self):
        for record in self:
            record.libro_count = len(record.libro_ids)

    # =====================================================
    # MÉTODOS DE ACCIÓN
    # =====================================================

    def action_ver_libros(self):
        """
        Abre una ventana mostrando los libros de esta categoría.
        Retorna una acción que Odoo ejecuta.
        """
        self.ensure_one()  # Asegura que es un solo registro
        return {
            'name': f'Libros en {self.name}',
            'type': 'ir.actions.act_window',
            'res_model': 'biblioteca.libro',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', self.libro_ids.ids)],
            'context': {'default_categoria_ids': [(4, self.id)]},
        }
