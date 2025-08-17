"""API endpointy pre autentifikáciu používateľa."""

from litestar import get, post, Response, status_codes
import logging
from litestar.response import Redirect
from litestar import Request
from litestar.di import Provide
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
##from litestar.datastructures import Form
from litestar.params import Body


from app.models import User, Category, Word, User
from app.schemas import UserCreate, UserLogin, TokenResponse, ExcelImportResponse
from app.auth.service import hash_password, verify_password
from app.auth.security import create_access_token
from app.db import get_db_session
import logging
from litestar.status_codes import HTTP_201_CREATED, HTTP_409_CONFLICT, HTTP_500_INTERNAL_SERVER_ERROR, HTTP_303_SEE_OTHER
from starlette.status import HTTP_303_SEE_OTHER, HTTP_500_INTERNAL_SERVER_ERROR, HTTP_200_OK
from jinja2 import Environment, FileSystemLoader
import os
import traceback
from litestar import MediaType

# Add this near your other imports
from pathlib import Path
import random

# Import Flash for flash messages
from litestar.plugins.flash import flash, get_flashes

# Update your template configuration
template_dir = Path(__file__).parent / "templates"
env = Environment(loader=FileSystemLoader(template_dir))
env.globals["get_flashes"] = get_flashes



@post("/register", status_code=HTTP_201_CREATED)
async def register_user(
    data: UserCreate,
    db_session: AsyncSession = Provide(get_db_session),
) -> Response[TokenResponse]:
    """Registruje nového používateľa."""
    try:
        # Overí, či e-mail už existuje
        result = await db_session.execute(select(User).where(User.email == data.email))
        if result.scalar_one_or_none():
            logging.warning(f"Registration attempt with existing email: {data.email}")
            return Response(
                status_code=HTTP_409_CONFLICT,
                content={"detail": "Email už existuje"},
            )

        # Vytvorenie a uloženie používateľa
        new_user = User(
            email=data.email,
            hashed_password=hash_password(data.password),
        )
        db_session.add(new_user)
        await db_session.commit()

        # Vytvorenie JWT tokenu
        token = create_access_token({"sub": data.email})
        return Response(
            content=TokenResponse(access_token=token).dict(),
            media_type="application/json",
            status_code=HTTP_201_CREATED,
        )

    except Exception as e:
        logging.error(f"Error in register_user: {e}")
        return Response(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal Server Error"},
        )


@post("/login")
async def login_user(
    request: Request,
    db_session: AsyncSession = Provide(get_db_session),
) -> Response:
    """Overí prihlasovacie údaje a vráti token alebo redirect."""
    try:
        form = await request.form()
        email = form.get("email")
        password = form.get("password")
        logging.info(f"Login attempt with email: {email}, password present: {password is not None}")
        
        result = await db_session.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        logging.info(f"User found: {user is not None}")
        
        if not user or not verify_password(password, user.hashed_password):
            logging.info("Invalid credentials")
            flash(request, "Nesprávny email alebo heslo", "error")
            return Redirect(path="/login", status_code=status_codes.HTTP_303_SEE_OTHER)
        
        flash(request, "Úspešne ste sa prihlásili.", "success")
        logging.info("Flash message set in login_user")
        response = Redirect(path="/dashboard", status_code=HTTP_303_SEE_OTHER)
        response.set_cookie(
            key="user_email",
            value=email,
            max_age=3600,
            httponly=True,
            secure=True,
            samesite="lax",
            path="/",
        )
        return response
    
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        logging.error(traceback.format_exc())
        flash(request, "Vnútorná chyba serveru", "error")
        return Redirect(path="/login", status_code=status_codes.HTTP_303_SEE_OTHER)

@get("/register")
async def register_page() -> Response:
    """Serve the register.html page."""
    import os
    from litestar import MediaType, status_codes, Response

    file_path = os.path.join(os.path.dirname(__file__), "templates", "register.html")
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            html_content = f.read()
        return Response(content=html_content, media_type=MediaType.HTML)
    except FileNotFoundError:
        return Response(
            status_code=status_codes.HTTP_404_NOT_FOUND,
            content="Register page not found",
        )

