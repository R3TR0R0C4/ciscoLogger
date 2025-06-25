# ciscoLogger

**ciscoLogger** es una solución para recolectar, almacenar y visualizar información de interfaces de switches Cisco. Incluye un backend en Python para la recolección de datos, una base de datos MariaDB/MySQL y un frontend web en PHP para la gestión y visualización.

## Tabla de Contenidos

- [ciscoLogger](#ciscologger)
  - [Tabla de Contenidos](#tabla-de-contenidos)
  - [Características](#características)
  - [Arquitectura](#arquitectura)
  - [Instalación](#instalación)
    - [Requisitos](#requisitos)
    - [Configuración de la Base de Datos](#configuración-de-la-base-de-datos)
    - [Configuración del Backend (Python)](#configuración-del-backend-python)
    - [Configuración del Frontend (PHP)](#configuración-del-frontend-php)
  - [Uso](#uso)
  - [Automatización y Limpieza](#automatización-y-limpieza)
  - [Estructura del Proyecto](#estructura-del-proyecto)
  - [Notas de Seguridad](#notas-de-seguridad)

## Características

- Recolección automática de información de interfaces de switches Cisco vía Telnet usando Netmiko.
- Almacenamiento estructurado en MariaDB/MySQL.
- Frontend web seguro con login y gestión de usuarios.
- Búsqueda avanzada por MAC, descripción, puerto, VLAN, etc.
- Visualización de históricos de cambios y resúmenes de actividad.
- Soporte para múltiples switches.
- Modo oscuro y claro en el frontend.

## Arquitectura

```
+-------------------+       +-------------------+       +-------------------+
|                   |       |                   |       |                   |
|   Switches Cisco  +------>+   Backend Python  +------>+   Base de Datos   |
|                   | Telnet|   (Netmiko)       |  SQL  |  (MariaDB/MySQL)  |
+-------------------+       +-------------------+       +-------------------+
                                                          ^
                                                          |
                                                +-------------------+
                                                |                   |
                                                |   Frontend PHP    |
                                                |  (Visualización)  |
                                                +-------------------+
```

## Instalación

### Requisitos

- Python 3.9+
- Netmiko, mariadb, pytz, zoneinfo
- Servidor web con PHP 7.4+ (Apache recomendado)
- MariaDB/MySQL

### Configuración de la Base de Datos

1. Ejecuta el script SQL para crear la base de datos y tablas.
2. Crea el usuario `logger` con permisos sobre la base de datos.

### Configuración del Backend (Python)

1. Copia y edita `devices.json` con la lista de switches y credenciales.
2. Instala dependencias Python:
   ```
   pip install netmiko mariadb pytz
   ```
3. Ejecuta el script principal:
   ```
   python Backend/Python/ciscoLogger_v6.py
   ```

### Configuración del Frontend (PHP)

1. Copia la carpeta `Frontend` a tu servidor web.
2. Configura los datos de conexión a la base de datos en los archivos PHP.
3. Accede a `http://<tu-servidor>/index.php`.

## Uso

- El acceso está protegido por login.
- El dashboard muestra pestañas por switch y el estado de sus interfaces.
- Búsquedas por MAC, descripción, histórico de puertos y estadísticas agregadas.
- El histórico permite ver cambios de estado, VLAN, descripción o MAC de cada puerto.

## Automatización y Limpieza

- El script `cleanup_old_data.py` elimina entradas antiguas del histórico.
- Se recomienda programar este script periódicamente.

## Estructura del Proyecto

```
ciscoLogger/
├── Backend/
│   ├── Python/
│   └── SQL/
├── Frontend/
│   ├── index.php
│   └── ciscoLogger/
└── readme.md
```

## Notas de Seguridad

- Contraseñas de usuarios hasheadas.
- Acceso a scripts PHP protegido por sesiones.
- Se recomienda usar HTTPS en producción.