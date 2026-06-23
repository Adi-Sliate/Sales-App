from sqlalchemy import func
from sqlalchemy.orm import Session
from .models import TransactionMain, TransactionSub,StockItems, TmpSummaryStockBalanceCalcWithValue,Accounts, JournalMain, JournalSub



def _line_amount_expr():
    # Use stored Amount when available, otherwise fallback to Qty * Rate
    return func.coalesce(
        TransactionSub.Amount,
        func.coalesce(TransactionSub.Qty, 0) * func.coalesce(TransactionSub.Rate, 0)
    )


def _line_cost_expr():
    return (
        func.coalesce(TransactionSub.CurrentCost, 0) *
        func.coalesce(TransactionSub.Qty, 0)
    )


def get_sales_summary(
    db: Session,
    date_from,
    date_to,
    trans_type=None,
    created_user=None,
    terminal_id=None,
):
    query = (
        db.query(
            TransactionMain.TransNo.label("trans_no"),
            TransactionMain.TransDate.label("trans_date"),
            TransactionMain.TransType.label("trans_type"),
            TransactionMain.Billing_Name.label("billing_name"),
            TransactionMain.CreatedUser.label("created_user"),
            TransactionMain.Terminal_ID.label("terminal_id"),
            TransactionMain.Net_Total.label("net_total"),
            TransactionMain.DiscountAmt.label("discount_amt"),
            TransactionMain.CashAmt.label("cash_amt"),
            TransactionMain.ChqAmt.label("chq_amt"),
            TransactionMain.CreditAmt.label("credit_amt"),
            TransactionMain.Cancel_Status.label("cancel_status"),
        )
        .filter(TransactionMain.TransDate >= date_from)
        .filter(TransactionMain.TransDate <= date_to)
    )

    if trans_type:
        query = query.filter(TransactionMain.TransType == trans_type)

    if created_user:
        query = query.filter(TransactionMain.CreatedUser == created_user)

    if terminal_id:
        query = query.filter(TransactionMain.Terminal_ID == terminal_id)

    return query.order_by(
        TransactionMain.TransDate.desc(),
        TransactionMain.TransNo.desc()
    ).all()


def get_item_summary(
    db: Session,
    date_from,
    date_to,
    item_code=None,
    item_name=None,
    trans_type=None,
    created_user=None,
):
    amount_expr = _line_amount_expr()

    query = (
        db.query(
            TransactionSub.ItemCode.label("item_code"),
            TransactionSub.Item_Name.label("item_name"),
            func.sum(func.coalesce(TransactionSub.Qty, 0)).label("total_qty"),
            func.sum(func.coalesce(TransactionSub.Free_Qty, 0)).label("total_free_qty"),
            func.sum(func.coalesce(TransactionSub.Discount_Amt, 0)).label("total_discount"),
            func.sum(amount_expr).label("total_amount"),
        )
        .join(TransactionMain, TransactionMain.TransNo == TransactionSub.Trans_No)
        .filter(TransactionMain.TransDate >= date_from)
        .filter(TransactionMain.TransDate <= date_to)
        .group_by(TransactionSub.ItemCode, TransactionSub.Item_Name)
    )

    if item_code:
        query = query.filter(TransactionSub.ItemCode == item_code)

    if item_name:
        query = query.filter(TransactionSub.Item_Name.ilike(f"%{item_name}%"))

    if trans_type:
        query = query.filter(TransactionMain.TransType == trans_type)

    if created_user:
        query = query.filter(TransactionMain.CreatedUser.ilike(f"%{created_user}%"))

    return query.order_by(func.sum(amount_expr).desc()).all()


def get_quantity_report(
    db: Session,
    date_from,
    date_to,
    item_code=None,
    item_name=None,
    trans_type=None,
    created_user=None,
):
    amount_expr = _line_amount_expr()

    query = (
        db.query(
            TransactionMain.TransNo.label("trans_no"),
            TransactionMain.TransDate.label("trans_date"),
            TransactionMain.TransType.label("trans_type"),
            TransactionMain.CreatedUser.label("created_user"),
            TransactionSub.ItemCode.label("item_code"),
            TransactionSub.Item_Name.label("item_name"),
            TransactionSub.Qty.label("qty"),
            TransactionSub.Free_Qty.label("free_qty"),
            TransactionSub.Rate.label("rate"),
            amount_expr.label("amount"),
            TransactionSub.CurrentCost.label("current_cost"),
            TransactionSub.Discount_Amt.label("discount_amt"),
        )
        .join(TransactionMain, TransactionMain.TransNo == TransactionSub.Trans_No)
        .filter(TransactionMain.TransDate >= date_from)
        .filter(TransactionMain.TransDate <= date_to)
    )

    if item_code:
        query = query.filter(TransactionSub.ItemCode == item_code)

    if item_name:
        query = query.filter(TransactionSub.Item_Name.ilike(f"%{item_name}%"))

    if trans_type:
        query = query.filter(TransactionMain.TransType == trans_type)

    if created_user:
        query = query.filter(TransactionMain.CreatedUser.ilike(f"%{created_user}%"))

    return query.order_by(
        TransactionMain.TransDate.desc(),
        TransactionMain.TransNo.desc()
    ).all()


