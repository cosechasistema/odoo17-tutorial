# -*- coding: utf-8 -*-
"""
Wizard para Exportar Datos - Tutorial 08

Permite exportar datos de la biblioteca a formato CSV o Excel.

CONCEPTOS CLAVE:
- Generación de archivos CSV programáticamente
- Uso de io.StringIO/BytesIO para streams
- Codificación base64 para descarga
- Selección dinámica de campos a exportar
"""

import base64
import csv
import io
from datetime import datetime

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class WizardExportarDatos(models.TransientModel):
    """
    Wizard para exportar datos de la biblioteca.

    Permite seleccionar:
    - Qué modelo exportar (libros, miembros, préstamos)
    - Qué campos incluir
    - Filtros de fecha
    - Formato de salida
    """

    _name = 'biblioteca.wizard.exportar.datos'
    _description = 'Wizard para Exportar Datos'

    # =====================================================
    # CAMPOS
    # =====================================================

    modelo = fields.Selection([
        ('libro', 'Libros'),
        ('miembro', 'Miembros'),
        ('prestamo', 'Préstamos'),
    ], string='Datos a Exportar', required=True, default='libro')

    # Campos a exportar por modelo
    campos_libro = fields.Many2many(
        'ir.model.fields',
        'wizard_export_campos_libro_rel',
        string='Campos de Libro',
        domain="[('model', '=', 'biblioteca.libro'), ('store', '=', True)]",
    )

    campos_miembro = fields.Many2many(
        'ir.model.fields',
        'wizard_export_campos_miembro_rel',
        string='Campos de Miembro',
        domain="[('model', '=', 'biblioteca.miembro'), ('store', '=', True)]",
    )

    campos_prestamo = fields.Many2many(
        'ir.model.fields',
        'wizard_export_campos_prestamo_rel',
        string='Campos de Préstamo',
        domain="[('model', '=', 'biblioteca.prestamo'), ('store', '=', True)]",
    )

    # Filtros
    fecha_desde = fields.Date(
        string='Desde',
        help='Filtrar por fecha de creación',
    )

    fecha_hasta = fields.Date(
        string='Hasta',
    )

    # Opciones de formato
    delimitador = fields.Selection([
        (',', 'Coma (,)'),
        (';', 'Punto y coma (;)'),
        ('\t', 'Tabulador'),
    ], string='Delimitador', default=';', required=True)

    incluir_ids = fields.Boolean(
        string='Incluir IDs',
        default=False,
    )

    # Archivo generado
    archivo = fields.Binary(
        string='Archivo Generado',
        readonly=True,
    )

    archivo_nombre = fields.Char(
        string='Nombre del Archivo',
        readonly=True,
    )

    estado = fields.Selection([
        ('configurar', 'Configurar'),
        ('descarga', 'Descargar'),
    ], default='configurar')

    # =====================================================
    # MÉTODOS
    # =====================================================

    @api.onchange('modelo')
    def _onchange_modelo(self):
        """Limpiar campos seleccionados al cambiar modelo."""
        self.campos_libro = False
        self.campos_miembro = False
        self.campos_prestamo = False

    def _get_model_name(self):
        """Obtiene el nombre técnico del modelo seleccionado."""
        model_map = {
            'libro': 'biblioteca.libro',
            'miembro': 'biblioteca.miembro',
            'prestamo': 'biblioteca.prestamo',
        }
        return model_map.get(self.modelo)

    def _get_campos_seleccionados(self):
        """Obtiene los campos seleccionados según el modelo."""
        if self.modelo == 'libro':
            return self.campos_libro
        elif self.modelo == 'miembro':
            return self.campos_miembro
        elif self.modelo == 'prestamo':
            return self.campos_prestamo
        return []

    def _get_default_fields(self):
        """
        Retorna campos por defecto si no se seleccionaron campos específicos.
        """
        defaults = {
            'libro': ['name', 'isbn', 'autor', 'editorial', 'paginas', 'precio', 'estado'],
            'miembro': ['name', 'numero_miembro', 'email', 'telefono', 'activo'],
            'prestamo': ['libro_id', 'miembro_id', 'fecha_prestamo', 'fecha_devolucion_esperada', 'estado'],
        }
        return defaults.get(self.modelo, ['name'])

    def _format_value(self, value, field_type):
        """
        Formatea un valor para CSV según su tipo.

        Args:
            value: Valor a formatear
            field_type: Tipo del campo Odoo

        Returns:
            String formateado
        """
        if value is False or value is None:
            return ''

        if field_type == 'many2one':
            # Para Many2one, obtener el display_name
            return value.display_name if hasattr(value, 'display_name') else str(value)

        if field_type == 'one2many' or field_type == 'many2many':
            # Para x2many, concatenar nombres
            if hasattr(value, 'mapped'):
                return ', '.join(value.mapped('display_name'))
            return str(value)

        if field_type == 'date':
            return value.strftime('%Y-%m-%d') if value else ''

        if field_type == 'datetime':
            return value.strftime('%Y-%m-%d %H:%M:%S') if value else ''

        if field_type == 'boolean':
            return 'Sí' if value else 'No'

        if field_type == 'selection':
            return str(value) if value else ''

        return str(value)

    def action_exportar(self):
        """
        Ejecuta la exportación de datos.

        PROCESO:
        1. Obtener registros según filtros
        2. Determinar campos a exportar
        3. Generar CSV
        4. Codificar y preparar descarga
        """
        self.ensure_one()

        model_name = self._get_model_name()
        if not model_name:
            raise UserError(_('Debe seleccionar un tipo de datos a exportar'))

        # Obtener modelo
        Model = self.env[model_name]

        # Construir dominio de búsqueda
        domain = []
        if self.fecha_desde:
            domain.append(('create_date', '>=', self.fecha_desde))
        if self.fecha_hasta:
            domain.append(('create_date', '<=', self.fecha_hasta))

        # Buscar registros
        registros = Model.search(domain)

        if not registros:
            raise UserError(_('No se encontraron registros para exportar'))

        # Determinar campos a exportar
        campos_obj = self._get_campos_seleccionados()
        if campos_obj:
            campos = campos_obj.mapped('name')
        else:
            campos = self._get_default_fields()

        # Agregar ID si se solicitó
        if self.incluir_ids and 'id' not in campos:
            campos = ['id'] + list(campos)

        # Obtener información de campos
        fields_info = Model.fields_get(campos)

        # Crear CSV
        output = io.StringIO()
        writer = csv.writer(output, delimiter=self.delimitador)

        # Escribir encabezado
        header = []
        for campo in campos:
            if campo in fields_info:
                header.append(fields_info[campo].get('string', campo))
            else:
                header.append(campo)
        writer.writerow(header)

        # Escribir datos
        for registro in registros:
            row = []
            for campo in campos:
                try:
                    value = getattr(registro, campo, '')
                    field_type = fields_info.get(campo, {}).get('type', 'char')
                    row.append(self._format_value(value, field_type))
                except Exception:
                    row.append('')
            writer.writerow(row)

        # Obtener contenido y codificar
        contenido = output.getvalue()
        output.close()

        # Codificar con BOM para Excel
        contenido_bytes = ('\ufeff' + contenido).encode('utf-8')
        self.archivo = base64.b64encode(contenido_bytes)

        # Nombre del archivo
        fecha_str = datetime.now().strftime('%Y%m%d_%H%M')
        self.archivo_nombre = f"exportacion_{self.modelo}_{fecha_str}.csv"

        self.estado = 'descarga'

        return self._reopen_wizard()

    def action_descargar(self):
        """Inicia la descarga del archivo generado."""
        self.ensure_one()

        if not self.archivo:
            raise UserError(_('Primero debe generar el archivo'))

        # Crear attachment
        attachment = self.env['ir.attachment'].create({
            'name': self.archivo_nombre,
            'type': 'binary',
            'datas': self.archivo,
            'mimetype': 'text/csv',
        })

        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}?download=true',
            'target': 'self',
        }

    def action_nueva_exportacion(self):
        """Reinicia el wizard para una nueva exportación."""
        self.estado = 'configurar'
        self.archivo = False
        self.archivo_nombre = False
        return self._reopen_wizard()

    def _reopen_wizard(self):
        """Reabre el wizard."""
        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }
