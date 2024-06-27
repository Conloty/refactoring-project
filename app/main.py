from flask import Flask, jsonify
import requests
from flask_sqlalchemy import SQLAlchemy 

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:12345@localhost/Practice_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class Vacancy(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(150), nullable = False)
    company = db.Column(db.String(150), nullable = False)
    city = db.Column(db.String(150), nullable = False)
    url = db.Column(db.String(150), nullable = False)

with app.app_context():
    db.create_all()


@app.route('/parse', methods = ['GET'])
def parse():
    url = 'https://api.hh.ru/vacancies'

    params = {
        'text': 'Python разработчик',
        'area': '1',
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
                "Ссылка": item['alternate_url']
            }
            results.append(result)
            vacancy = Vacancy(
                name = item['name'],
                company = item['employer']['name'],
                city = item['area']['name'],
                url = item['alternate_url']
            )
            db.session.add(vacancy)
        db.session.commit()
        return jsonify(results)
    else:
        return jsonify({'error': f"Ошибка: {response.status_code}"}), response.status_code
    

@app.route('/vacancies', methods=['GET'])
def get_vacancies():
    vacancies = Vacancy.query.all()
    results = [
        {
            "Вакансия": vacancy.name,
            "Компания": vacancy.company,
            "Город": vacancy.city,
            "Ссылка": vacancy.url
        } for vacancy in vacancies
    ]
    return jsonify(results)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)