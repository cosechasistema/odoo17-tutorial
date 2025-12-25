# Guía de Desarrollo Odoo 17

## Índice
1. [Arquitectura de Odoo](#1-arquitectura-de-odoo)
2. [Estructura de un Módulo](#2-estructura-de-un-módulo)
3. [Modelos y ORM](#3-modelos-y-orm)
4. [Tipos de Campos](#4-tipos-de-campos)
5. [Decoradores](#5-decoradores)
6. [Vistas XML](#6-vistas-xml)
7. [Seguridad](#7-seguridad)
8. [Herencia](#8-herencia)
9. [Controladores HTTP](#9-controladores-http)
10. [Testing](#10-testing)

---

## 1. Arquitectura de Odoo

Odoo sigue una arquitectura **MVC (Modelo-Vista-Controlador)** adaptada:

```
┌─────────────────────────────────────────────────────────────┐
│                     CLIENTE (Navegador)                      │
│                   JavaScript + OWL Framework                 │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    CONTROLADOR (Python)                      │
│              HTTP Controllers + RPC Methods                  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      MODELO (Python)                         │
│                   ORM + Lógica de Negocio                   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    BASE DE DATOS (PostgreSQL)                │
└─────────────────────────────────────────────────────────────┘
```

### Componentes Principales

| Componente | Descripción |
|------------|-------------|
| **Modelos** | Clases Python que definen la estructura de datos y lógica de negocio |
| **Vistas** | Archivos XML que definen la interfaz de usuario |
| **Controladores** | Manejan peticiones HTTP y endpoints REST |
| **Reportes** | Templates QWeb para generar PDFs |
| **Datos** | Archivos XML con datos por defecto o demo |
| **Seguridad** | Reglas de acceso y permisos |

---

## 2. Estructura de un Módulo

```
mi_modulo/
├── __init__.py              # Inicializa el paquete Python
├── __manifest__.py          # Metadatos del módulo (OBLIGATORIO)
├── models/                  # Modelos (tablas de BD)
│   ├── __init__.py
│   └── mi_modelo.py
├── views/                   # Vistas XML
│   ├── mi_modelo_views.xml
│   └── menu_views.xml
├── security/                # Permisos y reglas
│   └── ir.model.access.csv
├── data/                    # Datos por defecto
│   └── datos_iniciales.xml
├── demo/                    # Datos de demostración
│   └── demo_data.xml
├── controllers/             # Controladores HTTP (opcional)
│   ├── __init__.py
│   └── main.py
├── wizard/                  # Modelos transitorios (opcional)
│   ├── __init__.py
│   └── mi_wizard.py
├── report/                  # Reportes PDF (opcional)
│   └── report_templates.xml
└── static/                  # Archivos estáticos (opcional)
    ├── description/
    │   └── icon.png
    └── src/
        ├── js/
        └── css/
```

### Archivo `__manifest__.py`

```python
{
    'name': 'Mi Módulo',
    'version': '17.0.1.0.0',
    'summary': 'Descripción corta del módulo',
    'description': """
        Descripción larga del módulo.
        Puede usar reStructuredText.
    """,
    'author': 'Tu Nombre',
    'website': 'https://tu-sitio.com',
    'license': 'LGPL-3',
    'category': 'Uncategorized',

    # Módulos requeridos (siempre incluir 'base')
    'depends': ['base'],

    # Archivos que siempre se cargan
    'data': [
        'security/ir.model.access.csv',
        'views/mi_modelo_views.xml',
        'views/menu_views.xml',
    ],

    # Archivos solo para modo demo
    'demo': [
        'demo/demo_data.xml',
    ],

    # Si es una aplicación principal
    'application': False,

    # Si se puede instalar
    'installable': True,

    # Auto-instalar cuando las dependencias estén instaladas
    'auto_install': False,
}
```

### Archivo `__init__.py` Principal

```python
from . import models
from . import controllers  # Si existe
from . import wizard       # Si existe
```

---

## 3. Modelos y ORM

### Tipos de Modelos

| Tipo | Uso |
|------|-----|
| `models.Model` | Modelo persistente (crea tabla en BD) |
| `models.TransientModel` | Modelo temporal (se limpia automáticamente) - usado para wizards |
| `models.AbstractModel` | Modelo base para herencia (no crea tabla) |

### Estructura Básica de un Modelo

```python
from odoo import models, fields, api

class MiModelo(models.Model):
    _name = 'mi.modelo'              # Nombre técnico (tabla: mi_modelo)
    _description = 'Mi Modelo'        # Descripción legible
    _order = 'name asc'              # Orden por defecto
    _rec_name = 'name'               # Campo usado como nombre del registro

    # Campos
    name = fields.Char(string='Nombre', required=True)
    descripcion = fields.Text(string='Descripción')
    activo = fields.Boolean(string='Activo', default=True)

    # Métodos
    def mi_metodo(self):
        for record in self:
            # self es un recordset (puede tener múltiples registros)
            print(record.name)
```

### Métodos CRUD del ORM

```python
# CREAR un registro
nuevo = self.env['mi.modelo'].create({
    'name': 'Nuevo Registro',
    'descripcion': 'Una descripción',
})

# BUSCAR registros
registros = self.env['mi.modelo'].search([
    ('activo', '=', True),
    ('name', 'ilike', 'busqueda'),
])

# LEER un registro por ID
registro = self.env['mi.modelo'].browse(1)

# ACTUALIZAR
registro.write({
    'name': 'Nombre Actualizado',
})

# ELIMINAR
registro.unlink()
```

### Dominios de Búsqueda

```python
# Operadores: =, !=, >, <, >=, <=, like, ilike, in, not in
# Operadores lógicos: & (AND), | (OR), ! (NOT)

# AND implícito
[('campo1', '=', valor1), ('campo2', '=', valor2)]

# OR explícito
['|', ('campo1', '=', valor1), ('campo2', '=', valor2)]

# NOT
[('campo', 'not in', [1, 2, 3])]

# Búsqueda en campos relacionados
[('partner_id.country_id.code', '=', 'AR')]
```

### Métodos de Recordset

```python
registros = self.env['mi.modelo'].search([])

# mapped: extraer valores de un campo
nombres = registros.mapped('name')  # ['Reg1', 'Reg2', ...]

# filtered: filtrar registros
activos = registros.filtered(lambda r: r.activo)
# o usando el campo directamente
activos = registros.filtered('activo')

# sorted: ordenar
ordenados = registros.sorted(key=lambda r: r.name)
ordenados = registros.sorted('name', reverse=True)

# exists: verificar si hay registros
if registros.exists():
    print("Hay registros")

# ids: obtener lista de IDs
lista_ids = registros.ids  # [1, 2, 3, ...]
```

---

## 4. Tipos de Campos

### Campos Básicos

```python
from odoo import fields

# Texto
name = fields.Char(string='Nombre', size=100, required=True)
descripcion = fields.Text(string='Descripción')
html_content = fields.Html(string='Contenido HTML')

# Números
cantidad = fields.Integer(string='Cantidad', default=0)
precio = fields.Float(string='Precio', digits=(10, 2))  # 10 dígitos, 2 decimales
monto = fields.Monetary(string='Monto', currency_field='currency_id')

# Booleano
activo = fields.Boolean(string='Activo', default=True)

# Fecha y Hora
fecha = fields.Date(string='Fecha', default=fields.Date.today)
fecha_hora = fields.Datetime(string='Fecha y Hora', default=fields.Datetime.now)

# Selección
estado = fields.Selection([
    ('borrador', 'Borrador'),
    ('confirmado', 'Confirmado'),
    ('cancelado', 'Cancelado'),
], string='Estado', default='borrador')

# Binario (archivos, imágenes)
archivo = fields.Binary(string='Archivo')
imagen = fields.Image(string='Imagen', max_width=1024, max_height=1024)
```

### Campos Relacionales

```python
# Many2one: muchos registros de este modelo -> un registro del otro
# Ejemplo: Muchos libros pueden tener el mismo autor
autor_id = fields.Many2one(
    comodel_name='res.partner',
    string='Autor',
    ondelete='restrict',  # restrict, cascade, set null
    domain=[('is_company', '=', False)],  # Filtro opcional
)

# One2many: inverso del Many2one
# Ejemplo: Un autor tiene muchos libros
# REQUIERE un Many2one en el otro modelo que apunte a este
libro_ids = fields.One2many(
    comodel_name='biblioteca.libro',
    inverse_name='autor_id',
    string='Libros',
)

# Many2many: relación muchos a muchos
# Ejemplo: Un libro puede tener muchas categorías y una categoría muchos libros
categoria_ids = fields.Many2many(
    comodel_name='biblioteca.categoria',
    relation='libro_categoria_rel',  # Nombre tabla intermedia
    column1='libro_id',
    column2='categoria_id',
    string='Categorías',
)
```

### Campos Calculados

```python
# Campo calculado (compute)
total = fields.Float(
    string='Total',
    compute='_compute_total',
    store=True,  # True para guardar en BD (recomendado para reportes)
)

@api.depends('cantidad', 'precio')
def _compute_total(self):
    for record in self:
        record.total = record.cantidad * record.precio

# Campo calculado con inverso (editable)
nombre_completo = fields.Char(
    string='Nombre Completo',
    compute='_compute_nombre_completo',
    inverse='_inverse_nombre_completo',
    store=True,
)

@api.depends('nombre', 'apellido')
def _compute_nombre_completo(self):
    for record in self:
        record.nombre_completo = f"{record.nombre} {record.apellido}"

def _inverse_nombre_completo(self):
    for record in self:
        partes = record.nombre_completo.split(' ', 1)
        record.nombre = partes[0]
        record.apellido = partes[1] if len(partes) > 1 else ''
```

### Campos Relacionados

```python
# Acceso directo a un campo de un modelo relacionado
pais_autor = fields.Char(
    string='País del Autor',
    related='autor_id.country_id.name',
    readonly=True,  # Generalmente True
    store=False,    # False = no ocupa espacio en BD
)
```

---

## 5. Decoradores

### @api.model

```python
@api.model
def mi_metodo(self):
    """
    Método a nivel de modelo (no de registro).
    self es un recordset vacío.
    Uso: crear registros, operaciones generales.
    """
    return self.create({'name': 'Nuevo'})
```

### @api.depends

```python
@api.depends('campo1', 'campo2', 'linea_ids.precio')
def _compute_algo(self):
    """
    Se ejecuta automáticamente cuando cambian los campos especificados.
    Usado para campos computed.
    """
    for record in self:
        record.total = sum(record.linea_ids.mapped('precio'))
```

### @api.onchange

```python
@api.onchange('partner_id')
def _onchange_partner(self):
    """
    Se ejecuta en el cliente (navegador) cuando cambia el campo.
    Puede modificar otros campos o mostrar warnings.
    NO guarda en BD, solo actualiza la vista.
    """
    if self.partner_id:
        self.direccion = self.partner_id.street

    # Mostrar advertencia
    return {
        'warning': {
            'title': 'Advertencia',
            'message': 'Este cliente tiene saldo pendiente.',
        }
    }
```

### @api.constrains

```python
from odoo.exceptions import ValidationError

@api.constrains('cantidad', 'precio')
def _check_valores_positivos(self):
    """
    Validación que se ejecuta al guardar.
    Lanza error si no se cumple la condición.
    """
    for record in self:
        if record.cantidad < 0 or record.precio < 0:
            raise ValidationError('La cantidad y precio deben ser positivos.')
```

### @api.model_create_multi

```python
@api.model_create_multi
def create(self, vals_list):
    """
    Sobrescribir el método create.
    vals_list es una lista de diccionarios.
    """
    for vals in vals_list:
        # Modificar valores antes de crear
        if not vals.get('codigo'):
            vals['codigo'] = self.env['ir.sequence'].next_by_code('mi.secuencia')

    return super().create(vals_list)
```

---

## 6. Vistas XML

### Vista Form (Formulario)

```xml
<odoo>
    <record id="view_mi_modelo_form" model="ir.ui.view">
        <field name="name">mi.modelo.form</field>
        <field name="model">mi.modelo</field>
        <field name="arch" type="xml">
            <form string="Mi Modelo">
                <!-- Barra de botones de estado -->
                <header>
                    <button name="action_confirmar"
                            string="Confirmar"
                            type="object"
                            class="btn-primary"
                            invisible="estado != 'borrador'"/>
                    <button name="action_cancelar"
                            string="Cancelar"
                            type="object"
                            invisible="estado == 'cancelado'"/>
                    <field name="estado" widget="statusbar"
                           statusbar_visible="borrador,confirmado"/>
                </header>

                <sheet>
                    <!-- Ribbon para estados especiales -->
                    <div class="oe_button_box" name="button_box">
                        <button name="action_ver_lineas"
                                type="object"
                                class="oe_stat_button"
                                icon="fa-list">
                            <field name="cantidad_lineas" widget="statinfo"/>
                        </button>
                    </div>

                    <!-- Imagen o avatar -->
                    <field name="imagen" widget="image" class="oe_avatar"/>

                    <!-- Título principal -->
                    <div class="oe_title">
                        <h1>
                            <field name="name" placeholder="Nombre..."/>
                        </h1>
                    </div>

                    <!-- Grupos de campos -->
                    <group>
                        <group string="Información General">
                            <field name="partner_id"/>
                            <field name="fecha"/>
                            <field name="activo"/>
                        </group>
                        <group string="Valores">
                            <field name="cantidad"/>
                            <field name="precio"/>
                            <field name="total" readonly="1"/>
                        </group>
                    </group>

                    <!-- Pestañas (notebook) -->
                    <notebook>
                        <page string="Líneas" name="lineas">
                            <field name="linea_ids">
                                <tree editable="bottom">
                                    <field name="producto_id"/>
                                    <field name="cantidad"/>
                                    <field name="precio"/>
                                    <field name="subtotal"/>
                                </tree>
                            </field>
                        </page>
                        <page string="Notas" name="notas">
                            <field name="notas" placeholder="Notas internas..."/>
                        </page>
                    </notebook>
                </sheet>

                <!-- Chatter (mensajes y seguimiento) -->
                <div class="oe_chatter">
                    <field name="message_follower_ids"/>
                    <field name="activity_ids"/>
                    <field name="message_ids"/>
                </div>
            </form>
        </field>
    </record>
</odoo>
```

### Vista Tree (Lista)

```xml
<record id="view_mi_modelo_tree" model="ir.ui.view">
    <field name="name">mi.modelo.tree</field>
    <field name="model">mi.modelo</field>
    <field name="arch" type="xml">
        <tree string="Mi Modelo"
              decoration-danger="estado == 'cancelado'"
              decoration-success="estado == 'confirmado'"
              default_order="fecha desc">
            <field name="name"/>
            <field name="partner_id"/>
            <field name="fecha"/>
            <field name="total" sum="Total"/>
            <field name="estado"
                   widget="badge"
                   decoration-info="estado == 'borrador'"
                   decoration-success="estado == 'confirmado'"
                   decoration-danger="estado == 'cancelado'"/>
        </tree>
    </field>
</record>
```

### Vista Search (Búsqueda y Filtros)

```xml
<record id="view_mi_modelo_search" model="ir.ui.view">
    <field name="name">mi.modelo.search</field>
    <field name="model">mi.modelo</field>
    <field name="arch" type="xml">
        <search string="Buscar Mi Modelo">
            <!-- Campos de búsqueda -->
            <field name="name"/>
            <field name="partner_id"/>

            <!-- Filtros predefinidos -->
            <filter string="Activos"
                    name="filter_activos"
                    domain="[('activo', '=', True)]"/>
            <filter string="Confirmados"
                    name="filter_confirmados"
                    domain="[('estado', '=', 'confirmado')]"/>

            <separator/>

            <filter string="Fecha: Este Mes"
                    name="filter_este_mes"
                    domain="[('fecha', '>=', (context_today() - relativedelta(day=1)).strftime('%Y-%m-%d')),
                             ('fecha', '&lt;', (context_today() + relativedelta(months=1, day=1)).strftime('%Y-%m-%d'))]"/>

            <!-- Agrupaciones -->
            <group expand="0" string="Agrupar Por">
                <filter string="Estado" name="group_estado" context="{'group_by': 'estado'}"/>
                <filter string="Cliente" name="group_partner" context="{'group_by': 'partner_id'}"/>
                <filter string="Fecha" name="group_fecha" context="{'group_by': 'fecha:month'}"/>
            </group>
        </search>
    </field>
</record>
```

### Acciones y Menús

```xml
<!-- Acción de ventana -->
<record id="action_mi_modelo" model="ir.actions.act_window">
    <field name="name">Mi Modelo</field>
    <field name="res_model">mi.modelo</field>
    <field name="view_mode">tree,form,kanban</field>
    <field name="search_view_id" ref="view_mi_modelo_search"/>
    <field name="context">{'default_activo': True}</field>
    <field name="domain">[('activo', '=', True)]</field>
    <field name="help" type="html">
        <p class="o_view_nocontent_smiling_face">
            Crear el primer registro
        </p>
        <p>
            Haz clic en el botón para crear un nuevo registro.
        </p>
    </field>
</record>

<!-- Menú raíz -->
<menuitem id="menu_mi_modulo_root"
          name="Mi Módulo"
          sequence="10"/>

<!-- Submenú -->
<menuitem id="menu_mi_modelo"
          name="Mi Modelo"
          parent="menu_mi_modulo_root"
          action="action_mi_modelo"
          sequence="10"/>
```

---

## 7. Seguridad

### Archivo `ir.model.access.csv`

```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_mi_modelo_user,mi.modelo.user,model_mi_modelo,base.group_user,1,1,1,0
access_mi_modelo_manager,mi.modelo.manager,model_mi_modelo,base.group_system,1,1,1,1
```

| Columna | Descripción |
|---------|-------------|
| id | Identificador único de la regla |
| name | Nombre descriptivo |
| model_id:id | Referencia al modelo (model_nombre_modelo) |
| group_id:id | Grupo de usuarios (base.group_user, etc.) |
| perm_read | 1 = puede leer |
| perm_write | 1 = puede escribir |
| perm_create | 1 = puede crear |
| perm_unlink | 1 = puede eliminar |

### Record Rules (Reglas de Registro)

```xml
<record id="rule_mi_modelo_usuario" model="ir.rule">
    <field name="name">Mi Modelo: Solo propios</field>
    <field name="model_id" ref="model_mi_modelo"/>
    <field name="domain_force">[('create_uid', '=', user.id)]</field>
    <field name="groups" eval="[(4, ref('base.group_user'))]"/>
    <field name="perm_read" eval="True"/>
    <field name="perm_write" eval="True"/>
    <field name="perm_create" eval="True"/>
    <field name="perm_unlink" eval="True"/>
</record>
```

---

## 8. Herencia

### Herencia de Modelo (_inherit)

```python
from odoo import models, fields

class ResPartner(models.Model):
    _inherit = 'res.partner'  # Extender modelo existente

    # Agregar nuevos campos
    es_autor = fields.Boolean(string='Es Autor')
    biografia = fields.Text(string='Biografía')

    # Extender métodos existentes
    def write(self, vals):
        # Código antes de escribir
        result = super().write(vals)
        # Código después de escribir
        return result
```

### Herencia de Vista

```xml
<record id="view_partner_form_inherit" model="ir.ui.view">
    <field name="name">res.partner.form.inherit.mi_modulo</field>
    <field name="model">res.partner</field>
    <field name="inherit_id" ref="base.view_partner_form"/>
    <field name="arch" type="xml">
        <!-- Agregar después de un campo -->
        <field name="phone" position="after">
            <field name="es_autor"/>
        </field>

        <!-- Agregar dentro de un grupo -->
        <group name="sale" position="inside">
            <field name="biografia"/>
        </group>

        <!-- Reemplazar un elemento -->
        <field name="website" position="replace">
            <field name="website" widget="url"/>
        </field>

        <!-- Agregar atributos -->
        <field name="email" position="attributes">
            <attribute name="required">1</attribute>
        </field>
    </field>
</record>
```

### Posiciones de Herencia

| Posición | Descripción |
|----------|-------------|
| `inside` | Agregar al final del elemento |
| `after` | Agregar después del elemento |
| `before` | Agregar antes del elemento |
| `replace` | Reemplazar el elemento |
| `attributes` | Modificar atributos del elemento |

---

## 9. Controladores HTTP

### Controlador Básico

```python
from odoo import http
from odoo.http import request
import json

class MiControlador(http.Controller):

    @http.route('/mi_modulo/items', type='http', auth='public', website=True)
    def lista_items(self, **kwargs):
        """Ruta pública que renderiza una página web."""
        items = request.env['mi.modelo'].sudo().search([('activo', '=', True)])
        return request.render('mi_modulo.template_lista', {
            'items': items,
        })

    @http.route('/api/mi_modulo/items', type='json', auth='user', methods=['GET'])
    def api_lista_items(self, **kwargs):
        """API JSON para usuarios autenticados."""
        items = request.env['mi.modelo'].search([])
        return [{
            'id': item.id,
            'name': item.name,
            'total': item.total,
        } for item in items]

    @http.route('/api/mi_modulo/item/<int:item_id>', type='json', auth='user', methods=['GET'])
    def api_get_item(self, item_id, **kwargs):
        """Obtener un item específico."""
        item = request.env['mi.modelo'].browse(item_id)
        if not item.exists():
            return {'error': 'Item no encontrado'}
        return {
            'id': item.id,
            'name': item.name,
        }

    @http.route('/api/mi_modulo/item', type='json', auth='user', methods=['POST'])
    def api_crear_item(self, **kwargs):
        """Crear un nuevo item."""
        data = request.jsonrequest
        item = request.env['mi.modelo'].create({
            'name': data.get('name'),
            'cantidad': data.get('cantidad', 0),
        })
        return {'id': item.id, 'name': item.name}
```

### Autenticación

| Auth | Descripción |
|------|-------------|
| `public` | Sin autenticación requerida |
| `user` | Usuario debe estar logueado |
| `none` | Sin usuario ni base de datos (raro) |

---

## 10. Testing

### Estructura de Tests

```
mi_modulo/
└── tests/
    ├── __init__.py
    ├── test_mi_modelo.py
    └── test_logica.py
```

### Test Básico

```python
from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError

class TestMiModelo(TransactionCase):

    @classmethod
    def setUpClass(cls):
        """Se ejecuta una vez antes de todos los tests de la clase."""
        super().setUpClass()

        # Crear datos de prueba
        cls.partner = cls.env['res.partner'].create({
            'name': 'Partner de Prueba',
        })

        cls.mi_registro = cls.env['mi.modelo'].create({
            'name': 'Test',
            'partner_id': cls.partner.id,
            'cantidad': 10,
            'precio': 100.0,
        })

    def test_calculo_total(self):
        """Verificar que el total se calcula correctamente."""
        self.assertEqual(self.mi_registro.total, 1000.0)

    def test_cambiar_cantidad(self):
        """Verificar que al cambiar cantidad, cambia el total."""
        self.mi_registro.write({'cantidad': 5})
        self.assertEqual(self.mi_registro.total, 500.0)

    def test_constraint_cantidad_negativa(self):
        """Verificar que no se puede tener cantidad negativa."""
        with self.assertRaises(ValidationError):
            self.mi_registro.write({'cantidad': -1})

    def test_crear_registro(self):
        """Verificar que se puede crear un registro."""
        nuevo = self.env['mi.modelo'].create({
            'name': 'Nuevo Test',
            'cantidad': 1,
            'precio': 50.0,
        })
        self.assertTrue(nuevo.exists())
        self.assertEqual(nuevo.total, 50.0)
```

### Ejecutar Tests

```bash
# Ejecutar tests de un módulo específico
docker compose exec odoo odoo --test-enable -d nombre_bd -u mi_modulo --stop-after-init

# Solo un archivo de test
docker compose exec odoo odoo --test-file=/mnt/extra-addons/mi_modulo/tests/test_mi_modelo.py -d nombre_bd --stop-after-init

# Con tags específicos
docker compose exec odoo odoo --test-tags=/mi_modulo -d nombre_bd --stop-after-init
```

---

## Recursos Adicionales

- [Documentación Oficial Odoo 17](https://www.odoo.com/documentation/17.0/)
- [ORM API](https://www.odoo.com/documentation/17.0/developer/reference/backend/orm.html)
- [Guía de Vistas](https://www.odoo.com/documentation/17.0/developer/reference/backend/views.html)
- [Coding Guidelines](https://www.odoo.com/documentation/17.0/contributing/development/coding_guidelines.html)
