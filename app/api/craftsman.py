from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from sqlalchemy.orm import selectinload
from app.core.database import get_db
from app.models.user import User
from app.models.craftsman import CraftsmanProfile, Trade, ServiceArea, Portfolio, TradeType
from app.schemas.craftsman import (
    CraftsmanProfileCreate,
    CraftsmanProfileUpdate,
    CraftsmanProfileResponse,
    TradeCreate,
    ServiceAreaCreate,
    PortfolioCreate,
    PortfolioResponse,
    TradeResponse,
    ServiceAreaResponse,
    CraftsmanSearchFilters,
)
from app.api.dependencies import get_current_craftsman, get_current_active_user

router = APIRouter(prefix="/api/craftsman", tags=["Craftsman Profile"])


@router.post("/profile", response_model=CraftsmanProfileResponse, status_code=status.HTTP_201_CREATED)
async def create_profile(
    profile_data: CraftsmanProfileCreate,
    current_user: User = Depends(get_current_craftsman),
    db: AsyncSession = Depends(get_db)
):
    """Create craftsman profile (craftsmen only)"""
    # Check if profile already exists
    result = await db.execute(
        select(CraftsmanProfile).where(CraftsmanProfile.user_id == current_user.id)
    )
    existing_profile = result.scalar_one_or_none()

    if existing_profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Profile already exists"
        )

    # Create profile
    profile = CraftsmanProfile(
        user_id=current_user.id,
        company_name=profile_data.company_name,
        bio=profile_data.bio,
        hourly_rate=profile_data.hourly_rate,
        years_experience=profile_data.years_experience,
        max_radius_km=profile_data.max_radius_km,
        handwerkskammer_number=profile_data.handwerkskammer_number,
        tax_id=profile_data.tax_id,
    )

    db.add(profile)
    await db.flush()

    # Add trades
    for trade_data in profile_data.trades:
        trade = Trade(
            craftsman_id=profile.id,
            trade_type=trade_data.trade_type,
            is_primary=trade_data.is_primary
        )
        db.add(trade)

    # Add service areas
    for area_data in profile_data.service_areas:
        service_area = ServiceArea(
            craftsman_id=profile.id,
            postal_code=area_data.postal_code,
            city=area_data.city,
            state=area_data.state
        )
        db.add(service_area)

    await db.commit()
    await db.refresh(profile)

    # Load relationships
    result = await db.execute(
        select(CraftsmanProfile)
        .where(CraftsmanProfile.id == profile.id)
        .options(
            selectinload(CraftsmanProfile.trades),
            selectinload(CraftsmanProfile.service_areas),
            selectinload(CraftsmanProfile.portfolio)
        )
    )
    profile = result.scalar_one()

    return CraftsmanProfileResponse.from_orm(profile)


@router.get("/profile/me", response_model=CraftsmanProfileResponse)
async def get_my_profile(
    current_user: User = Depends(get_current_craftsman),
    db: AsyncSession = Depends(get_db)
):
    """Get current craftsman's profile"""
    result = await db.execute(
        select(CraftsmanProfile)
        .where(CraftsmanProfile.user_id == current_user.id)
        .options(
            selectinload(CraftsmanProfile.trades),
            selectinload(CraftsmanProfile.service_areas),
            selectinload(CraftsmanProfile.portfolio)
        )
    )
    profile = result.scalar_one_or_none()

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )

    return CraftsmanProfileResponse.from_orm(profile)


@router.put("/profile", response_model=CraftsmanProfileResponse)
async def update_profile(
    profile_data: CraftsmanProfileUpdate,
    current_user: User = Depends(get_current_craftsman),
    db: AsyncSession = Depends(get_db)
):
    """Update craftsman profile"""
    result = await db.execute(
        select(CraftsmanProfile).where(CraftsmanProfile.user_id == current_user.id)
    )
    profile = result.scalar_one_or_none()

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found. Create one first."
        )

    # Update fields
    update_data = profile_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(profile, field, value)

    await db.commit()
    await db.refresh(profile)

    # Load relationships
    result = await db.execute(
        select(CraftsmanProfile)
        .where(CraftsmanProfile.id == profile.id)
        .options(
            selectinload(CraftsmanProfile.trades),
            selectinload(CraftsmanProfile.service_areas),
            selectinload(CraftsmanProfile.portfolio)
        )
    )
    profile = result.scalar_one()

    return CraftsmanProfileResponse.from_orm(profile)


