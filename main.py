import pandas as pd
import datetime
import re
import os
import csv
import json
from io import StringIO
import ics
# --- PLIK KONFIGURACYJNY ---
CONFIG_FILE = 'options.json'

# --- DEFINICJA LOGICZNEJ KOLEJNOŚCI (DLA UI ORAZ SORTOWANIA WYNIKU) ---
LOGICAL_ORDER = [
    'Name',  # Kod przedmiotu
    'Tytuł',  # Nazwa przedmiotu
    'Typ',  # Typ zajęć
    'Data',  # Data (lub Data start w integrated)
    'Ogłoszony początek',  # Godzina start (standard)
    'Data_End_Integrated',  # Data koniec (integrated)
    'Ogłoszony koniec',  # Godzina koniec (standard)
    'Miejsce',  # Sala
    'Prowadzący / Odpowiedzialny',
    'Pojemność'
]

# --- PRZYJAZNE NAZWY DLA MENU WYBORU ---
FRIENDLY_NAME_MAP = {
    'Tytuł': 'Nazwa przedmiotu',
    'Ogłoszony początek': 'Od (godzina)',
    'Ogłoszony koniec': 'Do (godzina)',
    'Miejsce': 'Sala',
    'Pojemność': 'Pojemność sali',
    'Prowadzący / Odpowiedzialny': 'Prowadzący',
    'Name': 'Kod przedmiotu',
    'Data_End_Integrated': 'Data zakończenia',
    'Typ': 'Typ zajęć'
}

# --- DOMYŚLNE MAPOWANIE ---
DEFAULT_MAPA_KOLUMN = {
    'Name': 'Kod przedmiotu',
    'Tytuł': 'Nazwa przedmiotu',
    'Ogłoszony początek': 'Od',
    'Ogłoszony koniec': 'Do',
    'Miejsce': 'Sala',
    'Pojemność': 'Pojemność sali',
    'Prowadzący / Odpowiedzialny': 'Prowadzący',
    'Typ': 'Typ',
    'Data': 'Data',
    'Data_End_Integrated': 'Data zakończenia'
}

# --- DOMYŚLNA KONFIGURACJA ---
DEFAULT_CONFIG = {
    'quick_settings': {
        'type_mode': 'simple',
        'date_mode': 'integrated',
        'save_format': 'both',
        'extra_columns': []
    },
    'column_mapping': DEFAULT_MAPA_KOLUMN.copy(),
    'prefixes': {}
}

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

    if not lines: raise ValueError("Plik jest pusty!")

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
        choice = input("Wybór [1/2/3]: ").strip()
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


# --- POPRAWIONE MAPOWANIE ---

def customize_column_mapping(current_full_map, active_columns, date_mode='standard'):
    print("\n--- MAPOWANIE NAZW ---")

    # 1. Przygotowanie listy kluczy
    keys_to_show = [col for col in active_columns]
    if 'Name' not in keys_to_show: keys_to_show.insert(0, 'Name')
    if date_mode == 'integrated' and 'Data_End_Integrated' not in keys_to_show:
        keys_to_show.append('Data_End_Integrated')
    if date_mode == 'integrated':
        if 'Ogłoszony początek' in keys_to_show: keys_to_show.remove('Ogłoszony początek')
        if 'Ogłoszony koniec' in keys_to_show: keys_to_show.remove('Ogłoszony koniec')

    # 2. Sortowanie wyświetlania zgodnie z LOGICAL_ORDER
    sorted_keys = []
    for k in LOGICAL_ORDER:
        if k in keys_to_show: sorted_keys.append(k)
    for k in keys_to_show:
        if k not in sorted_keys: sorted_keys.append(k)
    keys_to_show = sorted_keys

    display_map = {}
    for k in keys_to_show:
        display_map[k] = current_full_map.get(k, DEFAULT_MAPA_KOLUMN.get(k, k))

    for k in keys_to_show:
        target_name = display_map.get(k, k)
        source_label = k
        if k == 'Name':
            source_label = "Kod przedmiotu (ID)"
        elif k == 'Data_End_Integrated':
            source_label = "Data zakończenia"
        elif k in FRIENDLY_NAME_MAP:
            source_label = f"{FRIENDLY_NAME_MAP[k]}"
        print(f"  * {source_label:35} -> {target_name}")

    if input("\nZmienić nazwy docelowe? [t/n]: ").strip().lower() != 't': return display_map

    print("\nWpisz nową nazwę lub ENTER by zostawić.")
    for src in keys_to_show:
        label = src
        if src == 'Name':
            label = "Kod przedmiotu (ID)"
        elif src == 'Data_End_Integrated':
            label = "Data zakończenia"
        elif src in FRIENDLY_NAME_MAP:
            label = FRIENDLY_NAME_MAP[src]
        val = input(f"'{label}' -> [{display_map.get(src, src)}]: ").strip()
        if val: display_map[src] = val

    global CURRENT_CONFIG
    CURRENT_CONFIG['column_mapping'].update(display_map)
    save_config()
    return display_map


