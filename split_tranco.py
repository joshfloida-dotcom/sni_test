import os
import zipfile
import urllib.request
import csv
import io

URL = "https://tranco-list.eu/top-1m.csv.zip"
ZIP_FILE = "top-1m.zip"
OUTPUT_DIR = "tranco_lists"
PARTS = 10

def main():
    print(f"Начинаем скачивание архива: {URL}")
    try:
        # Добавляем User-Agent, чтобы избежать блокировки от Cloudflare/NGINX
        req = urllib.request.Request(URL, headers={'User-Agent': 'Mozilla/5.0 (GitHub Actions Worker)'})
        with urllib.request.urlopen(req) as response, open(ZIP_FILE, 'wb') as out_file:
            out_file.write(response.read())
    except Exception as e:
        print(f"Ошибка при скачивании: {e}")
        return

    print("Распаковка архива и извлечение доменов...")
    domains = []
    
    try:
        with zipfile.ZipFile(ZIP_FILE, 'r') as z:
            # Ищем CSV файл внутри архива
            csv_filename = [name for name in z.namelist() if name.endswith('.csv')][0]
            with z.open(csv_filename) as f:
                # Читаем файл построчно (стандартный формат Tranco: rank,domain)
                decoded_file = io.TextIOWrapper(f, encoding='utf-8')
                reader = csv.reader(decoded_file)
                for row in reader:
                    if len(row) >= 2:
                        domains.append(row[1]) # Забираем только сам домен (без ранга)
                    elif len(row) == 1:
                        domains.append(row[0])
    except Exception as e:
         print(f"Ошибка при обработке архива: {e}")
         return
         
    total_domains = len(domains)
    print(f"Успешно извлечено {total_domains} доменов.")
    
    if total_domains == 0:
        print("Ошибка: список пуст.")
        return

    # Создаем папку для итоговых списков
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Считаем, сколько доменов должно быть в одной части (округление вверх)
    chunk_size = (total_domains + PARTS - 1) // PARTS
    
    print(f"Разбиваем на {PARTS} файлов (примерно по {chunk_size} строк в каждом)...")
    
    for i in range(PARTS):
        chunk = domains[i*chunk_size : (i+1)*chunk_size]
        if not chunk:
            break
            
        output_file = os.path.join(OUTPUT_DIR, f"tranco_part_{i+1}.txt")
        with open(output_file, 'w', encoding='utf-8') as out:
            out.write('\n'.join(chunk))
        print(f"  -> Сохранен {output_file} ({len(chunk)} доменов)")
        
    # Удаляем временный архив
    if os.path.exists(ZIP_FILE):
        os.remove(ZIP_FILE)
        
    print("Готово!")

if __name__ == "__main__":
    main()
