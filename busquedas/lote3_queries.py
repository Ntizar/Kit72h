
import json, sys, time
sys.path.insert(0, "C:/Users/d_ant/Projects/kit72h/busquedas")
from buscar3 import search

productos = [
 (34, "encendedor cerillas largas"),
 (35, "nevera portatil conservas 12v"),
 (36, "caja fuerte portatil pequeña efectivo"),
 (37, "radio fm am pilas dinamamo"),
 (38, "triangulos emergencia homologados pack"),
 (39, "baliza V16 conectada homologada"),
 (40, "botiquin coche"),
 (41, "manta termica emergencia"),
 (42, "linterna LED iman"),
 (43, "correa remolque coche cadena tiro"),
 (44, "cadenas nieve coche"),
 (45, "arrancador coche 12V powerbank"),
 (46, "agua mineral pack 24 botellas"),
 (47, "barritas energeticas pack"),
 (48, "garrafa agua 8 litros"),
 (49, "pack conservas variadas latas"),
 (50, "pack arroz pasta legumbres paquetes"),
]

out = {}
for num, q in productos:
    try:
        r = search(q)
    except Exception as e:
        r = None
    out[num] = {"q": q, "items": r}
    print(num, q, "->", len(r) if r else "FAIL", flush=True)
    time.sleep(1.5)

open("C:/Users/d_ant/Projects/kit72h/busquedas/lote3_raw.json","w",encoding="utf-8").write(json.dumps(out, ensure_ascii=False, indent=1))
print("DONE")
