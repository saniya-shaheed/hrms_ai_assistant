from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status
)

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.database import get_db

from app.dependencies.authorization import require_permission

from app.crud.leave_entitlement_rules import (
    get_all_entitlement_rules,
    get_entitlement_rule_by_id,
    get_overlapping_entitlement_rule,
    create_entitlement_rule_record,
    update_entitlement_rule_record
)

from app.crud.leave_types import get_leave_type_by_id

from app.schema.leave_entitlement_rules import (
    LeaveEntitlementRulesCreate,
    LeaveEntitlementRulesUpdate,
    LeaveEntitlementRulesOut
)


router = APIRouter(
    prefix="/leave/entitlements",
    tags=["Leave Entitlements"]
)


# --------------------------------------------------
# 1. GET ALL ENTITLEMENT RULES
# GET /leave/entitlements
# --------------------------------------------------

@router.get(
    "",
    response_model=list[LeaveEntitlementRulesOut]
)
def list_entitlement_rules(
    current_user=Depends(
        require_permission("leave.entitlement.read")
    ),
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100)
):
    return get_all_entitlement_rules(
        db,
        skip=skip,
        limit=limit
    )


# --------------------------------------------------
# 2. CREATE ENTITLEMENT RULE
# POST /leave/entitlements
# --------------------------------------------------

@router.post(
    "",
    response_model=LeaveEntitlementRulesOut,
    status_code=status.HTTP_201_CREATED
)
def create_entitlement_rule(
    rule_data: LeaveEntitlementRulesCreate,
    current_user=Depends(
        require_permission("leave.entitlement.create")
    ),
    db: Session = Depends(get_db)
):

    # Check leave type
    leave_type = get_leave_type_by_id(
        db,
        rule_data.leave_type_id
    )

    if leave_type is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Leave type not found"
        )

    if not leave_type.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot create entitlement for an inactive leave type"
        )

    # Check overlapping active rules
    if rule_data.is_active:
        existing_rule = get_overlapping_entitlement_rule(
            db,
            rule_data.leave_type_id,
            rule_data.employment_category,
            rule_data.effective_from,
            rule_data.effective_to
        )

        if existing_rule:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="An active entitlement rule already exists for this leave type, category and effective period"
            )

    try:
        return create_entitlement_rule_record(
            db,
            rule_data.model_dump()
        )

    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Entitlement rule conflicts with existing database records"
        )


# --------------------------------------------------
# 3. UPDATE ENTITLEMENT RULE
# PATCH /leave/entitlements/{id}
# --------------------------------------------------

@router.patch(
    "/{entitlement_rule_id}",
    response_model=LeaveEntitlementRulesOut
)
def update_entitlement_rule(
    entitlement_rule_id: int,
    rule_data: LeaveEntitlementRulesUpdate,
    current_user=Depends(
        require_permission("leave.entitlement.update")
    ),
    db: Session = Depends(get_db)
):

    # Find existing rule
    rule = get_entitlement_rule_by_id(
        db,
        entitlement_rule_id
    )

    if rule is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Entitlement rule not found"
        )

    update_data = rule_data.model_dump(
        exclude_unset=True
    )

    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields provided for update"
        )

    # Required fields cannot be NULL
    required_fields = [
        "leave_type_id",
        "employment_category",
        "entitlement_days",
        "effective_from",
        "is_active"
    ]

    for field in required_fields:
        if field in update_data and update_data[field] is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"{field} cannot be null"
            )

    # Determine the final values after applying PATCH
    leave_type_id = update_data.get(
        "leave_type_id",
        rule.leave_type_id
    )

    employment_category = update_data.get(
        "employment_category",
        rule.employment_category
    )

    effective_from = update_data.get(
        "effective_from",
        rule.effective_from
    )

    effective_to = update_data.get(
        "effective_to",
        rule.effective_to
    )

    is_active = update_data.get(
        "is_active",
        rule.is_active
    )

    # Validate date range
    if (
        effective_to is not None
        and effective_to < effective_from
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Effective to date cannot be earlier than effective from date"
        )

    # Validate leave type
    leave_type = get_leave_type_by_id(
        db,
        leave_type_id
    )

    if leave_type is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Leave type not found"
        )

    if is_active and not leave_type.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot activate an entitlement rule for an inactive leave type"
        )

    # Check overlapping rules when the resulting rule is active
    if is_active:
        existing_rule = get_overlapping_entitlement_rule(
            db,
            leave_type_id,
            employment_category,
            effective_from,
            effective_to,
            exclude_rule_id=entitlement_rule_id
        )

        if existing_rule:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Another active entitlement rule overlaps with this rule"
            )

    try:
        return update_entitlement_rule_record(
            db,
            rule,
            update_data
        )

    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Entitlement rule update conflicts with existing records"
        )