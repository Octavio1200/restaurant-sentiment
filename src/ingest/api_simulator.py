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
    ("Sushi Nami", "Monterrey"),
    ("Pasta & Co.", "Guadalajara"),
    ("Burger Station", "Puebla"),
    ("Café Aurora", "Querétaro"),
]

TEXTS_POS = [
    "Excelente servicio y la comida estuvo deliciosa, volveré pronto.",
    "Muy buena atención, el sabor fue increíble y las porciones perfectas.",
    "Me encantó el lugar, todo limpio y el staff muy amable.",
]

TEXTS_NEG = [
    "La comida llegó fría y el servicio fue muy lento.",
    "Mala experiencia, el personal fue grosero y la comida no tenía sabor.",
    "Demasiado caro para lo que ofrecen, no lo recomiendo.",
]

TEXTS_NEU = [
    "El lugar está bien, nada extraordinario pero cumple.",
    "La comida estuvo normal, el servicio aceptable.",
    "Una experiencia promedio, podría mejorar.",
]


def generate_reviews(n: int, seed: Optional[int] = None) -> List[Review]:
    if seed is not None:
        random.seed(seed)

    reviews = []
    now = datetime.utcnow()

    for _ in range(n):
        name, city = random.choice(RESTAURANTS)
        stars = random.choices([1, 2, 3, 4, 5], weights=[8, 10, 20, 30, 32])[0]

        if stars >= 4:
            text = random.choice(TEXTS_POS)
        elif stars <= 2:
            text = random.choice(TEXTS_NEG)
        else:
            text = random.choice(TEXTS_NEU)

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
