import os


def procesar_archivo(ruta, espacios_por_tab=4):
	with open(ruta, "rb") as f:
		contenido_binario = f.read()

	contenido_binario = contenido_binario.replace(b"\r\n", b"\n")

	try:
		contenido = contenido_binario.decode("utf-8")
	except UnicodeDecodeError:
		print(f"⚠ Error de codificación en {ruta}, omitido.")
		return

	lineas = contenido.splitlines()

	nuevas_lineas = []
	for linea in lineas:
		espacios = len(linea) - len(linea.lstrip(" "))
		tabs = espacios // espacios_por_tab
		nueva_linea = "\t" * tabs + linea.lstrip(" ")
		nuevas_lineas.append(nueva_linea)

	resultado = "\n".join(nuevas_lineas) + "\n"

	with open(ruta, "w", encoding="utf-8", newline="\n") as f:
		f.write(resultado)


# Cambia esta ruta si quieres limitar aún más
directorio_objetivo = "."

extensiones_objetivo = {".py", ".ps1", ".md"}
procesados = []

for root, _, archivos in os.walk(directorio_objetivo):
	if ".venv" in root or "site-packages" in root:
		continue  # evitar entornos virtuales
	for archivo in archivos:
		if any(archivo.endswith(ext) for ext in extensiones_objetivo):
			ruta = os.path.join(root, archivo)
			procesar_archivo(ruta)
			procesados.append(ruta)

print(f"✔ Archivos procesados: {len(procesados)}")