@get("/login")
async def login_page() -> Response:
    """Serve the login.html page."""
    import os
    from litestar import MediaType, status_codes, Response

    file_path = os.path.join(os.path.dirname(__file__), "templates", "login.html")
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            html_content = f.read()
        return Response(content=html_content, media_type=MediaType.HTML)
    except FileNotFoundError:
        return Response(
            status_code=status_codes.HTTP_404_NOT_FOUND,
            content="Login page not found",
        )


# Removed import of get_flashed_messages due to ImportError in current Litestar version

@get("/dashboard")
async def dashboard_page(
    request: Request,
    db_session: AsyncSession = Provide(get_db_session),
) -> Response:
    try:
        # Get email from cookies
        user_email = request.cookies.get("user_email")
        if not user_email:
            return Redirect(path="/", status_code=HTTP_303_SEE_OTHER)

        # Get user from DB
        user_stmt = select(User).where(User.email == user_email)
        user = await db_session.scalar(user_stmt)
        if not user:
            return Redirect(path="/", status_code=HTTP_303_SEE_OTHER)

        # Get user's categories
        category_stmt = select(Category).where(Category.user_id == user.id)
        categories = (await db_session.scalars(category_stmt)).all()

        # Render dashboard with categories
        template = env.get_template("dashboard.html")
        html_content = template.render(
            email=user_email,
            categories=categories,
            request=request
        )

        return Response(
            content=html_content,
            media_type=MediaType.HTML,
            status_code=HTTP_200_OK
        )

    except Exception as e:
        logging.error(f"Error in dashboard_page: {e}")
        logging.error(traceback.format_exc())
        return Response(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal Server Error"},
        )
    

@get("/", name="homepage")
async def homepage(request: Request) -> Response:
    """Serve the homepage with login/register links."""
    try:
        # Check if user is logged in (has cookie)
        if request.cookies.get("user_email"):
            return Redirect(path="/dashboard", status_code=HTTP_303_SEE_OTHER)
            
        template = env.get_template("home.html")
        html_content = template.render()
        return Response(
            content=html_content,
            media_type=MediaType.HTML,
            status_code=status_codes.HTTP_200_OK
        )
    except Exception as e:
        logging.error(f"Error loading homepage: {e}")
        # Fallback to simple response if template fails
        html_content = """
        <!DOCTYPE html>
        <html>
        <body>
            <h1>Vitajte</h1>
            <a href="/login">Prihlásiť sa</a> | 
            <a href="/register">Registrovať sa</a>
        </body>
        </html>
        """
        return Response(
            content=html_content,
            media_type=MediaType.HTML,
            status_code=status_codes.HTTP_200_OK
        )

@get("/logout")
async def logout_user(request: Request) -> Response:
    """Odhlási používateľa a presmeruje na homepage."""
    try:
        # Create response with redirect
        response = Redirect(path="/", status_code=HTTP_303_SEE_OTHER)
        
        # Expire the cookie by setting max_age to 0
        response.delete_cookie(
            key="user_email",
            path="/",
        )
        
        # Add flash message
        flash(request, "Úspešne ste sa odhlásili.", "success")
        logging.info("User logged out successfully")
        return response
        
    except Exception as e:
        logging.error(f"Logout failed: {str(e)}")
        logging.error(traceback.format_exc())
        flash(request, "Pri odhlasovaní nastala chyba", "error")
        return Redirect(path="/")
    
##### vocabulary app specific endpoints #####
#############################################

async def get_current_user_email(request: Request) -> str | Redirect:
    user_email = request.cookies.get("user_email")
    if not user_email:
        return Redirect(path="/", status_code=303)
    return user_email

@post("/category")
async def create_category(
    request: Request,
    db_session: AsyncSession = Provide(get_db_session)
) -> Redirect:
    form_data = await request.form()
    name = form_data.get("name")

    user_email = await get_current_user_email(request)
    if isinstance(user_email, Redirect):
        return user_email

    user = await db_session.scalar(select(User).where(User.email == user_email))
    if not user:
        return Redirect(path="/", status_code=303)

    category = Category(name=name, user_id=user.id)
    db_session.add(category)
    await db_session.commit()

    flash(request, "Kategória bola úspešne vytvorená.", "success")
    logging.info("Flash message set in create_category")
    return Redirect(path="/dashboard", status_code=303)

