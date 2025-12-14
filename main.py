# Import potřebných knihoven a modulů
import requests
from bs4 import BeautifulSoup
import csv
import argparse

def ziskani_HTML(url):  # Funkce pro získání HTML kódu webové stránky
    """Funkce pro získání obsahu webové stránky."""
    try:
        HTML_kod = requests.get(url, timeout=10)
    except requests.RequestException as e:
        print(f"Chyba při načítání stránky: {e}")
        return None
    if HTML_kod.status_code == 200:
        HTML_kod.encoding = "utf-8"
        web = BeautifulSoup(HTML_kod.text, "html.parser")
        return web
    else:
        print(f"Chyba při načítání stránky (HTTP {HTML_kod.status_code})")
        return None

def odkazy_vsech_okresu(web) -> list:   # Funkce pro získání odkazů na všechny okresy
    """Najde všechny odkazy na okresy (ps32?... nebo ps36?...)."""
    odkazy = []
    for a_tag in web.find_all("a", href=True):
        href = a_tag["href"]
        if href.startswith("ps32?") or href.startswith("ps36?"):  # všechny odkazy na okresy
            plny_odkaz = BASE_URL + href
            odkazy.append(plny_odkaz)
    return odkazy

def ziskani_nazvu_okresu(web) -> list:  # Funkce pro získání názvu vsech okresů
    """Funkce pro získání názvů všech okresů."""
    prvky_td_none = web.find_all("td", class_=None)  # Najde všechny <td> bez třídy
    vsechny_td = []     # List pro uložení textů všech <td>
    nazvy_okresu = []   # List pro uložení názvů okresů   
    for td in prvky_td_none:
        text = td.get_text(strip=True)
        vsechny_td.append(text)
    for polozka in vsechny_td:    
        if "CZ0" not in polozka:    # Pokud položka neobsahuje "CZ0", jedná se o název okresu
            nazvy_okresu.append(polozka)
    return nazvy_okresu

def vytvoreni_databaze_okresu(web) -> dict:  # Funkce pro vytvoření databáze okresů a jejich odkazů
    """Vrátí slovník s názvy okresů jako klíče a jejich odkazy jako hodnoty."""
    nazvy_okresu = ziskani_nazvu_okresu(web)    # List názvů okresů
    odkazy_na_okresy = odkazy_vsech_okresu(web) # List odkazů na okresy
    databaze_okresu = dict(zip(nazvy_okresu, odkazy_na_okresy)) # Vytvoření slovníku - databáze okresů
    return databaze_okresu

def ziskani_nazvu_obci(web) -> list:    # Funkce pro získání názvu obcí
    """Funkce pro získání názvů obcí z HTML kódu."""
    obce = web.find_all("td", class_="overflow_name")
    nazvy_obci = []   # Pro každý záznam vytáhni název obce (v textu odkazu)
    for td in obce:
        nazev = td.get_text(strip=True)
        nazvy_obci.append(nazev)    
    return nazvy_obci

def ziskani_cisla_okrsku(web) -> list:  # Funkce pro získání čísla okrsku
    """Funkce pro získání čísel okrsků z HTML kódu."""
    okrsky = web.find_all("td", class_="cislo")
    cisla_okrsku = []   # Pro každý záznam vytáhni číslo okrsku (v textu odkazu)
    for td in okrsky:
        cislo = td.get_text(strip=True)
        cisla_okrsku.append(cislo)
    return cisla_okrsku

def ziskani_poctu_volicu(web) -> int:   # Funkce pro získání počtu voličů v obci
    """Funkce pro získání počtu voličů v obci."""
    for td in web.find_all("td", class_="cislo", headers="sa2"):
        pocet_volicu = td.get_text(strip=True).replace("\xa0", "")
        return int(pocet_volicu)
    
def ziskani_poctu_vydanych_obalek(web) -> int:  # Funkce pro získání počtu vydaných obálek v obci
    """Funkce pro získání počtu vydaných obálek v obci."""
    for td in web.find_all("td", class_="cislo", headers="sa3"):
        vydane_obalky = td.get_text(strip=True).replace("\xa0", "")
        return int(vydane_obalky)

def ziskani_poctu_platnych_hlasu(web) -> int:   # Funkce pro získání počtu platných hlasů v obci
    """Funkce pro získání počtu platných hlasů v obci."""
    for td in web.find_all("td", class_="cislo", headers="sa6"):
        platne_hlasy = td.get_text(strip=True).replace("\xa0", "")
        return int(platne_hlasy)

def ziskani_poctu_hlasu_stran(web) -> list:  # Funkce pro získání počtu platných hlasů v obci
    """Funkce pro získání počtu hlasů pro jednotlivé strany v obci."""
    seznam_headers = ["t1sa2 t1sb3", "t2sa2 t2sb3"]   # Hlavičky pro obě tabulky s počty hlasů stran
    return [
        int(td.get_text(strip=True).replace("\xa0", ""))
        for header in seznam_headers
        for td in web.find_all("td", class_="cislo", headers=header)
    ]

def kandidujici_strany(web) -> list:    # Funkce pro získání kandidujících stran
    """Funkce pro získání všech kandidujících stran v daném kraji."""
    nazvy_stran = web.find_all("td", class_="overflow_name")
    seznam_stran = []   # Pro každý záznam vytáhni název strany (v textu odkazu)
    for td in nazvy_stran:
        nazev_strany = td.get_text(strip=True)
        seznam_stran.append(nazev_strany)
    return seznam_stran

