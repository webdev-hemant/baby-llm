"""Unit tests for Gentle Curiosity Protocol and session budget enforcement."""

from baby_llm.success.curiosity import GentleCuriosityEngine


def test_gentle_curiosity_probe_detection():
    engine = GentleCuriosityEngine(max_probes_per_session=1)

    # 1. Non-ambiguous turn -> No probe
    probe1 = engine.evaluate_turn_for_probe("I love drinking espresso in the morning.")
    assert probe1 is None

    # 2. Ambiguous Project Alpha mentioned -> Probes gently
    probe2 = engine.evaluate_turn_for_probe("We made big progress on Project Orion today.")
    assert probe2 is not None
    assert "Project Orion" in probe2
    assert "initiative" in probe2 or "milestone" in probe2

    # 3. Budget exhausted in same session -> No subsequent probe
    probe3 = engine.evaluate_turn_for_probe("Also Project Titan is launching next week.")
    assert probe3 is None


def test_gentle_curiosity_session_reset():
    engine = GentleCuriosityEngine(max_probes_per_session=1)

    probe = engine.evaluate_turn_for_probe("Reviewing Project Phoenix notes.")
    assert probe is not None
    assert engine.can_probe() is False

    # Reset session budget
    engine.reset_session()
    assert engine.can_probe() is True

    # New project can now be probed
    new_probe = engine.evaluate_turn_for_probe("Reviewing Project Andromeda notes.")
    assert new_probe is not None
    assert "Project Andromeda" in new_probe
