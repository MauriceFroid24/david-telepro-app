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
    .stApp { background: #080c14; color: #eef4ff; }
    [data-testid="stSidebar"] { background: #0d1422; border-right: 1px solid #1e2a3d; }
    [data-testid="stSidebar"] * { color: #e6edf7; }
    .block-container {padding-top: 0.8rem; padding-bottom: 1.1rem; max-width: 820px;}
    h1 {font-size: 1.55rem; margin-bottom: 0.1rem; color:#ffffff;}
    h2, h3 {margin-top: 0.5rem; color:#ffffff;}
    .script {
        background:#101a2b; border:1px solid #263753; border-left:5px solid #75a7ff; border-radius:14px;
        padding:13px 15px; margin:10px 0 16px 0; line-height:1.45; color:#eaf1ff;
    }
    .script b { color:#9fc0ff; }
    .ok {background:#0f2a1d; border:1px solid #236a44; color:#bff6d4; border-radius:12px; padding:10px; margin:8px 0;}
    .warn {background:#2d230b; border:1px solid #7d641c; color:#ffe6a3; border-radius:12px; padding:10px; margin:8px 0;}
    .bad {background:#311317; border:1px solid #7d2d37; color:#ffc7cf; border-radius:12px; padding:10px; margin:8px 0;}
    .mini {font-size:.88rem; color:#aeb9ca;}
    div[data-testid="stMetric"] {background:#0d1422; border:1px solid #1e2a3d; border-radius:12px; padding:8px;}
    div[data-testid="stMetric"] * { color:#eef4ff !important; }
    .stButton > button {width:100%; min-height:2.7rem; border-radius:12px; font-weight:700;}
    .stDownloadButton > button {width:100%; min-height:2.7rem; border-radius:12px; font-weight:700;}
    div[data-baseweb="input"], div[data-baseweb="textarea"], div[data-baseweb="select"] { background:#111a2a; border-radius:10px; }
    textarea, input { color:#ffffff !important; }
    .copy-wrap { margin-top: .3rem; }
    .copy-btn {
        width:100%; padding:13px 16px; border-radius:12px; border:1px solid #477bd3;
        background:#17498f; color:white; font-weight:800; cursor:pointer; font-size:16px;
    }
    .copy-btn:active { transform: scale(.99); }
    </style>
    """,
    unsafe_allow_html=True,
)

PAGES = [
    "Contact", "Logement", "Motivation", "Projet", "Engagement", "Décideurs & RDV", "Documents", "Rapport"
]

DEFAULTS = {
    "prenom": "", "nom": "", "telephone": "", "email": "",
    "proprietaire": None, "maison_ind": None, "res_principale": None,
    "surface": None, "age_maison": None, "cp": "", "ville": "", "adresse": "",
    "zone": None, "foyer": None, "rfr": "",
    "chauffage": "", "age_chaudiere": None, "ecs": "", "emetteurs": "",
    "facture": "", "fonctionne": None,
    "declencheur": "", "gene": "", "changement": "", "urgence": None,
    "projets": [], "projet_autre": "",
    "pret_lancer": None, "empechement": "", "budget": None, "mensualite": None,
    "decideurs": "", "tous_presents": None, "creneau_ok": None,
    "date_rdv": None, "heure_rdv": None, "duree": None,
    "docs_prets": None, "mail_docs": None, "mail_recu": None,
    "notes": "", "statut": None,
    "page": 0,
}

for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v


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
    if st.session_state.age_maison and st.session_state.age_maison >= 15: score += 4; plus.append("maison suffisamment ancienne")
    if st.session_state.chauffage.lower().strip() in ["gaz", "fioul"]: score += 8; plus.append("chauffage compatible remplacement")
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
    if st.session_state.heure_rdv and st.session_state.heure_rdv >= time(18,0):
        score -= 10; minus.append("RDV après 18h")
    return max(0, min(100, score)), plus, minus


def missing_items():
    checks = [
        ("Prénom", st.session_state.prenom), ("Nom", st.session_state.nom), ("Téléphone", st.session_state.telephone),
        ("Code postal", st.session_state.cp), ("Ville", st.session_state.ville),
        ("Zone", st.session_state.zone), ("Propriétaire", st.session_state.proprietaire),
        ("Maison individuelle", st.session_state.maison_ind), ("Résidence principale", st.session_state.res_principale),
        ("Surface", st.session_state.surface), ("Âge de la maison", st.session_state.age_maison),
        ("Chauffage actuel", st.session_state.chauffage), ("Âge système", st.session_state.age_chaudiere),
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


def generate_report():
    score, plus, minus = compute_score()
    now = datetime.now(ZoneInfo("Europe/Paris")).strftime("%d/%m/%Y %H:%M")
    missing = missing_items()
    rdv = "Non fixé"
    if st.session_state.date_rdv and st.session_state.heure_rdv:
        rdv = f"{st.session_state.date_rdv.strftime('%d/%m/%Y')} à {st.session_state.heure_rdv.strftime('%H:%M')}"
    return f"""RAPPORT RDV - ASSISTANT TÉLÉPRO ÉNERGIE
Généré le : {now}

SCORE QUALITÉ : {score}/100
Statut : {st.session_state.statut or 'Non renseigné'}
Projet : {project_label()}

PROSPECT
Prénom / Nom : {st.session_state.prenom} {st.session_state.nom}
Téléphone : {st.session_state.telephone}
Email : {st.session_state.email or 'Non renseigné'}
Adresse RDV : {st.session_state.adresse or 'Non renseignée'} - {st.session_state.cp} {st.session_state.ville}
Zone : {st.session_state.zone or 'Non renseignée'}

LOGEMENT
Propriétaire : {st.session_state.proprietaire}
Maison individuelle : {st.session_state.maison_ind}
Résidence principale : {st.session_state.res_principale}
Surface : {st.session_state.surface or 'Non renseignée'} m²
Âge de la maison : {st.session_state.age_maison or 'Non renseigné'} ans
Foyer : {st.session_state.foyer or 'Non renseigné'} personnes
RFR : {st.session_state.rfr or 'Non renseigné'}

INSTALLATION ACTUELLE
Chauffage : {st.session_state.chauffage or 'Non renseigné'}
Âge système : {st.session_state.age_chaudiere or 'Non renseigné'} ans
Fonctionne correctement : {st.session_state.fonctionne}
Eau chaude : {st.session_state.ecs or 'Non renseigné'}
Émetteurs : {st.session_state.emetteurs or 'Non renseigné'}
Facture / consommation : {st.session_state.facture or 'Non renseigné'}

MOTIVATION CLIENT
Déclencheur : {st.session_state.declencheur or 'Non renseigné'}
Gêne principale : {st.session_state.gene or 'Non renseigné'}
Ce que ça changerait : {st.session_state.changement or 'Non renseigné'}
Urgence : {st.session_state.urgence or 'Non renseignée'}

ENGAGEMENT / BUDGET
Prêt à lancer si faisable + rentable + budget OK : {st.session_state.pret_lancer}
Ce qui pourrait bloquer : {st.session_state.empechement or 'Non renseigné'}
Budget : {st.session_state.budget or 'Non renseigné'}
Fourchette mensualité acceptable : {st.session_state.mensualite or 'Non renseignée'}

DÉCIDEURS
Décideurs : {st.session_state.decideurs or 'Non renseigné'}
Tous présents : {st.session_state.tous_presents}
Second RDV payant expliqué : {st.session_state.creneau_ok}

RENDEZ-VOUS
Date / heure : {rdv}
Durée annoncée : {st.session_state.duree or 'Non renseignée'}
Adresse complète : {st.session_state.adresse or 'Non renseignée'}

DOCUMENTS
Documents prêts ou envoyables : {st.session_state.docs_prets}
Mail/SMS liste documents envoyé : {st.session_state.mail_docs}
Réception du mail/SMS confirmée : {st.session_state.mail_recu}

POINTS FORTS
- {(chr(10)+'- ').join(plus) if plus else 'Aucun point fort renseigné'}

POINTS DE VIGILANCE
- {(chr(10)+'- ').join(minus) if minus else 'Aucun point de vigilance majeur'}

CE QUI RESTE À COMPLÉTER
- {(chr(10)+'- ').join(missing) if missing else 'Tout est complet'}

NOTES BRUTES DAVID
{st.session_state.notes or 'Aucune note'}
"""


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
    st.caption("Navigation rapide")
    selected = st.radio("Étapes", PAGES, index=st.session_state.page, label_visibility="collapsed")
    st.session_state.page = PAGES.index(selected)
    st.divider()
    st.metric("Score", f"{score}/100")
    st.metric("À compléter", len(missing))
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
st.title("📞 Assistant Télépro Énergie")
st.caption("Mode sombre iPad — navigation rapide, faible surcharge, qualification terrain.")
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
    st.text_input("Ville", key="ville", placeholder="Ex : Meaux")
    box("Ne demande pas l’adresse complète au début. On la demande à la fin, quand le rendez-vous est justifié.", "warn")

elif page == 1:
    script("Je vais vous poser quelques questions rapides sur la maison. L’objectif est d’éviter de déplacer un expert si le logement ne correspond pas du tout aux critères techniques.")
    yn("Propriétaire ?", "proprietaire")
    yn("Maison individuelle ?", "maison_ind")
    yn("Résidence principale ?", "res_principale")
    st.number_input("Surface chauffée approximative (m²)", min_value=0, max_value=500, step=5, key="surface", value=None, placeholder="Ex : 120")
    st.number_input("Âge approximatif de la maison", min_value=0, max_value=250, step=1, key="age_maison", value=None, placeholder="Ex : 35")
    st.selectbox("Zone climatique", [None, "H1", "H2", "H3", "À confirmer"], key="zone", format_func=lambda x: "Sélectionner" if x is None else x)
    if st.session_state.zone in ["H2", "H3", "À confirmer"]:
        box("Ne pas annoncer les conditions H1 si la zone est H2/H3 ou incertaine. Dire que l’expert vérifiera les aides exactes.", "warn")
    st.number_input("Nombre de personnes au foyer", min_value=0, max_value=12, step=1, key="foyer", value=None)
    st.text_input("Revenu fiscal de référence si connu", key="rfr", placeholder="Ne pas bloquer si le client ne sait pas")
    st.text_input("Chauffage actuel", key="chauffage", placeholder="Gaz, fioul, électrique...")
    st.number_input("Âge chaudière / système actuel", min_value=0, max_value=60, step=1, key="age_chaudiere", value=None)
    yn("Le système fonctionne encore correctement ?", "fonctionne")
    st.text_input("Production d’eau chaude", key="ecs", placeholder="Chaudière, ballon électrique, BTD...")
    st.text_input("Émetteurs", key="emetteurs", placeholder="Radiateurs à eau, plancher chauffant, splits...")
    st.text_input("Facture / consommation actuelle", key="facture", placeholder="Ex : 220 €/mois gaz + électricité")

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
    st.time_input("Heure du RDV", key="heure_rdv", value=None, step=900)
    st.selectbox("Durée annoncée", [None, "1h30 à 2h", "2h", "2h à 2h30"], key="duree", format_func=lambda x: "Sélectionner" if x is None else x)
    if st.session_state.heure_rdv and st.session_state.heure_rdv >= time(18,0):
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
    - justificatifs de revenus si financement envisagé.
    """)
    box("Phrase : “Je reste avec vous quelques secondes, pouvez-vous me confirmer que vous avez bien reçu le mail avec la liste des documents ?”", "ok")

elif page == 7:
    st.selectbox("Statut final du lead", [None, "RDV validé", "RDV à confirmer", "À rappeler", "Non closable", "Hors critères"], key="statut", format_func=lambda x: "Sélectionner" if x is None else x)
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
