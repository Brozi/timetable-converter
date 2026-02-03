# Konwerter planów zajęć AGH z UniTime do Notion
Program ten został stworzony w celu konwersji plików .csv pobieranych z UniTime AGH ze stosowanego tam formatu 
(definiowanie zakresów powtarzających się zajęć "blokami") do formatu 
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
2. Umieść plik w osobnym folderze
3. Na ostrzeżeniu Defendera kliknij "Więcej informacji", a następnie "Uruchom mimo to"
4. Program sam wygeneruje pliki konfiguracyjne
## Jak korzystać? 
Program posiada kilka przydatnych funkcji, które 
ułatwiają dostosowanie pliku wyjściowego do własnych potrzeb. 
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

Wybór "2" powoduje przejście do menu konfiguracji trybu Quick.

Wybór "3" powoduje zakończenie działania programu.

### Tryby działania programu
Program po wyborze opcji "Wczytaj plik" oraz przejściu przez menu filtrowania zajęć 
prezentuje menu wyboru trybu działania
```terminaloutput
--- FILTROWANIE WIERSZY ---
1. Usuń całe PRZEDMIOTY
2. Usuń całe TYPY zajęć
3. Dalej
Wybór: 3

--- TRYB ---
1 -> 🚀 QUICK (Automat wg ustawień)
2 -> 🛠️ CUSTOM (Pełna kontrola)
3 -> 🐛 DEBUG (Excel, surowe dane)
Wybór: 
```
**Tryb Quick** oznacza szybką konwersję, bazowaną na domyślnych ustawieniach, 
lub tych zdefiniowanych przez użytkownika w menu konfiguracji trybu.  

**Tryb Custom** oznacza możliwość manualnego dopasowania niemal każdego
aspektu konwersji. Zostanie on szerzej omówiony w dalszej części dokumentacji

**Tryb Debug**  
W trybie debug jedyne przeprowadzane operacje to "rozwijanie" grup
przedmiotów na pojedyncze wiersze oraz dodanie kolumny z datą zajęć.
Program nie tworzy nowych kolumn. Zachowywane są również typy zajęć, 
jednakże następuje skrócenie ich formy. Prawdopodobnie nie wszystkie typy zajęć
zostały przewidziane, więc dla tych typów program skraca ich nazwy do trzech pierwszych 
liter.  
Tryb debug nie powinien mieć zastosowania dla zwykłych użytkowników, jednakże 
został w kodzie, aby umożliwić ewentualne rozwiązywanie różnego rodzaju problemów 
z działaniem programu (aby łatwiej było ustalić, na którym etapie występuje problem)
### Opis działania trybu Custom


