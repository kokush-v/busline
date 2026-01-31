# 🚌 Bus Reservation System: Технічна Специфікація

## 1. Технологічний Стек

- **Core:** Python 3.10+, FastAPI
- **Database:** PostgreSQL, SQLAlchemy 2.0 (Async), Alembic
- **Task Queue / Scheduling:** APScheduler (для очищення броней), `BackgroundTasks` (для PDF)
- **Storage:** AWS S3 (через `aioboto3`)
- **PDF:** ReportLab
- **Payments:** Mock (етап 1) -> Plaid (етап 2)

---

## 2. База Даних (Schema Design)

Ми переходимо від простого лічильника місць до обліку **конкретних місць**.

### ENUMS (Статуси)

```python
class OrderStatus(str, enum.Enum):
    PENDING = "pending"       # Бронь створена, таймер тікає (30 хв)
    PROCESSING = "processing" # Користувач почав оплату (Plaid), чекаємо вебхук
    PAID = "paid"             # Оплата успішна, квиток згенеровано
    FAILED = "failed"         # Помилка оплати
    CANCELLED = "cancelled"   # Час вичерпано або скасовано вручну

class SeatStatus(str, enum.Enum):
    FREE = "free"             # Вільне
    LOCKED = "locked"         # Тимчасово утримується (Order PENDING/PROCESSING)
    SOLD = "sold"             # Продано (Order PAID)

```

### MODELS (Код для `models.py`)

```python
class Order(Base):
    __tablename__ = 'orders'
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=True)

    status: Mapped[OrderStatus] = mapped_column(Enum(OrderStatus), default=OrderStatus.PENDING, nullable=False)
    total_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)

    # Plaid Integration
    external_payment_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    payment_method: Mapped[str | None] = mapped_column(String(50), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    tickets: Mapped[List["Ticket"]] = relationship("Ticket", back_populates="order", cascade="all, delete-orphan")

class Seat(Base):
    __tablename__ = 'seats'
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    trip_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('trips.id', ondelete='CASCADE'))
    position_index: Mapped[int] = mapped_column(Integer, nullable=False) # Номер місця (1, 2...)
    status: Mapped[SeatStatus] = mapped_column(Enum(SeatStatus), default=SeatStatus.FREE, nullable=False)

class Ticket(Base):
    __tablename__ = 'tickets'
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('orders.id', ondelete='CASCADE'))
    seat_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('seats.id'), unique=True)

    # Passenger Data
    passenger_name: Mapped[str] = mapped_column(String(100))
    passenger_email: Mapped[str | None] = mapped_column(String(100))
    passenger_age: Mapped[int | None] = mapped_column(Integer)

    # Route & Meta
    trip_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('trips.id'))
    start_stop_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('stops.id'))
    finish_stop_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('stops.id'))
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    pdf_url: Mapped[str | None] = mapped_column(String(500))

    order: Mapped["Order"] = relationship("Order", back_populates="tickets")

```

---

## 3. API Endpoints (Специфікація)

### 1. Перегляд місць

- **GET** `/trips/{trip_id}/seats`
- **Response:** Список місць `{id, position_index, status}`. Це дозволяє фронтенду намалювати схему автобуса.

### 2. Бронювання (Reserve) - **Core Logic**

- **POST** `/trips/{trip_id}/reserve`
- **Input:** Список `{seat_id, passenger_name, passenger_age, ...}`
- **Process (Transaction):**

1. `SELECT ... FOR UPDATE` для вибраних `seat_id`.
2. Перевірка: якщо хоча б одне місце != `FREE` -> `409 Conflict`.
3. `UPDATE seats SET status = 'locked'`.
4. Створення `Order` (Status: `PENDING`, Expires: `Now + 30 min`).
5. Створення `Ticket` записів.

- **Output:** `{order_id, status: "pending", expires_at: "..."}`.

### 3. Список замовлень

- **GET** `/orders`
- **Auth:** Тільки авторизовані. Повертає історію замовлень поточного юзера.

### 4. Деталі замовлення

- **GET** `/orders/{order_id}`
- **Auth:** Власник замовлення (User або Anon).
- **Output:** Повна інфа, включаючи статус оплати та посилання на PDF (якщо є).

### 5. Оплата (Pay)

- **POST** `/orders/{order_id}/pay`
- **Process:**

1. Перевірка таймера: якщо `expires_at < now` -> `400 Bad Request`.
2. **Mock (зараз):** Відразу ставимо `PAID`.
3. **Plaid (майбутнє):** Отримуємо Link Token, ставимо статус `PROCESSING`.
4. Якщо `PAID` -> Тригер фонової задачі (Generate PDF).

---

## 4. Фонова Логіка (Background Workers)

### А. Генерація квитка (Event-driven)

Запускається при переході в статус `PAID`.

1. **ReportLab:** Створити PDF у пам'яті (BytesIO). Вставити QR, дані пасажира.
2. **S3:** Завантажити файл.
3. **DB:** Оновити `ticket.pdf_url`.
4. **Email:** (Опціонально) Відправити лист.

### Б. Прибиральник (Scheduler / Cron)

Запускається **кожну 1 хвилину**.

1. Знайти всі `Order`, де:

- `status == PENDING` (Увага: `PROCESSING` не чіпаємо, гроші можуть ще йти).
- `expires_at < Current Time`.

2. **Дія:**

- `Order.status` -> `CANCELLED`.
- `Seat.status` (для всіх квитків у замовленні) -> `FREE`.

---

## 5. План дій (Step-by-Step)

1. [ ] **DB Setup:** Додати моделі в код, створити та застосувати міграції Alembic.
2. [ ] **Data Seeding:** Реалізувати логіку, щоб при створенні `Trip` автоматично створювались записи в таблиці `seats`.
3. [ ] **API Reserve:** Реалізувати `/reserve` з `SELECT FOR UPDATE` (найскладніша частина).
4. [ ] **API Pay:** Реалізувати заглушку оплати та перевірку таймера.
5. [ ] **Cleanup Worker:** Налаштувати APScheduler для скасування старих броней.
6. [ ] **PDF & S3:** Підключити генерацію файлів.
