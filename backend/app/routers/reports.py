@router.get("/debug-sql")
def debug_sql(
    date_from: date = Query(...),
    date_to: date = Query(...),
    trans_type: str | None = None,
    db: Session = Depends(get_db),
):
    from sqlalchemy import text
    
    start_date = datetime.combine(date_from, time.min)
    end_date = datetime.combine(date_to, time.max)
    
    # Direct SQL with no ORM
    sql = text("""
        SELECT 
            COUNT(*) as total_count
        FROM "TransactionMain"
        WHERE "TransDate" BETWEEN :start_date AND :end_date
        AND "TransType" = :trans_type
    """)
    
    result = db.execute(sql, {
        "start_date": start_date,
        "end_date": end_date,
        "trans_type": trans_type
    })
    
    row = result.fetchone()
    
    # Get sample data
    sample_sql = text("""
        SELECT 
            "TransNo",
            "TransDate",
            "TransType",
            "Net_Total"
        FROM "TransactionMain"
        WHERE "TransDate" BETWEEN :start_date AND :end_date
        AND "TransType" = :trans_type
        LIMIT 5
    """)
    
    sample_result = db.execute(sample_sql, {
        "start_date": start_date,
        "end_date": end_date,
        "trans_type": trans_type
    })
    
    samples = sample_result.fetchall()
    
    return {
        "debug": {
            "start_date": str(start_date),
            "end_date": str(end_date),
            "trans_type": trans_type
        },
        "count": row[0] if row else 0,
        "samples": [
            {
                "TransNo": s[0],
                "TransDate": str(s[1]),
                "TransType": s[2],
                "Net_Total": float(s[3]) if s[3] else 0
            }
            for s in samples
        ]
    }
