import streamlit as st
from datetime import date, time
from urllib.parse import quote

st.set_page_config(
    page_title="Maurice Télépro – Qualification RDV",
    page_icon="📞",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# -----------------------------
# STYLE
# -----------------------------
st.markdown("""
<style>
:root {
  --bg: #f6f8fb;
  --card: #ffffff;
  --text: #172033;
  --muted: #667085;
  --primary: #1f4ed8;
  --primary-soft: #eaf0ff;
  --green: #15803d;
  --orange: #c2410c;
  --red: #b91c1c;
  --border: #e5e7eb;
}
html, body, [data-testid="stAppViewContainer"] { background: var(--bg); }
[data-testid="stHeader"] { background: rgba(246,248,251,.85); }
.block-container { padding-top: 1.4rem; padding-bottom: 3rem; max-width: 1280px; }
.hero {
  background: linear-gradient(135deg, #0f172a 0%, #1f4ed8 100%);
  color: white; padding: 22px 26px; border-radius: 22px;
  box-shadow: 0 18px 50px rgba(15,23,42,.15); margin-bottom: 18px;
}
.hero h1 { margin: 0; font-size: 30px; letter-spacing: -0.02em; }
.hero p { margin: 8px 0 0; color: rgba(255,255,255,.85); font-size: 16px; }
.card {
  background: var(--card); border: 1px solid var(--border); border-radius: 18px;
  padding: 18px 20px; box-shadow: 0 10px 30px rgba(15,23,42,.05); margin-bottom: 14px;
}
.script {
  background: #0f172a; color: white; border-radius: 16px; padding: 16px 18px; margin: 10px 0 16px;
  border-left: 6px solid #60a5fa;
}
.script .label { color: #93c5fd; text-transform: uppercase; font-size: 12px; font-weight: 700; letter-spacing: .08em; margin-bottom: 6px; }
.script p { margin: 0; font-size: 18px; line-height: 1.45; }
.warning {
  background: #fff7ed; border: 1px solid #fed7aa; color: #7c2d12; border-radius: 14px; padding: 14px 16px; margin-bottom: 14px;
}
.good {
  background: #ecfdf5; border: 1px solid #bbf7d0; color: #14532d; border-radius: 14px; padding: 14px 16px; margin-bottom: 14px;
}
.bad {
  background: #fef2f2; border: 1px solid #fecaca; color: #7f1d1d; border-radius: 14px; padding: 14px 16px; margin-bottom: 14px;
}
.metric-card {
  background: white; border-radius: 18px; border: 1px solid var(--border); padding: 16px;
  text-align: center; box-shadow: 0 10px 30px rgba(15,23,42,.05);
}
.metric-card .big { font-size: 36px; font-weight: 800; margin: 0; }
.metric-card .small { color: var(--muted); font-size: 13px; margin-top: 4px; }
.pill { display:inline-block; padding: 5px 10px; border-radius: 999px; background:#eef2ff; color:#1e3a8a; font-weight:700; font-size:12px; margin-right:6px; }
textarea { min-height: 90px!important; }
.stButton > button { border-radius: 12px; font-weight: 700; min-height: 42px; }
[data-testid="stForm"] { border: 0; padding: 0; }
hr { border: none; border-top: 1px solid #e5e7eb; margin: 18px 0; }
.copybox {
  background: #101828; color: #f9fafb; padding: 18px; border-radius: 16px; white-space: pre-wrap;
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; font-size: 14px; line-height: 1.5;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# HELPERS
# -----------------------------
def init_state():
    defaults = {
        "lead_status": "",
        "owner": "Oui",
        "house": "Oui",
        "main_residence": "Oui",
        "decision_ready": "",
        "deciders_present": "",
        "address_ok": "",
        "score_notes": [],
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

def yn(label, key, help_text=None):
    return st.radio(label, ["Oui", "Non", "À confirmer"], horizontal=True, key=key, help=help_text)

def script(text):
    st.markdown(f"""
    <div class='script'>
      <div class='label'>Phrase à dire</div>
      <p>{text}</p>
    </div>
    """, unsafe_allow_html=True)

def tip(text):
    st.markdown(f"<div class='good'>✅ {text}</div>", unsafe_allow_html=True)

def alert(text):
    st.markdown(f"<div class='warning'>⚠️ {text}</div>", unsafe_allow_html=True)

def danger(text):
    st.markdown(f"<div class='bad'>⛔ {text}</div>", unsafe_allow_html=True)

def add_score(condition, points, label, notes):
    if condition:
        notes.append((points, label))
        return points
    return 0

# -----------------------------
# HEADER
# -----------------------------
st.markdown("""
<div class='hero'>
  <h1>📞 Maurice Télépro — Assistant de qualification</h1>
  <p>Objectif : qualifier vite, rassurer proprement et envoyer à Maurice des rendez-vous réellement closables.</p>
</div>
""", unsafe_allow_html=True)

left, mid, right = st.columns([1,1,1])
with left:
    st.markdown("<span class='pill'>iPad / PC</span><span class='pill'>Rapide</span><span class='pill'>Sans mémoire</span>", unsafe_allow_html=True)
with mid:
    st.caption("Les données ne sont pas sauvegardées automatiquement : copier le rapport final dans Alltoo.")
with right:
    if st.button("🔄 Nouveau lead / vider l'écran", use_container_width=True):
        st.session_state.clear()
        st.rerun()

# -----------------------------
# SIDEBAR
# -----------------------------
with st.sidebar:
    st.title("Règles d'or")
    st.write("✅ Parler d'une **validation projet**")
    st.write("✅ Dire **Maurice, expert/ingénieur**")
    st.write("✅ Demander l'adresse seulement quand le prospect est qualifié")
    st.write("✅ Fixer date/heure uniquement à la fin")
    st.divider()
    st.write("❌ Ne jamais dire Froid24")
    st.write("❌ Ne jamais dire démarche gouvernementale")
    st.write("❌ Ne pas dire bureau d'étude agréé ANAH si ce n'est pas juridiquement exact")
    st.write("❌ Ne pas demander : avez-vous déjà fait une étude ?")
    st.write("❌ Ne pas annoncer de prix cash")
    st.write("❌ Ne pas annoncer une prime H1 si le prospect est en H2/H3")
    st.write("❌ Ne pas présenter Maurice comme un commercial")

# -----------------------------
# LAYOUT
# -----------------------------
col_form, col_live = st.columns([1.35, .9], gap="large")

with col_form:
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["1. Contact", "2. Qualification", "3. Motivation", "4. Engagement", "5. RDV"])

    with tab1:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.subheader("1. Ouverture sans créer de méfiance")
        script("Bonjour, je parle bien à Monsieur / Madame ? Je m'appelle David. Je vous appelle suite à votre demande d'informations concernant les solutions pour améliorer votre chauffage ou réduire vos dépenses d'énergie. Je vais simplement vérifier si votre maison peut réellement mériter le déplacement de Maurice, notre expert thermicien. Est-ce que je peux vous poser quelques questions rapides ?")
        alert("Ne cite jamais Froid24. Ne dis pas que c'est une démarche gouvernementale. Tu réactives une demande d'information, puis tu qualifies sans créer de comparatif.")

        c1, c2 = st.columns(2)
        with c1:
            prenom = st.text_input("Prénom du prospect", placeholder="Ex : Jean")
            nom = st.text_input("Nom du prospect", placeholder="Ex : Martin")
            tel = st.text_input("Téléphone", placeholder="Ex : 06...")
        with c2:
            civilite = st.selectbox("Civilité", ["Monsieur", "Madame", "Monsieur et Madame", "À confirmer"])
            source = st.selectbox("Sujet initial du lead", ["PAC", "ITE", "Photovoltaïque", "Économies d'énergie", "Ne sait plus", "Autre"])
            email = st.text_input("Email", placeholder="Ex : client@email.fr")
            humeur = st.select_slider("Température du contact", options=["Froid", "Neutre", "Ouvert", "Très ouvert"], value="Neutre")

        rappel_demande = st.radio("Le prospect reconnaît-il la demande ?", ["Oui", "Ne sait plus", "Non"], horizontal=True)
        if rappel_demande == "Ne sait plus":
            script("Pas de souci, je comprends. On reçoit souvent des demandes faites après une simulation ou une recherche sur les aides énergie. Je ne vais pas vous déranger longtemps : je vérifie simplement si votre logement peut être concerné ou non.")
        elif rappel_demande == "Non":
            danger("Lead à risque. Reste poli, ne force pas. Tu peux qualifier très court, mais ne crée pas de faux RDV.")
        st.markdown("</div>", unsafe_allow_html=True)

    with tab2:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.subheader("2. Qualification technique rapide")
        script("Avant de parler de rendez-vous, je dois vérifier si votre logement rentre dans les critères techniques. Sinon, je préfère vous le dire tout de suite plutôt que de vous faire perdre du temps.")
        c1, c2, c3 = st.columns(3)
        with c1:
            owner = yn("Propriétaire ?", "owner")
            house = yn("Maison individuelle ?", "house")
            main_residence = yn("Résidence principale ?", "main_residence")
        with c2:
            surface = st.number_input("Surface chauffée approximative (m²)", min_value=0, max_value=500, value=0, step=5)
            occupants = st.number_input("Nombre de personnes dans le foyer", min_value=0, max_value=15, value=0, step=1)
            anciennete_maison = st.selectbox("Maison habitée depuis", ["À confirmer", "Moins de 2 ans", "2 à 5 ans", "5 à 10 ans", "+10 ans"])
            zone = st.selectbox("Zone climatique", ["À confirmer", "H1", "H2", "H3"])
        with c3:
            chauffage = st.selectbox("Chauffage actuel", ["Gaz", "Fioul", "Électricité", "Bois", "PAC déjà installée", "Autre", "À confirmer"])
            age_chaudiere = st.selectbox("Âge chaudière / système", ["À confirmer", "Moins de 5 ans", "5 à 10 ans", "10 à 15 ans", "15 à 20 ans", "+20 ans"])
            ecs = st.selectbox("Eau chaude", ["Chaudière", "Ballon électrique", "Ballon thermodynamique", "Autre", "À confirmer"])

        emetteurs = st.multiselect("Émetteurs de chaleur", ["Radiateurs à eau", "Plancher chauffant", "Radiateurs électriques", "Split / clim", "Autre", "À confirmer"], default=[])
        revenu = st.selectbox("Catégorie revenus estimée", ["Ne sait pas", "Bleu", "Jaune", "Violet", "Rose", "À vérifier avec avis d'imposition"])
        if zone in ["H2", "H3"]:
            alert("Attention : ne jamais annoncer de prime ou condition liée à la zone H1. David doit rester général : Maurice vérifiera les aides exactes selon la zone, les revenus et le logement.")
        st.markdown("</div>", unsafe_allow_html=True)

    with tab3:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.subheader("3. Motivation réelle du client")
        script("J'aimerais comprendre ce qui vous a poussé à demander des renseignements. Ce n'est pas juste une question technique : l'objectif est de savoir si le projet a un vrai intérêt pour vous.")
        motivation = st.text_area("Mot pour mot : pourquoi il s'intéresse au projet ?", placeholder="Ex : facture trop élevée, chaudière vieille, peur d'une panne, maison froide...")
        gene = st.text_area("Qu'est-ce qui le gêne le plus aujourd'hui ?", placeholder="Ex : 250€/mois de gaz, chaudière qui tombe souvent en panne...")
        projection = st.text_area("Si on règle le problème, qu'est-ce que ça change pour lui ?", placeholder="Ex : moins de charges, tranquillité, confort, anticiper la retraite...")
        facture = st.text_input("Facture / budget énergie actuel", placeholder="Ex : 180€/mois, 2 400€/an, 2 cuves de fioul/an...")
        script("Je ne vais pas vous annoncer un prix au téléphone, ce serait impossible sans voir la maison. Par contre, pour éviter de vous faire perdre du temps, si après aides le projet devait représenter une mensualité confortable, dans quelle fourchette vous vous sentiriez à l'aise ?")
        mensualite_ok = st.selectbox("Fourchette de mensualité acceptable", ["À confirmer", "Moins de 80€/mois", "80 à 120€/mois", "120 à 180€/mois", "180 à 250€/mois", "+250€/mois", "Refuse toute mensualité", "Paiement comptant uniquement"])
        urgence = st.select_slider("Urgence ressentie", options=["Aucune", "Faible", "Moyenne", "Forte", "Très forte"], value="Moyenne")
        st.markdown("</div>", unsafe_allow_html=True)

    with tab4:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.subheader("4. Engagement et objections avant RDV")
        script("Si Maurice confirme que c'est rentable, faisable techniquement, que les aides sont cohérentes et que la mensualité reste dans une zone confortable pour vous, est-ce que vous seriez prêt à monter un dossier ?")
        decision_ready = st.radio("Réponse à la question d'engagement", ["Oui", "Pourquoi pas", "Non", "À confirmer"], horizontal=True, key="decision_ready")
        if decision_ready in ["Pourquoi pas", "À confirmer"]:
            script("Je comprends. Qu'est-ce qu'il faudrait voir ou vérifier pour que vous puissiez prendre une décision sereinement ?")
        elif decision_ready == "Non":
            danger("Très probablement non closable. Ne fixe un RDV que s'il y a une vraie raison de continuer.")

        objections = st.multiselect("Objections / freins détectés", [
            "Veut comparer", "Doit demander à son conjoint", "Doit demander à ses enfants", "Peur du financement",
            "Peur des arnaques", "Ne veut pas de travaux", "Pas le budget", "Pas pressé", "A déjà une entreprise en tête",
            "Ne fait confiance qu'à son chauffagiste", "Autre"
        ])
        objection_detail = st.text_area("Détails objections — mots exacts", placeholder="Ex : 'Je veux en parler à mon fils avant de décider'...")

        script("Concrètement, qui prendra la décision finale si Maurice valide que le projet est intéressant ?")
        deciders = st.text_input("Décideur(s)", placeholder="Ex : Monsieur + Madame / fils / propriétaire indivision...")
        deciders_present = st.radio("Tous les décideurs seront présents au RDV ?", ["Oui", "Non", "À confirmer"], horizontal=True, key="deciders_present")
        if deciders_present != "Oui":
            alert("RDV fragile. Il faut expliquer qu'un 2e déplacement peut être payant ou non prioritaire, donc il faut les décideurs présents.")
            script("Comme Maurice va valider la faisabilité, la rentabilité et les conditions du projet en une seule visite, il faut que les personnes qui décident soient présentes. Sinon vous risquez d'avoir la moitié des informations et de devoir prévoir un deuxième rendez-vous, qui peut être payant ou non prioritaire.")
        st.markdown("</div>", unsafe_allow_html=True)

    with tab5:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.subheader("5. Adresse puis date/heure — seulement à la fin")
        tip("Oui, l'adresse, la date et l'heure se demandent à la fin. Avant, tu qualifies. Après, tu fixes.")
        script("Très bien. Vu ce que vous me dites, je peux organiser le passage de Maurice lui-même pour valider le projet. Pour organiser correctement son déplacement, pouvez-vous me confirmer l'adresse exacte du logement concerné ?")
        c1, c2 = st.columns([2,1])
        with c1:
            adresse = st.text_input("Adresse complète", placeholder="Numéro + rue")
        with c2:
            cp = st.text_input("Code postal", placeholder="Ex : 75000")
            ville = st.text_input("Ville", placeholder="Ex : Paris")
        adresse_ok = st.radio("Adresse confirmée ?", ["Oui", "Non", "À confirmer"], horizontal=True, key="address_ok")

        script("Je vais vous proposer un créneau. Prévoyez environ 1h30 à 2h, car Maurice va vérifier la partie technique, les aides, la rentabilité, le budget, puis décider si un dossier peut être monté et présenté en commission sous 24h, sous réserve d'un dossier complet.")
        c1, c2, c3 = st.columns(3)
        with c1:
            rdv_date = st.date_input("Date du RDV", value=date.today())
        with c2:
            rdv_time = st.time_input("Heure du RDV", value=time(10, 0))
            famille_enfants = st.radio("Famille avec enfants à la maison ?", ["Non", "Oui", "À confirmer"], horizontal=True)
        with c3:
            duree = st.selectbox("Durée annoncée", ["1h30", "2h", "2h30"])

        docs = st.multiselect("Documents à préparer / envoyer", [
            "Avis d'imposition complet", "Taxe foncière", "Facture énergie", "Pièces d'identité", "RIB", "Bulletins de salaire / justificatifs revenus", "Photos chaudière", "Photos radiateurs", "Photos compteur / tableau électrique"
        ], default=["Avis d'imposition complet", "Taxe foncière", "Facture énergie", "Pièces d'identité", "RIB"])

        script("Pour gagner du temps le jour du passage de Maurice, pouvez-vous préparer ces documents dans un dossier, soit en PDF, soit en photos bien lisibles ? Je vous envoie la liste par mail et je reste avec vous quelques secondes pour vérifier que vous l'avez bien reçue.")
        mail_envoye = st.radio("Mail liste documents envoyé ?", ["Oui", "Non", "À faire"], horizontal=True)
        mail_recu = st.radio("Client confirme réception du mail ?", ["Oui", "Non", "À confirmer"], horizontal=True)
        if mail_recu != "Oui":
            alert("Ne pas finir l'appel sans confirmer la réception du mail si possible. C'est un gros indicateur de sérieux.")

        script("Je vous confirme donc le rendez-vous avec Maurice. Il intervient comme expert thermicien mandaté par le bureau d'études. S'il valide le projet, la société d'installation sera choisie ensuite en fonction des impératifs techniques de votre maison. Si vous avez un imprévu, prévenez-nous simplement, car Maurice organise ses tournées et cela évite de bloquer un créneau inutilement.")
        commentaire_final = st.text_area("Commentaire final pour Maurice", placeholder="Ex : attention chien, portail, client méfiant, conjoint très important...")
        st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------
# LIVE PANEL / SCORE / REPORT
# -----------------------------
with col_live:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("Score RDV en direct")
    notes = []
    score = 0
    # variables may not exist before tabs render? They do render all.
    score += add_score(rappel_demande == "Oui", 8, "Reconnaît la demande", notes)
    score += add_score(humeur in ["Ouvert", "Très ouvert"], 8, "Contact ouvert", notes)
    score += add_score(owner == "Oui", 10, "Propriétaire", notes)
    score += add_score(house == "Oui", 8, "Maison individuelle", notes)
    score += add_score(main_residence == "Oui", 5, "Résidence principale", notes)
    score += add_score(surface >= 90, 8, "Surface intéressante", notes)
    score += add_score(chauffage in ["Gaz", "Fioul"], 10, "Chauffage gaz/fioul", notes)
    score += add_score(age_chaudiere in ["15 à 20 ans", "+20 ans"], 10, "Système ancien", notes)
    score += add_score(len(motivation.strip()) > 15, 10, "Motivation exprimée", notes)
    score += add_score(urgence in ["Forte", "Très forte"], 8, "Urgence forte", notes)
    score += add_score(decision_ready == "Oui", 15, "Prêt à avancer si projet cohérent", notes)
    score += add_score(deciders_present == "Oui", 10, "Décideurs présents", notes)
    score += add_score(adresse_ok == "Oui", 5, "Adresse confirmée", notes)
    score += add_score(mensualite_ok not in ["À confirmer", "Refuse toute mensualité"], 8, "Fourchette de mensualité validée", notes)
    score += add_score(mail_recu == "Oui", 7, "Mail documents reçu", notes)

    penalties = []
    if rappel_demande == "Non":
        score -= 20; penalties.append("Ne reconnaît pas la demande")
    if decision_ready == "Non":
        score -= 25; penalties.append("Refuse l'idée de lancer le projet")
    if "Veut comparer" in objections:
        score -= 15; penalties.append("Comparaison active")
    if deciders_present == "Non":
        score -= 20; penalties.append("Décideurs absents")
    if mensualite_ok == "Refuse toute mensualité":
        score -= 12; penalties.append("Refuse toute mensualité")
    if rdv_time.hour >= 18:
        score -= 10; penalties.append("RDV après 18h : plus risqué, surtout familles")
    if famille_enfants == "Oui" and rdv_time.hour >= 18:
        score -= 10; penalties.append("Famille avec enfants + RDV tardif")
    if mail_recu != "Oui":
        score -= 8; penalties.append("Réception mail documents non confirmée")
    if owner == "Non" or house == "Non":
        score -= 30; penalties.append("Critère bloquant possible")

    score = max(0, min(100, score))
    if score >= 80:
        color = "#15803d"; verdict = "🟢 Excellent — RDV à prioriser"
    elif score >= 60:
        color = "#c2410c"; verdict = "🟠 Moyen — à sécuriser"
    else:
        color = "#b91c1c"; verdict = "🔴 Risqué — attention déplacement inutile"

    st.markdown(f"""
    <div class='metric-card'>
      <p class='big' style='color:{color}'>{score}/100</p>
      <div class='small'>{verdict}</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### Points forts")
    if notes:
        for pts, label in notes[:8]:
            st.write(f"✅ {label} (+{pts})")
    else:
        st.write("Aucun point fort validé pour l'instant.")
    if penalties:
        st.markdown("### Risques")
        for p in penalties:
            st.write(f"⚠️ {p}")
    st.markdown("</div>", unsafe_allow_html=True)

    # report
    nom_complet = " ".join([x for x in [civilite if civilite != "À confirmer" else "", prenom, nom] if x]).strip() or "Prospect à compléter"
    rdv_str = f"{rdv_date.strftime('%d/%m/%Y')} à {rdv_time.strftime('%H:%M')}" if 'rdv_date' in locals() else "À compléter"
    adresse_full = ", ".join([x for x in [adresse, cp, ville] if x]).strip() or "Adresse à compléter"

    report = f"""📞 RAPPORT RDV POUR MAURICE

⭐ Score : {score}/100 — {verdict}

👤 Prospect : {nom_complet}
📱 Téléphone : {tel or 'À compléter'}
✉️ Email : {email or 'À compléter'}
🏠 Adresse : {adresse_full}
📅 RDV : {rdv_str}
⏱ Durée annoncée : {duree}
👨‍👩‍👧 Famille avec enfants : {famille_enfants}

✅ QUALIFICATION
- Propriétaire : {owner}
- Maison individuelle : {house}
- Résidence principale : {main_residence}
- Surface : {surface if surface else 'À compléter'} m²
- Foyer : {occupants if occupants else 'À compléter'} personne(s)
- Chauffage actuel : {chauffage}
- Âge système : {age_chaudiere}
- Eau chaude : {ecs}
- Émetteurs : {', '.join(emetteurs) if emetteurs else 'À compléter'}
- Zone climatique : {zone}
- Revenus estimés : {revenu}

🔥 MOTIVATION CLIENT — MOTS EXACTS
Pourquoi maintenant : {motivation or 'À compléter'}
Gêne principale : {gene or 'À compléter'}
Projection / bénéfice attendu : {projection or 'À compléter'}
Facture actuelle : {facture or 'À compléter'}
Fourchette mensualité acceptable : {mensualite_ok}
Urgence : {urgence}

🧠 ENGAGEMENT / DÉCISION
Réponse engagement : {decision_ready}
Décideur(s) : {deciders or 'À compléter'}
Décideurs présents : {deciders_present}
Objections : {', '.join(objections) if objections else 'Aucune objection forte détectée'}
Détails objections : {objection_detail or 'RAS'}

📄 DOCUMENTS À PRÉPARER / ENVOYER
{', '.join(docs) if docs else 'À compléter'}
Mail envoyé : {mail_envoye}
Réception mail confirmée : {mail_recu}

📝 COMMENTAIRE DAVID
{commentaire_final or 'RAS'}
"""

    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("Rapport prêt à copier dans Alltoo / WhatsApp")
    st.code(report, language="text")
    whatsapp_text = quote(report)
    st.markdown(f"[📲 Ouvrir WhatsApp avec le rapport](https://wa.me/?text={whatsapp_text})")
    st.download_button("⬇️ Télécharger le rapport TXT", report, file_name=f"rapport_rdv_{prenom or 'prospect'}_{nom or ''}.txt", mime="text/plain", use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("---")
st.caption("Version Maurice Télépro v4 — outil temporaire sans base de données. Sauvegarde recommandée : copier le rapport dans Alltoo après chaque appel.")
