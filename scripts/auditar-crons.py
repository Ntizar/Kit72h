#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Kit72h — auditor de crons: qué dispara cada job, con qué modelo y cuántos tokens.

Fuente: %LOCALAPPDATA%/hermes/cron/usage_audit.jsonl (una línea por run:
job_id, total_tokens, completion_tokens, model, duration_ms, error) cruzado con
%LOCALAPPDATA%/hermes/cron/jobs.json (nombre, horario, modelo anclado, estado).

Uso:
    python scripts/auditar-crons.py            # resumen de todos los jobs
    python scripts/auditar-crons.py --kit      # solo los kit72h
    python scripts/auditar-crons.py --runs     # detalle run a run
"""
import argparse
import collections
import json
import os
import sys

CRON = os.path.expandvars(r"%LOCALAPPDATA%\hermes\cron")


def cargar():
    with open(os.path.join(CRON, "jobs.json"), encoding="utf-8") as fh:
        jobs = json.load(fh)["jobs"]
    nombres = {j["id"]: j for j in jobs}
    agg = collections.defaultdict(lambda: dict(n=0, tot=0, comp=0, err=0,
                                               models=set(), ult=None, dur=0, runs=[]))
    with open(os.path.join(CRON, "usage_audit.jsonl"), encoding="utf-8") as fh:
        for linea in fh:
            linea = linea.strip()
            if not linea:
                continue
            e = json.loads(linea)
            a = agg[e["job_id"]]
            a["n"] += 1
            a["tot"] += e.get("total_tokens") or 0
            a["comp"] += e.get("completion_tokens") or 0
            a["dur"] += e.get("duration_ms") or 0
            a["err"] += 1 if e.get("error") else 0
            if e.get("model"):
                a["models"].add(e["model"])
            ts = e.get("ts")
            if a["ult"] is None or ts > a["ult"]:
                a["ult"] = ts
            a["runs"].append(e)
    return nombres, agg


def expr(j):
    s = j.get("schedule") or {}
    return s.get("expr", "?") if isinstance(s, dict) else str(s)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--kit", action="store_true", help="solo jobs kit72h")
    ap.add_argument("--runs", action="store_true", help="detalle run a run")
    args = ap.parse_args()

    if not os.path.isdir(CRON):
        sys.exit(f"No encuentro {CRON} — ¿estás en la máquina de Hermes?")

    nombres, agg = cargar()
    ids = set(agg)
    if args.kit:
        ids |= {jid for jid, j in nombres.items() if j.get("name", "").startswith("kit72h")}
    filas = [(jid, agg.get(jid, dict(n=0, tot=0, comp=0, err=0, models=set(),
                                     ult=None, dur=0, runs=[])))
             for jid in ids
             if (not args.kit or str(nombres.get(jid, {}).get("name", "")).startswith("kit72h"))]
    filas.sort(key=lambda kv: -kv[1]["tot"])

    ancho = max([len(str(nombres.get(jid, {}).get("name", jid))) for jid, _ in filas] + [10])
    print(f"{'CRON':{ancho}} | {'runs':>4} | {'err':>3} | {'tokens totales':>15} | {'media/run':>10} | modelo anclado")
    print("-" * (ancho + 62))
    total = 0
    for jid, a in filas:
        j = nombres.get(jid)
        nombre = j["name"] if j else f"{jid} [borrado]"
        modelo = (j.get("model") or "— (script, sin LLM)") if j else "—"
        estado = "" if j else "  ← job ya no existe"
        if j and j.get("state") == "paused":
            estado = "  ← PAUSADO"
        total += a["tot"]
        print(f"{nombre:{ancho}} | {a['n']:>4} | {a['err']:>3} | {a['tot']:>15,} | "
              f"{a['tot'] // max(a['n'], 1):>10,} | {modelo}{estado}")
    print("-" * (ancho + 62))
    print(f"{'TOTAL':{ancho}} | {sum(a['n'] for _, a in filas):>4} | "
          f"{sum(a['err'] for _, a in filas):>3} | {total:>15,} |")
    print(f"\n{len(filas)} jobs con registros de uso · desde el 27/08/2026 · "
          f"≈ {total / 1_000_000:.1f} M tokens")

    if args.runs:
        for jid, a in filas:
            j = nombres.get(jid)
            print(f"\n### {j['name'] if j else jid}  ({expr(j) if j else 'borrado'})")
            for e in sorted(a["runs"], key=lambda x: x.get("ts", ""))[-10:]:
                marca = "ERR" if e.get("error") else " ok"
                toks = (e.get("total_tokens") or 0)
                ms = (e.get("duration_ms") or 0)
                print(f"  {str(e.get('ts') or '')[:16]}  {marca}  {toks:>10,} "
                      f"tok  {e.get('model') or '-':<20} {ms // 1000:>4}s")


if __name__ == "__main__":
    main()
