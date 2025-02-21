-- Script para crear base de datos con parametros de prueba (No seguros)

-- Crear el rol si no existe
IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'planes') THEN
  CREATE ROLE planes WITH LOGIN PASSWORD 'Proyecto2025.';
  ALTER ROLE planes WITH SUPERUSER; -- O los privilegios específicos que necesites
  RAISE NOTICE 'Rol "planes" creado.';
ELSE
  RAISE NOTICE 'Rol "planes" ya existe.';
END IF;

-- Crear la base de datos si no existe
IF NOT EXISTS (SELECT 1 FROM pg_database WHERE datname = 'unexca_planes') THEN
  CREATE DATABASE unexca_planes WITH OWNER = planes ENCODING = 'UTF8'; -- Ajusta la codificación si es necesario
  RAISE NOTICE 'Base de datos "unexca_planes" creada.';
ELSE
  RAISE NOTICE 'Base de datos "unexca_planes" ya existe.';
END IF;

-- Otorga privilegios al rol en la base de datos
GRANT ALL PRIVILEGES ON DATABASE unexca_planes TO planes;