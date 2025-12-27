# -*- coding: utf-8 -*-
"""
Modelo de Log de Importación - Tutorial 08

Registra todas las importaciones realizadas para tener
un historial y poder auditar los datos importados.

CONCEPTOS CLAVE:
- Modelo para auditoría de operaciones
- Campos de relación con usuarios
- Almacenamiento de archivos procesados
- Estados de proceso
"""

from odoo import models, fields, api


class ImportLog(models.Model):
    """
    Registro de importaciones realizadas.

    Guarda información sobre cada importación:
    - Quién la realizó
    - Cuándo
    - Qué tipo de datos
    - Resultado (éxitos/errores)
    """

    _name = 'biblioteca.import.log'
    _description = 'Log de Importación'
    _order = 'fecha desc'
    _rec_name = 'nombre'

    # =====================================================
    # CAMPOS
    # =====================================================

    nombre = fields.Char(
        string='Nombre',
        required=True,
        readonly=True,
    )

    fecha = fields.Datetime(
        string='Fecha de Importación',
        default=fields.Datetime.now,
        readonly=True,
    )

    usuario_id = fields.Many2one(
        comodel_name='res.users',
        string='Usuario',
        default=lambda self: self.env.user,
        readonly=True,
    )

    tipo = fields.Selection([
        ('libro', 'Libros'),
        ('miembro', 'Miembros'),
        ('prestamo', 'Préstamos'),
        ('otro', 'Otro'),
    ], string='Tipo de Datos', required=True, readonly=True)

    archivo_nombre = fields.Char(
        string='Nombre del Archivo',
        readonly=True,
    )

    archivo_contenido = fields.Binary(
        string='Archivo Original',
        readonly=True,
        help='Copia del archivo importado para referencia',
    )

    # Estadísticas
    total_lineas = fields.Integer(
        string='Total Líneas',
        readonly=True,
        default=0,
    )

    lineas_exitosas = fields.Integer(
        string='Líneas Exitosas',
        readonly=True,
        default=0,
    )

    lineas_error = fields.Integer(
        string='Líneas con Error',
        readonly=True,
        default=0,
    )

    # Estado
    estado = fields.Selection([
        ('borrador', 'Borrador'),
        ('procesando', 'Procesando'),
        ('completado', 'Completado'),
        ('completado_errores', 'Completado con Errores'),
        ('error', 'Error'),
    ], string='Estado', default='borrador', readonly=True)

    # Detalles de errores
    errores = fields.Text(
        string='Detalle de Errores',
        readonly=True,
    )

    # Registros creados (referencia genérica)
    registros_creados_ids = fields.Char(
        string='IDs Creados',
        readonly=True,
        help='Lista de IDs de registros creados, separados por coma',
    )

    # Campo calculado para porcentaje de éxito
    porcentaje_exito = fields.Float(
        string='% Éxito',
        compute='_compute_porcentaje_exito',
    )

    @api.depends('total_lineas', 'lineas_exitosas')
    def _compute_porcentaje_exito(self):
        for record in self:
            if record.total_lineas > 0:
                record.porcentaje_exito = (record.lineas_exitosas / record.total_lineas) * 100
            else:
                record.porcentaje_exito = 0.0

    # =====================================================
    # MÉTODOS
    # =====================================================

    def action_ver_registros_creados(self):
        """
        Abre una vista con los registros creados en esta importación.
        """
        self.ensure_one()

        if not self.registros_creados_ids:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Sin registros',
                    'message': 'No hay registros asociados a esta importación.',
                    'type': 'warning',
                }
            }

        # Convertir string de IDs a lista
        ids = [int(x.strip()) for x in self.registros_creados_ids.split(',') if x.strip()]

        # Determinar el modelo según el tipo
        model_map = {
            'libro': 'biblioteca.libro',
            'miembro': 'biblioteca.miembro',
            'prestamo': 'biblioteca.prestamo',
        }

        model = model_map.get(self.tipo)
        if not model:
            return

        return {
            'name': f'Registros Importados ({self.nombre})',
            'type': 'ir.actions.act_window',
            'res_model': model,
            'view_mode': 'tree,form',
            'domain': [('id', 'in', ids)],
        }

    @api.model
    def crear_log(self, tipo, archivo_nombre, archivo_contenido=None):
        """
        Método helper para crear un nuevo log de importación.

        Args:
            tipo: Tipo de datos a importar
            archivo_nombre: Nombre del archivo
            archivo_contenido: Contenido binario del archivo (opcional)

        Returns:
            Registro de import.log creado
        """
        return self.create({
            'nombre': f"Importación {tipo.capitalize()} - {fields.Datetime.now()}",
            'tipo': tipo,
            'archivo_nombre': archivo_nombre,
            'archivo_contenido': archivo_contenido,
            'estado': 'procesando',
        })

    def actualizar_resultado(self, total, exitosas, errores_detalle=None):
        """
        Actualiza el log con el resultado de la importación.

        Args:
            total: Total de líneas procesadas
            exitosas: Líneas importadas exitosamente
            errores_detalle: Texto con detalle de errores
        """
        self.ensure_one()

        lineas_error = total - exitosas

        if lineas_error == 0:
            estado = 'completado'
        elif exitosas > 0:
            estado = 'completado_errores'
        else:
            estado = 'error'

        self.write({
            'total_lineas': total,
            'lineas_exitosas': exitosas,
            'lineas_error': lineas_error,
            'errores': errores_detalle,
            'estado': estado,
        })
