from pathlib import Path


def test_migration_chain_is_linear_and_media_migration_is_idempotent_safe():
    v1 = Path('migrations/versions/0001_initial.py').read_text()
    v2 = Path('migrations/versions/0002_scheduler_media.py').read_text()
    v3 = Path('migrations/versions/0003_scheduled_message_runs.py').read_text()
    assert "revision=\"0001_initial\"" in v1
    assert "down_revision='0001_initial'" in v2
    assert "down_revision='0002_scheduler_media'" in v3
    assert "inspect(op.get_bind())" in v2
    assert "if 'media_file_id' not in cols" in v2
    assert "scheduled_message_runs" in v3
    assert "uq_schedule_scheduled_for" in v3


def test_initial_migration_does_not_precreate_later_scheduler_run_table():
    text = Path('migrations/versions/0001_initial.py').read_text()
    assert 'if table.name == \"scheduled_message_runs\":' in text
    assert 'table.create(bind=bind, checkfirst=True)' in text