@post("/word")
async def add_word(
    request: Request,
    db_session: AsyncSession = Provide(get_db_session)
) -> Redirect:
    form_data = await request.form()
    sk = form_data.get("sk")
    en = form_data.get("en")
    category_id = form_data.get("category_id")

    user_email = await get_current_user_email(request)
    if isinstance(user_email, Redirect):
        return user_email

    word = Word(sk=sk, en=en, category_id=int(category_id), level=1)
    db_session.add(word)
    await db_session.commit()

    flash(request, "Slovíčko bolo úspešne pridané.", "success")
    logging.info("Flash message set in add_word")
    return Redirect(path="/dashboard", status_code=303)


@post("/word/{word_id:int}/level")
async def change_word_level(
    word_id: int,
    request: Request,
    db_session: AsyncSession = Provide(get_db_session)
) -> Redirect:
    form_data = await request.form()
    level = int(form_data.get("level", 1))
    
    word = await db_session.get(Word, word_id)
    if not word:
        flash(request, "Slovo neexistuje.", "error")
        return Redirect(path="/words", status_code=303)
    
    word.level = level
    await db_session.commit()
    
    flash(request, "Úroveň slova bola úspešne zmenená.", "success")
    return Redirect(path="/words", status_code=303)

@post("/word/{word_id:int}/delete")
async def delete_word(
    word_id: int,
    request: Request,
    db_session: AsyncSession = Provide(get_db_session)
) -> Redirect:
    word = await db_session.get(Word, word_id)
    if not word:
        flash(request, "Slovo neexistuje.", "error")
        return Redirect(path="/words", status_code=303)
    
    await db_session.delete(word)
    await db_session.commit()
    
    flash(request, "Slovo bolo úspešne odstránené.", "success")
    return Redirect(path="/words", status_code=303)

@get("/test-flash")
async def test_flash(request: Request) -> Response:
    flash(request, "Testovacia flash správa", "info")
    return Redirect(path="/dashboard", status_code=HTTP_303_SEE_OTHER)


@get("/test/{category_id:int}/{level:int}")
async def test_words(
    request: Request,
    category_id: int,
    level: int,
    db_session: AsyncSession = Provide(get_db_session)
) -> Response:
    user_email = await get_current_user_email(request)
    if isinstance(user_email, Redirect):
        return user_email

    result = await db_session.execute(
        select(Word).where(Word.category_id == category_id, Word.level == level)
    )
    words = result.scalars().all()
    random.shuffle(words)
    return Response(content=[{"id": w.id, "sk": w.sk, "en": w.en, "level": w.level} for w in words])

@get("/test")
async def test_page(
    request: Request,
    category_id: int = 1,
    level: int = 1,
    db_session: AsyncSession = Provide(get_db_session)
) -> Response:
    """Zobrazí testovaciu stránku pre slovíčka."""
    try:
        user_email = request.cookies.get("user_email")
        if not user_email:
            return Redirect(path="/", status_code=HTTP_303_SEE_OTHER)

        user_stmt = select(User).where(User.email == user_email)
        user = await db_session.scalar(user_stmt)
        if not user:
            return Redirect(path="/", status_code=HTTP_303_SEE_OTHER)

        category = await db_session.get(Category, category_id)
        if not category or category.user_id != user.id:
            flash(request, "Kategória neexistuje alebo k nej nemáte prístup.", "error")
            return Redirect(path="/dashboard", status_code=HTTP_303_SEE_OTHER)

        word_stmt = select(Word).where(Word.category_id == category_id, Word.level == level)
        words = (await db_session.scalars(word_stmt)).all()
        
        if not words:
            flash(request, "Žiadne slovíčka na tejto úrovni!", "error")
            return Redirect(path="/dashboard", status_code=HTTP_303_SEE_OTHER)

        template = env.get_template("test.html")
        html_content = template.render(
            email=user_email,
            category=category,
            level=level,
            total_words=len(words),
            request=request
        )

        return Response(
            content=html_content,
            media_type=MediaType.HTML,
            status_code=HTTP_200_OK
        )

    except Exception as e:
        logging.error(f"Error in test_page: {e}")
        logging.error(traceback.format_exc())
        return Response(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal Server Error"},
        )


