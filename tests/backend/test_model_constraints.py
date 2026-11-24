"""Schema constraints are tested only in a transient in-memory SQLite database."""

from datetime import datetime, timezone

import pytest
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db import Base
from app.models import CropSeasonConfiguration, ProcurementCentre, Slot


def test_unapproved_centre_cannot_be_marked_verified_without_authority() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        # This row is an isolated schema fixture in memory, never an app/project record.
        session.add(
            ProcurementCentre(
                code="test-centre",
                name="Test-only centre",
                verification_status="verified",
                participation_status="awaiting_authorization",
            )
        )
        with pytest.raises(IntegrityError):
            session.commit()

    engine.dispose()


def test_slot_rejects_nonpositive_capacity() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        # These entities exist only inside the isolated, ephemeral test database.
        centre = ProcurementCentre(code="test-centre", name="Test-only centre")
        session.add(centre)
        session.flush()
        crop = CropSeasonConfiguration(
            centre_id=centre.id,
            crop_code="test-crop",
            season_code="test-season",
        )
        session.add(crop)
        session.flush()
        session.add(
            Slot(
                centre_id=centre.id,
                crop_season_configuration_id=crop.id,
                starts_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
                ends_at=datetime(2026, 1, 1, 1, tzinfo=timezone.utc),
                capacity_limit=0,
                capacity_unit="test-only",
                configuration_reference="test-only",
            )
        )
        with pytest.raises(IntegrityError):
            session.commit()

    engine.dispose()
