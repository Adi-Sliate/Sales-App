from datetime import date, datetime, time
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from ..database import get_db
from .. import crud

router = APIRouter(prefix="/reports", tags=["Reports"])


def to_float(value):
    return float(value) if value is not None else 0.0



@router.get("/sales-summary")
def sales_summary(
    date_from: date = Query(...),
    date_to: date = Query(...),
    trans_type: str | None = None,
    created_user: str | None = None,
    terminal_id: str | None = None,
    db: Session = Depends(get_db),
):
    start_date = datetime.combine(date_from, time.min)
    end_date = datetime.combine(date_to, time.max)

    rows = crud.get_sales_summary(
        db=db,
        date_from=start_date,
        date_to=end_date,
        trans_type=trans_type,
        created_user=created_user,
        terminal_id=terminal_id,
    )

    total_net = sum(to_float(row.net_total) for row in rows)
    total_discount = sum(to_float(row.discount_amt) for row in rows)

    data = []
    for row in rows:
        data.append({
            "trans_no": to_float(row.trans_no) if row.trans_no is not None else 0,
            "trans_date": row.trans_date.isoformat() if row.trans_date else None,
            "trans_type": row.trans_type,
            "billing_name": row.billing_name,
            "created_user": row.created_user,
            "terminal_id": row.terminal_id,
            "net_total": to_float(row.net_total),
            "discount_amt": to_float(row.discount_amt),
            "cash_amt": to_float(row.cash_amt),
            "chq_amt": to_float(row.chq_amt),
            "credit_amt": to_float(row.credit_amt),
            "cancel_status": row.cancel_status,
        })

    return {
        "count": len(rows),
        "total_net": total_net,
        "total_discount": total_discount,
        "data": data,
    }


@router.get("/item-summary")
def item_summary(
    date_from: date = Query(...),
    date_to: date = Query(...),
    item_code: str | None = None,
    item_name: str | None = None,
    trans_type: str | None = None,
    created_user: str | None = None,
    db: Session = Depends(get_db),
):
    start_date = datetime.combine(date_from, time.min)
    end_date = datetime.combine(date_to, time.max)

    rows = crud.get_item_summary(
        db=db,
        date_from=start_date,
        date_to=end_date,
        item_code=item_code,
        item_name=item_name,
        trans_type=trans_type,
        created_user=created_user,
    )

    total_amount = sum(to_float(row.total_amount) for row in rows)
    total_qty = sum(to_float(row.total_qty) for row in rows)

    data = []
    for row in rows:
        data.append({
            "item_code": row.item_code,
            "item_name": row.item_name,
            "total_qty": to_float(row.total_qty),
            "total_free_qty": to_float(row.total_free_qty),
            "total_discount": to_float(row.total_discount),
            "total_amount": to_float(row.total_amount),
        })

    return {
        "count": len(rows),
        "total_qty": total_qty,
        "total_amount": total_amount,
        "data": data,
    }


@router.get("/quantity-report")
def quantity_report(
    date_from: date = Query(...),
    date_to: date = Query(...),
    item_code: str | None = None,
    item_name: str | None = None,
    trans_type: str | None = None,
    created_user: str | None = None,
    db: Session = Depends(get_db),
):
    start_date = datetime.combine(date_from, time.min)
    end_date = datetime.combine(date_to, time.max)

    rows = crud.get_quantity_report(
        db=db,
        date_from=start_date,
        date_to=end_date,
        item_code=item_code,
        item_name=item_name,
        trans_type=trans_type,
        created_user=created_user,
    )

    data = []
    total_qty = 0.0
    total_amount = 0.0

    for row in rows:
        qty = to_float(row.qty)
        free_qty = to_float(row.free_qty)
        rate = to_float(row.rate)
        amount = to_float(row.amount) if row.amount is not None else (qty * rate)
        current_cost = to_float(row.current_cost)
        discount_amt = to_float(row.discount_amt)

        total_qty += qty
        total_amount += amount

        data.append({
            "trans_no": to_float(row.trans_no) if row.trans_no is not None else 0,
            "trans_date": row.trans_date.isoformat() if row.trans_date else None,
            "trans_type": row.trans_type,
            "created_user": row.created_user,
            "item_code": row.item_code,
            "item_name": row.item_name,
            "qty": qty,
            "free_qty": free_qty,
            "rate": rate,
            "amount": amount,
            "current_cost": current_cost,
            "discount_amt": discount_amt,
        })

    return {
        "count": len(data),
        "total_qty": total_qty,
        "total_amount": total_amount,
        "data": data,
    }


