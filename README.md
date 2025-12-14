ENGETO-PROJEKT-3-ELECTIONS-SCRAPER
Python Akademie - třetí projekt

Popis projektu

Tento projekt slouží k extrahování výsledků parlamentních voleb v roce 2017. Odkaz prohlédnutí ZDE:
https://www.volby.cz/pls/ps2017nss/ps3?xjazyk=CZ


Instalace knihoven

Knihovny, které jsou použity v kódu jsou ulozžené v souboru requirements.txt. Pro instalaci je doporučeno použít nové virtuální prostředí a s nainstalovaným manažerem spustit následovně:

$ pip3 --version                        # ověření verze manažeru
$ pip3 install -r requirements.txt      # instalace knihoven


Spuštění projektu

Spuštění souboru main.py v rámci příkazového řádku vyžaduje dva povinné argumenty:

python main.py -o <nazev_okresu> -f <nazev_vysledneho_souboru>

nebo:

python main.py --okres <nazev_okresu> --outfile <nazev_vysledneho_souboru>

Následně se výsledky stáhnou a uloží do CSV souboru. Příponu ".csv" není nutné do názvu souboru zadávat, program ji automaticky přidělí sám.


Stručný popis funkce programu

Program nejdříve vytvoří jednoduchou databázi všech okresů s jejich odkazy. Na základě zadání 1. argumentu vyhodnotí, zda se zadaný název okresu nachází v databázi a poté dále pracuje s odkazem na příslušný okres a provede požadovanou analýzu. Je-li název okresu zadán chybně, program vypíše upozornění a ukončí se.
Ve 2. argumentu se definuje název CSV souboru. Příponu ".csv" program přidělí automaticky.


Ukázka projektu

Výsledky hlasování pro okres Zlín:

1. argument: "Zlín"
2. argument: vysledky_zlin


Spuštění programu:

python main.py -o "Zlín" -f vysledky_zlin

nebo:

python main.py --okres "Zlín" --outfile vysledky_zlin


Průbeh stahování:

Stahuji a analyzuji data pro okres: Zlín...
Ukládám data do CSV souboru: vysledky_zlin...

Částečný výstup:
Číslo, Název obce, Oprávnění voliči, Vydané obálky, Platné hlasy...
588318, Bělov, 257, 174, 174, 25, 0, 0, 8, 0, 14, 20, 1, 0, 2, 0, 0, 14, 0, 6, 51, 0, 0, 9, 4, 0, 0,20, 0
585076, Biskupice, 564, 314, 314, 17, 1, 0, 16, 0, 15, 34, 2, 6, 15, 0, 0, 16, 0, 1, 102, 0, 1, 38, 2, 0, 2, 42, 4
...

