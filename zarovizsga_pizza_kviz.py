import datetime
import json
import os
import unicodedata


REKORD_FAJL = os.path.join(os.path.dirname(__file__), "pizza_kviz_eredmenyek.json")



def ekezet_nelkul(szoveg):
    normalizalt = unicodedata.normalize("NFD", szoveg)
    return "".join(betu for betu in normalizalt if unicodedata.category(betu) != "Mn")


def tisztit(szoveg):
    return ekezet_nelkul(szoveg.strip().lower())


def valasz_beker(szoveg):
    return input(szoveg + " ").strip()


def egesz_szam_beker(szoveg):
    while True:
        try:
            return int(input(szoveg + " "))
        except ValueError:
            print("Egész számot adj meg!")


def lebego_szam_beker(szoveg):
    while True:
        try:
            return float(input(szoveg + " ").replace(",", "."))
        except ValueError:
            print("Számot adj meg!")


def szazalek_szamitas(pont, max_pont):
    if max_pont == 0:
        return 0
    return round(pont / max_pont * 100, 2)


def ertekeles_szoveg(szazalek):
    if szazalek >= 90:
        return "Nagyon ügyes vagy!"
    if szazalek >= 75:
        return "Szép eredmény!"
    if szazalek >= 50:
        return "Ez már egész jó."
    return "Érdemes még gyakorolni."



def szoveges_kerdes(kerdes):
    valasz = valasz_beker(kerdes["szoveg"])
    elfogadott = kerdes["helyes"]

    if kerdes.get("pontos", False):
        jo = valasz.strip().lower() in [h.lower() for h in elfogadott]
    else:
        tisztitott_valasz = tisztit(valasz)
        jo = tisztitott_valasz in [tisztit(h) for h in elfogadott]

    if jo:
        return kerdes["pont"], "Jó válasz."

    return 0, "Nem jó. Elfogadott válasz: " + elfogadott[0]


def egesz_kerdes(kerdes):
    valasz = egesz_szam_beker(kerdes["szoveg"])
    helyes = kerdes["helyes"]

    if valasz == helyes:
        return kerdes["pont"], "Jó válasz, pontos találat."

    elteres = abs(valasz - helyes) / helyes * 100

    if elteres <= kerdes.get("reszpont_hatar", 25):
        return kerdes["pont"] / 2, f"Közel volt. A helyes válasz: {helyes}."

    return 0, f"Nem jó. A helyes válasz: {helyes}."


def lebego_kerdes(kerdes):
    valasz = lebego_szam_beker(kerdes["szoveg"])
    helyes = kerdes["helyes"]
    tolerancia = kerdes["tolerancia"]

    if abs(valasz - helyes) <= tolerancia:
        return kerdes["pont"], "Jó válasz, tolerancián belül van."

    return 0, f"Nem jó. A helyes válasz körülbelül {helyes}."


def igaz_hamis_kerdes(kerdes):
    while True:
        valasz = valasz_beker(kerdes["szoveg"] + " (igaz/hamis)")
        valasz = tisztit(valasz)

        if valasz in ["igaz", "i"]:
            logikai_valasz = True
            break
        if valasz in ["hamis", "h"]:
            logikai_valasz = False
            break

        print("Igaz vagy hamis választ adj meg!")

    if logikai_valasz == kerdes["helyes"]:
        return kerdes["pont"], "Jó válasz."

    helyes_szoveg = "igaz" if kerdes["helyes"] else "hamis"
    return 0, f"Nem jó. A helyes válasz: {helyes_szoveg}."


def abcd_kerdes(kerdes):
    print(kerdes["szoveg"])

    for betu, szoveg in kerdes["opciok"].items():
        print(f"  {betu}) {szoveg}")

    if kerdes.get("tobb_valasz", False):
        valasz = valasz_beker("Válaszbetűk vesszővel elválasztva")
        valaszok = {darab.strip().upper() for darab in valasz.split(",") if darab.strip()}
    else:
        valasz = valasz_beker("Válaszbetű")
        valaszok = {valasz.upper()}

    helyes = set(kerdes["helyes"])

    if valaszok == helyes:
        return kerdes["pont"], "Jó válasz."

    jo_talalat = len(valaszok & helyes)
    rossz_talalat = len(valaszok - helyes)

    if kerdes.get("tobb_valasz", False) and jo_talalat > 0 and rossz_talalat == 0:
        reszpont = kerdes["pont"] * jo_talalat / len(helyes)
        return round(reszpont, 2), "Részben jó, de nem találtál meg minden helyes választ."

    return 0, "Nem jó. Helyes válasz: " + ", ".join(sorted(helyes))


def halmaz_kerdes(kerdes):
    valasz = valasz_beker(kerdes["szoveg"] + " Vesszővel válaszd el a válaszokat!")
    valaszok = {tisztit(darab) for darab in valasz.split(",") if darab.strip()}
    eredeti_valaszok = {tisztit(elem): elem for elem in kerdes["helyes"]}
    helyes = set(eredeti_valaszok)

    talalatok = valaszok & helyes
    hianyzo = helyes - valaszok

    if talalatok == helyes:
        return kerdes["pont"], "Minden szükséges elemet felsoroltál."

    reszpont = kerdes["pont"] * len(talalatok) / len(helyes)
    visszajelzes = "Találatok: " + str(len(talalatok)) + "/" + str(len(helyes))

    if hianyzo:
        hianyzo_szavak = [eredeti_valaszok[elem] for elem in hianyzo]
        visszajelzes += ". Kimaradt: " + ", ".join(sorted(hianyzo_szavak))

    return round(reszpont, 2), visszajelzes



def rekordok_betoltes():
    try:
        with open(REKORD_FAJL, "r", encoding="utf-8") as fajl:
            return json.load(fajl)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        return []


