"""Test StateManager """

import json

from src.collect.state import StateManager

def test_save_creates_state_file(tmp_path):
    state_file = tmp_path / "state.json"
    manager = StateManager(state_file=state_file)

    state = {
        "event_id": "test_event",
        "next_token": "token_001",
        "updated_at": "2026-11-16T10:00:00",
    }

    manager.save(state)

    assert state_file.exists()

    with state_file.open("r", encoding="utf-8") as f:
        saved_state = json.load(f)

    assert saved_state == state

def test_load_returns_saved_state(tmp_path):
    state_file = tmp_path / "state.json"

    state = {
        "event_id": "test_event",
        "next_token": "token_001",
    }

    with state_file.open("w", encoding="utf-8") as f:
        json.dump(state, f)

    manager = StateManager(state_file=state_file)

    assert manager.load() == state


def test_load_returns_none_when_file_does_not_exist(tmp_path):
    state_file = tmp_path / "state.json"
    manager = StateManager(state_file=state_file)

    assert manager.load() is None

def test_save_overwrites_existing_state(tmp_path):
    state_file = tmp_path / "state.json"
    manager = StateManager(state_file=state_file)

    first_state = {
        "event_id": "test_event",
        "next_token": "token_001",
    }

    second_state = {
        "event_id": "test_event",
        "next_token": "token_002",
    }

    manager.save(first_state)
    manager.save(second_state)

    assert manager.load() == second_state

def test_delete_removes_state_file(tmp_path):
    state_file = tmp_path / "state.json"
    manager = StateManager(state_file=state_file)

    manager.save({"event_id": "test_event"})

    manager.delete()

    assert not state_file.exists()

def test_delete_does_nothing_when_file_does_not_exist(tmp_path):
    state_file = tmp_path / "state.json"
    manager = StateManager(state_file=state_file)

    manager.delete()

    assert not state_file.exists()