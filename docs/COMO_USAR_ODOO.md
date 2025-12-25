# Cómo Usar Odoo - Guía para Principiantes

Esta guía explica los conceptos básicos de cómo funciona Odoo desde la perspectiva del usuario. Si vienes del desarrollo web tradicional, Odoo puede parecer diferente porque es un **ERP completo** con su propia forma de organizar las cosas.

## Índice
1. [Conceptos Básicos](#1-conceptos-básicos)
2. [Usuarios y Permisos](#2-usuarios-y-permisos)
3. [Cómo Ver los Módulos Instalados](#3-cómo-ver-los-módulos-instalados)
4. [Usando los Módulos de Tutorial](#4-usando-los-módulos-de-tutorial)
5. [Cómo Funcionan los Menús](#5-cómo-funcionan-los-menús)
6. [Flujo de Trabajo Típico](#6-flujo-de-trabajo-típico)

---

## 1. Conceptos Básicos

### ¿Qué es un "Módulo" en Odoo?

Un **módulo** es como un "plugin" o "aplicación" que agrega funcionalidad a Odoo. Cuando instalas un módulo:

1. Se crean las **tablas** en la base de datos
2. Se agregan **menús** a la interfaz
3. Se definen **permisos** de acceso
4. Aparece en la lista de **Apps** (si es una aplicación principal)

```
┌─────────────────────────────────────────────────────────────┐
│  ODOO = Base del sistema                                    │
├─────────────────────────────────────────────────────────────┤
│  + Módulo Ventas        (agrega menú "Ventas")             │
│  + Módulo Contabilidad  (agrega menú "Contabilidad")       │
│  + Módulo CRM           (agrega menú "CRM")                │
│  + Tu Módulo Biblioteca (agrega menú "Biblioteca")         │
└─────────────────────────────────────────────────────────────┘
```

### Diferencia: Aplicación vs Módulo

| Tipo | Descripción | Ejemplo |
|------|-------------|---------|
| **Aplicación** | Módulo principal, aparece en Apps | Ventas, CRM, Biblioteca |
| **Módulo** | Extensión, no aparece solo en Apps | Reportes de ventas, API |

Un módulo se convierte en "Aplicación" si tiene `application: True` en su `__manifest__.py`.

---

## 2. Usuarios y Permisos

### El Usuario Administrador

Cuando creas la base de datos en Odoo, creas un **usuario administrador** con tu email y contraseña. Este usuario:

- Tiene acceso a **TODAS** las funciones
- Puede instalar/desinstalar módulos
- Puede crear otros usuarios
- Puede ver todos los menús

**Para desarrollo y pruebas, usarás este usuario administrador. No necesitas crear otro.**

### Grupos de Usuarios

Odoo organiza los permisos en **grupos**:

```
base.group_user      = Usuario interno (empleado)
base.group_system    = Administrador de configuración
base.group_erp_manager = Acceso total a ajustes
```

Cuando defines un módulo, especificas qué grupos pueden:
- Leer registros
- Crear registros
- Modificar registros
- Eliminar registros

### ¿Necesitas crear usuarios para probar?

**Para desarrollo: NO.** Usa el administrador.

**Para probar permisos:** Sí, crea usuarios de prueba con distintos roles:

1. Ve a **Ajustes** → **Usuarios y Compañías** → **Usuarios**
2. Click en **Crear**
3. Asigna los grupos/permisos que quieras probar

---

## 3. Cómo Ver los Módulos Instalados

### Paso 1: Acceder a Odoo

1. Abre http://localhost:8070
2. Inicia sesión con tu email y contraseña

### Paso 2: Ver Aplicaciones Instaladas

1. Click en el **menú cuadrícula** (esquina superior izquierda, el ícono de 9 puntos)
2. Verás todas las aplicaciones/menús disponibles

```
┌────────────────────────────────────────┐
│  ⬚⬚⬚  ← Click aquí (Menú de Apps)      │
├────────────────────────────────────────┤
│                                        │
│   📊 Tableros    💰 Contabilidad       │
│                                        │
│   📚 Biblioteca  👥 Contactos          │
│                                        │
│   ⚙️ Ajustes                           │
│                                        │
└────────────────────────────────────────┘
```

### Paso 3: Ver Todos los Módulos

1. Ve a **Ajustes** (engranaje ⚙️)
2. En la barra izquierda, busca **Aplicaciones**
3. Aquí verás:
   - **Aplicaciones**: Módulos principales
   - **Actualizaciones**: Módulos con actualizaciones disponibles

### Filtrar Módulos

En la vista de Apps:
- **Installed** (Instaladas): Módulos que ya tienes
- **Apps** (Aplicaciones): Solo aplicaciones principales
- **Extra**: Módulos adicionales no instalados

---

## 4. Usando los Módulos de Tutorial

### Instalar el Módulo tutorial_01_basico

```bash
docker compose exec odoo odoo -d odoo_dev -i tutorial_01_basico --stop-after-init
```

### Ver el Menú de Biblioteca

1. **Reinicia Odoo** (si es necesario):
   ```bash
   docker compose restart odoo
   ```

2. **Refresca el navegador** (F5 o Ctrl+R)

3. **Click en el menú cuadrícula** (esquina superior izquierda)

4. **Busca "Biblioteca"** - debería aparecer como opción

5. **Click en Biblioteca**

```
┌─────────────────────────────────────────────────────────────┐
│  📚 Biblioteca                                              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Menú lateral:                Vista principal:              │
│  ┌─────────────┐              ┌─────────────────────────┐   │
│  │ 📖 Libros   │              │ Lista de libros...      │   │
│  │ 📁 Catálogo │              │ - Don Quijote           │   │
│  │    └─Libros │              │ - Cien años de soledad  │   │
│  └─────────────┘              │ - El Aleph              │   │
│                               └─────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### Si No Ves el Menú

**Problema común**: El menú no aparece después de instalar.

**Soluciones**:

1. **Refrescar la página** (F5)

2. **Actualizar la lista de Apps**:
   - Ve a Ajustes → Aplicaciones
   - Click en "Actualizar lista de Apps"

3. **Verificar que el módulo está instalado**:
   - Ve a Ajustes → Aplicaciones
   - Quita el filtro "Apps"
   - Busca "tutorial" o "biblioteca"
   - Debería decir "Instalada"

4. **Revisar permisos**:
   - El archivo `security/ir.model.access.csv` debe dar permisos a `base.group_user`

5. **Ver logs de error**:
   ```bash
   docker compose logs -f odoo
   ```

---

## 5. Cómo Funcionan los Menús

### Estructura de Menús en Odoo

Los menús en Odoo tienen una jerarquía:

```
Menú Raíz (aparece en el selector de apps)
└── Submenú Nivel 1
    └── Submenú Nivel 2
        └── Acción (abre una vista)
```

### Ejemplo del Módulo Biblioteca

```xml
<!-- Menú Raíz - aparece en el menú cuadrícula -->
<menuitem id="biblioteca_menu_root"
          name="Biblioteca"
          sequence="10"/>

<!-- Submenú de Catálogo -->
<menuitem id="biblioteca_menu_catalogo"
          name="Catálogo"
          parent="biblioteca_menu_root"
          sequence="10"/>

<!-- Opción Libros - abre la lista de libros -->
<menuitem id="biblioteca_menu_libro"
          name="Libros"
          parent="biblioteca_menu_catalogo"
          action="biblioteca_libro_action"
          sequence="10"/>
```

### Cómo se Conecta Todo

```
1. Usuario hace click en "Biblioteca"
         ↓
2. Odoo busca los menús hijos de "biblioteca_menu_root"
         ↓
3. Muestra "Catálogo" en el menú lateral
         ↓
4. Usuario hace click en "Catálogo" → "Libros"
         ↓
5. Odoo ejecuta la acción "biblioteca_libro_action"
         ↓
6. La acción abre la vista tree/form del modelo "biblioteca.libro"
         ↓
7. Usuario ve la lista de libros
```

### Archivo de Acción (action)

```xml
<record id="biblioteca_libro_action" model="ir.actions.act_window">
    <field name="name">Libros</field>
    <field name="res_model">biblioteca.libro</field>
    <field name="view_mode">tree,form</field>
</record>
```

Esta acción dice:
- **name**: Título de la ventana
- **res_model**: Qué modelo/tabla mostrar
- **view_mode**: Primero lista (tree), luego formulario (form)

---

## 6. Flujo de Trabajo Típico

### Desarrollador: Crear y Probar un Módulo

```
1. Crear/Editar archivos Python y XML
         ↓
2. Reiniciar Odoo (si cambió Python):
   $ docker compose restart odoo
         ↓
3. Actualizar el módulo:
   $ docker compose exec odoo odoo -d odoo_dev -u mi_modulo --stop-after-init
         ↓
4. Refrescar navegador (F5)
         ↓
5. Ir al menú del módulo
         ↓
6. Probar la funcionalidad
         ↓
7. Repetir si hay errores
```

### Usuario: Usar una Funcionalidad

```
1. Iniciar sesión en Odoo
         ↓
2. Click en el menú cuadrícula
         ↓
3. Seleccionar la aplicación (ej: Biblioteca)
         ↓
4. Navegar por el menú lateral
         ↓
5. Ver registros en vista lista (tree)
         ↓
6. Click en un registro para ver/editar (form)
         ↓
7. Usar botones para acciones especiales
```

---

## Ejemplo Práctico: Ver el Tutorial 01

### 1. Verificar que Odoo está corriendo

```bash
docker compose ps
```

Deberías ver:
```
NAME              STATUS
odoo17dev         Up
odoo17dev-db      Up (healthy)
odoo17dev-pgadmin Up
```

### 2. Instalar el módulo (si no está instalado)

```bash
docker compose exec odoo odoo -d odoo_dev -i tutorial_01_basico --stop-after-init
```

### 3. Abrir Odoo en el navegador

1. Ve a http://localhost:8070
2. Inicia sesión

### 4. Encontrar el menú Biblioteca

1. Click en el ícono cuadrícula (⬚⬚⬚) arriba a la izquierda
2. Busca "Biblioteca" en la lista
3. Click en "Biblioteca"

### 5. Ver los libros

1. En el menú lateral, ve a **Catálogo** → **Libros**
2. Deberías ver 5 libros de ejemplo:
   - Don Quijote de la Mancha
   - Cien Años de Soledad
   - El Aleph
   - Rayuela
   - La Casa de los Espíritus

### 6. Crear un libro nuevo

1. Click en el botón **Crear**
2. Llena los campos:
   - Título: "Mi Libro de Prueba"
   - Autor: "Tu Nombre"
   - ISBN: "1234567890123"
3. Click en **Guardar**

### 7. Editar un libro

1. Click en cualquier libro de la lista
2. Modifica algún campo
3. Click en **Guardar**

---

## Resumen

| Concepto | Qué es | Dónde verlo |
|----------|--------|-------------|
| **Módulo** | Código Python + XML que agrega funcionalidad | `custom_addons/` |
| **Aplicación** | Módulo principal con menú propio | Menú cuadrícula |
| **Menú** | Navegación para acceder a funciones | Menú lateral |
| **Acción** | Qué hacer cuando clickeas un menú | Abre vistas |
| **Vista** | Cómo se muestran los datos | Tree, Form, Search |
| **Modelo** | Tabla de la base de datos | Código Python |
| **Permisos** | Quién puede hacer qué | `ir.model.access.csv` |

---

## Próximos Pasos

1. **Explorar los otros tutoriales**:
   - `tutorial_02_relaciones` - Relaciones entre tablas
   - `tutorial_03_computed` - Campos calculados
   - etc.

2. **Leer la documentación técnica**:
   - `docs/GUIA_DESARROLLO.md` - Cómo desarrollar módulos
   - `docs/ORM_PARA_DESARROLLADORES_SQL.md` - Si vienes de SQL

3. **Experimentar**:
   - Modifica los archivos XML y ve los cambios
   - Agrega nuevos campos a los modelos
   - Crea tus propios módulos
