from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:12345@localhost/Practice_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class Vacancy(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    company = db.Column(db.String(150), nullable=False)
    city = db.Column(db.String(150), nullable=False)
    work_format = db.Column(db.String(150), nullable=True)
    url = db.Column(db.String(150), nullable=False)

with app.app_context():
    db.create_all()


@app.route('/parse', methods=['POST'])
def parse():
    data = request.get_json()
    job_title = data.get('jobTitle', '')
    company = data.get('company', '')
    city = data.get('city', '')
    work_format = data.get('workFormat', '')

    url = 'https://api.hh.ru/vacancies'
    params = {
        'text': f'{job_title} {company} {city} {work_format}',
        'area': '1',  # Moscow
        'per_page': 10
    }

    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        results = []
        for item in data['items']:
            result = {
                "Вакансия": item['name'],
                "Компания": item['employer']['name'],
                "Город": item['area']['name'],
                "Формат работы": item.get('schedule', {}).get('name', ''),
                "Ссылка": item['alternate_url']
            }
            results.append(result)
            vacancy = Vacancy(
                name=item['name'],
                company=item['employer']['name'],
                city=item['area']['name'],
                work_format=item.get('schedule', {}).get('name', ''),
                url=item['alternate_url']
            )
            db.session.add(vacancy)
        db.session.commit()
        return jsonify(results)
    else:
        return jsonify({'error': f"Ошибка: {response.status_code}"}), response.status_code



@app.route('/vacancies', methods=['GET'])
def get_vacancies():
    job_title = request.args.get('jobTitle', '')
    company = request.args.get('company', '')
    city = request.args.get('city', '')
    work_format = request.args.get('workFormat', '')

    query = Vacancy.query
    if job_title:
        query = query.filter(Vacancy.name.ilike(f'%{job_title}%'))
    if company:
        query = query.filter(Vacancy.company.ilike(f'%{company}%'))
    if city:
        query = query.filter(Vacancy.city.ilike(f'%{city}%'))
    if work_format:
        query = query.filter(Vacancy.work_format.ilike(f'%{work_format}%'))

    vacancies = query.all()
    results = [
        {
            "Вакансия": vacancy.name,
            "Компания": vacancy.company,
            "Город": vacancy.city,
            "Формат работы": vacancy.work_format,
            "Ссылка": vacancy.url
        } for vacancy in vacancies
    ]
    return jsonify(results)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)