@get("/words")
async def words_page(
    request: Request,
    db_session: AsyncSession = Provide(get_db_session),
) -> Response:
    try:
        # Get email from cookies
        user_email = request.cookies.get("user_email")
        if not user_email:
            return Redirect(path="/", status_code=HTTP_303_SEE_OTHER)

        # Get user from DB
        user_stmt = select(User).where(User.email == user_email)
        user = await db_session.scalar(user_stmt)
        if not user:
            return Redirect(path="/", status_code=HTTP_303_SEE_OTHER)

        # Get user's categories with their words
        category_stmt = select(Category).where(Category.user_id == user.id)
        categories = (await db_session.scalars(category_stmt)).all()
        
        # Fetch words for each category
        categories_with_words = []
        for category in categories:
            word_stmt = select(Word).where(Word.category_id == category.id)
            words = (await db_session.scalars(word_stmt)).all()
            categories_with_words.append({
                "category": category,
                "words": words
            })

        # Render words page
        template = env.get_template("words.html")
        html_content = template.render(
            email=user_email,
            categories_with_words=categories_with_words,
            request=request
        )

        return Response(
            content=html_content,
            media_type=MediaType.HTML,
            status_code=HTTP_200_OK
        )

    except Exception as e:
        logging.error(f"Error in words_page: {e}")
        logging.error(traceback.format_exc())
        return Response(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal Server Error"},
        )

@get("/category/{category_id:int}")
async def category_detail_page(
    category_id: int,
    request: Request,
    db_session: AsyncSession = Provide(get_db_session),
) -> Response:
    try:
        user_email = request.cookies.get("user_email")
        if not user_email:
            return Redirect(path="/", status_code=HTTP_303_SEE_OTHER)

        user_stmt = select(User).where(User.email == user_email)
        user = await db_session.scalar(user_stmt)
        if not user:
            return Redirect(path="/", status_code=HTTP_303_SEE_OTHER)

        category = await db_session.get(Category, category_id)
        if not category or category.user_id != user.id:
            flash(request, "Kategória neexistuje alebo k nej nemáte prístup.", "error")
            return Redirect(path="/dashboard", status_code=HTTP_303_SEE_OTHER)

        word_stmt = select(Word).where(Word.category_id == category_id)
        words = (await db_session.scalars(word_stmt)).all()

        template = env.get_template("category_detail.html")
        html_content = template.render(
            email=user_email,
            category=category,
            words=words,
            request=request
        )

        return Response(
            content=html_content,
            media_type=MediaType.HTML,
            status_code=HTTP_200_OK
        )

    except Exception as e:
        logging.error(f"Error in category_detail_page: {e}")
        logging.error(traceback.format_exc())
        return Response(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal Server Error"},
        )

@post("/category/{category_id:int}/edit")
async def edit_category(
    category_id: int,
    request: Request,
    db_session: AsyncSession = Provide(get_db_session)
) -> Redirect:
    """Edit a category name."""
    try:
        form_data = await request.form()
        new_name = form_data.get("name")

        if not new_name or not new_name.strip():
            flash(request, "Názov kategórie nemôže byť prázdny.", "error")
            return Redirect(path=f"/category/{category_id}", status_code=303)

        user_email = await get_current_user_email(request)
        if isinstance(user_email, Redirect):
            return user_email

        user = await db_session.scalar(select(User).where(User.email == user_email))
        if not user:
            return Redirect(path="/", status_code=303)

        category = await db_session.get(Category, category_id)
        if not category or category.user_id != user.id:
            flash(request, "Kategória neexistuje alebo k nej nemáte prístup.", "error")
            return Redirect(path="/dashboard", status_code=303)

        old_name = category.name
        category.name = new_name.strip()
        await db_session.commit()

        flash(request, f"Názov kategórie bol úspešne zmenený z '{old_name}' na '{new_name}'.", "success")
        return Redirect(path=f"/category/{category_id}", status_code=303)

    except Exception as e:
        logging.error(f"Error editing category: {e}")
        flash(request, "Chyba pri úprave kategórie.", "error")
        return Redirect(path=f"/category/{category_id}", status_code=303)

