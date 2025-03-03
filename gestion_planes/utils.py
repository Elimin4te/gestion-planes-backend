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
            for i in range(3):
                lineas[-1] = lineas[-1][:-3] + '...'

        return lineas

    else:
        return texto,


def dibujar_multi_linea(lienzo, lineas: tuple[str], x: int, y: int, interlinea: int = 12):
    """Escribe multiples lineas en el PDF."""
    for linea in lineas:
        lienzo.drawString(x, y, linea)
        y -= interlinea