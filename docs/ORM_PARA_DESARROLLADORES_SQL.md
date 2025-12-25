# ORM de Odoo para Desarrolladores SQL/MySQL

Esta guía está diseñada para desarrolladores con experiencia en bases de datos relacionales (MySQL, PostgreSQL) y desarrollo backend (Node.js, APIs REST) que quieren aprender a usar el ORM de Odoo.

## Índice
1. [Conceptos Fundamentales](#1-conceptos-fundamentales)
2. [Equivalencias SQL ↔ ORM](#2-equivalencias-sql--orm)
3. [CRUD Completo](#3-crud-completo)
4. [JOINs y Relaciones](#4-joins-y-relaciones)
5. [Transacciones](#5-transacciones)
6. [Cuándo Usar SQL Directo](#6-cuándo-usar-sql-directo)
7. [Patrones Comunes](#7-patrones-comunes)
8. [Errores Frecuentes](#8-errores-frecuentes)

---

## 1. Conceptos Fundamentales

### ¿Qué es diferente en Odoo?

| Concepto SQL | Concepto Odoo |
|--------------|---------------|
| Tabla | Modelo (clase Python) |
| Fila/Registro | Record (instancia en un recordset) |
| Columna | Campo (field) |
| Resultado de query | Recordset |
| Connection/Cursor | Environment (self.env) |

### El Recordset

En Odoo, **no trabajas con filas individuales** sino con **recordsets** - colecciones de registros.

```python
# En SQL pensarías:
# cursor.execute("SELECT * FROM usuarios WHERE id = 1")
# row = cursor.fetchone()  # Una fila

# En Odoo:
usuario = self.env['res.users'].browse(1)  # Es un recordset de 1 registro
usuarios = self.env['res.users'].search([])  # Es un recordset de N registros

# IMPORTANTE: Siempre iterar, aunque sea un solo registro
for user in usuario:
    print(user.name)

# O acceder directamente si estás seguro que es uno solo
print(usuario.name)  # Funciona si el recordset tiene exactamente 1 registro
```

### El Environment (self.env)

El `self.env` es tu "conexión" a Odoo. Contiene:

```python
self.env.user        # Usuario actual
self.env.company     # Compañía actual
self.env.context     # Diccionario de contexto
self.env.cr          # Cursor de PostgreSQL (para SQL directo)
self.env.uid         # ID del usuario actual

# Acceder a cualquier modelo
self.env['res.partner']      # Modelo de contactos
self.env['sale.order']       # Modelo de ventas
self.env['mi.modelo']        # Tu modelo personalizado
```

---

## 2. Equivalencias SQL ↔ ORM

### SELECT

```sql
-- SQL
SELECT * FROM res_partner WHERE active = true;
SELECT id, name, email FROM res_partner WHERE country_id = 10;
SELECT * FROM res_partner ORDER BY name ASC LIMIT 10;
SELECT COUNT(*) FROM res_partner WHERE is_company = true;
```

```python
# ORM
partners = self.env['res.partner'].search([('active', '=', True)])
partners = self.env['res.partner'].search([('country_id', '=', 10)])
partners = self.env['res.partner'].search([], order='name asc', limit=10)
count = self.env['res.partner'].search_count([('is_company', '=', True)])

# Leer campos específicos (equivalente a SELECT campo1, campo2)
data = partners.read(['id', 'name', 'email'])  # Lista de diccionarios
```

### INSERT

```sql
-- SQL
INSERT INTO res_partner (name, email, phone)
VALUES ('Juan Pérez', 'juan@email.com', '123456789');
```

```python
# ORM
nuevo_partner = self.env['res.partner'].create({
    'name': 'Juan Pérez',
    'email': 'juan@email.com',
    'phone': '123456789',
})

# El nuevo registro ya tiene su ID asignado
print(nuevo_partner.id)  # Ej: 42
```

### INSERT Múltiple

```sql
-- SQL
INSERT INTO res_partner (name, email) VALUES
    ('Partner 1', 'p1@email.com'),
    ('Partner 2', 'p2@email.com'),
    ('Partner 3', 'p3@email.com');
```

```python
# ORM - Más eficiente que crear uno por uno
nuevos = self.env['res.partner'].create([
    {'name': 'Partner 1', 'email': 'p1@email.com'},
    {'name': 'Partner 2', 'email': 'p2@email.com'},
    {'name': 'Partner 3', 'email': 'p3@email.com'},
])
# nuevos es un recordset con los 3 registros creados
```

### UPDATE

```sql
-- SQL
UPDATE res_partner SET phone = '999999999' WHERE id = 42;
UPDATE res_partner SET active = false WHERE country_id = 10;
```

```python
# ORM - Un registro
partner = self.env['res.partner'].browse(42)
partner.write({'phone': '999999999'})

# ORM - Múltiples registros
partners = self.env['res.partner'].search([('country_id', '=', 10)])
partners.write({'active': False})

# Atajo para un solo campo
partner.phone = '999999999'  # Equivale a write({'phone': '999999999'})
```

### DELETE

```sql
-- SQL
DELETE FROM res_partner WHERE id = 42;
DELETE FROM mi_tabla WHERE fecha < '2024-01-01';
```

```python
# ORM
partner = self.env['res.partner'].browse(42)
partner.unlink()

registros = self.env['mi.tabla'].search([('fecha', '<', '2024-01-01')])
registros.unlink()
```

---

## 3. CRUD Completo

### Ejemplo Práctico: Gestión de Productos

```python
class ProductoController:
    """
    Si vienes de Node.js/Express, esto sería similar a un controlador/servicio.
    En Odoo, esta lógica normalmente va en el modelo.
    """

    def listar_todos(self):
        """GET /productos"""
        return self.env['product.product'].search([])

    def obtener_por_id(self, producto_id):
        """GET /productos/:id"""
        producto = self.env['product.product'].browse(producto_id)
        if not producto.exists():
            return None  # En Odoo normalmente lanzarías una excepción
        return producto

    def crear(self, datos):
        """POST /productos"""
        return self.env['product.product'].create(datos)

    def actualizar(self, producto_id, datos):
        """PUT /productos/:id"""
        producto = self.env['product.product'].browse(producto_id)
        producto.write(datos)
        return producto

    def eliminar(self, producto_id):
        """DELETE /productos/:id"""
        producto = self.env['product.product'].browse(producto_id)
        producto.unlink()
        return True

    def buscar(self, termino):
        """GET /productos?q=termino"""
        return self.env['product.product'].search([
            '|',  # OR
            ('name', 'ilike', termino),
            ('default_code', 'ilike', termino),
        ])
```

---

## 4. JOINs y Relaciones

### En SQL tradicional necesitas JOINs explícitos

```sql
-- SQL: Obtener pedidos con información del cliente
SELECT
    so.name as pedido,
    rp.name as cliente,
    rp.email as email_cliente
FROM sale_order so
INNER JOIN res_partner rp ON so.partner_id = rp.id
WHERE so.state = 'sale';
```

### En Odoo, las relaciones son automáticas

```python
# ORM - NO necesitas JOIN, accedes directamente
pedidos = self.env['sale.order'].search([('state', '=', 'sale')])

for pedido in pedidos:
    print(pedido.name)              # Campo del pedido
    print(pedido.partner_id.name)   # Campo del partner relacionado
    print(pedido.partner_id.email)  # Otro campo del partner

# Es como si tuvieras un JOIN automático
```

### Relación One2many (similar a subconsulta)

```sql
-- SQL: Obtener líneas de un pedido
SELECT * FROM sale_order_line WHERE order_id = 42;
```

```python
# ORM
pedido = self.env['sale.order'].browse(42)
for linea in pedido.order_line:
    print(linea.product_id.name, linea.product_uom_qty, linea.price_unit)
```

### Relación Many2many

```sql
-- SQL: Productos y sus categorías (tabla intermedia)
SELECT p.name, c.name
FROM product_product p
JOIN product_category_rel pcr ON p.id = pcr.product_id
JOIN product_category c ON pcr.category_id = c.id;
```

```python
# ORM
productos = self.env['product.product'].search([])
for producto in productos:
    for categoria in producto.categ_ids:
        print(producto.name, categoria.name)
```

### Agregar/Quitar relaciones Many2many

```python
# Comandos especiales para campos One2many y Many2many
producto.write({
    'categ_ids': [
        (0, 0, {'name': 'Nueva Categoría'}),  # Crear y vincular
        (1, id, {'name': 'Actualizar'}),       # Actualizar existente
        (2, id),                                # Desvincular y eliminar
        (3, id),                                # Desvincular (no eliminar)
        (4, id),                                # Vincular existente
        (5, 0, 0),                              # Desvincular todos
        (6, 0, [id1, id2]),                     # Reemplazar con lista
    ]
})

# Ejemplos prácticos:
# Agregar categoría existente
producto.write({'categ_ids': [(4, categoria_id)]})

# Quitar una categoría (sin eliminarla)
producto.write({'categ_ids': [(3, categoria_id)]})

# Reemplazar todas las categorías
producto.write({'categ_ids': [(6, 0, [cat1_id, cat2_id, cat3_id])]})
```

---

## 5. Transacciones

### En SQL/Node.js

```javascript
// Node.js con MySQL
const connection = await pool.getConnection();
try {
    await connection.beginTransaction();
    await connection.execute('INSERT INTO...');
    await connection.execute('UPDATE...');
    await connection.commit();
} catch (error) {
    await connection.rollback();
    throw error;
} finally {
    connection.release();
}
```

### En Odoo

```python
# Odoo maneja las transacciones automáticamente
# Cada request HTTP es una transacción
# Si hay un error, hace rollback automático

def mi_metodo(self):
    # Todo esto es una transacción
    self.env['modelo.a'].create({...})
    self.env['modelo.b'].create({...})
    # Si algo falla, AMBOS creates se revierten

# Si necesitas control explícito:
def con_savepoint(self):
    try:
        with self.env.cr.savepoint():
            # Operaciones que pueden fallar
            self.crear_algo_riesgoso()
    except Exception:
        # El savepoint se revierte, pero la transacción principal continúa
        pass

# IMPORTANTE: NUNCA usar self.env.cr.commit() en código normal
# Odoo maneja los commits automáticamente
```

---

## 6. Cuándo Usar SQL Directo

### Usar ORM cuando:
- Operaciones CRUD normales
- Necesitas aplicar reglas de seguridad
- Trabajas con pocos registros (< 10,000)
- Necesitas los campos calculados y lógica del modelo

### Usar SQL directo cuando:
- Reportes con agregaciones complejas
- Operaciones masivas (> 100,000 registros)
- Consultas que no se pueden expresar con el ORM
- Performance crítico (pero medir primero)

### Cómo usar SQL directo

```python
from odoo import api, models

class MiModelo(models.Model):
    _name = 'mi.modelo'

    def reporte_complejo(self):
        # Usar self.env.cr para ejecutar SQL
        self.env.cr.execute("""
            SELECT
                partner_id,
                SUM(amount_total) as total_ventas,
                COUNT(*) as cantidad_pedidos
            FROM sale_order
            WHERE state = 'sale'
              AND date_order >= %s
            GROUP BY partner_id
            HAVING SUM(amount_total) > %s
            ORDER BY total_ventas DESC
        """, ('2024-01-01', 10000))

        resultados = self.env.cr.fetchall()
        # resultados = [(partner_id, total, cantidad), ...]

        # O como diccionarios:
        self.env.cr.dictfetchall()
        # [{'partner_id': 1, 'total_ventas': 50000, 'cantidad_pedidos': 10}, ...]

    def actualizar_masivo(self):
        # ADVERTENCIA: Esto salta la seguridad y validaciones de Odoo
        self.env.cr.execute("""
            UPDATE res_partner
            SET active = false
            WHERE last_activity_date < NOW() - INTERVAL '2 years'
        """)

        # IMPORTANTE: Invalidar caché después de SQL directo
        self.env['res.partner'].invalidate_cache()
```

### Forma segura con parámetros

```python
# NUNCA hacer esto (SQL Injection):
self.env.cr.execute(f"SELECT * FROM tabla WHERE name = '{nombre}'")  # MAL!

# SIEMPRE usar parámetros:
self.env.cr.execute("SELECT * FROM tabla WHERE name = %s", (nombre,))  # BIEN

# O usar el wrapper SQL de Odoo (Odoo 15+):
from odoo.tools import SQL
query = SQL("SELECT * FROM tabla WHERE name = %s", nombre)
self.env.cr.execute(query)
```

---

## 7. Patrones Comunes

### Obtener o Crear (Get or Create)

```python
# Patrón común: buscar un registro, si no existe, crearlo
def get_or_create_partner(self, email):
    partner = self.env['res.partner'].search([('email', '=', email)], limit=1)
    if not partner:
        partner = self.env['res.partner'].create({
            'name': email.split('@')[0],
            'email': email,
        })
    return partner
```

### Procesar en Lotes (Batch Processing)

```python
# Procesar muchos registros sin agotar memoria
def procesar_todos(self):
    offset = 0
    batch_size = 1000

    while True:
        registros = self.env['mi.modelo'].search(
            [('procesado', '=', False)],
            limit=batch_size,
            offset=offset
        )

        if not registros:
            break

        for registro in registros:
            self.procesar_uno(registro)

        # Commit intermedio para liberar memoria
        self.env.cr.commit()
        offset += batch_size
```

### Evitar N+1 Queries

```python
# MAL: N+1 queries
pedidos = self.env['sale.order'].search([])
for pedido in pedidos:
    # Esto genera una query por cada pedido para obtener el partner
    print(pedido.partner_id.name)

# BIEN: Prefetch automático
pedidos = self.env['sale.order'].search([])
# Odoo prefetch automáticamente los partners relacionados
for pedido in pedidos:
    print(pedido.partner_id.name)  # No genera queries adicionales

# MEJOR: Si necesitas control explícito
pedidos = self.env['sale.order'].search([])
pedidos.mapped('partner_id')  # Fuerza la carga de todos los partners
for pedido in pedidos:
    print(pedido.partner_id.name)
```

### Cambiar Contexto/Usuario

```python
# Ejecutar como superusuario (sin restricciones de seguridad)
registros = self.env['mi.modelo'].sudo().search([])

# Ejecutar como otro usuario
otro_usuario = self.env['res.users'].browse(2)
registros = self.env['mi.modelo'].with_user(otro_usuario).search([])

# Cambiar compañía
otra_company = self.env['res.company'].browse(2)
registros = self.env['mi.modelo'].with_company(otra_company).search([])

# Agregar contexto
registros = self.env['mi.modelo'].with_context(
    lang='es_ES',
    active_test=False,  # Incluir registros inactivos
    force_company=2,
).search([])
```

---

## 8. Errores Frecuentes

### Error 1: Olvidar que search() devuelve recordset

```python
# MAL
partner = self.env['res.partner'].search([('id', '=', 1)])
if partner == None:  # Nunca será None!
    print("No encontrado")

# BIEN
partner = self.env['res.partner'].search([('id', '=', 1)])
if not partner:  # Recordset vacío es falsy
    print("No encontrado")
if not partner.exists():  # Más explícito
    print("No encontrado")
```

### Error 2: Modificar recordset en iteración

```python
# MAL - Puede causar comportamientos inesperados
for partner in partners:
    if partner.active:
        partners -= partner  # Modificando mientras iteras

# BIEN - Filtrar primero
partners_activos = partners.filtered(lambda p: p.active)
for partner in partners_activos:
    # procesar
```

### Error 3: No usar browse correctamente

```python
# MAL - browse espera un ID, no un recordset
partner_id = self.env['res.partner'].search([...], limit=1)
partner = self.env['res.partner'].browse(partner_id)  # Error!

# BIEN - search ya devuelve un recordset
partner = self.env['res.partner'].search([...], limit=1)

# O si tienes solo el ID numérico:
partner = self.env['res.partner'].browse(42)
```

### Error 4: Comparar recordsets incorrectamente

```python
# MAL
if partner1 == partner2:  # Compara recordsets, no IDs

# BIEN
if partner1.id == partner2.id:
# O
if partner1 in partner2:  # Si partner2 es un recordset
```

### Error 5: Olvidar el self en métodos

```python
class MiModelo(models.Model):
    _name = 'mi.modelo'

    # MAL - Falta self
    def mi_metodo():
        pass

    # BIEN
    def mi_metodo(self):
        for record in self:
            # procesar cada registro
            pass
```

---

## Tabla de Referencia Rápida

| Operación SQL | ORM de Odoo |
|---------------|-------------|
| `SELECT * FROM tabla` | `self.env['tabla'].search([])` |
| `SELECT * FROM tabla WHERE id = 1` | `self.env['tabla'].browse(1)` |
| `SELECT * FROM tabla WHERE x = 'y'` | `self.env['tabla'].search([('x', '=', 'y')])` |
| `SELECT COUNT(*) FROM tabla` | `self.env['tabla'].search_count([])` |
| `INSERT INTO tabla (x) VALUES ('y')` | `self.env['tabla'].create({'x': 'y'})` |
| `UPDATE tabla SET x = 'y' WHERE id = 1` | `self.env['tabla'].browse(1).write({'x': 'y'})` |
| `DELETE FROM tabla WHERE id = 1` | `self.env['tabla'].browse(1).unlink()` |
| `SELECT DISTINCT x FROM tabla` | `self.env['tabla'].search([]).mapped('x')` |
| `... ORDER BY x ASC` | `search([], order='x asc')` |
| `... LIMIT 10 OFFSET 20` | `search([], limit=10, offset=20)` |
| `... WHERE x IN (1,2,3)` | `search([('x', 'in', [1,2,3])])` |
| `... WHERE x LIKE '%abc%'` | `search([('x', 'ilike', 'abc')])` |
| `... WHERE x IS NULL` | `search([('x', '=', False)])` |
| `... WHERE x IS NOT NULL` | `search([('x', '!=', False)])` |

---

## Recursos

- [Documentación ORM Odoo 17](https://www.odoo.com/documentation/17.0/developer/reference/backend/orm.html)
- [Expresiones de Dominio](https://www.odoo.com/documentation/17.0/developer/reference/backend/orm.html#domains)
