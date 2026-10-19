# main.py
import sqlite3
import pickle
import validaciones as val

DB_NAME = "transporte_aereo.db"

# 1. FUNCIÓN: Inicialización de Base de Datos (5 tablas, >=5 campos, >=2 tipos de datos)
def inicializar_bd():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("PRAGMA foreign_keys = ON;")
        
        # Tabla 1: Aerolíneas
        cursor.execute("""CREATE TABLE IF NOT EXISTS aerolineas (
            id_aerolinea INTEGER PRIMARY KEY AUTOINCREMENT, nombre TEXT, codigo TEXT, pais TEXT, activo INTEGER)""")
        
        # Tabla 2: Aviones
        cursor.execute("""CREATE TABLE IF NOT EXISTS aviones (
            id_avion INTEGER PRIMARY KEY AUTOINCREMENT, modelo TEXT, capacidad INTEGER, id_aerolinea INTEGER, operativo INTEGER,
            FOREIGN KEY(id_aerolinea) REFERENCES aerolineas(id_aerolinea) ON DELETE CASCADE)""")
        
        # Tabla 3: Vuelos
        cursor.execute("""CREATE TABLE IF NOT EXISTS vuelos (
            id_vuelo INTEGER PRIMARY KEY AUTOINCREMENT, numero_vuelo TEXT, origen TEXT, destino TEXT, fecha TEXT, id_avion INTEGER,
            FOREIGN KEY(id_avion) REFERENCES aviones(id_avion) ON DELETE CASCADE)""")
        
        # Tabla 4: Pasajeros
        cursor.execute("""CREATE TABLE IF NOT EXISTS pasajeros (
            id_pasajero INTEGER PRIMARY KEY AUTOINCREMENT, nombre TEXT, pasaporte TEXT, edad INTEGER, nacionalidad TEXT)""")
        
        # Tabla 5: Reservas
        cursor.execute("""CREATE TABLE IF NOT EXISTS reservas (
            id_reserva INTEGER PRIMARY KEY AUTOINCREMENT, id_vuelo INTEGER, id_pasajero INTEGER, asiento TEXT, precio REAL, pago_confirmado INTEGER,
            FOREIGN KEY(id_vuelo) REFERENCES vuelos(id_vuelo) ON DELETE CASCADE,
            FOREIGN KEY(id_pasajero) REFERENCES pasajeros(id_pasajero) ON DELETE CASCADE)""")
        conn.commit()

# 2. FUNCIÓN: Operaciones CRUD Genéricas para acortar código
def ejecutar_crud(tabla):
    while True:
        print(f"\n--- Gestión de {tabla.upper()} ---")
        opc = input("1. Insertar\n2. Consultar Todo\n3. Actualizar Activo/Operativo\n4. Eliminar\n5. Volver\nSeleccione: ")
        
        try:
            with sqlite3.connect(DB_NAME) as conn:
                cursor = conn.cursor()
                if opc == "1" and tabla == "aerolineas":
                    nom, cod, pais = input("Nombre: "), input("Código: "), input("País: ")
                    if val.validar_texto(nom) and val.validar_texto(cod, 2):
                        cursor.execute("INSERT INTO aerolineas (nombre, codigo, pais, activo) VALUES (?, ?, ?, 1)", (nom, cod, pais))
                    else: print("¡Datos inválidos!")
                
                elif opc == "1" and tabla == "aviones":
                    mod, cap, aerolinea = input("Modelo: "), input("Capacidad: "), input("ID Aerolínea: ")
                    if val.validar_texto(mod) and val.validar_numero(cap) and val.validar_numero(aerolinea):
                        cursor.execute("INSERT INTO aviones (modelo, capacidad, id_aerolinea, operativo) VALUES (?, ?, ?, 1)", (mod, int(cap), int(aerolinea)))
                    else: print("¡Datos inválidos!")
                
                elif opc == "2":
                    cursor.execute(f"SELECT * FROM {tabla}")
                    for fila in cursor.fetchall(): print(fila)
                
                elif opc == "3":
                    id_reg = input("Ingrese ID a modificar estado: ")
                    nuevo_estado = input("Nuevo estado (1: Activo/Si, 0: Inactivo/No): ")
                    campo_estado = "activo" if tabla == "aerolineas" else "operativo"
                    if val.validar_numero(id_reg) and nuevo_estado in ["0", "1"]:
                        cursor.execute(f"UPDATE {tabla} SET {campo_estado} = ? WHERE id_{tabla[:-1]} = ?", (int(nuevo_estado), int(id_reg)))
                
                elif opc == "4":
                    id_reg = input("Ingrese ID a eliminar: ")
                    if val.validar_numero(id_reg):
                        cursor.execute(f"DELETE FROM {tabla} WHERE id_{tabla[:-1]} = ?", (int(id_reg),))
                
                elif opc == "5": break
                conn.commit()
        except sqlite3.Error as e: print(f"Error de Base de Datos: {e}")
        except Exception as e: print(f"Error inesperado: {e}")

