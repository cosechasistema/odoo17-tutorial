# Configurar MCP PostgreSQL para Claude Code

Este documento explica cómo configurar el MCP (Model Context Protocol) de PostgreSQL para que Claude Code pueda consultar directamente la base de datos de Odoo.

## Requisitos

1. Docker funcionando
2. El proyecto Odoo iniciado (`docker compose up -d`)

## Configuración

### Opción 1: Configuración del Proyecto (Recomendado)

El archivo `.claude/settings.local.json` ya está configurado en este proyecto. Claude Code lo detectará automáticamente.

### Opción 2: Configuración Global

Para que funcione en cualquier proyecto, copia la configuración a tu archivo global de Claude Code:

**Linux/macOS:**
```bash
mkdir -p ~/.config/claude-code
cat >> ~/.config/claude-code/settings.json << 'EOF'
{
  "mcpServers": {
    "postgres-odoo": {
      "command": "docker",
      "args": [
        "run", "-i", "--rm",
        "--network", "host",
        "-e", "DATABASE_URI",
        "crystaldba/postgres-mcp",
        "--access-mode=unrestricted"
      ],
      "env": {
        "DATABASE_URI": "postgresql://odoo:odoo@localhost:5433/postgres"
      }
    }
  }
}
EOF
```

## Verificar Funcionamiento

Una vez configurado, puedes pedirle a Claude Code que:

1. **Liste las tablas de Odoo:**
   "Lista las tablas que empiezan con 'biblioteca_'"

2. **Verifique registros:**
   "Muéstrame los libros en la tabla biblioteca_libro"

3. **Analice estructura:**
   "Describe la estructura de la tabla biblioteca_prestamo"

4. **Ejecute queries:**
   "Cuenta cuántos libros hay disponibles"

## Herramientas Disponibles del MCP

| Herramienta | Descripción |
|-------------|-------------|
| `list_schemas` | Lista esquemas de la base de datos |
| `list_objects` | Lista tablas, vistas, secuencias |
| `get_object_details` | Muestra columnas e índices de una tabla |
| `execute_sql` | Ejecuta consultas SQL |
| `explain_query` | Muestra plan de ejecución |
| `analyze_db_health` | Analiza salud de la base de datos |

## Ejemplos de Uso

### Verificar que un módulo creó sus tablas

```
Claude, verifica si la tabla biblioteca_libro existe y muéstrame su estructura
```

### Verificar que se cargaron los datos de ejemplo

```
Claude, ejecuta SELECT * FROM biblioteca_libro para ver los libros cargados
```

### Verificar un préstamo

```
Claude, muéstrame los préstamos activos con los nombres de libros y miembros
```

## Seguridad

El MCP está configurado en modo `unrestricted` para desarrollo, lo que permite lectura Y escritura. Para producción, usa `--access-mode=restricted` que solo permite lectura.

## Troubleshooting

### Error: No se puede conectar

1. Verifica que los contenedores estén corriendo:
   ```bash
   docker compose ps
   ```

2. Verifica que PostgreSQL esté escuchando en el puerto 5433:
   ```bash
   docker compose exec db psql -U odoo -c "SELECT 1"
   ```

### Error: Imagen no encontrada

Descarga la imagen del MCP:
```bash
docker pull crystaldba/postgres-mcp
```

### El MCP no aparece en Claude Code

Reinicia Claude Code después de agregar la configuración.
