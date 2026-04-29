# dizi-us-service

Backend-сервис на FastAPI для управления аутентификацией, профилями пользователей и системой email-уведомлений.

## Технологический стек

- Framework: FastAPI
- Dependency Injection: Встроенная система Depends (используется get_user_service для инъекции бизнес-логики).
- Pydantic (схемы в app.schema).
- Фоновые задачи Taskiq.

## Инструкция по запуску

Для локального развертывания сервиса используется Docker и Docker Compose. Процесс состоит из двух этапов:

1. **Подготовка окружения**

В корневой директории проекта необходимо создать файл .env на основе шаблона .env.example. 
Заполните его актуальными параметрами (настройки базы данных, ключи для JWT, настройки SMTP для email).

```
cp .env.example .env
```

2. **Запуск контейнеров**

Запуск всех зависимостей (база данных, кэш) и самого приложения выполняется одной командой в фоновом режиме:

```
docker-compose up -d
```
После запуска сервис будет доступен по адресу http://localhost:8000. Документация по адресу http://localhost:8000/docs.

## Правила разработки

Для обеспечения высокого качества кода и эффективного взаимодействия в команде необходимо придерживаться следующих принципов:

- Обязательное использование аннотаций как для входных, так и для выходных параметров всех функций и методов.
- Код должен быть самодокументированным. Использование комментариев допускается только в исключительных случаях; логика должна быть понятна из названий и структур.
- Все входные данные должны проходить через Pydantic-схемы для обеспечения целостности данных.
- Придерживайтесь разделения на слои (Schema -> Router -> Service -> Repository).
- Код должен соответствовать стандартам PEP 8.

## Работа с Git и Merge Requests

### Именование веток

Название ветки должно четко отражать суть задачи:

- feat/описание-функционала — для новых возможностей.
- fix/описание-ошибки — для исправления багов.
- refactor/что-именно — для оптимизации и улучшения структуры.

### Процесс проверки

Для обеспечения стабильности основной ветки и прозрачности разработки, в проекте установлен следующий порядок внесения изменений:

1. **Оформление запроса (Merge Request)**

После завершения работы над задачей разработчик обязан создать Merge Request, соблюдая правила именования и описания:

