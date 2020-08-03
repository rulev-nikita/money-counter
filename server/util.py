from pathlib import Path
import csv
import datetime

def data_to_csv_file(user_id, data):
    folder = Path('csv_files')

    if not folder.exists():
        folder = Path('csv_files').mkdir(parents=True, exist_ok=True)

    name = folder/f'{user_id}_{datetime.datetime.now().strftime("%d.%m.%Y")}.csv'
    with open(name, 'w', newline='') as fin:
        writer = csv.writer(fin, dialect='excel')
        writer.writerow(["Category", "Value", "Description", "Date"])
        writer.writerows(data)
    return name