#!/bin/bash
# Script para actualizar un módulo de Odoo
# Uso: ./scripts/update_module.sh nombre_bd nombre_modulo

if [ -z "$1" ] || [ -z "$2" ]; then
    echo "Uso: $0 <nombre_bd> <nombre_modulo>"
    echo "Ejemplo: $0 odoo tutorial_01_basico"
    exit 1
fi

DB_NAME=$1
MODULE_NAME=$2

echo "Actualizando módulo '$MODULE_NAME' en base de datos '$DB_NAME'..."
docker compose exec odoo odoo -d "$DB_NAME" -u "$MODULE_NAME" --stop-after-init

if [ $? -eq 0 ]; then
    echo "Módulo actualizado exitosamente."
else
    echo "Error al actualizar el módulo."
    exit 1
fi
