import streamlit as st
from datetime import datetime, date, time
from urllib.parse import quote

st.set_page_config(page_title="Assistant Télépro David", page_icon="📞", layout="wide")

st.markdown("""
<style>
.block-container {padding-top: 1.2rem; padding-bottom: 2rem;}
.big-card {background: #f7f7f9; padding: 18px; border-radius: 16px; border: 1px solid #e6e6ea;}
.good {background:#e9f8ef;padding:12px;border-radius:12px;border-left:5px solid #19a35b;}
.mid {background:#fff6e6;padding:12px;border-radius:12px;border-left:5px solid #f0a000;}
.bad {background:#fdecec;padding:12px;border-radius:12px;border-left:5px solid #d93636;}
.small {font-size: 0.9rem; color:#555;}
</style>
""", unsafe_allow_html=True)

if "history" not in st.session_state:
    st.session_state.history = []

def yesno(label, key):
    return st.radio(label, ["Oui", "Non", "Je ne sais pas"], horizontal=True, key=key)

def score_lead(d):
    score = 0
    reasons = []
    # Base qualification
    for field, points, label in [
        ("proprietaire", 12, "propriétaire"),
        ("maison", 10, "maison individuelle"),
        ("res_principale", 8, "résidence principale"),
        ("radiateurs_eau", 8, "réseau radiateurs/plancher compatible"),
        ("decideurs_presents", 15, "tous les décideurs présents"),
    ]:
        if d.get(field) == "Oui":
            score += points; reasons.append(f"+{points} {label}")
        elif d.get(field) == "Non":
            score -= points; reasons.append(f"-{points} {label} absent")
    # Heating
    chauffage = d.get("chauffage", "")
    if chauffage in ["Gaz", "Fioul"]:
        score += 12; reasons.append("+12 chauffage gaz/fioul")
    elif chauffage:
        score += 3; reasons.append("+3 chauffage à vérifier")
    try:
        age = int(d.get("age_chaudiere", 0) or 0)
        if age >= 18:
            score += 12; reasons.append("+12 chaudière ancienne")
        elif age >= 10:
            score += 6; reasons.append("+6 chaudière intermédiaire")
    except Exception:
        pass
    try:
        surface = int(d.get("surface", 0) or 0)
        if surface >= 130:
            score += 12; reasons.append("+12 surface forte")
        elif surface >= 90:
            score += 8; reasons.append("+8 surface correcte")
        elif surface > 0:
            score -= 5; reasons.append("-5 surface faible")
    except Exception:
        pass
    try:
        facture = int(d.get("facture", 0) or 0)
        if facture >= 180:
            score += 10; reasons.append("+10 facture élevée")
        elif facture >= 120:
            score += 6; reasons.append("+6 facture significative")
    except Exception:
        pass
    # Motivation
    motivation = d.get("motivation_note", 0)
    score += int(motivation) * 3
    reasons.append(f"+{int(motivation)*3} motivation {motivation}/10")
    engagement = d.get("pret_si_ok", "")
    if engagement == "Oui":
        score += 18; reasons.append("+18 prêt à avancer si voyants au vert")
    elif engagement == "Non":
        score -= 35; reasons.append("-35 pas prêt à avancer")
    else:
        score -= 10; reasons.append("-10 engagement flou")
    # Red flags
    reds = d.get("red_flags", [])
    red_penalties = {
        "Veut juste comparer": -25,
        "Décideur absent": -25,
        "Projet dans plus de 12 mois": -20,
        "Ne veut rien changer": -40,
        "Cherche uniquement le prix": -15,
        "Méfiance forte / arnaque": -10,
        "Pas de disponibilité réelle": -25,
    }
    for r in reds:
        score += red_penalties.get(r, 0)
        reasons.append(f"{red_penalties.get(r, 0)} {r}")
    return max(0, min(100, score)), reasons

def quality_label(score):
    if score >= 75:
        return "🟢 Excellent RDV — à prioriser"
    if score >= 55:
        return "🟠 RDV moyen — à sécuriser avant déplacement"
    return "🔴 RDV risqué — éviter ou requalifier"

