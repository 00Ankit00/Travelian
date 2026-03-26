"""
Curated landmark and meal-area hints for structured demo itineraries.
Distances are rough straight-line / typical routing from the main city centre — not live GIS.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple


@dataclass(frozen=True)
class Landmark:
    name: str
    entry_inr: int
    distance_km: float
    direction: str
    detail: str


def _display_city(raw: str) -> str:
    s = (raw or "").split(",")[0].strip()
    if not s:
        return "Destination"
    return " ".join(p.capitalize() for p in s.split())


def destination_label(raw: str) -> str:
    """First segment of destination, title case (for copy)."""
    return _display_city(raw)


def normalize_city_key(destination: str) -> str:
    first = (destination or "").split(",")[0].strip().lower()
    aliases = {
        "bengaluru": "bangalore",
        "bombay": "mumbai",
        "calcutta": "kolkata",
        "pondicherry": "puducherry",
        "pondy": "puducherry",
    }
    return aliases.get(first, first)


_LANDMARKS: Dict[str, List[Landmark]] = {
    "jaipur": [
        Landmark("Amber Fort", 200, 11, "NE", "Fort-palace complex; composite tickets often bundle Jaigarh — check counters."),
        Landmark("City Palace & Jantar Mantar", 700, 2, "central", "Royal collections and historic observatory — single-day combo common."),
        Landmark("Hawa Mahal (facade + museum)", 200, 2, "central", "Quick photo stop outside; interior museum is compact."),
        Landmark("Nahargarh Fort sunset ridge", 200, 6, "NW", "Ridge views over Pink City; windy evenings — carry a layer."),
        Landmark("Albert Hall Museum", 300, 3, "S", "Indo-Saracenic building; cooler midday escape in summer."),
        Landmark("Jal Mahal viewpoint", 0, 8, "N", "Waterside palace views from promenade; no boat needed for a short visit."),
        Landmark("Johari Bazaar & Bapu Bazaar", 0, 2, "central", "Textiles, jewellery lanes — negotiate calmly, watch pickpockets."),
        Landmark("Galtaji (Monkey Temple)", 0, 10, "E", "Temple complex with natural springs — respectful dress."),
    ],
    "delhi": [
        Landmark("Red Fort (Lal Qila)", 600, 5, "NE", "ASI monument — security lines; closed Mondays historically — verify."),
        Landmark("Qutub Minar complex", 600, 16, "S", "Early slot beats heat; large grounds — allow 2+ hours."),
        Landmark("Humayun's Tomb", 600, 7, "SE", "UNESCO garden tomb — golden hour photos."),
        Landmark("India Gate & Rajpath walk", 0, 3, "central", "Evening crowds; tight security zone — light bag."),
        Landmark("Lotus Temple", 0, 13, "SE", "Silence hall slots; closed Mondays — confirm hours."),
        Landmark("Akshardham (exhibits)", 350, 12, "E", "Strict bag policy — locker use; evening water show optional."),
        Landmark("Chandni Chowk food & heritage lane", 0, 4, "N", "Parathe wali gali / jalebi runs — go with a local guide if first time."),
        Landmark("National Museum", 20, 3, "central", "Air-conditioned wings — good for summer afternoons."),
    ],
    "mumbai": [
        Landmark("Gateway of India & Apollo Bunder", 0, 4, "S", "Ferries to Elephanta optional — separate ticket/timing."),
        Landmark("Chhatrapati Shivaji Maharaj Vastu Sangrahalaya (Prince of Wales)", 150, 3, "S", "Gothic museum — quiet weekday mornings."),
        Landmark("Marine Drive & Chowpatty", 0, 2, "W", "Sunset walk; street food hygiene — pick busy stalls."),
        Landmark("Bandra–Worli Sea Link drive", 0, 12, "NW", "Toll by car; photo stops limited — plan cab round trip."),
        Landmark("Elephanta Caves (ferry + entry)", 600, 10, "E", "Half-day: ferry from Gateway + ASI ticket — avoid monsoon rough seas."),
        Landmark("Kanheri Caves (Sanjay Gandhi National Park)", 100, 28, "N", "Forest entry + cave cluster — start early for leopards-in-park awareness."),
        Landmark("Colaba Causeway & Kala Ghoda", 0, 4, "S", "Cafés, indie shops — walking friendly."),
        Landmark("Haji Ali Dargah walkway", 0, 8, "SW", "Tide-dependent path — check sea timings."),
    ],
    "bangalore": [
        Landmark("Bangalore Palace", 300, 4, "N", "Tudor-style palace tours — photography fees extra sometimes."),
        Landmark("Lalbagh Botanical Garden", 100, 5, "S", "Glasshouse events on weekends — arrive early."),
        Landmark("Cubbon Park & State Central Library", 0, 2, "central", "Morning walks; metro nearby."),
        Landmark("Tipu Sultan's Summer Palace", 25, 4, "S", "Compact wooden palace — combine with KR Market area."),
        Landmark("Nandi Hills (day trip)", 250, 60, "N", "Pre-dawn departures popular — park entry separate."),
        Landmark("Commercial Street & Brigade Road", 0, 3, "central", "Shopping/evening energy — parking is tight."),
        Landmark("Vidhana Soudha photo stop", 0, 2, "N", "Lit facade evenings; perimeter security."),
        Landmark("Ulsoor Lake promenade", 0, 5, "E", "Short lakeside walk — sunrise calm."),
    ],
    "chennai": [
        Landmark("Kapaleeshwarar Temple (Mylapore)", 0, 6, "S", "Dravidian gopuram; non-Hindus may have inner sanctum limits — respect signs."),
        Landmark("Marina Beach promenade", 0, 4, "E", "Avoid swimming; lighthouse district nearby."),
        Landmark("Fort St. George & Museum", 100, 4, "E", "Colonial-era seat — IDs may be checked."),
        Landmark("Government Museum complex", 50, 4, "central", "Bronze gallery highlight — closes early some days."),
        Landmark("San Thome Basilica", 0, 8, "S", "Seaside church — combine with Besant Nagar."),
        Landmark("Mahabalipuram day trip ( Shore Temple )", 600, 55, "S", "UNESCO coastal monuments — start early for heat."),
        Landmark("Bessie (Besant Nagar) beach & eateries", 0, 10, "SE", "Evening crowds — popular cafés."),
        Landmark("Valluvar Kottam", 50, 5, "W", "Tamil poet memorial — quick stop."),
    ],
    "kolkata": [
        Landmark("Victoria Memorial Hall", 100, 4, "SE", "Museum + gardens — evening sound-and-light seasonal."),
        Landmark("Howrah Bridge & flower market", 0, 3, "W", "Dawn photowalk — busy, watch belongings."),
        Landmark("Dakshineswar Kali Temple", 0, 12, "N", "Riverfront ghat — combine with Belur Math ferry."),
        Landmark("Indian Museum", 75, 3, "central", "Large natural history sections — half day possible."),
        Landmark("Kalighat Temple", 0, 7, "S", "Dense lanes — dress modestly, beware touts."),
        Landmark("Mother House (Missionaries of Charity)", 0, 5, "S", "Quiet visit; closed afternoons — verify."),
        Landmark("Park Street dining strip", 0, 2, "central", "Heritage restaurants — reserve weekends."),
        Landmark("Princep Ghat", 0, 5, "SW", "Riverfront evenings — boat rides optional."),
    ],
    "agra": [
        Landmark("Taj Mahal", 1300, 5, "E", "Time-slot tickets online — sunrise slots sell out; shoe covers/bag rules strict."),
        Landmark("Agra Fort", 650, 3, "central", "Mughal fort views toward Taj — allow 2 hours."),
        Landmark("Mehtab Bagh (Taj view garden)", 300, 6, "N", "Sunset silhouette shots — Yamuna bank."),
        Landmark("Itmad-ud-Daulah (Baby Taj)", 400, 7, "E", "Marble inlay preview — less crowded than Taj."),
        Landmark("Fatehpur Sikri (day trip)", 600, 40, "W", "Buland Darwaza + palace complex — long day by car."),
        Landmark("Akbar's Tomb, Sikandra", 350, 12, "NW", "Spacious gardens — morning pleasant."),
        Landmark("Kinari Bazaar (old Agra)", 0, 3, "central", "Marble inlay shops — heavy bargaining."),
        Landmark("Taj Nature Walk", 200, 8, "E", "Greenbelt alternate angles — birding mornings."),
    ],
    "goa": [
        Landmark("Basilica of Bom Jesus & Se Cathedral (Old Goa)", 0, 10, "NE", "UNESCO churches — modest dress."),
        Landmark("Fort Aguada & lighthouse", 50, 12, "N", "Coastal fort views — parking fills by midday."),
        Landmark("Fontainhas Latin Quarter (Panjim)", 0, 2, "central", "Colourful lanes — walking tour friendly."),
        Landmark("Dudhsagar Falls (jeep season)", 400, 60, "E", "Monsoon-dependent flow — permit/jeep costs vary."),
        Landmark("Spice plantation tour (Ponda)", 400, 25, "E", "Lunch-included packages common — compare inclusions."),
        Landmark("Anjuna / Arambol sunset", 0, 18, "N", "Cliff or beach spots — traffic on weekends."),
        Landmark("Palolem / Agonda (South Goa)", 0, 70, "S", "Full-day beach hop if staying north — plan drive time."),
        Landmark("Chapora Fort viewpoint", 0, 22, "N", "Short climb — iconic coast panorama."),
    ],
    "hyderabad": [
        Landmark("Charminar & Laad Bazaar", 0, 4, "SE", "Crowded core — pearls/bangles lanes; watch bags."),
        Landmark("Golconda Fort & sound show", 200, 11, "W", "Climb to Bala Hisar — evenings cooler."),
        Landmark("Salar Jung Museum", 50, 3, "SW", "Large collection — half day easy."),
        Landmark("Hussain Sagar (Buddha statue boat)", 350, 4, "N", "Boat rides weather dependent."),
        Landmark("Qutb Shahi Tombs", 40, 9, "W", "Garden tombs — photo friendly mornings."),
        Landmark("Ramoji Film City (day)", 1350, 35, "E", "Full-day ticketed park — separate budget."),
        Landmark("Chowmahalla Palace", 80, 4, "SE", "Nizam-era courtyards — combine with Charminar."),
        Landmark("HITEC City cyber lakeside walk", 0, 16, "NW", "Modern contrast to Old City."),
    ],
    "udaipur": [
        Landmark("City Palace complex", 600, 1, "central", "Lake-facing wings — museum tickets tiered."),
        Landmark("Lake Pichola boat to Jag Mandir", 800, 1, "central", "Sunset boats premium — confirm inclusions."),
        Landmark("Jagdish Temple", 0, 1, "central", "Carved temple steps — busy festivals."),
        Landmark("Saheliyon-ki-Bari", 50, 5, "N", "Fountains and marble elephants — short visit."),
        Landmark("Monsoon Palace (Sajjangarh)", 300, 8, "W", "Hill sunset — shared jeeps common."),
        Landmark("Bagore-ki-Haveli cultural show", 150, 1, "central", "Evening folk dance — tickets at gate."),
        Landmark("Vintage car museum", 350, 3, "E", "Royal collection — quick niche stop."),
        Landmark("Shilpgram crafts fair (seasonal)", 100, 7, "W", "Rural arts complex — weekends busier."),
    ],
    "varanasi": [
        Landmark("Dashashwamedh Ghat Ganga Aarti", 0, 4, "E", "Evening ceremony — arrive early for seating."),
        Landmark("Sunrise boat ride (main ghats)", 400, 4, "E", "Negotiate boat rate upfront; life jackets if offered."),
        Landmark("Kashi Vishwanath Temple corridor", 0, 4, "central", "Security and dress codes strict — mobile lockers."),
        Landmark("Sarnath (Buddhist site)", 50, 12, "NE", "Dhamek Stupa + museum — half day."),
        Landmark("Manikarnika / Harishchandra ghats (observe respectfully)", 0, 5, "E", "Quiet, no photography zones — cultural sensitivity."),
        Landmark("Ramnagar Fort", 200, 8, "SE", "Across the river — ferry or bridge routing."),
        Landmark("Banaras Hindu University campus", 0, 8, "S", "Wide campus — New Vishwanath Temple."),
        Landmark("Silk weaving alleys (Godowlia)", 0, 3, "central", "Saree workshops — buy from reputed co-ops if unsure."),
    ],
    "kochi": [
        Landmark("Fort Kochi Chinese fishing nets", 0, 8, "W", "Sunset tip — pay only agreed photo fees."),
        Landmark("Mattancherry Palace (Dutch)", 10, 9, "SW", "Murals and heritage — closed Fridays historically."),
        Landmark("Jew Town & Paradesi Synagogue", 100, 9, "SW", "Small synagogue — modest dress, closed Sabbath."),
        Landmark("St. Francis Church", 0, 8, "W", "Vasco-era church — quiet visit."),
        Landmark("Kerala Kathakali centre show", 400, 10, "central", "Make-up demo + performance tickets — book ahead."),
        Landmark("Marine Drive Kochi", 0, 4, "W", "Evening sea breeze — food stalls."),
        Landmark("Hill Palace Museum", 30, 14, "E", "Royal collections — out of core Fort area."),
        Landmark("Cherai Beach", 0, 25, "NW", "Calmer swim-ish beach — check local flags."),
    ],
    "mysuru": [
        Landmark("Mysore Palace", 200, 2, "central", "Illumination Sundays — interior shoe storage."),
        Landmark("Chamundeshwari Temple (hill)", 0, 13, "SE", "Steep drive or steps — views over city."),
        Landmark("St. Philomena's Cathedral", 0, 3, "N", "Neo-Gothic interiors — photo respectful."),
        Landmark("Brindavan Gardens & musical fountains", 100, 21, "NW", "Evening fountain show timing varies."),
        Landmark("Jaganmohan Palace Art Gallery", 150, 2, "central", "Raja Ravi Varma works — quiet."),
        Landmark("Devaraja Market", 0, 2, "central", "Mysore pak & flower stalls — crowded."),
        Landmark("Rail Museum Mysore", 50, 3, "E", "Family-friendly — short stop."),
        Landmark("Ranganathittu Bird Sanctuary", 100, 16, "N", "Boat safaris seasonal — mornings best."),
    ],
    "puducherry": [
        Landmark("White Town French Quarter walk", 0, 1, "E", "Grid lanes, cafés — morning light."),
        Landmark("Sri Aurobindo Ashram", 0, 1, "central", "Quiet meditation zones — follow visitor rules."),
        Landmark("Promenade Beach (Rock Beach)", 0, 1, "E", "No vehicles evening — families."),
        Landmark("Auroville Visitors Centre & Matrimandir view", 0, 12, "NW", "Day pass process — book inner chamber separately long ahead."),
        Landmark("Paradise Beach (Chunnambar boat)", 200, 8, "S", "Boat fees separate — carry water."),
        Landmark("Manakula Vinayagar Temple", 0, 1, "central", "Elephant blessing optional — small fee."),
        Landmark("Basilica of the Sacred Heart", 0, 2, "W", "Stained glass — quick stop."),
        Landmark("Ousteri Lake birding", 0, 12, "W", "Seasonal migrants — sunrise."),
    ],
}

_MEAL_HUBS: Dict[str, Dict[str, str]] = {
    "jaipur": {
        "breakfast": "Rawat Mishthan Bhandar / LMB / Sindhi Camp kachori belt",
        "lunch": "Handi / Spice Court / rooftop near Johri Bazaar",
        "dinner": "1135 AD (Amber area) or Masala Chowk / MI Road",
    },
    "delhi": {
        "breakfast": "Karim's vicinity (Old Delhi) or Bengali Market",
        "lunch": "Connaught Place inner circle or Khan Market",
        "dinner": "Hauz Khas Village or Dilli Haat INA",
    },
    "mumbai": {
        "breakfast": "Café Irani / Kyani & Co / Fort cafés",
        "lunch": "Crawford Market vicinity or Kala Ghoda",
        "dinner": "Juhu beach stalls (hygiene pick) or Bandra linking road",
    },
    "bangalore": {
        "breakfast": "CTR (Malleswaram) / Vidyarthi Bhavan",
        "lunch": "VV Puram food street or Indiranagar 12th Main",
        "dinner": "Koramangala 5th Block or Church Street",
    },
    "chennai": {
        "breakfast": "Saravana Bhavan / Murugan Idli / Mylapore tank lanes",
        "lunch": "Ratna Café (Samosapuri) or Besant Nagar",
        "dinner": "Nungambakkam Khader Nawaz Khan Rd or Alwarpet",
    },
    "kolkata": {
        "breakfast": "Territy Bazaar Chinese breakfast / Flury's",
        "lunch": "6 Ballygunge Place or Oh! Calcutta",
        "dinner": "Park Street aram or College Street adda cafés",
    },
    "agra": {
        "breakfast": "Ram Babu Paratha Bhandar or Sadar Bazar",
        "lunch": "Pinch of Spice / Shankara Vegis",
        "dinner": "Rooftop Taj Ganj views or Sadar market",
    },
    "goa": {
        "breakfast": "Mapusa market / Panjim cafés",
        "lunch": "Fish thali shacks (Anjuna-Baga) — pick busy ones",
        "dinner": "Fontainhas tavernas or beach shack (seasonal)",
    },
    "hyderabad": {
        "breakfast": "Niloufer Café / Nimrah (Charminar)",
        "lunch": "Paradise biryani / Shah Ghouse",
        "dinner": "Banjara Hills fine dine or late Irani chai at Secunderabad",
    },
    "udaipur": {
        "breakfast": "Jagat Niwas rooftop / local kachori lanes",
        "lunch": "Ambrai / lakeside thali hotels",
        "dinner": "Upre / Harigarh fort area sunset tables",
    },
    "varanasi": {
        "breakfast": "Kachori-sabzi lanes near Godowlia",
        "lunch": "Brown Bread Bakery / rooftop thalis",
        "dinner": "Ganga view cafés (Dashashwamedh) — check reviews",
    },
    "kochi": {
        "breakfast": "Fort Kochi Kashi Art Café / French toast lanes",
        "lunch": "Oceanos / Fort House",
        "dinner": "Malabar junction / seafood on Willingdon Island",
    },
    "mysuru": {
        "breakfast": "Mylari Hotel / Hotel Original Vinayaka Mylari",
        "lunch": "RRR thali / Hotel Hanumanthu",
        "dinner": "Oyster Bay / rooftop near palace",
    },
    "puducherry": {
        "breakfast": "Café des Arts / Bread & Chocolate",
        "lunch": "Villa Shanti / White Town bistros",
        "dinner": "Promenade sea-view or Auroville organic kitchens",
    },
}


def landmarks_for(destination: str) -> List[Landmark]:
    key = normalize_city_key(destination)
    if key in _LANDMARKS:
        return _LANDMARKS[key]
    d = _display_city(destination)
    return [
        Landmark(f"{d} Old Quarter Heritage Walk", 0, 2, "central", "Lanes, local shrines, and cafés — start from the main clock tower / square."),
        Landmark(f"{d} Viewpoint & Sunset Ridge", 50, 9, "W", "Elevated panorama — carry water; confirm road access in monsoon."),
        Landmark(f"{d} City Museum / Art District", 100, 4, "NE", "Air-conditioned galleries — good midday anchor."),
        Landmark(f"{d} Central Park & Lake Loop", 0, 3, "S", "Easy flat walk — families and joggers."),
        Landmark(f"{d} Handicrafts & Local Market", 0, 5, "E", "Textiles and snacks — cash small notes."),
        Landmark(f"{d} Riverside / Waterfront Promenade", 0, 6, "NW", "Evening breeze slot — boat rides if available."),
        Landmark(f"{d} Day-trip Nature Patch", 200, 45, "N", "Hills or sanctuary — shared tours common; start early."),
        Landmark(f"{d} Night Food Street", 0, 4, "central", "Street food hygiene — choose busy stalls with turnover."),
    ]


def meal_hub(city_key: str, meal: str) -> str:
    hubs = _MEAL_HUBS.get(city_key, {})
    return hubs.get(meal, "Main city-centre dining strip (pick busy, reviewed venues)")


def _entry_line(inr: int) -> str:
    if inr <= 0:
        return "Free / donation-only at gate (indicative) — still verify locally."
    return f"₹{inr} per person indicative (Indian national / ASI-style sites often differ) — **book online where available**."


def describe_landmark_visit(
    lm: Landmark,
    time: str,
    duration: str,
    dest_display: str,
) -> str:
    return (
        f"**Place:** {lm.name}\n\n"
        f"**Scheduled window:** {time} · plan ~{duration} on site (plus transfers)\n\n"
        f"**Distance from {dest_display} city centre (approx.):** {lm.distance_km:g} km {lm.direction}\n\n"
        f"**Entry / ticket:** {_entry_line(lm.entry_inr)}\n\n"
        f"**What to do:** {lm.detail}\n\n"
        f"**Transfers:** Metro / app cab / auto where available; add 20–40 min buffer in peak hours."
    )


def describe_meal_stop(
    city_key: str,
    meal: str,
    time: str,
    duration: str,
    distance_km: float,
    dest_display: str,
    budget_hint: str,
) -> Tuple[str, str]:
    hub = meal_hub(city_key, meal)
    if "Budget" in budget_hint or "Under ₹10" in budget_hint:
        spend = "₹80–250 per person typical"
    elif "Premium" in budget_hint or "Above ₹50" in budget_hint:
        spend = "₹600–1,800 per person typical"
    elif "Luxury" in budget_hint:
        spend = "₹400–1,200 per person typical"
    else:
        spend = "₹200–650 per person typical"
    title_map = {
        "breakfast": f"Breakfast — {hub.split('/')[0].strip()}",
        "lunch": f"Lunch — {hub.split('/')[0].strip()}",
        "dinner": f"Dinner — {hub.split('/')[0].strip()}",
    }
    title = title_map.get(meal, f"{meal.title()} — {hub.split('/')[0].strip()}")
    desc = (
        f"**Area / picks:** {hub}\n\n"
        f"**Time:** {time} · ~{duration}\n\n"
        f"**Distance from {dest_display} city centre (approx.):** {distance_km:g} km\n\n"
        f"**Typical spend:** {spend} (drinks extra)\n\n"
        f"**Notes:** Pick busy kitchens; bottled water; align spice level when ordering."
    )
    return title, desc


def pick_landmark(landmarks: List[Landmark], index: int) -> Landmark:
    return landmarks[index % len(landmarks)]
