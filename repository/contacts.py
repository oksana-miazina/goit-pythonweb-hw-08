from datetime import date, timedelta

from sqlalchemy import extract, or_, select
from sqlalchemy.orm import Session

from database.models import Contact
from schemas.contact import ContactCreate, ContactUpdate

BIRTHDAY_WINDOW_DAYS = 7


def create(db: Session, data: ContactCreate) -> Contact:
    contact = Contact(**data.model_dump())
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact


def get_all(db: Session) -> list[Contact]:
    stmt = select(Contact).order_by(Contact.id)
    return list(db.scalars(stmt).all())


def get_by_id(db: Session, contact_id: int) -> Contact | None:
    return db.get(Contact, contact_id)


def update(db: Session, contact: Contact, data: ContactUpdate) -> Contact:
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(contact, key, value)
    db.commit()
    db.refresh(contact)
    return contact


def remove(db: Session, contact: Contact) -> None:
    db.delete(contact)
    db.commit()


def _like_pattern(value: str) -> str:
    escaped = value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    return f"%{escaped}%"


def search(
    db: Session,
    first_name: str | None = None,
    last_name: str | None = None,
    email: str | None = None,
) -> list[Contact]:
    stmt = select(Contact)
    if first_name:
        stmt = stmt.where(Contact.first_name.ilike(_like_pattern(first_name), escape="\\"))
    if last_name:
        stmt = stmt.where(Contact.last_name.ilike(_like_pattern(last_name), escape="\\"))
    if email:
        stmt = stmt.where(Contact.email.ilike(_like_pattern(email), escape="\\"))
    stmt = stmt.order_by(Contact.id)
    return list(db.scalars(stmt).all())


def get_upcoming_birthdays(db: Session, days: int = BIRTHDAY_WINDOW_DAYS) -> list[Contact]:
    today = date.today()
    end = today + timedelta(days=days)
    birthday_key = extract("month", Contact.birthday) * 100 + extract("day", Contact.birthday)
    start_key = today.month * 100 + today.day
    end_key = end.month * 100 + end.day
    if start_key <= end_key:
        condition = birthday_key.between(start_key, end_key)
    else:
        condition = or_(birthday_key >= start_key, birthday_key <= end_key)
    stmt = select(Contact).where(condition).order_by(Contact.id)
    return list(db.scalars(stmt).all())
