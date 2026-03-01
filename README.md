# Konwerter planów zajęć AGH z UniTime do Notion
Program ten został stworzony w celu konwersji plików .csv pobieranych z UniTime AGH ze stosowanego tam formatu 
(definiowanie zakresów powtarzających się zajęć "blokami") do formatu 
umożliwiającego zapis całego planu do bazy danych w Notion 
(może działać również w innych miejscach, niemniej jednak 
taki był pierwotny cel). Program umieszcza każde wystąpienie 
zajęć z konkretnego przedmiotu w osobnym wierszu, co umożliwia 
zapis do bazy danych w Notion. Obecnie program wspiera również konwersję
bezpośrednio z planów zajęć w formacie USOSa, oraz dodawanie pojedynczych zajęć z USOSa do 
konwertowanych plików z UniTime.
# Działanie programu
Główna funkcjonalność programu polega na zmianie sposobu zapisywania zajęć. 
Domyślnie w plikach .csv generowanych przez 
Unitime zajęcia są umieszczane w "blokach" - 
zaznaczana jest data rozpoczęcia bloku, data jego zakończenia
(lub brak jakiejkolwiek daty w wypadku gdy są to pojedyncze zajęcia), 
oraz dzień, w którym zajęcia mają się powtarzać.
Program najprościej rzecz ujmując, na podstawie takiego 
bloku generuje tyle osobnych wierszy, 
ile razy dane zajęcia się powtórzą w danym zakresie czasowym. 
Dzieje się to dla każdego kolejnego bloku tego samego przedmiotu,
a potem dla każdego kolejnego przedmiotu. 
Zajmuje się tym funkcja `process_schedule_ranges()`.  
Finalnie takie działanie pozwala na uzyskanie pliku .csv, w 
którym jeden wiersz odpowiada jednemu konkretnemu wystąpieniu 
zajęć w planie. Ułatwia to importowanie pliku do Notion lub innych aplikacji 
(kalendarzy), które mogą nie 
radzić sobie z formatem stosowanym przez UniTime.
# Instalacja i Uruchomienie
1. Pobierz plik `.exe` z zakładki [Releases](https://github.com/Brozi/timetable-converter/releases).
2. Umieść plik w osobnym folderze
3. Na ostrzeżeniu Defendera kliknij "Więcej informacji", a następnie "Uruchom mimo to"
4. Program sam wygeneruje pliki konfiguracyjne
# Jak korzystać? 
Program posiada kilka przydatnych funkcji, które 
ułatwiają dostosowanie pliku wyjściowego do własnych potrzeb.  
**Są to między innymi:**
* Możliwość konwersji planów z USOSa lub UniTime
* Możliwość usuwania zajęć po ***przedmiocie*** lub ***typie*** (wykład, ćwiczenia)
* Możliwość importu pojedynczych zajęć z USOSa (przydatne w przypadku przedmiotów obieralnych z UBPO)
* Możliwość wyboru trybu działania
* Możliwość wyboru formatu dat i godzin (Osobne kolumny z godzinami i datą, lub cała data rozpoczęcia i zakończenia wraz z godziną)
* Możliwość wyboru w bardzo wygodny i intuicyjny sposób kolumn, które chcemy zachować w pliku wyjściowym (pełna lista w dokładnym opisie tej funkcjonalności)
* Możliwość formatowania skrótów typów zajęć (Wykład -> W, reszta -> CWA, lub oryginalne skróty)
* Możliwość dostosowania nazw zapisywanych kolumn
* Możliwość dostosowania skrótów ID przedmiotów
* Możliwość wyboru sposobu zapisu (aktualnie dostępne formaty: CSV, XLSX)
* Możliwość wyboru nazwy pliku (program automatycznie zapobiega nadpisywaniu plików o tej samej nazwie)

## Wybór funkcjonalności
Po uruchomieniu programu widoczne są trzy możliwe działania
```terminaloutput
=== KONWERTER PLANU ZAJĘĆ AGH ===

==================================================
1. Wczytaj plik
2. Konfiguracja QUICK
3. Wyjście
Wybór:
```
Wybór "1" umożliwia bezpośrednie przejście do funkcji wczytywania pliku CSV.

Wybór "2" powoduje przejście do menu konfiguracji trybu Quick.

Wybór "3" powoduje zakończenie działania programu.

## Tryby działania programu
Program po wyborze opcji "Wczytaj plik" oraz przejściu przez menu filtrowania zajęć 
prezentuje menu wyboru trybu działania
```terminaloutput
--- FILTROWANIE WIERSZY ---
1. Usuń całe PRZEDMIOTY
2. Usuń całe TYPY zajęć
3. Dalej
Wybór: 3

--- TRYB ---
1 -> QUICK (Automat wg ustawień)
2 -> CUSTOM (Pełna kontrola)
3 -> DEBUG (Excel, surowe dane)
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
## Dokładny opis działania trybu Quick
W trybie Quick input użytkownika konieczny jest jedynie przy wyborze nazwy
zapisywanego pliku. Pozostałe etapy konfiguracji przeprowadzane są na podstawie
ustawień zapisanych w pliku settings.json, oraz zdefiniowanych przez użytkownika 
przy użyciu menu konfiguracji trybu Quick.

## Dokładny opis działania trybu Custom
W trybie Custom użytkownik ma kontrolę nad każdym aspektem działania programu.
### Formatowanie dat i godzin
```terminaloutput
--- FORMATOWANIE DAT I GODZIN ---
1 = Standard   (Osobne kolumny: 'Data', 'Od', 'Do')
2 = Integrated (Kolumny scalone: 'Data' (data+start) i 'Do' (data+koniec))
Wybór [1/2]:
```
W tym menu możliwy jest wybór formatowania dat i godzin zajęć. Opcja **standard**
pozwala na zapisywanie daty zajęć, oraz godzin rozpoczęcia i zakończenia w osobnych kolumnach.  
Opcja **integrated** pozwala na zapis dwóch pól - daty rozpoczęcia zajęć razem z godziną, oraz daty 
zakończenia razem z godziną. Format ten znajduje zastosowanie przy wyświetlaniu zajęć w widoku
kalendarza w Notion, gdyż wymagane jest importowanie daty oraz godziny zakończenia
wydarzenia w jednym polu. Domyślnie wybieraną opcją jest opcja **integrated**.

### Wybór kolumn do zapisu
```terminaloutput
--- WYBÓR KOLUMN DO ZACHOWANIA ---
Lp.  Stan    Nazwa kolumny
--------------------------------------------------
 1. [ x ] Kod przedmiotu (kolumna wtórna)
 2. [ x ] Nazwa przedmiotu
 3. [ x ] Typ zajęć
 4. [ x ] Data
 5. [   ] Od (godzina)
 6. [ x ] Data zakończenia (kolumna wtórna)
 7. [   ] Do (godzina)
 8. [ x ] Sala
 9. [   ] Prowadzący
10. [   ] Pojemność sali
11. [   ] Grupa
12. [   ] Uwaga
13. [   ] Dzień tygodnia
14. [   ] Pierwszy dzień
15. [   ] Ostatni dzień
16. [   ] E-mail
--------------------------------------------------
• Wpisz numer, aby przełączyć ([x]/[ ]).
• Szybka selekcja (grupowa):
  - '0 +1,2,3' -> Wyczyść wszystko i dodaj 1, 2, 3.
  - '* -5,9'   -> Zaznacz wszystko i usuń 5, 9.
• ENTER = Zatwierdź.
```
W tym menu możliwa jest decyzja o tym, jakie kolumny powinny znaleźć 
się w pliku wyjściowym. Wybrać można z każdej przydatnej kolumny znajdującej się w pliku
wejściowym. Domyślnie wybrane kolumny to
* Kod przedmiotu
* Nazwa przedmiotu
* Typ zajęć 
* Data 
* Data zakończenia 
* Sala  

**Wymagany jest wybór co najmniej jednej kolumny**. Istnieją dwa sposoby wyboru kolumn, które mają zostać zapisane  
1. Wpisanie numeru kolumny, aby przełączyć jej stan, np.
```terminaloutput
>> 1

--- WYBÓR KOLUMN DO ZACHOWANIA ---
Lp.  Stan    Nazwa kolumny
--------------------------------------------------
 1. [   ] Kod przedmiotu (kolumna wtórna)
 2. [ x ] Nazwa przedmiotu
 3. [ x ] Typ zajęć
 4. [ x ] Data
 5. [   ] Od (godzina)
 6. [ x ] Data zakończenia (kolumna wtórna)
 7. [   ] Do (godzina)
 8. [ x ] Sala
 9. [   ] Prowadzący
10. [   ] Pojemność sali
11. [   ] Grupa
12. [   ] Uwaga
13. [   ] Dzień tygodnia
14. [   ] Pierwszy dzień
15. [   ] Ostatni dzień
16. [   ] E-mail
--------------------------------------------------
• Wpisz numer, aby przełączyć ([x]/[ ]).
• Szybka selekcja (grupowa):
  - '0 +1,2,3' -> Wyczyść wszystko i dodaj 1, 2, 3.
  - '* -5,9'   -> Zaznacz wszystko i usuń 5, 9.
• ENTER = Zatwierdź.
>>
```
2. Użycie szybkiej selekcji. Składnia tej opcji polega na symbolach 
operacji:
* `0` - Odznaczenie wszystkich kolumn z wyjątkiem pożądanych, wpisywanych od `+` i rozdzielonych `,`, np. `0 +1,2,3`  
* `*` - Zaznaczenie wszystkich kolumn z wyjątkiem niepożądanych, wpisywanych od `-` i rozdzielanych `,`, np. `* -5,9`
### Formatowanie typów zajęć
```
1 = Simple   (Wykład -> 'W', reszta -> 'CWA')
2 = Detailed (Zachowuje oryginalne skróty: CWP, CWL, KON)
Wybór [1/2]:
```
W tym menu możliwy jest wybór sposobu formatowania skrótów zajęć. Opcja **Simple** 
traktuje każde zajęcia niebędące wykładem jako ćwiczenia (CWA). Opcja **Detailed** pozwala na 
utworzenie skrótów na podstawie oryginalnych typów zajęć, tak, aby możliwe było rozróżnienie
między np. Ćwiczeniami Audytoryjnymi a Laboratoryjnymi. Domyślnie wybrana jest opcja **Simple**.
### Mapowanie nazw kolumn
```
--- MAPOWANIE NAZW ---
  * Kod przedmiotu (ID)                 -> Kod przedmiotu
  * Nazwa przedmiotu                    -> Nazwa przedmiotu
  * Typ zajęć                           -> Typ
  * Data                                -> Data
  * Data zakończenia                    -> Data zakończenia
  * Sala                                -> Sala

Zmienić nazwy docelowe? [t/n]: t

Wpisz nową nazwę lub ENTER by zostawić.
'Kod przedmiotu (ID)' -> [Kod przedmiotu]:
'Nazwa przedmiotu' -> [Nazwa przedmiotu]:
'Typ zajęć' -> [Typ]:
'Data' -> [Data]:
'Data zakończenia' -> [Data zakończenia]:
'Sala' -> [Sala]:
```
To menu umożliwia zmianę finalnej nazwy każdej z kolumn wybranych do zachowania.
Edytor działa na zasadzie przechodzenia linia po linii, za każdym razem pytając użytkownika
o nową nazwę danej kolumny. W wypadku pominięcia linii poprzez klawisz `Enter`
następuje zachowanie nazwy bez zmian.

### Konfiguracja ID przedmiotów
To menu odpowiada za możliwość edycji perfixów ID przypisywanych każdym zajęciom konkretneg przedmiotu. 

**Identyfikatory składają się z trzech części:**
* Prefixu
* Typu zajęć (`W`, lub `C`)
* Numeru spotkania (1 dla pierwszych zajęć w semestrze, 2 dla drugich itp. Numerowanie jest osobne dla wykładów i ćwiczeń)
* Każdy element indentyfikatora jest oddzielony `-`

**Domyślnie prefixy identyfikatorów powstają zgodnie z następującymi zasadami:**
* Jeśli nazwa przedmiotu składa się z pojedynczego słowa, prefixem będą cztery pierwsze litery tego słowa
* Jeśli nazwa składa się z kilku słów, prefixem będzie ciąg złożony z pierwszej litery każdego słowa.

Identyfikatory są konfigurowalne w sposób analogiczny do mapowania nazw kolumn

### Konfiguracja sposobu zapisu pliku wyjściowego
Aktualnie możliwe są trzy sposoby zapisu

1. CSV - Zapis do pliku CSV. Przydatny przy importach do wszelkieg rodzaju kalendarzy czy terminarzy, w tym Notion.
2. XLSX - Zapis do pliku XLSX (Excel). Przydatny w celu sprawdzenia poprawności zapisu przedmiotów (bardziej czytelny dla ludzi niż CSV)
3. Both - Zapisuje plik do obu formatów
