# coding: utf-8
"""Класс FastApiHandler, который обрабатывает запросы API."""

import os
from fastapi import HTTPException, status
from catboost import CatBoostClassifier


class FastApiHandler:
    """Класс FastApiHandler, который обрабатывает запрос и возвращает предсказание."""

    def __init__(self):
        """Инициализация переменных класса."""

        # Типы параметров запроса URI для проверки
        self.uri_param_types = {
            "user_id": str,
            "params": dict
        }

        # Проверяем, откуда происходит запуск сервиса - из докера или без него
        is_docker_run = os.environ.get('AM_I_IN_A_DOCKER_CONTAINER', False)
        model_path = "../models/catboost_churn_model.bin"

        if is_docker_run:
            print("I am running in a Docker container")
            model_path = "/docker/models/catboost_churn_model.bin"
        self.__load_churn_model(model_path=model_path)

    def __load_churn_model(self, model_path: str):
        """Загружаем обученную модель оттока.
        Args:
            model_path (str): Путь до модели.
        """
        try:
            self.model = CatBoostClassifier()
            self.model.load_model(model_path)
        except Exception as e:
            print(f"Failed to load model: {e}")
            self.__raise_server_internal_error()

    def __churn_predict(self, model_params: dict):
        """Предсказываем вероятность оттока.

        Args:
            model_params (dict): Параметры для модели.

        Returns:
            float - вероятность оттока от 0 до 1
        """
        return self.model.predict_proba(list(model_params.values()))[1]

    def check_required_uri_params(self, query_params):
        """Проверяем параметры URI запроса на наличие обязательного набора параметров.

        Args:
            query_params (dict): Параметры запроса.

        Raise:
            :class:`fastapi.HTTPException`: если отсутствуют обязательные параметры в URI запроса.
        """

    def check_required_model_params(self, model_params):
        """Проверяем параметры пользователя на наличие обязательного набора.

        Args:
            model_params (dict): Параметры пользователя для предсказания.

        Raise:
            :class:`fastapi.HTTPException`: если отсутствуют обязательные параметры в meta запроса.
        """

    def get_invalid_param_types(self, param_types, params_to_check):
        """Метод для проверки корректности типов значений параметров в словаре.

        Args:
            param_types (dict): Словарь, в котором ключ - это имя параметра, а значение - его разрешенный тип.
            params_to_check (dict): Словарь, для которого необходимо сделать проверку корректности типов значений
            параметров.

        Returns:
            list: Список названий параметров с неправильными типами. Если таких нет, то возвращается пустой список.
        """
        params_with_invalid_types = []
        for param in params_to_check.keys():
            if param in param_types:
                try:
                    param_type = param_types[param]
                    param_type(params_to_check[param])
                except ValueError:
                    params_with_invalid_types.append(param)
        return params_with_invalid_types

    def check_uri_param_types(self, query_params):
        """Проверяем корректность типов параметров запроса URI.
        Выбрасывает исключение :class:`util.custom_exceptions.InvalidUriParameterTypesError` для найденных параметров,
        которые имеют неожиданный тип.

        Args:
            query_params (dict): Параметры запроса.

        Raises:
            :class:`fastapi.HTTPException`: если имеются параметры с типом, отличным от ожидаемого.
        """
        params_with_invalid_types = self.get_invalid_param_types(self.uri_param_types, query_params)
        if params_with_invalid_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid types of URI parameters: {params_with_invalid_types}"
            )

    def prepare_params(self, params):
        """Разбираем запрос и проверяем его корректность.

        Args:
            params (dict): Словарь параметров запроса.

        Returns:
            - **dict**: Cловарь со всеми параметрами запроса.

        Raises:
            :class:`fastapi.HTTPException`: если будут ошибки.
        """
        return params

    def __raise_server_internal_error(self):
        """Вспомогательный метод для генерации 500-й ошибки."""
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server internal error"
        )

    def handle(self, params):
        """Метод для обработки запросов API для уже разобранного и провалидированного словаря параметров запроса.

        Args:
            params (dict): Словарь параметров запроса.

        Returns:
            dict: Словарь, содержащий результат выполнения запроса.
        """

        try:
            params = self.prepare_params(params)
        except HTTPException as e:
            raise e
        except Exception as e:
            print(f"Exception while preparing parameters from query: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid query"
            )

        try:
            model_params = params["params"]
            user_id = params["user_id"]
            print(f"Predicting for user_id: {user_id} and params:\n{model_params}")
            probability = self.__churn_predict(model_params)
            response = {"user_id": user_id, "probability": probability, "is_churn": int(probability > 0.5)}

        except Exception as e:
            print(f"Error while handling request: {e}")
            self.__raise_server_internal_error()
        else:
            return response
