"""
Travel booking helpers: partner deep links + optional Amadeus live flight/hotel data.
Set AMADEUS_CLIENT_ID and AMADEUS_CLIENT_SECRET for live offers (free test API: developers.amadeus.com).
"""
from __future__ import annotations

import logging
import os
import re
import time
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import quote, urlencode

import requests

# Common Indian cities → IATA (flights / Amadeus city codes for hotels where applicable)
CITY_IATA: Dict[str, str] = {
    "mumbai": "BOM",
    "bombay": "BOM",
    "delhi": "DEL",
    "new delhi": "DEL",
    "bengaluru": "BLR",
    "bangalore": "BLR",
    "chennai": "MAA",
    "madras": "MAA",
    "kolkata": "CCU",
    "calcutta": "CCU",
    "hyderabad": "HYD",
    "ahmedabad": "AMD",
    "jaipur": "JAI",
    "goa": "GOI",
    "panaji": "GOI",
    "kochi": "COK",
    "cochin": "COK",
    "pune": "PNQ",
    "lucknow": "LKO",
    "varanasi": "VNS",
    "udaipur": "UDR",
    "srinagar": "SXR",
    "chandigarh": "IXC",
    "amritsar": "ATQ",
    "indore": "IDR",
    "nagpur": "NAG",
    "patna": "PAT",
    "guwahati": "GAU",
    "visakhapatnam": "VTZ",
    "trivandrum": "TRV",
    "thiruvananthapuram": "TRV",
}

_amadeus_token: Optional[str] = None
_amadeus_token_expiry: float = 0.0


def _norm_city(name: str) -> str:
    return re.sub(r"\s+", " ", (name or "").strip().lower())


def city_to_iata(city: str) -> Optional[str]:
    key = _norm_city(city)
    if not key:
        return None
    if key in CITY_IATA:
        return CITY_IATA[key]
    for part in key.split(","):
        p = part.strip()
        if p in CITY_IATA:
            return CITY_IATA[p]
    return None


def _slug(s: str) -> str:
    s = _norm_city(s).replace(",", " ")
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s or "city"


def _skyscanner_path_segment(iata_o: str, iata_d: str, yymmdd: str) -> str:
    """Skyscanner-style path: /bom/jai/250301/ — uses 2-digit year."""
    return f"{iata_o.lower()}/{iata_d.lower()}/{yymmdd}"


def build_partner_links(
    origin: str,
    destination: str,
    start_date: str,
    end_date: str,
    adults: int,
) -> Dict[str, List[Dict[str, str]]]:
    """Curated booking-site URLs (no API keys)."""
    adults = max(1, min(int(adults or 1), 9))
    iata_o = city_to_iata(origin) or "DEL"
    iata_d = city_to_iata(destination) or "BOM"

    # YYYYMMDD for some sites
    ymd = start_date.replace("-", "") if start_date else ""
    yymmdd = ymd[2:] if len(ymd) == 8 else ymd

    sky = _skyscanner_path_segment(iata_o, iata_d, yymmdd or "250101")
    flights: List[Dict[str, str]] = [
        {
            "id": "skyscanner",
            "label": "Skyscanner (compare flights)",
            "href": f"https://www.skyscanner.co.in/transport/flights/{sky}/",
        },
        {
            "id": "google-flights",
            "label": "Google Flights",
            "href": (
                "https://www.google.com/travel/flights?"
                + urlencode(
                    {
                        "q": f"Flights from {origin} to {destination} on {start_date}",
                        "hl": "en",
                        "curr": "INR",
                    }
                )
            ),
        },
        {
            "id": "cleartrip-flights",
            "label": "Cleartrip Flights",
            "href": f"https://www.cleartrip.com/flights/results?from={iata_o}&to={iata_d}&depart-date={start_date}&adults={adults}",
        },
    ]

    # Ixigo trains (India-friendly search)
    trains: List[Dict[str, str]] = [
        {
            "id": "ixigo-trains",
            "label": "Ixigo Trains",
            "href": (
                "https://www.ixigo.com/trains/find-train?"
                + urlencode({"src": origin.strip(), "dst": destination.strip(), "date": start_date})
            ),
        },
        {
            "id": "irctc",
            "label": "IRCTC (official railways)",
            "href": "https://www.irctc.co.in/nget/train-search",
        },
    ]

    slug_o, slug_d = _slug(origin), _slug(destination)
    buses: List[Dict[str, str]] = [
        {
            "id": "redbus",
            "label": "redBus",
            "href": f"https://www.redbus.in/bus-tickets/{slug_o}-to-{slug_d}-bus-tickets",
        },
        {
            "id": "abhibus",
            "label": "AbhiBus",
            "href": (
                "https://www.abhibus.com/bus_search.php?"
                + urlencode({"source": origin.strip(), "destination": destination.strip(), "doj": start_date})
            ),
        },
    ]

    dest_q = destination.strip()
    hotels: List[Dict[str, str]] = [
        {
            "id": "booking",
            "label": "Booking.com",
            "href": (
                "https://www.booking.com/searchresults.html?"
                + urlencode(
                    {
                        "ss": dest_q,
                        "checkin": start_date,
                        "checkout": end_date,
                        "group_adults": adults,
                        "no_rooms": 1,
                    }
                )
            ),
        },
        {
            "id": "agoda",
            "label": "Agoda",
            "href": "https://www.agoda.com/search?" + urlencode({"city": dest_q, "checkIn": start_date, "checkOut": end_date}),
        },
        {
            "id": "makemytrip-hotels",
            "label": "MakeMyTrip Hotels",
            "href": "https://www.makemytrip.com/hotels/hotel-listing/?city=" + quote(dest_q),
        },
    ]

    return {"flights": flights, "trains": trains, "buses": buses, "hotels": hotels}


