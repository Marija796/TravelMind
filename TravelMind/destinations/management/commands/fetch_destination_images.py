"""
Fetches correct destination images from Wikipedia using BATCHED API calls.
All 100 primary titles are fetched in 2 requests (50 per batch).
All 100 secondary/landmark titles are fetched in 2 requests.
Total: 4 HTTP requests → no rate-limit issues.

Usage:
    python manage.py fetch_destination_images
"""
import time
import requests
from django.core.management.base import BaseCommand
from destinations.models import Destination

WIKI_API = 'https://en.wikipedia.org/w/api.php'
HEADERS  = {'User-Agent': 'TravelMind/1.0 (educational travel web app)'}

# Wikipedia article title used for each destination's MAIN overview image.
PRIMARY_TITLES = {
    # Europe
    'Paris':              'Paris',
    'Rome':               'Rome',
    'Barcelona':          'Barcelona',
    'Amsterdam':          'Amsterdam',
    'Prague':             'Prague',
    'Vienna':             'Vienna',
    'Budapest':           'Budapest',
    'London':             'London',
    'Berlin':             'Berlin',
    'Lisbon':             'Lisbon',
    'Santorini':          'Santorini',
    'Amalfi Coast':       'Amalfi Coast',
    'Dubrovnik':          'Dubrovnik',
    'Lake Bled':          'Lake Bled',
    'Hallstatt':          'Hallstatt',
    'Interlaken':         'Interlaken',
    'Zermatt':            'Zermatt',
    'Dolomites':          'Dolomites',
    'Norwegian Fjords':   'Geirangerfjord',
    'Scottish Highlands': 'Scottish Highlands',
    'Algarve':            'Algarve',
    'Cinque Terre':       'Cinque Terre',
    'Cappadocia':         'Cappadocia',
    'Istanbul':           'Istanbul',
    'Mykonos':            'Mykonos',
    'Plitvice Lakes':     'Plitvice Lakes National Park',
    'Athens':             'Athens',
    'Kotor':              'Kotor',
    'Bruges':             'Bruges',
    'Porto':              'Porto',
    # Asia
    'Tokyo':              'Tokyo',
    'Kyoto':              'Kyoto',
    'Osaka':              'Osaka',
    'Bali':               'Bali',
    'Singapore':          'Singapore',
    'Phuket':             'Phuket',
    'Chiang Mai':         'Chiang Mai',
    'Maldives':           'Maldives',
    'Bangkok':            'Bangkok',
    'Hong Kong':          'Hong Kong',
    'Seoul':              'Seoul',
    'Hanoi':              'Hanoi',
    'Hoi An':             'Hoi An Ancient Town',
    'Siem Reap':          'Angkor Wat',
    'Dubai':              'Dubai',
    'Marrakech':          'Marrakesh',
    'Cairo':              'Cairo',
    'Petra':              'Petra, Jordan',
    'Fez':                'Fez, Morocco',
    'Zanzibar':           'Zanzibar',
    'Luang Prabang':      'Luang Prabang',
    'Goa':                'Goa',
    'Kathmandu':          'Kathmandu',
    'Tbilisi':            'Tbilisi',
    'Bagan':              'Bagan',
    # Americas
    'New York City':      'New York City',
    'San Francisco':      'San Francisco',
    'New Orleans':        'New Orleans',
    'Miami':              'Miami',
    'Las Vegas':          'Las Vegas',
    'Machu Picchu':       'Machu Picchu',
    'Rio de Janeiro':     'Rio de Janeiro',
    'Buenos Aires':       'Buenos Aires',
    'Cartagena':          'Cartagena, Colombia',
    'Mexico City':        'Mexico City',
    'Cancún':             'Cancun',
    'Tulum':              'Tulum',
    'Havana':             'Havana',
    'Banff':              'Banff National Park',
    'Patagonia':          'Torres del Paine National Park',
    'Galápagos Islands':  'Galapagos Islands',
    'Iguazu Falls':       'Iguazu Falls',
    'Sedona':             'Sedona, Arizona',
    'Vancouver':          'Vancouver',
    'Medellín':           'Medellin',
    # Africa
    'Cape Town':          'Cape Town',
    'Masai Mara Safari':  'Maasai Mara',
    'Kilimanjaro':        'Mount Kilimanjaro',
    'Serengeti':          'Serengeti',
    'Victoria Falls':     'Victoria Falls',
    # Oceania
    'Sydney':             'Sydney',
    'Queenstown':         'Queenstown, New Zealand',
    'Fiji':               'Fiji',
    'Seychelles':         'Seychelles',
    'Bora Bora':          'Bora Bora',
    'Great Barrier Reef': 'Great Barrier Reef',
    'Melbourne':          'Melbourne',
    # Nordic / Atlantic
    'Reykjavik':          'Reykjavik',
    'Faroe Islands':      'Faroe Islands',
    'Lofoten Islands':    'Lofoten',
    'Azores':             'Azores',
    # Italy extras
    'Lake Como':          'Lake Como',
    'Portofino':          'Portofino',
    'Valletta':           'Valletta',
    'Tuscany':            'Tuscany',
    # Others
    'Monaco':             'Monaco',
    'Ibiza':              'Ibiza',
    'Napa Valley':        'Napa Valley',
    'Rotorua':            'Rotorua',
    'Cusco':              'Cusco',
}