def odkazy_vsech_obci(web) -> list:  # Funkce pro získání odkazů na všechny obce v okrese
    """Najde všechny odkazy na obce v daném okrese."""
    seznam_headers = ["t1sa1 t1sb1", "t2sa1 t2sb1", "t3sa1 t3sb1"]  # Hlavičky pro všechny tři tabulky s obcemi
    return [
        BASE_URL + a["href"]
        for header in seznam_headers
        for td in web.find_all("td", headers=header)
        for a in td.find_all("a", href=True)
    ]

##### HLAVNÍ PROGRAM #####
# Konstanty - URL adresy
BASE_URL = "https://www.volby.cz/pls/ps2017nss/"
ZDROJOVY_URL = BASE_URL + "ps3?xjazyk=CZ"

def main():
    """Hlavní funkce programu."""
    web_hlavni_stranky = ziskani_HTML(ZDROJOVY_URL)  # Získání HTML kódu hlavní stránky
    databaze_okresu = vytvoreni_databaze_okresu(web_hlavni_stranky) # Vytvoření databáze okresů

    #1) Požadované vstupy od uživatele
    parser = argparse.ArgumentParser(description="Stáhne výsledky voleb pro vybraný okres.")
    parser.add_argument(
        "-o", "--okres",
        required=True,
        help="Název okresu (přesně podle názvů v databázi)"
    )

    parser.add_argument(
        "-f", "--outfile",
        required=True,
        help="Název výstupního CSV souboru, např. vysledky.csv"
    )

    args = parser.parse_args()
    
    if args.okres not in databaze_okresu:   # Kontrola správnosti zadaného okresu
        print("Chybný název okresu")
        return
     
    zvoleny_okres = databaze_okresu[args.okres] # URL zvoleného okresu

    #2) Provedení požadované analýzy dat z daného okresu
    print(f"Stahuji a analyzuji data pro okres: {args.okres}...")
    analyzovany_okres = ziskani_HTML(zvoleny_okres) # Zvolený okres uživatelem
    cislo = ziskani_cisla_okrsku(analyzovany_okres) # Získání čísel okrsků v daném okrese
    nazev_obce = ziskani_nazvu_obci(analyzovany_okres)  # Získání názvů obcí v daném okrese
    opravneni_volici = []   # Získání oprávněných voličů ve všech obcích daného okresu
    vydane_obalky = []      # Získání počtů vydaných obálek ve všech obcích daného okresu
    platne_hlasy = []       # Získání počtů platných hlasů ve všech obcích daného okresu
    pocty_hlasu_stran = []  # Získání počtů hlasů pro jednotlivé strany ve všech obcích daného okresu
    odkazy_obci = odkazy_vsech_obci(analyzovany_okres)  # Získání odkazů na všechny obce v daném okrese

    for odkaz_obce in odkazy_obci:
        web_obce = ziskani_HTML(odkaz_obce)   # Analyzovaný web obce
        pocet_volicu = ziskani_poctu_volicu(web_obce)
        opravneni_volici.append(pocet_volicu)   # Oprávnění voliči
        pocet_vydanych_obalek = ziskani_poctu_vydanych_obalek(web_obce)
        vydane_obalky.append(pocet_vydanych_obalek)  # Vydané obálky
        pocet_platnych_hlasu = ziskani_poctu_platnych_hlasu(web_obce)
        platne_hlasy.append(pocet_platnych_hlasu)   # Platné hlasy
        pocet_hlasu_stranam = ziskani_poctu_hlasu_stran(web_obce)
        pocty_hlasu_stran.append(pocet_hlasu_stranam)   # Počty hlasů pro jednotlivé strany

    # Získání seznamu názvů kandidujících stran v daném okrese
    odkaz_prvni_obce = odkazy_obci[0]   # Odkaz pro získání názvů kandidujících stran
    web_prvni_obce = ziskani_HTML(odkaz_prvni_obce)
    seznam_stran = kandidujici_strany(web_prvni_obce) # Seznam stran

    #3) Vytvoření slovníku / databáze s požadovanými daty
    slovnik_prvni_cast = {
        "Číslo": cislo,
        "Název obce": nazev_obce,
        "Oprávnění voliči": opravneni_volici,
        "Vydané obálky": vydane_obalky,
        "Platné hlasy": platne_hlasy
    }
    slovnik_druha_cast = {
        seznam_stran[i]: [pocty_hlasu_stran[j][i] for j in range(len(pocty_hlasu_stran))]
        for i in range(len(seznam_stran))
    }
    databaze_dat = {**slovnik_prvni_cast, **slovnik_druha_cast} # Spojení obou částí do jednoho slovníku

    # 4) Uložení dat do CSV souboru
    print(f"Ukládám data do CSV souboru: {args.outfile}...")
    nazev_souboru = args.outfile + ".csv"
    with open(nazev_souboru, mode="w", newline="", encoding="utf-8") as csv_soubor:
        writer = csv.writer(csv_soubor)
        writer.writerow(databaze_dat.keys())    # Zápis hlavičky
        for i in range(len(nazev_obce)):    # Zápis datových řádků
            radek = [databaze_dat[key][i] for key in databaze_dat.keys()]
            writer.writerow(radek)

if __name__ == "__main__":  # Tento blok zajistí, že main() poběží jen při přímém spuštění skriptu
    main()