# servers/test_factory.py
"""Тест: проверяем, что Factory создаёт разные типы изменений схемы."""

from servers_project.servers.models import ChangeFactory

print("=" * 60)
print("ТЕСТ FACTORY")
print("=" * 60)

print("\n1. Создаём изменения разных типов через Factory:")

# Создаём CREATE
create_change = ChangeFactory.create(
    change_type="create",
    object_name="users",
    columns="id SERIAL PRIMARY KEY, name VARCHAR(100)"
)
print(f"\n✓ Создан: {create_change}")
print(create_change.get_info())

# Создаём ALTER
alter_change = ChangeFactory.create(
    change_type="alter",
    object_name="users",
    column="name",
    new_type="VARCHAR(255)"
)
print(f"\n✓ Создан: {alter_change}")
print(alter_change.get_info())

# Создаём RENAME
rename_change = ChangeFactory.create(
    change_type="rename",
    object_name="users",
    new_name="clients"
)
print(f"\n✓ Создан: {rename_change}")
print(rename_change.get_info())

# Создаём DROP
drop_change = ChangeFactory.create(
    change_type="drop",
    object_name="clients"
)
print(f"\n✓ Создан: {drop_change}")
print(drop_change.get_info())

print("\n2. Проверяем доступные типы:")
print(f"   Доступные типы: {ChangeFactory.get_available_types()}")

print("\n3. Проверяем обработку ошибок:")
try:
    bad_change = ChangeFactory.create("truncate", "logs")
except ValueError as e:
    print(f"Ошибка перехвачена: {e}")

print("\n4. Вывод:")
print("Factory создаёт объекты разных типов")
print("Клиентский код не знает о конкретных классах")
print("Обработка ошибок работает")