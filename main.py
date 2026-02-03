import pandas as pd
import datetime
import re
import os
import csv
import json
from io import StringIO
#Program działa super
#Jedyne co do naprawy to
#1. Zrobić tak żeby mozna było wybrać dowolne kolumny (co najmniej1)
#2. Podmienić nazwy kolumn podczas wyboru które zachować żeby dało się zrozumieć o co chodzi
# --- PLIK KONFIGURACYJNY ---
CONFIG_FILE = 'settings.json'

# --- DOMYŚLNE MAPOWANIE (Klucze to kolumny WYMAGANE w pliku źródłowym) ---
DEFAULT_MAPA_KOLUMN = {
    'Data': 'Data',
    'Tytuł': 'Przedmiot',
    'Ogłoszony początek': 'Od',
    'Ogłoszony koniec': 'Do',
    'Miejsce': 'Sala',
    'Typ': 'Typ',
    'Data_End_Integrated': 'Data końca zajęć'
}

# --- DOMYŚLNA KONFIGURACJA ---
DEFAULT_CONFIG = {
    'quick_settings': {
        'type_mode': 'simple',  # 'simple' / 'detailed'
        'date_mode': 'integrated',  # 'integrated' / 'standard'
        'save_format': 'both',  # 'csv' / 'xlsx' / 'both'
        'extra_columns': []  # Lista nazw dodatkowych kolumn do zachowania
    },
    'column_mapping': DEFAULT_MAPA_KOLUMN.copy(),
    'prefixes': {}
}

# --- ZMIENNA GLOBALNA NA KONFIGURACJĘ ---
CURRENT_CONFIG = DEFAULT_CONFIG.copy()


# --- FUNKCJE KONFIGURACJI ---

def load_config():
    global CURRENT_CONFIG
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                loaded = json.load(f)
                merged = DEFAULT_CONFIG.copy()
                merged.update(loaded)
                if 'prefixes' in loaded: merged['prefixes'] = loaded['prefixes']
                if 'column_mapping' in loaded: merged['column_mapping'] = loaded['column_mapping']
                if 'quick_settings' in loaded:
                    qs = DEFAULT_CONFIG['quick_settings'].copy()
                    qs.update(loaded['quick_settings'])
                    merged['quick_settings'] = qs
                CURRENT_CONFIG = merged
                print(f"✅ Załadowano ustawienia z {CONFIG_FILE}")
        except Exception as e:
            print(f"⚠️ Błąd odczytu ustawień: {e}. Używam domyślnych.")
            CURRENT_CONFIG = DEFAULT_CONFIG.copy()
    else:
        save_config()


def save_config():
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(CURRENT_CONFIG, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"❌ Błąd zapisu ustawień: {e}")


# --- FUNKCJE POMOCNICZE ---

