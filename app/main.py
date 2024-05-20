# импортируем библиотеку для работы со случайными числами
import random

# импортируем класс для создания экземпляра FastAPI-приложения
from fastapi import FastAPI

# создаём экземпляр FastAPI-приложения
app = FastAPI()

# обрабатываем запросы к корню приложения
@app.get("/")
def read_root():
    return {"Hello": "World"}

# обрабатываем запросы к специальному пути для получения предсказания модели
# временно имитируем предсказание со случайной генерацией score
@app.get("/api/churn/{user_id}")
def get_prediction_for_item(user_id: str):
    return {"user_id": user_id, "score": random.random()} 

# обрабатываем GET-запросы по пути /v1/credit/{client_id}, 
# чтобы узнать, выдать кредит или нет на основании кредитного score клиента
# ваш код #
@app.get("/api/credit/{client_id}")
def is_credit_approved(client_id: str):
    score = random.uniform(0, 1)
    if score > 0.8:
        return {"client_id": client_id, "approved": 1}
    else:
        return {"client_id": client_id, "approved": 0}