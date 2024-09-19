from fastapi import FastAPI, Depends, HTTPException, status, Form
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, User, Service
from passlib.context import CryptContext
from fastapi.templating import Jinja2Templates
from fastapi import Request
from fastapi.responses import RedirectResponse

# App and database setup
app = FastAPI()
engine = create_engine('sqlite:///db.sqlite')
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# For rendering templates
templates = Jinja2Templates(directory="templates")

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# Dependency: get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Password hashing functions
def hash_password(password: str):
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


# Register route
@app.get("/register", response_class=HTMLResponse)
async def get_register(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@app.post("/register")
async def register(
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    hashed_password = hash_password(password)
    user = User(username=username, email=email, hashed_password=hashed_password)
    db.add(user)
    db.commit()
    return {"message": "User registered successfully"}


# Login route
@app.get("/login", response_class=HTMLResponse)
async def get_login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/login")
async def login(
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    return {"message": "Login successful"}


# Home page (show services)
@app.get("/", response_class=HTMLResponse)
async def home(request: Request, db: Session = Depends(get_db)):
    services = db.query(Service).all()
    return templates.TemplateResponse("index.html", {"request": request, "services": services})


# Add service route
@app.get("/add_service", response_class=HTMLResponse)
async def get_add_service(request: Request):
    return templates.TemplateResponse("add_service.html", {"request": request})


@app.post("/add_service")
async def add_service(
    title: str = Form(...),
    description: str = Form(...),
    location: str = Form(...),
    contact: str = Form(...),
    user_id: int = Form(...),  # You would normally get this from a session
    db: Session = Depends(get_db)
):
    service = Service(title=title, description=description, location=location, contact=contact, user_id=user_id)
    db.add(service)
    db.commit()
    #return {"message": "Service added successfully"}
    return RedirectResponse(url="/?message=success", status_code=303)
