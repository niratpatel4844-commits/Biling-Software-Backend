from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Boolean, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.database import Base

class AccountType(enum.Enum):
    ASSET = "Asset"
    LIABILITY = "Liability"
    EQUITY = "Equity"
    REVENUE = "Revenue"
    EXPENSE = "Expense"

class AccountGroup(Base):
    __tablename__ = "account_groups"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    type = Column(Enum(AccountType))
    description = Column(String, nullable=True)

    accounts = relationship("Account", back_populates="group")

class Account(Base):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, index=True)
    group_id = Column(Integer, ForeignKey("account_groups.id"))
    code = Column(String, unique=True, index=True)
    name = Column(String, index=True)
    is_active = Column(Boolean, default=True)
    description = Column(String, nullable=True)

    group = relationship("AccountGroup", back_populates="accounts")
    journal_items = relationship("JournalEntryItem", back_populates="account")

class JournalEntry(Base):
    __tablename__ = "journal_entries"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, default=datetime.utcnow)
    reference = Column(String, nullable=True, index=True)
    description = Column(String)
    created_by_id = Column(Integer, ForeignKey("users.id"))
    
    items = relationship("JournalEntryItem", back_populates="journal_entry", cascade="all, delete-orphan")
    creator = relationship("User")

class JournalEntryItem(Base):
    __tablename__ = "journal_entry_items"

    id = Column(Integer, primary_key=True, index=True)
    journal_entry_id = Column(Integer, ForeignKey("journal_entries.id"))
    account_id = Column(Integer, ForeignKey("accounts.id"))
    debit = Column(Float, default=0.0)
    credit = Column(Float, default=0.0)
    description = Column(String, nullable=True)

    journal_entry = relationship("JournalEntry", back_populates="items")
    account = relationship("Account", back_populates="journal_items")
