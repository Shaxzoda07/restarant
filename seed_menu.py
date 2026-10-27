from django.core.management.base import BaseCommand

from restaurant.models import Category, Dish, Table

MENU = [
    ("Milliy taomlar", "🍚", [
        ("Buxoro oshi (to‘y oshi)", "Devzira guruchi, mol go‘shti, sariq sabzi, nohat va mayiz. Qozonda, o‘tin olovida damlangan.", 62000, "400 g", "🍚", True, False),
        ("Samarqand oshi", "Go‘shtli, sarimsoqpiyozli, dumba yog‘ida dimlangan, qorako‘z mayizli an’anaviy osh.", 58000, "400 g", "🍛", True, False),
        ("Dimlama", "Mol go‘shti, kartoshka, pomidor, bolgar qalampiri va ko‘katlar — o‘z sharbatida dimlangan.", 56000, "380 g", "🥘", False, False),
        ("Qozon kabob", "Qovurilgan qo‘zi go‘shti va kartoshka, piyoz bilan, qozonda tayyorlangan.", 69000, "350 g", "🍖", False, False),
        ("Qo‘lda cho‘zilgan lag‘mon", "Qo‘lda cho‘zilgan uy lag‘moni, sabzavotli go‘shtli sho‘rva bilan.", 46000, "450 g", "🍜", True, False),
    ]),
    ("Sho‘rvalar", "🍲", [
        ("Mastava", "Guruchli, go‘shtli, sabzavotli quyuq sho‘rva, qatiq bilan.", 34000, "350 ml", "🍲", False, False),
        ("Shurpa", "Qo‘zi go‘shtli, yirik sabzavotli, ko‘katli to‘yimli sho‘rva.", 42000, "400 ml", "🥣", False, False),
        ("Moshxo‘rda", "Mosh, guruchli, qatiq va zira bilan — an’anaviy yengil sho‘rva.", 32000, "350 ml", "🥣", False, False),
    ]),
    ("Somsa va xamir taomlar", "🥟", [
        ("Tandir somsa", "Qo‘y go‘shti va dumbali, tandirda pishirilgan qatlamali somsa.", 18000, "1 dona", "🥟", True, False),
        ("Samarqand non", "Tandirda yopilgan, kunjutli, dumaloq Samarqand noni.", 12000, "1 dona", "🫓", False, False),
        ("Manti", "Qo‘y go‘shti va piyozli, bug‘da pishirilgan yirik manti (5 dona).", 44000, "5 dona", "🥟", False, False),
        ("Chuchvara", "Mayda chuchvara, sho‘rvada yoki qatiq bilan.", 38000, "300 g", "🥟", False, False),
    ]),
    ("Kabob va gril", "🍢", [
        ("Qo‘y go‘shtli shashlik", "Mayin qo‘y go‘shti, ko‘mirda, piyoz va sumak bilan.", 29000, "1 sixga", "🍢", True, False),
        ("Jiz-biz", "Qo‘y jigari va ichki yog‘, ko‘mirda — Buxoro uslubida.", 78000, "300 g", "🍖", False, False),
        ("Tandir go‘sht", "Tandirda 4 soat pishirilgan qo‘zi qovurg‘asi.", 98000, "450 g", "🍖", True, False),
    ]),
    ("Zamonaviy taomlar", "✨", [
        ("Qo‘zi karre — anor sousida", "Sekin pishirilgan qo‘zi karre, anor demi-glas, kartoshka pyuresi.", 128000, "320 g", "🍷", True, True),
        ("Laganda tuxum-barak", "Zamonaviy talqindagi barak, brinza va sabzavotli yostiq bilan.", 64000, "280 g", "🍽️", False, True),
        ("Losos — zafaron sousida", "Zafaronli qaymoqli sous, qovurilgan sabzavotlar bilan.", 118000, "250 g", "🐟", False, True),
        ("Jigar pate va non", "Uy pate, anjir murabbosi va issiq tandir noni.", 52000, "150 g", "🥖", False, True),
    ]),
    ("Salatlar", "🥗", [
        ("Achchiq-chuchuk", "Yangi pomidor, piyoz, achchiq qalampir — an’anaviy yengil salat.", 22000, "250 g", "🥗", False, False),
        ("Buxoro salati", "Qovurilgan go‘sht, bodring, pomidor, yangi ko‘katlar.", 48000, "280 g", "🥗", False, False),
        ("Anor-qo‘y pishlog‘i salati", "Anor donalari, yashil salat, brinza va yong‘oq.", 46000, "230 g", "🥗", False, True),
    ]),
    ("Shirinliklar", "🍯", [
        ("Pashmak", "Qo‘lda tortilgan an’anaviy shirinlik, yong‘oq bilan.", 24000, "100 g", "🍬", False, False),
        ("Asal va yong‘oqli chak-chak", "Uyda pishirilgan chak-chak, tog‘ asali bilan.", 32000, "150 g", "🍯", True, False),
        ("Halva bilan qaymoq", "Qaymoq, uy halvasi va yangi mevalar.", 36000, "180 g", "🍮", False, True),
    ]),
    ("Ichimliklar", "🫖", [
        ("Ko‘k choy (choynak)", "Choynakda damlangan ko‘k choy, mayiz va nabot bilan.", 14000, "700 ml", "🫖", False, False),
        ("Anor sharbati", "Yangi siqilgan anor sharbati.", 26000, "300 ml", "🍹", False, False),
        ("Uy kompoti", "Mavsumiy quritilgan mevalardan tayyorlangan kompot.", 16000, "400 ml", "🍹", False, False),
        ("Mors (na’matak)", "Na’matak va asalli sovuq ichimlik.", 18000, "350 ml", "🥤", False, False),
    ]),
]


class Command(BaseCommand):
    help = "Boshlang'ich menyu va stollarni yaratadi (faqat baza bo'sh bo'lsa)"

    def handle(self, *args, **options):
        if Category.objects.exists():
            self.stdout.write("Menyu allaqachon mavjud — o'tkazib yuborildi")
            return
        for ci, (cname, icon, dishes) in enumerate(MENU):
            cat = Category.objects.create(name=cname, icon=icon, order=ci)
            for di, (name, desc, price, weight, emoji, popular, new) in enumerate(dishes):
                Dish.objects.create(category=cat, name=name, description=desc, price=price, weight=weight,
                                    emoji=emoji, is_popular=popular, is_new=new, order=di)
        zones = ["hall"] * 6 + ["terrace"] * 3 + ["vip"] * 2 + ["choyxona"] * 2
        seats = [2, 2, 4, 4, 4, 6, 4, 4, 6, 8, 10, 8, 12]
        for i, z in enumerate(zones, start=1):
            Table.objects.create(number=i, zone=z, seats=seats[i - 1])
        self.stdout.write(self.style.SUCCESS("Menyu va stollar yaratildi"))
