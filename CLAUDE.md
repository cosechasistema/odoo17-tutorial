# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Descripción del Proyecto

Entorno de desarrollo y aprendizaje de Odoo 17 usando Docker Compose. Incluye PostgreSQL 15, pgAdmin, y 6 módulos de tutorial progresivos.

## Arquitectura

```
odoo17-dev/
├── config/odoo.conf          # Configuración de Odoo
├── custom_addons/            # Módulos personalizados
│   ├── tutorial_01_basico/   # CRUD básico (biblioteca de libros)
│   ├── tutorial_02_relaciones/ # Many2one, One2many, Many2many
│   ├── tutorial_03_computed/   # Campos calculados, onchange, constraints
│   ├── tutorial_04_herencia/   # _inherit, _inherits, herencia de vistas
│   ├── tutorial_05_api_rest/   # Controladores HTTP y REST
│   └── tutorial_06_testing/    # Tests unitarios y de integración
├── docs/                     # Documentación detallada
├── scripts/                  # Scripts de utilidad
└── docker-compose.yml        # Servicios Docker
```

## Servicios

| Servicio | Puerto | Descripción |
|----------|--------|-------------|
| Odoo | 8070 | Aplicación web (http://localhost:8070) |
| PostgreSQL | 5433 | Base de datos (expuesto para MCP) |
| pgAdmin | 5050 | Administrador BD (http://localhost:5050) |

## Comandos Esenciales

```bash
# Iniciar servicios
docker compose up -d

# Ver logs de Odoo
docker compose logs -f odoo

# Reiniciar Odoo (después de cambiar código Python)
docker compose restart odoo

# Actualizar un módulo
docker compose exec odoo odoo -d NOMBRE_BD -u nombre_modulo --stop-after-init

# Shell de Odoo
docker compose exec odoo odoo shell -d NOMBRE_BD

# Ejecutar tests
docker compose exec odoo odoo -d NOMBRE_BD --test-enable -u modulo --stop-after-init
```

## Scripts de Utilidad

```bash
./scripts/update_module.sh NOMBRE_BD nombre_modulo  # Actualizar módulo
./scripts/run_tests.sh NOMBRE_BD nombre_modulo      # Ejecutar tests
./scripts/odoo_shell.sh NOMBRE_BD                   # Abrir shell
./scripts/create_module.sh nombre_modulo            # Crear módulo nuevo
```

## Módulos de Tutorial

Los módulos están diseñados para aprenderse en orden:

1. **tutorial_01_basico**: Modelo, campos, vistas form/tree/search, menús
2. **tutorial_02_relaciones**: Many2one, One2many, Many2many, herencia de modelo
3. **tutorial_03_computed**: @api.depends, @api.onchange, @api.constrains
4. **tutorial_04_herencia**: Extender res.partner, herencia de vistas XML
5. **tutorial_05_api_rest**: Controladores HTTP, endpoints JSON
6. **tutorial_06_testing**: TransactionCase, fixtures, assertions

## ORM de Odoo - Referencia Rápida

```python
# Buscar registros
registros = self.env['modelo'].search([('campo', '=', valor)])

# Obtener por ID
registro = self.env['modelo'].browse(id)

# Crear
nuevo = self.env['modelo'].create({'campo': valor})

# Actualizar
registro.write({'campo': nuevo_valor})

# Eliminar
registro.unlink()

# Métodos de recordset
nombres = registros.mapped('name')
activos = registros.filtered(lambda r: r.activo)
ordenados = registros.sorted('name')
```

## Estructura de un Módulo

```
mi_modulo/
├── __init__.py              # from . import models
├── __manifest__.py          # Metadatos del módulo
├── models/
│   ├── __init__.py          # from . import mi_modelo
│   └── mi_modelo.py         # class MiModelo(models.Model)
├── views/
│   ├── mi_modelo_views.xml  # form, tree, search
│   └── menu_views.xml       # acciones y menús
├── security/
│   └── ir.model.access.csv  # permisos
└── data/
    └── datos.xml            # datos iniciales
```

## Credenciales Desarrollo

| Servicio | Usuario | Contraseña |
|----------|---------|------------|
| Odoo Master | - | admin |
| PostgreSQL | odoo | odoo |
| pgAdmin | admin@local.dev | admin |

## Documentación

- `docs/GUIA_DESARROLLO.md` - Guía completa de desarrollo Odoo
- `docs/ORM_PARA_DESARROLLADORES_SQL.md` - Comparativa ORM vs SQL
- `docs/COMANDOS_REFERENCIA.md` - Comandos Docker y Odoo