def customize_prefixes(df, col_title_name):
    print("\n--- KONFIGURACJA SKRÓTÓW ID (PREFIX) ---")
    courses = df[col_title_name].unique()
    prefix_map = CURRENT_CONFIG.get('prefixes', {}).copy()
    for c in courses:
        clean_name = clean_text_for_notion(c)
        default_val = get_prefix_default(clean_name)
        current_val = prefix_map.get(clean_name, default_val)
        print(f"  * {clean_name:30} [{current_val}]")

    if input("\nEdytować skróty? [t/n]: ").strip().lower() != 't':
        final_map = prefix_map.copy()
        for c in courses:
            clean_name = clean_text_for_notion(c)
            if clean_name not in final_map: final_map[clean_name] = get_prefix_default(clean_name)
        return final_map

    print("Wpisz skrót lub ENTER dla domyślnego.")
    for c in courses:
        clean_name = clean_text_for_notion(c)
        default_val = prefix_map.get(clean_name, get_prefix_default(clean_name))
        user_p = input(f"Skrót dla '{clean_name}' [{default_val}]: ").strip().upper()
        prefix_map[clean_name] = user_p if user_p else default_val
    CURRENT_CONFIG['prefixes'] = prefix_map
    save_config()
    return prefix_map


def select_columns_ui(all_columns, preselected_extras, required_columns, date_mode='standard'):
    selected_extras = set(preselected_extras)

    # 1. Przygotowanie dostępnych kolumn
    virtual_cols = ['Name', 'Data_End_Integrated']
    available_cols = list(virtual_cols)
    for c in all_columns:
        if c not in available_cols: available_cols.append(c)

    # 2. Sortowanie logiczne w menu
    sorted_available = []
    for key in LOGICAL_ORDER:
        if key in available_cols: sorted_available.append(key)
    for c in available_cols:
        if c not in sorted_available: sorted_available.append(c)
    available_cols = sorted_available

    # 3. Obsługa Domyślnych Zaznaczeń (Jeśli lista jest pusta)
    selected_extras = {c for c in selected_extras if c in available_cols}
    if not selected_extras:
        defaults = {'Name', 'Tytuł', 'Typ', 'Miejsce', 'Data'}
        if date_mode == 'standard':
            defaults.add('Ogłoszony początek')
            defaults.add('Ogłoszony koniec')
        elif date_mode == 'integrated':
            defaults.add('Data_End_Integrated')
        for d in defaults:
            if d in available_cols: selected_extras.add(d)

    while True:
        print("\n--- WYBÓR KOLUMN DO ZACHOWANIA ---")
        print("Lp.  Stan    Nazwa kolumny")
        print("-" * 50)

        for i, col in enumerate(available_cols):
            status = "[ x ]" if col in selected_extras else "[   ]"
            display_name = col
            note = ""
            if col == 'Name':
                display_name = "Kod przedmiotu";
                note = " (kolumna wtórna)"
            elif col == 'Data_End_Integrated':
                display_name = "Data zakończenia";
                note = " (kolumna wtórna)"
            elif col in FRIENDLY_NAME_MAP:
                display_name = FRIENDLY_NAME_MAP[col]

            print(f"{i + 1:2}. {status} {display_name}{note}")

        print("-" * 50)
        print("• Wpisz numer, aby przełączyć ([x]/[ ]).")
        print("• Szybka selekcja (grupowa):")
        print("  - '0 +1,2,3' -> Wyczyść wszystko i dodaj 1, 2, 3.")
        print("  - '* -5,9'   -> Zaznacz wszystko i usuń 5, 9.")
        print("• ENTER = Zatwierdź.")

        choice = input(">> ").strip().lower()

        if choice in ['ok', '']:
            if len(selected_extras) >= 1:
                break
            else:
                print("⚠️ BŁĄD: Musisz wybrać co najmniej jedną kolumnę!");
                continue

        # --- NOWA LOGIKA PARSOWANIA (Z obsługa grup po przecinku) ---
        # Dzielimy najpierw po spacjach, żeby wyodrębnić grupy, np: "0", "+1,2,3"
        parts = choice.split()

        # Najpierw flagi globalne
        if '*' in parts or 'all' in parts:
            selected_extras = set(available_cols)
        elif '0' in parts or 'none' in parts:
            selected_extras = set()

        for part in parts:
            if part in ['*', 'all', '0', 'none', 'ok']: continue

            # Ustalamy tryb operacji dla danej grupy
            mode = 'toggle' # domyślny dla samych liczb
            content = part

            if part.startswith('-'):
                mode = 'remove'
                content = part[1:] # usuwamy minus
            elif part.startswith('+'):
                mode = 'add'
                content = part[1:] # usuwamy plus

            # Dzielimy zawartość grupy po przecinkach
            numbers = content.split(',')

            for n_str in numbers:
                if n_str.strip().isdigit():
                    idx = int(n_str.strip()) - 1
                    if 0 <= idx < len(available_cols):
                        col_name = available_cols[idx]

                        if mode == 'remove':
                            if col_name in selected_extras: selected_extras.remove(col_name)
                        elif mode == 'add':
                            selected_extras.add(col_name)
                        elif mode == 'toggle':
                            # Dla "1,2,3" bez prefiksu, przełączamy
                            if col_name in selected_extras:
                                selected_extras.remove(col_name)
                            else:
                                selected_extras.add(col_name)

    return list(selected_extras)