@post("/category/{category_id:int}/delete")
async def delete_category(
    category_id: int,
    request: Request,
    db_session: AsyncSession = Provide(get_db_session)
) -> Redirect:
    """Delete a category and all its associated words."""
    try:
        user_email = await get_current_user_email(request)
        if isinstance(user_email, Redirect):
            return user_email

        user = await db_session.scalar(select(User).where(User.email == user_email))
        if not user:
            return Redirect(path="/", status_code=303)

        category = await db_session.get(Category, category_id)
        if not category or category.user_id != user.id:
            flash(request, "Kategória neexistuje alebo k nej nemáte prístup.", "error")
            return Redirect(path="/dashboard", status_code=303)

        # Delete all words in the category first (due to foreign key constraints)
        from sqlalchemy import delete
        await db_session.execute(delete(Word).where(Word.category_id == category_id))
        
        # Delete the category
        await db_session.delete(category)
        await db_session.commit()

        flash(request, f"Kategória '{category.name}' bola úspešne odstránená.", "success")
        return Redirect(path="/dashboard", status_code=303)

    except Exception as e:
        logging.error(f"Error deleting category: {e}")
        logging.error(traceback.format_exc())
        flash(request, "Chyba pri odstraňovaní kategórie.", "error")

@post("/test-delete/{category_id:int}")
async def test_delete_category(
    category_id: int,
    request: Request,
    db_session: AsyncSession = Provide(get_db_session)
) -> Response:
    """Test delete category endpoint."""
    try:
        category = await db_session.get(Category, category_id)
        if not category:
            return Response(status_code=404, content={"detail": "Category not found"})
        return Response(status_code=200, content={"detail": "Category found"})
    except Exception as e:
        logging.error(f"Error in test_delete_category: {e}")
        return Response(status_code=500, content={"detail": "Internal Server Error"})

