# backend/app/models.py
from sqlalchemy import Column, DateTime, Numeric, String, CHAR, ForeignKey, Integer
from sqlalchemy.orm import relationship
from .database import Base

# PostgreSQL uses VARCHAR instead of NVARCHAR
# PostgreSQL uses NUMERIC(19,4) same as SQL Server
# PostgreSQL uses INTEGER instead of NUMERIC(18,0) for IDs

class TransactionMain(Base):
    __tablename__ = "transaction_main"  # PostgreSQL lowercase naming convention

    TransNo = Column(Integer, primary_key=True, index=True)  # Changed from Numeric(18,0)
    TransDate = Column(DateTime, nullable=False)
    TransType = Column(String(2), nullable=False)  # NVARCHAR -> String
    JournalNo = Column(Integer, nullable=False)  # Numeric -> Integer
    TransSerial = Column(Integer, nullable=False)
    CreatedUser = Column(String(20), nullable=False)

    Billing_Name = Column(String(100))
    Billing_Address = Column(String(150))
    Billing_Phone = Column(String(100))

    Net_Total = Column(Numeric(19, 4))
    DiscountRate = Column(Numeric(19, 4))
    DiscountAmt = Column(Numeric(19, 4))

    CashAmt = Column(Numeric(19, 4))
    ChqAmt = Column(Numeric(19, 4))
    CreditAmt = Column(Numeric(19, 4))

    Tender_Cash = Column(Numeric(19, 4))
    Tender_CreditCard = Column(Numeric(19, 4))
    Tender_Cheuqes = Column(Numeric(19, 4))
    Tender_Balance = Column(Numeric(19, 4))

    Cancel_Status = Column(String(1))  # CHAR -> String
    Terminal_ID = Column(String(20))
    Comments = Column(String(500))

    items = relationship(
        "TransactionSub",
        primaryjoin="TransactionMain.TransNo == foreign(TransactionSub.Trans_No)",
        viewonly=True,
    )


class TransactionSub(Base):
    __tablename__ = "transaction_sub"  # Fixed typo from "TransacitonSub"

    Trans_No = Column(Integer, ForeignKey("transaction_main.TransNo"), primary_key=True)
    TransIndex = Column(Integer, primary_key=True)

    ItemCode = Column(String(25))
    Item_Name = Column(String(150))
    Qty = Column(Numeric(19, 4))
    Rate = Column(Numeric(19, 4))
    Discount_Rate = Column(Numeric(19, 4))
    Discount_Amt = Column(Numeric(19, 4))
    Free_Qty = Column(Numeric(19, 4))
    Amount = Column(Numeric(19, 4))
    SalesPerson = Column(String(10))
    SalesPersonCode = Column(String(10))
    CurrentCost = Column(Numeric(19, 4))


class StockItems(Base):
    __tablename__ = "stock_items"

    Item_Code = Column(String(25), primary_key=True)
    Item_Name = Column(String(150))
    Current_Cost = Column(Numeric(19, 4))


class TmpSummaryStockBalanceCalcWithValue(Base):
    __tablename__ = "tmp_summary_stock_balance_calc_with_value"

    Item_Code = Column(String(25), primary_key=True)
    Item_Name = Column(String(150))
    OpenStock = Column(Numeric(19, 4))
    PurchaseQty = Column(Numeric(19, 4))
    LoadingQty = Column(Numeric(19, 4))
    SalesQty = Column(Numeric(19, 4))
    RetInQty = Column(Numeric(19, 4))
    Unloading = Column(Numeric(19, 4))
    Damage = Column(Numeric(19, 4))
    PhysicalBalance = Column(Numeric(19, 4))
    RetOutQty = Column(Numeric(19, 4))
    NetBal = Column(Numeric(19, 4))
    PackSize = Column(Numeric(19, 4))
    ShortageQty = Column(Numeric(19, 4))
    ListPrice = Column(Numeric(19, 4))
    Mac_ID = Column(String(20))
    IsItemHidden = Column(String(1))  # CHAR -> String


class Accounts(Base):
    __tablename__ = "accounts"

    Acc_Code = Column(String(20), primary_key=True)
    Account_Name = Column(String(100), nullable=False)


class JournalMain(Base):
    __tablename__ = "journal_main"

    JournalNo = Column(Integer, primary_key=True)
    JournalDate = Column(DateTime)
    Details = Column(String(100))
    CreatedUser = Column(String(20))


class JournalSub(Base):
    __tablename__ = "journal_sub"

    JournalNo = Column(Integer, ForeignKey("journal_main.JournalNo"), primary_key=True)
    JournalIndex = Column(Integer, primary_key=True)
    AccCode = Column(String(20), ForeignKey("accounts.Acc_Code"), nullable=False)

    DebitAmt = Column(Numeric(19, 4))
    CreditAmt = Column(Numeric(19, 4))
    Comments = Column(String(100))
