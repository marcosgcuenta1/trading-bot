"""Fuentes de noticias cripto (feeds RSS públicos y gratuitos).

Empezamos solo con RSS porque es legal, gratis y sin claves. X/Twitter y Reddit
se pueden añadir después (requieren API de pago o autenticación).

Cada fuente da, por noticia: título, resumen, enlace y fecha de publicación.
"""
from __future__ import annotations

# (nombre, url_del_feed)
FEEDS_RSS: list[tuple[str, str]] = [
    ("CoinDesk", "https://www.coindesk.com/arc/outboundfeeds/rss/"),
    ("Cointelegraph", "https://cointelegraph.com/rss"),
    ("Decrypt", "https://decrypt.co/feed"),
    ("BitcoinMagazine", "https://bitcoinmagazine.com/feed"),
    ("CryptoSlate", "https://cryptoslate.com/feed/"),
    ("TheBlock", "https://www.theblock.co/rss.xml"),
]
