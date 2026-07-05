import streamlit as st
from datetime import datetime, time
from zoneinfo import ZoneInfo

st.set_page_config(
    page_title="Assistant Télépro Énergie",
    page_icon="📞",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ---------- STYLE ----------
st.markdown(
    """
    <style>
    .main {background:#f6f7fb;}
    .block-container {padding-top:1.4rem; padding-bottom:2rem; max-width:1180px;}
    div[data-testid="stMetric"] {background:white; border:1px solid #e6e8ef; border-radius:16px; padding:14px; box-shadow:0 4px 14px rgba(20,20,30,.04);}
    .card {background:white; border:1px solid #e7e9f0; border-radius:18px; padding:18px; margin:12px 0; box-shadow:0 4px 16px rgba(15,23,42,.05);}
    .script {background:#101828; color:white; border-radius:16px; padding:16px 18px; font-size:1.02rem; line-height:1.55; margin:10px 0 16px 0;}
    .warning {background:#fff7e6; border:1px solid #ffd591; border-radius:14px; padding:12px 14px; margin:10px 0; color:#7a4b00;}
    .danger {background:#fff1f0; border:1px solid #ffa39e; border-radius:14px; padding:12px 14px; margin:10px 0; color:#8c1d18;}
    .success {background:#ecfdf3; border:1px solid #abefc6; border-radius:14px; padding:12px 14px; margin:10px 0; color:#05603a;}
    .small {font-size:.9rem; color:#667085;}
    h1,h2,h3 {letter-spacing:-.02em;}
    .stTabs [data-baseweb="tab-list"] {gap:8px;}
    .stTabs [data-baseweb="tab"] {background:white; border-radius:12px; border:1px solid #e7e9f0; padding:10px 14px;}
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------- HELPERS ----------
def init_state():
    defaults = {
        "prenom": "", "nom": "", "telephone": "", "email": "",
        "proprietaire": None, "maison_ind": None, "res_principale": None,
        "surface": None, "cp": "", "ville": "", "adresse": "",
        "zone": "À confirmer", "foyer": None, "rfr": "",
        "chauffage": "", "age_chaudiere": None, "ecs": "", "emetteurs": "",
        "facture": "", "fonctionne": None,
        "projets": [], "projet_autre": "",
        "declencheur": "", "gene": "", "changement": "", "urgence": "À qualifier",
        "pret_lancer": None, "empechement": "", "budget": "À qualifier", "mensualite": "À qualifier",
        "decideurs": "", "tous_presents": None, "creneau_ok": None,
        "date_rdv": None, "heure_rdv": None, "duree": "1h30 à 2h",
        "docs_prets": None, "mail_docs": None, "mail_recu": None,
        "notes": "", "statut": "À qualifier",
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def yn(label, key, help_text=None):
    return st.radio(label, ["Oui", "Non", "À confirmer"], key=key, horizontal=True, index=None, help=help_text)


def done(value):
    if value is None:
        return False
    if isinstance(value, str):
        return value.strip() != "" and value != "À qualifier"
    if isinstance(value, list):
        return len(value) > 0
    return True


def compute_score():
    score = 0
    reasons_plus, reasons_minus = [], []
    if st.session_state.proprietaire == "Oui": score += 10; reasons_plus.append("propriétaire")
    elif st.session_state.proprietaire == "Non": score -= 40; reasons_minus.append("pas propriétaire")
    if st.session_state.maison_ind == "Oui": score += 8; reasons_plus.append("maison individuelle")
    elif st.session_state.maison_ind == "Non": score -= 25; reasons_minus.append("pas maison individuelle")
    if st.session_state.res_principale == "Oui": score += 6
    if st.session_state.surface and st.session_state.surface >= 90: score += 8; reasons_plus.append("surface intéressante")
    if st.session_state.chauffage.lower() in ["gaz", "fioul"]: score += 8; reasons_plus.append("chauffage compatible remplacement")
    if st.session_state.age_chaudiere and st.session_state.age_chaudiere >= 15: score += 8; reasons_plus.append("chaudière ancienne")
    if st.session_state.declencheur.strip(): score += 8; reasons_plus.append("motivation identifiée")
    if st.session_state.gene.strip(): score += 8
    if st.session_state.pret_lancer == "Oui": score += 18; reasons_plus.append("intention de décision positive")
    elif st.session_state.pret_lancer == "Non": score -= 30; reasons_minus.append("pas prêt à lancer")
    if st.session_state.tous_presents == "Oui": score += 16; reasons_plus.append("décideurs présents")
    elif st.session_state.tous_presents == "Non": score -= 35; reasons_minus.append("décideurs absents")
    if st.session_state.docs_prets == "Oui": score += 7; reasons_plus.append("documents prêts")
    if st.session_state.mail_recu == "Oui": score += 5
    if st.session_state.heure_rdv and st.session_state.heure_rdv >= time(18,0):
        score -= 10; reasons_minus.append("RDV après 18h")
    return max(0, min(100, score)), reasons_plus, reasons_minus


def missing_items():
    checks = [
        ("Prénom prospect", st.session_state.prenom),
        ("Nom prospect", st.session_state.nom),
        ("Téléphone", st.session_state.telephone),
        ("Statut propriétaire", st.session_state.proprietaire),
        ("Maison individuelle", st.session_state.maison_ind),
        ("Résidence principale", st.session_state.res_principale),
        ("Surface", st.session_state.surface),
        ("Code postal", st.session_state.cp),
        ("Ville", st.session_state.ville),
        ("Type de projet", st.session_state.projets or st.session_state.projet_autre),
        ("Chauffage actuel", st.session_state.chauffage),
        ("Âge chaudière / système", st.session_state.age_chaudiere),
        ("Motivation déclencheur", st.session_state.declencheur),
        ("Gêne principale", st.session_state.gene),
        ("Question d’engagement", st.session_state.pret_lancer),
        ("Décideurs", st.session_state.decideurs),
        ("Tous décideurs présents", st.session_state.tous_presents),
        ("Adresse complète", st.session_state.adresse),
        ("Date RDV", st.session_state.date_rdv),
        ("Heure RDV", st.session_state.heure_rdv),
        ("Documents préparés/envoyés", st.session_state.docs_prets),
        ("Mail documents reçu", st.session_state.mail_recu),
    ]
    return [label for label, val in checks if not done(val)]


def script_box(text):
    st.markdown(f"<div class='script'><b>Phrase à dire :</b><br>{text}</div>", unsafe_allow_html=True)


def info_box(text, kind="card"):
    st.markdown(f"<div class='{kind}'>{text}</div>", unsafe_allow_html=True)


def project_label():
    parts = list(st.session_state.projets)
    if st.session_state.projet_autre.strip():
        parts.append(st.session_state.projet_autre.strip())
    return " + ".join(parts) if parts else "Non renseigné"


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
Statut : {st.session_state.statut}
Projet : {project_label()}

PROSPECT
Prénom / Nom : {st.session_state.prenom} {st.session_state.nom}
Téléphone : {st.session_state.telephone}
Email : {st.session_state.email or 'Non renseigné'}
Adresse RDV : {st.session_state.adresse or 'Non renseignée'} - {st.session_state.cp} {st.session_state.ville}
Zone : {st.session_state.zone}

LOGEMENT
Propriétaire : {st.session_state.proprietaire}
Maison individuelle : {st.session_state.maison_ind}
Résidence principale : {st.session_state.res_principale}
Surface : {st.session_state.surface or 'Non renseignée'} m²
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
Urgence : {st.session_state.urgence}

ENGAGEMENT / BUDGET
Prêt à lancer si rentable + faisable + budget OK : {st.session_state.pret_lancer}
Ce qui pourrait bloquer : {st.session_state.empechement or 'Non renseigné'}
Budget : {st.session_state.budget}
Fourchette mensualité acceptable : {st.session_state.mensualite}

DÉCIDEURS
Décideurs : {st.session_state.decideurs or 'Non renseigné'}
Tous présents : {st.session_state.tous_presents}
Créneau validé : {st.session_state.creneau_ok}

RENDEZ-VOUS
Date / heure : {rdv}
Durée annoncée : {st.session_state.duree}
Adresse complète : {st.session_state.adresse or 'Non renseignée'}

DOCUMENTS
Documents prêts ou envoyés : {st.session_state.docs_prets}
Mail avec liste envoyé : {st.session_state.mail_docs}
Réception du mail confirmée : {st.session_state.mail_recu}

POINTS FORTS
- {chr(10)+'- '.join(plus) if plus else 'Aucun point fort renseigné'}

POINTS DE VIGILANCE
- {chr(10)+'- '.join(minus) if minus else 'Aucun point de vigilance majeur'}

CE QUI RESTE À COMPLÉTER
- {chr(10)+'- '.join(missing) if missing else 'Tout est complet'}

NOTES BRUTES DAVID
{st.session_state.notes or 'Aucune note'}
"""

# ---------- APP ----------
init_state()

st.title("📞 Assistant Télépro Énergie")
st.caption("Qualification rapide PAC / ITE / Photovoltaïque — objectif : RDV closable, pas simple RDV.")

score, plus, minus = compute_score()
missing = missing_items()

c1, c2, c3, c4 = st.columns(4)
c1.metric("Score RDV", f"{score}/100")
c2.metric("Champs restants", len(missing))
c3.metric("Projet", project_label()[:22] + ("…" if len(project_label()) > 22 else ""))
c4.metric("Décideurs présents", st.session_state.tous_presents or "Non fait")

if score >= 80:
    info_box("🟢 Très bon RDV potentiel : continuer uniquement si les informations clés sont complètes.", "success")
elif score >= 55:
    info_box("🟠 RDV moyen : il faut renforcer motivation, décideurs, documents ou engagement avant validation.", "warning")
else:
    info_box("🔴 RDV fragile : attention aux kilomètres inutiles. Ne pas fixer tant que les points bloquants ne sont pas clarifiés.", "danger")

with st.expander("🚫 Règles interdites / posture", expanded=False):
    st.markdown("""
    - Ne jamais dire : **commercial**. Dire : **expert**, **ingénieur thermicien**, **expert mandaté par le bureau d’études**.
    - Ne pas citer le nom de l’installateur si cela crée de la méfiance.
    - Ne jamais demander : **“avez-vous déjà fait une étude ?”** Cela crée un réflexe de comparaison.
    - Ne pas annoncer de prime H1 si la zone est H2/H3 ou inconnue.
    - Ne pas annoncer un prix fixe. Parler seulement de **fourchette de mensualité possible**, sans détailler la durée au téléphone.
    - La date, l’heure et l’adresse complète se demandent à la fin, quand le prospect est qualifié.
    """)

tabs = st.tabs(["1. Contact", "2. Projet", "3. Logement", "4. Motivation", "5. Engagement", "6. RDV", "7. Documents", "8. Rapport"])

with tabs[0]:
    st.subheader("1. Accroche et identité")
    script_box("Bonjour, je vous appelle suite à votre demande d’informations concernant les solutions pour améliorer votre confort et réduire vos dépenses d’énergie. Je vais simplement vérifier quelques éléments pour savoir si cela mérite de mandater un expert/ingénieur thermicien sur place.")
    col1, col2 = st.columns(2)
    with col1:
        st.text_input("Prénom du prospect", key="prenom", placeholder="Ex : Jean")
        st.text_input("Nom du prospect", key="nom", placeholder="Ex : Martin")
        st.text_input("Téléphone", key="telephone", placeholder="06...")
    with col2:
        st.text_input("Email", key="email", placeholder="email@exemple.fr")
        st.text_input("Code postal", key="cp", placeholder="Ex : 77100")
        st.text_input("Ville", key="ville", placeholder="Ex : Meaux")
    info_box("💡 Ne demande pas l’adresse complète maintenant. Beaucoup de prospects se ferment. On la demande uniquement à la fin, quand le rendez-vous est justifié.", "warning")

with tabs[1]:
    st.subheader("2. Type de projet")
    script_box("Avant de parler de rendez-vous, je veux comprendre ce que vous souhaitez améliorer dans votre maison : chauffage, confort d’été, isolation, facture ou production d’énergie.")
    st.multiselect(
        "Projet identifié",
        ["PAC air/eau", "PAC air/air", "Isolation thermique extérieure (ITE)", "Panneaux photovoltaïques", "Ballon thermodynamique (BTD)", "Eau chaude sanitaire", "À déterminer"],
        key="projets",
        placeholder="Sélectionner un ou plusieurs projets"
    )
    st.text_input("Autre / combinaison personnalisée", key="projet_autre", placeholder="Ex : PAC air/eau + BTD + panneaux photovoltaïques")
    st.selectbox("Zone climatique", ["À confirmer", "H1", "H2", "H3"], key="zone")
    if st.session_state.zone in ["H2", "H3"]:
        info_box("⚠️ Zone H2/H3 : ne pas annoncer les primes ou conditions H1. Rester prudent : l’expert vérifiera les aides exactes.", "warning")
    if "PAC air/air" in st.session_state.projets:
        info_box("PAC air/air : parler confort, économies selon usage, climatisation/chauffage, mais ne pas mélanger avec les aides PAC air/eau.", "card")
    if "PAC air/eau" in st.session_state.projets:
        info_box("PAC air/eau : vérifier radiateurs à eau/plancher chauffant, chaudière actuelle, ECS, surface et faisabilité extérieure/intérieure.", "card")

with tabs[2]:
    st.subheader("3. Qualification logement")
    script_box("Je vais vous poser quelques questions rapides. L’objectif n’est pas de tout décider au téléphone, mais d’éviter de déplacer un expert si votre logement ne correspond pas du tout aux critères techniques.")
    col1, col2, col3 = st.columns(3)
    with col1:
        yn("Propriétaire ?", "proprietaire")
        yn("Maison individuelle ?", "maison_ind")
        yn("Résidence principale ?", "res_principale")
    with col2:
        st.number_input("Surface chauffée approximative (m²)", min_value=0, max_value=500, step=5, key="surface", value=None, placeholder="Ex : 120")
        st.number_input("Nombre de personnes au foyer", min_value=0, max_value=12, step=1, key="foyer", value=None)
        st.text_input("Revenu fiscal de référence si connu", key="rfr", placeholder="Ne pas bloquer si le client ne sait pas")
    with col3:
        st.text_input("Chauffage actuel", key="chauffage", placeholder="Gaz, fioul, électrique...")
        st.number_input("Âge chaudière / système actuel", min_value=0, max_value=60, step=1, key="age_chaudiere", value=None)
        yn("Le système fonctionne encore correctement ?", "fonctionne")
    st.text_input("Production d’eau chaude", key="ecs", placeholder="Chaudière, ballon électrique, BTD...")
    st.text_input("Émetteurs", key="emetteurs", placeholder="Radiateurs à eau, plancher chauffant, splits...")
    st.text_input("Facture / consommation actuelle", key="facture", placeholder="Ex : 220 €/mois gaz + électricité")

with tabs[3]:
    st.subheader("4. Motivation réelle")
    script_box("Pour que l’étude soit utile, j’ai besoin de comprendre ce qui vous a poussé à faire la demande. C’est important, parce que l’expert ne se déplace que si le projet a un vrai intérêt pour vous.")
    st.text_area("Qu’est-ce qui vous a donné envie de demander des renseignements ?", key="declencheur", placeholder="Écrire les mots exacts du client", height=90)
    st.text_area("Qu’est-ce qui vous gêne le plus aujourd’hui ?", key="gene", placeholder="Facture, panne, confort, bruit, froid, chaleur, peur d’une hausse...", height=90)
    st.text_area("Si on réglait ce problème, qu’est-ce que ça changerait pour vous ?", key="changement", placeholder="Projection concrète du client", height=90)
    st.select_slider("Urgence ressentie", options=["À qualifier", "Faible", "Moyenne", "Forte", "Très forte"], key="urgence")

with tabs[4]:
    st.subheader("5. Engagement et filtre anti-faux RDV")
    script_box("Je préfère être clair : l’expert ne vient pas pour une visite commerciale classique. Il vient vérifier la faisabilité, la rentabilité et décider s’il est pertinent de monter un dossier qui pourra passer en commission sous 24h si tout est complet.")
    yn("Si c’est faisable, rentable, que les aides sont cohérentes et que la mensualité reste confortable, êtes-vous prêt à lancer le projet ?", "pret_lancer")
    st.text_area("Qu’est-ce qui pourrait vous empêcher d’aller au bout ?", key="empechement", placeholder="Comparer, demander au fils, budget, confiance, travaux, délai...", height=90)
    st.selectbox("Budget / posture", ["À qualifier", "Comptant possible", "Financement souhaité", "Mensualité obligatoire", "Budget très sensible", "Refus de tout financement"], key="budget")
    st.selectbox("Fourchette de mensualité acceptable", ["À qualifier", "Moins de 50 €", "50 à 100 €", "100 à 150 €", "150 à 200 €", "200 € et plus", "Ne veut pas répondre"], key="mensualite")
    info_box("Ne donne pas de prix fixe au téléphone. Tu peux cadrer une fourchette de mensualité pour vérifier le confort budgétaire, sans détailler la durée.", "warning")

with tabs[5]:
    st.subheader("6. Décideurs, adresse et rendez-vous")
    script_box("Pour éviter un deuxième déplacement payant et pour que l’expert puisse statuer correctement, toutes les personnes qui prendront la décision doivent être présentes.")
    st.text_input("Qui prend la décision finale ?", key="decideurs", placeholder="Ex : Monsieur + Madame / fils / indivision...")
    yn("Tous les décideurs seront présents ?", "tous_presents")
    yn("Le prospect accepte qu’on évite un second RDV payant ?", "creneau_ok")
    st.markdown("### Adresse et créneau uniquement maintenant")
    st.text_input("Adresse complète du rendez-vous", key="adresse", placeholder="N°, rue, complément")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.date_input("Date du RDV", key="date_rdv", value=None, format="DD/MM/YYYY")
    with col2:
        st.time_input("Heure du RDV", key="heure_rdv", value=None, step=900)
    with col3:
        st.selectbox("Durée annoncée", ["1h30 à 2h", "2h", "2h à 2h30"], key="duree")
    if st.session_state.heure_rdv and st.session_state.heure_rdv >= time(18,0):
        info_box("⚠️ RDV après 18h : à éviter, surtout avec familles/enfants. Risque de fatigue, repas, enfants, baisse d’attention et annulation.", "danger")

with tabs[6]:
    st.subheader("7. Documents à préparer")
    script_box("Pour que l’expert gagne du temps et puisse décider rapidement si le dossier peut être monté, pouvez-vous préparer les documents dans un dossier, soit en PDF, soit en photos bien lisibles ?")
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
    info_box("Phrase importante : “Je reste avec vous quelques secondes, pouvez-vous me confirmer que vous avez bien reçu le mail avec la liste des documents ?”", "success")

with tabs[7]:
    st.subheader("8. Rapport à copier dans Alltoo / WhatsApp")
    st.selectbox("Statut final du lead", ["À qualifier", "RDV validé", "RDV à confirmer", "À rappeler", "Non closable", "Hors critères"], key="statut")
    st.text_area("Notes libres pendant l’appel", key="notes", placeholder="Écrire ici les mots exacts du client, objections, ambiance, détails utiles terrain...", height=130)
    report = generate_report()
    st.text_area("Rapport complet", value=report, height=520)
    st.download_button("⬇️ Télécharger le rapport .txt", data=report, file_name=f"rapport_rdv_{st.session_state.prenom}_{st.session_state.nom}.txt", mime="text/plain")
    with st.expander("Ce qui reste à compléter", expanded=True):
        if missing:
            for item in missing:
                st.write("- " + item)
        else:
            st.success("Tout est complet.")
