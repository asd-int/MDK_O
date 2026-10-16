class SchemaChange:
    def __init__(self, object_name: str):
        self.object_name = object_name

    def execute(self) -> str:
        raise NotImplementedError()

    def get_info(self) -> str:
        return self.execute()

class TruncateChange(SchemaChange):
    def execute(self) -> str:
        return f"TRUNCATE TABLE {self.object_name};"

class AlterChange(SchemaChange):
    def __init__(self, object_name: str, column: str, new_type: str):
        super().__init__(object_name)
        self.column = column
        self.new_type = new_type

    def execute(self) -> str:
        return f"ALTER TABLE {self.object_name} ALTER COLUMN {self.column} TYPE {self.new_type};"


class CreateChange(SchemaChange):
    def __init__(self, object_name: str, columns: str):
        super().__init__(object_name)
        self.columns = columns

    def execute(self) -> str:
        return f"CREATE TABLE {self.object_name} ({self.columns});"


class DropChange(SchemaChange):
    def execute(self) -> str:
        return f"DROP TABLE {self.object_name};"




class RenameChange(SchemaChange):
    def __init__(self, object_name: str, new_name: str):
        super().__init__(object_name)
        self.new_name = new_name

    def execute(self) -> str:
        return f"ALTER TABLE {self.object_name} RENAME TO {self.new_name};"




class ChangeFactory:
    _registry = {
        "alter": AlterChange,
        "create": CreateChange,
        "drop": DropChange,
        "rename": RenameChange,
        "truncate": TruncateChange
    }

    @classmethod
    def create(cls, change_type, *args, **kwargs):
        key = change_type.lower().strip()
        if key not in cls._registry:
            raise ValueError(f"Неизвестный тип: {change_type}")
        return cls._registry[key](*args, **kwargs)

    @classmethod
    def get_available_types(cls):
        return list(cls._registry.keys())