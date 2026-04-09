from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional, List, Dict, Any, Literal
import os
import sys
import json
from datetime import datetime
import logging
from dotenv import load_dotenv
import requests

# Load environment variables from .env file
load_dotenv()

try:
    from booking import get_booking_payload
    BOOKING_MODULE_AVAILABLE = True
except ImportError:
    BOOKING_MODULE_AVAILABLE = False
    get_booking_payload = None  # type: ignore

from destination_spots import (
    describe_landmark_visit,
    describe_meal_stop,
    destination_label,
    landmarks_for,
    normalize_city_key,
    pick_landmark,
)

def party_size_from_request(request: "TravelRequest") -> int:
    """Headcount used to scale trip totals. Budget tiers scale per person with trip length."""
    ctx = request.travelContext or {}
    style = request.travelStyle
    if style == "Solo Travel":
        return 1
    if style == "Couple Getaway":
        return 2
    if style == "Family Trip":
        adults = max(1, int(ctx.get("adults", 2) or 2))
        kids = max(0, int(ctx.get("kids", 0) or 0))
        return max(1, adults + kids)
    if style == "Group Adventure":
        return max(1, int(ctx.get("groupSize", 4) or 4))
    if style == "Business Trip":
        return max(1, int(ctx.get("partySize", 1) or 1))
    if style == "Backpacking":
        return max(1, int(ctx.get("partySize", 1) or 1))
    if style == "Luxury Travel":
        return max(1, int(ctx.get("partySize", 2) or 2))
    return 1


# Reference trip length for tier labels (tier names imply rough spend over ~3 days per person)
_BUDGET_REF_DAYS = 3


def _per_person_trip_total(budget_string: str, duration: int) -> int:
    """Scale per-person trip total linearly with duration vs a 3-day reference."""
    days = max(1, int(duration))
    if "Budget (Under ₹10,000)" in budget_string:
        ref = 8000
    elif "Moderate (₹10,000 - ₹25,000)" in budget_string:
        ref = 18000
    elif "Luxury (₹25,000 - ₹50,000)" in budget_string:
        ref = 40000
    elif "Premium (Above ₹50,000)" in budget_string:
        ref = 75000
    else:
        ref = 15000
    return int(round(ref * days / _BUDGET_REF_DAYS))


# Budget parsing function
def parse_budget(budget_string: str, duration: int, party_size: int = 1) -> dict:
    """
    Parse budget string and calculate detailed budget breakdown.

    Tier labels are calibrated for ~3 days per person; amounts scale with trip length and party size.

    Args:
        budget_string: Budget string from frontend (e.g., "Luxury (₹25,000 - ₹50,000)")
        duration: Trip duration in days
        party_size: Number of travelers (minimum 1)

    Returns:
        dict: Budget breakdown with total, daily, and category amounts
    """
    party_size = max(1, int(party_size))
    days = max(1, int(duration))

    per_person_total = _per_person_trip_total(budget_string, days)
    total_budget = per_person_total * party_size
    daily_budget = total_budget // days

    breakdown = {
        "total_budget": total_budget,
        "per_person_total": per_person_total,
        "party_size": party_size,
        "trip_days": days,
        "daily_budget": daily_budget,
        "accommodation": int(total_budget * 0.35),
        "food": int(total_budget * 0.25),
        "transport": int(total_budget * 0.20),
        "activities": int(total_budget * 0.15),
        "shopping": int(total_budget * 0.05),
    }

    return breakdown

# Add the current directory to path to import travel module
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from travel import (
        destination_research_task, accommodation_task, transportation_task,
        activities_task, dining_task, itinerary_task, chatbot_task,
        run_task
    )
    TRAVEL_MODULE_AVAILABLE = True
except ImportError:
    TRAVEL_MODULE_AVAILABLE = False
    print("Travel module not available")

class ExternalSignals(BaseModel):
    weather_impact_score: float
    is_holiday: bool
    event_intensity: float

class LocationCrowdData(BaseModel):
    location_id: str
    current_level: Literal["Low", "Medium", "High"]
    prediction_trend: List[int]  # 24h trend
    best_time_to_visit: str
    signals: ExternalSignals

class CrowdPredictionResponse(BaseModel):
    location: str
    date: str
    data: LocationCrowdData

# Initialize FastAPI app
app = FastAPI(
    title="Travelian API",
    description="AI-powered travel planning API for India",
    version="1.0.0"
)

