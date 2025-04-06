import shutil

from fastapi import APIRouter, Request, Depends, UploadFile
from fastapi.templating import Jinja2Templates
from app.farmers.router import get_all_farmers, get_farmer_by_id
from app.fields.router import get_all_fields
from app.users.router import get_me
from app.fields.router import get_my_fields

router = APIRouter(prefix='/pages', tags=['Фронтенд'])
templates = Jinja2Templates(directory='app/templates')


@router.get('/fields')
async def get_fields_html(request: Request, fields=Depends(get_all_fields)):
    return templates.TemplateResponse(
        name='fields.html',
        context={'request': request, 'fields': fields}
    )


@router.get('/farmers')
async def get_farmers_html(request: Request, farmers=Depends(get_all_farmers)):
    return templates.TemplateResponse(
        name='farmers.html',
        context={'request': request, 'farmers': farmers}
    )


@router.post('/add_photo')
async def add_farmer_photo(file: UploadFile, img_name: int):
    with open(f"app/static/images/{img_name}.webp", "wb+") as photo_obj:
        shutil.copyfileobj(file.file, photo_obj)


@router.get('/farmers/{farmer_id}')
async def get_farmers_html(request: Request, farmer=Depends(get_farmer_by_id)):
    return templates.TemplateResponse(
        name='farmer.html',
        context={'request': request, 'farmer': farmer}
    )


@router.get('/registration')
async def get_registration_html(request: Request):
    return templates.TemplateResponse(
        name='registration_form.html',
        context={'request': request}
    )


@router.get('/login')
async def get_login_html(request: Request):
    return templates.TemplateResponse(
        name='login_form.html',
        context={'request': request}
    )


@router.get('/profile')
async def get_my_profile(request: Request, profile=Depends(get_me)):
    return templates.TemplateResponse(
        name='profile.html',
        context={'request': request, 'profile': profile}
    )


@router.get('/add_field')
async def add_field_page(request: Request):
    return templates.TemplateResponse(
        'add_field.html',
        {'request': request}
    )


@router.get('/my_fields')
async def get_my_fields_html(
    request: Request,
    fields=Depends(get_my_fields)  # Используем эндпоинт для получения полей текущего пользователя
):
    return templates.TemplateResponse(
        'my_fields.html',
        {'request': request, 'fields': fields}
    )
