

EL depósito de Logísitca (deposito al que van las cajas al hacer "send to archive") es el área del AR cuyo depósito es el mismo del usuario.

usuario -> tiene un area de revista y un depósito en donde luego de todo el flujo de movimientos la caja es archivada

AR ->  su área de revista es el depósito intermedio en donde quedan las cajas que él debe fajar y rotular para luego enviarlas al Archivo

todos los AR que tengan un deposito B deben tener como área la misma área A, entonces al "llegar" una caja al depósito intermedio A, cualquier AR puede tramitar el envío al archivo definitivo.

falta implementar reject close
y reject send to archive

Botones "negativos" pegados a la izquierda de los "positivos"
"volver" el primero a la izquierda
todos deberían estar alineados a la derecha

TODO: si elijo preview box y hago back no se carga el select con la opción que había elegido 

**Resumen de las Funcionalidades Implementadas en el Sistema _gestión_archivo_**<br>

1. **Gestión de Usuarios**
   - **Roles**:  
     - Normal (`'normal'`)
     - Manager (`'manager'`)
     - Archive Responsible (`'archive_responsible'`)
     - Admin (`'admin'`)
   - **CRUD de Usuarios**: Alta, baja, modificación, y eliminación.
   - **Importación de Usuarios** desde archivos CSV.
   - **Autenticación y Autorización**:
     - Solo los usuarios con rol **Admin** pueden ver y acceder a la configuración del sistema.
     - Implementación del **logout**.
     - Corrección de problemas de login y logout.

2. **Gestión de Áreas**
   - **CRUD de Áreas**: Alta, baja, modificación, y eliminación.
   - **Importación de Áreas** desde archivos CSV.

3. **Gestión de Documentación**
   - **Modelo `Documentation`**:
     - Atributos: `cuit_number`, `name`, `doc_type`, `description`, `corpus`, `sheets`, `created_by`, `creation_date`, `box`.
     - Relación con `Box` (cada caja puede tener múltiples documentos).
   - **Funcionalidad para Agregar Documentación** a una caja desde la vista `add_documentation`.
   - **Visualización de Documentos Asociados** a una caja en `main`.

4. **Gestión de Cajas**
   - **Modelo `Box`**:
     - Contiene atributos como `name`, `area`, `user`, `box_type`, `destruction_year`, `description`, y `status`.
   - **CRUD de Cajas** con formularios dinámicos.
   - **Generación de PDFs** al crear una caja.
   - **Vista Previa** de la caja antes de ser insertada en la base de datos.
   - **Botón de Paginación y Búsqueda** en `create_box` para las cajas abiertas.
   - **Botón para Agregar Documentación** en las cajas abiertas (`main`), visible solo si el estado de la caja es **Open**.

5. **Gestión de Tipos de Caja y Documentación**
   - **Modelo `BoxType`** y **`DocType`** con restricciones de unicidad insensibles a mayúsculas.
   - **CRUD de Tipos de Caja y Documentación**.
   - **Filtros Dinámicos** en los campos `<select>` usando **Bootstrap Dropdown** y **JavaScript**.

6. **Configuración del Sistema**
   - **Modelo `SystemConfig`** para gestionar claves, valores y descripciones.
   - **Vista `config_keys_values`** para administrar la configuración del sistema:
     - Funcionalidad de **Agregar, Editar, y Eliminar** configuraciones.
     - La vista utiliza la plantilla `base.html`.

7. **Registro de Movimientos (`BoxLog`)**
   - **Modelo `BoxLog`** para registrar cambios en una caja:
     - Atributos: `log_type`, `box`, `area_origin`, `area_destination`, `doc_added`, `doc_removed`, `previous_status`, `new_status`, `observations`, `user`, `user_area`, `log_date`.
   - **Automatización del Registro**:
     - Se registra automáticamente cuando se agregan o eliminan documentos, o cuando una caja cambia de área.

8. **Interfaz de Usuario con Bootstrap**
   - **Uso de Bootstrap 5** para diseñar interfaces atractivas y responsivas.
   - **Botones con Íconos** de Bootstrap para acciones como **Edit**, **Delete**, y **Save**.
   - **Plantilla `base.html`** como estructura principal para todas las vistas.

9. **Optimización del Código**
   - Reducción y optimización de **importaciones duplicadas**.
   - Inclusión de **teclas rápidas** y funcionalidades de accesibilidad en el diseño.

10. **Otros Ajustes y Correcciones**
   - **Redirección de `/` a `main`**.
   - **Mensajes de Error Personalizados** cuando no hay elementos en las tablas.
   - **Filtros de Búsqueda y Ordenación** en las tablas de cajas abiertas.
   - Corrección de errores y mejoras generales en el flujo del sistema.

✅ **Estado Actual**
El sistema **gestión_archivo** tiene implementadas las principales funcionalidades para la gestión de usuarios, áreas, cajas, documentación, configuraciones y logs de movimiento, con una interfaz robusta y fácil de usar gracias a **Bootstrap** y **JavaScript**.




en View box: ver que si esta <> open, no se puede editar la caja.