def build_report(d, score, reasons):
    now = datetime.now().strftime("%d/%m/%Y %H:%M")
    lines = []
    lines.append(f"RAPPORT RDV TÉLÉPRO - DAVID")
    lines.append(f"Créé le : {now}")
    lines.append("")
    lines.append(f"Score : {score}/100 - {quality_label(score)}")
    lines.append("")
    lines.append("IDENTITÉ")
    lines.append(f"Prospect : {d.get('civilite','')} {d.get('nom','')}")
    lines.append(f"Téléphone : {d.get('telephone','')}")
    lines.append(f"Adresse : {d.get('adresse','')} {d.get('cp','')} {d.get('ville','')}")
    lines.append(f"RDV : {d.get('rdv_date','')} à {d.get('rdv_time','')}")
    lines.append("")
    lines.append("QUALIFICATION")
    lines.append(f"Propriétaire : {d.get('proprietaire','')}")
    lines.append(f"Maison individuelle : {d.get('maison','')}")
    lines.append(f"Résidence principale : {d.get('res_principale','')}")
    lines.append(f"Surface : {d.get('surface','')} m²")
    lines.append(f"Chauffage actuel : {d.get('chauffage','')}")
    lines.append(f"Âge chaudière : {d.get('age_chaudiere','')} ans")
    lines.append(f"ECS : {d.get('ecs','')}")
    lines.append(f"Émetteurs : {d.get('emetteurs','')}")
    lines.append(f"Facture énergie : environ {d.get('facture','')} €/mois")
    lines.append("")
    lines.append("MOTIVATION CLIENT")
    lines.append(f"Déclencheur : {d.get('declencheur','')}")
    lines.append(f"Gêne principale : {d.get('gene','')}")
    lines.append(f"Si rien ne change : {d.get('risque','')}")
    lines.append(f"Ce que ça changerait : {d.get('changement','')}")
    lines.append(f"Motivation : {d.get('motivation_note','')}/10")
    lines.append("")
    lines.append("DÉCISION")
    lines.append(f"Décideur final : {d.get('decideur','')}")
    lines.append(f"Tous décideurs présents : {d.get('decideurs_presents','')}")
    lines.append(f"Prêt à lancer si technique + aides + budget OK : {d.get('pret_si_ok','')}")
    lines.append(f"Ce qui pourrait bloquer : {d.get('blocage','')}")
    lines.append("")
    lines.append("DOCUMENTS")
    lines.append(", ".join(d.get("docs", [])) or "Aucun document confirmé")
    lines.append("")
    lines.append("ALERTES")
    lines.append(", ".join(d.get("red_flags", [])) or "Aucune alerte majeure")
    lines.append("")
    lines.append("NOTES EXACTES DU CLIENT")
    lines.append(d.get("notes_exactes", ""))
    lines.append("")
    lines.append("RAISONS DU SCORE")
    lines.extend(reasons)
    return "\n".join(lines)

st.title("📞 Assistant Télépro David — Qualification RDV closable")
st.caption("Objectif : protéger le temps terrain, éviter les faux RDV et envoyer à Simon un maximum d’informations utiles.")

tab1, tab2, tab3, tab4 = st.tabs(["1. Appel guidé", "2. Déballe / Conseils", "3. Rapport", "4. Historique"])

