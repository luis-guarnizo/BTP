# Spec Delta

## Purpose

Define cómo el personal de recepción y administración ve su sesión activa en el panel y cómo la cierra.

## ADDED Requirements

### Requirement: Cerrar sesión siempre visible en el panel
En todas las pantallas del panel de recepción, el sistema SHALL mostrar en la parte superior el usuario con sesión y un botón "Cerrar sesión" visible sin necesidad de desplazarse.

#### Scenario: Botón visible al entrar
- **WHEN** un recepcionista inicia sesión y entra a cualquier pantalla del panel
- **THEN** ve su nombre de usuario y el botón "Cerrar sesión" en la parte superior

#### Scenario: Pantalla angosta
- **WHEN** el panel se abre en una pantalla angosta (celular o tablet)
- **THEN** el botón "Cerrar sesión" sigue visible en la parte superior sin desplazarse

### Requirement: Cerrar sesión termina la sesión de recepción
Al usar "Cerrar sesión", el sistema SHALL terminar la sesión del personal y llevar a la pantalla de login de recepción; las pantallas del panel MUST dejar de ser accesibles hasta volver a iniciar sesión.

#### Scenario: Cierre de sesión exitoso
- **WHEN** el recepcionista pulsa "Cerrar sesión"
- **THEN** queda en la pantalla de login de recepción

#### Scenario: Volver atrás después de cerrar sesión
- **WHEN** después de cerrar sesión se intenta abrir una pantalla del panel
- **THEN** el sistema redirige a la pantalla de login de recepción