# --- KONFIGURACJA QUICK SETTINGS ---

def configure_quick_settings():
    global CURRENT_CONFIG
    qc = CURRENT_CONFIG['quick_settings']
    print("\n--- ⚙️ KONFIGURACJA TRYBU QUICK ---")

    print(f"\n1. TYPY ZAJĘĆ [Obecnie: {qc['type_mode']}]")
    print("   1 = Simple   (Wykład -> 'W', reszta -> 'CWA')")
    print("   2 = Detailed (Zachowuje oryginalne skróty: CWP, CWL, KON)")
    sel = input("   Wybór [1/2, ENTER=Bez zmian]: ").strip()
    if sel == '1': qc['type_mode'] = 'simple'
    if sel == '2': qc['type_mode'] = 'detailed'

    print(f"\n2. FORMAT DATY [Obecnie: {qc['date_mode']}]")
    print("   1 = Standard   (Osobne kolumny: 'Data', 'Od', 'Do')")
    print("   2 = Integrated (Kolumny scalone: 'Data' (data+start) i 'Do' (data+koniec))")
    sel = input("   Wybór [1/2, ENTER=Bez zmian]: ").strip()
    if sel == '1': qc['date_mode'] = 'standard'
    if sel == '2': qc['date_mode'] = 'integrated'

    print(f"\n3. FORMAT PLIKU [Obecnie: {qc['save_format']}]")
    print("   1 = CSV")
    print("   2 = XLSX")
    print("   3 = Both (Oba formaty)")
    sel = input("   Wybór [1/2/3, ENTER=Bez zmian]: ").strip()
    if sel == '1': qc['save_format'] = 'csv'
    if sel == '2': qc['save_format'] = 'xlsx'
    if sel == '3': qc['save_format'] = 'both'

    extras = qc.get('extra_columns', [])
    print(f"\n4. DODATKOWE KOLUMNY [Wybrane: {len(extras)}]")
    if extras:
        # Sortowanie wyświetlania
        pretty = []
        sorted_extras = []
        for k in LOGICAL_ORDER:
            if k in extras: sorted_extras.append(k)
        for k in extras:
            if k not in sorted_extras: sorted_extras.append(k)

        for e in sorted_extras:
            if e == 'Name':
                pretty.append('Kod przedmiotu')
            elif e == 'Data_End_Integrated':
                pretty.append('Data zakończenia')
            elif e in FRIENDLY_NAME_MAP:
                pretty.append(FRIENDLY_NAME_MAP[e])
            else:
                pretty.append(e)
        print(f"   Lista: {', '.join(pretty)}")
    else:
        print("   (Brak dodatkowych kolumn)")

    if input("   Edytować listę? [t/n]: ").strip().lower() == 't':
        print("\n   Aby wybrać kolumny, potrzebuję przykładowego pliku CSV.")
        path = input("   Podaj ścieżkę do pliku: ").strip().strip('"')
        if os.path.exists(path):
            try:
                raw = load_data(path)
                bad_cols = ['Zatwierdzony', 'Żądane usługi', 'Unnamed: 16', 'Nazwa']
                raw.drop(columns=[c for c in bad_cols if c in raw.columns], inplace=True)

                all_cols = raw.columns.tolist()

                # --- NAPRAWA BRAKUJĄCEJ KOLUMNY DATA ---
                if 'Data' not in all_cols:
                    all_cols.append('Data')

                req_cols = list(DEFAULT_MAPA_KOLUMN.keys())
                new_extras = select_columns_ui(all_cols, extras, req_cols, date_mode=qc['date_mode'])
                qc['extra_columns'] = new_extras
                print(f"   ✅ Zaktualizowano listę.")
            except Exception as e:
                print(f"   ❌ Błąd: {e}")
        else:
            print("   ❌ Plik nie istnieje.")

    print(f"\n5. NAZWY KOLUMN (MAPOWANIE)")
    if input("   Edytować? [t/n]: ").strip().lower() == 't':
        customize_column_mapping(CURRENT_CONFIG['column_mapping'], qc['extra_columns'], qc['date_mode'])
    print(f"\n6. SKRÓTY ID")
    if input("   Edytować? [t/n]: ").strip().lower() == 't':
        print("\n   Aby skonfigurować skróty, potrzebuję przykładowego pliku CSV.")
        path = input("   Podaj ścieżkę do pliku: ").strip().strip('"')
        if os.path.exists(path):
            try:
                df_raw = load_data(path)
                if not df_raw.empty: customize_prefixes(df_raw, 'Tytuł')
            except Exception as e:
                print(f"   ❌ Błąd: {e}")

    CURRENT_CONFIG['quick_settings'] = qc
    save_config()
    print("\n✅ Konfiguracja zapisana!")