# CORS middleware
allowed_origins = [
    origin.strip()
    for origin in os.getenv(
        "ALLOWED_ORIGINS",
        "http://localhost:3000,http://localhost:3001,http://localhost:3002",
    ).split(",")
    if origin.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class TravelRequest(BaseModel):
    origin: str = Field(min_length=2, max_length=120)
    destination: str = Field(min_length=2, max_length=120)
    startDate: str
    endDate: str
    duration: int = Field(ge=1, le=60)
    budget: str = Field(min_length=3, max_length=80)
    travelStyle: str = Field(min_length=2, max_length=80)
    interests: List[str] = Field(min_length=1)
    specialRequirements: Optional[str] = ""
    travelContext: Optional[Dict[str, Any]] = Field(default_factory=dict)

    @field_validator("origin", "destination", "budget", "travelStyle", mode="before")
    @classmethod
    def strip_strings(cls, value: str) -> str:
        if isinstance(value, str):
            return value.strip()
        return value

    @field_validator("interests")
    @classmethod
    def validate_interests(cls, value: List[str]) -> List[str]:
        cleaned = [item.strip() for item in value if isinstance(item, str) and item.strip()]
        if not cleaned:
            raise ValueError("At least one interest is required")
        return cleaned

    @model_validator(mode="after")
    def validate_dates_and_duration(self):
        try:
            start = datetime.strptime(self.startDate, "%Y-%m-%d").date()
            end = datetime.strptime(self.endDate, "%Y-%m-%d").date()
        except ValueError as exc:
            raise ValueError("Dates must be in YYYY-MM-DD format") from exc

        if end < start:
            raise ValueError("endDate must be on or after startDate")

        expected_duration = (end - start).days
        if expected_duration <= 0:
            raise ValueError("Trip duration must be at least 1 day")

        if self.duration != expected_duration:
            raise ValueError(f"duration must match date range ({expected_duration})")

        ctx = self.travelContext or {}
        if self.travelStyle == "Family Trip":
            adults = int(ctx.get("adults", 0)) if str(ctx.get("adults", "")).strip() else 0
            kids = int(ctx.get("kids", 0)) if str(ctx.get("kids", "")).strip() else 0
            if adults < 1:
                raise ValueError("Family Trip requires at least 1 adult")
            if kids < 0:
                raise ValueError("kids cannot be negative")
        elif self.travelStyle == "Group Adventure":
            group_size = int(ctx.get("groupSize", 0)) if str(ctx.get("groupSize", "")).strip() else 0
            if group_size < 3:
                raise ValueError("Group Adventure requires group size of at least 3")
        elif self.travelStyle == "Couple Getaway":
            if (ctx.get("adults") is not None) and int(ctx.get("adults", 0)) != 2:
                raise ValueError("Couple Getaway should have 2 adults")

        return self

class TravelResponse(BaseModel):
    itinerary: Dict[str, Any]
    map: Optional[Dict[str, Any]] = None
    budget: Optional[dict] = None

class ChatbotRequest(BaseModel):
    message: str = Field(min_length=1, max_length=1500)
    history: Optional[List[Dict[str, str]]] = Field(default_factory=list)

class ChatbotResponse(BaseModel):
    response: str
    history: List[Dict[str, str]]


class BookingSearchRequest(BaseModel):
    origin: str = Field(min_length=1, max_length=120)
    destination: str = Field(min_length=1, max_length=120)
    startDate: str
    endDate: str
    adults: int = Field(default=1, ge=1, le=9)

    @field_validator("origin", "destination", mode="before")
    @classmethod
    def strip_booking_cities(cls, value: str) -> str:
        if isinstance(value, str):
            return value.strip()
        return value

    @model_validator(mode="after")
    def validate_booking_dates(self):
        try:
            start = datetime.strptime(self.startDate, "%Y-%m-%d").date()
            end = datetime.strptime(self.endDate, "%Y-%m-%d").date()
        except ValueError as exc:
            raise ValueError("Dates must be in YYYY-MM-DD format") from exc
        if end < start:
            raise ValueError("endDate must be on or after startDate")
        return self


class HealthResponse(BaseModel):
    status: str
    timestamp: str
    travel_module: bool
    chatbot_module: bool
    version: str
    uptime: float
    environment: str

class ErrorDetail(BaseModel):
    code: str
    message: str
    details: Optional[Any] = None

class ErrorResponse(BaseModel):
    error: ErrorDetail

class ItineraryItem(BaseModel):
    time: str
    title: str
    description: str
    cost: int = Field(ge=0)
    duration: str
    distanceKm: Optional[float] = None
    entryFeeInr: Optional[int] = Field(
        default=None,
        ge=0,
        description="Indicative monument/site entry in INR (0 = free); omit for meals/transport.",
    )
    type: Literal["activity", "transport", "meal", "accommodation", "entertainment"] = "activity"
    category: str = "Activities & Sightseeing"

class DayPlan(BaseModel):
    day: int = Field(ge=1)
    title: str
    totalCost: int = Field(ge=0)
    location: str
    items: List[ItineraryItem]

class StructuredItinerary(BaseModel):
    title: str
    duration: str
    importantNotes: List[str]
    days: List[DayPlan] = Field(min_length=1)

class RoutePoint(BaseModel):
    name: str
    lat: float
    lon: float

class MapData(BaseModel):
    origin: RoutePoint
    destination: RoutePoint
    routeUrl: str
    googleMapsDirectionsUrl: str
    openStreetMapDirectionsUrl: str
    openStreetMapEmbedUrl: str

# Health check endpoint
@app.get("/health", response_model=HealthResponse)
async def health_check():
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        travel_module=TRAVEL_MODULE_AVAILABLE,
        chatbot_module=TRAVEL_MODULE_AVAILABLE,
        version="1.0.0",
        uptime=0.0,  # This would be calculated in a real app
        environment="development"
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(_: Request, exc: HTTPException):
    payload = ErrorResponse(
        error=ErrorDetail(
            code="http_error",
            message=str(exc.detail),
            details={"status_code": exc.status_code},
        )
    )
    return JSONResponse(status_code=exc.status_code, content=payload.model_dump())

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_: Request, exc: RequestValidationError):
    details = jsonable_encoder(exc.errors())
    payload = ErrorResponse(
        error=ErrorDetail(
            code="validation_error",
            message="Request validation failed",
            details=details,
        )
    )
    return JSONResponse(status_code=422, content=payload.model_dump())

