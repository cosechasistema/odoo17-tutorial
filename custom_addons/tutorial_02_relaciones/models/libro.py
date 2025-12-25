# -*- coding: utf-8 -*-
"""
Extensión del Modelo Libro - Tutorial 02

Demuestra cómo extender un modelo existente para agregar
campos y relaciones sin modificar el módulo original.
"""

from odoo import models, fields, api


class LibroExtension(models.Model):
    """
    Extensión del modelo biblioteca.libro.

    HERENCIA _inherit:
    No crea una nueva tabla, sino que agrega campos a la existente.
    Es la forma estándar de extender modelos en Odoo.
    """

    _inherit = 'biblioteca.libro'

    # =====================================================
    # RELACIÓN MANY2MANY (lado del libro)
    # =====================================================

    # Este campo Many2many es el "otro lado" del campo en biblioteca.categoria
    # Ambos apuntan a la misma tabla intermedia
    categoria_ids = fields.Many2many(
        comodel_name='biblioteca.categoria',
        relation='biblioteca_libro_categoria_rel',
        column1='libro_id',
        column2='categoria_id',
        string='Categorías',
    )

    # =====================================================
    # RELACIÓN ONE2MANY (historial de préstamos)
    # =====================================================

    # Todos los préstamos de este libro
    prestamo_ids = fields.One2many(
        comodel_name='biblioteca.prestamo',
        inverse_name='libro_id',
        string='Historial de Préstamos',
    )

    # =====================================================
    # CAMPOS CALCULADOS
    # =====================================================

    prestamo_count = fields.Integer(
        string='Total Préstamos',
        compute='_compute_prestamo_stats',
    )

    prestamo_activo_id = fields.Many2one(
        comodel_name='biblioteca.prestamo',
        string='Préstamo Actual',
        compute='_compute_prestamo_stats',
    )

    prestado_a = fields.Char(
        string='Prestado A',
        compute='_compute_prestamo_stats',
    )

    @api.depends('prestamo_ids', 'prestamo_ids.estado')
    def _compute_prestamo_stats(self):
        for record in self:
            record.prestamo_count = len(record.prestamo_ids)

            # Buscar préstamo activo
            prestamo_activo = record.prestamo_ids.filtered(
                lambda p: p.estado == 'activo'
            )[:1]  # Tomar el primero si hay varios

            record.prestamo_activo_id = prestamo_activo
            record.prestado_a = prestamo_activo.miembro_id.name if prestamo_activo else ''

    # =====================================================
    # MÉTODOS DE ACCIÓN
    # =====================================================

    def action_ver_prestamos(self):
        """Abre el historial de préstamos del libro."""
        self.ensure_one()
        return {
            'name': f'Préstamos de {self.name}',
            'type': 'ir.actions.act_window',
            'res_model': 'biblioteca.prestamo',
            'view_mode': 'tree,form',
            'domain': [('libro_id', '=', self.id)],
            'context': {'default_libro_id': self.id},
        }

    def action_crear_prestamo(self):
        """Abre formulario para crear un nuevo préstamo."""
        self.ensure_one()
        if not self.disponible:
            from odoo.exceptions import UserError
            raise UserError(f'El libro "{self.name}" no está disponible.')

        return {
            'name': 'Nuevo Préstamo',
            'type': 'ir.actions.act_window',
            'res_model': 'biblioteca.prestamo',
            'view_mode': 'form',
            'target': 'new',  # Abre en ventana modal
            'context': {
                'default_libro_id': self.id,
            },
        }
