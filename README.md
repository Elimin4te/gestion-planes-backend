```markdown
# Gestión de Planes UNEXCA

Este proyecto tiene como objetivo desarrollar un sistema para la gestión de planes académicos en la **Universidad Nacional Experimental de la Gran Caracas (UNEXCA)**. El sistema permitirá la creación, modificación y consulta de planes de aprendizaje y evaluación, así como la generación de reportes en formato PDF.

## Instalación

Para instalar el sistema, sigue los siguientes pasos:

1.  **Clonar el repositorio:**

```bash
git clone https://[https://github.com/borkdude/html/blob/main/.dir-locals.el](https://github.com/borkdude/html/blob/main/.dir-locals.el)
```

2.  **Crear un entorno virtual (recomendado):**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

3.  **Instalar las dependencias:**

```bash
pip install -r requirements.txt
```

4.  **Configurar la base de datos:**

*   Asegúrate de tener **PostgreSQL** instalado y configurado.
*   Crea una base de datos con el nombre `unexca_planes`.
*   Configura los datos de conexión a la base de datos en el archivo `settings.py` de tu proyecto Django.

Para crear la base de datos y el rol de usuario en PostgreSQL, puedes utilizar el script `crear_bd_y_rol.sql`. Este script se conecta a la base de datos `postgres` (o una con privilegios de superusuario) y ejecuta las siguientes acciones:

*   Crea el rol `planes` con la contraseña `Proyecto2025`. (**¡Recuerda cambiarla por una contraseña segura!**)
*   Crea la base de datos `unexca_planes` y asigna el rol `planes` como propietario.
*   Otorga todos los privilegios al rol `planes` en la base de datos `unexca_planes`.

Para ejecutar el script, utiliza el siguiente comando:

```bash
psql -U postgres -d postgres -f crear_bd_y_rol.sql
```

Reemplaza `postgres` con el nombre del usuario con privilegios de superusuario que tengas en tu sistema.

5.  **Migrar la base de datos:**

```bash
python manage.py migrate
```

Este comando crea las tablas en la base de datos según los modelos definidos en tu aplicación Django.

6.  **Poblar la base de datos (opcional):**

Para poblar la base de datos con datos de prueba, puedes utilizar el script `crear_datos_de_prueba.py`. Este script utiliza el método `get_or_create` para crear un docente con los datos especificados o obtenerlo si ya existe. Luego, crea una unidad curricular, un plan de aprendizaje, 6 objetivos de aprendizaje y un plan de evaluación con 6 ítems de evaluación, todos ellos relacionados entre sí.

Para ejecutar el script, utiliza el siguiente comando:

```bash
python manage.py runscript crear_datos_de_prueba
```

7.  **Limpiar la base de datos (opcional):**

Para limpiar la base de datos y eliminar todos los datos, puedes utilizar el script `limpiar_bd.py`. Este script elimina todos los registros de las tablas de tu base de datos.

**¡Advertencia!** Este script eliminará todos los datos de tu base de datos. Asegúrate de que esto es lo que deseas hacer y de que tienes una copia de seguridad de tus datos si es necesario.

Para ejecutar el script, utiliza el siguiente comando:

```bash
python manage.py runscript limpiar_bd
```

**¡Listo!** Con estos pasos, tendrás el sistema de gestión de planes UNEXCA instalado y configurado en tu entorno local.
