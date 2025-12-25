# -*- coding: utf-8 -*-
"""
Modelo de Libro - Tutorial 01

Este archivo define el modelo 'biblioteca.libro' que representa
un libro en nuestra biblioteca.

CONCEPTOS CLAVE:
- models.Model: Crea una tabla en la base de datos
- _name: Nombre técnico del modelo (tabla: biblioteca_libro)
- _description: Descripción legible para humanos
- _order: Ordenamiento por defecto de los registros
- fields.*: Diferentes tipos de campos
"""

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class Libro(models.Model):
    """
    Modelo que representa un libro en la biblioteca.

    EQUIVALENTE SQL:
    CREATE TABLE biblioteca_libro (
        id SERIAL PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        isbn VARCHAR(13),
        autor VARCHAR(100),
        editorial VARCHAR(100),
        fecha_publicacion DATE,
        paginas INTEGER,
        precio DECIMAL(10,2),
        descripcion TEXT,
        disponible BOOLEAN DEFAULT true,
        estado VARCHAR(20) DEFAULT 'disponible',
        create_uid INTEGER REFERENCES res_users(id),
        create_date TIMESTAMP,
        write_uid INTEGER REFERENCES res_users(id),
        write_date TIMESTAMP
    );
    """

    # =====================================================
    # ATRIBUTOS DEL MODELO
    # =====================================================

    _name = 'biblioteca.libro'  # Nombre técnico (tabla: biblioteca_libro)
    _description = 'Libro de Biblioteca'  # Descripción para la UI
    _order = 'name asc'  # Orden por defecto: por nombre ascendente
    _rec_name = 'name'  # Campo que se usa como "nombre" del registro

    # =====================================================
    # CAMPOS
    # =====================================================

    # Campo Char: texto corto (VARCHAR en SQL)
    name = fields.Char(
        string='Título',  # Etiqueta en la UI
        required=True,  # NOT NULL en SQL
        index=True,  # Crear índice en BD para búsquedas rápidas
        help='Título completo del libro',  # Tooltip de ayuda
    )

    # Campo Char con tamaño máximo
    isbn = fields.Char(
        string='ISBN',
        size=13,  # Máximo 13 caracteres
        copy=False,  # No se copia al duplicar registro
        help='Código ISBN-10 o ISBN-13',
    )

    # Más campos Char
    autor = fields.Char(string='Autor')
    editorial = fields.Char(string='Editorial')

    # Campo Date: solo fecha (DATE en SQL)
    fecha_publicacion = fields.Date(
        string='Fecha de Publicación',
        default=fields.Date.today,  # Valor por defecto: hoy
    )

    # Campo Integer: número entero (INTEGER en SQL)
    paginas = fields.Integer(
        string='Número de Páginas',
        default=0,
    )

    # Campo Float: número decimal (DECIMAL en SQL)
    precio = fields.Float(
        string='Precio',
        digits=(10, 2),  # 10 dígitos total, 2 decimales
        default=0.0,
    )

    # Campo Text: texto largo (TEXT en SQL)
    descripcion = fields.Text(
        string='Descripción',
        help='Sinopsis o descripción del libro',
    )

    # Campo Boolean: verdadero/falso (BOOLEAN en SQL)
    disponible = fields.Boolean(
        string='Disponible',
        default=True,
        help='Indica si el libro está disponible para préstamo',
    )

    # Campo Selection: lista de opciones (VARCHAR + CHECK en SQL)
    estado = fields.Selection(
        selection=[
            ('disponible', 'Disponible'),
            ('prestado', 'Prestado'),
            ('reservado', 'Reservado'),
            ('mantenimiento', 'En Mantenimiento'),
        ],
        string='Estado',
        default='disponible',
        required=True,
    )

    # Campo Image: para guardar imagen (BYTEA en SQL)
    portada = fields.Image(
        string='Portada',
        max_width=256,
        max_height=256,
    )

    # =====================================================
    # RESTRICCIONES SQL
    # =====================================================

    # Restricción única a nivel de base de datos
    _sql_constraints = [
        (
            'isbn_unique',  # Nombre de la constraint
            'UNIQUE(isbn)',  # SQL
            'El ISBN debe ser único. Ya existe un libro con este ISBN.'  # Mensaje
        ),
        (
            'paginas_positive',
            'CHECK(paginas >= 0)',
            'El número de páginas no puede ser negativo.'
        ),
        (
            'precio_positive',
            'CHECK(precio >= 0)',
            'El precio no puede ser negativo.'
        ),
    ]

    # =====================================================
    # RESTRICCIONES PYTHON (más flexibles)
    # =====================================================

    @api.constrains('isbn')
    def _check_isbn(self):
        """
        Valida que el ISBN tenga el formato correcto.

        @api.constrains: Se ejecuta al crear/modificar el registro.
        Si la validación falla, se lanza ValidationError y se revierte la transacción.
        """
        for record in self:
            if record.isbn:
                # Quitar guiones y espacios
                isbn_limpio = record.isbn.replace('-', '').replace(' ', '')
                # ISBN debe tener 10 o 13 dígitos
                if len(isbn_limpio) not in [10, 13]:
                    raise ValidationError(
                        'El ISBN debe tener 10 o 13 dígitos. '
                        f'El ISBN "{record.isbn}" tiene {len(isbn_limpio)} dígitos.'
                    )
                # Verificar que sean solo dígitos (excepto último de ISBN-10 que puede ser X)
                if not isbn_limpio[:-1].isdigit():
                    raise ValidationError(
                        f'El ISBN "{record.isbn}" contiene caracteres inválidos.'
                    )

    # =====================================================
    # MÉTODOS DE ACCIÓN (botones)
    # =====================================================

    def action_marcar_prestado(self):
        """
        Marca el libro como prestado.
        Este método se puede vincular a un botón en la vista.
        """
        for record in self:
            record.write({
                'estado': 'prestado',
                'disponible': False,
            })

    def action_marcar_disponible(self):
        """Marca el libro como disponible."""
        for record in self:
            record.write({
                'estado': 'disponible',
                'disponible': True,
            })

    # =====================================================
    # SOBRESCRITURA DE MÉTODOS CRUD
    # =====================================================

    @api.model_create_multi
    def create(self, vals_list):
        """
        Sobrescribe el método create para agregar lógica personalizada.

        @api.model_create_multi: Indica que vals_list es una lista de diccionarios.
        Esto es más eficiente para crear múltiples registros.
        """
        for vals in vals_list:
            # Ejemplo: Convertir ISBN a mayúsculas
            if vals.get('isbn'):
                vals['isbn'] = vals['isbn'].upper().replace('-', '').replace(' ', '')

        # Llamar al método original
        return super().create(vals_list)

    def write(self, vals):
        """
        Sobrescribe el método write para agregar lógica personalizada.

        self: Recordset con los registros a modificar.
        vals: Diccionario con los campos a actualizar.
        """
        # Ejemplo: Si cambia el estado a disponible, actualizar disponible
        if vals.get('estado') == 'disponible':
            vals['disponible'] = True
        elif vals.get('estado') in ['prestado', 'reservado', 'mantenimiento']:
            vals['disponible'] = False

        return super().write(vals)

    def unlink(self):
        """
        Sobrescribe el método unlink (delete) para agregar validaciones.
        """
        for record in self:
            if record.estado == 'prestado':
                raise ValidationError(
                    f'No se puede eliminar el libro "{record.name}" porque está prestado.'
                )
        return super().unlink()
