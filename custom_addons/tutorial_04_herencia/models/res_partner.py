# -*- coding: utf-8 -*-
"""
Herencia de res.partner - Tutorial 04

Demuestra cómo extender el modelo de contactos de Odoo
para agregar funcionalidad de autores de libros.

TIPOS DE HERENCIA EN ODOO:
1. _inherit (Herencia clásica): Extiende el modelo original
2. _inherits (Herencia delegada): Composición/delegación
3. _inherit + _name (Herencia prototipal): Crea nuevo modelo basado en otro
"""

from odoo import models, fields, api


class ResPartnerAutor(models.Model):
    """
    HERENCIA CLÁSICA (_inherit)

    Extiende res.partner para agregar campos y métodos.
    NO crea una nueva tabla, modifica la existente.

    Equivalente en otros lenguajes:
    - Python: class MiClase(ClaseBase)
    - JavaScript: class MiClase extends ClaseBase
    - SQL: ALTER TABLE res_partner ADD COLUMN ...
    """

    _inherit = 'res.partner'  # Modelo a extender

    # =====================================================
    # NUEVOS CAMPOS
    # =====================================================

    # Campos específicos para autores
    es_autor = fields.Boolean(
        string='Es Autor',
        default=False,
        help='Marcar si este contacto es un autor de libros',
    )

    biografia = fields.Text(
        string='Biografía',
        help='Biografía del autor',
    )

    fecha_nacimiento = fields.Date(
        string='Fecha de Nacimiento',
    )

    fecha_fallecimiento = fields.Date(
        string='Fecha de Fallecimiento',
    )

    nacionalidad = fields.Char(
        string='Nacionalidad',
    )

    genero_literario = fields.Selection([
        ('novela', 'Novela'),
        ('poesia', 'Poesía'),
        ('ensayo', 'Ensayo'),
        ('cuento', 'Cuento'),
        ('teatro', 'Teatro'),
        ('otro', 'Otro'),
    ], string='Género Literario Principal')

    # =====================================================
    # RELACIÓN CON LIBROS
    # =====================================================

    # Libros escritos por este autor
    libro_ids = fields.One2many(
        comodel_name='biblioteca.libro',
        inverse_name='autor_id',
        string='Libros Publicados',
    )

    libro_count = fields.Integer(
        string='Cantidad de Libros',
        compute='_compute_libro_count',
    )

    @api.depends('libro_ids')
    def _compute_libro_count(self):
        for record in self:
            record.libro_count = len(record.libro_ids)

    # =====================================================
    # SOBRESCRIBIR MÉTODOS
    # =====================================================

    def name_get(self):
        """
        Sobrescribir cómo se muestra el nombre del registro.

        IMPORTANTE: Siempre llamar a super() primero.
        """
        result = super().name_get()

        # Modificar solo para autores
        new_result = []
        for res in result:
            record = self.browse(res[0])
            if record.es_autor and record.nacionalidad:
                # Mostrar nacionalidad para autores
                new_result.append((res[0], f"{res[1]} ({record.nacionalidad})"))
            else:
                new_result.append(res)

        return new_result

    @api.model_create_multi
    def create(self, vals_list):
        """
        Sobrescribir create para agregar lógica al crear autores.
        """
        for vals in vals_list:
            # Si es autor, establecer como individuo (no empresa)
            if vals.get('es_autor'):
                vals['is_company'] = False

        return super().create(vals_list)

    def write(self, vals):
        """
        Sobrescribir write para validar cambios.
        """
        # Si se marca como autor, verificar que no sea empresa
        if vals.get('es_autor') and any(r.is_company for r in self):
            vals['is_company'] = False

        return super().write(vals)

    # =====================================================
    # MÉTODOS DE ACCIÓN
    # =====================================================

    def action_ver_libros(self):
        """Abre la lista de libros del autor."""
        self.ensure_one()
        return {
            'name': f'Libros de {self.name}',
            'type': 'ir.actions.act_window',
            'res_model': 'biblioteca.libro',
            'view_mode': 'tree,form',
            'domain': [('autor_id', '=', self.id)],
            'context': {'default_autor_id': self.id},
        }

    def action_marcar_como_autor(self):
        """Marca el contacto como autor."""
        self.write({'es_autor': True, 'is_company': False})


# =====================================================
# HERENCIA DELEGADA (_inherits) - EJEMPLO
# =====================================================

class BibliotecaSocio(models.Model):
    """
    HERENCIA DELEGADA (_inherits)

    Crea un nuevo modelo que "tiene" un res.partner.
    Es como composición: BibliotecaSocio CONTIENE un res.partner.

    Cuando creas un BibliotecaSocio:
    1. Se crea automáticamente un res.partner
    2. Se vincula a través de partner_id
    3. Puedes acceder a campos del partner directamente

    Equivalente conceptual:
    - Es como si BibliotecaSocio heredara los campos de res.partner
    - Pero cada modelo tiene su propia tabla
    """

    _name = 'biblioteca.socio'
    _description = 'Socio de Biblioteca (herencia delegada)'
    _inherits = {'res.partner': 'partner_id'}  # Delega a res.partner

    # Este campo es OBLIGATORIO con _inherits
    partner_id = fields.Many2one(
        'res.partner',
        string='Contacto',
        required=True,
        ondelete='cascade',
        auto_join=True,
    )

    # Campos propios del socio (además de los heredados de partner)
    numero_socio = fields.Char(
        string='Número de Socio',
        readonly=True,
        copy=False,
        default='Nuevo',
    )

    fecha_alta = fields.Date(
        string='Fecha de Alta',
        default=fields.Date.today,
    )

    tipo_membresia = fields.Selection([
        ('basica', 'Básica'),
        ('premium', 'Premium'),
        ('vip', 'VIP'),
    ], string='Tipo de Membresía', default='basica')

    # =====================================================
    # MÉTODOS
    # =====================================================

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('numero_socio', 'Nuevo') == 'Nuevo':
                vals['numero_socio'] = self.env['ir.sequence'].next_by_code(
                    'biblioteca.socio'
                ) or 'SOC-0001'
        return super().create(vals_list)