# Wikipedia article for each destination's SECONDARY (landmark) image.
SECONDARY_TITLES = {
    'Paris':              'Eiffel Tower',
    'Rome':               'Colosseum',
    'Barcelona':          'Sagrada Familia',
    'Amsterdam':          'Rijksmuseum',
    'Prague':             'Charles Bridge',
    'Vienna':             'Schonbrunn Palace',
    'Budapest':           'Hungarian Parliament Building',
    'London':             'Tower Bridge',
    'Berlin':             'Brandenburg Gate',
    'Lisbon':             'Alfama',
    'Santorini':          'Oia, Santorini',
    'Amalfi Coast':       'Positano',
    'Dubrovnik':          'Walls of Dubrovnik',
    'Lake Bled':          'Bled Castle',
    'Hallstatt':          'Hallstatt',
    'Interlaken':         'Jungfraujoch',
    'Zermatt':            'Matterhorn',
    'Dolomites':          'Tre Cime di Lavaredo',
    'Norwegian Fjords':   'Naeroyfjord',
    'Scottish Highlands': 'Loch Ness',
    'Algarve':            'Ponta da Piedade',
    'Cinque Terre':       'Vernazza',
    'Cappadocia':         'Goreme',
    'Istanbul':           'Hagia Sophia',
    'Mykonos':            'Mykonos',
    'Plitvice Lakes':     'Plitvice Lakes National Park',
    'Athens':             'Parthenon',
    'Kotor':              'Bay of Kotor',
    'Bruges':             'Belfry of Bruges',
    'Porto':              'Dom Luis I Bridge',
    'Tokyo':              'Shibuya',
    'Kyoto':              'Fushimi Inari-taisha',
    'Osaka':              'Dotonbori',
    'Bali':               'Tanah Lot',
    'Singapore':          'Marina Bay Sands',
    'Phuket':             'Maya Bay',
    'Chiang Mai':         'Doi Suthep',
    'Maldives':           'Maldives',
    'Bangkok':            'Wat Phra Kaew',
    'Hong Kong':          'Victoria Harbour',
    'Seoul':              'Gyeongbokgung Palace',
    'Hanoi':              'Hoan Kiem Lake',
    'Hoi An':             'Hoi An Ancient Town',
    'Siem Reap':          'Angkor Thom',
    'Dubai':              'Burj Khalifa',
    'Marrakech':          'Jemaa el-Fna',
    'Cairo':              'Great Pyramid of Giza',
    'Petra':              'Al-Khazneh',
    'Fez':                'Chouara Tannery',
    'Zanzibar':           'Stone Town, Zanzibar',
    'Luang Prabang':      'Wat Xieng Thong',
    'Goa':                'Basilica of Bom Jesus',
    'Kathmandu':          'Boudhanath',
    'Tbilisi':            'Narikala',
    'Bagan':              'Bagan',
    'New York City':      'Empire State Building',
    'San Francisco':      'Golden Gate Bridge',
    'New Orleans':        'French Quarter, New Orleans',
    'Miami':              'South Beach, Miami Beach',
    'Las Vegas':          'Las Vegas Strip',
    'Machu Picchu':       'Machu Picchu',
    'Rio de Janeiro':     'Christ the Redeemer',
    'Buenos Aires':       'La Boca',
    'Cartagena':          'Cartagena, Colombia',
    'Mexico City':        'Zocalo',
    'Cancún':             'Chichen Itza',
    'Tulum':              'Tulum ruins',
    'Havana':             'Havana',
    'Banff':              'Lake Louise, Alberta',
    'Patagonia':          'Torres del Paine',
    'Galápagos Islands':  'Galapagos Islands',
    'Iguazu Falls':       'Iguazu Falls',
    'Sedona':             'Sedona, Arizona',
    'Vancouver':          'Stanley Park',
    'Medellín':           'Medellin',
    'Cape Town':          'Table Mountain',
    'Masai Mara Safari':  'Maasai Mara',
    'Kilimanjaro':        'Mount Kilimanjaro',
    'Serengeti':          'Serengeti National Park',
    'Victoria Falls':     'Victoria Falls',
    'Sydney':             'Sydney Opera House',
    'Queenstown':         'Queenstown, New Zealand',
    'Fiji':               'Yasawa Islands',
    'Seychelles':         'Anse Source d\'Argent',
    'Bora Bora':          'Bora Bora',
    'Great Barrier Reef': 'Great Barrier Reef',
    'Melbourne':          'Federation Square',
    'Reykjavik':          'Northern Lights',
    'Faroe Islands':      'Faroe Islands',
    'Lofoten Islands':    'Reine, Norway',
    'Azores':             'Sete Cidades',
    'Lake Como':          'Lake Como',
    'Portofino':          'Portofino',
    'Valletta':           'Valletta',
    'Tuscany':            'Val d\'Orcia',
    'Monaco':             'Circuit de Monaco',
    'Ibiza':              'Ibiza',
    'Napa Valley':        'Napa Valley',
    'Rotorua':            'Wai-O-Tapu',
    'Cusco':              'Plaza de Armas, Cusco',
}


