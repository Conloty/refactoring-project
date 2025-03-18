from flask import jsonify, request
import requests
from db import db, Vacancy

Moscow_area_ID = '1'
Per_page = 10
url_hh_ru = 'https://api.hh.ru/vacancies'

def get_params():
    data = request.get_json()
    job_title = data.get('jobTitle', '')
    company = data.get('company', '')
    city = data.get('city', '')
    work_format = data.get('workFormat', '')

    params = {
        'text': f'{job_title} {company} {city} {work_format}',
        'area': Moscow_area_ID,
        'per_page': Per_page
    }    
    return params
    
def add_result(item):
    result = {
        "Вакансия": item['name'],
        "Компания": item['employer']['name'],
        "Город": item['area']['name'],
        "Формат работы": item.get('schedule', {}).get('name', ''),
        "Ссылка": item['alternate_url']
    }
    return result

def add_vacancy(item):
    vacancy = Vacancy(
        name=item['name'],
        company=item['employer']['name'],
        city=item['area']['name'],
        work_format=item.get('schedule', {}).get('name', ''),
        url=item['alternate_url']
    )
    return vacancy

def get_filters():
    return {
        'job_title': request.args.get('jobTitle', ''),
        'company': request.args.get('company', ''),
        'city': request.args.get('city', ''),
        'work_format': request.args.get('workFormat', '')
    }

def apply_filters(query, filters):
    if filters['job_title']:
        query = query.filter(Vacancy.name.ilike(f"%{filters['job_title']}%"))
    if filters['company']:
        query = query.filter(Vacancy.company.ilike(f"%{filters['company']}%"))
    if filters['city']:
        query = query.filter(Vacancy.city.ilike(f"%{filters['city']}%"))
    if filters['work_format']:
        query = query.filter(Vacancy.work_format.ilike(f"%{filters['work_format']}%"))
    return query
    
def get_results(vacancies):
    results = [
        {
            "Вакансия": vacancy.name,
            "Компания": vacancy.company,
            "Город": vacancy.city,
            "Формат работы": vacancy.work_format,
            "Ссылка": vacancy.url
        } for vacancy in vacancies
    ]
    return results

def init_routes(app):
    @app.route('/parse', methods=['POST'])
    def parse():
        params = get_params()
        response = requests.get(url_hh_ru, params=params)
        if response.status_code == 200:
            data = response.json()
            results = []
            for item in data['items']:
                result = add_result(item)
                results.append(result)
                vacancy = add_vacancy(item)
                db.session.add(vacancy)
            db.session.commit()
            return jsonify(results)
        else:
            return jsonify({'error': f"Ошибка: {response.status_code}"}), response.status_code

    @app.route('/vacancies', methods=['GET'])
    def get_vacancies():  
        filters = get_filters()
        query = Vacancy.query
        query = apply_filters(query, filters)

        vacancies = query.all()
        results = get_results(vacancies)
        
        return jsonify(results)