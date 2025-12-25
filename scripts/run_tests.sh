#!/bin/bash
# Script para ejecutar tests de un módulo
# Uso: ./scripts/run_tests.sh nombre_bd nombre_modulo

if [ -z "$1" ] || [ -z "$2" ]; then
    echo "Uso: $0 <nombre_bd> <nombre_modulo>"
    echo "Ejemplo: $0 odoo tutorial_06_testing"
    exit 1
fi

DB_NAME=$1
MODULE_NAME=$2

echo "Ejecutando tests del módulo '$MODULE_NAME'..."
docker compose exec odoo odoo -d "$DB_NAME" --test-enable -u "$MODULE_NAME" --stop-after-init --log-level=test

if [ $? -eq 0 ]; then
    echo "Tests completados."
else
    echo "Algunos tests fallaron."
    exit 1
fi
