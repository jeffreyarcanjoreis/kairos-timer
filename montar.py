"""Gera a versão instalável (PWA) do Kairos Timer a partir de app.html.

Uso: python montar.py
Saída: index.html, manifest.webmanifest, sw.js e icons/*.png (sem dependências externas).
"""
import hashlib
import json
import math
import struct
import zlib
from pathlib import Path

RAIZ = Path(__file__).parent
FUNDO = (0x14, 0x13, 0x0F)   # void
OSSO = (0xF0, 0xEB, 0xE0)    # bone
ARGILA = (0xC2, 0x61, 0x3F)  # clay


# ---------------- ícones (PNG desenhado à mão, com antisserrilhado) ----------------
def _cor(x, y):
    """x, y em 0..1. Devolve a cor do ponto: aro e botão em osso, fatia em argila, ou None (fundo)."""
    cx, cy = 0.5, 0.54
    dx, dy = x - cx, y - cy
    r = math.hypot(dx, dy)
    # aro
    if 0.265 <= r <= 0.315:
        return OSSO
    # botão de cima
    if abs(x - cx) <= 0.05 and 0.17 <= y <= 0.22:
        return OSSO
    if abs(x - cx) <= 0.02 and 0.2 <= y <= 0.24:
        return OSSO
    # fatia (intervalo) de 12h até 4h no sentido horário
    if r <= 0.2:
        ang = (math.degrees(math.atan2(dx, -dy)) + 360) % 360
        if ang <= 120:
            return ARGILA
    # ponto central
    return OSSO if r <= 0.03 else None


def _png(tam):
    ss = 3
    linhas = []
    for py in range(tam):
        linha = bytearray([0])
        for px in range(tam):
            soma = [0, 0, 0]
            for sy in range(ss):
                for sx in range(ss):
                    c = _cor((px + (sx + 0.5) / ss) / tam, (py + (sy + 0.5) / ss) / tam) or FUNDO
                    for i in range(3):
                        soma[i] += c[i]
            linha += bytes(round(v / (ss * ss)) for v in soma)
        linhas.append(bytes(linha))
    bruto = zlib.compress(b"".join(linhas), 9)

    def bloco(tipo, dados):
        return struct.pack(">I", len(dados)) + tipo + dados + struct.pack(">I", zlib.crc32(tipo + dados) & 0xFFFFFFFF)

    return (b"\x89PNG\r\n\x1a\n" + bloco(b"IHDR", struct.pack(">IIBBBBB", tam, tam, 8, 2, 0, 0, 0))
            + bloco(b"IDAT", bruto) + bloco(b"IEND", b""))


def gerar_icones():
    pasta = RAIZ / "icons"
    pasta.mkdir(exist_ok=True)
    for tam in (180, 192, 512):
        destino = pasta / f"icon-{tam}.png"
        if not destino.exists():
            destino.write_bytes(_png(tam))


# ---------------- página ----------------
CABECA = """<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<link rel="manifest" href="manifest.webmanifest">
<link rel="icon" type="image/png" sizes="192x192" href="icons/icon-192.png">
<link rel="apple-touch-icon" href="icons/icon-180.png">
<meta name="apple-mobile-web-app-title" content="Kairos Timer">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="mobile-web-app-capable" content="yes">
<style>:root{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}body{margin:0}</style>
"""


def gerar_pagina():
    corpo = (RAIZ / "app.html").read_text(encoding="utf-8")
    # o <title>, os <meta> e o <style> do app ficam no <head>; o resto vai no <body>
    corte = corpo.index("<main>")
    pagina = CABECA + corpo[:corte] + "</head>\n<body>\n" + corpo[corte:] + "\n</body>\n</html>\n"
    (RAIZ / "index.html").write_text(pagina, encoding="utf-8")
    return hashlib.sha256(pagina.encode("utf-8")).hexdigest()[:10]


MANIFESTO = {
    "name": "Kairos Timer",
    "short_name": "Kairos Timer",
    "description": "Cronômetro de intervalos: Tabata, EMOM, blocos e circuitos com bipes.",
    "lang": "pt-BR",
    "start_url": "./",
    "scope": "./",
    "display": "standalone",
    "orientation": "any",
    "background_color": "#14130f",
    "theme_color": "#14130f",
    "icons": [
        {"src": "icons/icon-192.png", "sizes": "192x192", "type": "image/png", "purpose": "any"},
        {"src": "icons/icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any"},
        {"src": "icons/icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"},
    ],
}

SW = """// Gerado por montar.py — não editar à mão.
const VERSAO = 'kairos-timer-%s';
const ARQUIVOS = ['./', './index.html', './manifest.webmanifest', './icons/icon-180.png', './icons/icon-192.png', './icons/icon-512.png'];
const FONTES = 'kairos-timer-fontes';

self.addEventListener('install', ev => {
  ev.waitUntil(caches.open(VERSAO).then(c => c.addAll(ARQUIVOS)).then(() => self.skipWaiting()));
});
self.addEventListener('activate', ev => {
  ev.waitUntil(caches.keys()
    .then(ks => Promise.all(ks.filter(k => k !== VERSAO && k !== FONTES).map(k => caches.delete(k))))
    .then(() => self.clients.claim()));
});
self.addEventListener('fetch', ev => {
  const req = ev.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);
  if (url.hostname === 'fonts.googleapis.com' || url.hostname === 'fonts.gstatic.com') {
    ev.respondWith(caches.open(FONTES).then(async c => {
      const salvo = await c.match(req);
      const rede = fetch(req).then(r => { if (r.ok || r.type === 'opaque') c.put(req, r.clone()); return r; }).catch(() => salvo);
      return salvo || rede;
    }));
    return;
  }
  if (url.origin !== self.location.origin) return;
  ev.respondWith(caches.match(req, { ignoreSearch: true }).then(salvo => salvo ||
    fetch(req).catch(() => req.mode === 'navigate' ? caches.match('./index.html') : Response.error())));
});
"""


def main():
    gerar_icones()
    versao = gerar_pagina()
    (RAIZ / "manifest.webmanifest").write_text(json.dumps(MANIFESTO, ensure_ascii=False, indent=2), encoding="utf-8")
    (RAIZ / "sw.js").write_text(SW % versao, encoding="utf-8")
    print("pronto, versão", versao)


if __name__ == "__main__":
    main()
