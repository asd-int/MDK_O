class SchemaChangeLogger:
    """Singleton: единый логгер изменений схемы БД."""
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.logs = []
        return cls._instance

    def log_change(self, change_type: str, object_name: str, details: str = "") -> str:
        if details:
            record = f"[{change_type}] {object_name} — {details}"
        else:
            record = f"[{change_type}] {object_name}"
        self.logs.append(record)
        return record

    def get_all_logs(self) -> list:
        return self.logs