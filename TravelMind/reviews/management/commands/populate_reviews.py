from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from destinations.models import Destination
from reviews.models import Review

User = get_user_model()

FAKE_USERS = [
    {'username': 'elena_traveller', 'email': 'elena@example.com', 'first_name': 'Елена', 'last_name': 'Петрова'},
    {'username': 'marko_mk', 'email': 'marko@example.com', 'first_name': 'Марко', 'last_name': 'Николов'},
    {'username': 'sofia_explorer', 'email': 'sofia@example.com', 'first_name': 'Софија', 'last_name': 'Димова'},
    {'username': 'alex_wanderer', 'email': 'alex@example.com', 'first_name': 'Александар', 'last_name': 'Стојановски'},
    {'username': 'maja_journeys', 'email': 'maja@example.com', 'first_name': 'Маjа', 'last_name': 'Илиевска'},
    {'username': 'ivan_mk', 'email': 'ivan@example.com', 'first_name': 'Иван', 'last_name': 'Костовски'},
    {'username': 'lena_world', 'email': 'lena@example.com', 'first_name': 'Лена', 'last_name': 'Тодорова'},
    {'username': 'stefan_travels', 'email': 'stefan@example.com', 'first_name': 'Стефан', 'last_name': 'Ристески'},
]

# Reviews keyed by destination name. Each entry: list of (username, rating, comment)
REVIEWS = {
    'Paris': [
        ('elena_traveller', 5, 'Апсолутно магичен град! Ајфеловата кула при зори е нешто што не можете да го опишете со зборови.'),
        ('marko_mk', 5, 'Најубавиот град во Европа. Кујната е неверојатна, музеите се светска класа.'),
        ('sofia_explorer', 4, 'Beautiful city, a bit crowded but worth every moment. The Louvre alone is worth the trip!'),
        ('alex_wanderer', 5, 'Paris is everything they say and more. Will definitely return.'),
    ],
    'Rome': [
        ('lena_world', 5, 'Рим е жив музеј. Колосеумот, Ватиканот, фонтаната Треви — се е неверојатно!'),
        ('stefan_travels', 5, 'Eternal City indeed. History around every corner. Amazing food too!'),
        ('maja_journeys', 4, 'Прекрасно место, но многу туристи. Препорачувам рано наутро за атракциите.'),
        ('ivan_mk', 5, 'The pasta and pizza in Rome is on another level. History + food = perfection.'),
    ],
    'Barcelona': [
        ('marko_mk', 5, 'Гауди е геније. Саградата Фамилија ме остави без зборови. Барселона е совршена!'),
        ('elena_traveller', 5, 'Amazing city — architecture, food, beaches, nightlife. Has it all!'),
        ('alex_wanderer', 4, 'Одличен град, многу енергичен. Плажите и тапасите се фантастични.'),
        ('sofia_explorer', 5, 'Barcelona exceeded all expectations. Gaudi work is truly unique.'),
    ],
    'Istanbul': [
        ('ivan_mk', 5, 'Истанбул е невероjатен — Исток среќава Запад. Аjа Софиjа ми го промени погледот.'),
        ('lena_world', 5, 'Grand Bazaar, Bosphorus sunset, incredible food. Istanbul is unforgettable!'),
        ('stefan_travels', 4, 'Грандиозен град со богата историjа. Патувањето е и достапно и вредно.'),
    ],
    'Santorini': [
        ('maja_journeys', 5, 'Zajdisonceto vo Oia e najubavo nešto što sum videla. San na Zemjata!'),
        ('elena_traveller', 5, 'Santorini is as beautiful as the photos, maybe even more. Pure magic!'),
        ('marko_mk', 4, 'Скапо, но вредно. Убавината е неспоредлива. Едношпатувај!'),
    ],
    'Tokyo': [
        ('alex_wanderer', 5, 'Токио е иднината и традицијата во исто време. Храната е апсолутно извонредна!'),
        ('sofia_explorer', 5, 'Most incredible city I have ever visited. Clean, safe, efficient and fascinating.'),
        ('ivan_mk', 5, 'Јапонија ги менува перспективите. Токио е на друго ниво на се.'),
        ('lena_world', 4, 'Amazing experience, very different from Europe. The ramen alone is worth the flight!'),
    ],
    'Bali': [
        ('maja_journeys', 5, 'Бали е духовен рај. Убуд, рис-терасите, храмовите — сè е совршено!'),
        ('stefan_travels', 5, 'Paradise on Earth. Great food, amazing culture, friendly people.'),
        ('elena_traveller', 4, 'Wonderful destination for relaxation and culture. Ubud is magical!'),
    ],
    'Dubai': [
        ('marko_mk', 4, 'Дубаи е разнишувачки — луксуз и архитектура на врвно ниво. Задолжително!'),
        ('alex_wanderer', 5, 'Futuristic city that needs to be seen to be believed. Burj Khalifa is breathtaking.'),
        ('sofia_explorer', 4, 'Very different from Europe but fascinating. Desert safari was highlight!'),
    ],
    'Kyoto': [
        ('lena_world', 5, 'Кjото е душата на Јапониjа. Сакура сезоната е незаборавна убавина.'),
        ('ivan_mk', 5, 'If Tokyo is the future, Kyoto is the soul. Temples, gardens, tea ceremonies — perfect.'),
        ('maja_journeys', 5, 'Најмирниот и наjубавиот град во кои сум биjала. Апсолутен рај.'),
    ],
    'Dubrovnik': [
        ('stefan_travels', 5, 'Game of Thrones setting but the real Dubrovnik is even better. Walls walk is incredible!'),
        ('elena_traveller', 4, 'Дубровник е бисер. Ѕидовите над морето се незаборавни. Препорачувам рано наутро.'),
        ('marko_mk', 5, 'Одиме секоjа година. Море + историjа = совршенство.'),
    ],
    'Amsterdam': [
        ('alex_wanderer', 4, 'Charming canal city. Anne Frank House was moving. Perfect for cycling!'),
        ('sofia_explorer', 5, 'Амстердам е уникатен — канали, музеи, велосипеди. Многу ми се допадна!'),
        ('lena_world', 4, 'Beautiful city, great museums. Rijksmuseum is world class.'),
    ],
    'Prague': [
        ('ivan_mk', 5, 'Прага е приказна — готска архитектура и прекрасно стар град. И достапна!'),
        ('maja_journeys', 5, 'One of the most beautiful cities in Europe. Cheap, charming and historic!'),
        ('stefan_travels', 4, 'Amazing city for a weekend trip. Old Town Square at night is magical.'),
    ],
    'Budapest': [
        ('elena_traveller', 5, 'Будимпешта е недооценета. Термалните бањи и Рибарскиот Бастион се невероjатни!'),
        ('marko_mk', 5, 'Best value European capital! Beautiful Danube views and incredible thermal baths.'),
        ('alex_wanderer', 4, 'Gorgeous city. Parliament building is stunning. Ruin bars are unique!'),
    ],
    'Athens': [
        ('sofia_explorer', 5, 'Акрополот и Партенонот ме оставија без дах. Историjата е живо тука!'),
        ('lena_world', 4, 'Cradle of civilization! Acropolis Museum is outstanding. Great food too.'),
        ('ivan_mk', 5, 'Атина е незаборавна. Историjата, храната, луѓето — сè е одлично.'),
    ],
    'Marrakech': [
        ('maja_journeys', 5, 'Маракеш е комплетно поинаков свет — бои, мириси, звуци. Риадите се рај!'),
        ('stefan_travels', 4, 'Unique and unforgettable experience. Souks are overwhelming but amazing.'),
        ('elena_traveller', 5, 'The magic of Morocco in one city. Jemaa el-Fna square at night is incredible!'),
    ],
    'Lisbon': [
        ('marko_mk', 5, 'Лисабон е шармантен и достапен. Фадо музиката, пастел де ната, трамваи — совршено!'),
        ('alex_wanderer', 5, 'Lisbon stole my heart. Best European city for value and authenticity.'),
        ('sofia_explorer', 4, 'Прекрасен град со уникатна атмосфера. Сè е достапно и убаво.'),
    ],
    'Vienna': [
        ('lena_world', 5, 'Виена е царска и елегантна. Кафеаните, операта, Шенбрун — сè е врвно!'),
        ('ivan_mk', 4, 'Imperial grandeur at its finest. The coffeehouse culture is unique to Vienna.'),
        ('maja_journeys', 5, 'Most cultured city I have visited. Music, art, architecture — all world class.'),
    ],
    'Cappadocia': [
        ('stefan_travels', 5, 'Летот со балон над Кападокиjа е врвното патничко искуство. Незаборавно!'),
        ('elena_traveller', 5, 'Surreal landscape unlike anything else on Earth. Balloon ride is a must!'),
        ('marko_mk', 5, 'Некоjа друга планета. Пештерските хотели и воздушните балони се единствени.'),
    ],
    'Bagan': [
        ('alex_wanderer', 5, 'Thousands of temples at sunrise — one of the most spiritual experiences of my life.'),
        ('sofia_explorer', 5, 'Баган е мистичен и неверојатен. Е-бициклот меѓу пагодите е незаборавно!'),
    ],
    'Kotor': [
        ('lena_world', 5, 'Котор е скриен бисер. Ѕидовите, заливот, старото место — сè е совршено!'),
        ('ivan_mk', 5, 'Hidden gem of the Balkans. The bay is stunning and the old town is charming.'),
        ('maja_journeys', 4, 'Одличен избор за одмор. Достапно и неверojатно убаво.'),
    ],

    # --- Additional destinations ---
    'Algarve': [
        ('elena_traveller', 5, 'The Algarve coastline is breathtaking — golden cliffs, turquoise sea caves and perfect beaches. Pure paradise!'),
        ('marko_mk', 5, 'Алгарве е совршена плажа. Клифовите и пештерите се единствени на светот. Задолжително!'),
        ('sofia_explorer', 4, 'Beautiful beaches but busy in summer. Visit in May or September for the best experience.'),
    ],
    'Amalfi Coast': [
        ('ivan_mk', 5, 'Амалфи Брег е сон — разноцветни куќи, кристално море, лимончело. Италија на нејзин врв!'),
        ('lena_world', 5, 'Driving the Amalfi Coast road was terrifying and beautiful at once. Positano is a dream village.'),
        ('stefan_travels', 4, 'Stunning scenery but expensive. Take the ferry between towns instead of the bus — far more relaxing.'),
    ],
    'Azores': [
        ('maja_journeys', 5, 'Азорите се непознат бисер — вулкани, кристални езера, кити и мир. Природата е неверојатна!'),
        ('alex_wanderer', 5, 'The most underrated destination in Europe. Whale watching, hot springs and dramatic landscapes all in one place.'),
        ('elena_traveller', 4, 'São Miguel island is absolutely stunning. The Sete Cidades crater lake is unforgettable.'),
    ],
    'Banff': [
        ('stefan_travels', 5, 'Банф е канадска природна магија. Туркоазните езера и планинските врвови ми го одзедоа здивот.'),
        ('marko_mk', 5, 'Lake Louise and Moraine Lake are the most beautiful lakes I have ever seen. Winter here is magical too.'),
        ('lena_world', 4, 'Incredible Canadian Rockies scenery. Book accommodation very early — it fills up fast!'),
    ],
    'Bangkok': [
        ('ivan_mk', 5, 'Бангкок е хаотичен и прекрасен истовремено. Храмовите, уличната храна и пазарите се фантастични!'),
        ('sofia_explorer', 5, 'The street food scene in Bangkok is unmatched anywhere in the world. Wat Pho alone is worth the trip.'),
        ('maja_journeys', 4, 'Amazing city full of energy. Grand Palace is stunning but get there early to avoid the crowds.'),
    ],
    'Berlin': [
        ('alex_wanderer', 5, 'Берлин е историjа, уметност и слобода во едно. Пространиот Бранденбуршки порти на зајдисонце е незаборавно.'),
        ('elena_traveller', 5, 'Best city for history, art and nightlife combined. The Wall Memorial is moving and essential.'),
        ('marko_mk', 4, 'Fascinating city with incredible energy. Museum Island is a full day well spent.'),
    ],
    'Bora Bora': [
        ('lena_world', 5, 'Бора Бора е луксуз во чиста форма. Пребарувачот над водата и лагуната — буквално рај на земјата.'),
        ('stefan_travels', 5, 'Most beautiful lagoon on the planet. The overwater bungalows are expensive but worth every cent.'),
        ('maja_journeys', 5, 'Nothing prepares you for how stunning Bora Bora really is. Snorkelling with sharks and rays was surreal.'),
    ],
    'Bruges': [
        ('sofia_explorer', 5, 'Бриж е средновековна бајка — канали, чоколадо, пиво и готска архитектура. Обожавам!'),
        ('ivan_mk', 5, 'The most fairy-tale city in Belgium. Climb the Belfry for the best views over the rooftops.'),
        ('alex_wanderer', 4, 'Incredibly charming but very touristy on weekends. Visit on a weekday morning for a magical experience.'),
    ],
    'Buenos Aires': [
        ('elena_traveller', 5, 'Буенос Аjрес е Европа во Јужна Америка — танго, одличен стек и страстна атмосфера!'),
        ('marko_mk', 5, 'The tango scene, the steakhouses, Recoleta cemetery — Buenos Aires is endlessly fascinating.'),
        ('lena_world', 4, 'A city of enormous culture and character. Palermo neighbourhood is perfect for eating and nightlife.'),
    ],
    'Cairo': [
        ('stefan_travels', 5, 'Каиро е шок за сетилата — во добра смисла. Пирамидите на Гиза на живо ги надминуваат сите очекувања.'),
        ('maja_journeys', 5, 'Standing before the Pyramids of Giza is one of those moments that changes you. Egyptian Museum is world class.'),
        ('ivan_mk', 4, 'Chaotic and overwhelming but unforgettable. The pyramids at sunset are one of the great wonders of the world.'),
    ],
    'Cancún': [
        ('alex_wanderer', 4, 'Канкун нуди совршени плажи и кристална вода. Cenotes се апсолутна задолжителна активност!'),
        ('sofia_explorer', 4, 'Beautiful Caribbean beaches and great value. Day trips to Chichén Itzá and Tulum are must-dos.'),
        ('elena_traveller', 5, 'The hotel zone is fun but venture out to the cenotes and Mayan ruins for the real magic.'),
    ],
    'Cape Town': [
        ('marko_mk', 5, 'Кejп Таун е едно од наjубавите места на планетата — планините, морето и виното се совршени.'),
        ('lena_world', 5, 'Table Mountain, Cape Point, Boulders Beach penguins — Cape Town delivers on every front. Breathtaking!'),
        ('stefan_travels', 4, 'Stunning natural setting and great food scene. The Garden Route day trip is highly recommended.'),
    ],
    'Cartagena': [
        ('maja_journeys', 5, 'Картахена е жива, шарена и романтична. Ѕидовите на старото место и карипската атмосфера се неодоливи!'),
        ('ivan_mk', 5, 'The most colourful city I have ever visited. The colonial old town is a UNESCO treasure.'),
        ('alex_wanderer', 4, 'Beautiful Caribbean walled city. Combine with a day trip to the Rosario Islands for perfect beaches.'),
    ],
    'Chiang Mai': [
        ('elena_traveller', 5, 'Чианг Маj е срцето на тајландската култура — храмови, кујна и слонови. Аjа не е хипстерска цел!'),
        ('sofia_explorer', 5, 'Cooking classes, temple hopping, elephant sanctuary — Chiang Mai is endlessly rewarding. Loved every moment.'),
        ('marko_mk', 4, 'Brilliant base for northern Thailand. The Sunday Night Market is one of the best street food experiences in Asia.'),
    ],
    'Cinque Terre': [
        ('lena_world', 5, 'Чинкуе Тере е италијанска совршеност — пет шарени рибарски села над морето. Незаборавно!'),
        ('stefan_travels', 5, 'The most picturesque coastline in Italy. Hiking between the villages is tough but the views are unreal.'),
        ('maja_journeys', 4, 'Beautiful but very crowded in peak season. Stay overnight for the evening magic when day-trippers leave.'),
    ],
    'Cusco': [
        ('ivan_mk', 5, 'Куско е мистичен инкаски град. Атмосферата, архитектурата и планините создаваат нешто посебно.'),
        ('alex_wanderer', 5, 'Gateway to Machu Picchu but fascinating in its own right. The Inca stonework is mind-blowing.'),
        ('elena_traveller', 4, 'Allow 2 days to acclimatise to the altitude before doing anything strenuous. San Blas neighbourhood is magical.'),
    ],
    'Dolomites': [
        ('marko_mk', 5, 'Доломитите се Алпите на стероиди — остри врвови, зелени долини и уникатна геологија. Рај за планинари!'),
        ('sofia_explorer', 5, 'The most dramatic mountain scenery in Europe. Tre Cime di Lavaredo at sunrise is absolutely awe-inspiring.'),
        ('lena_world', 4, 'Stunning in summer and winter. The via ferrata routes offer incredible adventure for experienced hikers.'),
    ],
    'Faroe Islands': [
        ('stefan_travels', 5, 'Фарски Острови се сурова, дива убавина — водопади кои паѓаат во море, магла и зелени клифови.'),
        ('maja_journeys', 5, 'Other-worldly landscapes unlike anything in Europe. Gásadalur waterfall and Sørvágsvatn lake are incredible.'),
        ('ivan_mk', 4, 'Remote and wild but utterly unique. Weather is very unpredictable — pack for all seasons in one day.'),
    ],
    'Fez': [
        ('alex_wanderer', 5, 'Фез е живиот музеј на арапскиот свет. Медината е лавиринт кој ве вовлекува во средниот век.'),
        ('elena_traveller', 5, 'The medina of Fez is the most atmospheric place I have been. The tanneries are colourful and fascinating.'),
        ('marko_mk', 4, 'Incredibly authentic Moroccan city. Hire a local guide for the medina — you will get hopelessly lost without one.'),
    ],
    'Fiji': [
        ('sofia_explorer', 5, 'Фиџи е тропски рај со наjтопли луѓе на светот. Корален гребен, прозирно море и беспрекорни плажи!'),
        ('lena_world', 5, 'The friendliest people on the planet and the most beautiful reefs. Fiji truly lives up to its paradise reputation.'),
        ('stefan_travels', 4, 'Incredible island hopping experience. The Yasawa Islands are remote and stunning. Worth the long flight!'),
    ],
    'Galápagos Islands': [
        ('maja_journeys', 5, 'Галапагос е научна фантастика на живо — игуани, морски лавови и гигантски желки без страв од луѓе!'),
        ('ivan_mk', 5, 'The most unique wildlife experience on Earth. Animals that have never learned to fear humans — truly Darwinian.'),
        ('alex_wanderer', 5, 'Snorkelling with sea lions, swimming with penguins — the Galápagos blew my mind completely. Life-changing.'),
    ],
    'Goa': [
        ('elena_traveller', 4, 'Гоа нуди убави плажи, добра храна и опуштена атмосфера. Северното Гоа е поживо, Јужното е помирно.'),
        ('marko_mk', 4, 'Great beach destination with fantastic Portuguese colonial heritage in Old Goa. Anjuna market is fun.'),
        ('sofia_explorer', 5, 'Loved the mix of beach, culture and food. The seafood curry in Goa is some of the best in India.'),
    ],
    'Great Barrier Reef': [
        ('lena_world', 5, 'Големиот Бариерен Гребен е Светско Чудо под вода — корали, риби, морски желки. Неверојатно!'),
        ('stefan_travels', 5, 'Snorkelling and diving at the Great Barrier Reef is the best underwater experience in the world. Do it now!'),
        ('maja_journeys', 4, 'Stunning but the bleaching is visible in some areas. Choose a well-rated eco-operator who cares about the reef.'),
    ],
    'Hallstatt': [
        ('ivan_mk', 5, 'Халштат е најубавото село во Австрија — езерото, планините и старите куќи создаваат совршена почтенска картичка.'),
        ('alex_wanderer', 5, 'Hallstatt looks like a painting come to life. The salt mine tour adds great historical context. Magical.'),
        ('elena_traveller', 4, 'Incredibly beautiful but very crowded in summer. Arrive before 9am or after 5pm to enjoy it peacefully.'),
    ],
    'Hanoi': [
        ('marko_mk', 5, 'Ханој е автентичен и хаотичен — старото четврти, пего кафе и одличен пхо. Вистинскиот Виетнам!'),
        ('sofia_explorer', 5, 'The Old Quarter is a sensory overload in the best possible way. Egg coffee is a must-try local experience!'),
        ('lena_world', 4, 'Fascinating and cheap. The street food scene around Hoan Kiem Lake is outstanding. Great base for Halong Bay.'),
    ],
    'Havana': [
        ('stefan_travels', 5, 'Хавана е замрзнато во времето — класични американски автомобили, колонијална архитектура и куба либре!'),
        ('maja_journeys', 5, 'One of the most unique cities on Earth. The music, the colour, the vintage cars — Havana is like nowhere else.'),
        ('ivan_mk', 4, 'Fascinating and melancholic at once. Old Havana at night with live salsa music is truly unforgettable.'),
    ],
    'Hoi An': [
        ('alex_wanderer', 5, 'Хо Ан е најчаробниот град во Азиjа — фенери, жолти куќи и совршена храна. Апсолутно обожавам!'),
        ('elena_traveller', 5, 'Hoi An Ancient Town is utterly charming. Have clothes tailor-made — incredible quality at unbeatable prices.'),
        ('marko_mk', 4, 'Beautiful and romantic, especially at night when the lanterns are lit. Cao Lau noodles are delicious.'),
    ],
    'Hong Kong': [
        ('sofia_explorer', 5, 'Хонг Конг е урбан спектакл — небодери, пазари и одлична хранa. Погледот од Викторија Врв е неверојатен!'),
        ('lena_world', 5, 'The energy of Hong Kong is electric. Dim sum breakfasts, harbour cruises and night markets are unforgettable.'),
        ('stefan_travels', 4, 'An extraordinary city that mixes East and West perfectly. Take the tram to the Peak for epic skyline views.'),
    ],
    'Ibiza': [
        ('maja_journeys', 4, 'Ибица нуди повеќе од ноќниот живот — заедите на Формантера, старото место и одличните ресторани се прекрасни.'),
        ('ivan_mk', 4, 'The sunsets at Café del Mar are legendary for good reason. Ibiza has a beautiful side beyond the clubs.'),
        ('alex_wanderer', 5, 'Incredible island — beach by day, amazing nightlife by night. The north of the island is tranquil and beautiful.'),
    ],
    'Iguazu Falls': [
        ('elena_traveller', 5, 'Игуазу Водопади ги надминаа сите мои очекувања. Толку моќно и убаво — Нijагара изгледа мала в споредба!'),
        ('marko_mk', 5, 'The most powerful waterfalls on Earth. Devil\'s Throat walkway puts you right in the spray. Absolutely incredible!'),
        ('sofia_explorer', 5, 'Visit both the Argentine and Brazilian sides — each offers completely different and equally stunning views.'),
    ],
    'Interlaken': [
        ('lena_world', 5, 'Интерлакен е авантуристичка престолнина на светот. Парашутизам над Алпите е скоро неверoватно!'),
        ('stefan_travels', 5, 'The setting between two lakes with the Alps as backdrop is jaw-dropping. Paragliding here is life-changing.'),
        ('maja_journeys', 4, 'Perfect adventure hub. Jungfrau day trip is pricey but absolutely worth it for the views above the clouds.'),
    ],
    'Kathmandu': [
        ('ivan_mk', 5, 'Катманду е духовна точка на светот — ступите, моноотите и планините го создаваат неповторливиот Непал.'),
        ('alex_wanderer', 5, 'Pashupatinath Temple and Swayambhunath stupa are profound spiritual experiences. Gateway to the Himalayas.'),
        ('elena_traveller', 4, 'Chaotic and fascinating in equal measure. The trekking routes from here are world-famous for good reason.'),
    ],
    'Kilimanjaro': [
        ('marko_mk', 5, 'Килиманxаро е предизвик на животот. Достигнувањето на врвот Ухуру е незаборавен момент. Вреди секое напорно чекање!'),
        ('sofia_explorer', 5, 'Summit day is brutal but standing on the roof of Africa at sunrise is the most powerful feeling of my life.'),
        ('lena_world', 4, 'The trek is physically demanding but manageable with good preparation. Lemosho route is the most scenic.'),
    ],
    'Lake Bled': [
        ('stefan_travels', 5, 'Бледско Езеро е словенечка бајка — замокот на карпа, островот со црква и Алпите во позадина. Совршено!'),
        ('maja_journeys', 5, 'One of the most photogenic places in Europe. Row a pletna to the island and climb the 99 steps for the bell.'),
        ('ivan_mk', 4, 'Incredibly scenic and very accessible. Ojstrica viewpoint gives the classic postcard panorama of the lake.'),
    ],
    'Lake Como': [
        ('alex_wanderer', 5, 'Езерото Комо е италиjански луксуз на неjзин врв — вили, кипарис и модрозелена вода. Апсолутно прекрасно!'),
        ('elena_traveller', 5, 'The most beautiful lake in Italy. Bellagio is charming and Varenna is even better without the crowds.'),
        ('marko_mk', 4, 'Stunning scenery and lovely towns. Take the ferry to explore all the villages — it\'s the best way to see Como.'),
    ],
    'Las Vegas': [
        ('sofia_explorer', 4, 'Лас Вегас е луд и грандиозен — шоуата, казината и хотелите се во своја лига. Прекрасно за неколку дена!'),
        ('lena_world', 4, 'The Strip at night is a spectacle unlike any other. Go for the shows — Cirque du Soleil is world class.'),
        ('stefan_travels', 3, 'Fun for 2-3 days but overwhelming after that. Day trip to the Grand Canyon or Red Rock Canyon is essential.'),
    ],
    'Lofoten Islands': [
        ('maja_journeys', 5, 'Лофотенските Острови се норвешко чудо — рибарски села, дивите планини и поларната светлина се магични!'),
        ('ivan_mk', 5, 'The most dramatic scenery in Scandinavia. Red fishermen\'s cabins against jagged mountains — absolutely surreal.'),
        ('alex_wanderer', 5, 'Kayaking between the peaks at midnight sun was one of the highlights of my life. Utterly spectacular.'),
    ],
    'London': [
        ('elena_traveller', 5, 'Лондон е светска метропола — Тауерот, Биг Бен, Бриx Маркет и театарот на Вест Енд. Никогаш не се здодевуваш!'),
        ('marko_mk', 5, 'Greatest city in the world for museums — and they are all free. British Museum and National Gallery are outstanding.'),
        ('sofia_explorer', 4, 'Incredibly diverse and exciting. Borough Market for food, Hampstead Heath for nature — London has everything.'),
    ],
    'Luang Prabang': [
        ('lena_world', 5, 'Луанг Прабанг е мирна, духовна и прекрасна — будистички монаси, водопади и Меконг. Мојот омилен во Азија!'),
        ('stefan_travels', 5, 'The most serene and beautiful town in Southeast Asia. The monks\' alms ceremony at dawn is deeply moving.'),
        ('maja_journeys', 4, 'A spiritual retreat disguised as a tourist destination. Kuang Si waterfall is among the most beautiful I\'ve seen.'),
    ],
    'Machu Picchu': [
        ('ivan_mk', 5, 'Мачу Пичу е врвот на моjот список. Таму стоjат облаци, инкаски урнатини и маглата — апсолутно свето место.'),
        ('alex_wanderer', 5, 'The most iconic archaeological site on Earth. Hike the Inca Trail — the arrival through the Sun Gate is emotional.'),
        ('elena_traveller', 5, 'Nothing prepares you for the scale and drama of Machu Picchu. It genuinely takes your breath away.'),
    ],
    'Maldives': [
        ('marko_mk', 5, 'Малдиви се наjчист вид на совршенство — пренoclувалиштата над вода, нискиот ид и кораловите гребени се рај!'),
        ('sofia_explorer', 5, 'The most crystal-clear water I have ever seen. Overwater bungalow sunrises and bioluminescent nights are magic.'),
        ('lena_world', 4, 'Expensive but an unforgettable luxury experience. Snorkelling from the beach with turtles and rays is spectacular.'),
    ],
    'Masai Mara Safari': [
        ('stefan_travels', 5, 'Масаи Мара е Африка во неjзиниот чист облик. Годишната миграција на Вилдебести е спектакл без рамен!'),
        ('maja_journeys', 5, 'The Great Migration is one of the greatest natural spectacles on Earth. Lion kills, cheetah sprints — incredible.'),
        ('ivan_mk', 5, 'Seeing the Big Five in one day was beyond belief. Kenyan safari is the wildlife experience of a lifetime.'),
    ],
    'Medellín': [
        ('alex_wanderer', 5, 'Меделjин е приказна за трансформацијата — кабел-железница, паркови и неверојатна енергија. Нов Латино Хаб!'),
        ('elena_traveller', 5, 'One of the most dynamic and innovative cities in Latin America. The cable car to the hillside communities is essential.'),
        ('marko_mk', 4, 'Fascinating story of urban reinvention. Eternal spring climate, great coffee and very friendly locals.'),
    ],
    'Melbourne': [
        ('sofia_explorer', 5, 'Мелбурн е светска класа — кафе сцена, уметност, дизаjн и невероjатна разновидност на храна. Мoja omilena!')
        ,
        ('lena_world', 5, 'The best coffee culture in the world. Laneway bars, street art and the most incredible food scene in Australia.'),
        ('stefan_travels', 4, 'Vibrant, creative and very liveable. The Great Ocean Road day trip is not to be missed.'),
    ],
    'Mexico City': [
        ('maja_journeys', 5, 'Мексико Сити е огромен и неверojатен — Теотивакан, музеи, тако и луrмиозен уличен живот!'),
        ('ivan_mk', 5, 'The most underrated capital in the Americas. Frida Kahlo Museum, Teotihuacan pyramids and the best tacos anywhere.'),
        ('alex_wanderer', 4, 'Enormous city but the historic centre and Coyoacán are very walkable. Street food here is world class.'),
    ],
    'Miami': [
        ('elena_traveller', 4, 'Мајами е сјаен — Art Deco Бич, Вајнвуд ѕидови и одлични кубански ресторани. Топло и живо!'),
        ('marko_mk', 4, 'South Beach is iconic. The Wynwood arts district is brilliant and the Cuban food in Little Havana is authentic.'),
        ('sofia_explorer', 5, 'Glamorous, sunny and diverse. Perfect for beach days, art galleries and amazing nightlife all in one trip.'),
    ],
    'Monaco': [
        ('lena_world', 4, 'Монако е луксуз концентриран на 2 km² — казиното, jaхтите и Формула 1 патеката се единствени на светот.'),
        ('stefan_travels', 4, 'The most densely packed luxury destination in the world. The Prince\'s Palace and Oceanographic Museum are excellent.'),
        ('maja_journeys', 3, 'Very expensive but fun to visit for a day from Nice. Casino Monte-Carlo is a spectacular building.'),
    ],
    'Mykonos': [
        ('ivan_mk', 5, 'Миконос е грчки луксуз — белобелите куќи, Малиот Венеција и вечерите при зајдисонце се совршени!'),
        ('alex_wanderer', 4, 'Glamorous and beautiful but very expensive. Paradise Beach is fun, Little Venice at sunset is magical.'),
        ('elena_traveller', 4, 'Stunning island but very overpriced. Combine with quieter Naxos or Paros for better value.'),
    ],
    'Napa Valley': [
        ('marko_mk', 5, 'Напа Вали е Калифорниjа на нejзиниот врв — бескраjни лозjа, ознакени вина и Мишлинови ресторани. Перфектно!'),
        ('sofia_explorer', 4, 'World-class wine country. Balloon ride over the vineyards at dawn is the most romantic experience imaginable.'),
        ('lena_world', 4, 'Beautiful rolling wine country. Hire bikes and cycle between wineries — perfect way to spend a day here.'),
    ],
    'New Orleans': [
        ('stefan_travels', 5, 'Нов Орлеанс е џез, гамбо и Маrди Гра. Bourbon Street е преполна, но French Quarter е апсолутна магија!'),
        ('maja_journeys', 5, 'The most unique city in America. Jazz pouring from every door, incredible Creole food and fascinating history.'),
        ('ivan_mk', 4, 'Beignets at Café Du Monde, ghost tours of the French Quarter, live jazz on Frenchmen Street — utterly unique.'),
    ],
    'New York City': [
        ('alex_wanderer', 5, 'Нy Јорк е сон на живо — Сентрал Парк, Мет, Бруклин Мост и неисцрпната eneрgija. Запира дишење!'),
        ('elena_traveller', 5, 'The energy of New York is like nowhere else. Central Park, the Met, Brooklyn Bridge — all iconic and brilliant.'),
        ('marko_mk', 4, 'Greatest city in the world for culture and food. Walk the High Line and eat your way through all five boroughs.'),
    ],
    'Norwegian Fjords': [
        ('sofia_explorer', 5, 'Норвешките Фjордови се природна рикошет — Geiranger и Nærøy фjордовите ги надминуваат сите фотографии!'),
        ('lena_world', 5, 'The fjords are more dramatic and beautiful than any photograph can convey. The cruise from Bergen is perfect.'),
        ('stefan_travels', 4, 'Breathtaking scenery at every turn. Flåm railway is a brilliant way to see the fjords from above and below.'),
    ],
    'Osaka': [
        ('maja_journeys', 5, 'Осака е кулинарска престолнина на Јапонија — такоjаки, окономиjаки и рамен на секој агол!'),
        ('ivan_mk', 5, 'Osaka is Japan\'s most fun city. Dotonbori at night is neon-lit insanity in the best possible way.'),
        ('alex_wanderer', 4, 'More relaxed and funnier than Tokyo. Osaka Castle is impressive and the food scene is unbeatable.'),
    ],
    'Patagonia': [
        ('elena_traveller', 5, 'Патагониjа е kraj на светот во вистинска смисла — глечери, торес и вечни ветришта. Диво совршенство!'),
        ('marko_mk', 5, 'Torres del Paine is one of the most dramatic landscapes on Earth. The W Trek is challenging and utterly glorious.'),
        ('sofia_explorer', 5, 'The Perito Moreno glacier calving is one of the great natural spectacles. Raw and magnificent wilderness.'),
    ],
    'Petra': [
        ('ljena_world', 5, 'Петра е едно од чудата на светот со право — Трезорот осветлен со свеќи е мistical и незаборавен!'),
        ('stefan_travels', 5, 'Walking through the Siq and seeing the Treasury emerge is one of the great dramatic moments in travel.'),
        ('maja_journeys', 4, 'Petra by Night is magical. Allow 2 full days — there is far more to see beyond the Treasury.'),
    ],
    'Phuket': [
        ('ivan_mk', 4, 'Пукет нуди убави плажи и живо ноќно живеење. Патонг е бучен, но западниот брег е убав и мирен.'),
        ('alex_wanderer', 4, 'Good base for island hopping. Phi Phi Islands day trip is stunning. Old Phuket Town is underrated.'),
        ('elena_traveller', 3, 'Beautiful beaches but very touristy. Head north to Khao Lak or south to Koh Lanta for fewer crowds.'),
    ],
    'Plitvice Lakes': [
        ('marko_mk', 5, 'Плитвичките Езера се хрватска природна магија — тиркизните езера поврзани со водопади се совршенство!'),
        ('sofia_explorer', 5, 'The most beautiful national park in Europe. Turquoise terraced lakes and waterfalls everywhere. Fairytale!'),
        ('lena_world', 4, 'Stunning but very crowded. Book tickets well in advance and arrive at opening time for the best experience.'),
    ],
    'Porto': [
        ('stefan_travels', 5, 'Порто е автентичен португалски бисер — азулехос плочки, порт вино и мостот Луис I при зајдисонце. Обожавам!'),
        ('maja_journeys', 5, 'One of the most beautiful and affordable cities in Europe. Ribeira neighbourhood is pure magic at sunset.'),
        ('ivan_mk', 4, 'Wonderful walking city. The port wine cellars in Vila Nova de Gaia are a must. Francesinha sandwich is insane!'),
    ],
    'Portofino': [
        ('alex_wanderer', 5, 'Портофино е скапо, но неодоливо убаво — пастелните куќи и jахтите во малото пристаниште се иконски!'),
        ('elena_traveller', 4, 'Arguably the most glamorous village in Italy. Hike from Santa Margherita for the best clifftop views.'),
        ('marko_mk', 5, 'The most beautiful harbour in the Mediterranean. The gelato overlooking the piazzetta is a perfect moment.'),
    ],
    'Queenstown': [
        ('sofia_explorer', 5, 'Квинстаун е авантуристичката престолнина — банџи скок, скијање и Милфорд Саунд. Нова Зеландија е неверојатна!'),
        ('lena_world', 5, 'Adventure capital of the world for good reason. Milford Sound day trip is one of the most beautiful on Earth.'),
        ('stefan_travels', 4, 'Spectacular alpine setting and great activities year-round. The gondola views over the lake are outstanding.'),
    ],
    'Reykjavik': [
        ('maja_journeys', 5, 'Рекjaвик е портата кон исландски чуда — Северните светлини, гejзерите и ледничките лагуни се незаборавни!'),
        ('ivan_mk', 5, 'Iceland is another planet. The Northern Lights, the Golden Circle and the Blue Lagoon are all extraordinary.'),
        ('alex_wanderer', 5, 'Most unique country I have visited. Midnight sun in summer and aurora in winter — Iceland never disappoints.'),
    ],
    'Rio de Janeiro': [
        ('elena_traveller', 5, 'Рио де Жанеиро е карневал на животот — Копакабана, Криступ Спасителот и Сугарлоаф. Колоритно и страсно!'),
        ('marko_mk', 5, 'Christ the Redeemer at sunset with the city below is one of the great views of the world. Rio is spectacular.'),
        ('sofia_explorer', 4, 'Beautiful and exciting city. Take the cable car to Sugarloaf Mountain — the view over Guanabara Bay is epic.'),
    ],
    'Rotorua': [
        ('lena_world', 4, 'Роторуа е геотермален феномен — гejзери, кал бари и маорска култура во едно место. Незаборавно и уникатно!'),
        ('stefan_travels', 4, 'Fascinating geothermal area. The Māori cultural show and hangi dinner are genuinely moving experiences.'),
        ('maja_journeys', 4, 'Unique destination. Te Puia geyser is impressive and the Wai-O-Tapu Thermal Wonderland is like another planet.'),
    ],
    'San Francisco': [
        ('ivan_mk', 5, 'Сан Франциско е град на контрасти — Голдeн Гejт, трамваи, Чаjнатаун и Алкатраз. Iконски и убав!'),
        ('alex_wanderer', 5, 'One of the most beautiful and characterful cities in America. The Golden Gate Bridge never gets old.'),
        ('elena_traveller', 4, 'Wonderful city to explore on foot. Ride the cable cars, walk across the Golden Gate, eat at the Ferry Building.'),
    ],
    'Scottish Highlands': [
        ('marko_mk', 5, 'Шкотскиот Виsorамен е дива, романтична убавина — замоци, лохови и зелени котлини. Лос Сенос, Скај Ај!'),
        ('sofia_explorer', 5, 'The most atmospheric and dramatic landscapes in the UK. Isle of Skye is other-worldly. Glencoe is haunting.'),
        ('lena_world', 4, 'Road trip through the Highlands is unforgettable. Eilean Donan Castle is as romantic as it looks in photos.'),
    ],
    'Sedona': [
        ('stefan_travels', 5, 'Седона е духовна и визуелна магија — портокалови карпи, нилска небо и виברационска eнергиjа. Незаборавно!'),
        ('maja_journeys', 5, 'The red rock formations are surreal and stunning. Best sunset I have ever seen was from Airport Mesa overlook.'),
        ('ivan_mk', 4, 'Incredible high desert landscape. Cathedral Rock and Bell Rock hikes offer spectacular views with moderate effort.'),
    ],
    'Seoul': [
        ('alex_wanderer', 5, 'Сеул е перфектна мешавина на традицијата и иднината — Гионг-Бокgung, K-pop, јукке и хangул. Го сакам!'),
        ('elena_traveller', 5, 'Most exciting city in Asia. Bukchon Hanok Village, street food in Myeongdong, palaces — Seoul has everything.'),
        ('marko_mk', 4, 'Brilliant food, great shopping and fascinating culture. Namsan Tower cable car views over Seoul are superb.'),
    ],
    'Serengeti': [
        ('sofia_explorer', 5, 'Серенgети е африканската душа — бескрajната рамнина, лавовите и слоновите при зајдисонце. Незаборавно!'),
        ('lena_world', 5, 'The most epic wildlife experience on Earth. Over a million wildebeest migrating is simply staggering to witness.'),
        ('stefan_travels', 4, 'World-class safari destination. Hot air balloon at dawn over the Serengeti plains is the ultimate experience.'),
    ],
    'Seychelles': [
        ('maja_journeys', 5, 'Сеjшели се наjубавите плажи на светот — гранитни карпи, бирквизна вода и тропска природа. Рај!'),
        ('ivan_mk', 5, 'Praslin\'s Anse Lazio is the most beautiful beach I have ever been to. The giant tortoises on La Digue are magical.'),
        ('alex_wanderer', 4, 'Incredibly beautiful but expensive. Island hopping between Mahé, Praslin and La Digue is essential.'),
    ],
    'Siem Reap': [
        ('elena_traveller', 5, 'Сием Реап е портата кон Ангкор Ват — највеличествениот храмски комплекс на светот. Мистичен и грандиозен!'),
        ('marko_mk', 5, 'Angkor Wat at sunrise is one of the most breathtaking sights in Asia. The temple complex is enormous and awe-inspiring.'),
        ('sofia_explorer', 4, 'Fascinating destination. Hire a tuk-tuk for the temples — the driver\'s knowledge adds so much to the experience.'),
    ],
    'Singapore': [
        ('lena_world', 5, 'Сингапур е иднината денес — Marina Bay Sands, Gardens by the Bay и храната на хoкeр центрите се врвни!'),
        ('stefan_travels', 5, 'The cleanest, most efficient city in Asia. Hawker centres offer some of the world\'s best food at minimal cost.'),
        ('maja_journeys', 4, 'An incredible stopover destination. The Gardens by the Bay at night are visually stunning and futuristic.'),
    ],
    'Sydney': [
        ('ivan_mk', 5, 'Сjдниjа е еден од наjубавите градови — Oперата, Харбур Брич и Бонди плажа формираат незаборавна тријада!'),
        ('alex_wanderer', 5, 'Sydney Opera House and Harbour Bridge together are the most iconic urban skyline in the Southern Hemisphere.'),
        ('elena_traveller', 4, 'Beautiful coastal city with a relaxed lifestyle. Walk the Bondi to Coogee coastal path for amazing ocean views.'),
    ],
    'Tbilisi': [
        ('marko_mk', 5, 'Тбилиси е скриен бисер — серните бањи, Нарикала тврдина и виното. Грузиjа е наjнедооценета земjа!'),
        ('sofia_explorer', 5, 'One of the most underrated capitals in the world. The Old Town, the sulfur baths and Georgian food are superb.'),
        ('lena_world', 4, 'Fascinating mix of Orthodox churches, mosques and Soviet architecture. Georgian wine is world-class and very cheap.'),
    ],
    'Tulum': [
        ('stefan_travels', 5, 'Тулум е совршен спој — мajански урнатини над Карипско Море, ценоти и бохо вилаi. Мексико на неговиот врв!'),
        ('maja_journeys', 5, 'The most Instagram-worthy ruin in Mexico — but it genuinely deserves it. Cenote swimming is unforgettable.'),
        ('ivan_mk', 4, 'Beautiful and spiritual destination. Rent a bike to explore the coast and cenotes — it\'s the best way to see Tulum.'),
    ],
    'Tuscany': [
        ('alex_wanderer', 5, 'Тоскана е совршенство — кипарис, лозjа, villa и прекрасни средновековни градови. Италија на нejзин врв!'),
        ('elena_traveller', 5, 'Rolling hills, cypress trees, perfect wine and amazing food. Tuscany is everything beautiful about Italy distilled.'),
        ('marko_mk', 4, 'The most beautiful countryside in Europe. Val d\'Orcia is a UNESCO landscape for very good reason.'),
    ],
    'Valletta': [
        ('sofia_explorer', 5, 'Валета е наjмал главен град на ЕУ, но со огромна историja — баrocni цркви, канони и Малтешки убавини.'),
        ('lena_world', 4, 'A remarkable baroque city packed into a tiny peninsula. Upper Barrakka Gardens offer stunning views of the Grand Harbour.'),
        ('stefan_travels', 4, 'Underrated European capital. The co-cathedral of St John is one of the most ornate interiors I have seen.'),
    ],
    'Vancouver': [
        ('maja_journeys', 5, 'Ванкувер е совршенство — планини, море, Stanley Park и мултикултурна храна. Наjубавиот град во Канада!'),
        ('ivan_mk', 5, 'Mountains, ocean and forest all within the city limits. Stanley Park is the best urban park in North America.'),
        ('alex_wanderer', 4, 'Stunning natural setting and very liveable city. Granville Island market is excellent and Whistler is nearby.'),
    ],
    'Victoria Falls': [
        ('elena_traveller', 5, 'Викториjа Водопади се задушувачки — димот и буката на водата се слушаат и чувствуваат километри далеку!'),
        ('marko_mk', 5, 'The largest waterfall in the world by total volume. The spray can be felt from a kilometre away. Truly magnificent.'),
        ('sofia_explorer', 4, 'Extraordinary natural wonder. Devil\'s Pool swimming at the edge is terrifying and exhilarating. Unforgettable!'),
    ],
    'Zanzibar': [
        ('lena_world', 5, 'Занзибар е афрички тропски рај — Stone Town, чинговите плажи и зачините создаваат уникатна атмосфера!'),
        ('stefan_travels', 5, 'Perfect beach holiday with fascinating Swahili culture. Stone Town is a UNESCO World Heritage site for good reason.'),
        ('maja_journeys', 4, 'Beautiful spice island. Nungwi Beach is paradise and the sunset dhow cruise is genuinely magical.'),
    ],
    'Zermatt': [
        ('ivan_mk', 5, 'Цермат и Матерхорн се симболи на швајцарски совршенство. Возот до Горнерграт и погледот на врвовите е духовно!'),
        ('alex_wanderer', 5, 'The most iconic mountain view in the Alps. Matterhorn is even more dramatic in real life than in photos.'),
        ('elena_traveller', 4, 'Beautiful car-free mountain village. The Glacier Paradise cable car is the highest in the Alps — incredible views.'),
    ],
}


