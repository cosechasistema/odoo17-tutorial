# Referencia de Comandos - Odoo 17 con Docker

## Índice
1. [Comandos Docker Compose](#1-comandos-docker-compose)
2. [Gestión de Módulos](#2-gestión-de-módulos)
3. [Base de Datos](#3-base-de-datos)
4. [Shell de Odoo](#4-shell-de-odoo)
5. [Logs y Debug](#5-logs-y-debug)
6. [Testing](#6-testing)
7. [pgAdmin](#7-pgadmin)

---

## 1. Comandos Docker Compose

### Iniciar Servicios

```bash
# Iniciar todos los servicios en segundo plano
docker compose up -d

# Iniciar y ver logs en tiempo real
docker compose up

# Iniciar solo un servicio específico
docker compose up -d odoo
docker compose up -d db
docker compose up -d pgadmin
```

### Detener Servicios

```bash
# Detener todos los servicios
docker compose down

# Detener y eliminar volúmenes (CUIDADO: borra datos)
docker compose down -v

# Detener un servicio específico
docker compose stop odoo
```

### Reiniciar

```bash
# Reiniciar todos los servicios
docker compose restart

# Reiniciar solo Odoo (útil después de cambiar código Python)
docker compose restart odoo
```

### Ver Estado

```bash
# Ver estado de contenedores
docker compose ps

# Ver uso de recursos
docker stats
```

### Reconstruir

```bash
# Reconstruir imágenes (si modificaste Dockerfile)
docker compose build

# Forzar reconstrucción sin caché
docker compose build --no-cache

# Recrear contenedores
docker compose up -d --force-recreate
```

---

## 2. Gestión de Módulos

### Actualizar un Módulo

```bash
# Actualizar módulo específico
docker compose exec odoo odoo -d NOMBRE_BD -u nombre_modulo --stop-after-init

# Actualizar múltiples módulos
docker compose exec odoo odoo -d NOMBRE_BD -u modulo1,modulo2 --stop-after-init

# Actualizar todos los módulos instalados
docker compose exec odoo odoo -d NOMBRE_BD -u all --stop-after-init
```

### Instalar un Módulo

```bash
# Instalar módulo (primero debe aparecer en lista de Apps)
docker compose exec odoo odoo -d NOMBRE_BD -i nombre_modulo --stop-after-init
```

### Verificar Addons Path

```bash
# Ver la configuración actual
docker compose exec odoo cat /etc/odoo/odoo.conf

# Listar módulos disponibles en extra-addons
docker compose exec odoo ls -la /mnt/extra-addons
```

---

## 3. Base de Datos

### Acceso Directo a PostgreSQL

```bash
# Conectar a PostgreSQL
docker compose exec db psql -U odoo -d postgres

# Listar bases de datos
docker compose exec db psql -U odoo -d postgres -c "\l"

# Conectar a una base de datos específica
docker compose exec db psql -U odoo -d NOMBRE_BD
```

### Comandos SQL Útiles

```sql
-- Listar tablas de Odoo
\dt ir_*

-- Ver estructura de una tabla
\d res_partner

-- Contar registros
SELECT COUNT(*) FROM res_partner;

-- Salir
\q
```

### Backup y Restore

```bash
# Backup de base de datos
docker compose exec db pg_dump -U odoo NOMBRE_BD > backup.sql

# Backup con compresión
docker compose exec db pg_dump -U odoo -Fc NOMBRE_BD > backup.dump

# Restore
docker compose exec -T db psql -U odoo NOMBRE_BD < backup.sql

# Restore desde dump comprimido
docker compose exec db pg_restore -U odoo -d NOMBRE_BD backup.dump
```

### Crear/Eliminar Base de Datos

```bash
# Crear nueva base de datos
docker compose exec db createdb -U odoo NUEVA_BD

# Eliminar base de datos
docker compose exec db dropdb -U odoo NOMBRE_BD
```

---

## 4. Shell de Odoo

### Acceder al Shell Interactivo

```bash
# Shell de Odoo (Python con environment cargado)
docker compose exec odoo odoo shell -d NOMBRE_BD
```

### Ejemplos en el Shell

```python
# Ya tienes 'self' y 'env' disponibles

# Buscar registros
partners = env['res.partner'].search([])
print(len(partners))

# Crear registro
nuevo = env['res.partner'].create({'name': 'Test'})
print(nuevo.id)

# Modificar
nuevo.write({'phone': '123456'})

# Eliminar
nuevo.unlink()

# Commit cambios (IMPORTANTE)
env.cr.commit()

# Salir
exit()
```

---

## 5. Logs y Debug

### Ver Logs

```bash
# Logs de todos los servicios
docker compose logs

# Logs en tiempo real
docker compose logs -f

# Logs de un servicio específico
docker compose logs -f odoo
docker compose logs -f db

# Últimas N líneas
docker compose logs --tail=100 odoo
```

### Niveles de Log

En `config/odoo.conf`:
```ini
log_level = debug      # Máximo detalle
log_level = info       # Normal
log_level = warning    # Solo advertencias y errores
log_level = error      # Solo errores
```

### Debug con Breakpoints

```python
# En tu código Python, agregar:
import pdb; pdb.set_trace()

# O para web:
import wdb; wdb.set_trace()
```

### Ver Queries SQL

```python
# En el shell o código:
import logging
logging.getLogger('odoo.sql_db').setLevel(logging.DEBUG)
```

---

## 6. Testing

### Ejecutar Tests de un Módulo

```bash
# Tests de un módulo específico
docker compose exec odoo odoo \
    -d NOMBRE_BD \
    -u nombre_modulo \
    --test-enable \
    --stop-after-init

# Solo tests, sin actualizar módulo
docker compose exec odoo odoo \
    -d NOMBRE_BD \
    --test-tags=/nombre_modulo \
    --stop-after-init
```

### Ejecutar un Test Específico

```bash
# Archivo de test específico
docker compose exec odoo odoo \
    -d NOMBRE_BD \
    --test-file=/mnt/extra-addons/mi_modulo/tests/test_mi_modelo.py \
    --stop-after-init
```

### Tags de Tests

```python
# En el archivo de test:
from odoo.tests import tagged

@tagged('post_install', '-at_install', 'mi_tag')
class TestMiModelo(TransactionCase):
    pass
```

```bash
# Ejecutar por tag
docker compose exec odoo odoo -d NOMBRE_BD --test-tags=mi_tag --stop-after-init
```

---

## 7. pgAdmin

### Acceso

- **URL**: http://localhost:5050
- **Email**: admin@local.dev
- **Password**: admin

### Configurar Conexión al Servidor

1. Click derecho en "Servers" → "Register" → "Server"
2. Pestaña "General":
   - Name: `Odoo 17 Dev`
3. Pestaña "Connection":
   - Host: `db` (nombre del servicio Docker)
   - Port: `5432`
   - Username: `odoo`
   - Password: `odoo`
4. Guardar

### Consultas Útiles en pgAdmin

```sql
-- Ver módulos instalados
SELECT name, state, latest_version
FROM ir_module_module
WHERE state = 'installed'
ORDER BY name;

-- Ver usuarios
SELECT id, login, name
FROM res_users
WHERE active = true;

-- Ver compañías
SELECT id, name
FROM res_company;

-- Estadísticas de tablas
SELECT
    schemaname,
    relname as tabla,
    n_live_tup as filas
FROM pg_stat_user_tables
ORDER BY n_live_tup DESC
LIMIT 20;
```

---

## Troubleshooting

### Odoo no inicia

```bash
# Ver logs de error
docker compose logs odoo

# Verificar que PostgreSQL esté healthy
docker compose ps

# Reiniciar todo
docker compose down && docker compose up -d
```

### Error de permisos en custom_addons (PermissionError)

**Síntoma:** Odoo muestra error 500 y en los logs aparece:
```
PermissionError: [Errno 13] Permission denied: '/mnt/extra-addons/mi_modulo/__manifest__.py'
```

**Causa:** Los archivos del módulo no tienen permisos de lectura para el usuario del contenedor Docker (normalmente UID 101 o 1000).

**Solución:**
```bash
# Opción 1: Dar permisos a todos los módulos
chmod -R 755 custom_addons/

# Opción 2: Dar permisos a un módulo específico
chmod -R 755 custom_addons/nombre_modulo/

# Después reiniciar Odoo
docker compose restart odoo
```

**Prevención:** Cada vez que crees un módulo nuevo (manualmente o con scripts), ejecuta:
```bash
chmod -R 755 custom_addons/nuevo_modulo/
```

**Nota para desarrollo:** Si usas un IDE o editor que crea archivos, verifica que los permisos por defecto sean correctos. Puedes agregar esto a tu script de creación de módulos.

### Base de datos no aparece

```bash
# Verificar que existe
docker compose exec db psql -U odoo -c "\l"

# Crear si no existe
docker compose exec db createdb -U odoo nueva_bd
```

### Limpiar todo y empezar de nuevo

```bash
# CUIDADO: Esto borra TODOS los datos
docker compose down -v
rm -rf postgres_data/
docker compose up -d
```

### Cache de assets

```bash
# Limpiar assets (CSS/JS)
docker compose exec odoo odoo -d NOMBRE_BD --dev=all --stop-after-init
```

---

## Atajos Útiles

Agregar a tu `~/.bashrc` o `~/.zshrc`:

```bash
# Aliases para Odoo
alias odoo-up="cd ~/odoo17-dev && docker compose up -d"
alias odoo-down="cd ~/odoo17-dev && docker compose down"
alias odoo-logs="cd ~/odoo17-dev && docker compose logs -f odoo"
alias odoo-restart="cd ~/odoo17-dev && docker compose restart odoo"
alias odoo-shell="cd ~/odoo17-dev && docker compose exec odoo odoo shell -d"
alias odoo-update="cd ~/odoo17-dev && docker compose exec odoo odoo -d"

# Función para actualizar módulo
odoo-u() {
    cd ~/odoo17-dev && docker compose exec odoo odoo -d $1 -u $2 --stop-after-init
}
# Uso: odoo-u nombre_bd nombre_modulo
```
