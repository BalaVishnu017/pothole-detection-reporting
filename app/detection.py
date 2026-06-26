"""
InfraVision AI — Detection Module
===================================
Encapsulates all YOLO-based pothole detection logic.

Provides:
    - Cached model loading (one load per Streamlit session)
    - Severity classification (Low / Medium / High / Critical)
    - Image and video detection APIs
    - Evidence frame extraction and saving
"""

import logging
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional

import cv2
import numpy as np
import streamlit as st

logger = logging.getLogger(__name__)


# =============================================================================
# Enumerations & Data Classes
# =============================================================================


class Severity(str, Enum):
    """Pothole severity classification levels."""

    NONE = "None"
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"


# Colour associated with each severity level (for UI rendering)
SEVERITY_COLORS: dict[Severity, str] = {
    Severity.NONE: "#4caf50",  # green
    Severity.LOW: "#8bc34a",  # light green
    Severity.MEDIUM: "#ff9800",  # amber
    Severity.HIGH: "#f44336",  # red
    Severity.CRITICAL: "#b71c1c",  # deep red
}

SEVERITY_EMOJIS: dict[Severity, str] = {
    Severity.NONE: "✅",
    Severity.LOW: "🟡",
    Severity.MEDIUM: "🟠",
    Severity.HIGH: "🔴",
    Severity.CRITICAL: "🚨",
}


@dataclass
class Detection:
    """Represents a single detected pothole."""

    x: float
    y: float
    width: float
    height: float
    confidence: float
    area_ratio: float  # fraction of frame area occupied by the pothole

    @property
    def area(self) -> float:
        return self.width * self.height


@dataclass
class DetectionResult:
    """Aggregated result of running detection on one image/frame."""

    detections: list[Detection] = field(default_factory=list)
    annotated_image: Optional[np.ndarray] = None
    severity: Severity = Severity.NONE
    total_potholes: int = 0
    max_confidence: float = 0.0
    max_area_ratio: float = 0.0


# =============================================================================
# Model Loading
# =============================================================================


@st.cache_resource(show_spinner="Loading AI model…")
def load_model(model_path: str = "models/best.pt"):
    """
    Load and cache the YOLO model.  Called once per Streamlit session.

    Args:
        model_path: Path to the .pt model weights file.

    Returns:
        Ultralytics YOLO model instance.

    Raises:
        FileNotFoundError: If the model file cannot be found.
        RuntimeError:      If the model fails to load.
    """
    from ultralytics import YOLO

    if not Path(model_path).exists():
        raise FileNotFoundError(
            f"Model not found at '{model_path}'. "
            "Please download best.pt and place it in the models/ directory. "
            "See README.md for instructions."
        )
    try:
        model = YOLO(model_path)
        logger.info("YOLO model loaded from '%s'.", model_path)
        return model
    except Exception as exc:
        raise RuntimeError(f"Failed to load YOLO model: {exc}") from exc


# =============================================================================
# Severity Classification
# =============================================================================


def classify_severity(detections: list[Detection], conf_threshold: float = 0.5) -> Severity:
    """
    Classify the worst-case severity based on detection parameters.

    Severity rules (evaluated in priority order):
        Critical : any pothole covering > 15% of the frame
        High     : any pothole covering > 8% of the frame
        Medium   : any pothole covering > 3% of the frame
        Low      : potholes detected below the medium threshold
        None     : no detections

    Args:
        detections:      List of Detection objects.
        conf_threshold:  Minimum confidence to consider a detection.

    Returns:
        The highest-severity Severity enum value.
    """
    if not detections:
        return Severity.NONE

    confirmed = [d for d in detections if d.confidence >= conf_threshold]
    if not confirmed:
        return Severity.NONE

    max_ratio = max(d.area_ratio for d in confirmed)

    if max_ratio > 0.15:
        return Severity.CRITICAL
    if max_ratio > 0.08:
        return Severity.HIGH
    if max_ratio > 0.03:
        return Severity.MEDIUM
    return Severity.LOW


# =============================================================================
# Detection Functions
# =============================================================================


def detect_image(
    model,
    image: np.ndarray,
    confidence: float = 0.5,
) -> DetectionResult:
    """
    Run pothole detection on a single image.

    Args:
        model:      Loaded YOLO model.
        image:      BGR image as a NumPy array.
        confidence: Confidence threshold.

    Returns:
        DetectionResult with annotated image and severity.
    """
    frame_area = image.shape[0] * image.shape[1]
    results = model.predict(image, conf=confidence, verbose=False)
    result = results[0]

    detections: list[Detection] = []
    for box in result.boxes:
        x, y, w, h = box.xywh[0].tolist()
        conf = float(box.conf[0])
        area_ratio = (w * h) / frame_area
        detections.append(
            Detection(x=x, y=y, width=w, height=h, confidence=conf, area_ratio=area_ratio)
        )

    severity = classify_severity(detections, confidence)
    annotated = result.plot()

    return DetectionResult(
        detections=detections,
        annotated_image=annotated,
        severity=severity,
        total_potholes=len(detections),
        max_confidence=max((d.confidence for d in detections), default=0.0),
        max_area_ratio=max((d.area_ratio for d in detections), default=0.0),
    )


def detect_video(
    model,
    video_path: str,
    confidence: float = 0.5,
    critical_area_ratio: float = 0.05,
    frame_display_placeholder=None,
) -> tuple[DetectionResult, Optional[str]]:
    """
    Run pothole detection on a video file, streaming frames to Streamlit.

    Args:
        model:                    Loaded YOLO model.
        video_path:               Path to the input video file.
        confidence:               Confidence threshold.
        critical_area_ratio:      Area ratio threshold to extract evidence frame.
        frame_display_placeholder: Streamlit empty() placeholder for live display.

    Returns:
        (best_result, evidence_path)
        - best_result: DetectionResult for the worst-case frame found.
        - evidence_path: Path to the saved evidence JPEG, or None.
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise RuntimeError(f"Cannot open video file: {video_path}")

    best_result: Optional[DetectionResult] = None
    evidence_path: Optional[str] = None
    frame_count = 0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    Path("outputs").mkdir(exist_ok=True)

    try:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            frame_count += 1
            result = detect_image(model, frame, confidence)

            # Display live feed
            if frame_display_placeholder is not None:
                frame_display_placeholder.image(result.annotated_image, channels="BGR")

            # Track worst-case result
            if best_result is None or result.max_area_ratio > best_result.max_area_ratio:
                best_result = result

            # Save evidence frame for the first critical detection
            if (
                evidence_path is None
                and result.max_area_ratio >= critical_area_ratio
                and result.severity in (Severity.HIGH, Severity.CRITICAL)
            ):
                evidence_path = "outputs/evidence_frame.jpg"
                cv2.imwrite(evidence_path, result.annotated_image)
                logger.info(
                    "Evidence frame saved at frame %d/%d → '%s'.",
                    frame_count,
                    total_frames,
                    evidence_path,
                )
    finally:
        cap.release()

    if best_result is None:
        best_result = DetectionResult()

    logger.info(
        "Video analysis complete: %d frames, max severity=%s.",
        frame_count,
        best_result.severity,
    )
    return best_result, evidence_path
