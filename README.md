# Konwerter planów zajęć AGH z UniTime do Notion
Program ten został stworzony w celu konwersji plików .csv pobieranych z UniTime AGH ze stosowanego tam formatu 
(definiowanie czasu trwania zajęć "zakresami") do formatu 
umożliwiającego zapis całego planu do bazy danych w Notion 
(może działać również w innych miejscach, niemniej jednak 
taki był pierwotny cel). Program umieszcza każde wystąpienie 
zajęć z konkretnego przedmiotu w osobnym wierszu, co umożliwia 
zapis do bazy danych w Notion.  
## Działanie programu
Główna funkcjonalność programu polega na zmianie sposobu zapisywania zajęć. 
Domyślnie w plikach .csv generowanych przez 
Unitime zajęcia są umieszczane w "blokach" - 
zaznaczana jest data rozpoczęcia bloku, data jego zakończenia
(lub brak jakiejkolwiek daty w wypadku gdy są to pojedyncze zajęcia), 
oraz dzień, w którym zajęcia mają się powtarzać.
Program najprościej rzecz ujmując, na podstawie takiego 
bloku generuje tyle osobnych wierszy, 
ile razy dane zajęcia się powtórzą w danym zakresie czasowym. 
I tak dla każdego kolejnego bloku tego samego przedmiotu,
a potem dla każdego kolejnego przedmiotu. 
Dzieje się to w funkcji `process_schedule_ranges()`.  
Finalnie takie działanie pozwala na uzyskanie pliku .csv, w 
którym jeden wiersz odpowiada jednemu konkretnemu wystąpieniu 
zajęć w planie. Ułatwia to importowanie pliku do Notion lub innych aplikacji 
(kalendarzy), które mogą nie 
radzić sobie z formatem stosowanym przez UniTime.
## Instalacja i Uruchomienie
1. Pobierz plik `.exe` z zakładki [Releases](https://github.com/Brozi/timetable-converter/releases).
2. Umieść go w jakimś folderze, bo 
program generuje pliki konfiguracyjne podczas pracy
3. Uruchom plik. Program sam utworzy potrzebne pliki konfiguracyjne.
## Jak korzystać? 
Program posiada kilka przydatnych funkcji, które 
ułatwiają dostosowanie outputu do własnych potrzeb. 
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