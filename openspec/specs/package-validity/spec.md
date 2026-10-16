# package-validity Specification

## Purpose

Define la fecha de compra de un paquete o mensualidad (cómo se registra y se corrige) y cómo se calcula a partir de ella la fecha de vencimiento que determina si el alumno puede hacer check-in.

## Requirements

### Requirement: Fecha de compra al vender
Al vender o renovar un paquete, el sistema SHALL permitir que recepción indique la fecha de compra. Si no se indica, la fecha de compra MUST ser la fecha de hoy (zona horaria de la academia).

#### Scenario: Venta sin cambiar la fecha
- **WHEN** el recepcionista registra una venta sin modificar el campo de fecha de compra
- **THEN** el paquete queda con fecha de compra igual a la fecha de hoy

#### Scenario: Venta registrada al día siguiente
- **WHEN** el 16 de octubre el recepcionista registra una venta indicando fecha de compra 15 de octubre
- **THEN** el paquete queda con fecha de compra 15 de octubre y su vencimiento se calcula desde esa fecha

#### Scenario: El formulario propone hoy por defecto
- **WHEN** el recepcionista abre el formulario de venta
- **THEN** el campo de fecha de compra muestra la fecha de hoy ya seleccionada

### Requirement: Editar la fecha de compra de un paquete vendido
El sistema SHALL permitir que recepción o administración cambie la fecha de compra de un paquete ya registrado. Solo la fecha de compra es editable por esta vía; alumno, plan, forma de pago y créditos MUST quedar sin cambios.

#### Scenario: Recepcionista corrige la fecha
- **WHEN** el recepcionista cambia la fecha de compra de un paquete existente y guarda
- **THEN** el paquete queda con la nueva fecha de compra y la tabla de paquetes la muestra

#### Scenario: Créditos no cambian al editar
- **WHEN** se edita la fecha de compra de un paquete Social con 3 créditos restantes
- **THEN** el paquete sigue con 3 créditos restantes

#### Scenario: Usuario sin permisos
- **WHEN** alguien sin sesión de recepción o administración intenta cambiar la fecha de compra
- **THEN** el sistema rechaza la petición y el paquete no cambia

#### Scenario: Fecha inválida
- **WHEN** se envía una fecha de compra vacía o con formato inválido
- **THEN** el sistema rechaza el cambio con un mensaje de error y el paquete no cambia

### Requirement: Vencimiento recalculado al cambiar la compra
La fecha de vencimiento SHALL calcularse siempre desde la fecha de compra vigente. Cada vez que cambie la fecha de compra, por cualquier medio (panel de recepción o admin), el sistema MUST recalcular el vencimiento.

#### Scenario: Recalculo al editar desde recepción
- **WHEN** se cambia la fecha de compra de un paquete Social del 10 de octubre al 8 de octubre
- **THEN** su vencimiento pasa del 9 de noviembre al 7 de noviembre

#### Scenario: Recalculo al editar desde el admin
- **WHEN** un administrador cambia la fecha de compra de un paquete desde el admin de Django
- **THEN** el vencimiento se recalcula con la misma regla

#### Scenario: Estado se actualiza
- **WHEN** un paquete vencido recibe una fecha de compra más reciente cuyo nuevo vencimiento es posterior a hoy
- **THEN** el paquete vuelve a estar activo y el alumno puede hacer check-in

### Requirement: Vencimiento de paquetes Social
Un paquete de categoría Social SHALL vencer el número configurado de días después de la fecha de compra (por defecto 30).

#### Scenario: Social con validez por defecto
- **WHEN** se vende un paquete Social con fecha de compra 15 de octubre
- **THEN** vence el 14 de noviembre

### Requirement: Vencimiento de mensualidades de Líneas
Una mensualidad de Líneas SHALL vencer el día 5 del mes siguiente al mes de la fecha de compra, sin importar el día del mes en que se compró.

#### Scenario: Compra al inicio del ciclo
- **WHEN** se vende una mensualidad de Líneas con fecha de compra 5 de septiembre
- **THEN** vence el 5 de octubre

#### Scenario: Compra antes del día 5
- **WHEN** se vende una mensualidad de Líneas con fecha de compra 3 de septiembre
- **THEN** vence el 5 de octubre

#### Scenario: Compra tardía en el mes
- **WHEN** se vende una mensualidad de Líneas con fecha de compra 20 de septiembre
- **THEN** vence el 5 de octubre

#### Scenario: Cambio de año
- **WHEN** se vende una mensualidad de Líneas con fecha de compra 15 de diciembre de 2026
- **THEN** vence el 5 de enero de 2027
