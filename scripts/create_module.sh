#!/bin/bash
# Script para crear la estructura base de un módulo nuevo
# Uso: ./scripts/create_module.sh nombre_modulo

if [ -z "$1" ]; then
    echo "Uso: $0 <nombre_modulo>"
    echo "Ejemplo: $0 mi_modulo"
    exit 1
fi

MODULE_NAME=$1
MODULE_PATH="custom_addons/$MODULE_NAME"

if [ -d "$MODULE_PATH" ]; then
    echo "Error: El módulo '$MODULE_NAME' ya existe."
    exit 1
fi

echo "Creando estructura para módulo '$MODULE_NAME'..."

# Crear directorios
mkdir -p "$MODULE_PATH"/{models,views,security,data}

# Crear __manifest__.py
cat > "$MODULE_PATH/__manifest__.py" << EOF
# -*- coding: utf-8 -*-
{
    'name': '$MODULE_NAME',
    'version': '17.0.1.0.0',
    'summary': 'Descripción corta del módulo',
    'description': """
        Descripción larga del módulo.
    """,
    'author': 'Tu Nombre',
    'license': 'LGPL-3',
    'category': 'Uncategorized',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'views/menu_views.xml',
    ],
    'installable': True,
    'application': False,
}
EOF

# Crear __init__.py principal
cat > "$MODULE_PATH/__init__.py" << EOF
# -*- coding: utf-8 -*-
from . import models
EOF

# Crear models/__init__.py
cat > "$MODULE_PATH/models/__init__.py" << EOF
# -*- coding: utf-8 -*-
# from . import mi_modelo
EOF

# Crear security/ir.model.access.csv
cat > "$MODULE_PATH/security/ir.model.access.csv" << EOF
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
EOF

# Crear views/menu_views.xml
cat > "$MODULE_PATH/views/menu_views.xml" << EOF
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <!-- Agregar menús y acciones aquí -->
</odoo>
EOF

echo "Módulo '$MODULE_NAME' creado en $MODULE_PATH"
echo ""
echo "Próximos pasos:"
echo "1. Edita __manifest__.py con la información de tu módulo"
echo "2. Crea tus modelos en models/"
echo "3. Agrega permisos en security/ir.model.access.csv"
echo "4. Crea vistas en views/"
echo "5. Reinicia Odoo: docker compose restart odoo"
echo "6. Instala el módulo desde Aplicaciones o con:"
echo "   docker compose exec odoo odoo -d NOMBRE_BD -i $MODULE_NAME --stop-after-init"
