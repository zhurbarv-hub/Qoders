"""
Dashboard API Endpoints for KKT Services Expiration Management System

This module provides dashboard statistics and summary endpoints:
- GET /api/dashboard/summary - Dashboard statistics and urgent deadlines
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, case
from datetime import date, timedelta
from typing import List

from backend.database import get_db
from backend.models import User, Deadline, DeadlineType
from backend.schemas import DashboardSummary, StatusBreakdown, UrgentDeadline
from backend.dependencies import get_current_active_user


# Create API router
router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


@router.get("/summary", response_model=DashboardSummary, summary="Get Dashboard Summary")
async def get_dashboard_summary(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Retrieve dashboard statistics and urgent deadlines
    
    **Statistics Calculated:**
    - total_clients: Count of all users with role='client'
    - active_clients: Count of active client users
    - total_deadlines: Count of all deadlines
    - status_breakdown:
      - green: Deadlines > 14 days until expiration
      - yellow: Deadlines 7-14 days until expiration
      - red: Deadlines 0-7 days until expiration
      - expired: Deadlines past expiration date
    - urgent_deadlines: Top 10 deadlines expiring soonest (active only)
    
    **Response:**
    - DashboardSummary object with all statistics
    
    **Authentication:**
    Requires valid JWT token
    """
    # Calculate date thresholds
    today = date.today()
    yellow_threshold = today + timedelta(days=14)
    red_threshold = today + timedelta(days=7)
    
    # 1. Total Clients (users with role='client')
    total_clients = db.query(func.count(User.id))\
                      .filter(User.role == 'client')\
                      .scalar()
    
    # 2. Active Clients
    active_clients = db.query(func.count(User.id))\
                       .filter(
                           User.role == 'client',
                           User.is_active == True
                       ).scalar()
    
    # 3. Total Deadlines
    total_deadlines = db.query(func.count(Deadline.id)).scalar()
    
    # 4. Status Breakdown
    # Count deadlines by status color
    green_count = db.query(func.count(Deadline.id))\
                    .filter(
                        Deadline.status == 'active',
                        Deadline.expiration_date >= yellow_threshold
                    ).scalar()
    
    yellow_count = db.query(func.count(Deadline.id))\
                     .filter(
                         Deadline.status == 'active',
                         Deadline.expiration_date >= red_threshold,
                         Deadline.expiration_date < yellow_threshold
                     ).scalar()
    
    red_count = db.query(func.count(Deadline.id))\
                  .filter(
                      Deadline.status == 'active',
                      Deadline.expiration_date >= today,
                      Deadline.expiration_date < red_threshold
                  ).scalar()
    
    expired_count = db.query(func.count(Deadline.id))\
                      .filter(
                          Deadline.status == 'active',
                          Deadline.expiration_date < today
                      ).scalar()
    
    status_breakdown = StatusBreakdown(
        green=green_count or 0,
        yellow=yellow_count or 0,
        red=red_count or 0,
        expired=expired_count or 0
    )
    
    # 5. Urgent Deadlines (Top 10 expiring soonest)
    urgent_deadlines_query = db.query(
        User.company_name.label('client_name'),
        DeadlineType.type_name.label('deadline_type'),
        Deadline.expiration_date,
        func.julianday(Deadline.expiration_date) - func.julianday(today)
    ).join(User)\
     .join(DeadlineType)\
     .filter(
         Deadline.status == 'active',
         Deadline.expiration_date >= today
     ).order_by(Deadline.expiration_date)\
     .limit(10)\
     .all()
    
    urgent_deadlines = []
    for row in urgent_deadlines_query:
        days_remaining = int((row.expiration_date - today).days)
        # Use company_name, fallback to user's full_name if needed
        client_display = row.client_name if row.client_name else "Клиент"
        urgent_deadlines.append(UrgentDeadline(
            client_name=client_display,
            deadline_type=row.deadline_type,
            expiration_date=row.expiration_date,
            days_remaining=days_remaining
        ))
    
    # Build and return summary
    return DashboardSummary(
        total_clients=total_clients or 0,
        active_clients=active_clients or 0,
        total_deadlines=total_deadlines or 0,
        status_breakdown=status_breakdown,
        urgent_deadlines=urgent_deadlines
    )


@router.get("/stats/by-type", summary="Get Statistics by Deadline Type")
async def get_stats_by_type(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get deadline statistics grouped by deadline type
    
    **Response:**
    Array of statistics per deadline type:
    - type_name: Deadline type name
    - total_count: Total deadlines of this type
    - active_count: Active deadlines
    - expired_count: Expired deadlines
    
    **Authentication:**
    Requires valid JWT token
    """
    today = date.today()
    
    stats = db.query(
        DeadlineType.type_name,
        func.count(Deadline.id).label('total_count'),
        func.sum(case((Deadline.status == 'active', 1), else_=0)).label('active_count'),
        func.sum(case((Deadline.expiration_date < today, 1), else_=0)).label('expired_count')
    ).outerjoin(Deadline)\
     .group_by(DeadlineType.id, DeadlineType.type_name)\
     .all()
    
    result = []
    for stat in stats:
        result.append({
            'type_name': stat.type_name,
            'total_count': stat.total_count or 0,
            'active_count': int(stat.active_count or 0),
            'expired_count': int(stat.expired_count or 0)
        })
    
    return result


@router.get("/stats/by-client", summary="Get Top Clients by Deadline Count")
async def get_stats_by_client(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get top 10 clients by number of active deadlines
    
    **Response:**
    Array of top clients:
    - client_name: Client organization name (or full name)
    - deadline_count: Number of active deadlines
    - urgent_count: Number of urgent deadlines (< 14 days)
    
    **Authentication:**
    Requires valid JWT token
    """
    today = date.today()
    urgent_threshold = today + timedelta(days=14)
    
    stats = db.query(
        User.company_name,
        User.full_name,
        func.count(Deadline.id).label('deadline_count'),
        func.sum(case((Deadline.expiration_date < urgent_threshold, 1), else_=0)).label('urgent_count')
    ).join(Deadline)\
     .filter(
         User.role == 'client',
         User.is_active == True,
         Deadline.status == 'active'
     ).group_by(User.id, User.company_name, User.full_name)\
     .order_by(func.count(Deadline.id).desc())\
     .limit(10)\
     .all()
    
    result = []
    for stat in stats:
        # Use company_name if available, otherwise full_name
        display_name = stat.company_name if stat.company_name else stat.full_name
        result.append({
            'client_name': display_name,
            'deadline_count': stat.deadline_count or 0,
            'urgent_count': int(stat.urgent_count or 0)
        })
    
    return result


# ============================================
# Testing
# ============================================

if __name__ == "__main__":
    print("=" * 60)
    print("МОДУЛЬ ДАШБОРДА")
    print("=" * 60)
    
    print("\nДоступные эндпоинты:")
    print("  • GET /api/dashboard/summary - Общая статистика дашборда")
    print("  • GET /api/dashboard/stats/by-type - Статистика по типам")
    print("  • GET /api/dashboard/stats/by-client - Топ клиентов")
    
    print("\n" + "=" * 60)
    print("✅ МОДУЛЬ ГОТОВ К ИСПОЛЬЗОВАНИЮ")
    print("=" * 60)
