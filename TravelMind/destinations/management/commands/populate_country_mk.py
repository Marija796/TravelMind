from django.core.management.base import BaseCommand
from destinations.models import Destination

# Every country value currently used by a Destination row, mapped to its
# real Macedonian name (not a transliteration) - mirrors the pattern
# already used by populate_name_mk.py for destination names.
COUNTRY_MK = {
    'Argentina': 'Аргентина',
    'Australia': 'Австралија',
    'Austria': 'Австрија',
    'Belgium': 'Белгија',
    'Brazil': 'Бразил',
    'Cambodia': 'Камбоџа',
    'Canada': 'Канада',
    'China': 'Кина',
    'Colombia': 'Колумбија',
    'Croatia': 'Хрватска',
    'Cuba': 'Куба',
    'Czech Republic': 'Чешка',
    'Denmark': 'Данска',
    'Ecuador': 'Еквадор',
    'Egypt': 'Египет',
    'Fiji': 'Фиџи',
    'France': 'Франција',
    'French Polynesia': 'Француска Полинезија',
    'Georgia': 'Грузија',
    'Germany': 'Германија',
    'Greece': 'Грција',
    'Hungary': 'Унгарија',
    'Iceland': 'Исланд',
    'India': 'Индија',
    'Indonesia': 'Индонезија',
    'Italy': 'Италија',
    'Japan': 'Јапонија',
    'Jordan': 'Јордан',
    'Kenya': 'Кенија',
    'Laos': 'Лаос',
    'Maldives': 'Малдиви',
    'Malta': 'Малта',
    'Mexico': 'Мексико',
    'Monaco': 'Монако',
    'Montenegro': 'Црна Гора',
    'Morocco': 'Мароко',
    'Myanmar': 'Мјанмар',
    'Nepal': 'Непал',
    'Netherlands': 'Холандија',
    'New Zealand': 'Нов Зеланд',
    'Norway': 'Норвешка',
    'Peru': 'Перу',
    'Portugal': 'Португалија',
    'Seychelles': 'Сејшели',
    'Singapore': 'Сингапур',
    'Slovenia': 'Словенија',
    'South Africa': 'Јужна Африка',
    'South Korea': 'Јужна Кореја',
    'Spain': 'Шпанија',
    'Switzerland': 'Швајцарија',
    'Tanzania': 'Танзанија',
    'Thailand': 'Тајланд',
    'Turkey': 'Турција',
    'USA': 'САД',
    'United Arab Emirates': 'Обединети Арапски Емирати',
    'United Kingdom': 'Обединето Кралство',
    'Vietnam': 'Виетнам',
    'Zambia': 'Замбија',
}


class Command(BaseCommand):
    help = 'Populate country_mk (Macedonian country name) for all destinations.'

    def handle(self, *args, **options):
        updated, not_found = 0, []

        for english_name, mk_name in COUNTRY_MK.items():
            count = Destination.objects.filter(country=english_name).update(country_mk=mk_name)
            if count:
                updated += count
            else:
                not_found.append(english_name)

        remaining = Destination.objects.filter(country_mk='').values_list('country', flat=True).distinct()
        if remaining:
            self.stdout.write(self.style.WARNING(
                f'Countries still without a Macedonian translation: {", ".join(sorted(set(remaining)))}'
            ))
        self.stdout.write(self.style.SUCCESS(f'Done -- {updated} destination(s) updated with a Macedonian country name.'))
