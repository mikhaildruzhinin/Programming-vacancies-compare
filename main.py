import os
import requests
from terminaltables import AsciiTable
from dotenv import load_dotenv

# Headhunter
def calculate_average_salary_for_headhunter(vacancy_list):
    salary_list = []
    for vacancy in vacancy_list:
        if vacancy['salary'] is not None:
            salary_prediction = predict_rub_salary_for_headhunter(vacancy['salary'])
            if salary_prediction is not None:
                salary_list.append(salary_prediction)
    vacancies_processed = len(salary_list)
    average_salary = int(sum(salary_list) / vacancies_processed)
    return vacancies_processed, average_salary

def predict_rub_salary_for_headhunter(salary):
    salary_from = salary['from']
    salary_to = salary['to']
    currency = salary['currency']
    if salary is not None:
        salary_prediction = predict_rub_salary(salary_from, salary_to, currency)
        return salary_prediction

def fetch_all_vacancies_for_headhunter(language):
    url = 'https://api.hh.ru/vacancies'
    payload = {'text': f'Программист {language}', 'area': 1, 'period': 30, }
    response = requests.get(url, params=payload)
    response.raise_for_status()
    total_pages = response.json()['pages']
    vacancies_found = response.json()['found']
    vacancy_list = []
    page = 0
    while page < total_pages:
        payload = {'text': f'Программист {language}', 'area': 1, 'period': 30, 'page': page}
        response = requests.get(url, params=payload)
        page_list = response.json()['items']
        for vacancy in page_list:
            vacancy_list.append(vacancy)
        page += 1
    return vacancies_found, vacancy_list

def collect_statistics_by_language_for_headhunter(prog_languages):
    salary_statistics = {}
    for language in prog_languages:
        vacancies_found, vacancy_list = fetch_all_vacancies_for_headhunter(language)
        vacancies_processed, average_salary = calculate_average_salary_for_headhunter(vacancy_list)
        salary_statistics[language] = {'vacancies_found': vacancies_found, 'vacancies_processed': vacancies_processed, 'average_salary': average_salary}
    return salary_statistics

# Superjob
def calculate_average_salary_for_superjob(vacancy_list):
    salary_list = []
    for vacancy in vacancy_list:
        if vacancy['payment_to'] != 0 or vacancy['payment_to'] != 0:
            salary_prediction = predict_rub_salary_for_superjob(vacancy)
            if salary_prediction is not None:
                salary_list.append(salary_prediction)
    vacancies_processed = len(salary_list)
    if vacancies_processed > 0:
        average_salary = int(sum(salary_list) / vacancies_processed)
    else:
        average_salary = 0
    return vacancies_processed, average_salary

def predict_rub_salary_for_superjob(vacancy):
    salary_from = vacancy['payment_from']
    salary_to = vacancy['payment_to']
    currency = vacancy['currency']
    salary_prediction = predict_rub_salary(salary_from, salary_to, currency)
    return salary_prediction

def fetch_all_vacanсies_for_superjob(language, superjob_secret_key):
    url = 'https://api.superjob.ru/2.0/vacancies'
    payload = {'keyword': language, 'catalogues': 48, 'town': 4}
    headers = {'X-Api-App-Id': superjob_secret_key}
    response = requests.get(url, params=payload, headers=headers)
    response.raise_for_status()
    vacancies_found = response.json()['total']
    vacancy_list = []
    page = 0
    while True:
        payload = {'keyword': language, 'catalogues': 48, 'town': 4, 'page': page}
        response = requests.get(url, params=payload, headers=headers)
        response.raise_for_status()
        page_list = response.json()['objects']
        for vacancy in page_list:
            vacancy_list.append(vacancy)
        page += 1
        if not response.json()['more']:
            break
    return vacancies_found, vacancy_list

def collect_statistics_by_language_for_superjob(prog_languages, superjob_secret_key):
    salary_statistics = {}
    for language in prog_languages:
        vacancies_found, vacancy_list = fetch_all_vacanсies_for_superjob(language, superjob_secret_key)
        vacancies_processed, average_salary = calculate_average_salary_for_superjob(vacancy_list)
        salary_statistics[language] = {'vacancies_found': vacancies_found, 'vacancies_processed': vacancies_processed, 'average_salary': average_salary}
    return salary_statistics

# common
def predict_rub_salary(salary_from, salary_to, currency):
    if currency != 'RUR' and currency != 'rub':
        return None
    elif salary_from is None or salary_from == 0:
        salary_prediction = salary_to * 0.8
    elif salary_to is None or salary_to == 0:
        salary_prediction = salary_from * 1.2
    else:
        salary_prediction = (salary_from + salary_to) / 2
    return salary_prediction

def create_table(prog_languages, salary_statistics, title):
    table_data = [['Язык программирования', 'Вакансий найдено', 'Вакансий обработано', 'Средняя зарплата']]
    for language in prog_languages:
        table_raw = [language, salary_statistics[language]['vacancies_found'], salary_statistics[language]['vacancies_processed'], salary_statistics[language]['average_salary']]
        table_data.append(table_raw)
    table = AsciiTable(table_data, title=title)
    return table

def main():
    load_dotenv()
    superjob_secret_key = os.getenv('SUPERJOB_SECRET_KEY')
    prog_languages = ['TypeScript', 'Swift', 'Scala', 'Objective-C', 'Shell', 'Go', 'C', 'C#', 'C++', 'PHP', 'Ruby', '1C', 'Python', 'Java', 'JavaScript']
    salary_statistics_for_headhunter = collect_statistics_by_language_for_headhunter(prog_languages)
    title = 'HeadHunter Moscow'
    table_for_headhunter = create_table(prog_languages, salary_statistics_for_headhunter, title)
    print(table_for_headhunter.table)
    print()
    salary_statistics_for_superjob = collect_statistics_by_language_for_superjob(prog_languages, superjob_secret_key)
    title = 'SuperJob Moscow'
    table_for_superjob = create_table(prog_languages, salary_statistics_for_superjob, title)
    print(table_for_superjob.table)

if __name__ == '__main__':
    main()