class Command(BaseCommand):
    help = 'Populate database with fake users and reviews for popular destinations'

    def handle(self, *args, **options):
        self.stdout.write('Creating fake users...')
        users = {}
        for u in FAKE_USERS:
            user, created = User.objects.get_or_create(
                username=u['username'],
                defaults={
                    'email': u['email'],
                    'first_name': u.get('first_name', ''),
                    'last_name': u.get('last_name', ''),
                }
            )
            if created:
                user.set_password('TravelMind2024!')
                user.save()
            users[u['username']] = user
        self.stdout.write(f'  {len(users)} users ready.')

        self.stdout.write('Creating reviews...')
        created_count = 0
        skipped_count = 0
        for dest_name, review_list in REVIEWS.items():
            try:
                dest = Destination.objects.get(name=dest_name)
            except Destination.DoesNotExist:
                self.stdout.write(f'  Skipping {dest_name} — not found in DB')
                continue
            for username, rating, comment in review_list:
                user = users.get(username)
                if not user:
                    continue
                _, created = Review.objects.get_or_create(
                    user=user,
                    destination=dest,
                    defaults={'rating': rating, 'comment': comment},
                )
                if created:
                    created_count += 1
                else:
                    skipped_count += 1

        self.stdout.write(self.style.SUCCESS(
            f'Done. Created {created_count} reviews, skipped {skipped_count} existing.'
        ))
