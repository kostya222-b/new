import os
import sqlite3
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from urllib.parse import unquote

# Настройки FastAPI
tags_metadata = [
    {
        'name': 'SEARCH ANSWERS',
        'description': 'API для поиска правильных ответов.',
    }
]

origin_endpoint = [
    'https://iomqt-vo.edu.rosminzdrav.ru',
    'https://iomqt-spo.edu.rosminzdrav.ru',
    'https://iomqt-nmd.edu.rosminzdrav.ru'
]

app = FastAPI(
    root_path="/api",
    title='API for SEARCH ANSWERS',
    description='API для поиска правильных ответов',
    version='0.1.0',
    openapi_tags=tags_metadata,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origin_endpoint,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def search_correct_answers(quest: str):
    # Получаем путь к текущей директории
    this_folder = os.getcwd()

    # Список файлов баз данных
    db_files = ['answers_1.db', 'answers_2.db']

    for db_file in db_files:
        db_path = f'{this_folder}/{db_file}'

        # Проверяем, существует ли файл
        if not os.path.exists(db_path):
            continue

        try:
            # Подключаемся к базе данных
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            # Ищем вопрос в базе данных в колонке options
            cursor.execute('SELECT options FROM questions WHERE question LIKE ?', (f'%{quest}%',))
            result = cursor.fetchone()

            conn.close()

            if result:
                # Разбиваем варианты ответов на отдельные строки
                options = result[0].split('\n')
                # Отбираем правильные ответы (те, которые заканчиваются на '+')
                correct_options = [option.strip().rstrip('.+') for option in options if option.strip().endswith('.+')]
                return correct_options
        except Exception as e:
            print(f"Ошибка при работе с базой данных {db_file}: {e}")
            continue

    raise HTTPException(status_code=404, detail='Нет такого вопроса')

@app.get('/search')
async def search(quest: str):
    try:
        decoded_quest = unquote(quest)
        true_answers_list = search_correct_answers(decoded_quest)
        return {"correct_options": true_answers_list}
    except HTTPException as e:
        raise e

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000)
