#!/bin/bash
# Script para acceder al shell de Odoo
# Uso: ./scripts/odoo_shell.sh nombre_bd

if [ -z "$1" ]; then
    echo "Uso: $0 <nombre_bd>"
    echo "Ejemplo: $0 odoo"
    exit 1
fi

DB_NAME=$1

echo "Iniciando shell de Odoo para base de datos '$DB_NAME'..."
echo "Comandos útiles:"
echo "  env['modelo'].search([])  - Buscar registros"
echo "  env.cr.commit()           - Guardar cambios"
echo "  exit()                    - Salir"
echo ""

docker compose exec odoo odoo shell -d "$DB_NAME"
