def base_filter():
    return """
    WHERE (:agence IS NULL OR nom_agence = :agence)
    AND (:segment IS NULL OR nom_segment = :segment)
    AND (annee BETWEEN :year_start AND :year_end)
    """
def kpis_query(filters):
    sql = """
    SELECT 
        COUNT(*) AS total_transactions,
        SUM(montant) AS total_ca,
        COUNT(DISTINCT client_id) AS clients_actifs,
        AVG(montant) AS marge_moyenne
    FROM transactions_clean
    WHERE 1=1
    """

    params = {}

    if filters["agence"]:
        sql += " AND nom_agence = :agence"
        params["agence"] = filters["agence"]

    if filters["segment"]:
        sql += " AND nom_segment = :segment"
        params["segment"] = filters["segment"]

    sql += " AND annee BETWEEN :year_start AND :year_end"
    params["year_start"] = filters["year_start"]
    params["year_end"] = filters["year_end"]

    return sql, params

def monthly_query():
    return f"""
    SELECT annee, mois,
        SUM(CASE WHEN type_operation='debit' THEN montant ELSE 0 END) AS debit,
        SUM(CASE WHEN type_operation='credit' THEN montant ELSE 0 END) AS credit
    FROM transactions_clean
    {base_filter()}
    GROUP BY annee, mois
    ORDER BY annee, mois
    """

def agence_query():
    return f"""
    SELECT nom_agence, SUM(montant) AS total_ca
    FROM transactions_clean
    {base_filter()}
    GROUP BY nom_agence
    """

def segment_query():
    return f"""
    SELECT nom_segment, COUNT(*) AS total
    FROM transactions_clean
    {base_filter()}
    GROUP BY nom_segment
    """

def risk_query():
    return """
    SELECT score_credit_client, montant, categorie_risque, statut
    FROM transactions_clean
    """

def top_risk_clients():
    return """
    SELECT client_id,
           AVG(score_credit_client) AS score_credit_client,
           SUM(montant) AS total_montant
    FROM transactions_clean
    GROUP BY client_id
    ORDER BY score_credit_client ASC
    LIMIT 10
    """
