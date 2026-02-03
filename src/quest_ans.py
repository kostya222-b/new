import os
import sqlite3
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from urllib.parse import unquote
import re

# Настройки FastAPI
tags_metadata = [
    {
        'name': 'SEARCH ANSWERS',
        'description': 'API для поиска правильных ответов.',
    }
]

# ИСПРАВЛЕНО: Убраны лишние пробелы в конце URL (были причиной проблем CORS)
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
    this_folder = os.getcwd()
    db_files = ['answers_1.db', 'answers_2.db']

    for db_file in db_files:
        db_path = f'{this_folder}/{db_file}'
        if not os.path.exists(db_path):
            continue

        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT options FROM questions WHERE question = ?', (quest,))
            result = cursor.fetchone()
            conn.close()

            if result:
                options = result[0].split('\n')
                correct_options = []
                for option in options:
                    if '.+' in option:
                        if option.count('.+') > 1:
                            sub_options = re.split(r'\s*\.\+\s*,\s*|\s*\.\+', option.strip())
                            for sub_option in sub_options:
                                if sub_option.strip():
                                    correct_options.append(sub_option.strip())
                        else:
                            correct_option = option.strip().rstrip('.+')
                            correct_options.append(correct_option)
                return correct_options
        except Exception as e:
            print(f"Ошибка при работе с базой данных {db_file}: {e}")
            continue
    
    # ИСПРАВЛЕНО: Возвращаем пустой список вместо исключения
    return []

@app.get('/test')
async def test(quest: str):
    # ИСПРАВЛЕНО: Убрано исключение, всегда возвращаем 200 OK
    decoded_quest = unquote(quest)
    true_answers_list = search_correct_answers(decoded_quest)
    # Всегда возвращаем успешный ответ даже для несуществующих вопросов
    return {"correct_options": true_answers_list}

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000)