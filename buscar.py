import json, os, urllib.request, urllib.parse
from datetime import date, datetime

TOKEN = os.environ["TP_TOKEN"]
MARKER = os.environ.get("TP_MARKER", "")
cfg = json.load(open("config.json", encoding="utf-8"))
ARQ = "data/ofertas.json"

try:
    salvas = {o["id"]: o for o in json.load(open(ARQ, encoding="utf-8"))}
except Exception:
    salvas = {}

def meses(n):
    h = date.today()
    for i in range(n):
        m = h.month - 1 + i
        yield f"{h.year + m // 12}-{m % 12 + 1:02d}"

for destino in cfg["destinos"]:
    for mes in meses(cfg["meses_a_frente"]):
        params = {
            "origin": cfg["origem"], "destination": destino,
            "departure_at": mes, "one_way": "false" if cfg["ida_e_volta"] else "true",
            "currency": cfg["moeda"], "sorting": "price", "limit": 10, "token": TOKEN,
        }
        url = "https://api.travelpayouts.com/aviasales/v3/prices_for_dates?" + urllib.parse.urlencode(params)
        try:
            dados = json.load(urllib.request.urlopen(url, timeout=30)).get("data", [])
        except Exception as e:
            print("erro", destino, mes, e)
            continue
        for d in dados:
            if d["price"] > cfg["preco_max"]:
                continue
            link = "https://www.aviasales.com" + d["link"]
            if MARKER:
                link += "&marker=" + MARKER
            oid = f'{d["origin"]}-{d["destination"]}-{d["departure_at"]}-{d.get("return_at","")}'
            antiga = salvas.get(oid, {})
            salvas[oid] = {
                "id": oid, "origem": d["origin"], "destino": d["destination"],
                "preco": d["price"], "moeda": cfg["moeda"].upper(),
                "ida": d["departure_at"], "volta": d.get("return_at"),
                "companhia": d.get("airline"), "escalas": d.get("transfers"),
                "link": link,
                "achado_em": antiga.get("achado_em", datetime.utcnow().isoformat(timespec="minutes")),
            }

hoje = date.today().isoformat()
lista = [o for o in salvas.values() if o["ida"][:10] >= hoje]
lista.sort(key=lambda o: o["preco"])
json.dump(lista, open(ARQ, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(len(lista), "ofertas salvas")
