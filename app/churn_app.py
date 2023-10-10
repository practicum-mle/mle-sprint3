# coding: utf-8
"""Приложение Fast API для модели оттока."""


from fastapi import FastAPI, Body
from typing import Dict, Union
from pydantic import BaseModel, Field

from fastapi_handler import FastApiHandler


"""
Пример запуска из директории mle-sprint3/app:
uvicorn churn_app:app --reload --port 8080 --host 0.0.0.0

Для просмотра документации API и совершения тестовых запросов зайти на http://0.0.0.0:8080/api/public/v1/doc
"""


class Item(BaseModel):
    user_id: str
    params: dict


# Создаем приложение Fast API
app = FastAPI(
    title="Churn Model API",
    description="API сервиса получения вероятности оттока",
    version="1.0.0",
    docs_url="/api/public/v1/doc"
)

# Создаем обработчик запросов для API
app.handler = FastApiHandler()


class ItemResponse(BaseModel):
    """Ответ для предсказания оттока в Churn Model API."""
    user_id: str = Field(
        ...,
        description="Идентификатор пользователя"
    )
    probability: float = Field(
        ...,
        description="Вероятность оттока"
    )
    is_churn: int = Field(
        ...,
        description="Принадлежность оттоку"
    )


class ErrorResponse(BaseModel):
    """Модель ответа для ошибок в Churn Model API."""
    error: Union[str, Dict] = Field(
        ...,
        description="Текст сообщения с ошибкой"
    )


ERROR_RESPONSES = {
    400: {'model': ErrorResponse},
    422: {'model': ErrorResponse},
    500: {'model': ErrorResponse}
}


@app.post(
    "/api/public/v1/churn/",
    response_model=ItemResponse,
    responses=ERROR_RESPONSES,
    include_in_schema=True,
    summary="Получить предсказание оттока для пользователя.",
    description="Получить предсказание оттока для пользователя. "
                "В теле запроса должны быть отправлены параметры для модели."
)
async def get_prediction_for_item(
    user_id: str,
    params: dict = Body(
        None,
        title="Параметры пользователя",
        description="Параметры пользователя пользователя в формате JSON",
        example={
            'gender': 1.0,
            'SeniorCitizen': 0.0,
            'Partner': 0.0,
            'Dependents': 0.0,
            'Type': 0.5501916796819537,
            'PaperlessBilling': 1.0,
            'PaymentMethod': 0.2192247621752094,
            'MonthlyCharges': 50.8,
            'TotalCharges': 288.05,
            'MultipleLines': 0.0,
            'InternetService': 0.3437455629703251,
            'OnlineSecurity': 0.0,
            'OnlineBackup': 0.0,
            'DeviceProtection': 0.0,
            'TechSupport': 1.0,
            'StreamingTV': 0.0,
            'StreamingMovies': 0.0,
            'days': 245.0,
            'services': 2.0
        }
    )
):
    """Метод для получения вероятности оттока пользователя.

    Args:
        user_id (str): Идентификатор пользователя.
        params (dict): Произвольное тело запроса в формате JSON.

    Returns:
        dict: Полученная рекомендация сетов цен.
    """
    print(f"user_id: {user_id}")
    print(f"params: {params}")
    all_params = {
        "user_id": user_id,
        "params": params
    }
    # return {"user_id": user_id, "probability": 0.9, "is_churn": 1}
    return app.handler.handle(all_params)
