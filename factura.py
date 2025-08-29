from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
import os

INV_FILE = "inventario.txt"
FAC_FILE = "facturas.txt"
IVA_TASA = Decimal("0.19")

def money(value) -> Decimal:
    return (Decimal(str(value))).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

def input_no_vacio(msg: str) -> str:
    while True:
        s = input(msg).strip()
        if s:
            return s
        print("Entrada vacía, intenta de nuevo.")

def leer_lineas_seguras(path):
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        return [ln.strip() for ln in f if ln.strip()]

def escribir_lineas(path, lineas):
    with open(path, "w", encoding="utf-8") as f:
        for ln in lineas:
            f.write(ln.strip() + "\n")

def pausa():
    input("\nPresiona ENTER para continuar...")

def cargar_inventario():
    lineas = leer_lineas_seguras(INV_FILE)
    inv = {}
    for ln in lineas:
        try:
            pid, nombre, precio, stock = ln.split("|")
            inv[pid] = {
                "id": pid,
                "nombre": nombre,
                "precio": money(precio),
                "stock": int(stock),
            }
        except Exception:
            print(f"Línea inválida en inventario: {ln}")
    return inv

def guardar_inventario(inv):
    lineas = []
    for pid, p in inv.items():
        lineas.append(f'{p["id"]}|{p["nombre"]}|{money(p["precio"])}|{int(p["stock"])}')
    escribir_lineas(INV_FILE, lineas)

def inventario_listar():
    inv = cargar_inventario()
    if not inv:
        print("No hay productos en el inventario.")
        return
    print("\n=== Inventario ===")
    print(f'{"ID":<10} {"Nombre":<25} {"Precio":>10} {"Stock":>8}')
    for p in inv.values():
        print(f'{p["id"]:<10} {p["nombre"]:<25} {money(p["precio"]):>10} {p["stock"]:>8}')

def inventario_buscar():
    inv = cargar_inventario()
    if not inv:
        print("Inventario vacío.")
        return
    criterio = input_no_vacio("Buscar por ID o nombre contiene: ").lower()
    encontrados = [p for p in inv.values() if p["id"].lower() == criterio or criterio in p["nombre"].lower()]
    if not encontrados:
        print("Sin coincidencias.")
        return
    print("\nResultados:")
    for p in encontrados:
        print(f'- {p["id"]} | {p["nombre"]} | ${money(p["precio"])} | stock: {p["stock"]}')

def inventario_agregar():
    inv = cargar_inventario()
    pid = input_no_vacio("ID producto (único): ")
    if pid in inv:
        print("Ya existe un producto con ese ID.")
        return
    nombre = input_no_vacio("Nombre: ")
    try:
        precio = money(input_no_vacio("Precio (ej. 19999.99): "))
        if precio < 0:
            raise ValueError
    except Exception:
        print("Precio inválido.")
        return
    try:
        stock = int(input_no_vacio("Stock (entero >=0): "))
        if stock < 0:
            raise ValueError
    except Exception:
        print("Stock inválido.")
        return
    inv[pid] = {"id": pid, "nombre": nombre, "precio": precio, "stock": stock}
    guardar_inventario(inv)
    print("Producto agregado.")

def inventario_actualizar():
    inv = cargar_inventario()
    if not inv:
        print("Inventario vacío.")
        return
    pid = input_no_vacio("ID del producto a actualizar: ")
    if pid not in inv:
        print("No existe ese producto.")
        return
    p = inv[pid]
    print(f'Producto actual: {p["id"]} | {p["nombre"]} | ${money(p["precio"])} | stock {p["stock"]}')
    print("Qué desea actualizar?")
    print("1) Precio")
    print("2) Stock")
    op = input_no_vacio("> ")
    if op == "1":
        try:
            nuevo = money(input_no_vacio("Nuevo precio: "))
            if nuevo < 0:
                raise ValueError
            p["precio"] = nuevo
            guardar_inventario(inv)
            print("Precio actualizado.")
        except Exception:
            print("Precio inválido.")
    elif op == "2":
        try:
            nuevo = int(input_no_vacio("Nuevo stock: "))
            if nuevo < 0:
                raise ValueError
            p["stock"] = nuevo
            guardar_inventario(inv)
            print("Stock actualizado.")
        except Exception:
            print("Stock inválido.")
    else:
        print("Opción no válida.")

