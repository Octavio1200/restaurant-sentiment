from fastapi import FastAPI, Query
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta
import random
import uuid

app = FastAPI(title="Restaurant Reviews API Simulator", version="0.1.0")

class Review(BaseModel):
    review_id: str
    business_id: str
    restaurant_name: str
    city: str
    stars: int
    text: str
    created_at: str


RESTAURANTS = [
    ("La Taquería Central", "CDMX"),
    ("Tacos El Guero", "CDMX"),
    ("Café Roma", "CDMX"),
    ("Ramen Shibuya", "CDMX"),
    ("Mariscos Don Neto", "CDMX"),
    ("Sushi Nami", "Monterrey"),
    ("Asador del Norte", "Monterrey"),
    ("Café Obispado", "Monterrey"),
    ("Pizza Sierra Madre", "Monterrey"),
    ("Tortas La Estación", "Monterrey"),
    ("Pasta & Co.", "Guadalajara"),
    ("Birria La Tradición", "Guadalajara"),
    ("Café Chapultepec", "Guadalajara"),
    ("Sushi Andares", "Guadalajara"),
    ("Tacos Providencia", "Guadalajara"),
    ("Burger Station", "Puebla"),
    ("Mole & Más", "Puebla"),
    ("Cemitas La Casa", "Puebla"),
    ("Café Zócalo", "Puebla"),
    ("Antojitos Angelópolis", "Puebla"),
    ("Café Aurora", "Querétaro"),
    ("Tacos La Alameda", "Querétaro"),
    ("Sushi Juriquilla", "Querétaro"),
    ("Pasta Centro", "Querétaro"),
    ("La Parrilla QRO", "Querétaro"),
]


ADJ_POS = ["deliciosa", "increíble", "excelente", "espectacular", "muy buena"]
ADJ_NEG = ["fría", "insípida", "mala", "terrible", "decepcionante"]
SERVICE_POS = ["muy amable", "rápido", "atento", "excelente", "cordial"]
SERVICE_NEG = ["lento", "grosero", "desorganizado", "pésimo", "muy tardado"]
ITEMS = ["tacos", "ramen", "pizza", "café", "postre", "hamburguesa", "birria", "mariscos", "pasta"]
EXTRAS = ["volveré pronto", "lo recomiendo", "no regreso", "no lo recomiendo", "podría mejorar", "fue una sorpresa"]

def make_text(stars: int) -> str:
    item = random.choice(ITEMS)
    extra = random.choice(EXTRAS)

    if stars >= 4:
        return f"El {item} estuvo {random.choice(ADJ_POS)} y el servicio fue {random.choice(SERVICE_POS)}; {extra}."
    elif stars <= 2:
        return f"El {item} estuvo {random.choice(ADJ_NEG)} y el servicio fue {random.choice(SERVICE_NEG)}; {extra}."
    else:
        return f"El {item} estuvo normal y el servicio fue aceptable; {extra}."



def generate_reviews(n: int, seed: Optional[int] = None) -> List[Review]:
    if seed is not None:
        random.seed(seed)

    reviews = []
    now = datetime.utcnow()

    for _ in range(n):
        name, city = random.choice(RESTAURANTS)
        stars = random.choices([1, 2, 3, 4, 5], weights=[8, 10, 20, 30, 32])[0]

        text = make_text(stars) + f" (ticket:{random.randint(1000,9999)})"

        created_at = (now - timedelta(minutes=random.randint(1, 20000))).isoformat()

        reviews.append(
            Review(
                review_id=str(uuid.uuid4()),
                business_id=str(uuid.uuid4()),
                restaurant_name=name,
                city=city,
                stars=stars,
                text=text,
                created_at=created_at,
            )
        )
    return reviews


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/reviews", response_model=List[Review])
def get_reviews(
    limit: int = Query(50, ge=1, le=500),
    seed: Optional[int] = None
):

    return generate_reviews(limit, seed)
