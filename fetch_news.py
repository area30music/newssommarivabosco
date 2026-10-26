import urllib.request
import xml.etree.ElementTree as ET
import json
import datetime
import re

feeds = [
    {"name": "TargatoCN", "url": "https://www.targatocn.it/rss.xml", "limit": 3},
    {"name": "Gazzetta d'Alba", "url": "https://www.gazzettadalba.it/feed/", "limit": 3},
    {"name": "IdeaWebTV", "url": "https://www.ideawebtv.it/feed/", "limit": 3},
    {"name": "La Guida", "url": "https://www.laguida.it/feed/", "limit": 3}
]

all_news = []

# Notizia fissa iniziale del Comune di Sommariva
all_news.append({
    "source": "Sommariva News",
    "category": "Territorio",
    "title": "Aggiornamenti in tempo reale dal comune e dalle iniziative del territorio di Sommariva del Bosco",
    "image": "https://images.unsplash.com/photo-1585829365295-ab7cd400c167?auto=format&fit=crop&w=800&q=80",
    "link": "https://www.comune.sommarivadelbosco.cn.it/",
    "pubDate": datetime.datetime.now().isoformat()
})

DEFAULT_IMAGE = "https://images.unsplash.com/photo-1504711434969-e33886168f5c?auto=format&fit=crop&w=800&q=80"

for feed in feeds:
    try:
        req = urllib.request.Request(feed["url"], headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            xml_data = response.read()
            root = ET.fromstring(xml_data)
            
            items = root.findall('.//item')[:feed["limit"]]
            for item in items:
                title = item.find('title')
                link = item.find('link')
                pubDate = item.find('pubDate')
                description = item.find('description')
                
                # Gestione namespace content:encoded per le immagini
                encoded = item.find('{http://purl.org/rss/1.0/modules/content/}encoded')
                raw_text = (encoded.text if encoded is not None else "") + (description.text if description is not None else "")
                
                title_text = title.text if title is not None else ""
                link_text = link.text if link is not None else ""
                
                if not title_text or not link_text:
                    continue

                clean_title = title_text.strip()

                # Estrazione immagine reale (da enclosure o tag img nel testo)
                img_url = DEFAULT_IMAGE
                enclosure = item.find('enclosure')
                if enclosure is not None and enclosure.get('url'):
                    img_url = enclosure.get('url')
                else:
                    img_match = re.search(r'<img[^>]+src="([^">]+)"', raw_text)
                    if img_match:
                        img_url = img_match.group(1)

                # Categoria automatica
                t_lower = clean_title.lower()
                category = "Cronaca"
                if any(w in t_lower for w in ["calcio", "sport", "squadra", "volley", "partita"]):
                    category = "Sport"
                elif any(w in t_lower for w in ["vino", "fiera", "cibo", "ristorante", "tartufo", "mercato"]):
                    category = "Eventi & Food"
                elif any(w in t_lower for w in ["comune", "sindaco", "politica", "regione", "amministrazione"]):
                    category = "Territorio"
                elif any(w in t_lower for w in ["teatro", "mostra", "cultura", "libri", "spettacolo"]):
                    category = "Cultura"

                all_news.append({
                    "source": feed["name"],
                    "category": category,
                    "title": clean_title,
                    "image": img_url,
                    "link": link_text.strip(),
                    "pubDate": pubDate.text if pubDate is not None else datetime.datetime.now().isoformat()
                })
    except Exception as e:
        print(f"Errore feed {feed['name']}: {e}")

with open('news.json', 'w', encoding='utf-8') as f:
    json.dump(all_news, f, ensure_ascii=False, indent=2)