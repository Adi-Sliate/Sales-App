# backend/app/schemas.py
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, ConfigDict


class SalesSummaryRow(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    trans_no: Decimal
    trans_date: datetime
    trans_type: str
    billing_name: str | None = None
    created_user: str
    terminal_id: str | None = None
    net_total: Decimal | None = None
    discount_amt: Decimal | None = None
    cash_amt: Decimal | None = None
    chq_amt: Decimal | None = None
    credit_amt: Decimal | None = None
    cancel_status: str | None = None


class ItemSummaryRow(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    item_code: str | None = None
    item_name: str | None = None
    total_qty: Decimal | None = None
    total_free_qty: Decimal | None = None
    total_discount: Decimal | None = None
    total_amount: Decimal | None = None


class QuantityReportRow(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    trans_no: Decimal
    trans_date: datetime
    trans_type: str
    created_user: str
    item_code: str | None = None
    item_name: str | None = None
    qty: Decimal | None = None
    free_qty: Decimal | None = None
    rate: Decimal | None = None
    amount: Decimal | None = None
    current_cost: Decimal | None = None
    discount_amt: Decimal | None = None


class BillReportRow(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    trans_no: Decimal
    trans_date: datetime
    trans_type: str
    billing_name: str | None = None
    created_user: str
    terminal_id: str | None = None
    net_total: Decimal | None = None
    discount_amt: Decimal | None = None
    cash_amt: Decimal | None = None
    chq_amt: Decimal | None = None
    credit_amt: Decimal | None = None
    cancel_status: str | None = None
    comments: str | None = None


class GPReportRow(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    item_code: str | None = None
    item_name: str | None = None
    total_qty: Decimal | None = None
    total_amount: Decimal | None = None
    total_cost: Decimal | None = None
    gross_profit: Decimal | None = None
    gp_percent: Decimal | None = None


class StockReportRow(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    item_code: str | None = None
    item_name: str | None = None
    units: Decimal | None = None
    rate: Decimal | None = None
    value: Decimal | None = None



class ExpensesReportRow(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str | None = None
    details: str | None = None
    user: str | None = None
    comments: str | None = None
    amount: Decimal | None = None
