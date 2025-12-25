# Odoo 17 - Entorno de Desarrollo y Aprendizaje

Entorno completo para aprender a desarrollar módulos en Odoo 17 usando Docker. Incluye documentación en español, 6 módulos de tutorial progresivos y scripts de utilidad.

## Requisitos Previos

- **Docker** y **Docker Compose** instalados
- **Git** instalado
- 4GB de RAM mínimo recomendado

### Verificar instalación

```bash
docker --version        # Docker version 20.x o superior
docker compose version  # Docker Compose version v2.x
git --version          # git version 2.x
```

## Inicio Rápido

### 1. Clonar el repositorio

```bash
git clone https://github.com/cosechasistema/odoo17-tutorial.git
cd odoo17-tutorial
```

### 2. Dar permisos a los módulos

```bash
chmod -R 755 custom_addons/
```

### 3. Iniciar los servicios

```bash
docker compose up -d
```

Esto iniciará:
- **Odoo 17** en http://localhost:8070
- **PostgreSQL 15** en localhost:5433
- **pgAdmin 4** en http://localhost:5050

### 4. Crear la base de datos

1. Abre http://localhost:8070
2. Completa el formulario:
   - **Master Password**: `admin`
   - **Database Name**: `odoo_dev` (o el nombre que prefieras)
   - **Email**: tu email
   - **Password**: tu contraseña
   - **Language**: Spanish (AR) o tu preferencia
3. Click en "Create database"

### 5. Instalar el primer módulo tutorial

```bash
docker compose exec odoo odoo -d odoo_dev -i tutorial_01_basico --stop-after-init
```

### 6. Acceder a Odoo

1. Abre http://localhost:8070
2. Inicia sesión con el email y contraseña que creaste
3. Ve al menú **Biblioteca** para ver el módulo instalado

## Estructura del Proyecto

```
odoo17-tutorial/
├── config/
│   └── odoo.conf              # Configuración de Odoo
├── custom_addons/             # Tus módulos personalizados
│   ├── tutorial_01_basico/    # CRUD básico
│   ├── tutorial_02_relaciones/# Relaciones entre modelos
│   ├── tutorial_03_computed/  # Campos calculados
│   ├── tutorial_04_herencia/  # Herencia de modelos
│   ├── tutorial_05_api_rest/  # APIs REST
│   └── tutorial_06_testing/   # Tests unitarios
├── docs/                      # Documentación detallada
├── scripts/                   # Scripts de utilidad
├── docker-compose.yml         # Configuración Docker
└── README.md                  # Este archivo
```

## Módulos de Tutorial

Los módulos están diseñados para seguirse en orden:

| # | Módulo | Aprenderás |
|---|--------|------------|
| 1 | `tutorial_01_basico` | Modelos, campos, vistas form/tree/search, menús |
| 2 | `tutorial_02_relaciones` | Many2one, One2many, Many2many, herencia |
| 3 | `tutorial_03_computed` | @api.depends, @api.onchange, @api.constrains |
| 4 | `tutorial_04_herencia` | Extender modelos existentes, herencia de vistas |
| 5 | `tutorial_05_api_rest` | Controladores HTTP, endpoints JSON |
| 6 | `tutorial_06_testing` | Tests unitarios con TransactionCase |

### Instalar módulos

```bash
# Instalar un módulo
docker compose exec odoo odoo -d odoo_dev -i nombre_modulo --stop-after-init

# Instalar varios módulos
docker compose exec odoo odoo -d odoo_dev -i tutorial_01_basico,tutorial_02_relaciones --stop-after-init

# Actualizar un módulo después de cambios
docker compose exec odoo odoo -d odoo_dev -u nombre_modulo --stop-after-init
```

## Comandos Útiles

### Docker

```bash
# Iniciar servicios
docker compose up -d

# Detener servicios
docker compose down

# Ver logs de Odoo
docker compose logs -f odoo

# Reiniciar Odoo (después de cambiar código Python)
docker compose restart odoo

# Ver estado de servicios
docker compose ps
```

### Scripts incluidos

```bash
# Actualizar módulo
./scripts/update_module.sh odoo_dev nombre_modulo

# Ejecutar tests
./scripts/run_tests.sh odoo_dev nombre_modulo

# Abrir shell de Odoo
./scripts/odoo_shell.sh odoo_dev

# Crear nuevo módulo
./scripts/create_module.sh mi_nuevo_modulo
```

