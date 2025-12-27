# -*- coding: utf-8 -*-
"""
Wizard para Importar Miembros - Tutorial 08

Permite importar miembros de la biblioteca desde un archivo CSV.

Similar al wizard de libros pero con campos específicos de miembros
y validaciones adicionales (email único, formato de fechas, etc.)
"""

import base64
import csv
import io
from datetime import datetime

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class WizardImportarMiembros(models.TransientModel):
    """
    Wizard para importar miembros desde CSV.

    El archivo CSV debe tener las columnas:
    - name (requerido): Nombre del miembro
    - email: Correo electrónico
    - telefono: Número de teléfono
    - direccion: Dirección
    - fecha_alta: Fecha de alta (formato: YYYY-MM-DD)
    """

    _name = 'biblioteca.wizard.importar.miembros'
    _description = 'Wizard para Importar Miembros'

    # =====================================================
    # CAMPOS
    # =====================================================

    archivo = fields.Binary(
        string='Archivo CSV',
        required=True,
    )

    archivo_nombre = fields.Char(
        string='Nombre del Archivo',
    )

    delimitador = fields.Selection([
        (',', 'Coma (,)'),
        (';', 'Punto y coma (;)'),
        ('\t', 'Tabulador'),
        ('|', 'Pipe (|)'),
    ], string='Delimitador', default=',', required=True)

    tiene_encabezado = fields.Boolean(
        string='Primera fila es encabezado',
        default=True,
    )

    formato_fecha = fields.Selection([
        ('%Y-%m-%d', 'YYYY-MM-DD (2024-01-31)'),
        ('%d/%m/%Y', 'DD/MM/YYYY (31/01/2024)'),
        ('%m/%d/%Y', 'MM/DD/YYYY (01/31/2024)'),
        ('%d-%m-%Y', 'DD-MM-YYYY (31-01-2024)'),
    ], string='Formato de Fecha', default='%Y-%m-%d', required=True)

    omitir_duplicados = fields.Boolean(
        string='Omitir emails duplicados',
        default=True,
        help='Si el email ya existe, omite el registro en lugar de dar error',
    )

    preview = fields.Text(
        string='Vista Previa',
        readonly=True,
    )

    resultado = fields.Text(
        string='Resultado',
        readonly=True,
    )

    estado = fields.Selection([
        ('cargar', 'Cargar Archivo'),
        ('preview', 'Vista Previa'),
        ('resultado', 'Resultado'),
    ], default='cargar')

    # =====================================================
    # MÉTODOS
    # =====================================================

    @api.onchange('archivo', 'delimitador', 'tiene_encabezado')
    def _onchange_archivo(self):
        """Genera vista previa cuando se carga el archivo."""
        if not self.archivo:
            self.preview = ''
            return

        try:
            contenido = base64.b64decode(self.archivo)
            try:
                texto = contenido.decode('utf-8')
            except UnicodeDecodeError:
                texto = contenido.decode('latin-1')

            reader = csv.reader(io.StringIO(texto), delimiter=self.delimitador)
            lineas = list(reader)

            preview_lines = []
            for i, linea in enumerate(lineas[:6]):
                if i == 0 and self.tiene_encabezado:
                    preview_lines.append(f"[ENCABEZADO] {' | '.join(linea)}")
                else:
                    preview_lines.append(f"[Línea {i}] {' | '.join(linea)}")

            if len(lineas) > 6:
                preview_lines.append(f"... y {len(lineas) - 6} líneas más")

            self.preview = '\n'.join(preview_lines)
            self.estado = 'preview'

        except Exception as e:
            self.preview = f"Error al leer archivo: {str(e)}"

    def _parsear_fecha(self, fecha_str):
        """
        Parsea una fecha según el formato seleccionado.

        Args:
            fecha_str: String con la fecha

        Returns:
            Objeto date o False si está vacío
        """
        if not fecha_str or not fecha_str.strip():
            return False

        try:
            return datetime.strptime(fecha_str.strip(), self.formato_fecha).date()
        except ValueError:
            raise ValidationError(
                f"Formato de fecha inválido: '{fecha_str}'. "
                f"Se esperaba formato: {self.formato_fecha}"
            )

    def _validar_email(self, email):
        """
        Valida formato básico de email.

        Args:
            email: String con el email

        Returns:
            Email validado o False
        """
        if not email or not email.strip():
            return False

        email = email.strip().lower()

        # Validación básica
        if '@' not in email or '.' not in email.split('@')[-1]:
            raise ValidationError(f"Email inválido: {email}")

        return email

    def action_importar(self):
        """Ejecuta la importación de miembros."""
        self.ensure_one()

        if not self.archivo:
            raise UserError(_('Debe seleccionar un archivo CSV'))

        # Crear log
        log = self.env['biblioteca.import.log'].crear_log(
            tipo='miembro',
            archivo_nombre=self.archivo_nombre,
            archivo_contenido=self.archivo,
        )

        try:
            contenido = base64.b64decode(self.archivo)
            try:
                texto = contenido.decode('utf-8')
            except UnicodeDecodeError:
                texto = contenido.decode('latin-1')

            reader = csv.DictReader(
                io.StringIO(texto),
                delimiter=self.delimitador
            ) if self.tiene_encabezado else csv.reader(
                io.StringIO(texto),
                delimiter=self.delimitador
            )

            total = 0
            exitosas = 0
            omitidas = 0
            errores = []
            ids_creados = []

            columnas = ['name', 'email', 'telefono', 'direccion', 'fecha_alta']

            for i, linea in enumerate(reader, start=2 if self.tiene_encabezado else 1):
                total += 1

                try:
                    if not self.tiene_encabezado:
                        linea = dict(zip(columnas, linea))

                    # Validar nombre requerido
                    if not linea.get('name'):
                        raise ValidationError("El nombre (name) es requerido")

                    # Validar y preparar email
                    email = self._validar_email(linea.get('email', ''))

                    # Verificar duplicado de email
                    if email and self.omitir_duplicados:
                        existe = self.env['biblioteca.miembro'].search([
                            ('email', '=', email)
                        ], limit=1)
                        if existe:
                            omitidas += 1
                            continue

                    # Preparar valores
                    vals = {
                        'name': linea.get('name', '').strip(),
                        'email': email,
                        'telefono': linea.get('telefono', '').strip() or False,
                        'direccion': linea.get('direccion', '').strip() or False,
                    }

                    # Parsear fecha si viene
                    if linea.get('fecha_alta'):
                        vals['fecha_alta'] = self._parsear_fecha(linea['fecha_alta'])

                    # Crear miembro
                    nuevo = self.env['biblioteca.miembro'].create(vals)
                    ids_creados.append(nuevo.id)
                    exitosas += 1

                except Exception as e:
                    errores.append(f"Línea {i}: {str(e)}")

            # Actualizar log
            errores_texto = '\n'.join(errores) if errores else None
            log.actualizar_resultado(total, exitosas, errores_texto)
            log.registros_creados_ids = ','.join(map(str, ids_creados))

            self.resultado = f"""
=== IMPORTACIÓN COMPLETADA ===

Total de líneas: {total}
Importadas exitosamente: {exitosas}
Omitidas (duplicadas): {omitidas}
Con errores: {total - exitosas - omitidas}

{'=' * 30}
ERRORES:
{errores_texto or 'Ninguno'}
            """.strip()

            self.estado = 'resultado'

            return self._reopen_wizard()

        except Exception as e:
            log.write({
                'estado': 'error',
                'errores': str(e),
            })
            raise UserError(_(f'Error durante la importación: {str(e)}'))

    def action_descargar_plantilla(self):
        """Genera y descarga plantilla CSV de ejemplo."""
        plantilla = """name,email,telefono,direccion,fecha_alta
Juan Pérez,juan.perez@example.com,555-1234,Calle Principal 123,2024-01-15
María García,maria.garcia@example.com,555-5678,Avenida Central 456,2024-02-20
Carlos López,carlos.lopez@example.com,555-9012,Plaza Mayor 789,2024-03-10"""

        archivo = base64.b64encode(plantilla.encode('utf-8'))

        attachment = self.env['ir.attachment'].create({
            'name': 'plantilla_miembros.csv',
            'type': 'binary',
            'datas': archivo,
            'mimetype': 'text/csv',
        })

        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}?download=true',
            'target': 'self',
        }

    def _reopen_wizard(self):
        """Reabre el wizard para mostrar resultados."""
        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }
