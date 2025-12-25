# -*- coding: utf-8 -*-
"""
API REST de Biblioteca - Tutorial 05

Para desarrolladores que vienen de Node.js/Express, este archivo
muestra cómo crear endpoints REST en Odoo.

COMPARACIÓN CON EXPRESS:

Express:
    app.get('/api/libros', (req, res) => { ... })
    app.post('/api/libros', (req, res) => { ... })

Odoo:
    @http.route('/api/libros', type='json', auth='user', methods=['GET'])
    def get_libros(self, **kw): ...

TIPOS DE RUTAS:
- type='http': Respuesta HTML, redirect, archivos
- type='json': Respuesta JSON (usa JSON-RPC internamente)

AUTENTICACIÓN:
- auth='public': Sin autenticación
- auth='user': Requiere sesión de usuario
- auth='none': Sin usuario ni base de datos
"""

from odoo import http
from odoo.http import request, Response
import json
import logging

_logger = logging.getLogger(__name__)


class BibliotecaAPI(http.Controller):
    """
    Controlador REST para la biblioteca.

    Rutas disponibles:
    - GET  /api/biblioteca/libros - Listar todos los libros
    - GET  /api/biblioteca/libro/<id> - Obtener un libro
    - POST /api/biblioteca/libro - Crear libro
    - PUT  /api/biblioteca/libro/<id> - Actualizar libro
    - DELETE /api/biblioteca/libro/<id> - Eliminar libro
    """

    # =====================================================
    # HELPERS
    # =====================================================

    def _response_json(self, data, status=200):
        """
        Helper para crear respuestas JSON.

        En Odoo, las rutas type='json' ya devuelven JSON automáticamente.
        Este helper es para rutas type='http' que quieren devolver JSON.
        """
        return Response(
            json.dumps(data),
            status=status,
            headers=[('Content-Type', 'application/json')],
        )

    def _libro_to_dict(self, libro):
        """Convierte un registro de libro a diccionario."""
        return {
            'id': libro.id,
            'name': libro.name,
            'isbn': libro.isbn,
            'autor': libro.autor,
            'editorial': libro.editorial,
            'fecha_publicacion': str(libro.fecha_publicacion) if libro.fecha_publicacion else None,
            'paginas': libro.paginas,
            'precio': libro.precio,
            'disponible': libro.disponible,
            'estado': libro.estado,
        }

    # =====================================================
    # ENDPOINTS PÚBLICOS (sin autenticación)
    # =====================================================

    @http.route(
        '/api/biblioteca/public/libros',
        type='http',
        auth='public',
        methods=['GET'],
        csrf=False,  # Deshabilitar CSRF para APIs públicas
    )
    def get_libros_public(self, **kwargs):
        """
        GET /api/biblioteca/public/libros
        Lista libros disponibles (público, sin autenticación).

        Query params:
        - limit: número máximo de resultados (default: 100)
        - offset: página (default: 0)
        - disponible: true/false
        """
        try:
            limit = int(kwargs.get('limit', 100))
            offset = int(kwargs.get('offset', 0))

            domain = []
            if kwargs.get('disponible') == 'true':
                domain.append(('disponible', '=', True))

            libros = request.env['biblioteca.libro'].sudo().search(
                domain, limit=limit, offset=offset
            )

            data = {
                'success': True,
                'count': len(libros),
                'data': [self._libro_to_dict(libro) for libro in libros],
            }

            return self._response_json(data)

        except Exception as e:
            _logger.error(f'Error en API: {e}')
            return self._response_json({
                'success': False,
                'error': str(e),
            }, status=500)

    # =====================================================
    # ENDPOINTS JSON-RPC (requieren autenticación)
    # =====================================================

    @http.route(
        '/api/biblioteca/libros',
        type='json',
        auth='user',
        methods=['POST'],
    )
    def get_libros(self, domain=None, limit=100, offset=0, order='name'):
        """
        POST /api/biblioteca/libros (JSON-RPC)
        Lista libros con filtros.

        Body JSON:
        {
            "jsonrpc": "2.0",
            "method": "call",
            "params": {
                "domain": [["disponible", "=", true]],
                "limit": 10,
                "order": "name"
            },
            "id": 1
        }
        """
        domain = domain or []
        libros = request.env['biblioteca.libro'].search(
            domain, limit=limit, offset=offset, order=order
        )

        return {
            'count': len(libros),
            'data': [self._libro_to_dict(libro) for libro in libros],
        }

    @http.route(
        '/api/biblioteca/libro/<int:libro_id>',
        type='json',
        auth='user',
        methods=['POST'],
    )
    def get_libro(self, libro_id, **kwargs):
        """
        GET /api/biblioteca/libro/<id> (via JSON-RPC POST)
        Obtiene un libro por ID.
        """
        libro = request.env['biblioteca.libro'].browse(libro_id)

        if not libro.exists():
            return {'error': 'Libro no encontrado', 'id': libro_id}

        return self._libro_to_dict(libro)

    @http.route(
        '/api/biblioteca/libro/create',
        type='json',
        auth='user',
        methods=['POST'],
    )
    def create_libro(self, **kwargs):
        """
        POST /api/biblioteca/libro/create
        Crea un nuevo libro.

        Body JSON (params):
        {
            "name": "Título del libro",
            "isbn": "1234567890",
            "autor": "Nombre del autor",
            ...
        }
        """
        required_fields = ['name']
        for field in required_fields:
            if not kwargs.get(field):
                return {'error': f'Campo requerido: {field}'}

        try:
            # Filtrar solo campos válidos del modelo
            valid_fields = ['name', 'isbn', 'autor', 'editorial',
                           'fecha_publicacion', 'paginas', 'precio',
                           'descripcion', 'disponible', 'estado']

            vals = {k: v for k, v in kwargs.items() if k in valid_fields}

            libro = request.env['biblioteca.libro'].create(vals)

            return {
                'success': True,
                'id': libro.id,
                'message': f'Libro "{libro.name}" creado correctamente',
            }

        except Exception as e:
            _logger.error(f'Error creando libro: {e}')
            return {'error': str(e)}

    @http.route(
        '/api/biblioteca/libro/update/<int:libro_id>',
        type='json',
        auth='user',
        methods=['POST'],
    )
    def update_libro(self, libro_id, **kwargs):
        """
        PUT /api/biblioteca/libro/update/<id>
        Actualiza un libro existente.
        """
        libro = request.env['biblioteca.libro'].browse(libro_id)

        if not libro.exists():
            return {'error': 'Libro no encontrado', 'id': libro_id}

        try:
            valid_fields = ['name', 'isbn', 'autor', 'editorial',
                           'fecha_publicacion', 'paginas', 'precio',
                           'descripcion', 'disponible', 'estado']

            vals = {k: v for k, v in kwargs.items() if k in valid_fields}

            libro.write(vals)

            return {
                'success': True,
                'id': libro.id,
                'message': 'Libro actualizado correctamente',
            }

        except Exception as e:
            return {'error': str(e)}

    @http.route(
        '/api/biblioteca/libro/delete/<int:libro_id>',
        type='json',
        auth='user',
        methods=['POST'],
    )
    def delete_libro(self, libro_id, **kwargs):
        """
        DELETE /api/biblioteca/libro/delete/<id>
        Elimina un libro.
        """
        libro = request.env['biblioteca.libro'].browse(libro_id)

        if not libro.exists():
            return {'error': 'Libro no encontrado', 'id': libro_id}

        try:
            nombre = libro.name
            libro.unlink()

            return {
                'success': True,
                'message': f'Libro "{nombre}" eliminado correctamente',
            }

        except Exception as e:
            return {'error': str(e)}

    # =====================================================
    # ENDPOINTS REST PUROS (HTTP)
    # =====================================================

    @http.route(
        '/api/v2/libros',
        type='http',
        auth='user',
        methods=['GET'],
        csrf=False,
    )
    def rest_get_libros(self, **kwargs):
        """
        GET /api/v2/libros
        Endpoint REST puro (sin JSON-RPC).

        Headers requeridos:
        - Cookie con sesión de Odoo

        Query params:
        - search: término de búsqueda
        - estado: disponible|prestado|reservado
        - limit: número máximo
        """
        try:
            domain = []

            if kwargs.get('search'):
                domain.append(('name', 'ilike', kwargs['search']))

            if kwargs.get('estado'):
                domain.append(('estado', '=', kwargs['estado']))

            limit = int(kwargs.get('limit', 50))

            libros = request.env['biblioteca.libro'].search(domain, limit=limit)

            return self._response_json({
                'success': True,
                'count': len(libros),
                'results': [self._libro_to_dict(l) for l in libros],
            })

        except Exception as e:
            return self._response_json({
                'success': False,
                'error': str(e),
            }, status=500)

    @http.route(
        '/api/v2/libro/<int:libro_id>',
        type='http',
        auth='user',
        methods=['GET'],
        csrf=False,
    )
    def rest_get_libro(self, libro_id, **kwargs):
        """GET /api/v2/libro/<id>"""
        libro = request.env['biblioteca.libro'].browse(libro_id)

        if not libro.exists():
            return self._response_json({
                'success': False,
                'error': 'Libro no encontrado',
            }, status=404)

        return self._response_json({
            'success': True,
            'data': self._libro_to_dict(libro),
        })

    # =====================================================
    # DOCUMENTACIÓN
    # =====================================================

    @http.route(
        '/api/biblioteca',
        type='http',
        auth='public',
    )
    def api_docs(self, **kwargs):
        """
        GET /api/biblioteca
        Documentación de la API.
        """
        docs = """
        <html>
        <head><title>API Biblioteca</title></head>
        <body>
        <h1>API Biblioteca - Documentación</h1>

        <h2>Endpoints Públicos</h2>
        <ul>
            <li><code>GET /api/biblioteca/public/libros</code> - Listar libros</li>
        </ul>

        <h2>Endpoints Autenticados (JSON-RPC)</h2>
        <ul>
            <li><code>POST /api/biblioteca/libros</code> - Listar con filtros</li>
            <li><code>POST /api/biblioteca/libro/&lt;id&gt;</code> - Obtener libro</li>
            <li><code>POST /api/biblioteca/libro/create</code> - Crear libro</li>
            <li><code>POST /api/biblioteca/libro/update/&lt;id&gt;</code> - Actualizar</li>
            <li><code>POST /api/biblioteca/libro/delete/&lt;id&gt;</code> - Eliminar</li>
        </ul>

        <h2>Endpoints REST</h2>
        <ul>
            <li><code>GET /api/v2/libros</code> - Listar libros</li>
            <li><code>GET /api/v2/libro/&lt;id&gt;</code> - Obtener libro</li>
        </ul>

        <h2>Autenticación</h2>
        <p>Para endpoints autenticados, primero obtén una sesión:</p>
        <pre>
POST /web/session/authenticate
{
    "jsonrpc": "2.0",
    "params": {
        "db": "nombre_bd",
        "login": "usuario",
        "password": "contraseña"
    }
}
        </pre>
        </body>
        </html>
        """
        return docs
