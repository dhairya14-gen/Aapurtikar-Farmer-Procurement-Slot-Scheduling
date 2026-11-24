"""Persistence schema foundation. Models do not create or seed records."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    ForeignKeyConstraint,
    Index,
    Integer,
    JSON,
    String,
    Table,
    Column,
    UniqueConstraint,
    Uuid,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


user_roles = Table(
    "user_roles",
    Base.metadata,
    Column("user_id", Uuid(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("role_id", Uuid(as_uuid=True), ForeignKey("roles.id", ondelete="RESTRICT"), primary_key=True),
)


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )


class User(TimestampMixin, Base):
    __tablename__ = "users"
    __table_args__ = (Index("ix_users_external_subject", "external_subject", unique=True),)

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    external_subject: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(nullable=False, default=True, server_default="true")

    roles: Mapped[list[Role]] = relationship(secondary=user_roles, back_populates="users")
    farmer_profile: Mapped[FarmerProfile | None] = relationship(back_populates="user", uselist=False)


class Role(TimestampMixin, Base):
    __tablename__ = "roles"
    __table_args__ = (UniqueConstraint("code", name="uq_roles_code"),)

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code: Mapped[str] = mapped_column(String(40), nullable=False)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)

    users: Mapped[list[User]] = relationship(secondary=user_roles, back_populates="roles")


class FarmerProfile(TimestampMixin, Base):
    __tablename__ = "farmer_profiles"
    __table_args__ = (UniqueConstraint("farmer_reference", name="uq_farmer_profiles_reference"),)

    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    farmer_reference: Mapped[str | None] = mapped_column(String(100), nullable=True)

    user: Mapped[User] = relationship(back_populates="farmer_profile")
    bookings: Mapped[list[Booking]] = relationship(back_populates="farmer")


class ProcurementCentre(TimestampMixin, Base):
    __tablename__ = "procurement_centres"
    __table_args__ = (
        CheckConstraint(
            "verification_status IN ('unverified', 'awaiting_authorization', 'verified', 'disabled')",
            name="ck_centres_verification_status",
        ),
        CheckConstraint(
            "participation_status IN ('unverified', 'awaiting_authorization', 'authorized', 'disabled')",
            name="ck_centres_participation_status",
        ),
        CheckConstraint(
            "verification_status != 'verified' OR "
            "(authorized_by_user_id IS NOT NULL AND authorized_at IS NOT NULL AND authorization_reference IS NOT NULL)",
            name="ck_centres_verified_has_authorization",
        ),
        CheckConstraint(
            "participation_status != 'authorized' OR "
            "(authorized_by_user_id IS NOT NULL AND authorized_at IS NOT NULL AND authorization_reference IS NOT NULL)",
            name="ck_centres_participation_has_authorization",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    district: Mapped[str | None] = mapped_column(String(120), nullable=True)
    state: Mapped[str | None] = mapped_column(String(120), nullable=True)
    verification_status: Mapped[str] = mapped_column(String(32), nullable=False, default="unverified")
    participation_status: Mapped[str] = mapped_column(String(32), nullable=False, default="awaiting_authorization")
    operating_timezone: Mapped[str | None] = mapped_column(String(80), nullable=True)
    authorized_by_user_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    authorized_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    authorization_reference: Mapped[str | None] = mapped_column(String(500), nullable=True)

    crop_seasons: Mapped[list[CropSeasonConfiguration]] = relationship(back_populates="centre")
    slots: Mapped[list[Slot]] = relationship(back_populates="centre", overlaps="crop_season,slots")


class CropSeasonConfiguration(TimestampMixin, Base):
    __tablename__ = "crop_season_configurations"
    __table_args__ = (
        UniqueConstraint("centre_id", "crop_code", "season_code", name="uq_crop_season_scope"),
        CheckConstraint(
            "status IN ('unverified', 'awaiting_authorization', 'authorized', 'disabled')",
            name="ck_crop_season_status",
        ),
        CheckConstraint(
            "status != 'authorized' OR "
            "(authorized_by_user_id IS NOT NULL AND authorized_at IS NOT NULL AND authorization_reference IS NOT NULL)",
            name="ck_crop_season_authorized_has_authorization",
        ),
        CheckConstraint(
            "effective_until IS NULL OR effective_from IS NULL OR effective_until >= effective_from",
            name="ck_crop_season_effective_interval",
        ),
        UniqueConstraint("id", "centre_id", name="uq_crop_seasons_id_centre"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    centre_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("procurement_centres.id", ondelete="RESTRICT"), nullable=False
    )
    crop_code: Mapped[str] = mapped_column(String(80), nullable=False)
    season_code: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="awaiting_authorization")
    effective_from: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    effective_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    authorized_by_user_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    authorized_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    authorization_reference: Mapped[str | None] = mapped_column(String(500), nullable=True)

    centre: Mapped[ProcurementCentre] = relationship(back_populates="crop_seasons")
    slots: Mapped[list[Slot]] = relationship(back_populates="crop_season", overlaps="centre,slots")


class Slot(TimestampMixin, Base):
    __tablename__ = "slots"
    __table_args__ = (
        CheckConstraint("ends_at > starts_at", name="ck_slots_positive_interval"),
        CheckConstraint("capacity_limit > 0", name="ck_slots_positive_capacity"),
        CheckConstraint("length(trim(capacity_unit)) > 0", name="ck_slots_capacity_unit_nonempty"),
        CheckConstraint("length(trim(configuration_reference)) > 0", name="ck_slots_configuration_reference_nonempty"),
        ForeignKeyConstraint(
            ["crop_season_configuration_id", "centre_id"],
            ["crop_season_configurations.id", "crop_season_configurations.centre_id"],
            ondelete="RESTRICT",
            name="fk_slots_crop_season_same_centre",
        ),
        Index("ix_slots_centre_starts_at", "centre_id", "starts_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    centre_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("procurement_centres.id", ondelete="RESTRICT"), nullable=False
    )
    crop_season_configuration_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    starts_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    ends_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    capacity_limit: Mapped[int] = mapped_column(Integer, nullable=False)
    capacity_unit: Mapped[str] = mapped_column(String(80), nullable=False)
    configuration_reference: Mapped[str] = mapped_column(String(500), nullable=False)

    centre: Mapped[ProcurementCentre] = relationship(back_populates="slots", overlaps="crop_season,slots")
    crop_season: Mapped[CropSeasonConfiguration] = relationship(back_populates="slots", overlaps="centre,slots")
    bookings: Mapped[list[Booking]] = relationship(back_populates="slot")


class Booking(TimestampMixin, Base):
    __tablename__ = "bookings"
    __table_args__ = (
        CheckConstraint(
            "status IN ('requested', 'confirmed', 'cancelled', 'no_show', 'checked_in', 'completed')",
            name="ck_bookings_status",
        ),
        Index("ix_bookings_slot_status", "slot_id", "status"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    farmer_user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("farmer_profiles.user_id", ondelete="RESTRICT"), nullable=False
    )
    slot_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("slots.id", ondelete="RESTRICT"), nullable=False)
    status: Mapped[str] = mapped_column(String(24), nullable=False, default="requested")
    created_by_user_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    farmer: Mapped[FarmerProfile] = relationship(back_populates="bookings")
    slot: Mapped[Slot] = relationship(back_populates="bookings")
    events: Mapped[list[BookingEvent]] = relationship(back_populates="booking", cascade="all, delete-orphan")


class BookingEvent(Base):
    __tablename__ = "booking_events"
    __table_args__ = (
        CheckConstraint(
            "event_type IN ('created', 'confirmed', 'cancelled', 'no_show', 'checked_in', 'completed')",
            name="ck_booking_events_type",
        ),
        Index("ix_booking_events_booking_occurred", "booking_id", "occurred_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    booking_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("bookings.id", ondelete="CASCADE"), nullable=False
    )
    event_type: Mapped[str] = mapped_column(String(24), nullable=False)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    actor_user_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    booking: Mapped[Booking] = relationship(back_populates="events")


class QueueServiceEvent(Base):
    __tablename__ = "queue_service_events"
    __table_args__ = (
        CheckConstraint(
            "event_type IN ('check_in', 'service_start', 'service_complete')",
            name="ck_queue_service_events_type",
        ),
        UniqueConstraint("episode_reference", "event_type", name="uq_queue_episode_event_type"),
        Index("ix_queue_events_centre_occurred", "centre_id", "occurred_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    centre_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("procurement_centres.id", ondelete="RESTRICT"), nullable=False
    )
    episode_reference: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    booking_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("bookings.id", ondelete="SET NULL"), nullable=True
    )
    event_type: Mapped[str] = mapped_column(String(24), nullable=False)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    sequence_number: Mapped[int] = mapped_column(Integer, nullable=False)
    actor_user_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )


class AuditLog(Base):
    __tablename__ = "audit_logs"
    __table_args__ = (Index("ix_audit_logs_entity", "entity_type", "entity_id", "occurred_at"),)

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    actor_user_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    entity_type: Mapped[str] = mapped_column(String(100), nullable=False)
    entity_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), nullable=True)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    details: Mapped[dict[str, object] | None] = mapped_column(JSON, nullable=True)
