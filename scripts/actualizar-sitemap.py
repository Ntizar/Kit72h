#!/usr/bin/env python3
"""Actualiza el sitemap con los nuevos artículos del blog."""
import os
import re

BLOG = 'blog'
SITEMAP = 'sitemap.xml'

with open(SITEMAP, 'r', encoding='utf-8') as f:
    sitemap = f.read()

existing = set()
for m in re.finditer(r'<loc>(.*?)</loc>', sitemap):
    url = m.group(1)
    if '/blog/' in url:
        existing.add(url)

today = '2026-10-01'
new_entries = []
for d in sorted(os.listdir(BLOG)):
    slug = d.lower()
    url = f'https://kit72h.com/blog/{slug}/'
    if url not in existing:
        entry = f'  <url><loc>{url}</loc><lastmod>{today}</lastmod><changefreq>yearly</changefreq><priority>0.7</priority></url>'
        new_entries.append(entry)
        print(f'Added: {url}')

if new_entries:
    insert_pos = sitemap.rfind('</urlset>')
    new_content = sitemap[:insert_pos] + '\n'.join(new_entries) + sitemap[insert_pos:]
    with open(SITEMAP, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print(f'Sitemap updated with {len(new_entries)} entries')
else:
    print('No new entries to add')