- Обязательное указание номера задачи (например, [ISSUE-12] или [TASK-42]) в начале заголовка. В описании должен быть представлен краткий перечень ключевых изменений.
- Связь с тикетами: В описании рекомендуется использовать ключевые слова (например, Closes #12), если ваша система управления задачами поддерживает автоматическое закрытие.

2. **Назначение проверяющего (Reviewer)**

- В поле Reviewer необходимо в обязательном порядке указывать пользователя darkgoodack.
- Создание MR без назначения хотя бы одного ответственного за проверку считается плохим тоном.

3. **Прохождение проверки и слияние**

- Merge в основную ветку разрешено только после получения статуса Approved от проверяющего.
- Все автоматические проверки (тесты, линтеры, проверка типов) должны быть успешно пройдены до начала ревью.
- Если в процессе ревью были оставлены комментарии, разработчик обязан внести правки или аргументированно ответить на них. Повторный запрос на проверку отправляется после устранения всех замечаний.

## API
## 1. Аутентификация
### 1.1 Регистрация v1 (OTP через Redis)
POST (http://localhost/api/v1/auth/register)

Request Body
```json
{
  "email": "user@example.com",
  "password": "StrongPass1"
}
```
Валидация пароля
- минимум 8 символов
- минимум 1 заглавная буква
- минимум 1 цифра

Ответ (RegisterOut)
```json
{
  "message": "Письмо для подтверждения отправлена на почту"
}
```
Логика
1. Создается пользователь (is_active=False)
2. Генерируется OTP-код
3. Код сохраняется в Redis
4. Отправляется письмо с кодом

### 1.2 Подтверждение почты v1
POST (http://localhost/api/v1/auth/verify)

Request Body
```json
{
  "email": "user@example.com",
  "code": "12345"
}
```

Валидация кода
- 5 символов
- только цифры

Ответ (VerifyEmailOut)
```json
{
  "message": "Почта подтверждена"
}
```

Результат
1. Пользователь становится is_active=True
2. Отправляется email об активации бесплатного тарифа
3. Создается подписка в БД

### 1.3 Регистрация v2 (JWT-ссылка)
POST (http://localhost/api/v2/auth/register)

Request Body
```json
{
  "email": "user@example.com",
  "password": "StrongPass1"
}
```

Ответ
```json
{
  "message": "Письмо для подтверждения отправлена на почту"
}
```

Логика
1. Генерируется JWT с user_id
2. Отправляется email со ссылкой подтверждения

### 1.4 Подтверждение почты v2
POST (http://localhost/api/v2/auth/verify?token=JWT_TOKEN)

Query параметры
```
token: str
```
Ответ
```json
{
  "message": "Почта подтверждена"
}
```

Логика
1. Декодируется JWT
2. Пользователь становится is_active=True
3. Отправляется email об активации бесплатного тарифа
4. Создается подписка в БД


### 1.5 Авторизация
POST (http://localhost/api/v1/auth/login)

Request Body
```json
{
  "email": "user@example.com",
  "password": "StrongPass1"
}
```
Ответ
```json
{
  "access_token": "jwt_access",
  "refresh_token": "jwt_refresh",
  "token_type": "Bearer"
}
```

### 1.6 Обновление токенов
POST (http://localhost/api/v1/auth/refresh)

Request Body
```json
{
  "refresh_token": "jwt_refresh"
}
```

Ответ
```json
{
  "access_token": "new_access",
  "refresh_token": "new_refresh",
  "token_type": "Bearer"
}
```
### 1.7 Смена пароля (вводятся старый и новый)
POST (http://localhost:8000/api/v1/auth/password-change)

Request Body
```json
{
  "old_password": "OldPass234!Word",
  "new_password": "NewPas@2sword"
}
```
Ответ
```json
{
  "detail": "Пароль успешно изменен"
}
```

### 1.8 Восстановление пароля по почте (отправка письма с токеном)
POST (http://localhost:8000/api/v1/auth/password-reset/request)

Request Body
```json
{
  "email": "some@gmail.com"
}
```
Ответ
```json
{
  "detail": "Инструкция по восстановлению пароля отправлена на почту"
}
```

### 1.9 Восстановление пароля по почте (подтверждение токена)
POST (http://localhost:8000/api/v1/auth/password-reset/confirm)
Request Body
```
{
  "password": "new!PasSword12",
  "token": "MZsmrboLez2jcVb81ax5zDJrSDhf3J_OX813o_mGoqA"
}
```
Ответ
```json
{
  "detail": "Пароль успешно обновлен"
}
```

### 1.10 Получение данных авторизации
GET (http://localhost:8000/api/v1/auth/me)

Ответ
```json
{
    "is_admin": false,
    "id": "12345678-1234-1234-1234-123456789123"
}
```

## 2. OAuth авторизация

### 2.1 Google
GET (http://localhost/api/v1/auth/google/login)

Ответ:
```json
{
  "url": "https://accounts.google.com/..."
}
```

GET (http://localhost/api/v1/auth/google/callback?code=AUTH_CODE)

Ответ:
```json
{
  "access_token": "...",
  "refresh_token": "...",
  "token_type": "Bearer"
}
```

### 2.2 Yandex

GET (http://localhost/api/v1/auth/yandex/login)
Ответ:
```json
{
  "url": "https://oauth.yandex.ru/..."
}
```

GET (http://localhost/api/v1/auth/yandex/callback?code=AUTH_CODE)
Ответ:
```json
{
  "access_token": "...",
  "refresh_token": "...",
  "token_type": "Bearer"
}
```

## 3. Тарифы

### 3.1 Создание тарифа
POST (http://localhost/api/v1/tariff/)
Request Body
```json
{
  "name": "Pro",
  "description": "Расширенный тариф",
  "price": 199000,
  "period_days": 30,
  "project_limit": 10,
  "room_limit": 50,
  "furniture_regeneration_limit": 1000
}
```
Ограничения
- price ≥ 0
- period_days > 0
- лимиты ≥ 0

Ответ (201 Created)
```json
{
  "id": "uuid",
  "name": "Pro",
  "description": "Расширенный тариф",
  "price": 199000,
  "period_days": 30,
  "project_limit": 10,
  "room_limit": 50,
  "furniture_regeneration_limit": 1000
}
```

### 3.2 Получение списка тарифов
GET (http://localhost/api/v1/tariff/)

Ответ:
```json
[
  {
    "id": "uuid",
    "name": "Free",
    "description": "...",
    "price": 0,
    "period_days": 30,
    "project_limit": 1,
    "room_limit": 3,
    "furniture_regeneration_limit": 10
  }
]
```

### 3.3 Получение тарифа
GET (http://localhost/api/v1/tariff/{tariff_id})
Ответ:
```json
{
    "id": "uuid",
    "name": "Free",
    "description": "...",
    "price": 0,
    "period_days": 30,
    "project_limit": 1,
    "room_limit": 3,
    "furniture_regeneration_limit": 10
  }
```

### 3.4 Обновление тарифа
PATCH (http://localhost/api/v1/tariff/{tariff_id})

Request Body
```json
{
  "price": 149000,
  "project_limit": 20
}
```
Обновляются только переданные поля.

или 

Request Body
```json
{
    "name": "Free",
    "description": "...",
    "price": 0,
    "period_days": 30,
    "project_limit": 1,
    "room_limit": 3,
    "furniture_regeneration_limit": 10
  }
```
Обновляются все переданные поля.

### 3.5 Удаление тарифа
DELETE (http://localhost/api/v1/tariff/{tariff_id})

Ответ: HTTP 204 No Content

## 4. Подписка

### 4.1 Получение активной подписки
GET (http://localhost/api/v1/subscription/my/active)

Authorization: Bearer <access_token>

Ответ (SubscriptionShortRead | null)
```json
{
  "id": "uuid",
  "start_date": "2026-03-01T10:00:00",
  "end_date": "2026-03-31T10:00:00",
  "is_active": true,
  "tariff": {
    "id": "uuid",
    "name": "Pro",
    "description": "...",
    "price": 199000,
    "period_days": 30,
    "project_limit": 10,
    "room_limit": 50,
    "furniture_regeneration_limit": 1000
  }
}
```