def _batch_fetch(titles, size=1200):
    """
    Fetch Wikipedia page images for up to 50 titles per request.
    Returns dict mapping each input title → image URL.
    Handles Wikipedia's redirect and normalization chains.
    """
    results = {}
    batch_size = 50

    for start in range(0, len(titles), batch_size):
        batch = titles[start:start + batch_size]
        try:
            r = requests.get(
                WIKI_API,
                params={
                    'action':      'query',
                    'titles':      '|'.join(batch),
                    'prop':        'pageimages',
                    'pithumbsize': size,
                    'format':      'json',
                    'redirects':   '1',
                },
                headers=HEADERS,
                timeout=30,
            )
            r.raise_for_status()
            data = r.json()
            q = data.get('query', {})

            # Build chain: current_title_lower → original_input_title
            chain = {t.lower(): t for t in batch}
            for n in q.get('normalized', []):
                orig = chain.pop(n['from'].lower(), n['from'])
                chain[n['to'].lower()] = orig
            for rd in q.get('redirects', []):
                orig = chain.pop(rd['from'].lower(), rd['from'])
                chain[rd['to'].lower()] = orig

            for page in q.get('pages', {}).values():
                page_key = page.get('title', '').lower()
                original  = chain.get(page_key, page.get('title', ''))
                thumb = page.get('thumbnail')
                if thumb:
                    url = thumb['source']
                    if not url.lower().endswith('.svg'):
                        results[original] = url

        except Exception:
            pass

        if start + batch_size < len(titles):
            time.sleep(1)

    return results


class Command(BaseCommand):
    help = 'Fetch correct destination images from Wikipedia (4 batched API calls)'

    def handle(self, *args, **options):
        self.stdout.write('Fetching primary images from Wikipedia (batch)...')
        primary_map = _batch_fetch(list(PRIMARY_TITLES.values()))
        self.stdout.write(f'  Got {len(primary_map)} primary images.')

        self.stdout.write('Fetching secondary/landmark images from Wikipedia (batch)...')
        secondary_map = _batch_fetch(list(SECONDARY_TITLES.values()))
        self.stdout.write(f'  Got {len(secondary_map)} secondary images.')

        self.stdout.write('Updating destinations...')
        updated, no_image, not_in_db = 0, [], []

        for dest_name, primary_title in PRIMARY_TITLES.items():
            secondary_title = SECONDARY_TITLES.get(dest_name, primary_title)

            primary_url   = primary_map.get(primary_title)
            secondary_url = secondary_map.get(secondary_title) or primary_url

            if not primary_url:
                safe_title = primary_title.encode('ascii', 'replace').decode('ascii')
                self.stdout.write(self.style.WARNING(f'  No image: {dest_name} (tried "{safe_title}")'))
                no_image.append(dest_name)
                continue

            count = Destination.objects.filter(name=dest_name).update(
                image_url=primary_url,
                images=[primary_url, secondary_url],
            )
            if count:
                updated += 1
                self.stdout.write(f'  OK {dest_name}')
            else:
                self.stdout.write(self.style.WARNING(f'  Not in DB: {dest_name}'))
                not_in_db.append(dest_name)

        self.stdout.write('')
        if no_image:
            self.stdout.write(self.style.WARNING(f'No Wikipedia image for: {", ".join(no_image)}'))
        if not_in_db:
            self.stdout.write(self.style.WARNING(f'Not in DB: {", ".join(not_in_db)}'))
        self.stdout.write(self.style.SUCCESS(
            f'Done -- {updated} updated, {len(not_in_db)} not in DB, {len(no_image)} no image.'
        ))
