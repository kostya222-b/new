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
    this_folder = os.getcwd()
    db_path = f'{this_folder}/answers.db'

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('SELECT options FROM questions WHERE question LIKE ?', (f'%{quest}%',))
    result = cursor.fetchone()

    conn.close()

    if result:
        options = result[0].split('\n')
        correct_options = [option.strip().rstrip('.+') for option in options if option.strip().endswith('.+')]
        return correct_options
    else:
        raise HTTPException(status_code=404, detail='Нет такого вопроса')

@app.get('/test')
async def test(quest: str):
    try:
        decoded_quest = unquote(quest)
        true_answers_list = search_correct_answers(decoded_quest)
        return {"correct_options": true_answers_list}
    except HTTPException as e:
        raise e

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)