def rekordok_mentes(rekordok):
    with open(REKORD_FAJL, "w", encoding="utf-8") as fajl:
        json.dump(rekordok, fajl, indent=4, ensure_ascii=False)


def eredmeny_mentes(nev, pont, max_pont):
    rekordok = rekordok_betoltes()
    szazalek = szazalek_szamitas(pont, max_pont)

    uj_rekord = {
        "nev": nev,
        "datum": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "pont": pont,
        "max_pont": max_pont,
        "szazalek": szazalek
    }

    rekordok.append(uj_rekord)
    rekordok_mentes(rekordok)


def legjobb_eredmeny_kiiras():
    rekordok = rekordok_betoltes()

    if not rekordok:
        print("Még nincs mentett rekord.")
        return

    legjobb = max(rekordok, key=lambda rekord: rekord["szazalek"])
    print("Legjobb eddigi eredmény:")
    print(f"{legjobb['nev']} - {legjobb['szazalek']}% ({legjobb['pont']}/{legjobb['max_pont']} pont)")



kerdesek = [
    {
        "tipus": "szoveg",
        "szoveg": "Melyik városból származik a nápolyi pizza?",
        "helyes": ["Nápoly"],
        "pontos": True,
        "pont": 1
    },
    {
        "tipus": "szoveg",
        "szoveg": "Melyik az egyik legismertebb olasz pizza, amelynek neve hasonlít egy női névre?",
        "helyes": ["Margherita", "Margarita"],
        "pontos": False,
        "pont": 1
    },
    {
        "tipus": "egesz",
        "szoveg": "Hány fokos kemencében sütik körülbelül a nápolyi pizzát?",
        "helyes": 450,
        "reszpont_hatar": 25,
        "pont": 1
    },
    {
        "tipus": "egesz",
        "szoveg": "Hány perc alatt sül meg körülbelül egy nápolyi pizza?",
        "helyes": 2,
        "reszpont_hatar": 50,
        "pont": 1
    },
    {
        "tipus": "lebego",
        "szoveg": "Hány százalék víz kerül körülbelül a pizzatésztába 100 g liszthez viszonyítva?",
        "helyes": 60.0,
        "tolerancia": 5.0,
        "pont": 1
    },
    {
        "tipus": "igaz_hamis",
        "szoveg": "A klasszikus nápolyi pizzatésztába tojás is kerül.",
        "helyes": False,
        "pont": 1
    },
    {
        "tipus": "abcd",
        "szoveg": "Melyik sajt jellemző leginkább a klasszikus olasz pizzára?",
        "opciok": {
            "A": "mozzarella",
            "B": "cheddar",
            "C": "trappista",
            "D": "füstölt sajt"
        },
        "helyes": ["A"],
        "tobb_valasz": False,
        "pont": 1
    },
    {
        "tipus": "abcd",
        "szoveg": "Mely hozzávalók tartozhatnak egy egyszerű pizzatésztához?",
        "opciok": {
            "A": "liszt",
            "B": "víz",
            "C": "tojás",
            "D": "só",
            "E": "élesztő"
        },
        "helyes": ["A", "B", "D", "E"],
        "tobb_valasz": True,
        "pont": 1
    },
    {
        "tipus": "halmaz",
        "szoveg": "Sorolj fel három alapvető pizzatészta-hozzávalót!",
        "helyes": {"liszt", "víz", "só"},
        "pont": 1
    },
    {
        "tipus": "halmaz",
        "szoveg": "Sorolj fel három feltétet vagy alapanyagot, ami egy Margherita pizzán szerepelhet!",
        "helyes": {"paradicsom", "mozzarella", "bazsalikom"},
        "pont": 1
    }
]


def kviz_inditas():
    print("Pizza kvíz - záróvizsga projekt")
    print("Válaszolj a 10 pizzás kérdésre!")
    print()

    nev = valasz_beker("Add meg a neved")
    if nev == "":
        nev = "Névtelen játékos"

    pont = 0
    max_pont = sum(kerdes["pont"] for kerdes in kerdesek)

    print()
    print("Kezdődik a kvíz!")
    print()

    for sorszam, kerdes in enumerate(kerdesek, 1):
        print(f"{sorszam}. kérdés")
        if kerdes["tipus"] == "szoveg":
            kapott_pont, visszajelzes = szoveges_kerdes(kerdes)
        elif kerdes["tipus"] == "egesz":
            kapott_pont, visszajelzes = egesz_kerdes(kerdes)
        elif kerdes["tipus"] == "lebego":
            kapott_pont, visszajelzes = lebego_kerdes(kerdes)
        elif kerdes["tipus"] == "igaz_hamis":
            kapott_pont, visszajelzes = igaz_hamis_kerdes(kerdes)
        elif kerdes["tipus"] == "abcd":
            kapott_pont, visszajelzes = abcd_kerdes(kerdes)
        elif kerdes["tipus"] == "halmaz":
            kapott_pont, visszajelzes = halmaz_kerdes(kerdes)
        pont += kapott_pont
        print(visszajelzes)
        print(f"Kapott pont: {kapott_pont}/{kerdes['pont']}")
        print()

    szazalek = szazalek_szamitas(pont, max_pont)

    print("Eredmény")
    print("--------")
    print(f"Pontszám: {pont}/{max_pont}")
    print(f"Százalék: {szazalek}%")
    print(ertekeles_szoveg(szazalek))
    print()

    eredmeny_mentes(nev, pont, max_pont)
    print(f"Az eredményt elmentettem ebbe a fájlba: {os.path.basename(REKORD_FAJL)}")
    print()
    legjobb_eredmeny_kiiras()


kviz_inditas()