with tab1:
    st.subheader("Appel guidé")
    st.info("Règle d'or : David ne prend pas un RDV, il vérifie si le déplacement de Simon mérite d'être fait.")
    with st.form("lead_form"):
        c1, c2, c3 = st.columns(3)
        with c1:
            civilite = st.selectbox("Civilité", ["Monsieur", "Madame", "Monsieur et Madame", ""])
            nom = st.text_input("Nom prospect")
            telephone = st.text_input("Téléphone")
        with c2:
            adresse = st.text_input("Adresse")
            cp = st.text_input("Code postal")
            ville = st.text_input("Ville")
        with c3:
            rdv_date = st.date_input("Date RDV", value=date.today())
            rdv_time = st.time_input("Heure RDV", value=time(10, 0))
            source = st.text_input("Source lead / campagne", value="Froid24")

        st.markdown("### 1) Qualification logement")
        q1, q2, q3 = st.columns(3)
        with q1:
            proprietaire = yesno("Propriétaire ?", "prop")
        with q2:
            maison = yesno("Maison individuelle ?", "maison")
        with q3:
            res_principale = yesno("Résidence principale ?", "res")
        q4, q5, q6 = st.columns(3)
        with q4:
            surface = st.number_input("Surface environ (m²)", min_value=0, max_value=500, value=100, step=5)
        with q5:
            chauffage = st.selectbox("Chauffage actuel", ["Gaz", "Fioul", "Électrique", "Bois", "PAC existante", "Autre", "Je ne sais pas"])
        with q6:
            age_chaudiere = st.number_input("Âge chaudière / système", min_value=0, max_value=60, value=15)
        q7, q8, q9 = st.columns(3)
        with q7:
            ecs = st.selectbox("Eau chaude", ["Chaudière", "Ballon électrique", "Ballon thermodynamique", "Autre", "Je ne sais pas"])
        with q8:
            emetteurs = st.selectbox("Émetteurs", ["Radiateurs à eau", "Plancher chauffant", "Radiateurs électriques", "Mixte", "Je ne sais pas"])
            radiateurs_eau = "Oui" if emetteurs in ["Radiateurs à eau", "Plancher chauffant", "Mixte"] else "Non"
        with q9:
            facture = st.number_input("Facture énergie estimée €/mois", min_value=0, max_value=1000, value=150, step=10)

        st.markdown("### 2) Motivation réelle")
        declencheur = st.text_area("Qu'est-ce qui vous a donné envie de demander des renseignements ?", height=70)
        gene = st.text_area("Qu'est-ce qui vous dérange le plus aujourd'hui ?", height=70)
        risque = st.text_area("Si rien ne change dans 2 ans, qu'est-ce qui risque de vous embêter ?", height=70)
        changement = st.text_area("Si on arrivait à régler ça, qu'est-ce que ça changerait pour vous ?", height=70)
        motivation_note = st.slider("Motivation réelle du prospect", 1, 10, 7)

        st.markdown("### 3) Décision et engagement")
        decideur = st.text_input("Qui prend la décision finale ?")
        decideurs_presents = yesno("Tous les décideurs seront présents au RDV ?", "decideurs")
        pret_si_ok = yesno("Si technique + aides + budget sont OK, prêt à lancer le projet ?", "pret")
        blocage = st.text_area("Qu'est-ce qui pourrait vous empêcher d'aller au bout ?", height=70)

        st.markdown("### 4) Documents et alertes")
        docs = st.multiselect("Documents que le client peut préparer", [
            "Avis d'imposition", "Taxe foncière", "Facture énergie", "Pièces d'identité propriétaires", "RIB", "Bulletins de salaire / justificatifs revenus"
        ])
        red_flags = st.multiselect("Alertes / risques", [
            "Veut juste comparer", "Décideur absent", "Projet dans plus de 12 mois", "Ne veut rien changer",
            "Cherche uniquement le prix", "Méfiance forte / arnaque", "Pas de disponibilité réelle"
        ])
        notes_exactes = st.text_area("Phrases exactes du client à transmettre à Simon", height=130)
        submitted = st.form_submit_button("✅ Générer le rapport")

    if submitted:
        data = locals().copy()
        data["rdv_date"] = rdv_date.strftime("%d/%m/%Y")
        data["rdv_time"] = rdv_time.strftime("%H:%M")
        score, reasons = score_lead(data)
        report = build_report(data, score, reasons)
        st.session_state.last_report = report
        st.session_state.last_score = score
        st.session_state.history.append({"nom": nom, "date": data["rdv_date"], "heure": data["rdv_time"], "score": score, "rapport": report})
        st.success("Rapport généré")

