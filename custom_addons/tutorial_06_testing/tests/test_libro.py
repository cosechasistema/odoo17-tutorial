# -*- coding: utf-8 -*-
"""
Tests del Modelo Libro - Tutorial 06

Este archivo demuestra cómo escribir tests unitarios en Odoo.

TIPOS DE TESTS EN ODOO:
1. TransactionCase: Cada test en una transacción separada (rollback automático)
2. SingleTransactionCase: Todos los tests comparten una transacción
3. SavepointCase: Similar a TransactionCase pero usa savepoints
4. HttpCase: Para tests que requieren servidor web (tours, UI)

EJECUTAR TESTS:
docker compose exec odoo odoo -d NOMBRE_BD --test-enable -u tutorial_06_testing --stop-after-init

EJECUTAR UN TEST ESPECÍFICO:
docker compose exec odoo odoo -d NOMBRE_BD --test-tags=/tutorial_06_testing.test_libro --stop-after-init
"""

from odoo.tests.common import TransactionCase, tagged
from odoo.exceptions import ValidationError
from datetime import date


@tagged('post_install', '-at_install', 'biblioteca', 'libro')
class TestLibro(TransactionCase):
    """
    Tests para el modelo biblioteca.libro

    @tagged:
    - 'post_install': Ejecutar después de instalar módulos
    - '-at_install': NO ejecutar durante instalación
    - 'biblioteca': Tag personalizado para filtrar
    """

    @classmethod
    def setUpClass(cls):
        """
        Se ejecuta UNA VEZ antes de todos los tests de la clase.
        Ideal para crear datos que se usarán en múltiples tests.

        IMPORTANTE: Llamar siempre a super().setUpClass()
        """
        super().setUpClass()

        # Crear datos de prueba
        cls.Libro = cls.env['biblioteca.libro']

        cls.libro_test = cls.Libro.create({
            'name': 'Libro de Prueba',
            'isbn': '1234567890123',
            'autor': 'Autor Test',
            'paginas': 200,
            'precio': 25.50,
            'estado': 'disponible',
            'disponible': True,
        })

        cls.libro_prestado = cls.Libro.create({
            'name': 'Libro Prestado',
            'isbn': '9876543210123',
            'autor': 'Otro Autor',
            'paginas': 150,
            'precio': 15.00,
            'estado': 'prestado',
            'disponible': False,
        })

    def test_crear_libro_basico(self):
        """
        Test: Crear un libro con datos básicos.

        Cada método que empieza con test_ es un test.
        """
        libro = self.Libro.create({
            'name': 'Nuevo Libro',
            'autor': 'Nuevo Autor',
        })

        # Assertions
        self.assertTrue(libro.exists(), "El libro debe existir")
        self.assertEqual(libro.name, 'Nuevo Libro')
        self.assertEqual(libro.estado, 'disponible', "Estado default debe ser 'disponible'")
        self.assertTrue(libro.disponible, "Debe estar disponible por defecto")

    def test_isbn_unico(self):
        """
        Test: No se pueden crear dos libros con el mismo ISBN.
        """
        with self.assertRaises(Exception):  # Puede ser IntegrityError o ValidationError
            self.Libro.create({
                'name': 'Libro Duplicado',
                'isbn': '1234567890123',  # ISBN ya existe en libro_test
            })

    def test_isbn_formato(self):
        """
        Test: El ISBN debe tener 10 o 13 dígitos.
        """
        with self.assertRaises(ValidationError):
            self.Libro.create({
                'name': 'ISBN Inválido',
                'isbn': '12345',  # Solo 5 dígitos
            })

    def test_accion_prestar(self):
        """
        Test: La acción de marcar prestado funciona correctamente.
        """
        libro = self.libro_test

        # Verificar estado inicial
        self.assertEqual(libro.estado, 'disponible')
        self.assertTrue(libro.disponible)

        # Ejecutar acción
        libro.action_marcar_prestado()

        # Verificar cambios
        self.assertEqual(libro.estado, 'prestado')
        self.assertFalse(libro.disponible)

    def test_accion_disponible(self):
        """
        Test: La acción de marcar disponible funciona correctamente.
        """
        libro = self.libro_prestado

        # Ejecutar acción
        libro.action_marcar_disponible()

        # Verificar cambios
        self.assertEqual(libro.estado, 'disponible')
        self.assertTrue(libro.disponible)

    def test_no_eliminar_prestado(self):
        """
        Test: No se puede eliminar un libro prestado.
        """
        libro = self.libro_prestado

        with self.assertRaises(ValidationError) as context:
            libro.unlink()

        # Verificar mensaje de error
        self.assertIn('prestado', str(context.exception).lower())

    def test_buscar_por_autor(self):
        """
        Test: Buscar libros por autor.
        """
        libros = self.Libro.search([('autor', 'ilike', 'Test')])

        self.assertGreaterEqual(len(libros), 1)
        self.assertIn(self.libro_test, libros)

    def test_campos_calculados(self):
        """
        Test: Verificar que los campos calculados funcionan.

        NOTA: Este test asume que el módulo tutorial_02_relaciones está instalado.
        """
        # Verificar que el conteo de préstamos existe y es un número
        if hasattr(self.libro_test, 'prestamo_count'):
            self.assertIsInstance(self.libro_test.prestamo_count, int)

    def test_write_actualiza_disponible(self):
        """
        Test: Al cambiar estado, se actualiza automáticamente disponible.
        """
        libro = self.Libro.create({
            'name': 'Test Write',
            'estado': 'disponible',
        })

        self.assertTrue(libro.disponible)

        libro.write({'estado': 'prestado'})
        self.assertFalse(libro.disponible)

        libro.write({'estado': 'disponible'})
        self.assertTrue(libro.disponible)

    def test_paginas_positivas(self):
        """
        Test: El número de páginas no puede ser negativo.
        """
        # La constraint SQL debería prevenir esto
        with self.assertRaises(Exception):
            self.Libro.create({
                'name': 'Páginas Negativas',
                'paginas': -10,
            })


