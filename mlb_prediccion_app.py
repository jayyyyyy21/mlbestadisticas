
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import time

estadisticas_equipo = {}

def scrap_stat(url, nombre_columna, is_percentage=False):
    res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(res.text, "html.parser")
    table = soup.find("table", {"class": "tr-table datatable scrollable"})
    rows = table.find_all("tr")[1:]

    for row in rows:
        cols = row.find_all("td")
        if len(cols) < 2:
            continue
        equipo = cols[0].text.strip()
        val = cols[1].text.strip().replace('%','')
        try:
            val = float(val) / 100 if is_percentage else float(val)
        except:
            continue
        if equipo not in estadisticas_equipo:
            estadisticas_equipo[equipo] = {}
        estadisticas_equipo[equipo][nombre_columna] = val
    time.sleep(1)

urls = {
    "Promedio de bateo": "https://www.teamrankings.com/mlb/stat/batting-average",
    "Carreras por juego": "https://www.teamrankings.com/mlb/stat/runs-per-game",
    "OPS (slugging + OBP)": "https://www.teamrankings.com/mlb/stat/on-base-plus-slugging",
    "ERA del bullpen": "https://www.teamrankings.com/mlb/stat/earned-run-average",
    "WHIP del bullpen": "https://www.teamrankings.com/mlb/stat/walks-hits-per-inning",
    "Porcentaje de victorias": "https://www.teamrankings.com/mlb/stat/win-pct",
    "Errores defensivos por juego": "https://www.teamrankings.com/mlb/stat/errors-per-game"
}

for stat, url in urls.items():
    scrap_stat(url, stat, is_percentage=("porcentaje" in stat.lower()))

partidos = [
    ("Yankees", "Rays"), ("Astros", "White Sox"), ("Mets", "Cardinals"), ("Guardians", "Blue Jays"),
    ("Rockies", "Giants"), ("Padres", "Pirates"), ("Twins", "Red Sox"), ("Athletics", "Marlins"),
    ("Diamondbacks", "Phillies"), ("Nationals", "Reds"), ("Mariners", "Rangers"), ("Cubs", "Brewers"),
    ("Dodgers", "Braves"), ("Royals", "Orioles"), ("Tigers", "Angels")
]

rows = []
for equipo_a, equipo_b in partidos:
    partido = f"{equipo_a} vs {equipo_b}"
    for stat in urls.keys():
        val_a = estadisticas_equipo.get(equipo_a, {}).get(stat, None)
        val_b = estadisticas_equipo.get(equipo_b, {}).get(stat, None)
        if val_a is None or val_b is None:
            continue
        row = {
            "Partido": partido,
            "Estadística": stat,
            "Equipo A": round(val_a, 3),
            "Equipo B": round(val_b, 3),
            "Cuota A": 1.85 if stat == "Promedio de bateo" else None,
            "Cuota B": 2.10 if stat == "Promedio de bateo" else None
        }
        rows.append(row)

df = pd.DataFrame(rows)
fecha = datetime.today().strftime("%Y-%m-%d")
df.to_excel(f"estadisticas_MLB_{fecha}.xlsx", index=False)
print(f"Archivo generado: estadisticas_MLB_{fecha}.xlsx")