@post("/category/{category_id:int}/import-excel")
async def import_excel_words(
    category_id: int,
    request: Request,
    db_session: AsyncSession = Provide(get_db_session)
) -> Response[ExcelImportResponse]:
    """Import slovíčok z Excel súboru do kategórie."""
    try:
        # Kontrola prihlásenia
        user_email = request.cookies.get("user_email")
        if not user_email:
            flash(request, "Nie ste prihlásený", "error")
            return Redirect(path="/", status_code=HTTP_303_SEE_OTHER)

        # Kontrola kategórie
        category = await db_session.get(Category, category_id)
        if not category:
            return Response(
                status_code=status_codes.HTTP_404_NOT_FOUND,
                content=ExcelImportResponse(
                    success=False,
                    message="Kategória neexistuje",
                    imported_count=0,
                    skipped_count=0,
                    errors=["Kategória neexistuje"]
                )
            )

        # Kontrola vlastníctva kategórie
        user = await db_session.scalar(select(User).where(User.email == user_email))
        if not user or category.user_id != user.id:
            return Response(
                status_code=status_codes.HTTP_403_FORBIDDEN,
                content=ExcelImportResponse(
                    success=False,
                    message="Nemáte prístup k tejto kategórii",
                    imported_count=0,
                    skipped_count=0,
                    errors=["Nemáte prístup k tejto kategórii"]
                )
            )

        # Spracovanie uploadovaného súboru
        from litestar.datastructures import UploadFile
        
        form = await request.form()
        excel_file: UploadFile = form.get("excel_file")
        
        if not excel_file:
            return Response(
                status_code=status_codes.HTTP_400_BAD_REQUEST,
                content=ExcelImportResponse(
                    success=False,
                    message="Žiadny súbor nebol nahraný",
                    imported_count=0,
                    skipped_count=0,
                    errors=["Žiadny súbor nebol nahraný"]
                )
            )

        excel_file: UploadFile = form.get("excel_file")
        if not excel_file.filename.endswith(('.xlsx', '.xls')):
            return Response(
                status_code=status_codes.HTTP_400_BAD_REQUEST,
                content=ExcelImportResponse(
                    success=False,
                    message="Nepodporovaný formát súboru. Použite .xlsx alebo .xls",
                    imported_count=0,
                    skipped_count=0,
                    errors=["Nepodporovaný formát súboru"]
                )
            )

        # Spracovanie obsahu súboru
        content = await excel_file.read()
        
        # Kontrola veľkosti súboru (max 2MB)
        if len(content) > 2 * 1024 * 1024:  # 2MB
            return Response(
                status_code=status_codes.HTTP_400_BAD_REQUEST,
                content=ExcelImportResponse(
                    success=False,
                    message="Súbor je príliš veľký. Maximálna veľkosť je 2MB",
                    imported_count=0,
                    skipped_count=0,
                    errors=["Súbor je príliš veľký"]
                )
            )

        # Spracovanie Excel súboru
        import openpyxl
        from io import BytesIO

        try:
            workbook = openpyxl.load_workbook(BytesIO(content))
            sheet = workbook.active
            
            imported_count = 0
            skipped_count = 0
            errors = []
            
            # Preskočiť header ak existuje
            start_row = 1
            first_row = [cell.value for cell in sheet[1]]
            if first_row and any(isinstance(cell, str) and cell.lower() in ['slovicko', 'preklad', 'word', 'translation'] for cell in first_row):
                start_row = 2
            
            for row_idx, row in enumerate(sheet.iter_rows(min_row=start_row, values_only=True), start=start_row):
                try:
                    if len(row) < 2:
                        errors.append(f"Riadok {row_idx}: Nedostatočný počet stĺpcov")
                        continue
                    
                    slovicko = str(row[0]).strip() if row[0] else None
                    preklad = str(row[1]).strip() if row[1] else None
                    
                    if not slovicko or not preklad:
                        errors.append(f"Riadok {row_idx}: Chýbajúce slovíčko alebo preklad")
                        skipped_count += 1
                        continue
                    
                    # Kontrola duplikátov
                    existing_word = await db_session.scalar(
                        select(Word).where(
                            Word.sk == slovicko,
                            Word.en == preklad,
                            Word.category_id == category_id
                        )
                    )
                    
                    if existing_word:
                        skipped_count += 1
                        continue
                    
                    # Vytvorenie nového slovíčka
                    new_word = Word(
                        sk=slovicko,
                        en=preklad,
                        category_id=category_id,
                        level=1  # Predvolená úroveň
                    )
                    db_session.add(new_word)
                    imported_count += 1
                    
                except Exception as e:
                    errors.append(f"Riadok {row_idx}: {str(e)}")
                    skipped_count += 1
            
            await db_session.commit()
            
            flash(request, f"Import dokončený! Importovaných: {imported_count}, Preskočených: {skipped_count}", "success")
            return Redirect(path=f"/category/{category_id}", status_code=HTTP_303_SEE_OTHER)

        except Exception as e:
            await db_session.rollback()
            return Response(
                status_code=status_codes.HTTP_400_BAD_REQUEST,
                content=ExcelImportResponse(
                    success=False,
                    message=f"Chyba pri spracovaní Excel súboru: {str(e)}",
                    imported_count=0,
                    skipped_count=0,
                    errors=[str(e)]
                )
            )

    except Exception as e:
        logging.error(f"Error in import_excel_words: {e}")
        logging.error(traceback.format_exc())
        return Response(
            status_code=status_codes.HTTP_500_INTERNAL_SERVER_ERROR,
            content=ExcelImportResponse(
                success=False,
                message="Interná chyba servera",
                imported_count=0,
                skipped_count=0,
                errors=["Interná chyba servera"]
            )
        )