@router.get("/bill-report")
def bill_report(
    date_from: date = Query(...),
    date_to: date = Query(...),
    trans_type: str | None = None,
    created_user: str | None = None,
    terminal_id: str | None = None,
    bill_no: float | None = None,
    db: Session = Depends(get_db),
):
    start_date = datetime.combine(date_from, time.min)
    end_date = datetime.combine(date_to, time.max)

    rows = crud.get_bill_report(
        db=db,
        date_from=start_date,
        date_to=end_date,
        trans_type=trans_type,
        created_user=created_user,
        terminal_id=terminal_id,
        bill_no=bill_no,
    )

    total_net = sum(to_float(row.net_total) for row in rows)
    total_discount = sum(to_float(row.discount_amt) for row in rows)

    data = []
    for row in rows:
        data.append({
            "trans_no": to_float(row.trans_no) if row.trans_no is not None else 0,
            "trans_date": row.trans_date.isoformat() if row.trans_date else None,
            "trans_type": row.trans_type,
            "billing_name": row.billing_name,
            "created_user": row.created_user,
            "terminal_id": row.terminal_id,
            "net_total": to_float(row.net_total),
            "discount_amt": to_float(row.discount_amt),
            "cash_amt": to_float(row.cash_amt),
            "chq_amt": to_float(row.chq_amt),
            "credit_amt": to_float(row.credit_amt),
            "cancel_status": row.cancel_status,
            "comments": row.comments,
        })

    return {
        "count": len(rows),
        "total_net": total_net,
        "total_discount": total_discount,
        "data": data,
    }


@router.get("/gp-report")
def gp_report(
    date_from: date = Query(...),
    date_to: date = Query(...),
    item_code: str | None = None,
    item_name: str | None = None,
    trans_type: str | None = None,
    created_user: str | None = None,
    db: Session = Depends(get_db),
):
    start_date = datetime.combine(date_from, time.min)
    end_date = datetime.combine(date_to, time.max)

    rows = crud.get_gp_report(
        db=db,
        date_from=start_date,
        date_to=end_date,
        item_code=item_code,
        item_name=item_name,
        trans_type=trans_type,
        created_user=created_user,
    )

    total_qty = 0
    total_amount = 0
    total_cost = 0
    total_gp = 0

    data = []

    for row in rows:
        amount = float(row.total_amount or 0)
        cost = float(row.total_cost or 0)
        gp = amount - cost
        gp_percent = (gp / amount * 100) if amount else 0

        total_qty += float(row.total_qty or 0)
        total_amount += amount
        total_cost += cost
        total_gp += gp

        data.append({
            "item_code": row.item_code,
            "item_name": row.item_name,
            "total_qty": float(row.total_qty or 0),
            "total_amount": amount,
            "total_cost": cost,
            "gross_profit": gp,
            "gp_percent": round(gp_percent, 2),
        })

    return {
        "count": len(data),
        "total_qty": total_qty,
        "total_amount": total_amount,
        "total_cost": total_cost,
        "total_gp": total_gp,
        "data": data,
    }

@router.get("/stock-report")
def stock_report(
    item_code: str | None = None,
    item_name: str | None = None,
    db: Session = Depends(get_db),
):
    rows = crud.get_stock_report(
        db=db,
        item_code=item_code,
        item_name=item_name,
    )

    data = []
    total_units = 0.0
    total_value = 0.0

    for row in rows:
        units = to_float(row.units)
        rate = to_float(row.rate)
        value = to_float(row.value)

        total_units += units
        total_value += value

        data.append({
            "item_code": row.item_code,
            "item_name": row.item_name,
            "units": units,
            "rate": rate,
            "value": value,
        })

    return {
        "count": len(data),
        "total_units": total_units,
        "total_value": total_value,
        "data": data,
    }



@router.get("/expenses-report")
def expenses_report(
    date_from: date = Query(...),
    date_to: date = Query(...),
    name: str | None = None,
    detail: str | None = None,
    user: str | None = None,
    comments: str | None = None,
    db: Session = Depends(get_db),
):
    start_date = datetime.combine(date_from, time.min)
    end_date = datetime.combine(date_to, time.max)

    rows = crud.get_expenses_report(
        db=db,
        date_from=start_date,
        date_to=end_date,
        name=name,
        detail=detail,
        user=user,
        comments=comments,
    )

    data = []
    total_amount = 0.0

    for row in rows:
        amount = to_float(row.amount)
        total_amount += amount

        data.append({
            "name": row.name,
            "details": row.details,
            "user": row.user,
            "comments": row.comments,
            "amount": amount,
        })

    return {
        "count": len(data),
        "total_amount": total_amount,
        "data": data,
    }

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
