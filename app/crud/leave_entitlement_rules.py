from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.models.leave_entitlement_rules import LeaveEntitlementRules


def get_all_entitlement_rules(
    db: Session,
    skip: int = 0,
    limit: int = 100
):
    return (
        db.query(LeaveEntitlementRules)
        .order_by(
            LeaveEntitlementRules.leave_type_id,
            LeaveEntitlementRules.effective_from
        )
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_entitlement_rule_by_id(
    db: Session,
    entitlement_rule_id: int
):
    return (
        db.query(LeaveEntitlementRules)
        .filter(
            LeaveEntitlementRules.entitlement_rule_id
            == entitlement_rule_id
        )
        .first()
    )


def get_overlapping_entitlement_rule(
    db: Session,
    leave_type_id: int,
    employment_category: str,
    effective_from,
    effective_to,
    exclude_rule_id: int | None = None
):
    query = db.query(LeaveEntitlementRules).filter(
        LeaveEntitlementRules.leave_type_id == leave_type_id,
        LeaveEntitlementRules.is_active.is_(True),

        # The date periods must overlap
        or_(
            LeaveEntitlementRules.effective_to.is_(None),
            LeaveEntitlementRules.effective_to >= effective_from
        )
    )

    # Treat "All" as a category applying to everyone.
    # Therefore, it conflicts with overlapping specific categories too.
    if employment_category == "All":
        pass
    else:
        query = query.filter(
            LeaveEntitlementRules.employment_category.in_(
                ["All", employment_category]
            )
        )

    if effective_to is not None:
        query = query.filter(
            LeaveEntitlementRules.effective_from <= effective_to
        )

    if exclude_rule_id is not None:
        query = query.filter(
            LeaveEntitlementRules.entitlement_rule_id
            != exclude_rule_id
        )

    return query.first()


def create_entitlement_rule_record(
    db: Session,
    rule_data: dict
):
    rule = LeaveEntitlementRules(**rule_data)

    try:
        db.add(rule)
        db.commit()
        db.refresh(rule)
        return rule

    except Exception:
        db.rollback()
        raise


def update_entitlement_rule_record(
    db: Session,
    rule: LeaveEntitlementRules,
    update_data: dict
):
    try:
        for key, value in update_data.items():
            setattr(rule, key, value)

        db.commit()
        db.refresh(rule)
        return rule

    except Exception:
        db.rollback()
        raise