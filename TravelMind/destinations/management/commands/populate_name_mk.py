from django.core.management.base import BaseCommand
from destinations.models import Destination

NAME_MK = {
    # Europe
    'Paris':              'Париз',
    'Rome':               'Рим',
    'Barcelona':          'Барселона',
    'Amsterdam':          'Амстердам',
    'Prague':             'Прага',
    'Vienna':             'Виена',
    'Budapest':           'Будимпешта',
    'London':             'Лондон',
    'Berlin':             'Берлин',
    'Lisbon':             'Лисабон',
    'Santorini':          'Санторини',
    'Amalfi Coast':       'Амалфитански Брег',
    'Dubrovnik':          'Дубровник',
    'Lake Bled':          'Бледско Езеро',
    'Hallstatt':          'Халштат',
    'Interlaken':         'Интерлакен',
    'Zermatt':            'Зермат',
    'Dolomites':          'Доломити',
    'Norwegian Fjords':   'Норвешки Фјордови',
    'Scottish Highlands': 'Шкотски Висорамнини',
    'Algarve':            'Алгарве',
    'Cinque Terre':       'Ченке Тере',
    'Cappadocia':         'Кападокија',
    'Istanbul':           'Истанбул',
    'Mykonos':            'Миконос',
    'Plitvice Lakes':     'Плитвички Езера',
    'Athens':             'Атина',
    'Kotor':              'Котор',
    'Bruges':             'Бриж',
    'Porto':              'Порто',
    # Asia
    'Tokyo':              'Токио',
    'Kyoto':              'Кјото',
    'Osaka':              'Осака',
    'Bali':               'Бали',
    'Singapore':          'Сингапур',
    'Phuket':             'Пукет',
    'Chiang Mai':         'Чјанг Маи',
    'Maldives':           'Малдиви',
    'Bangkok':            'Бангкок',
    'Hong Kong':          'Хонг Конг',
    'Seoul':              'Сеул',
    'Hanoi':              'Ханој',
    'Hoi An':             'Хои Ан',
    'Siem Reap':          'Сием Реп',
    'Dubai':              'Дубаи',
    'Marrakech':          'Маракеш',
    'Cairo':              'Каиро',
    'Petra':              'Петра',
    'Fez':                'Фес',
    'Zanzibar':           'Занзибар',
    'Luang Prabang':      'Луанг Прабанг',
    'Goa':                'Гоа',
    'Kathmandu':          'Катманду',
    'Tbilisi':            'Тбилиси',
    'Bagan':              'Баган',
    # Americas
    'New York City':      'Њујорк',
    'San Francisco':      'Сан Франциско',
    'New Orleans':        'Њу Орлеанс',
    'Miami':              'Мајами',
    'Las Vegas':          'Лас Вегас',
    'Machu Picchu':       'Мачу Пичу',
    'Rio de Janeiro':     'Рио де Жанеиро',
    'Buenos Aires':       'Буенос Аирес',
    'Cartagena':          'Картагена',
    'Mexico City':        'Мексико Сити',
    'Cancún':             'Канкун',
    'Tulum':              'Тулум',
    'Havana':             'Хавана',
    'Banff':              'Банф',
    'Patagonia':          'Патагонија',
    'Galápagos Islands':  'Галапагос Острови',
    'Iguazu Falls':       'Водопади Игуасу',
    'Sedona':             'Седона',
    'Vancouver':          'Ванкувер',
    'Medellín':           'Меделин',
    # Africa
    'Cape Town':          'Кејптаун',
    'Masai Mara Safari':  'Масаи Мара Сафари',
    'Kilimanjaro':        'Килиманџаро',
    'Serengeti':          'Серенгети',
    'Victoria Falls':     'Водопади Викторија',
    # Oceania
    'Sydney':             'Сиднеј',
    'Queenstown':         'Квинстаун',
    'Fiji':               'Фиџи',
    'Seychelles':         'Сејшели',
    'Bora Bora':          'Бора Бора',
    'Great Barrier Reef': 'Голем Бариерен Гребен',
    'Melbourne':          'Мелбурн',
    # Nordic / Atlantic
    'Reykjavik':          'Рејкјавик',
    'Faroe Islands':      'Фарски Острови',
    'Lofoten Islands':    'Лофотенски Острови',
    'Azores':             'Азорски Острови',
    # Italy extras
    'Lake Como':          'Езеро Комо',
    'Portofino':          'Портофино',
    'Valletta':           'Валета',
    'Tuscany':            'Тоскана',
    # Others
    'Monaco':             'Монако',
    'Ibiza':              'Ибица',
    'Napa Valley':        'Долина Напа',
    'Rotorua':            'Роторуа',
    'Cusco':              'Куско',
}


class Command(BaseCommand):
    help = 'Populate name_mk (Macedonian name) for all destinations'

    def handle(self, *args, **options):
        updated, not_found = 0, []

        for english_name, mk_name in NAME_MK.items():
            count = Destination.objects.filter(name=english_name).update(name_mk=mk_name)
            if count:
                updated += count
            else:
                not_found.append(english_name)

        if not_found:
            self.stdout.write(self.style.WARNING(f'Not found: {", ".join(not_found)}'))
        self.stdout.write(self.style.SUCCESS(f'Done -- {updated} destinations updated with Macedonian names.'))
