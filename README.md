# Konwerter planów zajęć AGH z UniTime do Notion
Program ten został stworzony w celu konwersji plików .csv pobieranych z UniTime AGH ze stosowanego tam formatu (definiowanie czasu trwania zajęć "zakresami") do formatu umożliwiającego zapis całego planu do bazy danych w Notion (może działać również w innych miejscach, niemniej jednak taki był pierwotny cel). Program umieszcza każde jedno wystąpienie zajęć z konkretnego przedmiotu w osobnym wierszu, co umożliwia zapis do bazy danych w Notion. 

## Instalacja i Uruchomienie
1. Pobierz plik `.exe` z zakładki [Releases](https://github.com/Brozi/timetable-converter/releases).
2. Umieść go w jakimś folderze, bo program generuje pliki konfiguracyjne podczas pracy
3. Uruchom plik. Program sam utworzy potrzebne pliki konfiguracyjne.
## Jak korzystać? 
Program posiada kilka przydatnych funkcji, które ułatwiają dostosowanie outputu do własnych potrzeb. 
### Wybór funkcjonalności
Po uruchomieniu programu widoczne są trzy możliwe działania
```terminal
=== KONWERTER PLANU ZAJĘĆ AGH ===

==================================================
1. Wczytaj plik
2. ⚙️ Konfiguracja QUICK
3. Wyjście
Wybór:
```
Wybór "1" umożliwia bezpośrednie przejście do funkcji wczytywania pliku CSV.

Wybór "2" powoduje przejście do menu konfiguracji jednego z trybów działania programu

Wybór "3" powoduje zakończenie działania programu. 
