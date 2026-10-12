from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from database.db import get_db
from repository import contacts as repository
from schemas.contact import ContactCreate, ContactResponse, ContactUpdate

router = APIRouter(prefix="/contacts", tags=["contacts"])


def _not_found() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Контакт не знайдено",
    )


def _duplicate_email() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail="Контакт з такою електронною адресою вже існує",
    )


@router.post(
    "/",
    response_model=ContactResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Створити контакт",
    responses={409: {"description": "Електронна адреса вже зайнята"}},
)
def create_contact(body: ContactCreate, db: Session = Depends(get_db)):
    try:
        return repository.create(db, body)
    except IntegrityError:
        db.rollback()
        raise _duplicate_email()


@router.get(
    "/",
    response_model=list[ContactResponse],
    summary="Список контактів",
)
def read_contacts(db: Session = Depends(get_db)):
    return repository.get_all(db)


@router.get(
    "/search",
    response_model=list[ContactResponse],
    summary="Пошук контактів",
    description="Необов'язкові query-параметри first_name, last_name та email. Кілька параметрів звужують вибірку.",
)
def search_contacts(
    first_name: str | None = Query(default=None, description="Ім'я або його частина"),
    last_name: str | None = Query(default=None, description="Прізвище або його частина"),
    email: str | None = Query(default=None, description="Електронна адреса або її частина"),
    db: Session = Depends(get_db),
):
    return repository.search(db, first_name=first_name, last_name=last_name, email=email)


@router.get(
    "/birthdays",
    response_model=list[ContactResponse],
    summary="Дні народження на найближчі 7 днів",
)
def read_upcoming_birthdays(db: Session = Depends(get_db)):
    return repository.get_upcoming_birthdays(db)


@router.get(
    "/{contact_id}",
    response_model=ContactResponse,
    summary="Отримати контакт за ідентифікатором",
    responses={404: {"description": "Контакт не знайдено"}},
)
def read_contact(contact_id: int, db: Session = Depends(get_db)):
    contact = repository.get_by_id(db, contact_id)
    if contact is None:
        raise _not_found()
    return contact


@router.put(
    "/{contact_id}",
    response_model=ContactResponse,
    summary="Оновити контакт",
    responses={
        404: {"description": "Контакт не знайдено"},
        409: {"description": "Електронна адреса вже зайнята"},
    },
)
def update_contact(
    contact_id: int,
    body: ContactUpdate,
    db: Session = Depends(get_db),
):
    contact = repository.get_by_id(db, contact_id)
    if contact is None:
        raise _not_found()
    try:
        return repository.update(db, contact, body)
    except IntegrityError:
        db.rollback()
        raise _duplicate_email()


@router.delete(
    "/{contact_id}",
    response_model=ContactResponse,
    summary="Видалити контакт",
    responses={404: {"description": "Контакт не знайдено"}},
)
def delete_contact(contact_id: int, db: Session = Depends(get_db)):
    contact = repository.get_by_id(db, contact_id)
    if contact is None:
        raise _not_found()
    payload = ContactResponse.model_validate(contact)
    repository.remove(db, contact)
    return payload
