import pytest
from models import db
from services.section_service import update_section

def test_update_section_blocked_when_closed(setup_database):
    section = setup_database
    section.open = False
    db.session.commit()

    form_data = {
        'section_number': '1A',
        'teacher_id': section.teacher_id,
        'evaluation_weight_type': 'porcentaje'
    }

    with pytest.raises(ValueError) as exc_info:
        update_section(section.id, form_data)

    assert "cerrada" in str(exc_info.value).lower()
