import pytest

from app.services.materiality_service import MaterialityService, MaterialityWeights


def test_calculates_normalized_component_scores():
    service = MaterialityService()

    assert service.calculate_impact(5, 4, 5, 3) == 85.0
    assert service.calculate_financial(2, 5, 3, 3, 4) == 68.0


def test_calculates_configurable_materiality_score():
    service = MaterialityService(MaterialityWeights(impact=0.4, financial=0.4, stakeholder=0.2))

    assert service.calculate_materiality(80, 60, 40) == 64.0
    assert service.calculate_materiality(100, 100, 100) == 100.0
    assert service.calculate_materiality(0, 0, 0) == 0.0


@pytest.mark.parametrize(
    ("score", "priority"),
    [
        (0, "low"),
        (39, "low"),
        (40, "medium"),
        (59, "medium"),
        (60, "high"),
        (79, "high"),
        (80, "critical"),
        (100, "critical"),
    ],
)
def test_classifies_priority_boundaries(score, priority):
    assert MaterialityService.classify_priority(score) == priority


def test_returns_no_stakeholder_or_materiality_score_when_inputs_are_incomplete():
    service = MaterialityService()

    assert service.calculate_stakeholder([]) is None
    assert service.calculate_materiality(80, 60, None) is None


@pytest.mark.parametrize("values", [(0, 3, 4, 5), (1, 2, 3, 6)])
def test_rejects_invalid_dimension_values(values):
    with pytest.raises(ValueError, match="between 1 and 5"):
        MaterialityService().calculate_impact(*values)


def test_rejects_invalid_weights_and_scores():
    with pytest.raises(ValueError, match="add up"):
        MaterialityWeights(impact=0.5, financial=0.5, stakeholder=0.5)
    with pytest.raises(ValueError, match="between 0 and 100"):
        MaterialityService().calculate_materiality(101, 50, 50)
