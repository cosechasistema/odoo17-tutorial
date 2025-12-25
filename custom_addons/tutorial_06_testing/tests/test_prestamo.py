# -*- coding: utf-8 -*-
"""
Tests del Modelo Préstamo - Tutorial 06

Demuestra tests más complejos con relaciones entre modelos.
"""

from odoo.tests.common import TransactionCase, tagged
from odoo.exceptions import ValidationError, UserError
from datetime import date, timedelta


@tagged('post_install', '-at_install', 'biblioteca', 'prestamo')
class TestPrestamo(TransactionCase):
    """Tests para el modelo biblioteca.prestamo"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Modelos
        cls.Libro = cls.env['biblioteca.libro']
        cls.Miembro = cls.env['biblioteca.miembro']
        cls.Prestamo = cls.env['biblioteca.prestamo']
        cls.Partner = cls.env['res.partner']

        # Crear partner para miembro
        cls.partner = cls.Partner.create({
            'name': 'Miembro Test',
            'email': 'miembro@test.com',
        })

        # Crear miembro
        cls.miembro = cls.Miembro.create({
            'partner_id': cls.partner.id,
        })

        # Crear libros
        cls.libro_disponible = cls.Libro.create({
            'name': 'Libro Disponible Test',
            'isbn': '1111111111111',
            'estado': 'disponible',
            'disponible': True,
        })

        cls.libro_otro = cls.Libro.create({
            'name': 'Otro Libro Test',
            'isbn': '2222222222222',
            'estado': 'disponible',
            'disponible': True,
        })

    def test_crear_prestamo(self):
        """Test: Crear un préstamo básico."""
        prestamo = self.Prestamo.create({
            'libro_id': self.libro_disponible.id,
            'miembro_id': self.miembro.id,
        })

        # Verificar que se creó
        self.assertTrue(prestamo.exists())
        self.assertEqual(prestamo.estado, 'activo')

        # Verificar que el libro ahora está prestado
        self.assertEqual(self.libro_disponible.estado, 'prestado')
        self.assertFalse(self.libro_disponible.disponible)

    def test_devolver_libro(self):
        """Test: Devolver un libro prestado."""
        prestamo = self.Prestamo.create({
            'libro_id': self.libro_otro.id,
            'miembro_id': self.miembro.id,
        })

        # Devolver
        prestamo.action_devolver()

        # Verificar estado del préstamo
        self.assertEqual(prestamo.estado, 'devuelto')
        self.assertIsNotNone(prestamo.fecha_devolucion_real)

        # Verificar estado del libro
        self.assertEqual(self.libro_otro.estado, 'disponible')
        self.assertTrue(self.libro_otro.disponible)

    def test_no_eliminar_prestamo_activo(self):
        """Test: No se puede eliminar un préstamo activo."""
        prestamo = self.Prestamo.create({
            'libro_id': self.libro_disponible.id,
            'miembro_id': self.miembro.id,
        })

        with self.assertRaises(UserError):
            prestamo.unlink()

    def test_fecha_devolucion_calculada(self):
        """Test: La fecha de devolución esperada se calcula correctamente."""
        prestamo = self.Prestamo.create({
            'libro_id': self.libro_disponible.id,
            'miembro_id': self.miembro.id,
            'dias_prestamo': 14,
        })

        fecha_esperada = date.today() + timedelta(days=14)
        self.assertEqual(prestamo.fecha_devolucion_esperada, fecha_esperada)

    def test_dias_retraso(self):
        """Test: Cálculo de días de retraso."""
        prestamo = self.Prestamo.create({
            'libro_id': self.libro_disponible.id,
            'miembro_id': self.miembro.id,
            'fecha_prestamo': date.today() - timedelta(days=20),
            'dias_prestamo': 14,
        })

        # Debería tener 6 días de retraso (20 - 14 = 6)
        self.assertGreater(prestamo.dias_retraso, 0)

    def test_relaciones(self):
        """Test: Las relaciones Many2one funcionan correctamente."""
        prestamo = self.Prestamo.create({
            'libro_id': self.libro_disponible.id,
            'miembro_id': self.miembro.id,
        })

        # Verificar acceso a campos relacionados
        self.assertEqual(prestamo.libro_titulo, self.libro_disponible.name)
        self.assertEqual(prestamo.miembro_nombre, self.miembro.name)

    def test_miembro_prestamo_count(self):
        """Test: El miembro refleja correctamente sus préstamos."""
        # Crear préstamo
        self.Prestamo.create({
            'libro_id': self.libro_disponible.id,
            'miembro_id': self.miembro.id,
        })

        # Verificar que el miembro tiene el préstamo
        self.assertGreaterEqual(self.miembro.prestamo_count, 1)
        self.assertGreaterEqual(self.miembro.prestamos_activos, 1)


@tagged('post_install', '-at_install', 'biblioteca', 'integracion')
class TestIntegracionBiblioteca(TransactionCase):
    """
    Tests de integración que prueban flujos completos.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.Libro = cls.env['biblioteca.libro']
        cls.Miembro = cls.env['biblioteca.miembro']
        cls.Prestamo = cls.env['biblioteca.prestamo']
        cls.Partner = cls.env['res.partner']

    def test_flujo_completo_prestamo(self):
        """
        Test de integración: Flujo completo de préstamo y devolución.

        1. Crear libro
        2. Crear miembro
        3. Crear préstamo
        4. Verificar estados
        5. Devolver libro
        6. Verificar estados finales
        """
        # 1. Crear libro
        libro = self.Libro.create({
            'name': 'Libro Flujo Completo',
            'isbn': '3333333333333',
            'precio': 30.0,
        })
        self.assertEqual(libro.estado, 'disponible')

        # 2. Crear miembro
        partner = self.Partner.create({'name': 'Usuario Flujo'})
        miembro = self.Miembro.create({'partner_id': partner.id})
        self.assertTrue(miembro.activo)

        # 3. Crear préstamo
        prestamo = self.Prestamo.create({
            'libro_id': libro.id,
            'miembro_id': miembro.id,
        })

        # 4. Verificar estados después del préstamo
        self.assertEqual(prestamo.estado, 'activo')
        self.assertEqual(libro.estado, 'prestado')
        self.assertFalse(libro.disponible)
        self.assertEqual(miembro.prestamos_activos, 1)

        # 5. Devolver libro
        prestamo.action_devolver()

        # 6. Verificar estados finales
        self.assertEqual(prestamo.estado, 'devuelto')
        self.assertEqual(libro.estado, 'disponible')
        self.assertTrue(libro.disponible)

        # El miembro ya no tiene préstamos activos
        # Forzar recálculo
        miembro.invalidate_recordset(['prestamos_activos'])
        self.assertEqual(miembro.prestamos_activos, 0)

    def test_multiple_prestamos_miembro(self):
        """
        Test: Un miembro puede tener múltiples préstamos.
        """
        # Crear miembro
        partner = self.Partner.create({'name': 'Multi Prestamos'})
        miembro = self.Miembro.create({'partner_id': partner.id})

        # Crear 3 libros y 3 préstamos
        for i in range(3):
            libro = self.Libro.create({
                'name': f'Libro Multi {i}',
                'isbn': f'444444444444{i}',
            })
            self.Prestamo.create({
                'libro_id': libro.id,
                'miembro_id': miembro.id,
            })

        # Verificar
        miembro.invalidate_recordset(['prestamos_activos', 'prestamo_count'])
        self.assertEqual(miembro.prestamos_activos, 3)
        self.assertEqual(miembro.prestamo_count, 3)