@app.exception_handler(Exception)
async def generic_exception_handler(_: Request, exc: Exception):
    logging.exception("Unhandled server error")
    payload = ErrorResponse(
        error=ErrorDetail(code="internal_error", message="Internal server error")
    )
    return JSONResponse(status_code=500, content=payload.model_dump())

def geocode_city(city_name: str) -> Optional[RoutePoint]:
    try:
        response = requests.get(
            "https://nominatim.openstreetmap.org/search",
            params={"q": city_name, "format": "json", "limit": 1},
            timeout=3,
            headers={"User-Agent": "Travelian/1.0 (travel-planner)"},
        )
        response.raise_for_status()
        data = response.json()
        if not data:
            return None
        item = data[0]
        return RoutePoint(
            name=city_name,
            lat=float(item["lat"]),
            lon=float(item["lon"]),
        )
    except Exception:
        logging.warning("Failed to geocode city: %s", city_name)
        return None

def build_map_data(origin_city: str, destination_city: str) -> Optional[MapData]:
    origin = geocode_city(origin_city)
    destination = geocode_city(destination_city)
    if not origin or not destination:
        return None

    left = min(origin.lon, destination.lon) - 0.5
    right = max(origin.lon, destination.lon) + 0.5
    bottom = min(origin.lat, destination.lat) - 0.5
    top = max(origin.lat, destination.lat) + 0.5

    route_url = (
        "https://www.openstreetmap.org/directions"
        f"?engine=fossgis_osrm_car&route={origin.lat}%2C{origin.lon}%3B{destination.lat}%2C{destination.lon}"
    )
    google_url = (
        "https://www.google.com/maps/dir/"
        f"{origin.lat},{origin.lon}/{destination.lat},{destination.lon}"
    )
    osm_url = route_url
    embed_url = (
        "https://www.openstreetmap.org/export/embed.html"
        f"?bbox={left},{bottom},{right},{top}"
        "&layer=mapnik"
        f"&marker={origin.lat},{origin.lon}"
    )
    return MapData(
        origin=origin,
        destination=destination,
        routeUrl=route_url,
        googleMapsDirectionsUrl=google_url,
        openStreetMapDirectionsUrl=osm_url,
        openStreetMapEmbedUrl=embed_url,
    )

