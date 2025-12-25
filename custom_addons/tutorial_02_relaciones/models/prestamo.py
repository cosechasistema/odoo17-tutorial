# -*- coding: utf-8 -*-
"""
Modelo de Préstamo - Tutorial 02

Modelo central que demuestra múltiples Many2one y lógica de negocio.
"""

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
from dateutil.relativedelta import relativedelta


class Prestamo(models.Model):
    """
    Préstamo de libro.

    RELACIONES MANY2ONE:
    - libro_id: Qué libro se presta
    - miembro_id: A quién se presta

    Este modelo muestra cómo trabajar con múltiples relaciones
    y cómo acceder a datos de registros relacionados.
    """

    _name = 'biblioteca.prestamo'
    _description = 'Préstamo de Libro'
    _order = 'fecha_prestamo desc'

    # =====================================================
    # RELACIONES MANY2ONE
    # =====================================================

    libro_id = fields.Many2one(
        comodel_name='biblioteca.libro',
        string='Libro',
        required=True,
        ondelete='restrict',
        # Dominio: solo libros disponibles
        # (Se puede hacer dinámico con una función)
        domain="[('disponible', '=', True)]",
    )

    miembro_id = fields.Many2one(
        comodel_name='biblioteca.miembro',
        string='Miembro',
        required=True,
        ondelete='restrict',
        domain="[('activo', '=', True)]",
    )

    # =====================================================
    # CAMPOS DE FECHAS
    # =====================================================

    fecha_prestamo = fields.Date(
        string='Fecha de Préstamo',
        default=fields.Date.today,
        required=True,
    )

    fecha_devolucion_esperada = fields.Date(
        string='Fecha Devolución Esperada',
        compute='_compute_fecha_devolucion',
        store=True,
    )

    fecha_devolucion_real = fields.Date(
        string='Fecha Devolución Real',
    )

    # =====================================================
    # ESTADO Y CAMPOS CALCULADOS
    # =====================================================

    estado = fields.Selection([
        ('activo', 'Activo'),
        ('devuelto', 'Devuelto'),
        ('vencido', 'Vencido'),
    ], string='Estado', default='activo', required=True)

    dias_prestamo = fields.Integer(
        string='Días de Préstamo',
        default=14,
        help='Número de días que se presta el libro',
    )

    dias_retraso = fields.Integer(
        string='Días de Retraso',
        compute='_compute_dias_retraso',
    )

    # =====================================================
    # CAMPOS RELATED (info del libro y miembro)
    # =====================================================

    libro_titulo = fields.Char(
        string='Título',
        related='libro_id.name',
    )

    libro_autor = fields.Char(
        string='Autor',
        related='libro_id.autor',
    )

    miembro_nombre = fields.Char(
        string='Nombre del Miembro',
        related='miembro_id.name',
    )

    miembro_email = fields.Char(
        string='Email',
        related='miembro_id.email',
    )

    # =====================================================
    # NOTAS
    # =====================================================

    notas = fields.Text(string='Notas')

    # =====================================================
    # CAMPOS CALCULADOS
    # =====================================================

    @api.depends('fecha_prestamo', 'dias_prestamo')
    def _compute_fecha_devolucion(self):
        for record in self:
            if record.fecha_prestamo:
                record.fecha_devolucion_esperada = (
                    record.fecha_prestamo + relativedelta(days=record.dias_prestamo)
                )
            else:
                record.fecha_devolucion_esperada = False

    @api.depends('fecha_devolucion_esperada', 'fecha_devolucion_real', 'estado')
    def _compute_dias_retraso(self):
        hoy = fields.Date.today()
        for record in self:
            if record.estado == 'devuelto' and record.fecha_devolucion_real:
                # Si ya devolvió, calcular retraso real
                if record.fecha_devolucion_real > record.fecha_devolucion_esperada:
                    delta = record.fecha_devolucion_real - record.fecha_devolucion_esperada
                    record.dias_retraso = delta.days
                else:
                    record.dias_retraso = 0
            elif record.estado == 'activo' and record.fecha_devolucion_esperada:
                # Si aún tiene el libro, calcular retraso actual
                if hoy > record.fecha_devolucion_esperada:
                    delta = hoy - record.fecha_devolucion_esperada
                    record.dias_retraso = delta.days
                else:
                    record.dias_retraso = 0
            else:
                record.dias_retraso = 0

    # =====================================================
    # ONCHANGE
    # =====================================================

    @api.onchange('libro_id')
    def _onchange_libro(self):
        """
        Cuando cambia el libro, mostrar información adicional.
        onchange se ejecuta en el cliente antes de guardar.
        """
        if self.libro_id:
            # Podrías agregar lógica aquí, como mostrar un warning
            if self.libro_id.estado == 'mantenimiento':
                return {
                    'warning': {
                        'title': 'Libro en mantenimiento',
                        'message': 'Este libro está en mantenimiento y no debería prestarse.',
                    }
                }

    @api.onchange('miembro_id')
    def _onchange_miembro(self):
        """Verificar estado del miembro."""
        if self.miembro_id:
            if self.miembro_id.fecha_vencimiento < fields.Date.today():
                return {
                    'warning': {
                        'title': 'Membresía vencida',
                        'message': f'La membresía de {self.miembro_id.name} está vencida.',
                    }
                }

    # =====================================================
    # MÉTODOS CRUD
    # =====================================================

    @api.model_create_multi
    def create(self, vals_list):
        """Al crear préstamo, marcar libro como prestado."""
        prestamos = super().create(vals_list)
        for prestamo in prestamos:
            prestamo.libro_id.write({
                'estado': 'prestado',
                'disponible': False,
            })
        return prestamos

    def unlink(self):
        """No permitir eliminar préstamos activos."""
        for record in self:
            if record.estado == 'activo':
                raise UserError(
                    'No se puede eliminar un préstamo activo. '
                    'Primero debe devolverse el libro.'
                )
        return super().unlink()

    # =====================================================
    # MÉTODOS DE ACCIÓN
    # =====================================================

    def action_devolver(self):
        """Marca el préstamo como devuelto."""
        for record in self:
            if record.estado != 'activo':
                raise UserError('Este préstamo ya fue devuelto.')

            record.write({
                'estado': 'devuelto',
                'fecha_devolucion_real': fields.Date.today(),
            })

            # Marcar libro como disponible
            record.libro_id.write({
                'estado': 'disponible',
                'disponible': True,
            })

    def action_renovar(self):
        """Renueva el préstamo por más días."""
        for record in self:
            if record.estado != 'activo':
                raise UserError('Solo se pueden renovar préstamos activos.')

            if record.dias_retraso > 0:
                raise UserError(
                    'No se puede renovar un préstamo con retraso. '
                    'Por favor devuelva el libro primero.'
                )

            # Extender la fecha de devolución
            record.fecha_prestamo = fields.Date.today()

    # =====================================================
    # RESTRICCIONES
    # =====================================================

    @api.constrains('libro_id', 'estado')
    def _check_libro_disponible(self):
        """Verificar que el libro esté disponible al crear préstamo."""
        for record in self:
            if record.estado == 'activo':
                # Buscar otros préstamos activos del mismo libro
                otros = self.search([
                    ('libro_id', '=', record.libro_id.id),
                    ('estado', '=', 'activo'),
                    ('id', '!=', record.id),
                ])
                if otros:
                    raise ValidationError(
                        f'El libro "{record.libro_id.name}" ya está prestado '
                        f'a {otros[0].miembro_id.name}.'
                    )

    # =====================================================
    # CRON JOB (se ejecuta automáticamente)
    # =====================================================

    @api.model
    def _cron_actualizar_vencidos(self):
        """
        Método para ejecutar periódicamente.
        Marca como vencidos los préstamos que pasaron su fecha.
        """
        hoy = fields.Date.today()
        prestamos_vencidos = self.search([
            ('estado', '=', 'activo'),
            ('fecha_devolucion_esperada', '<', hoy),
        ])
        prestamos_vencidos.write({'estado': 'vencido'})
        return True
