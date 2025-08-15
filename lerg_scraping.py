import requests
from bs4 import BeautifulSoup
import csv
from datetime import datetime
import os
import getpass

BASE_URL = "https://localcallingguide.com/lca_prefix.php"
PARAMS = {
    "pastdays": 7,
    "nextdays": 0,
    "page": 1
}



def extract_table_data(soup):
    data = []
    table = soup.find("table")
    if not table:
        return data

    for row in table.find_all("tr"):
        cols = row.find_all("td")
        if len(cols) == 10:
            cells = [col.get_text(strip=True) for col in cols]
            data.append(cells)
    return data

def scrape_all_pages():
    usuario = getpass.getuser()
    print(f"Saasa Systems™ - Verve LERG scraping tool\n Welcome {usuario}!")
    all_data = []
    while True:
        print(f"🔎 Scraping page {PARAMS['page']}...")
        response = requests.get(BASE_URL, params=PARAMS)
        soup = BeautifulSoup(response.text, "html.parser")
        page_data = extract_table_data(soup)
        if not page_data:
            break
        all_data.extend(page_data)
        PARAMS["page"] += 1
    return all_data


def procesar_datos(data):
    datos_finales = []
    for row in data:
        col1 = row[0].replace("-", "")[:6]
        col2 = row[1]

        if col2.isdigit():
            comb = col1 + col2
            new_row = [comb] + [row[i] for i in range(2, 10) if i not in [4, 7, 8, 9]]

            ocn_original = new_row[3]
            ocn_part = ocn_original[:4]
            category_part = ocn_original[4:] if len(ocn_original) > 4 else ""
            category_part = category_part.replace(",", "").lstrip()

            new_row[3] = ocn_part          #OCN
            new_row.insert(4, category_part)  #category 
            new_row.append("UNKNOWN")     #endoffice

            fila_ordenada = [
                new_row[0],  #NPA-NXX+BLOCK
                new_row[2],  #Region
                new_row[5],  #LATA
                new_row[3],  #OCN
                new_row[6],  #endoffice
                new_row[1],  #Rate Centre
                new_row[4],  #category
            ]

            datos_finales.append(fila_ordenada)
    return datos_finales
def save_to_csv(data):
    headers = ["npanxx", "state", "lata", "ocn", "endoffice", "rclata", "category"]

    fecha_actual = datetime.today().strftime("%Y%m%d%H%M%S")
    nombre = f"lerg_npanxx_{fecha_actual}.csv"

    with open(nombre, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(data) 
        print(f"✅ File {nombre} has been created.")

def create_rate_file(data):
    headers = [
        "Mask", "Rate", "Inter", "Intra", "DNIS"
    ]
    fecha_actual = datetime.today().strftime("%Y%m%d%H%M%S")
    nombre = f"lerg_rate_{fecha_actual}.csv"

    registros_vistos = set()
    filas = []
    
    for fila in data:
        npanxx_raw = fila[0]
        rclata_value = fila[5]
        dnis_modificado = f"1{npanxx_raw[:6]}"

        if dnis_modificado in registros_vistos:
            continue
        registros_vistos.add(dnis_modificado)

        nueva_fila = [
            rclata_value, "0.0523", "0.0523", "0.0523", dnis_modificado
        ]
        filas.append(nueva_fila)

    with open(nombre, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(filas)

    print(f"🚫 Duplicated entries removed.\n✅ File {nombre} has been created with {len(filas)} unique rows.")

def esperar_salida(msg="\nPress any key to exit"):
    try:
        if os.name == "nt":
            import msvcrt
            print(msg)
            msvcrt.getch()  
        else:
            input("\nPress Enter to exit...")
    except Exception:
        pass

if __name__ == "__main__":
    try:
        datos = scrape_all_pages()
        print(f"📄 {len(datos)} rows")
        datos_finales = procesar_datos(datos)
        print(f"🧹 {len(datos_finales)} valid and processed rows.")
        save_to_csv(datos_finales)
        create_rate_file(datos_finales)
        path = os.getcwd()
        print(f"📁 Files saved in {path}")
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
    finally:
        esperar_salida()


