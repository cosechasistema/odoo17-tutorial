# Errores Comunes en Desarrollo Odoo 17

Este documento recopila errores comunes encontrados durante el desarrollo, sus causas y soluciones. El objetivo es aprender de los errores para no repetirlos.

## Índice

1. [Errores de Permisos](#1-errores-de-permisos)
2. [Errores de Vistas XML](#2-errores-de-vistas-xml)
3. [Errores de Modelos y Campos](#3-errores-de-modelos-y-campos)
4. [Errores de Dependencias](#4-errores-de-dependencias)
5. [Errores de Manifest](#5-errores-de-manifest)

---

## 1. Errores de Permisos

### PermissionError: Permission denied en __manifest__.py

**Error en logs:**
```
PermissionError: [Errno 13] Permission denied: '/mnt/extra-addons/mi_modulo/__manifest__.py'
```

**Síntomas:**
- Odoo muestra página de error 500
- No carga ninguna página
- En los logs aparece el error cada vez que intentas acceder

**¿Por qué ocurre?**

Docker ejecuta Odoo con un usuario específico (generalmente UID 101). Cuando creas archivos desde tu máquina host, estos pueden tener permisos restrictivos (ej: 644 o 600) que no permiten lectura al usuario de Docker.

```bash
# Ver los permisos actuales
ls -la custom_addons/mi_modulo/

# Ejemplo de permisos problemáticos:
# -rw------- 1 usuario usuario  450 Dec 27 10:00 __manifest__.py  (600 - solo owner)
# -rw-r----- 1 usuario usuario  450 Dec 27 10:00 __manifest__.py  (640 - owner y grupo)

# Permisos correctos:
# -rwxr-xr-x 1 usuario usuario  450 Dec 27 10:00 __manifest__.py  (755)
# -rw-r--r-- 1 usuario usuario  450 Dec 27 10:00 __manifest__.py  (644 mínimo)
```

**Solución:**
```bash
# Dar permisos de lectura y ejecución a directorios, lectura a archivos
chmod -R 755 custom_addons/nombre_modulo/

# Reiniciar Odoo para que recargue
docker compose restart odoo
```

**Prevención:**

1. **Después de crear módulos:**
   ```bash
   chmod -R 755 custom_addons/nuevo_modulo/
   ```

2. **Configurar umask en tu shell** (opcional):
   ```bash
   # Agregar a ~/.bashrc o ~/.zshrc
   umask 022  # Archivos nuevos tendrán 644, directorios 755
   ```

3. **Usar script de creación de módulos** que incluya el chmod automáticamente.

---

## 2. Errores de Vistas XML

### XPath con @string no funciona (Odoo 17)

**Error:**
```
Element '<xpath expr="//button[@string='Marcar Prestado']">' cannot be located in parent view
```

**¿Por qué ocurre?**

En Odoo 17, los selectores XPath que usan `@string` (el texto visible del elemento) ya no funcionan de manera confiable. Odoo prioriza atributos técnicos como `@name`.

**Incorrecto:**
```xml
<xpath expr="//field[@string='Disponible']" position="after">
<xpath expr="//button[@string='Marcar Prestado']" position="attributes">
```

**Correcto:**
```xml
<xpath expr="//field[@name='disponible']" position="after">
<xpath expr="//button[@name='action_marcar_prestado']" position="attributes">
```

**Regla:** Siempre usar `@name` en lugar de `@string` para selectores XPath.

---

### Heredar vista que no tiene el elemento padre (button_box)

**Error:**
```
Element '<xpath expr="//div[@name='button_box']">' cannot be located in parent view
```

**¿Por qué ocurre?**

Intentas agregar contenido a un `button_box` que no existe en la vista padre. No todos los formularios tienen un `button_box` definido.

**Solución:** Crear el `button_box` antes del elemento que sí existe:

```xml
<!-- Crear button_box antes de un campo que sí existe -->
<xpath expr="//field[@name='portada']" position="before">
    <div name="button_box" class="oe_button_box">
        <!-- Aquí van los botones estadísticos -->
        <button name="action_ver_prestamos" type="object" class="oe_stat_button">
            <field name="prestamos_count" widget="statinfo" string="Préstamos"/>
        </button>
    </div>
</xpath>
```

---

### Campo computed en filtro de búsqueda

**Error:**
```
Field biblioteca.miembro.prestamos_activos is not searchable
```

**¿Por qué ocurre?**

Los campos `compute` sin `store=True` no se guardan en la base de datos, por lo tanto no se pueden usar en:
- Filtros de búsqueda (`<filter>`)
- Dominios de búsqueda
- Ordenamiento

**Incorrecto:**
```python
prestamos_activos = fields.Integer(compute='_compute_prestamos')
```
```xml
<filter string="Con Préstamos" domain="[('prestamos_activos', '>', 0)]"/>
```

**Solución 1:** Agregar `store=True` (si el valor no cambia frecuentemente):
```python
prestamos_activos = fields.Integer(compute='_compute_prestamos', store=True)
```

**Solución 2:** Eliminar el filtro del search view:
```xml
<!-- Simplemente no incluir el filtro -->
```

**Solución 3:** Usar un campo relacionado que sí esté almacenado:
```xml
<filter string="Con Préstamos" domain="[('prestamo_ids', '!=', False)]"/>
```

---

## 3. Errores de Modelos y Campos

### One2many sin campo inverso Many2one

**Error:**
```
Field biblioteca.libro.prestamo_ids with unknown comodel_name 'biblioteca.prestamo'
```
o
```
KeyError: 'libro_id'
```

**¿Por qué ocurre?**

Un campo `One2many` requiere que exista un campo `Many2one` en el modelo relacionado que apunte de vuelta.

**Incorrecto:** Definir One2many sin el Many2one correspondiente:
```python
# En libro.py
prestamo_ids = fields.One2many('biblioteca.prestamo', 'libro_id', string='Préstamos')

# Pero en prestamo.py NO existe:
# libro_id = fields.Many2one('biblioteca.libro', ...)
```

**Correcto:**
```python
# En prestamo.py (DEBE existir primero)
libro_id = fields.Many2one('biblioteca.libro', string='Libro', required=True)

# En libro.py
prestamo_ids = fields.One2many('biblioteca.prestamo', 'libro_id', string='Préstamos')
```

---

### Falso en onchange causa error

**Error:**
```
TypeError: unsupported operand type(s) for -: 'bool' and 'datetime.date'
```

**¿Por qué ocurre?**

En métodos `@api.onchange`, los campos relacionados pueden ser `False` si no están seleccionados.

**Incorrecto:**
```python
@api.onchange('miembro_id')
def _onchange_miembro(self):
    if self.miembro_id:
        # Esto falla si fecha_vencimiento es False
        dias = (self.miembro_id.fecha_vencimiento - date.today()).days
```

**Correcto:**
```python
@api.onchange('miembro_id')
def _onchange_miembro(self):
    if self.miembro_id and self.miembro_id.fecha_vencimiento:
        dias = (self.miembro_id.fecha_vencimiento - date.today()).days
```

---

## 4. Errores de Dependencias

### Módulo no instalable por dependencia faltante

**Error:**
```
Module tutorial_07_reportes depends on tutorial_02_relaciones which is not installed
```

**¿Por qué ocurre?**

El módulo declarado en `depends` del `__manifest__.py` no está instalado.

**Solución:**
1. Primero instalar las dependencias en orden
2. O instalar el módulo padre, que instalará las dependencias automáticamente

```bash
# Ver dependencias de un módulo
grep -A5 "'depends'" custom_addons/tutorial_07_reportes/__manifest__.py
```

---

### Referencia a external_id que no existe

**Error:**
```
External ID not found in the system: tutorial_01_basico.menu_biblioteca_root
```

**¿Por qué ocurre?**

Estás referenciando un `xml_id` de otro módulo que:
- No está instalado
- El ID está mal escrito
- El módulo cambió el ID

**Solución:** Verificar que:
1. El módulo esté en `depends`
2. El ID exista y esté bien escrito

```bash
# Buscar el ID correcto
grep -r "menu_biblioteca_root" custom_addons/
```

---

## 5. Errores de Manifest

### Website URL inválida (Error 404 en "Más información")

**Error:** Al hacer clic en "Más información" de un módulo, aparece error 404.

**¿Por qué ocurre?**

El campo `website` en `__manifest__.py` tiene una URL que no existe o es placeholder.

**Incorrecto:**
```python
'website': 'https://github.com/tu-usuario',  # URL placeholder
```

**Correcto:**
```python
'website': '',  # Dejar vacío si no hay web real
# o
'website': 'https://tu-sitio-real.com',
```

---

## Checklist de Prevención

Antes de probar un módulo nuevo, verificar:

- [ ] Permisos: `chmod -R 755 custom_addons/mi_modulo/`
- [ ] Dependencias: Todos los módulos en `depends` están instalados
- [ ] Security: Archivo `ir.model.access.csv` existe y está en `data` del manifest
- [ ] XPath: Usar `@name` en lugar de `@string`
- [ ] Campos compute: Agregar `store=True` si se usan en filtros
- [ ] Many2one/One2many: Ambos lados de la relación existen
- [ ] Website: URL válida o vacía en manifest

---

## Cómo Diagnosticar Errores

### 1. Ver logs completos
```bash
docker compose logs -f odoo
```

### 2. Buscar el error específico
```bash
docker compose logs odoo 2>&1 | grep -i "error\|exception\|traceback" -A 10
```

### 3. Reiniciar con modo debug
```bash
docker compose exec odoo odoo -d NOMBRE_BD --dev=all
```

### 4. Verificar sintaxis XML
```bash
xmllint --noout custom_addons/mi_modulo/views/*.xml
```

### 5. Verificar sintaxis Python
```bash
python3 -m py_compile custom_addons/mi_modulo/models/*.py
```