def inventario_eliminar():
    inv = cargar_inventario()
    if not inv:
        print("Inventario vacío.")
        return
    pid = input_no_vacio("ID del producto a eliminar: ")
    if pid not in inv:
        print("No existe ese producto.")
        return
    confirm = input_no_vacio(f"Confirma eliminar '{inv[pid]['nombre']}'? (s/n): ").lower()
    if confirm == "s":
        inv.pop(pid)
        guardar_inventario(inv)
        print("Producto eliminado.")
    else:
        print("Operación cancelada.")

def parse_items(cadena):
    items = []
    if not cadena:
        return items
    for chunk in cadena.split(";"):
        if not chunk.strip():
            continue
        try:
            pid, cant, precio = chunk.split("@")
            items.append({
                "id": pid,
                "cantidad": int(cant),
                "precio": money(precio)
            })
        except Exception:
            pass
    return items

def items_to_str(items):
    parts = []
    for it in items:
        parts.append(f'{it["id"]}@{int(it["cantidad"])}@{money(it["precio"])}')
    return ";".join(parts)

def cargar_facturas():
    lineas = leer_lineas_seguras(FAC_FILE)
    facs = []
    for ln in lineas:
        try:
            fid, fecha_iso, cliente, items_str, subtotal, iva, total = ln.split("|")
            facs.append({
                "id": fid,
                "fecha": fecha_iso,
                "cliente": cliente,
                "items": parse_items(items_str),
                "subtotal": money(subtotal),
                "iva": money(iva),
                "total": money(total),
            })
        except Exception:
            print(f"Línea inválida en facturas: {ln}")
    return facs

def guardar_facturas(facs):
    lineas = []
    for f in facs:
        lineas.append("|".join([
            f["id"],
            f["fecha"],
            f["cliente"],
            items_to_str(f["items"]),
            str(money(f["subtotal"])),
            str(money(f["iva"])),
            str(money(f["total"])),
        ]))
    escribir_lineas(FAC_FILE, lineas)

def calcular_totales(items):
    subtotal = sum((money(it["precio"]) * it["cantidad"] for it in items), Decimal("0.00"))
    subtotal = money(subtotal)
    iva = money(subtotal * IVA_TASA)
    total = money(subtotal + iva)
    return subtotal, iva, total

def descontar_stock(inv, items):
    for it in items:
        pid = it["id"]
        if pid not in inv:
            raise ValueError(f"Producto '{pid}' no existe.")
        if inv[pid]["stock"] < it["cantidad"]:
            raise ValueError(f"Stock insuficiente para '{inv[pid]['nombre']}'. Disponible: {inv[pid]['stock']}, requerido: {it['cantidad']}")
    for it in items:
        inv[it["id"]]["stock"] -= it["cantidad"]

def reponer_stock(inv, items):
    for it in items:
        if it["id"] in inv:
            inv[it["id"]]["stock"] += it["cantidad"]

def facturas_listar():
    facs = cargar_facturas()
    if not facs:
        print("No hay facturas registradas.")
        return
    print("\n=== Facturas ===")
    print(f'{"ID":<10} {"Fecha":<20} {"Cliente":<25} {"Total":>12}')
    for f in facs:
        print(f'{f["id"]:<10} {f["fecha"]:<20} {f["cliente"]:<25} {money(f["total"]):>12}')