# 3. FUNCIÓN: Menú de Consultas Complejas y Reportes TXT
def menu_consultas():
    print("\n--- CONSULTAS DE TRANSPORTE AÉREO ---")
    print("1. Ver Aviones por Aerolínea (JOIN)")
    print("2. Ver Reservas con Pasajeros y Vuelos (MULTI-JOIN)")
    opc = input("Seleccione consulta: ")
    
    query = ""
    if opc == "1":
        query = """SELECT ae.nombre, av.modelo, av.capacidad FROM aviones av 
                   JOIN aerolineas ae ON av.id_aerolinea = ae.id_aerolinea"""
    elif opc == "2":
        query = """SELECT p.nombre, v.numero_vuelo, r.asiento, r.precio FROM reservas r
                   JOIN pasajeros p ON r.id_pasajero = p.id_pasajero
                   JOIN vuelos v ON r.id_vuelo = v.id_vuelo"""
    else: return

    try:
        with sqlite3.connect(DB_NAME) as conn:
            res = conn.cursor().execute(query).fetchall()
            for fila in res: print(fila)
            
            if input("\n¿Desea guardar el resultado en reporte.txt? (s/n): ").lower() == 's':
                with open("reporte.txt", "w", encoding="utf-8") as f:
                    for fila in res: f.write(str(fila) + "\n")
                print("Guardado en reporte.txt")
    except sqlite3.Error as e: print(f"Error: {e}")

# 4. FUNCIÓN: Exportar Tablas (TXT o Pickle Binario)
def exportar_tabla():
    tabla = input("Tabla a exportar (aerolineas/aviones): ").lower()
    if tabla not in ["aerolineas", "aviones"]: return
    fmt = input("Formato de exportación (1: TXT, 2: Pickle Binario): ")
    
    try:
        with sqlite3.connect(DB_NAME) as conn:
            datos = conn.cursor().execute(f"SELECT * FROM {tabla}").fetchall()
            if fmt == "1":
                with open(f"export_{tabla}.txt", "w") as f:
                    for d in datos: f.write(f"{d}\n")
            elif fmt == "2":
                with open(f"export_{tabla}.pkl", "wb") as f:
                    pickle.dump(datos, f)
            print("¡Exportación exitosa!")
    except Exception as e: print(f"Error al exportar: {e}")

# FUNCIÓN MENÚ PRINCIPAL
def menu():
    inicializar_bd()
    while True:
        print("\n===== CONTROL DE OPERACIONES AÉREAS =====")
        print("1. Administrar Aerolíneas\n2. Administrar Aviones\n3. Consultas Avanzadas\n4. Exportar Datos\n5. Salir")
        opc = input("Seleccione una opción: ")
        if opc == "1": ejecutar_crud("aerolineas")
        elif opc == "2": ejecutar_crud("aviones")
        elif opc == "3": menu_consultas()
        elif opc == "4": exportar_tabla()
        elif opc == "5": break
        else: print("Opción inválida.")

if __name__ == "__main__":
    menu()
