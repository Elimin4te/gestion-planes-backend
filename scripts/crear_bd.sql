-- Script para crear base de datos con parametros de prueba (No seguros)

-- Crear el rol
CREATE ROLE planes WITH LOGIN PASSWORD 'Proyecto2025.';
ALTER ROLE planes WITH SUPERUSER;

-- Crear la base de datos
CREATE DATABASE unexca_planes WITH OWNER = planes ENCODING = 'UTF8';

-- Otorga privilegios al rol en la base de datos
GRANT ALL PRIVILEGES ON DATABASE unexca_planes TO planes;