def _amadeus_host() -> str:
    return os.getenv("AMADEUS_HOST", "https://test.api.amadeus.com").rstrip("/")


def _amadeus_credentials() -> Tuple[Optional[str], Optional[str]]:
    cid = os.getenv("AMADEUS_CLIENT_ID", "").strip()
    sec = os.getenv("AMADEUS_CLIENT_SECRET", "").strip()
    if not cid or not sec:
        return None, None
    return cid, sec


def get_amadeus_token() -> Optional[str]:
    global _amadeus_token, _amadeus_token_expiry
    cid, sec = _amadeus_credentials()
    if not cid:
        return None
    now = time.time()
    if _amadeus_token and now < _amadeus_token_expiry - 30:
        return _amadeus_token
    try:
        r = requests.post(
            f"{_amadeus_host()}/v1/security/oauth2/token",
            data={
                "grant_type": "client_credentials",
                "client_id": cid,
                "client_secret": sec,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=12,
        )
        r.raise_for_status()
        data = r.json()
        _amadeus_token = data.get("access_token")
        _amadeus_token_expiry = now + int(data.get("expires_in", 1700))
        return _amadeus_token
    except Exception:
        logging.exception("Amadeus OAuth failed")
        _amadeus_token = None
        _amadeus_token_expiry = 0.0
        return None


def amadeus_resolve_city_iata(city: str, token: str) -> Optional[str]:
    direct = city_to_iata(city)
    if direct:
        return direct
    try:
        r = requests.get(
            f"{_amadeus_host()}/v1/reference-data/locations",
            params={"keyword": city.strip()[:50], "subType": "CITY", "max": "3"},
            headers={"Authorization": f"Bearer {token}"},
            timeout=10,
        )
        r.raise_for_status()
        d = r.json()
        for it in d.get("data") or []:
            code = it.get("iataCode")
            if code:
                return code
    except Exception:
        logging.exception("Amadeus city lookup failed for %s", city)
    return None


def fetch_amadeus_flights(
    origin: str,
    destination: str,
    departure_date: str,
    adults: int,
    token: str,
    max_offers: int = 6,
) -> Tuple[List[Dict[str, Any]], Optional[str]]:
    o = amadeus_resolve_city_iata(origin, token)
    d = amadeus_resolve_city_iata(destination, token)
    if not o or not d:
        return [], "Could not resolve airport/city codes for flight search."
    adults = max(1, min(int(adults or 1), 9))
    try:
        r = requests.get(
            f"{_amadeus_host()}/v2/shopping/flight-offers",
            params={
                "originLocationCode": o,
                "destinationLocationCode": d,
                "departureDate": departure_date,
                "adults": adults,
                "currencyCode": "INR",
                "max": max_offers,
            },
            headers={"Authorization": f"Bearer {token}"},
            timeout=15,
        )
        r.raise_for_status()
        payload = r.json()
    except Exception as e:
        logging.exception("Amadeus flight offers failed")
        return [], str(e) or "Flight search failed."

    offers: List[Dict[str, Any]] = []
    for item in (payload.get("data") or [])[:max_offers]:
        price = (item.get("price") or {}).get("grandTotal") or (item.get("price") or {}).get("total")
        curr = (item.get("price") or {}).get("currency", "INR")
        itins = item.get("itineraries") or []
        segs = (itins[0].get("segments") or []) if itins else []
        first = segs[0] if segs else {}
        last = segs[-1] if segs else {}
        carrier = (first.get("carrierCode") or "") + (f" {first.get('number') or ''}").strip()
        offers.append(
            {
                "price": price,
                "currency": curr,
                "carrierSummary": carrier,
                "departureAt": (first.get("departure") or {}).get("at"),
                "arrivalAt": (last.get("arrival") or {}).get("at"),
                "duration": (itins[0].get("duration") if itins else None),
                "segments": len(segs),
                "originIata": o,
                "destIata": d,
            }
        )
    return offers, None


def fetch_amadeus_hotels(
    city_name: str,
    check_in: str,
    check_out: str,
    adults: int,
    token: str,
    max_hotels: int = 8,
) -> Tuple[List[Dict[str, Any]], Optional[str]]:
    code = amadeus_resolve_city_iata(city_name, token)
    if not code:
        return [], "Could not resolve city code for hotels."
    adults = max(1, min(int(adults or 1), 9))
    try:
        lr = requests.get(
            f"{_amadeus_host()}/v1/reference-data/locations/hotels/by-city",
            params={"cityCode": code},
            headers={"Authorization": f"Bearer {token}"},
            timeout=12,
        )
        lr.raise_for_status()
        hotels_raw = (lr.json().get("data") or [])[:max_hotels]
        hotel_ids = [h.get("hotelId") for h in hotels_raw if h.get("hotelId")]
        if not hotel_ids:
            return [], "No hotels found for this city in Amadeus test data."
        r = requests.get(
            f"{_amadeus_host()}/v3/shopping/hotel-offers",
            params={
                "hotelIds": ",".join(hotel_ids[:20]),
                "checkInDate": check_in,
                "checkOutDate": check_out,
                "adults": adults,
                "currency": "INR",
                "lang": "EN",
            },
            headers={"Authorization": f"Bearer {token}"},
            timeout=20,
        )
        r.raise_for_status()
        payload = r.json()
    except Exception as e:
        logging.exception("Amadeus hotel offers failed")
        return [], str(e) or "Hotel search failed."

    out: List[Dict[str, Any]] = []
    for block in (payload.get("data") or [])[:max_hotels]:
        hid = block.get("hotel", {}).get("hotelId")
        name = block.get("hotel", {}).get("name") or "Hotel"
        offers = block.get("offers") or []
        if not offers:
            continue
        o0 = offers[0]
        price = (o0.get("price") or {}).get("total")
        curr = (o0.get("price") or {}).get("currency", "INR")
        out.append(
            {
                "hotelId": hid,
                "name": name,
                "price": price,
                "currency": curr,
                "checkIn": check_in,
                "checkOut": check_out,
            }
        )
    return out, None if out else "No live hotel rates returned (test data may be limited)."


DUMMY_OPTION_COUNT = 20

_FLIGHT_BASE = [
    ("IndiGo", "6E"),
    ("Air India", "AI"),
    ("SpiceJet", "SG"),
    ("Akasa Air", "QP"),
    ("Vistara", "UK"),
    ("Air India Express", "IX"),
    ("Star Air", "S5"),
    ("Alliance Air", "9I"),
]
_TRAIN_NAMES = [
    "Rajdhani Express",
    "Shatabdi Express",
    "Duronto Express",
    "Garib Rath",
    "Humsafar Express",
    "Tejas Express",
    "Vande Bharat",
    "Sampark Kranti",
    "Double Decker",
    "Uday Express",
    "Antyodaya Express",
    "Jan Shatabdi",
    "Mail / Express",
    "Superfast Express",
    "Passenger",
    "MEMU",
    "AC Express",
    "Night Rider Express",
    "Festival Special",
    "Summer Special",
]
_BUS_OPS = [
    "VRL Travels",
    "SRS Travels",
    "Orange Travels",
    "National Travels",
    "Kallada Travels",
    "Parveen Travels",
    "Jabbar Travels",
    "Sharma Travels",
    "Rajasthan State Roadways",
    "Maharashtra State Roadways",
    "Dolphin Travels",
    "Sugama Tourist",
    "Sea Bird Tourist",
    "Neeta Tours",
    "Paulo Travels",
    "Morning Star Travels",
    "KPN Travels",
    "GreenLine Travels",
    "YBM Travels",
    "IntrCity SmartBus",
]
_HOTEL_ADJECTIVES = [
    "Grand",
    "Royal",
    "Heritage",
    "Plaza",
    "Regency",
    "Palace",
    "Residency",
    "Cliff",
    "Lake View",
    "Garden",
    "City Centre",
    "Metro",
    "Boutique",
    "Premium",
    "Comfort",
    "Executive",
    "Business",
    "Luxury",
    "Eco",
    "Signature",
]


def _inr(amount: int) -> str:
    return f"₹{amount:,}"


def _display_city(raw: str) -> str:
    """First segment before comma; title case for labels (e.g. chennai -> Chennai)."""
    s = (raw or "").split(",")[0].strip()
    if not s:
        return "City"
    return " ".join(part.capitalize() for part in s.split())


def _train_title_with_cities(base_name: str, o_disp: str, d_disp: str) -> str:
    """Embed origin/destination into train names (e.g. Chennai Rajdhani)."""
    b = base_name.strip()
    low = b.lower()
    if "rajdhani" in low:
        return f"{d_disp} Rajdhani"
    if "shatabdi" in low:
        return f"{d_disp} Shatabdi"
    if "vande bharat" in low:
        return f"Vande Bharat · {o_disp}–{d_disp}"
    if "duronto" in low:
        return f"{d_disp} Duronto (ex-{o_disp})"
    if "garib" in low:
        return f"{o_disp}–{d_disp} Garib Rath"
    if "humsafar" in low:
        return f"{d_disp} Humsafar (from {o_disp})"
    if "tejas" in low:
        return f"{d_disp} Tejas Express"
    if "sampark" in low:
        return f"{d_disp} Sampark Kranti"
    if "double decker" in low:
        return f"{o_disp}–{d_disp} Double Decker"
    if "uday" in low:
        return f"{d_disp} Uday Express"
    if "antyodaya" in low:
        return f"{o_disp}–{d_disp} Antyodaya"
    if "jan shatabdi" in low:
        return f"{d_disp} Jan Shatabdi"
    if "superfast" in low:
        return f"{d_disp} Superfast (via {o_disp})"
    if "mail" in low and "/" in b:
        return f"{o_disp}–{d_disp} Mail Express"
    if "passenger" in low:
        return f"{o_disp}–{d_disp} Passenger"
    if "memu" in low:
        return f"{d_disp} area MEMU / suburban link"
    if "ac express" in low:
        return f"{o_disp}–{d_disp} AC Express"
    if "night rider" in low:
        return f"{o_disp}–{d_disp} Night Rider"
    if "festival" in low:
        return f"{d_disp} Festival Special (from {o_disp})"
    if "summer" in low:
        return f"{o_disp}–{d_disp} Summer Special"
    return f"{o_disp}–{d_disp} {b}"


def _hotel_title_variant(i: int, adj: str, d_disp: str) -> Tuple[str, str]:
    """Rotate hotel naming so destination keyword is prominent."""
    patterns = [
        (f"{adj} {d_disp} Hotel & Spa", f"{d_disp} city centre · near landmarks"),
        (f"{d_disp} Palace · {adj} Collection", f"Old {d_disp} quarter"),
        (f"The {d_disp} Heritage by {adj}", f"Heritage district · {d_disp}"),
        (f"{d_disp} Residency — {adj}", f"CBD · {d_disp}"),
        (f"{adj} Towers, {d_disp}", f"Skyline views · {d_disp}"),
        (f"{d_disp} Lakefront · {adj}", f"Lakeside · {d_disp}"),
        (f"{d_disp} Airport Inn ({adj})", f"Near airport · {d_disp}"),
        (f"{adj} Boutique · {d_disp}", f"Arts district · {d_disp}"),
    ]
    return patterns[i % len(patterns)]


def build_dummy_booking_options(
    origin: str,
    destination: str,
    start_date: str,
    end_date: str,
    adults: int,
    count: int = DUMMY_OPTION_COUNT,
) -> Dict[str, List[Dict[str, str]]]:
    """Deterministic demo rows for UI (not real inventory)."""
    o_raw = (origin or "").strip()
    d_raw = (destination or "").strip()
    o_disp = _display_city(o_raw)
    d_disp = _display_city(d_raw)
    adults = max(1, min(int(adults or 1), 9))
    iata_o = city_to_iata(o_raw) or "—"
    iata_d = city_to_iata(d_raw) or "—"
    flights: List[Dict[str, str]] = []
    trains: List[Dict[str, str]] = []
    buses: List[Dict[str, str]] = []
    hotels: List[Dict[str, str]] = []

    for i in range(count):
        carrier, code = _FLIGHT_BASE[i % len(_FLIGHT_BASE)]
        fn = f"{code}{(200 + i * 37) % 900 + 100}"
        dep_h = 5 + (i * 3) % 14
        dep_m = (i * 17) % 60
        dur_h = 1 + (i % 4)
        dur_m = (i * 11) % 50
        price_f = 3200 + (i * 641) % 14500 + adults * 400
        flights.append(
            {
                "id": f"dummy-flight-{i + 1}",
                "title": f"{carrier} {fn} · {o_disp}→{d_disp}",
                "subtitle": f"Route {o_disp} → {d_disp} · {start_date}",
                "price": _inr(price_f),
                "meta": (
                    f"Dep {dep_h:02d}:{dep_m:02d} · ~{dur_h}h {dur_m}m · {adults} adult(s) · "
                    f"Est. {iata_o}–{iata_d}"
                ),
                "badge": "Non-stop" if i % 3 else f"{1 + i % 2} stop(s)",
            }
        )

        tn_base = _TRAIN_NAMES[i % len(_TRAIN_NAMES)]
        tr_no = f"{10000 + i * 111}"
        cls = ["3A", "2A", "SL", "CC", "EC", "1A", "2S", "GN"][(i + adults) % 8]
        tr_price = 450 + (i * 223) % 3200 + adults * 180
        trains.append(
            {
                "id": f"dummy-train-{i + 1}",
                "title": f"{_train_title_with_cities(tn_base, o_disp, d_disp)} ({tr_no})",
                "subtitle": f"{o_disp} → {d_disp} · {start_date}",
                "price": _inr(tr_price),
                "meta": (
                    f"Class {cls} · Dep {6 + (i % 12):02d}:{(i * 7) % 60:02d} · "
                    f"~{4 + i % 18}h · {o_disp} to {d_disp}"
                ),
                "badge": cls,
            }
        )

        op = _BUS_OPS[i % len(_BUS_OPS)]
        typ = ["AC Sleeper", "Volvo AC", "Non-AC Seater", "AC Seater", "Bharat Benz"][(i + 2) % 5]
        bus_price = 600 + (i * 317) % 2800 + adults * 120
        buses.append(
            {
                "id": f"dummy-bus-{i + 1}",
                "title": f"{op} · {o_disp} to {d_disp}",
                "subtitle": f"{typ} · Intercity {o_disp} – {d_disp}",
                "price": _inr(bus_price),
                "meta": (
                    f"Board near {o_disp} · Drop {d_disp} · Pickup ~{7 + (i % 10):02d}:{(i * 13) % 60:02d} · {start_date}"
                ),
                "badge": typ.split()[0],
            }
        )

        adj = _HOTEL_ADJECTIVES[i % len(_HOTEL_ADJECTIVES)]
        nights = 1 + (i % 6)
        night_rate = 1800 + (i * 509) % 12000
        total_h = night_rate * nights + adults * 400
        h_title, h_sub = _hotel_title_variant(i, adj, d_disp)
        hotels.append(
            {
                "id": f"dummy-hotel-{i + 1}",
                "title": h_title,
                "subtitle": f"{h_sub} · {nights} night(s)",
                "price": _inr(total_h),
                "meta": (
                    f"~{_inr(night_rate)}/night in {d_disp} · Check-in {start_date} · {adults} guest(s)"
                ),
                "badge": f"{3 + (i % 3)}★",
            }
        )

    return {"flights": flights, "trains": trains, "buses": buses, "hotels": hotels}


def get_booking_payload(
    origin: str,
    destination: str,
    start_date: str,
    end_date: str,
    adults: int,
) -> Dict[str, Any]:
    links = build_partner_links(origin, destination, start_date, end_date, adults)
    _acid, _asec = _amadeus_credentials()
    live: Dict[str, Any] = {
        "flights": [],
        "hotels": [],
        "flightError": None,
        "hotelError": None,
        "amadeusConfigured": bool(_acid and _asec),
    }

    token = get_amadeus_token()
    if token:
        flights, ferr = fetch_amadeus_flights(origin, destination, start_date, adults, token)
        live["flights"] = flights
        live["flightError"] = ferr
        hotels, herr = fetch_amadeus_hotels(destination, start_date, end_date, adults, token)
        live["hotels"] = hotels
        live["hotelError"] = herr
    else:
        live["flightError"] = None if not _amadeus_credentials()[0] else "Amadeus token unavailable."
        live["hotelError"] = live["flightError"]

    return {
        "links": links,
        "dummy": build_dummy_booking_options(
            origin, destination, start_date, end_date, adults, DUMMY_OPTION_COUNT
        ),
        "live": live,
        "meta": {
            "originIataGuess": city_to_iata(origin),
            "destinationIataGuess": city_to_iata(destination),
        },
    }
