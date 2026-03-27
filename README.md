# Konwerter planów zajęć AGH (USOS / Unitime)

## Opis projektu
Narzędzie CLI (Command Line Interface) napisane w języku Python, służące do automatycznej transformacji i czyszczenia surowych eksportów danych rozkładów zajęć z systemów uczelnianych. 
Program przekształca nieustrukturyzowane pliki w czytelne formaty CSV i XLSX, ułatwiając dalsze zarządzanie kalendarzem.

## Główne funkcjonalności
* **Przetwarzanie danych:** Import i parsowanie danych z systemów USOS oraz Unitime. Rozwijanie zakresów dat do pojedynczych dni.
* **Transformacja:** Zaawansowane filtrowanie, czyszczenie ciągów znaków (usuwanie duplikatów, znaków specjalnych) oraz logiczne sortowanie kolumn.
* **System konfiguracji:** Zapis i odczyt ustawień użytkownika w pliku JSON, umożliwiający trwałe mapowanie nazw kolumn oraz definiowanie własnych skrótów (prefixów) dla przedmiotów.
* **Tryb interaktywny:** Możliwość ręcznego wykluczania konkretnych przedmiotów lub typów zajęć z poziomu konsoli oraz interaktywny interfejs wyboru kolumn docelowych.
* **Bezpieczeństwo plików:** Automatyczne zapobieganie nadpisywaniu istniejących plików wynikowych.

## Technologie i biblioteki
* **Python 3.x**
* **pandas** - do zaawansowanych operacji na ramkach danych.
* **json, os, re, csv** - wbudowane biblioteki do zarządzania konfiguracją, plikami i wyrażeniami regularnymi.

## Jak uruchomić
### Gotowy plik .exe
1.Pobierz plik .exe z zakładki Releases.
2. Umieść plik w osobnym folderze
3. Na ostrzeżeniu Defendera kliknij "Więcej informacji", a następnie "Uruchom mimo to"
4. Program sam wygeneruje pliki konfiguracyjne
### Skrypt python
1. Upewnij się, że masz zainstalowanego Pythona oraz bibliotekę pandas (`pip install pandas`).
2. Uruchom skrypt w terminalu: `python main.py`.
3. Postępuj zgodnie z instrukcjami w oknie konsoli: wskaż plik źródłowy, dostosuj ustawienia i wybierz format zapisu.
