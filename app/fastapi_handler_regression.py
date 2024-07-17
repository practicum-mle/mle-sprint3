"""Класс FastApiHandler, который обрабатывает запросы API."""

# импортируем класс модели
from catboost import CatBoostRegressor

class FastApiHandler:
    """Класс FastApiHandler, который обрабатывает запрос и возвращает предсказание."""

    def __init__(self, model_path: str = "../models/catboost_churn_model.bin"):
        """Инициализация переменных класса.

        Args:
            model_path (str): Путь до модели.
        """

        # типы параметров запроса для проверки
        self.query_param_types = {
            "client_id": str,
            "model_params": dict
        }
        # список необходимых параметров модели 
        self.required_model_params = [
            'gender', 'Type', 'PaperlessBilling', 'PaymentMethod', 
            'MonthlyCharges', 'TotalCharges'
        ]
        self.model_path = model_path
        self.load_credit_model()

    def load_credit_model(self):
        """Загружаем обученную модель предсказания кредитного рейтинга."""
        try:
            self.model = CatBoostRegressor()
            self.model.load_model(self.model_path)
        except Exception as e:
            print(f"Failed to load model: {e}") 

    def credit_rating_predict(self, model_params: dict) -> float:
        """Предсказываем кредитный рейтинг.

        Args:
            model_params (dict): Параметры для получения предсказаний моделью.

        Returns:
            float — кредитный рейтинг

        Examples:
            "model_params": {
                "gender": 1.0,
                "Type": 0.5501916796819537,
                "PaperlessBilling": 1.0,
                "PaymentMethod": 0.2192247621752094,
                "MonthlyCharges": 50.8,
                "TotalCharges": 288.05,
                ...
            }
        """
        return self.model.predict(list(model_params.values())) 

    def check_required_query_params(self, query_params: dict) -> bool:
        """Проверяем параметры запроса на наличие обязательного набора.

        Args:
            query_params (dict): Параметры запроса.

        Returns:
            bool: True — если есть нужные параметры, False — иначе

       	Examples:
            "query_params": {
                "client_id": 123,
                "model_params": {...}
            } 
        """
        for param in self.query_param_types.keys():
            if param not in query_params:
                return False

        return True

    def check_required_query_types(self, query_params: dict) -> bool:
        """Проверяем параметры запроса на типы данных.

        Args:
            query_params (dict): Параметры запроса.

        Returns:
            bool: True — если типы параметров соответствуют, False — иначе

       	Examples:
            "query_params": {
                "client_id": "123",
                "model_params": {...}
            } 
        """
        for param, param_type in self.query_param_types.items():
            if not isinstance(query_params[param], param_type):
                return False

        return True

    def check_required_model_params(self, model_params: dict) -> bool:
        """Проверяем параметры пользователя на наличие обязательного набора.

        Args:
            model_params (dict): Параметры пользователя для предсказания.

        Returns:
            bool: True — если есть нужные параметры, False — иначе
        """
        if set(model_params.keys()) == set(self.required_model_params):
            return True
        return False 
 
    def validate_params(self, params: dict) -> bool:
        """Проверяем корректность параметров запроса и параметров модели.

        Args:
            params (dict): Словарь параметров запроса.

        Returns:
             bool: True — если пройдены проверки, False — иначе

        Examples:
            "params": {
                "client_id": "123",
                "model_params": {
                    "gender": 1.0,
                    "Type": 0.5501916796819537,
                    "PaperlessBilling": 1.0,
                    "PaymentMethod": 0.2192247621752094,
                    "MonthlyCharges": 50.8,
                    "TotalCharges": 288.05,
                    ...
                }
            }
        """
        if self.check_required_query_params(params):
            print("All query params exist")
        else:
            print("Not all query params exist")
            return False

        if self.check_required_query_types(params):
            print("All query params types valid")
        else:
            print("Not all query params types valid")
            return False

        if self.check_required_model_params(params["model_params"]):
            print("All model params exist")
        else:
            print("Not all model params exist")
            return False
        return True 

    def handle(self, params):
        """Функция для обработки входящих запросов по API. Запрос состоит из параметров.

        Args:
            params (dict): Словарь параметров запроса.

        Returns:
            dict: Словарь, содержащий результат выполнения запроса.
        """
        try:
            # Валидируем запрос к API
            if not self.validate_params(params):
                print("Error while handling request")
                response = {"Error": "Problem with parameters"}
            else:
                model_params = params["model_params"]
                client_id = params["client_id"]
                print(f"Predicting for client_id: {client_id} and model_params:\n{model_params}")
                # Получаем предсказания модели
                predicted_rating = self.credit_rating_predict(model_params)
                response = {
                    "client_id": client_id, 
                    "predicted_credit_rating": predicted_rating
                }
        except Exception as e:
            print(f"Error while handling request: {e}")
            return {"Error": "Problem with request"}
        else:
            return response 

if __name__ == "__main__":

    # test_params = {
    #     "client_id": 123,
    #     "params": {
    #         "gender": 1.0,
    #         "Type": 0.5501916796819537,
    #         "PaperlessBilling": 1.0,
    #         "PaymentMethod": 0.2192247621752094,
    #         "MonthlyCharges": 50.8,
    #         "TotalCharges": 288.05,
    #     }
    # }

    test_params = {
        "client_id": "123",
        "model_params": {
            "gender": 1.0,
            "Type": 0.5501916796819537,
            "PaperlessBilling": 1.0,
            "PaymentMethod": 0.2192247621752094,
            "MonthlyCharges": 50.8,
            "TotalCharges": 288.05,
        }
    }

    # создаём обработчик запросов для API
    handler = FastApiHandler()

    # делаем тестовый запрос
    response = handler.handle(test_params)
    print(f"Response: {response}")