def factura_detalle():
    facs = cargar_facturas()
    fid = input_no_vacio("ID de la factura: ")
    f = next((x for x in facs if x["id"] == fid), None)
    if not f:
        print("No existe esa factura.")
        return
    print("\n=== Detalle Factura ===")
    print(f'ID: {f["id"]}')
    print(f'Fecha: {f["fecha"]}')
    print(f'Cliente: {f["cliente"]}')
    print(f'Items:')
    inv = cargar_inventario()
    print(f'{"ProdID":<10} {"Nombre":<25} {"Cant":>5} {"P.Unit":>10} {"Importe":>12}')
    for it in f["items"]:
        nombre = inv.get(it["id"], {}).get("nombre", "(eliminado)")
        importe = money(it["precio"]) * it["cantidad"]
        print(f'{it["id"]:<10} {nombre:<25} {it["cantidad"]:>5} {money(it["precio"]):>10} {money(importe):>12}')
    print(f'\nSubtotal: {money(f["subtotal"])}')
    print(f'IVA 19%:  {money(f["iva"])}')
    print(f'Total:    {money(f["total"])}')

def factura_crear():
    inv = cargar_inventario()
    if not inv:
        print("No hay productos en inventario.")
        return
    fid = input_no_vacio("ID de factura (único): ")
    facs = cargar_facturas()
    if any(f["id"] == fid for f in facs):
        print("Ya existe una factura con ese ID.")
        return
    cliente = input_no_vacio("Nombre del cliente: ")
    items = []
    while True:
        pid = input("ID de producto (ENTER para terminar): ").strip()
        if not pid:
            break
        if pid not in inv:
            print("Producto no existe.")
            continue
        try:
            cant = int(input_no_vacio("Cantidad: "))
            if cant <= 0:
                raise ValueError
        except Exception:
            print("Cantidad inválida.")
            continue
        items.append({"id": pid, "cantidad": cant, "precio": money(inv[pid]["precio"])})
    if not items:
        print("No se agregaron items.")
        return
    try:
        descontar_stock(inv, items)
    except ValueError as e:
        print(f"{e}")
        return
    subtotal, iva, total = calcular_totales(items)
    factura = {
        "id": fid,
        "fecha": datetime.now().isoformat(timespec="seconds"),
        "cliente": cliente,
        "items": items,
        "subtotal": subtotal,
        "iva": iva,
        "total": total,
    }
    facs.append(factura)
    guardar_facturas(facs)
    guardar_inventario(inv)
    print("Factura creada correctamente.")
    factura_imprimir(factura, inv)

def factura_imprimir(f, inv=None):
    if inv is None:
        inv = cargar_inventario()
    print("\n--- FACTURA ---")
    print(f'ID: {f["id"]} | Fecha: {f["fecha"]} | Cliente: {f["cliente"]}')
    print(f'{"ProdID":<10} {"Nombre":<25} {"Cant":>5} {"P.Unit":>10} {"Importe":>12}')
    for it in f["items"]:
        nombre = inv.get(it["id"], {}).get("nombre", "(eliminado)")
        importe = money(it["precio"]) * it["cantidad"]
        print(f'{it["id"]:<10} {nombre:<25} {it["cantidad"]:>5} {money(it["precio"]):>10} {money(importe):>12}')
    print(f'\nSubtotal: {money(f["subtotal"])}')
    print(f'IVA 19%:  {money(f["iva"])}')
    print(f'Total:    {money(f["total"])}')
    print("---------------")

