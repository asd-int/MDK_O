from django.http import HttpResponse
from .singleton import SchemaChangeLogger
from .models import ChangeFactory


def index(request):
    logger = SchemaChangeLogger()
    logger2 = SchemaChangeLogger()

    html = ["<h1>Журнал изменений схем БД</h1>"]

    html.append("<h2>Singleton:</h2>")
    html.append(f"<p>id(logger1) = {id(logger)}</p>")
    html.append(f"<p>id(logger2) = {id(logger2)}</p>")
    html.append(f"<p>id(logger1) == id(logger2): {id(logger) == id(logger2)}</p>")

    html.append("<h2>Factory:</h2><ul>")
    try:
        change = ChangeFactory.create("create", "users", "id SERIAL PRIMARY KEY")
        sql = change.execute()
        logger.log_change("CREATE", "users", sql)
        html.append(f"<li>{sql}</li>")

        change = ChangeFactory.create("alter", "users", "name", "VARCHAR(255)")
        sql = change.execute()
        logger.log_change("ALTER", "users", sql)
        html.append(f"<li>{sql}</li>")

        change = ChangeFactory.create("rename", "users", "clients")
        sql = change.execute()
        logger.log_change("RENAME", "users", sql)
        html.append(f"<li>{sql}</li>")

        change = ChangeFactory.create("drop", "clients")
        sql = change.execute()
        logger.log_change("DROP", "clients", sql)
        html.append(f"<li>{sql}</li>")

        change = ChangeFactory.create("truncate", "logs")
        sql = change.execute()
        logger.log_change("TRUNCATE", "logs", sql)
        html.append(f"<li>{sql}</li>")

    except ValueError as e:
        html.append(f"<li>{e}</li>")
    html.append("</ul>")

    return HttpResponse("".join(html))


def history_view(request):  # Переименовали функцию в понятную history_view
    logger = SchemaChangeLogger()
    logs = logger.get_all_logs()

    html = ["<h1>История изменений схем БД</h1>"]

    if logs:
        html.append("<p>Данные успешно сохранены в памяти Singleton-объекта между запросами:</p>")
        html.append("<ol>")
        for record in logs:
            html.append(f"<li><code>{record}</code></li>")
        html.append("</ol>")
    else:
        html.append(
            "<p>Журнал пуст. Сначала зайдите на главную страницу, чтобы фабрика создала логи!</p>")

    return HttpResponse("".join(html))