def load_data(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except UnicodeDecodeError:
        with open(path, 'r', encoding='windows-1250') as f:
            lines = f.readlines()

    if not lines:
        raise ValueError("Plik jest pusty!")

    first_line = lines[0].strip()
    if first_line.startswith('"') and ',""' in first_line:
        cleaned_lines = []
        for line in lines:
            line = line.strip()
            if line.startswith('"'): line = line[1:]
            if line.endswith('"'): line = line[:-1]
            line = line.replace('""', '"')
            cleaned_lines.append(line)
        return pd.read_csv(StringIO('\n'.join(cleaned_lines)), sep=',')

    return pd.read_csv(path, sep=',')


def parse_days_of_week(day_str, day_map):
    if pd.isna(day_str): return []
    tokens = re.findall(r'[A-ZŚĆŹŻŁŃ][a-zśźćżłń]*', day_str)
    return [day_map[t] for t in tokens if t in day_map]


def get_unique_filename(base_filename):
    if not os.path.exists(base_filename): return base_filename
    name, ext = os.path.splitext(base_filename)
    counter = 1
    while True:
        new_filename = f"{name}_{counter}{ext}"
        if not os.path.exists(new_filename): return new_filename
        counter += 1


def get_prefix_default(name):
    if not isinstance(name, str): return ""
    words = name.split()
    if len(words) == 1:
        return words[0][:4].upper()
    else:
        return "".join([w[0] for w in words]).upper()


def clean_text_for_notion(text):
    if pd.isna(text): return ""
    text = str(text)
    text = re.split(r'[\(\[]', text)[0]
    text = text.replace(',', '')
    text = text.split('.')[0]
    return re.sub(r'\s+', ' ', text).strip()


def filter_data_interactive(df):
    while True:
        print("\n--- FILTROWANIE WIERSZY ---")
        print("1. Usuń całe PRZEDMIOTY")
        print("2. Usuń całe TYPY zajęć")
        print("3. Dalej")
        choice = input("Wybór: ").strip()
        if choice == '3': break

        if choice == '1':
            items = sorted(df['Tytuł'].unique().tolist())
            print(f"\nZnalezione przedmioty:")
            for i, item in enumerate(items): print(f"[{i + 1}] {item}")
            to_rem = input("\nNumery do usunięcia (po przecinku): ").strip()
            if to_rem:
                try:
                    idxs = [int(x) - 1 for x in to_rem.split(',') if x.strip().isdigit()]
                    sel = [items[i] for i in idxs if 0 <= i < len(items)]
                    if sel: df = df[~df['Tytuł'].isin(sel)]
                except:
                    pass
        elif choice == '2':
            items = sorted(df['Typ'].unique().tolist())
            print(f"\nZnalezione typy:")
            for i, item in enumerate(items): print(f"[{i + 1}] {item}")
            to_rem = input("\nNumery do usunięcia (po przecinku): ").strip()
            if to_rem:
                try:
                    idxs = [int(x) - 1 for x in to_rem.split(',') if x.strip().isdigit()]
                    sel = [items[i] for i in idxs if 0 <= i < len(items)]
                    if sel: df = df[~df['Typ'].isin(sel)]
                except:
                    pass
        if df.empty: return df
    return df


# --- POPRAWIONE MAPOWANIE (Synchronizacja z extra_columns i date_mode) ---

def customize_column_mapping(current_full_map, extra_columns=None, date_mode='standard'):
    """
    Wyświetla mapowanie dla kolumn systemowych oraz kolumn wybranych jako extra.
    Ukrywa/Pokazuje kolumny specyficzne dla trybu daty.
    """
    print("\n--- MAPOWANIE NAZW ---")

    if extra_columns is None:
        extra_columns = []

    # Zmiana 1: Dynamiczna lista kluczy w zależności od trybu daty
    req_keys = ['Data', 'Tytuł', 'Miejsce', 'Typ']

    if date_mode == 'standard':
        req_keys.extend(['Ogłoszony początek', 'Ogłoszony koniec'])
    else:
        # W trybie integrated dodajemy naszą wirtualną kolumnę
        req_keys.append('Data_End_Integrated')

    display_map = {}

    for k in req_keys:
        # Pobieramy nazwę z mapy, a jak nie ma to z domyślnej
        display_map[k] = current_full_map.get(k, DEFAULT_MAPA_KOLUMN.get(k, k))

    for k in extra_columns:
        if k not in req_keys:
            display_map[k] = current_full_map.get(k, k)

    # Wyświetlanie
    for k in req_keys:
        label = k
        if k == 'Data_End_Integrated':
            label = "Data (Koniec - Integrated)"
        print(f"  * {label:30} -> {display_map[k]}")

    other_keys = sorted([k for k in display_map.keys() if k not in req_keys])
    if other_keys:
        print("  --- Dodatkowe ---")
        for k in other_keys:
            print(f"  * {k:30} -> {display_map[k]}")

    if input("\nZmienić nazwy docelowe? (t/n): ").strip().lower() != 't':
        return display_map

    print("\nWpisz nową nazwę lub ENTER by zostawić.")
    for src in req_keys + other_keys:
        label = src
        if src == 'Data_End_Integrated':
            label = "Data (Koniec - Integrated)"

        val = input(f"'{label}' -> [{display_map[src]}]: ").strip()
        if val:
            display_map[src] = val

    global CURRENT_CONFIG
    CURRENT_CONFIG['column_mapping'].update(display_map)
    save_config()
    return display_map


def customize_prefixes(df, col_title_name):
    print("\n--- KONFIGURACJA SKRÓTÓW ID (PREFIX) ---")
    courses = df[col_title_name].unique()

    # Zmiana 3: Ładowanie istniejących prefixów z konfiga
    prefix_map = CURRENT_CONFIG.get('prefixes', {}).copy()

    for c in courses:
        clean_name = clean_text_for_notion(c)
        default_val = get_prefix_default(clean_name)
        current_val = prefix_map.get(clean_name, default_val)
        print(f"  * {clean_name:30} [{current_val}]")

    if input("\nEdytować skróty? (t/n): ").strip().lower() != 't':
        # Jeśli nie edytujemy, zwracamy to co mamy (uzupełnione o domyślne dla nowych przedmiotów)
        final_map = prefix_map.copy()
        for c in courses:
            clean_name = clean_text_for_notion(c)
            if clean_name not in final_map:
                final_map[clean_name] = get_prefix_default(clean_name)
        return final_map

    print("Wpisz skrót lub ENTER dla domyślnego.")
    for c in courses:
        clean_name = clean_text_for_notion(c)
        default_val = prefix_map.get(clean_name, get_prefix_default(clean_name))

        user_p = input(f"Skrót dla '{clean_name}' [{default_val}]: ").strip().upper()
        prefix_map[clean_name] = user_p if user_p else default_val

    # Zmiana 3: Zapis do konfiga
    CURRENT_CONFIG['prefixes'] = prefix_map
    save_config()
    return prefix_map


def select_columns_ui(all_columns, preselected_extras, required_columns):
    selected_extras = set(preselected_extras)
    selected_extras = {c for c in selected_extras if c in all_columns}

    while True:
        print("\n--- WYBÓR KOLUMN DO ZACHOWANIA ---")
        print("Lp.  Stan   Nazwa kolumny")
        print("-" * 40)

        for i, col in enumerate(all_columns):
            if col in required_columns:
                status = "[REQ]"
                desc = "(Wymagana systemowo)"
            else:
                status = "[ x ]" if col in selected_extras else "[   ]"
                desc = ""
            print(f"{i + 1:2}. {status} {col} {desc}")

        print("-" * 40)
        print("Wpisz numer kolumny, aby przełączyć [x]/[ ].")
        print("Wpisz 'ok' lub wciśnij ENTER, aby zatwierdzić.")
        choice = input(">> ").strip().lower()

        if choice in ['ok', '']: break

        try:
            nums = [int(x) - 1 for x in choice.replace(',', ' ').split() if x.strip().isdigit()]
            for idx in nums:
                if 0 <= idx < len(all_columns):
                    col_name = all_columns[idx]
                    if col_name not in required_columns:
                        if col_name in selected_extras:
                            selected_extras.remove(col_name)
                        else:
                            selected_extras.add(col_name)
                    else:
                        print(f"⚠️ Kolumna '{col_name}' jest wymagana.")
        except:
            pass

    return list(selected_extras)


# --- KONFIGURACJA QUICK SETTINGS ---

def configure_quick_settings():
    global CURRENT_CONFIG
    qc = CURRENT_CONFIG['quick_settings']

    print("\n--- ⚙️ KONFIGURACJA TRYBU QUICK ---")

    # 1. Typy
    print(f"\n1. TYPY ZAJĘĆ [Obecnie: {qc['type_mode']}]")
    print("   1 = Simple   (Wykład -> 'W', reszta -> 'CWA')")
    print("   2 = Detailed (Zachowuje oryginalne skróty: CWP, CWL, KON)")
    sel = input("   Wybór (1/2, ENTER=Bez zmian): ").strip()
    if sel == '1': qc['type_mode'] = 'simple'
    if sel == '2': qc['type_mode'] = 'detailed'

    # 2. Daty
    print(f"\n2. FORMAT DATY [Obecnie: {qc['date_mode']}]")
    print("   1 = Standard   (Osobne kolumny: 'Data', 'Od', 'Do')")
    print("   2 = Integrated (Kolumny scalone: 'Data' (data+start) i 'Do' (data+koniec))")
    sel = input("   Wybór (1/2, ENTER=Bez zmian): ").strip()
    if sel == '1': qc['date_mode'] = 'standard'
    if sel == '2': qc['date_mode'] = 'integrated'

    # 3. Zapis
    print(f"\n3. FORMAT PLIKU [Obecnie: {qc['save_format']}]")
    print("   1 = CSV")
    print("   2 = XLSX")
    print("   3 = Both (Oba formaty)")
    sel = input("   Wybór (1/2/3, ENTER=Bez zmian): ").strip()
    if sel == '1': qc['save_format'] = 'csv'
    if sel == '2': qc['save_format'] = 'xlsx'
    if sel == '3': qc['save_format'] = 'both'

    # 4. Kolumny
    extras = qc.get('extra_columns', [])
    print(f"\n4. DODATKOWE KOLUMNY [Wybrane: {len(extras)}]")
    if extras:
        print(f"   Lista: {', '.join(extras)}")
    else:
        print("   (Brak dodatkowych kolumn)")

    if input("   Edytować listę? (t/n): ").strip().lower() == 't':
        print("\n   Aby wybrać kolumny, potrzebuję przykładowego pliku CSV.")
        path = input("   Podaj ścieżkę do pliku: ").strip().strip('"')

        if os.path.exists(path):
            try:
                try:
                    df_dummy = pd.read_csv(path, sep=',', nrows=0, encoding='utf-8')
                except:
                    df_dummy = pd.read_csv(path, sep=';', nrows=0, encoding='utf-8')

                all_cols = df_dummy.columns.tolist()
                req_cols = list(DEFAULT_MAPA_KOLUMN.keys())

                new_extras = select_columns_ui(all_cols, extras, req_cols)
                qc['extra_columns'] = new_extras
                extras = new_extras
                print(f"   ✅ Zaktualizowano listę: {new_extras}")
            except Exception as e:
                print(f"   ❌ Błąd odczytu pliku: {e}")
        else:
            print("   ❌ Plik nie istnieje.")

    # 5. Mapowanie (Synchronizowane)
    print(f"\n5. NAZWY KOLUMN (MAPOWANIE)")
    if input("   Edytować? (t/n): ").strip().lower() == 't':
        # Przekazujemy date_mode, żeby pokazać odpowiednie pole dla końca daty
        customize_column_mapping(CURRENT_CONFIG['column_mapping'], extras, qc['date_mode'])
        print("   ✅ Mapowanie zaktualizowane.")

    # 6. Prefiksy (NOWE)
    print(f"\n6. SKRÓTY ID (PREFIX)")
    if input("   Edytować? (t/n): ").strip().lower() == 't':
        print("\n   Aby skonfigurować skróty, potrzebuję przykładowego pliku CSV.")
        path = input("   Podaj ścieżkę do pliku: ").strip().strip('"')
        if os.path.exists(path):
            try:
                df_raw = load_data(path)
                if not df_raw.empty:
                    # Wywołanie funkcji, która teraz zapisuje do configa
                    customize_prefixes(df_raw, 'Tytuł')
            except Exception as e:
                print(f"   ❌ Błąd: {e}")
        else:
            print("   ❌ Plik nie istnieje.")

    CURRENT_CONFIG['quick_settings'] = qc
    save_config()
    print("\n✅ Konfiguracja zapisana!")


def process_schedule_ranges(df):
    day_map = {'Pn': 0, 'Wt': 1, 'Śr': 2, 'Cz': 3, 'Pt': 4, 'So': 5, 'Nd': 6}
    new_rows = []
    for _, row in df.iterrows():
        s_str = row['Pierwszy dzień']
        e_str = row['Ostatni dzień']
        d_str = row['Dzień tygodnia']
        if pd.isna(s_str): continue

        s_date = pd.to_datetime(s_str, dayfirst=True)
        e_date = pd.to_datetime(e_str, dayfirst=True) if not pd.isna(e_str) else s_date
        days = parse_days_of_week(d_str, day_map)

        if not days:
            r = row.to_dict();
            r['Data'] = s_date.date();
            new_rows.append(r)
        else:
            curr = s_date
            while curr <= e_date:
                if curr.weekday() in days:
                    r = row.to_dict();
                    r['Data'] = curr.date();
                    new_rows.append(r)
                curr += datetime.timedelta(days=1)
    return pd.DataFrame(new_rows)


# --- MAIN ---

def main():
    print("=== KONWERTER PLANU ZAJĘĆ AGH ===")
    load_config()

    while True:
        print("\n" + "=" * 50)
        print("1. Wczytaj plik")
        print("2. ⚙️ Konfiguracja QUICK")
        print("3. Wyjście")

        ch = input("Wybór: ").strip()
        if ch == '3' or ch.lower() in ['q', 'exit']: break
        if ch == '2': configure_quick_settings(); continue
        if ch != '1': continue

        # 1. Load
        path = input("Ścieżka CSV: ").strip().strip('"')
        if not os.path.exists(path): print("❌ Brak pliku."); continue

        try:
            raw = load_data(path)
            if 'Pierwszy dzień' not in raw.columns: raw = pd.read_csv(path, sep=';')
        except Exception as e:
            print(f"❌ Błąd: {e}");
            continue

        print("⏳ Rozwijanie kalendarza...")
        df = process_schedule_ranges(raw)

        # 2. Filter Rows
        df = filter_data_interactive(df)
        if df.empty: print("⚠️ Pusto."); continue

        # 3. Mode Selection
        print("\n--- TRYB ---")
        print("1 -> 🚀 QUICK (Automat wg ustawień)")
        print("2 -> 🛠️ CUSTOM (Pełna kontrola)")
        print("3 -> 🐛 DEBUG (Excel, surowe dane)")

        mode = ''
        while mode not in ['1', '2', '3']: mode = input("Wybór: ").strip()

        # Inicjalizacja
        type_mode = 'detailed'
        date_mode = 'standard'
        save_format = 'xlsx'
        active_map = CURRENT_CONFIG['column_mapping'].copy()
        custom_prefixes = {}  # Słownik na prefixy

        required_cols = list(DEFAULT_MAPA_KOLUMN.keys())
        extra_cols = []

        if mode == '1':  # QUICK
            qc = CURRENT_CONFIG['quick_settings']
            type_mode = qc['type_mode']
            date_mode = qc['date_mode']
            save_format = qc['save_format']
            extra_cols = qc.get('extra_columns', [])

            active_map = CURRENT_CONFIG['column_mapping'].copy()

            df['Tytuł'] = df['Tytuł'].apply(clean_text_for_notion)
            col_t = active_map.get('Tytuł', 'Tytuł')

            if 'Tytuł' in df.columns:
                df = df.rename(columns={'Tytuł': col_t})
                # Zmiana 3: Ładowanie zapisanych prefixów w trybie Quick
                custom_prefixes = CURRENT_CONFIG.get('prefixes', {})
                df = df.rename(columns={col_t: 'Tytuł'})

        elif mode == '2':  # CUSTOM
            all_cols_in_file = df.columns.tolist()
            preselected = CURRENT_CONFIG['quick_settings'].get('extra_columns', [])

            extra_cols = select_columns_ui(all_cols_in_file, preselected, required_cols)

            print("\n--- FORMATOWANIE TYPÓW ZAJĘĆ ---")
            print("1 = Simple   (Wykład -> 'W', reszta -> 'CWA')")
            print("2 = Detailed (Zachowuje oryginalne skróty: CWP, CWL, KON)")
            if input("Wybór: ") == '1': type_mode = 'simple'

            print("\n--- FORMATOWANIE DAT I GODZIN ---")
            print("1 = Standard   (Osobne kolumny: 'Data', 'Od', 'Do')")
            print("2 = Integrated (Kolumny scalone: 'Data' (data+start) i 'Do' (data+koniec))")
            if input("Wybór: ") == '2': date_mode = 'integrated'

            active_map = customize_column_mapping(active_map, extra_cols, date_mode)

            df['Tytuł'] = df['Tytuł'].apply(clean_text_for_notion)
            col_t = active_map.get('Tytuł', 'Tytuł')
            if 'Tytuł' in df.columns:
                df = df.rename(columns={'Tytuł': col_t})
                custom_prefixes = customize_prefixes(df, col_t)
                df = df.rename(columns={col_t: 'Tytuł'})

            print("\n[Zapis] 1=CSV, 2=XLSX, 3=Both");
            sf = input("Wybór: ")
            if sf == '1':
                save_format = 'csv'
            elif sf == '3':
                save_format = 'both'

        elif mode == '3':  # DEBUG
            print("--> DEBUG: Wszystkie kolumny zachowane.")

        # --- PRZETWARZANIE ---

        if mode in ['1', '2']:
            target_cols = set(required_cols + extra_cols)
            # Filtrujemy DF przed rename, używając nazw źródłowych
            keys_to_keep = [k for k in df.columns if k in target_cols]
            if keys_to_keep:
                df = df[keys_to_keep]

        C_TITLE = active_map.get('Tytuł', 'Tytuł')
        C_TYPE = active_map.get('Typ', 'Typ')
        C_DATE = active_map.get('Data', 'Data')
        # Używamy nazw źródłowych dla stałych kolumn, bo rename jest później
        C_START = 'Ogłoszony początek'
        C_END = 'Ogłoszony koniec'

        if 'Typ' in df.columns:
            if type_mode == 'simple':
                df['Typ'] = df['Typ'].apply(lambda x: 'W' if str(x).strip() == 'Wykład' else 'CWA')
            else:
                def map_d(v):
                    v = str(v).strip()
                    # Dedykowane skróty
                    if v == 'Wykład': return 'W'
                    if v == 'Ćwiczenia projektowe': return 'CWP'
                    if v == 'Ćwiczenia laboratoryjne': return 'CWL'
                    if v == 'Konwersatorium': return 'KON'
                    if v == 'Lektorat': return 'LEK'
                    if v == 'Ćwiczenia audytoryjne': return 'CWA'
                    if v == 'Basen' : return 'Basen'
                    if v == 'Zajęcia Warsztatowe': return 'WAR'
                    if v == 'Wychowanie fizyczne' : return 'WF'
                    if v == 'Wychowanie fizyczne2': return 'WF'

                    # Jeśli nie znaleziono powyżej -> 3 pierwsze litery wielkimi literami
                    # np. "Seminarium" -> "SEM", "Projekt" -> "PRO"
                    return v[:3].upper()

                df['Typ'] = df['Typ'].apply(map_d)
            df['Typ'] = df['Typ'].astype(str).str.replace(',', '', regex=False).str.strip()

        if all(c in df.columns for c in [C_TITLE, C_TYPE, C_DATE, C_START]):
            df = df.sort_values(by=[C_TITLE, C_TYPE, C_DATE, C_START])

            # Generowanie ID (Prefix)
            def get_prefix_logic(name):
                # 1. Sprawdź w custom_prefixes (czy to z configa, czy z ręki)
                if name in custom_prefixes:
                    return custom_prefixes[name]
                # 2. Jeśli brak, generuj domyślny
                return get_prefix_default(name)

            df['ID_Prefix'] = df[C_TITLE].map(get_prefix_logic)
            df['ID_Number'] = df.groupby([C_TITLE, C_TYPE]).cumcount() + 1

            def gen_id(row):
                p = row['ID_Prefix'] if not pd.isna(row['ID_Prefix']) else "UNK"
                t = str(row[C_TYPE])[0].upper() if pd.notna(row[C_TYPE]) else "X"
                return f"{p}-{t}{row['ID_Number']:02d}"

            df['Name'] = df.apply(gen_id, axis=1)
            df = df.drop(columns=['ID_Prefix', 'ID_Number'])

        # Formatowanie godzin przed ewentualnym scaleniem
        for c in [C_START, C_END]:
            if c in df.columns:
                df[c] = df[c].astype(str).str.strip().apply(lambda x: x.zfill(5) if ':' in x else x)

        cols_order = ['Name'] if 'Name' in df.columns else []
        if C_DATE in df.columns: cols_order.append(C_DATE)

        # Obsługa Integrated (Custom name + Drop source cols)
        if date_mode == 'integrated' and all(c in df.columns for c in [C_DATE, C_START, C_END]):
            df[C_DATE] = df[C_DATE].astype(str).str.strip()

            # Pobieramy nazwę kolumny końcowej z mapowania (lub domyślną)
            c_end_target_name = active_map.get('Data_End_Integrated', 'Encounter End')

            df[c_end_target_name] = df[C_DATE] + ' ' + df[C_END]
            df[C_DATE] = df[C_DATE] + ' ' + df[C_START]

            # Usuwamy kolumny źródłowe
            df = df.drop(columns=[C_START, C_END], errors='ignore')
            cols_order.append(c_end_target_name)

        # Finalna zamiana nazw
        df = df.rename(columns=active_map)

        # Sortowanie kolumn
        remain = [c for c in df.columns if c not in cols_order]
        df = df[cols_order + remain]

        # Sortowanie wierszy (jeśli kolumna Data istnieje po rename)
        # Musimy znaleźć obecną nazwę kolumny Data
        target_data_col = active_map.get('Data', 'Data')
        if target_data_col in df.columns:
            df = df.sort_values(by=[target_data_col])

        df = df.loc[:, ~df.columns.str.contains('^Unnamed')]

        print("\n--- ZAPIS ---")
        base = input("Nazwa pliku (ENTER=auto): ").strip()
        base = re.sub(r'\.(csv|xlsx|xls)$', '', base, flags=re.I) or "przetworzony_plan"

        def save(df, ext, bn):
            fn = get_unique_filename(bn + ext)
            try:
                if ext == '.csv':
                    df.to_csv(fn, index=False, encoding='utf-8-sig', quoting=csv.QUOTE_MINIMAL)
                else:
                    df.to_excel(fn, index=False)
                print(f"✅ {fn}")
            except Exception as e:
                print(f"❌ {e}")

        if save_format in ['csv', 'both']: save(df, '.csv', base)
        if save_format in ['xlsx', 'both']: save(df, '.xlsx', base)

        print("\n✨ Gotowe!")


if __name__ == "__main__":
    main()