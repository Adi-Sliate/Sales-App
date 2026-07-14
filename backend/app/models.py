# backend/app/models.py
from sqlalchemy import Column, DateTime, Numeric, NVARCHAR, CHAR, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base


class TransactionMain(Base):
    __tablename__ = "TransactionMain"

    TransNo = Column(Numeric(18, 0), primary_key=True, index=True)
    TransDate = Column(DateTime, nullable=False)
    TransType = Column(NVARCHAR(2), nullable=False)
    JournalNo = Column(Numeric(18, 0), nullable=False)
    TransSerial = Column(Numeric(18, 0), nullable=False)
    CreatedUser = Column(NVARCHAR(20), nullable=False)

    Billing_Name = Column(NVARCHAR(100))
    Billing_Address = Column(NVARCHAR(150))
    Billing_Phone = Column(NVARCHAR(100))

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

    Cancel_Status = Column(CHAR(1))
    Terminal_ID = Column(NVARCHAR(20))
    Comments = Column(NVARCHAR(500))

    items = relationship(
        "TransactionSub",
        primaryjoin="TransactionMain.TransNo == foreign(TransactionSub.Trans_No)",
        viewonly=True,
    )


class TransactionSub(Base):
    __tablename__ = "TransacitonSub"

    Trans_No = Column(Numeric(18, 0), ForeignKey("TransactionMain.TransNo"), primary_key=True)
    TransIndex = Column(Numeric(18, 0), primary_key=True)

    ItemCode = Column(NVARCHAR(25))
    Item_Name = Column(NVARCHAR(150))
    Qty = Column(Numeric(19, 4))
    Rate = Column(Numeric(19, 4))
    Discount_Rate = Column(Numeric(19, 4))
    Discount_Amt = Column(Numeric(19, 4))
    Free_Qty = Column(Numeric(19, 4))
    Amount = Column(Numeric(19, 4))
    SalesPerson = Column(NVARCHAR(10))
    SalesPersonCode = Column(NVARCHAR(10))
    CurrentCost = Column(Numeric(19, 4))


class StockItems(Base):
    __tablename__ = "StockItems"

    Item_Code = Column(NVARCHAR(25), primary_key=True)
    Item_Name = Column(NVARCHAR(150))
    Current_Cost = Column(Numeric(19, 4))


class TmpSummaryStockBalanceCalcWithValue(Base):
    __tablename__ = "tmp_Summary_Stock_Balance_Calc_With_Value"

    Item_Code = Column(NVARCHAR(25), primary_key=True)
    Item_Name = Column(NVARCHAR(150))
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
    Mac_ID = Column(NVARCHAR(20))
    IsItemHidden = Column(CHAR(1))


class Accounts(Base):
    __tablename__ = "Accounts"

    Acc_Code = Column(NVARCHAR(20), primary_key=True)
    Account_Name = Column(NVARCHAR(100), nullable=False)


class JournalMain(Base):
    __tablename__ = "JournalMain"

    JournalNo = Column(Numeric(18, 0), primary_key=True)
    JournalDate = Column(DateTime)
    Details = Column(NVARCHAR(100))
    CreatedUser = Column(NVARCHAR(20))


class JournalSub(Base):
    __tablename__ = "JournalSub"

    JournalNo = Column(Numeric(18, 0), ForeignKey("JournalMain.JournalNo"), primary_key=True)
    JournalIndex = Column(Numeric(18, 0), primary_key=True)
    AccCode = Column(NVARCHAR(20), ForeignKey("Accounts.Acc_Code"), nullable=False)

    DebitAmt = Column(Numeric(19, 4))
    CreditAmt = Column(Numeric(19, 4))
    Comments = Column(NVARCHAR(100))
