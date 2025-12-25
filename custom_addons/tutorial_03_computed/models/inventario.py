# -*- coding: utf-8 -*-
"""
Modelo de Inventario - Tutorial 03

Demuestra campos calculados, onchange y constraints avanzados.
"""

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class InventarioLibro(models.Model):
    """
    Control de inventario de libros.

    CAMPOS COMPUTED:
    - stock_total: suma de entradas
    - stock_disponible: total - prestados
    - valor_inventario: precio * cantidad
    """

    _name = 'biblioteca.inventario'
    _description = 'Inventario de Biblioteca'
    _order = 'libro_id'

    # =====================================================
    # RELACIÓN
    # =====================================================

    libro_id = fields.Many2one(
        'biblioteca.libro',
        string='Libro',
        required=True,
        ondelete='cascade',
    )

    # =====================================================
    # CAMPOS DE STOCK
    # =====================================================

    # Stock inicial al agregar libros al inventario
    stock_inicial = fields.Integer(
        string='Stock Inicial',
        default=0,
    )

    # Entradas de libros (compras, donaciones)
    entradas = fields.Integer(
        string='Entradas',
        default=0,
        help='Libros añadidos por compra o donación',
    )

    # Salidas permanentes (pérdidas, bajas)
    salidas = fields.Integer(
        string='Salidas',
        default=0,
        help='Libros dados de baja o perdidos',
    )

    # =====================================================
    # CAMPOS COMPUTED (No almacenados)
    # =====================================================

    # Campo computed SIN store - se calcula en tiempo real
    stock_total = fields.Integer(
        string='Stock Total',
        compute='_compute_stock',
        help='Stock inicial + entradas - salidas',
    )

    # Cantidad de libros actualmente prestados
    prestados = fields.Integer(
        string='Prestados',
        compute='_compute_prestados',
    )

    # Stock disponible para préstamo
    stock_disponible = fields.Integer(
        string='Disponible',
        compute='_compute_stock',
    )

    @api.depends('stock_inicial', 'entradas', 'salidas')
    def _compute_stock(self):
        """
        Calcula stock total y disponible.

        @api.depends especifica qué campos "disparan" el recálculo.
        Si cualquiera de estos campos cambia, se recalcula automáticamente.
        """
        for record in self:
            record.stock_total = record.stock_inicial + record.entradas - record.salidas
            # Restamos los prestados del stock disponible
            record.stock_disponible = record.stock_total - record.prestados

    @api.depends('libro_id', 'libro_id.prestamo_ids', 'libro_id.prestamo_ids.estado')
    def _compute_prestados(self):
        """
        Cuenta cuántos libros están prestados actualmente.

        NOTA: Dependemos de campos en modelos relacionados.
        El path libro_id.prestamo_ids.estado significa:
        "recalcular cuando cambie el estado de cualquier préstamo del libro"
        """
        for record in self:
            if record.libro_id:
                record.prestados = len(record.libro_id.prestamo_ids.filtered(
                    lambda p: p.estado == 'activo'
                ))
            else:
                record.prestados = 0

    # =====================================================
    # CAMPO COMPUTED ALMACENADO (store=True)
    # =====================================================

    # El valor del inventario se guarda en BD para reportes/búsquedas
    valor_inventario = fields.Float(
        string='Valor del Inventario',
        compute='_compute_valor',
        store=True,  # SE GUARDA EN BD
        help='Valor total = precio del libro x cantidad disponible',
    )

    @api.depends('stock_disponible', 'libro_id.precio')
    def _compute_valor(self):
        """
        Calcula el valor monetario del inventario.

        store=True: El valor se guarda en la base de datos.
        Ventajas: Búsquedas rápidas, reportes, ordenamiento.
        Desventaja: Ocupa espacio, se debe recalcular explícitamente.
        """
        for record in self:
            precio = record.libro_id.precio or 0.0
            record.valor_inventario = record.stock_disponible * precio

    # =====================================================
    # CAMPO COMPUTED EDITABLE (con inverse)
    # =====================================================

    # Porcentaje de ocupación - editable por el usuario
    porcentaje_prestado = fields.Float(
        string='% Prestado',
        compute='_compute_porcentaje',
        inverse='_inverse_porcentaje',
        digits=(5, 2),
        help='Porcentaje de libros prestados. Editable para ajustar.',
    )

    @api.depends('stock_total', 'prestados')
    def _compute_porcentaje(self):
        for record in self:
            if record.stock_total > 0:
                record.porcentaje_prestado = (record.prestados / record.stock_total) * 100
            else:
                record.porcentaje_prestado = 0.0

    def _inverse_porcentaje(self):
        """
        inverse permite que el campo computed sea editable.
        Cuando el usuario modifica el porcentaje, calculamos
        cuántos libros deberían estar prestados.

        NOTA: Esto es solo demostrativo - en la práctica el
        número de préstamos viene de los registros de préstamo.
        """
        for record in self:
            if record.stock_total > 0:
                # Aquí podrías ajustar el stock si tuviera sentido
                pass

    # =====================================================
    # NIVEL DE STOCK - Ejemplo de Selection computed
    # =====================================================

    nivel_stock = fields.Selection([
        ('critico', 'Crítico (< 2)'),
        ('bajo', 'Bajo (2-5)'),
        ('normal', 'Normal (5-10)'),
        ('alto', 'Alto (> 10)'),
    ], string='Nivel de Stock', compute='_compute_nivel')

    @api.depends('stock_disponible')
    def _compute_nivel(self):
        for record in self:
            if record.stock_disponible < 2:
                record.nivel_stock = 'critico'
            elif record.stock_disponible < 5:
                record.nivel_stock = 'bajo'
            elif record.stock_disponible <= 10:
                record.nivel_stock = 'normal'
            else:
                record.nivel_stock = 'alto'

    # =====================================================
    # ONCHANGE - Reactividad en formularios
    # =====================================================

    @api.onchange('stock_inicial')
    def _onchange_stock_inicial(self):
        """
        @api.onchange se ejecuta en el CLIENTE (navegador)
        cuando el usuario cambia el campo.

        DIFERENCIAS con @api.depends:
        - onchange: solo en UI, antes de guardar
        - depends: cuando cambia en BD, después de guardar

        Usos comunes:
        - Mostrar advertencias
        - Pre-llenar otros campos
        - Validaciones en tiempo real
        """
        if self.stock_inicial < 0:
            return {
                'warning': {
                    'title': 'Stock negativo',
                    'message': 'El stock inicial no puede ser negativo.',
                }
            }

        # Ejemplo: si el stock inicial es 0, sugerir cantidad
        if self.stock_inicial == 0 and self.libro_id:
            return {
                'warning': {
                    'title': 'Sin stock',
                    'message': f'¿Desea agregar copias del libro "{self.libro_id.name}"?',
                }
            }

    @api.onchange('libro_id')
    def _onchange_libro(self):
        """Auto-llenar campos cuando se selecciona un libro."""
        if self.libro_id:
            # Buscar si ya existe inventario para este libro
            existente = self.search([
                ('libro_id', '=', self.libro_id.id),
                ('id', '!=', self._origin.id),  # Excluir el registro actual
            ], limit=1)
            if existente:
                return {
                    'warning': {
                        'title': 'Inventario existente',
                        'message': f'Ya existe un registro de inventario para "{self.libro_id.name}".',
                    }
                }

    # =====================================================
    # CONSTRAINTS - Validaciones al guardar
    # =====================================================

    @api.constrains('stock_inicial', 'entradas', 'salidas')
    def _check_stock_positivo(self):
        """
        @api.constrains se ejecuta al GUARDAR en base de datos.
        Si la validación falla, se revierte la transacción.
        """
        for record in self:
            if record.stock_inicial < 0:
                raise ValidationError('El stock inicial no puede ser negativo.')
            if record.entradas < 0:
                raise ValidationError('Las entradas no pueden ser negativas.')
            if record.salidas < 0:
                raise ValidationError('Las salidas no pueden ser negativas.')

    @api.constrains('salidas', 'stock_inicial', 'entradas')
    def _check_salidas_no_exceden(self):
        """Las salidas no pueden exceder el stock."""
        for record in self:
            if record.salidas > (record.stock_inicial + record.entradas):
                raise ValidationError(
                    f'Las salidas ({record.salidas}) no pueden exceder '
                    f'el stock total ({record.stock_inicial + record.entradas}).'
                )

    # =====================================================
    # SQL CONSTRAINTS
    # =====================================================

    _sql_constraints = [
        ('libro_unique', 'UNIQUE(libro_id)',
         'Ya existe un registro de inventario para este libro.'),
    ]

    # =====================================================
    # MÉTODOS DE ACCIÓN
    # =====================================================

    def action_agregar_stock(self):
        """Incrementa el stock en 1."""
        for record in self:
            record.entradas += 1

    def action_registrar_baja(self):
        """Registra una baja de stock."""
        for record in self:
            if record.stock_disponible <= 0:
                raise ValidationError('No hay stock disponible para dar de baja.')
            record.salidas += 1
