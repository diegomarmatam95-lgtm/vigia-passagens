import json, os, statistics, urllib.request, urllib.parse
from datetime import date, datetime, timezone

TOKEN = os.environ["TP_TOKEN"]
MARKER = os.environ.get("TP_MARKER", "")
cfg = json.load(open("config.json", encoding="utf-8"))
ARQ = "data/ofertas.json"

inicio = date.fromisoformat(cfg["data_inicio"])
fim = date.fromisoformat(cfg["data_fim"]) if cfg.get("data_fim") else None
desc_min = cfg.get("desconto_minimo_pct", 0)
teto = cfg.get("preco_max", 0)

def no_periodo(dia):
    return dia >= inicio.isoformat() and (not fim or dia <= fim.isoformat())

try:
    antigas = json.load(open(ARQ, encoding="utf-8"))
except Exception:
    antigas = []
salvas = {
    o["id"]: o for o in antigas
    if o["destino"] in cfg["destinos"] and no_periodo(o["ida"][:10])
}

def meses():
    ano, mes, n = inicio.year, inicio.month, 0
    while True:
        if fim:
            if (ano, mes) > (fim.year, fim.month):
                break
        elif n >= cfg["meses_a_frente"]:

            break
        yield f"{ano}-{mes:02d}"
        mes += 1
        if mes == 13:
            ano, mes = ano + 1, 1
        n += 1

for destino in cfg["destinos"]:
    for mes in meses():
        params = {
            "origin": cfg["origem"], "destination": destino,
            "departure_at": mes, "one_way": "false" if cfg["ida_e_volta"] else "true",
            "currency": cfg["moeda"], "sorting": "price", "limit": 1000, "token": TOKEN,
        }
        url = "https://api.travelpayouts.com/aviasales/v3/prices_for_dates?" + urllib.parse.urlencode(params)
        try:
            dados = json.load(urllib.request.urlopen(url, timeout=30)).get("data", [])
        except Exception as e:
            print("erro", destino, mes, e)
            continue
        precos = [d["price"] for d in dados]
        normal = statistics.median(precos) if len(precos) >= 5 else None
