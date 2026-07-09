import streamlit as st
from datetime import datetime, time
from zoneinfo import ZoneInfo
import html
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Assistant Télépro Énergie",
    page_icon="📞",
    layout="centered",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    :root { color-scheme: dark; }
    .stApp { background: #080c14 !important; color: #eef4ff !important; }

    /* Barre blanche Streamlit du haut */
    header[data-testid="stHeader"] {
        background: #080c14 !important;
        border-bottom: 1px solid #111827 !important;
    }
    header[data-testid="stHeader"] * { color: #eaf1ff !important; }
    [data-testid="stToolbar"] { background: transparent !important; }
    [data-testid="stDecoration"] { display:none !important; }

    [data-testid="stSidebar"] { background: #0d1422 !important; border-right: 1px solid #1e2a3d; }
    [data-testid="stSidebar"] * { color: #e6edf7 !important; }
    .block-container {padding-top: 0.8rem; padding-bottom: 1.1rem; max-width: 820px;}
    h1 {font-size: 1.55rem; margin-bottom: 0.1rem; color:#ffffff !important;}
    h2, h3, h4, p, label, span, div { color:#eef4ff; }
    h2, h3 {margin-top: 0.5rem; color:#ffffff !important;}
    .script {
        background:#101a2b; border:1px solid #263753; border-left:5px solid #75a7ff; border-radius:14px;
        padding:13px 15px; margin:10px 0 16px 0; line-height:1.45; color:#eaf1ff;
    }
    .script b { color:#9fc0ff !important; }
    .ok {background:#0f2a1d; border:1px solid #236a44; color:#bff6d4; border-radius:12px; padding:10px; margin:8px 0;}
    .warn {background:#2d230b; border:1px solid #7d641c; color:#ffe6a3; border-radius:12px; padding:10px; margin:8px 0;}
    .bad {background:#311317; border:1px solid #7d2d37; color:#ffc7cf; border-radius:12px; padding:10px; margin:8px 0;}
    .mini {font-size:.88rem; color:#aeb9ca;}
    div[data-testid="stMetric"] {background:#0d1422; border:1px solid #1e2a3d; border-radius:12px; padding:8px;}
    div[data-testid="stMetric"] * { color:#eef4ff !important; }
    .stButton > button {width:100%; min-height:2.7rem; border-radius:12px; font-weight:700; background:#132033 !important; color:#f4f7ff !important; border:1px solid #304461 !important;}
    .stDownloadButton > button {width:100%; min-height:2.7rem; border-radius:12px; font-weight:700; background:#132033 !important; color:#f4f7ff !important; border:1px solid #304461 !important;}

    /* Champs sombres lisibles */
    div[data-baseweb="input"], div[data-baseweb="textarea"], div[data-baseweb="select"] {
        background:#111a2a !important;
        border:1px solid #2c3b55 !important;
        border-radius:10px !important;
        color:#ffffff !important;
    }
    div[data-baseweb="input"] > div,
    div[data-baseweb="textarea"] > div,
    div[data-baseweb="select"] > div {
        background:#111a2a !important;
        color:#ffffff !important;
    }
    input, textarea,
    input[type="text"], input[type="number"], input[type="email"], input[type="tel"] {
        background:#111a2a !important;
        color:#ffffff !important;
        caret-color:#ffffff !important;
    }
    input::placeholder, textarea::placeholder { color:#8290a6 !important; opacity:1 !important; }
    div[data-baseweb="select"] span { color:#ffffff !important; }
    [data-baseweb="popover"], [data-baseweb="menu"] { background:#111a2a !important; color:#ffffff !important; }
    [role="option"] { background:#111a2a !important; color:#ffffff !important; }
    [role="option"]:hover { background:#1b2b45 !important; }

    .copy-wrap { margin-top: .3rem; }
    .copy-btn {
        width:100%; padding:13px 16px; border-radius:12px; border:1px solid #477bd3;
        background:#17498f; color:white; font-weight:800; cursor:pointer; font-size:16px;
    }
    .copy-btn:active { transform: scale(.99); }
    .app-header {
        display:flex; align-items:center; justify-content:space-between; gap:12px;
        margin: 0 0 6px 0;
    }
    .app-title {
        font-size:1.55rem; font-weight:800; color:#ffffff; line-height:1.2;
    }
    .version-badge {
        background:#122542; border:1px solid #345886; color:#cfe2ff;
        border-radius:999px; padding:6px 10px; font-size:.78rem; font-weight:800;
        white-space:nowrap;
    }
    .version-card {
        background:#0b1728; border:1px solid #263753; border-radius:12px;
        padding:10px 12px; margin-bottom:10px;
    }

    /* Calendrier date_input : correction blanc sur blanc */
    [data-baseweb="calendar"], [data-baseweb="calendar"] * {
        background:#111a2a !important;
        color:#ffffff !important;
        fill:#ffffff !important;
    }
    [data-baseweb="calendar"] button {
        background:#16233a !important;
        color:#ffffff !important;
        border-color:#304461 !important;
    }
    [aria-label*="calendar"], [aria-label*="Calendar"] {
        background:#111a2a !important;
        color:#ffffff !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

APP_VERSION = "v0.14.0"
APP_VERSION_LABEL = "Version 14"
APP_UPDATED_AT = "09/07/2026"

PAGES = [
    "Contact", "Logement", "Motivation", "Projet", "Engagement", "Décideurs & RDV", "Documents", "Rapport"
]

DEFAULTS = {
    "prenom": "", "nom": "", "telephone": "", "email": "",
    "proprietaire": None, "maison_ind": None, "res_principale": None,
    "surface": None, "annee_construction": None, "cp": "", "ville": "", "adresse": "",
    "zone": None, "foyer": None, "rfr": "", "enfants_charge": None,
    "situation_mr": None, "situation_mme": None, "revenus_mensuels": None, "age_mr": None, "age_mme": None,
    "chauffage": "", "chauffage_gaz": False, "chauffage_fioul": False, "chauffage_elec": False, "chauffage_bois": False, "chauffage_pac": False, "chauffage_clim": False, "chauffage_autre": "", "age_chaudiere": None, "ecs": "", "emetteurs": "",
    "facture": "", "fonctionne": None,
    "declencheur": "", "gene": "", "changement": "", "urgence": None,
    "projets": [], "projet_autre": "",
    "pret_lancer": None, "empechement": "", "budget": None, "mensualite": None, "credits": "",
    "decideurs": "", "tous_presents": None, "creneau_ok": None,
    "date_rdv": None, "heure_rdv": None, "duree": None,
    "docs_prets": None, "mail_docs": None, "mail_recu": None,
    "notes_perso": "", "notes": "", "statut": None,
    "page": 0,
}

for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v

# IMPORTANT STREAMLIT : quand on navigue page par page, Streamlit peut nettoyer
# les valeurs des widgets qui ne sont plus affichés. Cette ligne "ré-attache"
# chaque valeur à session_state pour éviter de perdre les informations en changeant de page.
for k in list(DEFAULTS.keys()):
    st.session_state[k] = st.session_state.get(k, DEFAULTS[k])


def yn(label, key):
    return st.radio(label, ["Oui", "Non", "À confirmer"], key=key, horizontal=True, index=None)


def done(value):
    if value is None:
        return False
    if isinstance(value, str):
        return value.strip() != "" and value != "À qualifier"
    if isinstance(value, list):
        return len(value) > 0
    return True


def climate_zone_from_cp(cp):
    cp = (cp or "").strip().upper().replace(" ", "")
    if len(cp) < 2:
        return None
    # Les codes postaux corses commencent par 20 et relèvent de la zone H3.
    if cp.startswith("20"):
        return "H3"
    dep = cp[:2]
    h1 = {"01","02","03","05","08","10","14","15","19","21","23","25","27","28","38","39","42","43","45","51","52","54","55","57","58","59","60","61","62","63","67","68","69","70","71","73","74","76","77","78","80","87","88","89","90","91","92","93","94","95"}
    h2 = {"04","07","09","12","16","17","18","22","24","26","29","31","32","33","35","36","37","40","41","44","46","47","48","49","50","53","56","64","65","72","79","81","82","84","85","86"}
    h3 = {"06","11","13","30","34","66","83"}
    if dep in h1: return "H1"
    if dep in h2: return "H2"
    if dep in h3: return "H3"
    return None

def parse_hour(value):
    if value is None:
        return None
    if isinstance(value, time):
        return value
    if isinstance(value, str) and value:
        try:
            h, m = value.split(":")
            return time(int(h), int(m))
        except Exception:
            return None
    return None

def heating_label():
    vals = []
    for key, label in [
        ("chauffage_gaz", "Gaz"), ("chauffage_fioul", "Fioul"), ("chauffage_elec", "Électrique"),
        ("chauffage_bois", "Bois / granulés"), ("chauffage_pac", "Pompe à chaleur existante"),
        ("chauffage_clim", "Climatisation réversible"),
    ]:
        if st.session_state.get(key):
            vals.append(label)
    other = (st.session_state.get("chauffage_autre") or "").strip()
    if other:
        vals.append(other)
    return " + ".join(vals)

def house_age_from_year():
    y = st.session_state.get("annee_construction")
    if y:
        return max(0, datetime.now().year - int(y))
    return None

def half_hour_options():
    out = []
    for h in range(8, 23):
        for m in (0, 30):
            if h == 22 and m == 30:
                continue
            out.append(f"{h:02d}:{m:02d}")
    return out


def project_label():
    parts = list(st.session_state.projets or [])
    if st.session_state.projet_autre.strip():
        parts.append(st.session_state.projet_autre.strip())
    return " + ".join(parts) if parts else "Non renseigné"


def compute_score():
    score = 0
    plus, minus = [], []
    if st.session_state.proprietaire == "Oui": score += 10; plus.append("propriétaire")
    elif st.session_state.proprietaire == "Non": score -= 40; minus.append("pas propriétaire")
    if st.session_state.maison_ind == "Oui": score += 8; plus.append("maison individuelle")
    elif st.session_state.maison_ind == "Non": score -= 25; minus.append("pas maison individuelle")
    if st.session_state.res_principale == "Oui": score += 6; plus.append("résidence principale")
    if st.session_state.surface and st.session_state.surface >= 90: score += 8; plus.append("surface intéressante")
    if house_age_from_year() and house_age_from_year() >= 15: score += 4; plus.append("maison suffisamment ancienne")
    if st.session_state.chauffage_gaz or st.session_state.chauffage_fioul: score += 8; plus.append("chauffage compatible remplacement")
    if st.session_state.age_chaudiere and st.session_state.age_chaudiere >= 15: score += 8; plus.append("système ancien")
    if st.session_state.declencheur.strip(): score += 8; plus.append("motivation identifiée")
    if st.session_state.gene.strip(): score += 8
    if st.session_state.projets or st.session_state.projet_autre.strip(): score += 5; plus.append("type de projet identifié")
    if st.session_state.pret_lancer == "Oui": score += 18; plus.append("intention de décision positive")
    elif st.session_state.pret_lancer == "Non": score -= 30; minus.append("pas prêt à lancer")
    if st.session_state.tous_presents == "Oui": score += 16; plus.append("décideurs présents")
    elif st.session_state.tous_presents == "Non": score -= 35; minus.append("décideurs absents")
    if st.session_state.docs_prets == "Oui": score += 7; plus.append("documents prêts")
    if st.session_state.mail_recu == "Oui": score += 5; plus.append("mail documents confirmé")
    hr = parse_hour(st.session_state.heure_rdv)
    if hr and hr >= time(18,0):
        score -= 10; minus.append("RDV après 18h")
    return max(0, min(100, score)), plus, minus


def missing_items():
    checks = [
        ("Prénom", st.session_state.prenom), ("Nom", st.session_state.nom), ("Téléphone", st.session_state.telephone),
        ("Code postal", st.session_state.cp), ("Ville", st.session_state.ville),
        ("Zone", st.session_state.zone),
        ("Nombre d’enfants à charge", st.session_state.enfants_charge),
        ("Situation professionnelle Mr/Mme", st.session_state.situation_mr or st.session_state.situation_mme),
        ("Revenus mensuels", st.session_state.revenus_mensuels),
        ("Âge Mr/Mme", st.session_state.age_mr or st.session_state.age_mme),
        ("Propriétaire", st.session_state.proprietaire),
        ("Maison individuelle", st.session_state.maison_ind), ("Résidence principale", st.session_state.res_principale),
        ("Surface", st.session_state.surface), ("Année de construction", st.session_state.annee_construction),
        ("Chauffage actuel", heating_label()), ("Âge système", st.session_state.age_chaudiere),
        ("Motivation", st.session_state.declencheur), ("Gêne principale", st.session_state.gene),
        ("Type de projet", st.session_state.projets or st.session_state.projet_autre),
        ("Engagement", st.session_state.pret_lancer), ("Décideurs", st.session_state.decideurs),
        ("Tous décideurs présents", st.session_state.tous_presents), ("Adresse complète", st.session_state.adresse),
        ("Date RDV", st.session_state.date_rdv), ("Heure RDV", st.session_state.heure_rdv),
        ("Documents", st.session_state.docs_prets), ("Mail documents reçu", st.session_state.mail_recu),
    ]
    return [label for label, val in checks if not done(val)]


def script(text):
    st.markdown(f"<div class='script'><b>Phrase à dire</b><br>{text}</div>", unsafe_allow_html=True)


def box(text, kind="warn"):
    st.markdown(f"<div class='{kind}'>{text}</div>", unsafe_allow_html=True)


def report_value(value, suffix=""):
    """Return clean value for report or None if empty/non renseigné."""
    if value is None:
        return None
    if isinstance(value, str):
        v = value.strip()
        if not v or v in ["Non renseigné", "Non renseignée", "Sélectionner"]:
            return None
        return v + suffix
    if isinstance(value, list):
        return ", ".join(value) if value else None
    return f"{value}{suffix}"


def add_line(lines, label, value, suffix=""):
    v = report_value(value, suffix)
    if v is not None:
        lines.append(f"{label} : {v}")


def add_section(lines, title, items):
    section = []
    for label, value, suffix in items:
        v = report_value(value, suffix)
        if v is not None:
            section.append(f"{label} : {v}")
    if section:
        lines.append(f"\n{title}")
        lines.extend(section)


def generate_report():
    score, plus, minus = compute_score()
    now = datetime.now(ZoneInfo("Europe/Paris")).strftime("%d/%m/%Y %H:%M")
    missing = missing_items()
    rdv = None
    if st.session_state.date_rdv and st.session_state.heure_rdv:
        rdv = f"{st.session_state.date_rdv.strftime('%d/%m/%Y')} à {st.session_state.heure_rdv}"

    lines = [
        "RAPPORT RDV - ASSISTANT TÉLÉPRO ÉNERGIE",
        f"Généré le : {now}",
        "",
        f"SCORE QUALITÉ : {score}/100",
    ]
    add_line(lines, "Statut", st.session_state.statut)
    add_line(lines, "Projet", project_label() if project_label() != "Non renseigné" else None)

    # Le rapport commence volontairement par les informations techniques.
    add_section(lines, "INFOS TECHNIQUES - LOGEMENT", [
        ("Propriétaire", st.session_state.proprietaire, ""),
        ("Maison individuelle", st.session_state.maison_ind, ""),
        ("Résidence principale", st.session_state.res_principale, ""),
        ("Surface", st.session_state.surface, " m²"),
        ("Année de construction", st.session_state.annee_construction, ""),
        ("Zone climatique auto", st.session_state.zone, ""),
    ])

    add_section(lines, "INSTALLATION ACTUELLE", [
        ("Chauffage", heating_label(), ""),
        ("Âge système", st.session_state.age_chaudiere, " ans"),
        ("Fonctionne correctement", st.session_state.fonctionne, ""),
        ("Eau chaude", st.session_state.ecs, ""),
        ("Émetteurs", st.session_state.emetteurs, ""),
        ("Facture / consommation mensuelle", st.session_state.facture, ""),
    ])

    add_section(lines, "INFOS FINANCIÈRES / FOYER", [
        ("Nombre de personnes au foyer", st.session_state.foyer, ""),
        ("Nombre d’enfants à charge", st.session_state.enfants_charge, ""),
        ("RFR", st.session_state.rfr, ""),
        ("Situation professionnelle Monsieur", st.session_state.situation_mr, ""),
        ("Situation professionnelle Madame", st.session_state.situation_mme, ""),
        ("Revenus mensuels du foyer", st.session_state.revenus_mensuels, " €"),
        ("Âge Monsieur", st.session_state.age_mr, " ans"),
        ("Âge Madame", st.session_state.age_mme, " ans"),
        ("Crédits contractés / objets", st.session_state.credits, ""),
    ])

    add_section(lines, "MOTIVATION CLIENT", [
        ("Déclencheur", st.session_state.declencheur, ""),
        ("Gêne principale", st.session_state.gene, ""),
        ("Ce que ça changerait", st.session_state.changement, ""),
        ("Urgence", st.session_state.urgence, ""),
    ])

    add_section(lines, "ENGAGEMENT / BUDGET", [
        ("Prêt à lancer si faisable + rentable + budget OK", st.session_state.pret_lancer, ""),
        ("Ce qui pourrait bloquer", st.session_state.empechement, ""),
        ("Budget", st.session_state.budget, ""),
        ("Fourchette mensualité acceptable", st.session_state.mensualite, ""),
    ])

    add_section(lines, "DÉCIDEURS", [
        ("Décideurs", st.session_state.decideurs, ""),
        ("Tous présents", st.session_state.tous_presents, ""),
        ("Second RDV payant expliqué", st.session_state.creneau_ok, ""),
    ])

    add_section(lines, "RENDEZ-VOUS", [
        ("Date / heure", rdv, ""),
        ("Durée annoncée", st.session_state.duree, ""),
    ])

    add_section(lines, "DOCUMENTS", [
        ("Documents prêts ou envoyables", st.session_state.docs_prets, ""),
        ("Mail/SMS liste documents envoyé", st.session_state.mail_docs, ""),
        ("Réception du mail/SMS confirmée", st.session_state.mail_recu, ""),
    ])

    if plus:
        lines.append("\nPOINTS FORTS")
        lines.extend(["- " + x for x in plus])
    if minus:
        lines.append("\nPOINTS DE VIGILANCE")
        lines.extend(["- " + x for x in minus])
    if missing:
        lines.append("\nCE QUI RESTE À COMPLÉTER")
        lines.extend(["- " + x for x in missing])

    if st.session_state.notes_perso.strip():
        lines.append("\nNOTES PERSO PERMANENTES")
        lines.append(st.session_state.notes_perso.strip())
    if st.session_state.notes.strip():
        lines.append("\nNOTES BRUTES DAVID")
        lines.append(st.session_state.notes.strip())

    # Coordonnées volontairement à la fin du rapport.
    add_section(lines, "COORDONNÉES PROSPECT", [
        ("Prénom / Nom", (st.session_state.prenom + " " + st.session_state.nom).strip(), ""),
        ("Téléphone", st.session_state.telephone, ""),
        ("Email", st.session_state.email, ""),
        ("Adresse RDV", st.session_state.adresse, ""),
        ("Code postal", st.session_state.cp, ""),
        ("Ville", st.session_state.ville, ""),
    ])

    return "\n".join(lines) + "\n"


def go(delta):
    st.session_state.page = max(0, min(len(PAGES) - 1, st.session_state.page + delta))


def reset_all():
    for k, v in DEFAULTS.items():
        if k != "page":
            st.session_state[k] = v
    st.session_state.page = 0

# SIDEBAR NAVIGATION
score, plus, minus = compute_score()
missing = missing_items()

with st.sidebar:
    st.markdown("## 📞 Télépro")
    st.markdown(f"""
    <div class='version-card'>
        <b>🟢 Version installée</b><br>
        {APP_VERSION} — {APP_VERSION_LABEL}<br>
        <span class='mini'>Mise à jour : {APP_UPDATED_AT}</span>
    </div>
    """, unsafe_allow_html=True)
    st.caption("Navigation rapide")
    selected = st.radio("Étapes", PAGES, index=st.session_state.page, label_visibility="collapsed")
    st.session_state.page = PAGES.index(selected)
    st.divider()
    st.metric("Score", f"{score}/100")
    st.metric("À compléter", len(missing))
    st.markdown("### 📝 Note perso")
    st.text_area(
        "Visible sur toutes les pages",
        key="notes_perso",
        height=180,
        placeholder="Remarques client, objection importante, détail à ne pas oublier..."
    )
    st.caption("Cette note reste affichée pendant tout l’appel et sera reprise dans le rapport final.")
    if st.button("🆕 Nouveau lead"):
        reset_all()
        st.rerun()
    with st.expander("Règles rapides", expanded=False):
        st.markdown("""
        - Dire **expert / ingénieur thermicien**, jamais commercial.
        - Ne pas citer l’installateur si cela crée de la méfiance.
        - Ne jamais demander : **avez-vous déjà fait une étude ?**
        - Ne pas annoncer les primes H1 si zone H2/H3 ou inconnue.
        - Le projet précis arrive après la motivation.
        - Date, heure et adresse complète uniquement à la fin.
        - Éviter les RDV après 18h.
        """)

page = st.session_state.page
st.markdown(f"""
<div class='app-header'>
  <div class='app-title'>📞 Assistant Télépro Énergie</div>
  <div class='version-badge'>{APP_VERSION}</div>
</div>
""", unsafe_allow_html=True)
st.caption(f"Mode sombre iPad — navigation rapide, faible surcharge, qualification terrain. Dernière mise à jour : {APP_UPDATED_AT}.")
st.progress((page + 1) / len(PAGES))

h1, h2, h3 = st.columns(3)
h1.metric("Étape", f"{page+1}/{len(PAGES)}")
h2.metric("Score", f"{score}/100")
h3.metric("À compléter", len(missing))
st.markdown(f"### {PAGES[page]}")

# PAGES
if page == 0:
    script("Bonjour, je vous appelle suite à votre demande d’informations concernant les solutions pour améliorer votre confort et réduire vos dépenses d’énergie. Je vérifie simplement quelques éléments pour savoir si cela mérite de mandater un expert / ingénieur thermicien sur place.")
    st.text_input("Prénom du prospect", key="prenom", placeholder="Ex : Jean")
    st.text_input("Nom du prospect", key="nom", placeholder="Ex : Martin")
    st.text_input("Téléphone", key="telephone", placeholder="06...")
    st.text_input("Email", key="email", placeholder="email@exemple.fr")
    st.text_input("Code postal", key="cp", placeholder="Ex : 77100")
    auto_zone = climate_zone_from_cp(st.session_state.cp)
    st.session_state.zone = auto_zone
    if auto_zone:
        box(f"Zone climatique détectée automatiquement : {auto_zone}", "ok")
    elif st.session_state.cp.strip():
        box("Zone climatique non détectée automatiquement pour ce code postal. L’expert vérifiera.", "warn")
    st.text_input("Ville", key="ville", placeholder="Ex : Meaux")
    box("Ne demande pas l’adresse complète au début. On la demande à la fin, quand le rendez-vous est justifié.", "warn")

elif page == 1:
    script("Je vais vous poser quelques questions rapides sur la maison. On commence par la partie technique pour éviter de déplacer un expert si le logement ne correspond pas aux critères de faisabilité.")
    st.markdown("#### 1. Infos techniques logement")
    yn("Propriétaire ?", "proprietaire")
    yn("Maison individuelle ?", "maison_ind")
    yn("Résidence principale ?", "res_principale")
    st.number_input("Surface chauffée approximative (m²)", min_value=0, max_value=500, step=5, key="surface", value=None, placeholder="Ex : 120")
    st.number_input("Année de construction", min_value=1800, max_value=datetime.now().year, step=1, key="annee_construction", value=None, placeholder="Ex : 1985")
    auto_zone = climate_zone_from_cp(st.session_state.cp)
    st.session_state.zone = auto_zone
    if auto_zone:
        box(f"Zone climatique détectée automatiquement depuis le code postal : {auto_zone}", "ok")
    else:
        box("Zone climatique non déterminée : ne pas annoncer de primes précises avant vérification.", "warn")
    if st.session_state.zone in ["H2", "H3", "À confirmer"] or st.session_state.zone is None:
        box("Ne pas annoncer les conditions H1 si la zone est H2/H3 ou incertaine. Dire que l’expert vérifiera les aides exactes.", "warn")

    st.markdown("#### 2. Installation actuelle")
    st.markdown("Chauffage actuel")
    c1, c2 = st.columns(2)
    with c1:
        st.checkbox("Gaz", key="chauffage_gaz")
        st.checkbox("Électrique", key="chauffage_elec")
        st.checkbox("Pompe à chaleur existante", key="chauffage_pac")
    with c2:
        st.checkbox("Fioul", key="chauffage_fioul")
        st.checkbox("Bois / granulés", key="chauffage_bois")
        st.checkbox("Climatisation réversible", key="chauffage_clim")
    st.text_input("Autre chauffage / précision", key="chauffage_autre", placeholder="Ex : gaz + cheminée, chaudière hybride...")
    st.session_state.chauffage = heating_label()
    st.number_input("Âge chaudière / système actuel", min_value=0, max_value=60, step=1, key="age_chaudiere", value=None)
    yn("Le système fonctionne encore correctement ?", "fonctionne")
    st.text_input("Production d’eau chaude", key="ecs", placeholder="Chaudière, ballon électrique, BTD...")
    st.text_input("Émetteurs", key="emetteurs", placeholder="Radiateurs à eau, plancher chauffant, splits...")
    st.text_input("Facture / consommation mensuelle actuelle", key="facture", placeholder="Ex : 220 €/mois gaz + électricité")

    st.markdown("#### 3. Infos financières / foyer")
    st.number_input("Nombre de personnes au foyer", min_value=0, max_value=12, step=1, key="foyer", value=None)
    st.number_input("Nombre d’enfants à charge", min_value=0, max_value=10, step=1, key="enfants_charge", value=None)
    st.text_input("Revenu fiscal de référence si connu", key="rfr", placeholder="Ne pas bloquer si le client ne sait pas")
    st.selectbox("Situation professionnelle Monsieur", [None, "CDI", "CDD", "Intérim", "Indépendant", "Retraité depuis moins de 2 ans", "Retraité depuis plus de 2 ans", "Sans emploi", "Autre / à préciser"], key="situation_mr", format_func=lambda x: "Sélectionner" if x is None else x)
    st.selectbox("Situation professionnelle Madame", [None, "CDI", "CDD", "Intérim", "Indépendant", "Retraitée depuis moins de 2 ans", "Retraitée depuis plus de 2 ans", "Sans emploi", "Autre / à préciser"], key="situation_mme", format_func=lambda x: "Sélectionner" if x is None else x)
    st.number_input("Revenus mensuels du foyer (€)", min_value=0, max_value=30000, step=100, key="revenus_mensuels", value=None, placeholder="Ex : 3200")
    st.text_area("Crédits en cours + objet", key="credits", placeholder="Ex : crédit auto 280 €/mois, prêt conso 120 €/mois, crédit immo 850 €/mois...", height=80)
    c_age1, c_age2 = st.columns(2)
    with c_age1:
        st.number_input("Âge de Monsieur", min_value=0, max_value=110, step=1, key="age_mr", value=None)
    with c_age2:
        st.number_input("Âge de Madame", min_value=0, max_value=110, step=1, key="age_mme", value=None)
    box("Financement : si contrat de travail, demander seulement la dernière fiche de paie. Si retraité depuis moins de 2 ans, demander l’attestation de retraite. Ne pas surcharger le client avec des documents inutiles.", "ok")

elif page == 2:
    script("Avant de parler du type de solution, j’ai besoin de comprendre ce qui vous a poussé à faire la demande. L’expert ne se déplace que si le projet peut avoir un vrai intérêt pour vous.")
    st.text_area("Qu’est-ce qui vous a donné envie de demander des renseignements ?", key="declencheur", placeholder="Écrire les mots exacts du client", height=80)
    st.text_area("Qu’est-ce qui vous gêne le plus aujourd’hui ?", key="gene", placeholder="Facture, panne, confort, bruit, froid, chaleur, hausse...", height=80)
    st.text_area("Si on réglait ce problème, qu’est-ce que ça changerait pour vous ?", key="changement", placeholder="Projection concrète", height=80)
    st.selectbox("Urgence ressentie", [None, "Faible", "Moyenne", "Forte", "Très forte"], key="urgence", format_func=lambda x: "Sélectionner" if x is None else x)

elif page == 3:
    script("D’après ce que vous me dites, on va identifier la famille de solutions à vérifier. Le choix définitif appartient à l’expert après faisabilité, rentabilité et contraintes de la maison.")
    st.multiselect(
        "Projet à vérifier",
        ["PAC air/eau", "PAC air/air", "Isolation thermique extérieure (ITE)", "Panneaux photovoltaïques", "Ballon thermodynamique (BTD)", "Eau chaude sanitaire", "À déterminer"],
        key="projets",
        placeholder="Sélectionner un ou plusieurs projets"
    )
    st.text_input("Autre / combinaison personnalisée", key="projet_autre", placeholder="Ex : PAC air/eau + BTD + panneaux photovoltaïques")
    if "PAC air/air" in st.session_state.projets:
        box("PAC air/air : parler confort, climatisation/chauffage, économies selon usage. Ne pas mélanger avec PAC air/eau.", "ok")
    if "PAC air/eau" in st.session_state.projets:
        box("PAC air/eau : vérifier radiateurs à eau / plancher chauffant, chaudière actuelle, ECS, surface.", "ok")
    if "Panneaux photovoltaïques" in st.session_state.projets:
        box("Photovoltaïque : éviter toute promesse de rentabilité avant validation de l’orientation, toiture, consommation et contraintes techniques.", "warn")

elif page == 4:
    script("Je préfère être clair : l’expert ne vient pas pour une visite commerciale classique. Il vient vérifier la faisabilité, la rentabilité et décider s’il est pertinent de monter un dossier qui pourra passer en commission sous 24h si tout est complet.")
    yn("Si c’est faisable, rentable, que les aides sont cohérentes et que la mensualité reste confortable, êtes-vous prêt à lancer le projet ?", "pret_lancer")
    st.text_area("Qu’est-ce qui pourrait vous empêcher d’aller au bout ?", key="empechement", placeholder="Comparer, demander au fils, budget, confiance, travaux, délai...", height=90)
    st.selectbox("Budget / posture", [None, "Comptant possible", "Financement souhaité", "Mensualité obligatoire", "Budget très sensible", "Refus de tout financement"], key="budget", format_func=lambda x: "Sélectionner" if x is None else x)
    st.selectbox("Fourchette de mensualité acceptable", [None, "Moins de 50 €", "50 à 100 €", "100 à 150 €", "150 à 200 €", "200 € et plus", "Ne veut pas répondre"], key="mensualite", format_func=lambda x: "Sélectionner" if x is None else x)
    box("Ne donne pas de prix fixe. Cadrer seulement une fourchette de mensualité possible, sans détailler la durée au téléphone.", "warn")
    box("Ne demande jamais : “avez-vous déjà fait une étude ?” Cela crée un réflexe de comparaison.", "bad")

elif page == 5:
    script("Pour éviter un deuxième déplacement payant et pour que l’expert puisse statuer correctement, toutes les personnes qui prendront la décision doivent être présentes.")
    st.text_input("Qui prend la décision finale ?", key="decideurs", placeholder="Ex : Monsieur + Madame / fils / indivision...")
    yn("Tous les décideurs seront présents ?", "tous_presents")
    yn("Le prospect a compris qu’on veut éviter un second RDV payant ?", "creneau_ok")
    st.markdown("#### Adresse et créneau uniquement maintenant")
    st.text_input("Adresse complète du rendez-vous", key="adresse", placeholder="N°, rue, complément")
    st.date_input("Date du RDV", key="date_rdv", value=None, format="DD/MM/YYYY")
    st.selectbox("Heure du RDV", [None] + half_hour_options(), key="heure_rdv", format_func=lambda x: "Sélectionner" if x is None else x)
    st.selectbox("Durée annoncée", [None, "1h30 à 2h", "2h", "2h à 2h30"], key="duree", format_func=lambda x: "Sélectionner" if x is None else x)
    hr = parse_hour(st.session_state.heure_rdv)
    if hr and hr >= time(18,0):
        box("RDV après 18h : à éviter, surtout avec familles/enfants. Risque de fatigue, repas, enfants, baisse d’attention et annulation.", "bad")

elif page == 6:
    script("Pour que l’expert gagne du temps et puisse décider rapidement si le dossier peut être monté, pouvez-vous préparer les documents dans un dossier, en PDF ou en photos bien lisibles ?")
    yn("Documents prêts ou envoyables rapidement ?", "docs_prets")
    yn("Mail/SMS avec liste des documents envoyé ?", "mail_docs")
    yn("Le client confirme la bonne réception du mail/SMS ?", "mail_recu")
    st.markdown("""
    **Liste à envoyer au client :**
    - dernier avis d’imposition complet, toutes les pages ;
    - taxe foncière ;
    - facture énergie récente ;
    - pièces d’identité des propriétaires ;
    - RIB si dossier lancé ;
    - si financement envisagé : dernière fiche de paie si contrat de travail ; attestation de retraite si retraité depuis moins de 2 ans.
    """)
    box("Phrase : “Je reste avec vous quelques secondes, pouvez-vous me confirmer que vous avez bien reçu le mail avec la liste des documents ?”", "ok")

elif page == 7:
    st.selectbox("Statut final du lead", [None, "RDV validé", "RDV à confirmer", "À rappeler", "Non closable", "Hors critères"], key="statut", format_func=lambda x: "Sélectionner" if x is None else x)
    st.markdown("#### Note perso permanente")
    st.info(st.session_state.notes_perso or "Aucune note perso permanente saisie dans le volet de gauche.")
    st.text_area("Notes libres pendant l’appel", key="notes", placeholder="Mots exacts du client, objections, ambiance, détails utiles terrain...", height=110)
    report = generate_report()
    if score >= 80:
        box("Très bon RDV potentiel si les points obligatoires sont complets.", "ok")
    elif score >= 55:
        box("RDV moyen : renforcer motivation, décideurs, documents ou engagement avant validation.", "warn")
    else:
        box("RDV fragile : attention aux kilomètres inutiles.", "bad")

    escaped_report = html.escape(report)
    components.html(f"""
    <div class='copy-wrap'>
      <textarea id="crm_report" style="position:absolute;left:-9999px;top:-9999px;">{escaped_report}</textarea>
      <button class="copy-btn" onclick="navigator.clipboard.writeText(document.getElementById('crm_report').value).then(()=>{{this.innerText='✅ Rapport copié pour Alltoo / CRM';}})">📋 Copier le rapport pour Alltoo / CRM</button>
    </div>
    """, height=62)
    st.text_area("Rapport complet à copier dans Alltoo / WhatsApp", value=report, height=420)
    st.download_button("Télécharger le rapport .txt", data=report, file_name=f"rapport_rdv_{st.session_state.prenom}_{st.session_state.nom}.txt", mime="text/plain")
    with st.expander("Ce qui reste à compléter", expanded=True):
        if missing:
            for item in missing:
                st.write("- " + item)
        else:
            st.success("Tout est complet.")

st.divider()

left, mid, right = st.columns([1,1,1])
with left:
    st.button("⬅️ Retour", on_click=go, args=(-1,), disabled=page == 0)
with mid:
    if st.button("🆕 Nouveau lead"):
        reset_all()
        st.rerun()
with right:
    st.button("Suivant ➡️", on_click=go, args=(1,), disabled=page == len(PAGES) - 1)