def factura_editar():
    facs = cargar_facturas()
    if not facs:
        print("No hay facturas.")
        return
    fid = input_no_vacio("ID de la factura a editar: ")
    idx = next((i for i, x in enumerate(facs) if x["id"] == fid), None)
    if idx is None:
        print("Factura no encontrada.")
        return
    inv = cargar_inventario()
    f = facs[idx]
    reponer_stock(inv, f["items"])
    print("Editando items. Los productos actuales fueron repuestos temporalmente en stock.")
    nuevos = []
    while True:
        pid = input("ID de producto (ENTER para terminar): ").strip()
        if not pid:
            break
        if pid not in inv:
            print("Producto no existe.")
            continue
        try:
            cant = int(input_no_vacio("Cantidad: "))
            if cant <= 0:
                raise ValueError
        except Exception:
            print("Cantidad inválida.")
            continue
        nuevos.append({"id": pid, "cantidad": cant, "precio": money(inv[pid]["precio"])})
    if not nuevos:
        print("No se agregaron items. Se restauran los originales.")
        try:
            descontar_stock(inv, f["items"])
        except Exception as e:
            print(f"Error al restaurar stock: {e}")
        guardar_inventario(inv)
        return
    try:
        descontar_stock(inv, nuevos)
    except ValueError as e:
        print(f"{e}")
        try:
            descontar_stock(inv, f["items"])
        except Exception as e2:
            print(f"Error al restaurar stock: {e2}")
        guardar_inventario(inv)
        return
    subtotal, iva, total = calcular_totales(nuevos)
    f["items"] = nuevos
    f["subtotal"] = subtotal
    f["iva"] = iva
    f["total"] = total
    facs[idx] = f
    guardar_facturas(facs)
    guardar_inventario(inv)
    print("Factura actualizada.")
    factura_imprimir(f, inv)

def factura_eliminar():
    facs = cargar_facturas()
    if not facs:
        print("No hay facturas.")
        return
    fid = input_no_vacio("ID de la factura a eliminar: ")
    idx = next((i for i, x in enumerate(facs) if x["id"] == fid), None)
    if idx is None:
        print("No existe esa factura.")
        return
    inv = cargar_inventario()
    reponer_stock(inv, facs[idx]["items"])
    del facs[idx]
    guardar_facturas(facs)
    guardar_inventario(inv)
    print("Factura eliminada y stock repuesto.")

def menu_inventario():
    while True:
        print("\n=== Gestión de Inventario ===")
        print("1) Añadir producto")
        print("2) Listar productos")
        print("3) Buscar producto (ID o nombre)")
        print("4) Actualizar precio/stock")
        print("5) Eliminar producto")
        print("0) Volver")
        op = input_no_vacio("> ")
        if op == "1":
            inventario_agregar()
            pausa()
        elif op == "2":
            inventario_listar()
            pausa()
        elif op == "3":
            inventario_buscar()
            pausa()
        elif op == "4":
            inventario_actualizar()
            pausa()
        elif op == "5":
            inventario_eliminar()
            pausa()
        elif op == "0":
            break
        else:
            print("Opción inválida.")

def menu_facturas():
    while True:
        print("\n=== Sistema de Facturación ===")
        print("1) Crear nueva factura")
        print("2) Listar facturas")
        print("3) Mostrar detalle de factura")
        print("4) Editar items de factura")
        print("5) Eliminar factura")
        print("0) Volver")
        op = input_no_vacio("> ")
        if op == "1":
            factura_crear()
            pausa()
        elif op == "2":
            facturas_listar()
            pausa()
        elif op == "3":
            factura_detalle()
            pausa()
        elif op == "4":
            factura_editar()
            pausa()
        elif op == "5":
            factura_eliminar()
            pausa()
        elif op == "0":
            break
        else:
            print("Opción inválida.")

def asegurar_archivos():
    if not os.path.exists(INV_FILE):
        with open(INV_FILE, "w", encoding="utf-8") as f:
            f.write("")
    if not os.path.exists(FAC_FILE):
        with open(FAC_FILE, "w", encoding="utf-8") as f:
            f.write("")

def main():
    asegurar_archivos()
    while True:
        print("\n===== Sistema Inventario & Facturación (TXT) =====")
        print("1) Inventario")
        print("2) Facturación")
        print("9) Ayuda / Formato de archivos")
        print("0) Salir")
        op = input_no_vacio("> ")
        if op == "1":
            menu_inventario()
        elif op == "2":
            menu_facturas()
        elif op == "9":
            print("Formato inventario: id|nombre|precio|stock")
            print("Formato facturas: id|fecha_iso|cliente|items|subtotal|iva|total")
            pausa()
        elif op == "0":
            print("Hasta luego")
            break
        else:
            print("Opción inválida.")

if __name__ == "__main__":
    main()
