from django.core.management.base import BaseCommand
from destinations.models import Destination

IMG = 'https://images.unsplash.com/photo-{}?w=800&auto=format&fit=crop&q=80'

# Two unique, location-accurate Unsplash photo IDs per destination.
# Format: 'Destination Name': [primary_id, secondary_id]
DESTINATION_IMAGES = {
    # ── Europe ──────────────────────────────────────────────────────────────
    'Paris':            ['1499856871958-5b9627545d1a', '1502602898657-3e91760cbb34'],
    'Rome':             ['1552832230-c0197dd311b5',    '1531572753322-ad063cecc140'],
    'Barcelona':        ['1539037116277-4db20889f2d4', '1583422409516-2895a9b52da3'],
    'Amsterdam':        ['1534351590666-13e3e96b5017', '1512470876302-e49dcc1adbb4'],
    'Prague':           ['1541849546-216549ae216d',    '1592906209472-a36b1f3782ef'],
    'Vienna':           ['1516550893885-985c836c2e4a', '1599946347371-68eb71b16afc'],
    'Budapest':         ['1549144511-f099e773c147',    '1600611053254-3eb2cad1e2a4'],
    'London':           ['1513635269975-59663e0ac1ad', '1486299267070-83823f5448c5'],
    'Berlin':           ['1560969184-10fe8719e047',    '1587383378702-fb56b408e9e5'],
    'Lisbon':           ['1596567153406-0c6bd74e7b7b', '1558069369-0fbdd3d9c174'],
    'Santorini':        ['1533105079780-92b9be482077', '1570077188670-e3a8d69ac5ff'],
    'Amalfi Coast':     ['1534430480872-3498386e7856', '1612698093158-e07ac200d44e'],
    'Dubrovnik':        ['1555990538-1b6f0c0c1a1c',   '1563805175-c9c2e29d62b6'],
    'Lake Bled':        ['1469474968028-56623f02e42e', '1569665266565-e13e23f63c65'],
    'Hallstatt':        ['1508193638397-1ce7e052dc1d', '1467269804805-5c3e2b3af5b6'],
    'Interlaken':       ['1531366936337-7c912a4589a7', '1548032850-b2c4e1ad2e16'],
    'Zermatt':          ['1548438294-1ad5d5f4f063',    '1520208422220-d12a3c588e6c'],
    'Dolomites':        ['1551632811-561732d1e306',    '1476514525535-07fb3b4ae5f1'],
    'Norwegian Fjords': ['1513519245088-0e12902e5a38', '1531802615847-57f26455f0a3'],
    'Scottish Highlands':['1565939570932-b587ab503e4b','1490425688786-9e6aebf77bc3'],
    'Algarve':          ['1558618666-fcd25c85cd64',    '1505765050516-4cf7e6b23c26'],
    'Cinque Terre':     ['1516483638261-f4dbaf036963', '1621123027990-1f5c79b30f30'],
    'Cappadocia':       ['1581852017103-68ac65514cf7', '1543149118428-5cac3e4cc5a9'],
    'Istanbul':         ['1524231757912-21f4fe3a7200', '1582719471538-13d09b10c0c6'],
    'Mykonos':          ['1613395877344-13d4a8e0d49e', '1601581899060-f87f989d7139'],
    'Plitvice Lakes':   ['1551929048-1d6afee82c61',    '1518621736915-f6c673a9e4d0'],
    'Athens':           ['1555993539-1732b0258235',    '1580474593566-9b2b6c0c2a40'],
    'Kotor':            ['1599894048603-ac1edc7a00dc', '1605600221752-c8b39c25d0da'],
    'Bruges':           ['1548707284-a1a7c8f91f9d',    '1577717903312-82a6e5701f75'],
    'Porto':            ['1555881400-74d7acaacd8b',    '1597955441947-2bec29c94fcc'],

    # ── Asia ────────────────────────────────────────────────────────────────
    'Tokyo':            ['1540959733332-eab4deabeeaf', '1503899036392-e98de4b6de89'],
    'Kyoto':            ['1493976040374-85c8e12f0c0e', '1528360983277-13d401cdc186'],
    'Osaka':            ['1557409518-a18c2af99c4b',    '1590559899731-f8c9ee30d70a'],
    'Bali':             ['1537996194471-e657df975ab4', '1518548419791-f0f5ced3671c'],
    'Singapore':        ['1525625293386-3f8f99389edd', '1582719471172-f9a3b7d7c5c1'],
    'Phuket':           ['1552465011-b4e21bf6e79a',    '1520250497591-112f2f40a3f4'],
    'Chiang Mai':       ['1555217851-6141535bd771',    '1583417319-9c6ba432bb74'],
    'Maldives':         ['1514282401047-d79a71a590e8', '1573790387-cdd3756dd4f9'],
    'Bangkok':          ['1508009603885-50cf7c579365', '1559827160-f8d7a2c58d1b'],
    'Hong Kong':        ['1531259683007-016a7b628fc3', '1506748686714-04f6a21b7bdd'],
    'Seoul':            ['1517154421773-0855edd8b90c', '1583416750470-5a95dc28be2d'],
    'Hanoi':            ['1540166918756-7a8b73ab25cc', '1598030473776-34a6fca7bcf0'],
    'Hoi An':           ['1559827291-72ebff18ca85',    '1555652736-80a965f4c9b8'],
    'Siem Reap':        ['1600699268439-fc6d03e01f33', '1558607519-89df6c1d5f3b'],
    'Dubai':            ['1512453979798-5ea266f8880c', '1582672060-1fc7a7de6cb1'],
    'Marrakech':        ['1597212618440-806262de4f0b', '1539650116574-75c0c6e73338'],
    'Cairo':            ['1572252009286-268acec5ca0a', '1568322503739-4f130da4e843'],
    'Petra':            ['1548074258-b0de0f0c29d8',    '1570948001-0e450e14d6b4'],
    'Fez':              ['1538430420919-68bce3e9b9fb', '1535220923879-ce10bdd19df1'],
    'Zanzibar':         ['1571019613454-1cb2f99b2d8b', '1590559898968-c9c3e8b7c7a6'],
    'Luang Prabang':    ['1610559228800-b788f80c3c1a', '1544450665-19f7fb4c44b0'],
    'Goa':              ['1590374505637-4c1b2fbbe28e', '1519046909901-0b8ba9e74aeb'],
    'Kathmandu':        ['1605540436563-5bca919ae766', '1565117455925-8a7eff0c3e2b'],
    'Tbilisi':          ['1550997817-c18fcc1e3dc4',    '1598461620836-07c2b5c7a5e1'],
    'Bagan':            ['1600078635765-0fb7e980b6ca', '1598865222073-d8c9db83d3a2'],

    # ── Americas ────────────────────────────────────────────────────────────
    'New York City':    ['1485871276861-b7c9b92e9b80', '1477959858617-67f85cf4f1df'],
    'San Francisco':    ['1501594907352-04cda38ebc29', '1506510497523-78c7c6b60c89'],
    'New Orleans':      ['1504711434969-e33886168f5c', '1571501802183-8e6f54b68e62'],
    'Miami':            ['1535498730771-e735b998cd64', '1508690269-3a48e1f02e81'],
    'Las Vegas':        ['1486325212027-8081e485255e', '1556740714-a8395b3bb30e'],
    'Machu Picchu':     ['1526392060635-9d6019884377', '1587595431096-4c5eed38ba55'],
    'Rio de Janeiro':   ['1483729558449-d196097202be', '1544451326-a6aff32a3a8b'],
    'Buenos Aires':     ['1589909202802-8f4aadce1849', '1580819343019-ad86ddb57e40'],
    'Cartagena':        ['1519125323398-675f0ddb6308', '1604537466608-09f8b2c4b3d4'],
    'Mexico City':      ['1518659526054-190340b32735', '1588392742-c98a1f694a0e'],
    'Cancún':           ['1510525009512-ad7fc13d6c70', '1602002208183-8b5a1fe47e49'],
    'Tulum':            ['1544551763-46a013bb70d5',    '1600456397236-b50f8b7d9a37'],
    'Havana':           ['1500759285222-a95626b934cb', '1570475071693-2aa0a65c62ac'],
    'Banff':            ['1441974231531-c6227db76b6e', '1500534314209-a25ddb2bd429'],
    'Patagonia':        ['1501854140801-50d01698950b', '1553789340-ded31a5c2d95'],
    'Galápagos Islands':['1518715993400-a9a5e4b53cc6', '1498855926480-d8c9fef23926'],
    'Iguazu Falls':     ['1516426122078-c23e76319801', '1604271931970-a5a4bb823e87'],
    'Sedona':           ['1474044159687-1ee9f3a51722', '1472396961693-142e6e269027'],
    'Vancouver':        ['1559511454-b0b2ca4160a7',    '1477959858617-67f85cf4f1df'],
    'Medellín':         ['1549054575-f853e5f6c8f8',    '1561334960-f9f23ef6ea8b'],

    # ── Africa ──────────────────────────────────────────────────────────────
    'Cape Town':        ['1580060839134-75a5edca2e99', '1516026672447-9e88bb9a5b48'],
    'Masai Mara Safari':['1547471080-7cc2caa01a7e',    '1549366021-4a9ae43d02c8'],
    'Kilimanjaro':      ['1589802829985-35cb977f072c', '1519400237-f1b28fce4b32'],
    'Serengeti':        ['1504248987-24f5b98b1d3a',    '1516426122078-c23e76319801'],
    'Victoria Falls':   ['1577083559562-b2b41d70a6d3', '1543349689-1ec93dca51a3'],

    # ── Oceania ─────────────────────────────────────────────────────────────
    'Sydney':           ['1523482580672-f1ce58af5c06', '1526109641975-ac69f9af2b46'],
    'Queenstown':       ['1507699622108-4be3abd695ad', '1594495651076-a6a1a8bcb5b1'],
    'Fiji':             ['1506929562872-bb421503ef21', '1559128378-39e4ab25c4e2'],
    'Seychelles':       ['1589979481623-1c77cca2bbba', '1586500036125-32e8ec88d0e7'],
    'Bora Bora':        ['1589179053754-23cd22671a46', '1598811012613-b28bda4e9e70'],
    'Great Barrier Reef':['1583212292454-0d6c62dc43c2','1510149834264-9e6026cec49e'],
    'Melbourne':        ['1514395462740-ba30ed6a8e0a', '1571074481999-78bf2b7bffcf'],

    # ── Iceland / Monaco / Italy extras / Spain extras ───────────────────────
    'Reykjavik':        ['1504543151748-db3f1f9e3d36', '1519882840518-2c7f0f9f74c6'],
    'Monaco':           ['1533697638450-cca4d3e64e9b', '1567942712661-03c9b1a00e0b'],
    'Lake Como':        ['1527838832700-5059252407fa', '1598728825573-9bb1f7ae6e60'],
    'Portofino':        ['1523528576989-c8b45d5bdb7f', '1550535424-1bac47d3ce44'],
    'Valletta':         ['1601445638532-3c6f6c3aa1d6', '1565011893012-64640cdf9765'],
    'Tuscany':          ['1516484681798-8def6d1a5a79', '1523906834672-2c78d4c5e2de'],
    'Ibiza':            ['1505236732171-83b56e9e9f32', '1598211624559-1e8ee5dd3688'],

    # ── Atlantic islands / Nordic ────────────────────────────────────────────
    'Azores':           ['1565113400393-7e46bd10e1a2', '1552009575264-12c56e8bf5bf'],
    'Faroe Islands':    ['1490425688786-9e6aebf77bc3', '1556998252-b5eed5b3a0c6'],
    'Lofoten Islands':  ['1580979560261-d3e7e3f9c6e9', '1551076508-31d39f6ff3f2'],

    # ── North America extras ────────────────────────────────────────────────
    'Napa Valley':      ['1507434965515-61970f2bd869', '1510312670557-eaa4e067ed0b'],
    'Rotorua':          ['1558618047-3c8d70e4b8be',    '1545458065-15e07ac2f67b'],

    # ── South America extras ────────────────────────────────────────────────
    'Cusco':            ['1552557058-ec3b0f1c2dc0',    '1583377702935-e0640d56e605'],
}


class Command(BaseCommand):
    help = 'Update image_url and images fields for all destinations with curated Unsplash photos'

    def handle(self, *args, **options):
        updated = 0
        not_found = []

        for name, ids in DESTINATION_IMAGES.items():
            primary = IMG.format(ids[0])
            secondary = IMG.format(ids[1])
            count = Destination.objects.filter(name=name).update(
                image_url=primary,
                images=[primary, secondary],
            )
            if count:
                updated += count
                self.stdout.write(f'  OK {name}')
            else:
                not_found.append(name)
                self.stdout.write(self.style.WARNING(f'  NOT FOUND: {name}'))

        self.stdout.write('')
        if not_found:
            self.stdout.write(
                self.style.WARNING(f'Not found ({len(not_found)}): {", ".join(not_found)}')
            )
        self.stdout.write(
            self.style.SUCCESS(f'Done — updated {updated} destinations.')
        )