@router.post("/trades", response_model=TradeResponse, status_code=status.HTTP_201_CREATED)
async def add_trade(
    trade_data: TradeCreate,
    current_user: User = Depends(get_current_craftsman),
    db: AsyncSession = Depends(get_db)
):
    """Add a trade to craftsman profile"""
    # Get profile
    result = await db.execute(
        select(CraftsmanProfile).where(CraftsmanProfile.user_id == current_user.id)
    )
    profile = result.scalar_one_or_none()

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )

    trade = Trade(
        craftsman_id=profile.id,
        trade_type=trade_data.trade_type,
        is_primary=trade_data.is_primary
    )

    db.add(trade)
    await db.commit()
    await db.refresh(trade)

    return TradeResponse.from_orm(trade)


@router.post("/service-areas", response_model=ServiceAreaResponse, status_code=status.HTTP_201_CREATED)
async def add_service_area(
    area_data: ServiceAreaCreate,
    current_user: User = Depends(get_current_craftsman),
    db: AsyncSession = Depends(get_db)
):
    """Add a service area to craftsman profile"""
    # Get profile
    result = await db.execute(
        select(CraftsmanProfile).where(CraftsmanProfile.user_id == current_user.id)
    )
    profile = result.scalar_one_or_none()

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )

    service_area = ServiceArea(
        craftsman_id=profile.id,
        postal_code=area_data.postal_code,
        city=area_data.city,
        state=area_data.state
    )

    db.add(service_area)
    await db.commit()
    await db.refresh(service_area)

    return ServiceAreaResponse.from_orm(service_area)


@router.post("/portfolio", response_model=PortfolioResponse, status_code=status.HTTP_201_CREATED)
async def add_portfolio_item(
    portfolio_data: PortfolioCreate,
    current_user: User = Depends(get_current_craftsman),
    db: AsyncSession = Depends(get_db)
):
    """Add a portfolio item"""
    # Get profile
    result = await db.execute(
        select(CraftsmanProfile).where(CraftsmanProfile.user_id == current_user.id)
    )
    profile = result.scalar_one_or_none()

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )

    portfolio_item = Portfolio(
        craftsman_id=profile.id,
        title=portfolio_data.title,
        description=portfolio_data.description,
        image_url=portfolio_data.image_url,
        trade_type=portfolio_data.trade_type
    )

    db.add(portfolio_item)
    await db.commit()
    await db.refresh(portfolio_item)

    return PortfolioResponse.from_orm(portfolio_item)


@router.get("/search", response_model=List[CraftsmanProfileResponse])
async def search_craftsmen(
    trade_type: TradeType | None = None,
    postal_code: str | None = None,
    city: str | None = None,
    max_hourly_rate: float | None = None,
    min_rating: float | None = None,
    is_verified: bool | None = None,
    skip: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db)
):
    """Search for craftsmen with filters"""
    query = select(CraftsmanProfile).options(
        selectinload(CraftsmanProfile.trades),
        selectinload(CraftsmanProfile.service_areas),
        selectinload(CraftsmanProfile.portfolio)
    ).where(CraftsmanProfile.accepts_bookings == True)

    # Apply filters
    if trade_type:
        query = query.join(CraftsmanProfile.trades).where(Trade.trade_type == trade_type)

    if postal_code or city:
        query = query.join(CraftsmanProfile.service_areas)
        if postal_code:
            query = query.where(ServiceArea.postal_code == postal_code)
        if city:
            query = query.where(ServiceArea.city.ilike(f"%{city}%"))

    if max_hourly_rate:
        query = query.where(CraftsmanProfile.hourly_rate <= max_hourly_rate)

    if min_rating:
        query = query.where(CraftsmanProfile.average_rating >= min_rating)

    if is_verified is not None:
        query = query.where(CraftsmanProfile.is_verified == is_verified)

    # Pagination
    query = query.offset(skip).limit(limit)

    result = await db.execute(query)
    profiles = result.scalars().unique().all()

    return [CraftsmanProfileResponse.from_orm(p) for p in profiles]


@router.get("/{craftsman_id}", response_model=CraftsmanProfileResponse)
async def get_craftsman_profile(
    craftsman_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific craftsman's public profile"""
    result = await db.execute(
        select(CraftsmanProfile)
        .where(CraftsmanProfile.id == craftsman_id)
        .options(
            selectinload(CraftsmanProfile.trades),
            selectinload(CraftsmanProfile.service_areas),
            selectinload(CraftsmanProfile.portfolio)
        )
    )
    profile = result.scalar_one_or_none()

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Craftsman not found"
        )

    return CraftsmanProfileResponse.from_orm(profile)