### Shell de Odoo

```bash
docker compose exec odoo odoo shell -d odoo_dev
```

```python
# Dentro del shell
>>> env['biblioteca.libro'].search([])
>>> env['res.partner'].create({'name': 'Test'})
>>> env.cr.commit()  # Guardar cambios
>>> exit()
```

## Accesos

| Servicio | URL | Credenciales |
|----------|-----|--------------|
| Odoo | http://localhost:8070 | Las que creaste |
| pgAdmin | http://localhost:5050 | admin@local.dev / admin |
| PostgreSQL | localhost:5433 | odoo / odoo |

### Configurar pgAdmin

1. Abre http://localhost:5050
2. Login: `admin@local.dev` / `admin`
3. Click derecho en "Servers" → "Register" → "Server"
4. General → Name: `Odoo Dev`
5. Connection:
   - Host: `db`
   - Port: `5432`
   - Username: `odoo`
   - Password: `odoo`
6. Save

## Crear tu Propio Módulo

### Opción 1: Usar el script

```bash
./scripts/create_module.sh mi_modulo
```

### Opción 2: Manual

```bash
mkdir -p custom_addons/mi_modulo/{models,views,security}
```

Estructura mínima:
```
mi_modulo/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   └── mi_modelo.py
├── views/
│   └── mi_modelo_views.xml
└── security/
    └── ir.model.access.csv
```

Ver ejemplos en `custom_addons/tutorial_01_basico/`

## Documentación

| Documento | Descripción |
|-----------|-------------|
| [COMO_USAR_ODOO.md](docs/COMO_USAR_ODOO.md) | Guía para principiantes - Cómo usar módulos |
| [GUIA_DESARROLLO.md](docs/GUIA_DESARROLLO.md) | Guía completa de desarrollo Odoo |
| [ORM_PARA_DESARROLLADORES_SQL.md](docs/ORM_PARA_DESARROLLADORES_SQL.md) | Transición de SQL/MySQL a Odoo ORM |
| [COMANDOS_REFERENCIA.md](docs/COMANDOS_REFERENCIA.md) | Referencia de comandos Docker y Odoo |
| [CONFIGURAR_MCP.md](docs/CONFIGURAR_MCP.md) | Configurar MCP PostgreSQL para Claude Code |

## Flujo de Desarrollo Recomendado

1. **Edita** los archivos Python/XML en `custom_addons/`
2. **Reinicia** Odoo si cambiaste Python:
   ```bash
   docker compose restart odoo
   ```
3. **Actualiza** el módulo:
   ```bash
   docker compose exec odoo odoo -d odoo_dev -u mi_modulo --stop-after-init
   ```
4. **Verifica** en el navegador http://localhost:8070

> **Tip**: Con `dev_mode = reload` en odoo.conf, Odoo reinicia automáticamente al detectar cambios en Python.

## Troubleshooting

### Error de permisos en módulos

```bash
chmod -R 755 custom_addons/
docker compose restart odoo
```

### Odoo no inicia

```bash
# Ver logs de error
docker compose logs odoo

# Reiniciar todo
docker compose down && docker compose up -d
```

### Base de datos no aparece

```bash
# Verificar que PostgreSQL esté corriendo
docker compose ps

# Ver bases de datos existentes
docker compose exec db psql -U odoo -d postgres -c "\l"
```

### Limpiar y empezar de nuevo

```bash
# CUIDADO: Esto borra TODOS los datos
docker compose down -v
rm -rf postgres_data/
docker compose up -d
```

## Recursos Adicionales

- [Documentación Oficial Odoo 17](https://www.odoo.com/documentation/17.0/)
- [ORM API Reference](https://www.odoo.com/documentation/17.0/developer/reference/backend/orm.html)
- [Views Reference](https://www.odoo.com/documentation/17.0/developer/reference/backend/views.html)
- [Coding Guidelines](https://www.odoo.com/documentation/17.0/contributing/development/coding_guidelines.html)

## Licencia

Este proyecto es para fines educativos. Los módulos de ejemplo están bajo licencia LGPL-3.

---

Creado con [Claude Code](https://claude.ai/code)
