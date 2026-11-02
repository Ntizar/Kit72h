#!/usr/bin/env python3
"""Runner para analizar_paginas sin ejecutar main()"""
import importlib.util
import sys

spec = importlib.util.spec_from_file_location("seo_ctr", "scripts/kit72h-seo-ctr.py")
seo_ctr = importlib.util.module_from_spec(spec)
sys.modules['seo_ctr'] = seo_ctr
spec.loader.exec_module(seo_ctr)

if hasattr(seo_ctr, 'analizar_paginas'):
    seo_ctr.analizar_paginas()
else:
    print("Error: analizar_paginas no encontrado en seo_ctr")
    sys.exit(1)

print("SEO analysis complete.")