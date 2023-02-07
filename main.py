import time
import csv
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager


def number(num):
    tera = ['2', '3', '4']
    terov = ['11', '12', '13', '14']
    if str(num)[-2:] in terov:
        return f'{num} контрактов'
    elif str(num)[-1] in tera:
        return f'{num} контракта'
    elif str(num)[-1] == '1':
        return f'{num} контракт'
    else:
        return f'{num} контрактов'


options_chrome = webdriver.ChromeOptions()
options_chrome.add_argument('--headless')
driver = webdriver.Chrome(options=options_chrome, service=ChromeService(ChromeDriverManager().install()))
write_list = []
print("hello")
time.sleep(2)
with open('INN.txt', 'r', encoding='utf-8') as file:
    inn_list = file.read().split()
    print('Сбор всех инн из файла')
try:
    with open(f'{input("Введите имя файла, с которым будет вестись сравнение:")}.json', 'r', encoding='utf-8') as file:
        students = json.load(file)
except FileNotFoundError:
    print('Файл не найден')
    time.sleep(5)

with webdriver.Chrome(options=options_chrome) as browser:
    browser.get('https://torgeat.ru/eatpost/')
    pages = browser.find_element(By.CLASS_NAME, "pgs").find_elements(By.TAG_NAME, 'a')
    last_page = int(pages[-2].text)
    for i in range(1, 300):
        print(f'page {i} / {last_page} ')
        browser.get(f'https://torgeat.ru/eatpost/?page={i}')
        suppliers = browser.find_element(By.TAG_NAME, "tbody").find_elements(By.TAG_NAME, 'tr')
        for supp in suppliers:
            try:
                inn = supp.find_elements(By.TAG_NAME, 'td')[1].text.split()[0]
                name = ' '.join(supp.find_elements(By.TAG_NAME, 'td')[1].text.split()[1:])
                numb_mono = int(supp.find_elements(By.TAG_NAME, 'td')[2].text.split()[0])
                summ = int(supp.find_elements(By.TAG_NAME, 'td')[3].text.replace(' ', ''))
            except Exception as err:
                print(err)
                continue
            if inn in inn_list:
                if inn in students:
                    if summ != students[inn][1]:
                        new_kt = numb_mono - students[inn][0]
                        new_sum = summ - students[inn][1]
                        write_list.append([name, inn, new_kt, new_sum, numb_mono, summ])
                        students[inn] = [numb_mono, summ]
                        print(f'{name} выиграл {number(new_kt)} на {new_sum} р.!')
                    else:
                        write_list.append([name, inn, "Новых контрактов нет", "----", numb_mono, summ])
                        print(f'{name} без новых  контрактов')
                else:
                    write_list.append([name, inn, "Новых контрактов нет", "----", numb_mono, summ])
                    students[inn] = [numb_mono, summ]
                    print(f"Добавление в список нового ученика:{name}", students[inn])

seconds = time.time()
tform = time.strftime('%d_%m', time.localtime(seconds))

with open(f'res{tform}.csv', 'w', encoding='utf-8-sig', newline='') as file:
    writer = csv.writer(file, delimiter=';')
    writer.writerow(['Наименование', 'ИНН', 'Кол-во новых контрактов', 'Сумма н/к', 'Кол-во контрактов', 'Сумма'])
    for el in write_list:
        writer.writerow(el)

with open(f'{tform}.json', 'w', encoding='utf-8') as file:
    json.dump(students, file, indent=4, ensure_ascii=False)
    print('Готово!')
