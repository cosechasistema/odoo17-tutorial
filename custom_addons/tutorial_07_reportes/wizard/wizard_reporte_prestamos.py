# -*- coding: utf-8 -*-
"""
Wizard para Reporte de Préstamos - Tutorial 07

Demuestra cómo crear un wizard (TransientModel) para
generar reportes con parámetros personalizados.

CONCEPTOS CLAVE:
- TransientModel: Modelo temporal que se limpia automáticamente
- Wizard: Formulario emergente para recopilar datos del usuario
- Generar reportes con filtros dinámicos
"""

from odoo import models, fields, api
from odoo.exceptions import UserError


class WizardReportePrestamos(models.TransientModel):
    """
    Wizard para generar reporte de préstamos con filtros.

    TransientModel vs Model:
    - TransientModel: Datos temporales, se limpian automáticamente
    - Model: Datos persistentes en la base de datos

    Uso típico de wizards:
    - Recopilar parámetros antes de ejecutar una acción
    - Confirmar operaciones masivas
    - Generar reportes con filtros
    """

    _name = 'biblioteca.wizard.reporte.prestamos'
    _description = 'Wizard para Reporte de Préstamos'

    # =====================================================
    # CAMPOS DEL WIZARD
    # =====================================================

    # Filtro por miembro (opcional)
    miembro_id = fields.Many2one(
        comodel_name='biblioteca.miembro',
        string='Miembro',
        help='Dejar vacío para incluir todos los miembros',
    )

    # Filtro por estado
    estado = fields.Selection([
        ('todos', 'Todos'),
        ('activo', 'Solo Activos'),
        ('vencido', 'Solo Vencidos'),
        ('devuelto', 'Solo Devueltos'),
    ], string='Estado', default='todos', required=True)

    # Rango de fechas
    fecha_desde = fields.Date(
        string='Desde',
        default=lambda self: fields.Date.today().replace(day=1),
    )

    fecha_hasta = fields.Date(
        string='Hasta',
        default=fields.Date.today,
    )

    # Opciones de agrupación
    agrupar_por = fields.Selection([
        ('ninguno', 'Sin Agrupar'),
        ('miembro', 'Por Miembro'),
        ('estado', 'Por Estado'),
        ('mes', 'Por Mes'),
    ], string='Agrupar Por', default='miembro')

    # Mostrar totales
    mostrar_totales = fields.Boolean(
        string='Mostrar Totales',
        default=True,
    )

    # =====================================================
    # MÉTODOS
    # =====================================================

    def _get_prestamos(self):
        """
        Obtiene los préstamos según los filtros seleccionados.
        Retorna un recordset de biblioteca.prestamo.
        """
        domain = []

        # Filtro por miembro
        if self.miembro_id:
            domain.append(('miembro_id', '=', self.miembro_id.id))

        # Filtro por estado
        if self.estado != 'todos':
            domain.append(('estado', '=', self.estado))

        # Filtro por fecha
        if self.fecha_desde:
            domain.append(('fecha_prestamo', '>=', self.fecha_desde))
        if self.fecha_hasta:
            domain.append(('fecha_prestamo', '<=', self.fecha_hasta))

        prestamos = self.env['biblioteca.prestamo'].search(
            domain,
            order='fecha_prestamo desc'
        )

        return prestamos

    def _prepare_report_data(self):
        """
        Prepara los datos para el reporte.
        Retorna un diccionario con toda la información necesaria.
        """
        prestamos = self._get_prestamos()

        if not prestamos:
            raise UserError('No se encontraron préstamos con los filtros seleccionados.')

        # Datos base
        data = {
            'prestamos': prestamos,
            'wizard': self,
            'fecha_generacion': fields.Datetime.now(),
            'total_prestamos': len(prestamos),
        }

        # Calcular estadísticas
        data['total_activos'] = len(prestamos.filtered(lambda p: p.estado == 'activo'))
        data['total_vencidos'] = len(prestamos.filtered(lambda p: p.estado == 'vencido'))
        data['total_devueltos'] = len(prestamos.filtered(lambda p: p.estado == 'devuelto'))

        # Agrupar si es necesario
        if self.agrupar_por == 'miembro':
            grupos = {}
            for prestamo in prestamos:
                key = prestamo.miembro_id
                if key not in grupos:
                    grupos[key] = self.env['biblioteca.prestamo']
                grupos[key] |= prestamo
            data['grupos'] = grupos
            data['grupo_label'] = 'Miembro'

        elif self.agrupar_por == 'estado':
            grupos = {}
            for prestamo in prestamos:
                key = prestamo.estado
                if key not in grupos:
                    grupos[key] = self.env['biblioteca.prestamo']
                grupos[key] |= prestamo
            data['grupos'] = grupos
            data['grupo_label'] = 'Estado'

        elif self.agrupar_por == 'mes':
            grupos = {}
            for prestamo in prestamos:
                key = prestamo.fecha_prestamo.strftime('%Y-%m')
                if key not in grupos:
                    grupos[key] = self.env['biblioteca.prestamo']
                grupos[key] |= prestamo
            data['grupos'] = grupos
            data['grupo_label'] = 'Mes'

        else:
            data['grupos'] = None

        return data

    def action_generar_reporte(self):
        """
        Genera el reporte PDF.
        Este método se llama desde el botón del wizard.
        """
        self.ensure_one()

        # Validar fechas
        if self.fecha_desde and self.fecha_hasta:
            if self.fecha_desde > self.fecha_hasta:
                raise UserError('La fecha "Desde" no puede ser mayor que "Hasta".')

        # Obtener préstamos para pasar al reporte
        prestamos = self._get_prestamos()

        if not prestamos:
            raise UserError('No se encontraron préstamos con los filtros seleccionados.')

        # Preparar datos adicionales para el reporte
        data = {
            'wizard_id': self.id,
            'miembro_id': self.miembro_id.id if self.miembro_id else False,
            'estado': self.estado,
            'fecha_desde': self.fecha_desde,
            'fecha_hasta': self.fecha_hasta,
            'agrupar_por': self.agrupar_por,
            'mostrar_totales': self.mostrar_totales,
        }

        # Retornar la acción del reporte
        return self.env.ref(
            'tutorial_07_reportes.action_report_prestamos_wizard'
        ).report_action(prestamos, data=data)

    def action_vista_previa(self):
        """
        Muestra una vista previa en pantalla (vista tree).
        Útil para verificar los datos antes de generar el PDF.
        """
        self.ensure_one()
        prestamos = self._get_prestamos()

        if not prestamos:
            raise UserError('No se encontraron préstamos con los filtros seleccionados.')

        return {
            'name': 'Vista Previa de Préstamos',
            'type': 'ir.actions.act_window',
            'res_model': 'biblioteca.prestamo',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', prestamos.ids)],
            'context': {'create': False},
        }
