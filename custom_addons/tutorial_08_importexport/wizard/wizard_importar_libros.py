# -*- coding: utf-8 -*-
"""
Wizard para Importar Libros - Tutorial 08

Permite importar libros desde un archivo CSV.

CONCEPTOS CLAVE:
- Leer archivos CSV en Python
- Decodificar base64 (archivos binarios en Odoo)
- Validación de datos durante importación
- Manejo de errores línea por línea
- Transacciones y rollback
"""

import base64
import csv
import io

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class WizardImportarLibros(models.TransientModel):
    """
    Wizard para importar libros desde CSV.

    El archivo CSV debe tener las columnas:
    - name (requerido): Título del libro
    - isbn: Código ISBN
    - autor: Nombre del autor
    - editorial: Editorial
    - paginas: Número de páginas
    - precio: Precio del libro
    """

    _name = 'biblioteca.wizard.importar.libros'
    _description = 'Wizard para Importar Libros'

    # =====================================================
    # CAMPOS
    # =====================================================

    archivo = fields.Binary(
        string='Archivo CSV',
        required=True,
        help='Archivo CSV con los libros a importar',
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

    actualizar_existentes = fields.Boolean(
        string='Actualizar si existe ISBN',
        default=False,
        help='Si el ISBN ya existe, actualiza el registro en lugar de crear uno nuevo',
    )

    # Vista previa
    preview = fields.Text(
        string='Vista Previa',
        readonly=True,
    )

    # Resultado
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
        """
        Genera vista previa cuando se carga el archivo.
        """
        if not self.archivo:
            self.preview = ''
            return

        try:
            # Decodificar archivo base64
            contenido = base64.b64decode(self.archivo)
            # Intentar decodificar como UTF-8
            try:
                texto = contenido.decode('utf-8')
            except UnicodeDecodeError:
                # Si falla, intentar con latin-1
                texto = contenido.decode('latin-1')

            # Leer CSV
            reader = csv.reader(
                io.StringIO(texto),
                delimiter=self.delimitador
            )

            lineas = list(reader)

            # Generar preview (máximo 5 líneas)
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

    def action_vista_previa(self):
        """Muestra la vista previa del archivo."""
        self._onchange_archivo()
        return self._reopen_wizard()

    def action_importar(self):
        """
        Ejecuta la importación de libros.

        PROCESO:
        1. Decodificar archivo
        2. Parsear CSV
        3. Validar cada línea
        4. Crear/actualizar registros
        5. Registrar resultados en log
        """
        self.ensure_one()

        if not self.archivo:
            raise UserError(_('Debe seleccionar un archivo CSV'))

        # Crear log de importación
        log = self.env['biblioteca.import.log'].crear_log(
            tipo='libro',
            archivo_nombre=self.archivo_nombre,
            archivo_contenido=self.archivo,
        )

        try:
            # Decodificar archivo
            contenido = base64.b64decode(self.archivo)
            try:
                texto = contenido.decode('utf-8')
            except UnicodeDecodeError:
                texto = contenido.decode('latin-1')

            # Parsear CSV
            reader = csv.DictReader(
                io.StringIO(texto),
                delimiter=self.delimitador
            ) if self.tiene_encabezado else csv.reader(
                io.StringIO(texto),
                delimiter=self.delimitador
            )

            # Procesar líneas
            total = 0
            exitosas = 0
            errores = []
            ids_creados = []

            # Definir mapeo de columnas si no hay encabezado
            columnas = ['name', 'isbn', 'autor', 'editorial', 'paginas', 'precio']

            for i, linea in enumerate(reader, start=2 if self.tiene_encabezado else 1):
                total += 1

                try:
                    # Convertir a diccionario si no tiene encabezado
                    if not self.tiene_encabezado:
                        linea = dict(zip(columnas, linea))

                    # Validar datos requeridos
                    if not linea.get('name'):
                        raise ValidationError(f"El título (name) es requerido")

                    # Preparar valores
                    vals = {
                        'name': linea.get('name', '').strip(),
                        'isbn': linea.get('isbn', '').strip() or False,
                        'autor': linea.get('autor', '').strip() or False,
                        'editorial': linea.get('editorial', '').strip() or False,
                    }

                    # Convertir campos numéricos
                    if linea.get('paginas'):
                        try:
                            vals['paginas'] = int(linea['paginas'])
                        except ValueError:
                            raise ValidationError(f"Páginas debe ser un número: {linea['paginas']}")

                    if linea.get('precio'):
                        try:
                            # Manejar tanto punto como coma decimal
                            precio_str = linea['precio'].replace(',', '.')
                            vals['precio'] = float(precio_str)
                        except ValueError:
                            raise ValidationError(f"Precio debe ser un número: {linea['precio']}")

                    # Buscar si existe por ISBN
                    libro_existente = False
                    if vals.get('isbn') and self.actualizar_existentes:
                        libro_existente = self.env['biblioteca.libro'].search([
                            ('isbn', '=', vals['isbn'])
                        ], limit=1)

                    if libro_existente:
                        # Actualizar existente
                        libro_existente.write(vals)
                        ids_creados.append(libro_existente.id)
                    else:
                        # Crear nuevo
                        nuevo = self.env['biblioteca.libro'].create(vals)
                        ids_creados.append(nuevo.id)

                    exitosas += 1

                except Exception as e:
                    errores.append(f"Línea {i}: {str(e)}")

            # Actualizar log
            errores_texto = '\n'.join(errores) if errores else None
            log.actualizar_resultado(total, exitosas, errores_texto)
            log.registros_creados_ids = ','.join(map(str, ids_creados))

            # Preparar resultado
            self.resultado = f"""
=== IMPORTACIÓN COMPLETADA ===

Total de líneas: {total}
Importadas exitosamente: {exitosas}
Con errores: {total - exitosas}

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
        """
        Genera y descarga una plantilla CSV de ejemplo.
        """
        # Contenido de la plantilla
        plantilla = """name,isbn,autor,editorial,paginas,precio
Don Quijote de la Mancha,9788420412146,Miguel de Cervantes,Alfaguara,1250,29.95
Cien años de soledad,9780307474728,Gabriel García Márquez,Vintage,417,15.99
El principito,9788478887194,Antoine de Saint-Exupéry,Salamandra,96,12.50"""

        # Codificar en base64
        archivo = base64.b64encode(plantilla.encode('utf-8'))

        # Crear attachment temporal
        attachment = self.env['ir.attachment'].create({
            'name': 'plantilla_libros.csv',
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
