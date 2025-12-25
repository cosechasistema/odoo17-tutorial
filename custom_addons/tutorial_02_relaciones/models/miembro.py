# -*- coding: utf-8 -*-
"""
Modelo de Miembro - Tutorial 02

Demuestra el uso de Many2one (herencia) y One2many.
"""

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta


class Miembro(models.Model):
    """
    Miembro de la biblioteca.

    RELACIÓN MANY2ONE a res.partner:
    Cada miembro está vinculado a un contacto (partner) existente.
    Esto evita duplicar datos de contacto.

    RELACIÓN ONE2MANY:
    Un miembro tiene muchos préstamos (inverso del Many2one en préstamos).
    """

    _name = 'biblioteca.miembro'
    _description = 'Miembro de Biblioteca'
    _order = 'name'

    # =====================================================
    # RELACIÓN MANY2ONE
    # =====================================================

    # Many2one crea una columna partner_id INTEGER REFERENCES res_partner(id)
    partner_id = fields.Many2one(
        comodel_name='res.partner',  # Modelo relacionado
        string='Contacto',
        required=True,
        ondelete='restrict',  # No permitir borrar el partner si tiene miembro
        # Opciones de ondelete:
        # - 'restrict': Error si se intenta borrar
        # - 'cascade': Borrar este registro también
        # - 'set null': Poner NULL en este campo
        domain=[('is_company', '=', False)],  # Solo personas, no empresas
    )

    # =====================================================
    # CAMPOS RELATED (acceso directo a campos del partner)
    # =====================================================

    # Los campos related obtienen el valor de un campo del registro relacionado
    # No se almacenan por defecto (store=False), son calculados en tiempo real
    name = fields.Char(
        string='Nombre',
        related='partner_id.name',
        store=True,  # Almacenar para poder buscar/ordenar
        readonly=True,
    )

    email = fields.Char(
        string='Email',
        related='partner_id.email',
        readonly=False,  # Permite editar (modifica el partner)
    )

    phone = fields.Char(
        string='Teléfono',
        related='partner_id.phone',
        readonly=False,
    )

    # =====================================================
    # CAMPOS PROPIOS DEL MIEMBRO
    # =====================================================

    numero_carnet = fields.Char(
        string='Número de Carnet',
        copy=False,
        readonly=True,
        default='Nuevo',
    )

    fecha_registro = fields.Date(
        string='Fecha de Registro',
        default=fields.Date.today,
        required=True,
    )

    fecha_vencimiento = fields.Date(
        string='Fecha de Vencimiento',
        compute='_compute_fecha_vencimiento',
        store=True,
    )

    activo = fields.Boolean(
        string='Activo',
        default=True,
    )

    notas = fields.Text(
        string='Notas',
    )

    # =====================================================
    # RELACIÓN ONE2MANY
    # =====================================================

    # One2many es la inversa de un Many2one
    # Muestra todos los préstamos que tienen a este miembro en su campo miembro_id
    prestamo_ids = fields.One2many(
        comodel_name='biblioteca.prestamo',  # Modelo relacionado
        inverse_name='miembro_id',  # Campo Many2one en el otro modelo
        string='Préstamos',
    )

    # =====================================================
    # CAMPOS CALCULADOS
    # =====================================================

    prestamo_count = fields.Integer(
        string='Cantidad de Préstamos',
        compute='_compute_prestamo_count',
    )

    prestamos_activos = fields.Integer(
        string='Préstamos Activos',
        compute='_compute_prestamo_count',
    )

    @api.depends('fecha_registro')
    def _compute_fecha_vencimiento(self):
        for record in self:
            if record.fecha_registro:
                # Membresía válida por 1 año
                record.fecha_vencimiento = record.fecha_registro + relativedelta(years=1)
            else:
                record.fecha_vencimiento = False

    @api.depends('prestamo_ids', 'prestamo_ids.estado')
    def _compute_prestamo_count(self):
        for record in self:
            record.prestamo_count = len(record.prestamo_ids)
            record.prestamos_activos = len(record.prestamo_ids.filtered(
                lambda p: p.estado == 'activo'
            ))

    # =====================================================
    # MÉTODOS CRUD
    # =====================================================

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('numero_carnet', 'Nuevo') == 'Nuevo':
                # Generar número de carnet secuencial
                vals['numero_carnet'] = self.env['ir.sequence'].next_by_code(
                    'biblioteca.miembro.carnet'
                ) or 'MBR-0001'

        return super().create(vals_list)

    # =====================================================
    # RESTRICCIONES
    # =====================================================

    _sql_constraints = [
        ('partner_unique', 'UNIQUE(partner_id)',
         'Ya existe un miembro para este contacto.'),
        ('carnet_unique', 'UNIQUE(numero_carnet)',
         'El número de carnet debe ser único.'),
    ]

    @api.constrains('prestamo_ids')
    def _check_prestamos_limite(self):
        """Un miembro no puede tener más de 5 préstamos activos."""
        for record in self:
            if record.prestamos_activos > 5:
                raise ValidationError(
                    f'El miembro {record.name} ya tiene 5 préstamos activos. '
                    'No puede solicitar más libros.'
                )

    # =====================================================
    # MÉTODOS DE ACCIÓN
    # =====================================================

    def action_ver_prestamos(self):
        """Abre los préstamos de este miembro."""
        self.ensure_one()
        return {
            'name': f'Préstamos de {self.name}',
            'type': 'ir.actions.act_window',
            'res_model': 'biblioteca.prestamo',
            'view_mode': 'tree,form',
            'domain': [('miembro_id', '=', self.id)],
            'context': {'default_miembro_id': self.id},
        }

    def action_renovar_membresia(self):
        """Renueva la membresía por un año más."""
        for record in self:
            record.fecha_registro = fields.Date.today()
            # fecha_vencimiento se recalcula automáticamente
