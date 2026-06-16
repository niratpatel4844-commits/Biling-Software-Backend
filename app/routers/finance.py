from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, desc
from typing import List, Optional
from datetime import datetime
from app.database import get_db
from app.models.user import User
from app.models.finance import AccountGroup, Account, JournalEntry, JournalEntryItem, AccountType
from app.schemas.schemas import AccountGroupResponse, AccountResponse, JournalEntryResponse, JournalEntryCreate
from app.utils.auth import get_current_user, require_permission

router = APIRouter(prefix="/api/finance", tags=["Finance"])

@router.get("/accounts/groups", response_model=List[AccountGroupResponse])
def get_account_groups(db: Session = Depends(get_db), user: User = Depends(require_permission("finance", "view"))):
    return db.query(AccountGroup).all()

@router.get("/accounts", response_model=List[AccountResponse])
def get_accounts(db: Session = Depends(get_db), user: User = Depends(require_permission("finance", "view"))):
    return db.query(Account).options(joinedload(Account.group)).all()

@router.post("/journal", response_model=JournalEntryResponse)
def create_journal_entry(entry_in: JournalEntryCreate, db: Session = Depends(get_db), user: User = Depends(require_permission("finance", "create"))):
    total_debit = sum(item.debit for item in entry_in.items)
    total_credit = sum(item.credit for item in entry_in.items)
    
    if abs(total_debit - total_credit) > 0.01:
        raise HTTPException(status_code=400, detail="Journal entry must be balanced (Debits = Credits)")
        
    entry = JournalEntry(
        date=entry_in.date,
        reference=entry_in.reference,
        description=entry_in.description,
        created_by_id=user.id
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    
    for item in entry_in.items:
        je_item = JournalEntryItem(
            journal_entry_id=entry.id,
            account_id=item.account_id,
            debit=item.debit,
            credit=item.credit,
            description=item.description
        )
        db.add(je_item)
    
    db.commit()
    db.refresh(entry)
    return entry

@router.get("/journal", response_model=List[JournalEntryResponse])
def get_journal_entries(limit: int = 50, skip: int = 0, db: Session = Depends(get_db), user: User = Depends(require_permission("finance", "view"))):
    return db.query(JournalEntry).options(
        joinedload(JournalEntry.items).joinedload(JournalEntryItem.account).joinedload(Account.group)
    ).order_by(desc(JournalEntry.date)).offset(skip).limit(limit).all()

@router.get("/ledger/{account_id}")
def get_ledger(account_id: int, db: Session = Depends(get_db), user: User = Depends(require_permission("finance", "view"))):
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
        
    items = db.query(JournalEntryItem).options(
        joinedload(JournalEntryItem.journal_entry)
    ).filter(JournalEntryItem.account_id == account_id).join(JournalEntry).order_by(JournalEntry.date).all()
    
    balance = 0.0
    transactions = []
    
    is_debit_normal = account.group.type in [AccountType.ASSET, AccountType.EXPENSE]
    
    for item in items:
        if is_debit_normal:
            balance += (item.debit - item.credit)
        else:
            balance += (item.credit - item.debit)
            
        transactions.append({
            "id": item.id,
            "date": item.journal_entry.date,
            "reference": item.journal_entry.reference,
            "description": item.journal_entry.description,
            "item_description": item.description,
            "debit": item.debit,
            "credit": item.credit,
            "balance": balance
        })
        
    return {
        "account": {"id": account.id, "name": account.name, "code": account.code, "type": account.group.type},
        "transactions": transactions,
        "current_balance": balance
    }

@router.get("/trial-balance")
def get_trial_balance(db: Session = Depends(get_db), user: User = Depends(require_permission("finance", "view"))):
    balances = db.query(
        Account.id,
        Account.name,
        Account.code,
        AccountGroup.type,
        func.sum(JournalEntryItem.debit).label('total_debit'),
        func.sum(JournalEntryItem.credit).label('total_credit')
    ).join(JournalEntryItem, Account.id == JournalEntryItem.account_id).join(AccountGroup, Account.group_id == AccountGroup.id)\
    .group_by(Account.id, Account.name, Account.code, AccountGroup.type).all()
    
    result = []
    total_debit = 0
    total_credit = 0
    
    for b in balances:
        td = b.total_debit or 0
        tc = b.total_credit or 0
        is_debit_normal = b.type in [AccountType.ASSET, AccountType.EXPENSE]
        
        debit_bal = 0
        credit_bal = 0
        
        if is_debit_normal:
            bal = td - tc
            if bal > 0: debit_bal = bal
            else: credit_bal = abs(bal)
        else:
            bal = tc - td
            if bal > 0: credit_bal = bal
            else: debit_bal = abs(bal)
            
        total_debit += debit_bal
        total_credit += credit_bal
        
        result.append({
            "account_id": b.id,
            "account_name": b.name,
            "account_code": b.code,
            "type": b.type.value,
            "debit": debit_bal,
            "credit": credit_bal
        })
        
    return {
        "accounts": result,
        "total_debit": total_debit,
        "total_credit": total_credit
    }

@router.get("/pnl")
def get_pnl(db: Session = Depends(get_db), user: User = Depends(require_permission("finance", "view"))):
    balances = db.query(
        AccountGroup.type,
        Account.name,
        Account.code,
        func.sum(JournalEntryItem.debit).label('total_debit'),
        func.sum(JournalEntryItem.credit).label('total_credit')
    ).join(JournalEntryItem, Account.id == JournalEntryItem.account_id).join(AccountGroup, Account.group_id == AccountGroup.id)\
    .filter(AccountGroup.type.in_([AccountType.REVENUE, AccountType.EXPENSE]))\
    .group_by(AccountGroup.type, Account.name, Account.code).all()
    
    revenues = []
    expenses = []
    total_revenue = 0
    total_expense = 0
    
    for b in balances:
        td = b.total_debit or 0
        tc = b.total_credit or 0
        
        if b.type == AccountType.REVENUE:
            bal = tc - td # Revenue is credit normal
            revenues.append({"name": b.name, "code": b.code, "balance": bal})
            total_revenue += bal
        else:
            bal = td - tc # Expense is debit normal
            expenses.append({"name": b.name, "code": b.code, "balance": bal})
            total_expense += bal
            
    net_profit = total_revenue - total_expense
    
    return {
        "revenues": revenues,
        "expenses": expenses,
        "total_revenue": total_revenue,
        "total_expense": total_expense,
        "net_profit": net_profit
    }

@router.get("/balance-sheet")
def get_balance_sheet(db: Session = Depends(get_db), user: User = Depends(require_permission("finance", "view"))):
    balances = db.query(
        AccountGroup.type,
        Account.name,
        Account.code,
        func.sum(JournalEntryItem.debit).label('total_debit'),
        func.sum(JournalEntryItem.credit).label('total_credit')
    ).join(JournalEntryItem, Account.id == JournalEntryItem.account_id).join(AccountGroup, Account.group_id == AccountGroup.id)\
    .filter(AccountGroup.type.in_([AccountType.ASSET, AccountType.LIABILITY, AccountType.EQUITY]))\
    .group_by(AccountGroup.type, Account.name, Account.code).all()
    
    assets = []
    liabilities = []
    equity = []
    
    total_assets = 0
    total_liabilities = 0
    total_equity = 0
    
    for b in balances:
        td = b.total_debit or 0
        tc = b.total_credit or 0
        
        if b.type == AccountType.ASSET:
            bal = td - tc
            assets.append({"name": b.name, "code": b.code, "balance": bal})
            total_assets += bal
        elif b.type == AccountType.LIABILITY:
            bal = tc - td
            liabilities.append({"name": b.name, "code": b.code, "balance": bal})
            total_liabilities += bal
        elif b.type == AccountType.EQUITY:
            bal = tc - td
            equity.append({"name": b.name, "code": b.code, "balance": bal})
            total_equity += bal
            
    # Calculate current period Net Profit to add to Equity (Retained Earnings)
    pnl_data = get_pnl(db, user)
    net_profit = pnl_data["net_profit"]
    
    total_equity += net_profit
    
    return {
        "assets": assets,
        "liabilities": liabilities,
        "equity": equity,
        "total_assets": total_assets,
        "total_liabilities": total_liabilities,
        "total_equity": total_equity,
        "net_profit": net_profit
    }
