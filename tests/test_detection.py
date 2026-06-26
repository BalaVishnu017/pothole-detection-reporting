"""
Tests — Detection Module
==========================
Unit tests for severity classification logic and DetectionResult assembly.
No YOLO model is loaded — we test the pure Python classification functions.
"""

from app.detection import (
    Detection,
    DetectionResult,
    Severity,
    classify_severity,
)

# =============================================================================
# Helper Factory
# =============================================================================


def make_detection(confidence: float = 0.9, area_ratio: float = 0.10) -> Detection:
    """Create a Detection with default dummy bounding box values."""
    return Detection(
        x=100.0,
        y=100.0,
        width=200.0,
        height=200.0,
        confidence=confidence,
        area_ratio=area_ratio,
    )


# =============================================================================
# Severity Classification Tests
# =============================================================================


class TestClassifySeverity:

    def test_no_detections_returns_none(self):
        assert classify_severity([]) == Severity.NONE

    def test_low_confidence_detections_return_none(self):
        """Detections below the confidence threshold should be ignored."""
        d = make_detection(confidence=0.3, area_ratio=0.20)
        result = classify_severity([d], conf_threshold=0.5)
        assert result == Severity.NONE

    def test_small_area_returns_low(self):
        d = make_detection(confidence=0.9, area_ratio=0.01)
        assert classify_severity([d]) == Severity.LOW

    def test_medium_area_returns_medium(self):
        d = make_detection(confidence=0.9, area_ratio=0.05)
        assert classify_severity([d]) == Severity.MEDIUM

    def test_high_area_returns_high(self):
        d = make_detection(confidence=0.9, area_ratio=0.10)
        assert classify_severity([d]) == Severity.HIGH

    def test_very_large_area_returns_critical(self):
        d = make_detection(confidence=0.9, area_ratio=0.20)
        assert classify_severity([d]) == Severity.CRITICAL

    def test_worst_case_dominates(self):
        """Multiple potholes — the largest one determines severity."""
        detections = [
            make_detection(confidence=0.9, area_ratio=0.01),  # LOW
            make_detection(confidence=0.9, area_ratio=0.20),  # CRITICAL
            make_detection(confidence=0.9, area_ratio=0.05),  # MEDIUM
        ]
        assert classify_severity(detections) == Severity.CRITICAL

    def test_boundary_critical(self):
        """Exactly at critical boundary (> 0.15)."""
        d = make_detection(confidence=0.9, area_ratio=0.151)
        assert classify_severity([d]) == Severity.CRITICAL

    def test_boundary_high(self):
        """Exactly at high boundary (> 0.08)."""
        d = make_detection(confidence=0.9, area_ratio=0.081)
        assert classify_severity([d]) == Severity.HIGH

    def test_boundary_medium(self):
        """Exactly at medium boundary (> 0.03)."""
        d = make_detection(confidence=0.9, area_ratio=0.031)
        assert classify_severity([d]) == Severity.MEDIUM

    def test_custom_confidence_threshold(self):
        """Confidence threshold parameter is respected."""
        d = make_detection(confidence=0.6, area_ratio=0.20)
        # With default threshold=0.5 → CRITICAL
        assert classify_severity([d], conf_threshold=0.5) == Severity.CRITICAL
        # With threshold=0.7 → detection ignored → NONE
        assert classify_severity([d], conf_threshold=0.7) == Severity.NONE


# =============================================================================
# DetectionResult Tests
# =============================================================================


class TestDetectionResult:

    def test_default_detection_result(self):
        result = DetectionResult()
        assert result.total_potholes == 0
        assert result.severity == Severity.NONE
        assert result.max_confidence == 0.0
        assert result.max_area_ratio == 0.0
        assert result.annotated_image is None

    def test_detection_area_property(self):
        d = make_detection()
        assert d.area == d.width * d.height


# =============================================================================
# Severity Enum Tests
# =============================================================================


class TestSeverityEnum:

    def test_severity_values(self):
        assert Severity.NONE.value == "None"
        assert Severity.LOW.value == "Low"
        assert Severity.MEDIUM.value == "Medium"
        assert Severity.HIGH.value == "High"
        assert Severity.CRITICAL.value == "Critical"

    def test_severity_is_string_enum(self):
        """Severity should be usable as a string."""
        assert isinstance(Severity.CRITICAL, str)
        assert Severity.HIGH == "High"