def process_schedule_ranges(df):
    day_map = {'Pn': 0, 'Wt': 1, 'Śr': 2, 'Cz': 3, 'Pt': 4, 'So': 5, 'Nd': 6}
    new_rows = []
    for _, row in df.iterrows():
        s_str = row['Pierwszy dzień'];
        e_str = row['Ostatni dzień'];
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
        print("1. 📄 Wczytaj plik")
        print("2. ⚙️ Konfiguracja QUICK")
        print("3. 🔚 Wyjście")

        ch = input("Wybór: ").strip()
        if ch == '3' or ch.lower() in ['q', 'exit']: break
        if ch == '2': configure_quick_settings(); continue
        if ch != '1': continue

        path = input("Podaj ścieżkę do pliku CSV lub przeciągnij go do tego okna: ").strip().strip('"')
        if not os.path.exists(path): print("❌ Brak pliku."); continue

        try:
            raw = load_data(path)
            if 'Pierwszy dzień' not in raw.columns: raw = pd.read_csv(path, sep=';')

            # --- USUWANIE ŚMIECIOWYCH KOLUMN ---
            cols_to_drop = ['Żądane usługi', 'Unnamed: 16', 'Zatwierdzony', 'Nazwa']
            existing_to_drop = [c for c in cols_to_drop if c in raw.columns]
            if existing_to_drop: raw.drop(columns=existing_to_drop, inplace=True)

        except Exception as e:
            print(f"❌ Błąd: {e}"); continue

        print("⏳ Rozwijanie kalendarza...");
        df = process_schedule_ranges(raw)
        df = filter_data_interactive(df)
        if df.empty: print("⚠️ Pusto."); continue

        print("\n--- TRYB ---")
        print("1 -> 🚀 QUICK (Automat wg ustawień)")
        print("2 -> 🛠️ CUSTOM (Pełna kontrola)")
        print("3 -> 🐛 DEBUG (Excel, surowe dane)")

        mode = ''
        while mode not in ['1', '2', '3']: mode = input("Wybór [1/2/3]: ").strip()

        type_mode = 'simple';
        date_mode = 'integrated';
        save_format = 'both'
        active_map = CURRENT_CONFIG['column_mapping'].copy()
        custom_prefixes = {};
        extra_cols = []
        source_key_cols = ['Data', 'Tytuł', 'Typ', 'Ogłoszony początek', 'Ogłoszony koniec', 'Miejsce']

        if mode == '1':  # QUICK
            qc = CURRENT_CONFIG['quick_settings']
            type_mode, date_mode, save_format = qc['type_mode'], qc['date_mode'], qc['save_format']
            extra_cols = qc.get('extra_columns', [])
            if not extra_cols:
                # Domyślne jeśli pusty config
                extra_cols = ['Name', 'Tytuł', 'Typ', 'Data', 'Miejsce']
                if date_mode == 'integrated':
                    extra_cols.append('Data_End_Integrated')
                else:
                    extra_cols.extend(['Ogłoszony początek', 'Ogłoszony koniec'])

            active_map = CURRENT_CONFIG['column_mapping'].copy()
            df['Tytuł'] = df['Tytuł'].apply(clean_text_for_notion)
            col_t = active_map.get('Tytuł', 'Tytuł')
            if 'Tytuł' in df.columns:
                df = df.rename(columns={'Tytuł': col_t})
                custom_prefixes = CURRENT_CONFIG.get('prefixes', {})
                df = df.rename(columns={col_t: 'Tytuł'})

        elif mode == '2':  # CUSTOM
            all_cols = df.columns.tolist()
            preselected = CURRENT_CONFIG['quick_settings'].get('extra_columns', [])

            print("\n--- FORMATOWANIE DAT I GODZIN ---")
            print("1 = Standard   (Osobne kolumny: 'Data', 'Od', 'Do')")
            print("2 = Integrated (Kolumny scalone: 'Data' (data+start) i 'Do' (data+koniec))")
            if input("Wybór [1/2]: ") == '1': date_mode = 'standard'

            # Przekazujemy date_mode do UI aby ustalić domyślne zaznaczenia
            extra_cols = select_columns_ui(all_cols, preselected, source_key_cols, date_mode=date_mode)

            # --- ZAPAMIĘTYWANIE WYBORU (PERSISTENCE) ---
            CURRENT_CONFIG['quick_settings']['extra_columns'] = extra_cols
            save_config()

            print("\n--- FORMATOWANIE TYPÓW ZAJĘĆ ---")
            print("1 = Simple   (Wykład -> 'W', reszta -> 'CWA')")
            print("2 = Detailed (Zachowuje oryginalne skróty: CWP, CWL, KON)")
            if input("Wybór [1/2]: ") == '2' : type_mode = 'detailed'
            print(type_mode)

            active_map = customize_column_mapping(active_map, extra_cols, date_mode)
            df['Tytuł'] = df['Tytuł'].apply(clean_text_for_notion)
            col_t = active_map.get('Tytuł', 'Tytuł')
            if 'Tytuł' in df.columns:
                df = df.rename(columns={'Tytuł': col_t})
                custom_prefixes = customize_prefixes(df, col_t)
                df = df.rename(columns={col_t: 'Tytuł'})

            print("\n[Zapis] 1=CSV, 2=XLSX, 3=Both")
            sf = input("Wybór [1/2/3]: ")
            if sf == '1':
                save_format = 'csv'
            elif sf == '2':
                save_format = 'xlsx'

        elif mode == '3':
            save_format = 'xlsx'
            extra_cols = df.columns.tolist()

        # --- PRZETWARZANIE ---
        S_TITLE, S_TYPE, S_DATA, S_START, S_END = 'Tytuł', 'Typ', 'Data', 'Ogłoszony początek', 'Ogłoszony koniec'

        if mode in ['1', '2']:
            target_cols = set(extra_cols)
            for sys in [S_TITLE, S_TYPE, S_DATA, S_START, S_END, 'Miejsce']:
                if sys in df.columns: target_cols.add(sys)
            keys = [k for k in df.columns if k in target_cols]
            if keys: df = df[keys]

        if S_TYPE in df.columns:
            if type_mode == 'simple':
                df[S_TYPE] = df[S_TYPE].apply(lambda x: 'W' if str(x).strip() == 'Wykład' else 'CWA')
            else:
                def map_d(v):
                    v = str(v).strip()
                    m = {'Wykład': 'W', 'Ćwiczenia projektowe': 'CWP', 'Ćwiczenia laboratoryjne': 'CWL',
                         'Konwersatorium': 'KON', 'Lektorat': 'LEK', 'Ćwiczenia audytoryjne': 'CWA',
                         'Zajęcia warsztatowe': 'WAR', 'Wychowanie fizyczne 2': 'WF',
                         'Wychowanie fizyczne 1': "WF", 'Wychowanie fizyczne 3' : 'WF' }
                    return m.get(v, v[:3].upper())

                df[S_TYPE] = df[S_TYPE].apply(map_d)
            df[S_TYPE] = df[S_TYPE].astype(str).str.replace(',', '').str.strip()

        if all(c in df.columns for c in [S_TITLE, S_TYPE, S_DATA, S_START]):
            df = df.sort_values(by=[S_TITLE, S_TYPE, S_DATA, S_START])

            def get_prefix_logic(name): return custom_prefixes.get(name, get_prefix_default(name))

            df['ID_Prefix'] = df[S_TITLE].map(get_prefix_logic)
            df['ID_Number'] = df.groupby([S_TITLE, S_TYPE]).cumcount() + 1
            df['Name'] = df.apply(lambda
                                      r: f"{r['ID_Prefix'] if not pd.isna(r['ID_Prefix']) else 'UNK'}-{str(r[S_TYPE])[0].upper() if pd.notna(r[S_TYPE]) else 'X'}{r['ID_Number']:02d}",
                                  axis=1)
            df = df.drop(columns=['ID_Prefix', 'ID_Number'])

        for c in [S_START, S_END]:
            if c in df.columns: df[c] = df[c].astype(str).str.strip().apply(lambda x: x.zfill(5) if ':' in x else x)

        if all(c in df.columns for c in [S_DATA, S_START, S_END]):
            df[S_DATA] = df[S_DATA].astype(str).str.strip()
            c_end_key = 'Data_End_Integrated'
            if (date_mode == 'integrated') or (c_end_key in extra_cols):
                df[c_end_key] = df[S_DATA] + ' ' + df[S_END]
                if date_mode == 'integrated':
                    df[S_DATA] = df[S_DATA] + ' ' + df[S_START]
                    df = df.drop(columns=[S_START, S_END], errors='ignore')

        df = df.rename(columns=active_map)

        # --- FINALNE SORTOWANIE I FILTROWANIE ---
        if mode in ['1', '2']:
            final_columns = []

            # Krok 1: Określ mapowane nazwy kluczowych kolumn
            T_CODE = active_map.get('Name', 'Name')
            T_NAME = active_map.get('Tytuł', 'Tytuł')
            T_TYPE = active_map.get('Typ', 'Typ')  # Pobieramy nazwę dla Typu
            T_DATA = active_map.get('Data', 'Data')
            T_END = active_map.get('Data_End_Integrated', 'Data_End_Integrated')
            T_ROOM = active_map.get('Miejsce', 'Miejsce')

            # Krok 2: Ustal Priorytetową Kolejność (Typ po Nazwie)
            priority_names = []
            priority_names.append(T_CODE)
            priority_names.append(T_NAME)
            priority_names.append(T_TYPE)
            priority_names.append(T_DATA)
            if date_mode == 'standard':
                priority_names.append(active_map.get('Ogłoszony początek', 'Ogłoszony początek'))
                priority_names.append(active_map.get('Ogłoszony koniec', 'Ogłoszony koniec'))
            priority_names.append(T_END)
            priority_names.append(T_ROOM)

            # Krok 3: Zbuduj listę kolumn wybranych przez użytkownika
            user_selected_mapped = []
            for src in extra_cols:
                # Logika ignorowania wchłoniętych kolumn w trybie integrated
                if date_mode == 'integrated' and src in ['Ogłoszony początek', 'Ogłoszony koniec']: continue
                if date_mode == 'integrated' and src == 'Data':
                    tgt = active_map.get('Data', 'Data');
                    user_selected_mapped.append(tgt)
                    tgt_e = active_map.get('Data_End_Integrated', 'Data_End_Integrated')
                    if tgt_e not in user_selected_mapped: user_selected_mapped.append(tgt_e)
                    continue

                tgt = active_map.get(src, src)
                if tgt in df.columns: user_selected_mapped.append(tgt)

            # Krok 4: Sklejanie (Priorytety TYLKO jeśli wybrane + Reszta z wyboru użytkownika)
            for p in priority_names:
                if p in user_selected_mapped and p not in final_columns:
                    final_columns.append(p)

            for u in user_selected_mapped:
                if u not in final_columns:
                    final_columns.append(u)

            if final_columns: df = df[final_columns]

        # Sortowanie wierszy po dacie
        if active_map.get('Data', 'Data') in df.columns:
            df = df.sort_values(by=[active_map.get('Data', 'Data')])

        print("\n--- ZAPIS ---")
        base = input("Nazwa pliku (ENTER=auto): ").strip() or "przetworzony_plan"

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