def build_structured_itinerary(
    request: TravelRequest,
    budget_info: Dict[str, int],
    raw_itinerary: str,
    map_data: Optional[MapData] = None,
) -> StructuredItinerary:
    day_count = request.duration
    daily_cost = budget_info["daily_budget"]
    per_item_cost = max(daily_cost // 6, 1)
    days: List[DayPlan] = []
    interest_focus = request.interests[:3] if request.interests else ["Culture & Heritage"]
    travel_ctx = request.travelContext or {}
    style = request.travelStyle

    # Style-aware defaults
    start_time = "07:30 AM"
    evening_time = "08:00 PM"
    activity_duration = "2.5 hours"
    notes: List[str] = []

    if style == "Family Trip":
        kids = int(travel_ctx.get("kids", 0) or 0)
        kid_age_group = str(travel_ctx.get("kidAgeGroup", "Mixed"))
        start_time = "08:30 AM"
        evening_time = "07:00 PM"
        activity_duration = "2 hours"
        notes.append(f"Family pacing enabled: kids={kids}, age group={kid_age_group}.")
    elif style == "Business Trip":
        business_days = int(travel_ctx.get("businessDays", 2) or 2)
        priority = str(travel_ctx.get("priority", "Balanced"))
        notes.append(f"Business-first scheduling applied for {business_days} day(s), priority={priority}.")
    elif style == "Backpacking":
        start_time = "06:45 AM"
        activity_duration = "3 hours"
        notes.append("Backpacking mode: early starts, longer outdoor blocks, budget transfers.")
    elif style == "Luxury Travel":
        start_time = "09:00 AM"
        evening_time = "09:00 PM"
        activity_duration = "2 hours"
        notes.append("Luxury mode: fewer transitions, premium dining, comfort-first routing.")
    elif style == "Couple Getaway":
        notes.append(f"Couple mode: occasion={travel_ctx.get('occasion', 'Leisure')}.")
    elif style == "Group Adventure":
        notes.append(f"Group mode: size={travel_ctx.get('groupSize', 4)}, fitness={travel_ctx.get('fitnessLevel', 'Moderate')}.")
    elif style == "Solo Travel":
        notes.append(f"Solo mode: pace={travel_ctx.get('pace', 'Balanced')}, nightlife={travel_ctx.get('nightlifeInterest', 'Moderate')}.")

    intercity_distance = None
    if map_data:
        # Approximate straight-line distance; useful as transfer context.
        lat1, lon1 = map_data.origin.lat, map_data.origin.lon
        lat2, lon2 = map_data.destination.lat, map_data.destination.lon
        from math import radians, sin, cos, sqrt, atan2
        r = 6371.0
        dlat = radians(lat2 - lat1)
        dlon = radians(lon2 - lon1)
        a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        intercity_distance = round(r * c, 1)

    city_key = normalize_city_key(request.destination)
    dest_display = destination_label(request.destination)
    landmarks = landmarks_for(request.destination)
    budget_str = request.budget

    def interest_category(slot: int) -> str:
        tag = interest_focus[min(slot, len(interest_focus) - 1)]
        t = tag.lower()
        if "culture" in t or "heritage" in t:
            return "Culture & Heritage"
        if "food" in t or "dining" in t:
            return "Food & Dining"
        if "shop" in t:
            return "Shopping & Markets"
        return "Activities & Sightseeing"

    for day_index in range(1, day_count + 1):
        # Keep local mobility under 100km/day once destination touring is underway.
        local_day_distances = [4 + day_index, 12 + (day_index % 4), 6, 18 + (day_index % 5), 10, 8]
        local_total = sum(local_day_distances)
        if local_total > 100:
            scale = 100 / local_total
            local_day_distances = [max(round(x * scale, 1), 2) for x in local_day_distances]

        if day_index == 1:
            items: List[ItineraryItem] = []
            if intercity_distance:
                # Estimate transport cost at ~₹10/km (mix of rail/road) or a fraction of per-item cost
                transport_cost = int(intercity_distance * 10)
                items.append(
                    ItineraryItem(
                        time="07:00 AM",
                        title=f"Depart from {request.origin}",
                        description=(
                            f"**Route:** {request.origin} → {request.destination}\n\n"
                            f"**Straight-line distance (approx.):** {intercity_distance} km — road or rail will differ.\n\n"
                            f"**Plan:** Boarding buffer, ID, and tickets (phone + backup printout).\n\n"
                            f"**On arrival:** Head toward **{dest_display}** city centre / your stay."
                        ),
                        cost=transport_cost,
                        duration="3-6 hours",
                        distanceKm=intercity_distance,
                        type="transport",
                        category="Transportation",
                    )
                )
            else:
                items.append(
                    ItineraryItem(
                        time=start_time,
                        title=f"Morning — settle in {dest_display}",
                        description=(
                            f"**Plan:** Breakfast near stay, light walk, and confirm any **online monument slots** for the next days.\n\n"
                            f"**Ask locally:** Nearest safe walking pocket toward the old core / waterfront."
                        ),
                        cost=max(per_item_cost // 2, 1),
                        duration="1 hour",
                        distanceKm=round(local_day_distances[0], 1),
                        type="meal",
                        category="Food & Dining",
                    )
                )
            lm_ori = pick_landmark(landmarks, 0)
            lunch_title, lunch_desc, lunch_cost = describe_meal_stop(
                city_key,
                "lunch",
                "12:30 PM",
                "1.5 hours",
                local_day_distances[0],
                dest_display,
                budget_str,
            )
            dinner_title, dinner_desc, dinner_cost = describe_meal_stop(
                city_key,
                "dinner",
                "06:30 PM",
                "1.5 hours",
                local_day_distances[2],
                dest_display,
                budget_str,
            )
            items.extend(
                [
                    ItineraryItem(
                        time="12:30 PM",
                        title=f"Hotel check-in & lunch — {dest_display}",
                        description=lunch_desc,
                        cost=lunch_cost,
                        duration="1.5 hours",
                        distanceKm=round(local_day_distances[0], 1),
                        type="meal",
                        category="Food & Dining",
                    ),
                    ItineraryItem(
                        time="03:00 PM",
                        title=lm_ori.name,
                        description=describe_landmark_visit(
                            lm_ori, "03:00 PM", "2 hours", dest_display
                        ),
                        cost=lm_ori.entry_inr,
                        duration="2 hours",
                        distanceKm=round(lm_ori.distance_km, 1),
                        type="activity",
                        category=interest_category(0),
                        entryFeeInr=lm_ori.entry_inr,
                    ),
                    ItineraryItem(
                        time="06:30 PM",
                        title=dinner_title,
                        description=dinner_desc,
                        cost=dinner_cost,
                        duration="1.5 hours",
                        distanceKm=round(local_day_distances[2], 1),
                        type="meal",
                        category="Food & Dining",
                    ),
                ]
            )
        else:
            spot_off = 1 + (day_index - 2) * 3
            lm_a = pick_landmark(landmarks, spot_off)
            lm_b = pick_landmark(landmarks, spot_off + 1)
            lm_e = pick_landmark(landmarks, spot_off + 2)

            br_title, br_desc, br_cost = describe_meal_stop(
                city_key,
                "breakfast",
                start_time,
                "45 mins",
                local_day_distances[0],
                dest_display,
                budget_str,
            )
            lu_title, lu_desc, lu_cost = describe_meal_stop(
                city_key,
                "lunch",
                "12:30 PM",
                "1 hour",
                local_day_distances[2],
                dest_display,
                budget_str,
            )
            di_title, di_desc, di_cost = describe_meal_stop(
                city_key,
                "dinner",
                evening_time,
                "1.5 hours",
                local_day_distances[5],
                dest_display,
                budget_str,
            )

            business_focus_block = None
            if style == "Business Trip":
                business_days = int(travel_ctx.get("businessDays", 2) or 2)
                if day_index <= business_days:
                    business_focus_block = ItineraryItem(
                        time="09:00 AM",
                        title=f"Business meetings — {dest_display}",
                        description=(
                            f"**Venue cluster:** CBD / business district toward **{dest_display}** core.\n\n"
                            f"**Plan:** Minimise cross-town hops; use hotel lobby or coworking between slots.\n\n"
                            f"**Backup:** Offline maps, power bank, and a 4G failover."
                        ),
                        cost=0,
                        duration="3 hours",
                        distanceKm=round(local_day_distances[1], 1),
                        type="activity",
                        category="Transportation",
                    )

            morning_activity = (
                business_focus_block
                if business_focus_block
                else ItineraryItem(
                    time="09:00 AM",
                    title=lm_a.name,
                    description=describe_landmark_visit(
                        lm_a, "09:00 AM", activity_duration, dest_display
                    ),
                    cost=lm_a.entry_inr,
                    duration=activity_duration,
                    distanceKm=round(lm_a.distance_km, 1),
                    type="activity",
                    category=interest_category(0),
                    entryFeeInr=lm_a.entry_inr,
                )
            )

            items = [
                ItineraryItem(
                    time=start_time,
                    title=br_title,
                    description=br_desc,
                    cost=br_cost,
                    duration="45 mins",
                    distanceKm=round(local_day_distances[0], 1),
                    type="meal",
                    category="Food & Dining",
                ),
                morning_activity,
                ItineraryItem(
                    time="12:30 PM",
                    title=lu_title,
                    description=lu_desc,
                    cost=lu_cost,
                    duration="1 hour",
                    distanceKm=round(local_day_distances[2], 1),
                    type="meal",
                    category="Food & Dining",
                ),
                ItineraryItem(
                    time="02:00 PM",
                    title=lm_b.name,
                    description=describe_landmark_visit(
                        lm_b, "02:00 PM", activity_duration, dest_display
                    ),
                    cost=lm_b.entry_inr,
                    duration=activity_duration,
                    distanceKm=round(lm_b.distance_km, 1),
                    type="activity",
                    category=interest_category(1),
                    entryFeeInr=lm_b.entry_inr,
                ),
                ItineraryItem(
                    time="05:30 PM",
                    title=f"{lm_e.name} — evening",
                    description=describe_landmark_visit(
                        lm_e, "05:30 PM", "1.5 hours", dest_display
                    ),
                    cost=lm_e.entry_inr,
                    duration="1.5 hours",
                    distanceKm=round(lm_e.distance_km, 1),
                    type="entertainment",
                    category=interest_category(2),
                    entryFeeInr=lm_e.entry_inr,
                ),
                ItineraryItem(
                    time=evening_time,
                    title=di_title,
                    description=di_desc,
                    cost=di_cost,
                    duration="1.5 hours",
                    distanceKm=round(local_day_distances[5], 1),
                    type="meal",
                    category="Food & Dining",
                ),
            ]

        days.append(
            DayPlan(
                day=day_index,
                title=f"Day {day_index} in {request.destination}",
                totalCost=daily_cost,
                location=request.destination,
                items=items,
            )
        )
    structured = StructuredItinerary(
        title=f"{request.duration}-Day Itinerary for {request.destination}",
        duration=f"{request.duration} days",
        importantNotes=[
            f"Budget level selected: {request.budget}",
            f"Travel style: {request.travelStyle}",
            f"Interests: {', '.join(request.interests)}",
            "Routing rule applied: once local sightseeing starts, daily local travel is capped at <=100 km.",
            "Indicative only: spot names, entry fees, and distances from city centre are planning hints — confirm on official sites.",
            *notes,
        ],
        days=days,
    )
    if raw_itinerary and len(raw_itinerary.strip()) > 20:
        structured.importantNotes.append("AI recommendation text was generated and can be shown in advanced view.")
    return structured

def run_groq_prompt(prompt: str, system_prompt: str = "") -> str:
    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key:
        return ""

    model = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {groq_api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": model,
                "messages": messages,
                "temperature": 0.4,
            },
            timeout=12,
        )
        response.raise_for_status()
        payload = response.json()
        return payload["choices"][0]["message"]["content"].strip()
    except Exception:
        logging.exception("Groq request failed")
        return ""

# Travel planning endpoint
@app.post(
    "/travel/plan",
    response_model=TravelResponse,
    responses={422: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
)
async def plan_travel(request: TravelRequest):
    if not TRAVEL_MODULE_AVAILABLE:
        raise HTTPException(status_code=500, detail="Travel module not available")
    
    try:
        party_size = party_size_from_request(request)
        budget_info = parse_budget(request.budget, request.duration, party_size)

        input_context = (
            f"Travel Request Details:\n"
            f"Origin: {request.origin}\n"
            f"Destination: {request.destination}\n"
            f"Duration: {request.duration} days\n"
            f"Party size: {party_size} traveler(s)\n"
            f"Budget tier (per person, scales with {request.duration} day trip): {request.budget}\n"
            f"Total trip budget (whole group): ₹{budget_info['total_budget']:,}\n"
            f"Per-person budget (estimated): ₹{budget_info['per_person_total']:,}\n"
            f"Daily group budget (avg): ₹{budget_info['daily_budget']:,}\n"
            f"Budget Breakdown: Accommodation ₹{budget_info['accommodation']:,}, Food ₹{budget_info['food']:,}, Transport ₹{budget_info['transport']:,}, Activities ₹{budget_info['activities']:,}\n"
            f"Travel Style: {request.travelStyle}\n"
            f"Travel Context: {json.dumps(request.travelContext or {})}\n"
            f"Preferences/Interests: {', '.join(request.interests)}\n"
            f"Special Requirements: {request.specialRequirements}\n"
        )
        
        raw_itinerary = "Unable to generate itinerary"
        use_ai_itinerary = os.getenv("USE_AI_ITINERARY", "false").lower() == "true"
        if use_ai_itinerary:
            # Prefer Groq when configured; fall back to Gemini if Groq is unavailable.
            groq_result = run_groq_prompt(
                prompt=input_context,
                system_prompt=(
                    "You are a travel planner. Return concise, practical, day-by-day "
                    "recommendations focused on timings, costs, and logistics."
                ),
            )
            if groq_result:
                raw_itinerary = groq_result
            else:
                api_key = os.getenv("GEMINI_API_KEY")
                try:
                    ai_result = run_task(itinerary_task, input_context, api_key)
                    if ai_result and not str(ai_result).startswith("⚠️"):
                        raw_itinerary = str(ai_result)
                    else:
                        logging.warning("AI itinerary generation returned warning response; using fallback itinerary.")
                except Exception:
                    logging.exception("AI itinerary generation failed; using fallback itinerary.")

        map_data = build_map_data(request.origin, request.destination)
        structured_itinerary = build_structured_itinerary(request, budget_info, raw_itinerary, map_data)
        
        return TravelResponse(
            itinerary=structured_itinerary.model_dump(),
            map=map_data.model_dump() if map_data else None,
            budget=budget_info,
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logging.exception("Error planning travel")
        raise HTTPException(status_code=500, detail=f"Error planning travel: {str(e)}")

# Chatbot endpoint
@app.post("/chatbot/ask", response_model=ChatbotResponse)
async def ask_chatbot(request: ChatbotRequest):
    if not TRAVEL_MODULE_AVAILABLE:
        raise HTTPException(status_code=500, detail="Chatbot module not available")
    
    try:
        chat_history = request.history or []
        history_text = "\n".join(
            f"{item.get('role', 'user')}: {item.get('content', '')}" for item in chat_history[-10:]
        )
        chat_input = (
            f"Conversation so far:\n{history_text}\n\n"
            f"User message: {request.message}"
            if history_text
            else request.message
        )
        response = run_groq_prompt(
            prompt=chat_input,
            system_prompt="You are a helpful India travel assistant. Keep responses practical and concise.",
        )
        if not response:
            api_key = os.getenv("GEMINI_API_KEY")
            response = run_task(chatbot_task, chat_input, api_key)
        
        # Update history
        new_history = request.history.copy() if request.history else []
        new_history.append({"role": "user", "content": request.message})
        new_history.append({"role": "assistant", "content": response})
        
        return ChatbotResponse(
            response=response,
            history=new_history
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logging.exception("Error processing chatbot request")
        raise HTTPException(status_code=500, detail=f"Error processing chatbot request: {str(e)}")


@app.post("/bookings/search")
async def search_bookings(request: BookingSearchRequest):
    """Partner booking links + optional Amadeus live flight/hotel offers (see env.example)."""
    if not BOOKING_MODULE_AVAILABLE or not get_booking_payload:
        raise HTTPException(status_code=500, detail="Booking module not available")
    try:
        payload = get_booking_payload(
            request.origin,
            request.destination,
            request.startDate,
            request.endDate,
            request.adults,
        )
        return JSONResponse(content=jsonable_encoder(payload))
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logging.exception("Booking search failed")
        raise HTTPException(status_code=500, detail=f"Booking search failed: {str(e)}")


# ==========================================
# TRIPSYNC: MOCK DATA & MATCHING ENDPOINT
# ==========================================

MOCK_GROUPS: List[Dict[str, Any]] = [
    {
        "group_id": "GRP-1001", "admin_id": "USR-882", "member_ids": ["USR-882", "USR-104", "USR-999"], "max_capacity": 6,
        "destination": "Goa", "dates": {"start": "2026-11-10", "end": "2026-11-15"}, "budget_range": {"min": 15000, "max": 25000}, "status": "OPEN",
    },
    {
        "group_id": "GRP-1002", "admin_id": "USR-411", "member_ids": ["USR-411", "USR-002"], "max_capacity": 4,
        "destination": "Jaipur", "dates": {"start": "2026-12-01", "end": "2026-12-05"}, "budget_range": {"min": 10000, "max": 20000}, "status": "OPEN",
    },
    {
        "group_id": "GRP-1003", "admin_id": "USR-777", "member_ids": ["USR-777"], "max_capacity": 8,
        "destination": "Manali", "dates": {"start": "2026-10-15", "end": "2026-10-22"}, "budget_range": {"min": 8000, "max": 18000}, "status": "OPEN",
    },
    {
        "group_id": "GRP-1004", "admin_id": "USR-333", "member_ids": ["USR-333", "USR-444", "USR-555", "USR-666"], "max_capacity": 8,
        "destination": "Kerala", "dates": {"start": "2026-08-10", "end": "2026-08-20"}, "budget_range": {"min": 25000, "max": 50000}, "status": "OPEN",
    }
]

@app.get("/groups/search")
async def search_groups(destination: str, start_date: str, end_date: str, budget_min: int, budget_max: int):
    try:
        req_start = datetime.strptime(start_date, "%Y-%m-%d").timestamp()
        req_end = datetime.strptime(end_date, "%Y-%m-%d").timestamp()
        req_duration = req_end - req_start
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD.")

    if req_duration <= 0:
        raise HTTPException(status_code=400, detail="End date must be after start date.")

    matched_groups = []
    
    # We will relax the exact destination matching slightly purely for mock demonstration purposes 
    # if the user searches for something we don't have, we'll just inject a dummy group for their destination!

    has_exact_dest = any(g["destination"].lower() == destination.lower() for g in MOCK_GROUPS)
    dynamic_groups = list(MOCK_GROUPS)
    if not has_exact_dest:
        dynamic_groups.append({
            "group_id": f"GRP-DYN-{len(dynamic_groups)+1}",
            "admin_id": "USR-NEW",
            "member_ids": ["USR-NEW"],
            "max_capacity": 5,
            "destination": destination.title(),
            "dates": {"start": start_date, "end": end_date},
            "budget_range": {"min": budget_min, "max": budget_max},
            "status": "OPEN"
        })

    for group in dynamic_groups:
        if group["destination"].lower() != destination.lower():
            continue
        
        if len(group["member_ids"]) >= group["max_capacity"] or group["status"] != "OPEN":
            continue
        
        grp_start = datetime.strptime(group["dates"]["start"], "%Y-%m-%d").timestamp()
        grp_end = datetime.strptime(group["dates"]["end"], "%Y-%m-%d").timestamp()
        
        overlap_start = max(req_start, grp_start)
        overlap_end = min(req_end, grp_end)
        overlap_duration = overlap_end - overlap_start
        
        date_overlap_percentage = (overlap_duration / req_duration) * 100 if overlap_duration > 0 else 0
        
        overlap_min = max(budget_min, group["budget_range"]["min"])
        overlap_max = min(budget_max, group["budget_range"]["max"])
        
        overlap_spread = overlap_max - overlap_min
        req_spread = budget_max - budget_min
        
        if req_spread == 0:
            budget_overlap_percentage = 100 if overlap_spread >= 0 else 0
        else:
            budget_overlap_percentage = (overlap_spread / req_spread) * 100 if overlap_spread > 0 else 0
            
        if date_overlap_percentage < 75: date_overlap_percentage = 85
        if budget_overlap_percentage < 75: budget_overlap_percentage = 90
        
        overall_score = round((date_overlap_percentage + budget_overlap_percentage) / 2)
        
        matched_groups.append({
            **group,
            "matchScore": overall_score,
            "slotsLeft": group["max_capacity"] - len(group["member_ids"])
        })
        
    matched_groups.sort(key=lambda x: x["matchScore"], reverse=True)
    return {"groups": matched_groups}

# ==========================================
# CROWD PREDICTION ENGINE
# ==========================================
import random

def generate_crowd_data(location_id: str, target_date: str = None) -> LocationCrowdData:
    rng = random.Random(sum(ord(c) for c in location_id) + (len(target_date) if target_date else 0))
    
    is_holiday = rng.choice([True, False, False, False])
    weather_score = rng.uniform(0.1, 1.0)
    event_intensity = rng.uniform(0.0, 1.0)
    
    TRENDS = [
        # 0: Mid-day peak 
        [5, 5, 5, 5, 5, 10, 20, 40, 70, 90, 100, 95, 85, 75, 60, 50, 40, 30, 20, 15, 10, 5, 5, 5],
        # 1: Evening peak
        [10, 5, 5, 5, 5, 5, 10, 15, 20, 25, 30, 35, 40, 50, 60, 75, 90, 100, 95, 85, 60, 40, 25, 15],
        # 2: Morning & Evening peak
        [5, 5, 5, 5, 10, 25, 60, 90, 100, 85, 60, 40, 35, 30, 40, 55, 80, 95, 85, 60, 40, 20, 10, 5]
    ]
    trend_index = sum(ord(c) for c in location_id) % 3
    base_trend = TRENDS[trend_index]
    
    # Add slight random noise using the RNG so it still looks organic but follows the identical shape
    trend = [min(100, max(5, int(val * rng.uniform(0.9, 1.1)))) for val in base_trend]
        
    current_val = trend[12]
    if current_val < 40:
        current_level = "Low"
    elif current_val < 75:
        current_level = "Medium"
    else:
        current_level = "High"
        
    daylight_hours = [(h, trend[h]) for h in range(7, 19)]
    best_hour, _ = min(daylight_hours, key=lambda x: x[1])
    am_pm = "AM" if best_hour < 12 else "PM"
    display_hour = best_hour if best_hour <= 12 else best_hour - 12
    if display_hour == 0: display_hour = 12
    
    return LocationCrowdData(
        location_id=location_id,
        current_level=current_level,
        prediction_trend=trend,
        best_time_to_visit=f"Best at {display_hour} {am_pm}",
        signals=ExternalSignals(
            weather_impact_score=round(weather_score, 2),
            is_holiday=is_holiday,
            event_intensity=round(event_intensity, 2)
        )
    )

@app.get("/api/crowd/status/{location_id}", response_model=LocationCrowdData)
async def get_crowd_status(location_id: str):
    return generate_crowd_data(location_id)

@app.get("/api/crowd/forecast", response_model=CrowdPredictionResponse)
async def get_crowd_forecast(location: str, date: str):
    data = generate_crowd_data(location, date)
    return CrowdPredictionResponse(location=location, date=date, data=data)

@app.get("/api/crowd/recommendations")
async def get_crowd_recommendations(status: str = "low"):
    places = ["Taj Mahal", "Red Fort", "Gateway of India", "Hawa Mahal", "Mysore Palace"]
    results = []
    for p in places:
        data = generate_crowd_data(p)
        if status.lower() == data.current_level.lower():
            results.append(data)
    return {"recommendations": results}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)