def get_bill_report(
    db: Session,
    date_from,
    date_to,
    trans_type=None,
    created_user=None,
    terminal_id=None,
    bill_no=None,
):
    query = (
        db.query(
            TransactionMain.TransNo.label("trans_no"),
            TransactionMain.TransDate.label("trans_date"),
            TransactionMain.TransType.label("trans_type"),
            TransactionMain.Billing_Name.label("billing_name"),
            TransactionMain.CreatedUser.label("created_user"),
            TransactionMain.Terminal_ID.label("terminal_id"),
            TransactionMain.Net_Total.label("net_total"),
            TransactionMain.DiscountAmt.label("discount_amt"),
            TransactionMain.CashAmt.label("cash_amt"),
            TransactionMain.ChqAmt.label("chq_amt"),
            TransactionMain.CreditAmt.label("credit_amt"),
            TransactionMain.Cancel_Status.label("cancel_status"),
            TransactionMain.Comments.label("comments"),
        )
        .filter(TransactionMain.TransDate >= date_from)
        .filter(TransactionMain.TransDate <= date_to)
    )

    if trans_type:
        query = query.filter(TransactionMain.TransType == trans_type)

    if created_user:
        query = query.filter(TransactionMain.CreatedUser.ilike(f"%{created_user}%"))

    if terminal_id:
        query = query.filter(TransactionMain.Terminal_ID.ilike(f"%{terminal_id}%"))

    if bill_no:
        query = query.filter(TransactionMain.TransNo == bill_no)

    return query.order_by(
        TransactionMain.TransDate.desc(),
        TransactionMain.TransNo.desc()
    ).all()


def get_gp_report(
    db: Session,
    date_from,
    date_to,
    item_code=None,
    item_name=None,
    trans_type=None,
    created_user=None,
):
    amount_expr = _line_amount_expr()
    cost_expr = _line_cost_expr()
    gp_expr = amount_expr - cost_expr

    query = (
        db.query(
            TransactionSub.ItemCode.label("item_code"),
            TransactionSub.Item_Name.label("item_name"),
            func.sum(func.coalesce(TransactionSub.Qty, 0)).label("total_qty"),
            func.sum(amount_expr).label("total_amount"),
            func.sum(cost_expr).label("total_cost"),
            func.sum(gp_expr).label("gross_profit"),
        )
        .join(TransactionMain, TransactionMain.TransNo == TransactionSub.Trans_No)
        .filter(TransactionMain.TransDate >= date_from)
        .filter(TransactionMain.TransDate <= date_to)
        .group_by(TransactionSub.ItemCode, TransactionSub.Item_Name)
    )

    if item_code:
        query = query.filter(TransactionSub.ItemCode == item_code)

    if item_name:
        query = query.filter(TransactionSub.Item_Name.ilike(f"%{item_name}%"))

    if trans_type:
        query = query.filter(TransactionMain.TransType == trans_type)

    if created_user:
        query = query.filter(TransactionMain.CreatedUser.ilike(f"%{created_user}%"))

    return query.order_by(func.sum(gp_expr).desc()).all()



def stock_units_expr():
    return func.coalesce(TmpSummaryStockBalanceCalcWithValue.NetBal, 0)


def stock_rate_expr():
    return func.coalesce(StockItems.Current_Cost, 0)


def stock_value_expr():
    return (
        func.coalesce(TmpSummaryStockBalanceCalcWithValue.NetBal, 0) *
        func.coalesce(StockItems.Current_Cost, 0)
    )


def get_stock_report(
    db: Session,
    item_code=None,
    item_name=None,
):
    units_expr = stock_units_expr()
    rate_expr = stock_rate_expr()
    value_expr = stock_value_expr()

    query = (
        db.query(
            StockItems.Item_Code.label("item_code"),
            StockItems.Item_Name.label("item_name"),
            units_expr.label("units"),
            rate_expr.label("rate"),
            value_expr.label("value"),
        )
        .join(
            TmpSummaryStockBalanceCalcWithValue,
            StockItems.Item_Code == TmpSummaryStockBalanceCalcWithValue.Item_Code
        )
    )

    if item_code:
        query = query.filter(StockItems.Item_Code == item_code)

    if item_name:
        query = query.filter(StockItems.Item_Name.ilike(f"%{item_name}%"))

    return query.order_by(StockItems.Item_Code.asc()).all()




def expenses_amount_expr():
    # Use Debit amount when available, otherwise Credit amount
    return func.coalesce(JournalSub.DebitAmt, JournalSub.CreditAmt, 0)


def get_expenses_report(
    db: Session,
    date_from,
    date_to,
    name=None,
    detail=None,
    user=None,
    comments=None,
):
    amount_expr = expenses_amount_expr()

    query = (
        db.query(
            Accounts.Account_Name.label("name"),
            JournalMain.Details.label("details"),
            JournalMain.CreatedUser.label("user"),
            JournalSub.Comments.label("comments"),
            amount_expr.label("amount"),
        )
        .join(JournalSub, JournalMain.JournalNo == JournalSub.JournalNo)
        .join(Accounts, Accounts.Acc_Code == JournalSub.AccCode)
        .filter(JournalMain.JournalDate >= date_from)
        .filter(JournalMain.JournalDate <= date_to)
    )

    if name:
        query = query.filter(Accounts.Account_Name.ilike(f"%{name}%"))

    if detail:
        query = query.filter(JournalMain.Details.ilike(f"%{detail}%"))

    if user:
        query = query.filter(JournalMain.CreatedUser.ilike(f"%{user}%"))

    if comments:
        query = query.filter(JournalSub.Comments.ilike(f"%{comments}%"))

    return query.order_by(
        JournalMain.JournalDate.desc(),
        Accounts.Acc_Code.asc()
    ).all()
