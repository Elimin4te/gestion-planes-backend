def ajustar_texto_pdf(texto: str, max_caracteres: int, max_lineas: int = 4, elipsis: bool = False) -> tuple[str]:
    """Funcion para ajustar los textos a las columnas de los formatos pdf."""
    if len(texto) > max_caracteres:
        # Puntos suspensivos si el texto es muy largo.
        if elipsis:
            texto = texto[:max_caracteres]
            texto = texto[:-3] + '...'
            return texto,

        lineas = []
        palabras = texto.split()
        linea_actual = ""

        for palabra in palabras:
            if len(linea_actual) + len(palabra) + 1 <= max_caracteres:
                if linea_actual:
                    linea_actual += " " + palabra
                else:
                    linea_actual = palabra
            else:
                lineas.append(linea_actual)
                linea_actual = palabra

        if linea_actual:
            lineas.append(linea_actual)

        if len(lineas) > max_lineas:
            lineas[max_lineas-1] = ' '.join(lineas[max_lineas-1].split(' ')[:-1]) + '...'
            lineas = lineas[:max_lineas]

        return lineas

    else:
        return texto,


def dibujar_multi_linea(lienzo, lineas: tuple[str], x: int, y: int, interlinea: int = 12):
    """Escribe multiples lineas en el PDF."""
    for linea in lineas:
        lienzo.drawString(x, y, linea)
        y -= interlinea


def obtener_valores_de_opciones(opciones: list[tuple[str, str]]) -> tuple[str]:
    """Devuelve los valores que se utilizan en la base de datos para una lista de opciones."""
    return [opt[0] for opt in opciones]