with tab2:
    st.subheader("Déballe recommandée")
    st.markdown("""
### Ouverture
Bonjour Monsieur / Madame [Nom], David à l'appareil. Je vous appelle concernant votre demande d'informations sur les solutions permettant de réduire votre consommation de chauffage.

J'ai simplement besoin de vérifier quelques éléments pour savoir si cela vaut vraiment la peine de déplacer un conseiller chez vous. Si je vois que le projet n'est pas pertinent, je préfère vous le dire maintenant plutôt que vous faire perdre deux heures. Est-ce que vous avez deux minutes ?

### Posture
Notre rôle n'est pas de remplacer systématiquement les chaudières. Le but est d'abord de vérifier si votre maison mérite réellement cet investissement : technique, aides, budget et économies.

### Questions à poser
1. Vous êtes bien propriétaire de la maison ?
2. C'est votre résidence principale ?
3. Vous chauffez avec quoi aujourd'hui ? Gaz, fioul, autre ?
4. Votre chaudière a environ quel âge ?
5. Vous avez des radiateurs à eau ou un plancher chauffant ?
6. Qu'est-ce qui vous a donné envie de demander des renseignements ?
7. Qu'est-ce qui vous dérange le plus aujourd'hui ?
8. Si rien ne change dans deux ans, qu'est-ce qui risque de vous embêter ?
9. Si on arrivait à régler ça, qu'est-ce que ça changerait pour vous ?
10. Qui prendra la décision finale si le projet vous convient ?
11. Si le projet est techniquement faisable, que les aides sont bien présentes et que le budget vous convient, est-ce que vous seriez prêt à lancer le projet ?

### Phrase de transparence
Je préfère être transparent avec vous : le conseiller se déplace uniquement lorsqu'il pense qu'il existe une vraie possibilité que le projet puisse aboutir. De votre côté, je vous demande la même transparence. Si aujourd'hui vous savez déjà que vous ne souhaitez rien changer, dites-le-moi maintenant, cela nous évitera de vous déranger inutilement.

### Confirmation RDV
Parfait, je vous confirme donc le rendez-vous le [date] à [heure]. Le rendez-vous dure généralement entre 1h30 et 2h. Il faudra que toutes les personnes qui décident soient présentes, sinon l'étude ne sera pas complète.

### Documents
Préparez si possible : avis d'imposition, taxe foncière, facture d'énergie, pièces d'identité des propriétaires, RIB si le dossier est lancé, et justificatifs de revenus si un financement est envisagé.

---

### À ne pas dire
❌ « Avez-vous déjà fait faire une étude ? »  
❌ « Vous pourrez comparer. »  
❌ « Je vous envoie un commercial. »  
❌ « Vous n'êtes engagé à rien. »  
❌ « C'est une démarche gouvernementale » si ce n'est pas juridiquement exact.  
❌ « Bureau d'étude agréé ANAH » si la société ne l'est pas réellement.

### À dire à la place
✅ « On va vérifier si votre maison mérite réellement cet investissement. »  
✅ « Le conseiller vient valider un projet, pas vendre systématiquement une pompe à chaleur. »  
✅ « Si ce n'est pas cohérent, il vous le dira clairement. »  
✅ « Si tout est cohérent, vous aurez tous les éléments pour décider. »
""")

with tab3:
    st.subheader("Rapport à envoyer à Simon")
    report = st.session_state.get("last_report", "Aucun rapport généré pour l'instant.")
    score = st.session_state.get("last_score", None)
    if score is not None:
        css = "good" if score >= 75 else "mid" if score >= 55 else "bad"
        st.markdown(f"<div class='{css}'><b>{quality_label(score)}</b><br>Score : {score}/100</div>", unsafe_allow_html=True)
    st.text_area("Rapport", value=report, height=500)
    if report != "Aucun rapport généré pour l'instant.":
        st.download_button("⬇️ Télécharger le rapport TXT", report, file_name="rapport_rdv_david.txt")
        mailto = "mailto:?subject=" + quote("Rapport RDV David") + "&body=" + quote(report[:1800])
        whatsapp = "https://wa.me/?text=" + quote(report[:1800])
        st.markdown(f"[📧 Envoyer par email]({mailto})")
        st.markdown(f"[💬 Envoyer par WhatsApp]({whatsapp})")

with tab4:
    st.subheader("Historique de la session")
    if not st.session_state.history:
        st.write("Aucun RDV enregistré dans cette session.")
    else:
        for h in reversed(st.session_state.history):
            st.markdown(f"**{h['nom']}** — {h['date']} {h['heure']} — Score {h['score']}/100")
            with st.expander("Voir rapport"):
                st.text(h["rapport"])