@tagged('post_install', '-at_install', 'biblioteca')
class TestLibroSearch(TransactionCase):
    """Tests específicos para búsquedas."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Libro = cls.env['biblioteca.libro']

        # Crear varios libros para tests de búsqueda
        cls.libros = cls.Libro.create([
            {'name': 'Python Básico', 'autor': 'Juan', 'paginas': 100},
            {'name': 'Python Avanzado', 'autor': 'María', 'paginas': 300},
            {'name': 'JavaScript', 'autor': 'Pedro', 'paginas': 200},
        ])

    def test_search_count(self):
        """Test: search_count devuelve el número correcto."""
        count = self.Libro.search_count([('name', 'ilike', 'Python')])
        self.assertGreaterEqual(count, 2)

    def test_search_limit(self):
        """Test: search respeta el límite."""
        libros = self.Libro.search([], limit=2)
        self.assertLessEqual(len(libros), 2)

    def test_search_order(self):
        """Test: search respeta el ordenamiento."""
        libros = self.Libro.search([('name', 'ilike', 'Python')], order='paginas asc')

        if len(libros) >= 2:
            self.assertLessEqual(libros[0].paginas, libros[1].paginas)

    def test_mapped(self):
        """Test: mapped extrae valores correctamente."""
        nombres = self.libros.mapped('name')
        self.assertIn('Python Básico', nombres)
        self.assertIn('JavaScript', nombres)

    def test_filtered(self):
        """Test: filtered funciona correctamente."""
        grandes = self.libros.filtered(lambda l: l.paginas > 150)
        self.assertGreaterEqual(len(grandes), 2)

    def test_sorted(self):
        """Test: sorted ordena correctamente."""
        ordenados = self.libros.sorted('paginas')
        for i in range(len(ordenados) - 1):
            self.assertLessEqual(ordenados[i].paginas, ordenados[i+1].paginas)
