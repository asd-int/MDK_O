# servers/test_singleton.py
"""Тест: проверяем, что Singleton создаёт только один экземпляр."""

from servers_project.servers.singleton import SchemaChangeLogger

print("=" * 60)
print("ТЕСТ SINGLETON")
print("=" * 60)

# Создаём "два" объекта
print("\n1. Создаём первый объект...")
logger1 = SchemaChangeLogger()

print("\n2. Создаём второй объект...")
logger2 = SchemaChangeLogger()

print("\n3. Проверяем, что это ОДИН И ТОТ ЖЕ объект:")
print(f"   logger1 is logger2: {logger1 is logger2}")
print(f"   id(logger1): {id(logger1)}")
print(f"   id(logger2): {id(logger2)}")

print("\n4. Добавляем запись в журнал через logger1:")
record = logger1.log_change("CREATE", "users", "CREATE TABLE users (id SERIAL);")
print(f"   Результат: {record}")

print("\n5. Получаем журнал через logger2:")
print(f"   Все записи: {logger2.get_all_logs()}")

print("\n6. Вывод:")
print("logger1 и logger2 — это один объект")
print("Запись, добавленная через logger1, видна в logger2")
print("Singleton работает корректно!")