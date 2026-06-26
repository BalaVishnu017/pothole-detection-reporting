"""
InfraVision AI — Main Application Entry Point
==============================================
This is the slim entrypoint for the Streamlit application.
All heavy logic lives in the app/ package modules.

Run:
    streamlit run app.py
"""

import logging
import tempfile
from pathlib import Path

import numpy as np
import streamlit as st

# ── Logging Setup ──────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# ── Page Configuration (must be first Streamlit call) ─────────────────────
st.set_page_config(
    page_title="InfraVision AI",
    page_icon="🚧",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Inject Custom CSS ──────────────────────────────────────────────────────
_css_path = Path("assets/style.css")
if _css_path.exists():
    with open(_css_path) as _f:
        st.markdown(f"<style>{_f.read()}</style>", unsafe_allow_html=True)


# ── Application Imports ────────────────────────────────────────────────────
from app.auth import init_session, render_login_page, render_signup_page  # noqa: E402
from app.database import init_db  # noqa: E402
from app.detection import Severity, detect_image, detect_video, load_model  # noqa: E402
from app.email_service import send_report  # noqa: E402
from app.gps_service import get_default_coordinates  # noqa: E402
from app.ui_components import (  # noqa: E402
    render_detection_result,
    render_header,
    render_report_status,
    render_sidebar,
    render_welcome_banner,
)
from config.settings import settings  # noqa: E402

# =============================================================================
# Detection Interface (shown when logged in)
# =============================================================================


def pothole_detection_interface() -> None:
    """Render the main pothole detection dashboard."""

    # ── Sidebar ─────────────────────────────────────────────────────────────
    confidence = render_sidebar(
        username=st.session_state["username"],
        role=st.session_state["user_role"],
    )

    # ── Welcome Banner ───────────────────────────────────────────────────────
    render_welcome_banner(st.session_state["username"])

    # ── Load Model ───────────────────────────────────────────────────────────
    try:
        model = load_model(settings.model_path)
    except (FileNotFoundError, RuntimeError) as exc:
        st.error(f"⚠️ **Model Error:** {exc}")
        st.info(
            "📥 **Download the model:** Place `best.pt` inside the `models/` directory. "
            "See [README.md](README.md) for the download link."
        )
        return

    # ── Location Settings ────────────────────────────────────────────────────
    st.markdown("### 📍 Location Settings")
    location_mode = st.radio(
        "Location Mode",
        ["Use Default Location", "Enter Manually"],
        horizontal=True,
        label_visibility="collapsed",
    )

    current_coords = get_default_coordinates()

    if location_mode == "Enter Manually":
        col1, col2, col3 = st.columns(3)
        with col1:
            lat_input = st.text_input("Latitude", value=str(current_coords.latitude))
        with col2:
            lon_input = st.text_input("Longitude", value=str(current_coords.longitude))
        with col3:
            place_input = st.text_input("Place Name (Optional)", value="")

        from app.gps_service import parse_coordinates

        parsed_coords = parse_coordinates(
            lat_input, lon_input, place_input if place_input else None
        )
        if parsed_coords:
            current_coords = parsed_coords
        else:
            st.error("Invalid coordinates entered. Using default.")

    st.divider()

    # ── Input Mode Tabs ──────────────────────────────────────────────────────
    tab_image, tab_video = st.tabs(["📸 Image Detection", "🎥 Video Detection"])

    # ────────────────────────────────────────────────────────────────────────
    # TAB 1 — Image Detection
    # ────────────────────────────────────────────────────────────────────────
    with tab_image:
        st.markdown("### Upload or capture a road image")
        uploaded_file = st.file_uploader(
            "Drag & drop or click to upload",
            type=["jpg", "jpeg", "png"],
            key="image_uploader",
            help="Supports JPG, JPEG, and PNG formats.",
        )

        if uploaded_file:
            col_orig, col_result = st.columns(2)

            with col_orig:
                st.markdown("**📷 Original Image**")
                st.image(uploaded_file, use_container_width=True)

            if st.button("🔍 Analyze Image", key="analyze_image_btn", use_container_width=True):
                file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
                import cv2

                img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

                with st.spinner("Running AI detection…"):
                    result = detect_image(model, img, confidence)

                with col_result:
                    st.markdown("**🤖 AI Detection Output**")
                    if result.annotated_image is not None:
                        st.image(result.annotated_image, channels="BGR", use_container_width=True)

                render_detection_result(result, current_coords)

                if result.total_potholes > 0 and result.severity in (
                    Severity.HIGH,
                    Severity.CRITICAL,
                ):
                    # Save evidence
                    Path("outputs").mkdir(exist_ok=True)
                    evidence_path = "outputs/evidence_image.jpg"
                    import cv2

                    cv2.imwrite(evidence_path, result.annotated_image)

                    st.warning(
                        f"⚠️ **{result.severity.value} severity** pothole detected! "
                        "Sending report to road department…"
                    )
                    success, msg = send_report(
                        evidence_path=evidence_path,
                        coordinates=current_coords,
                        severity=result.severity,
                        reported_by=st.session_state["username"],
                    )
                    render_report_status(success, msg)

                    # Update report count in DB
                    if success:
                        from app.database import increment_report_count

                        increment_report_count(st.session_state["username"])

    # ────────────────────────────────────────────────────────────────────────
    # TAB 2 — Video Detection
    # ────────────────────────────────────────────────────────────────────────
    with tab_video:
        st.markdown("### Upload a road video for analysis")
        uploaded_video = st.file_uploader(
            "Drag & drop or click to upload",
            type=["mp4", "mov", "avi"],
            key="video_uploader",
            help="Supports MP4, MOV, and AVI formats.",
        )

        if uploaded_video:
            # Show GPS info
            coords = current_coords
            st.info(
                f"📍 **Location detected:** `{coords}` "
                f"— [View on Maps]({coords.to_google_maps_url()})"
            )

            if st.button("▶️ Analyze Video", key="analyze_video_btn", use_container_width=True):
                # Write to a temp file
                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tfile:
                    tfile.write(uploaded_video.read())
                    video_path = tfile.name

                with st.spinner("Analyzing video — this may take a moment…"):
                    frame_placeholder = st.empty()
                    best_result, evidence_path = detect_video(
                        model=model,
                        video_path=video_path,
                        confidence=confidence,
                        critical_area_ratio=settings.critical_area_ratio,
                        frame_display_placeholder=frame_placeholder,
                    )

                frame_placeholder.empty()  # Clear live feed after analysis

                st.markdown("### 📊 Analysis Results")
                render_detection_result(best_result, coords)

                if evidence_path and best_result.severity in (Severity.HIGH, Severity.CRITICAL):
                    st.warning(
                        f"⚠️ **{best_result.severity.value} severity** defect found in video! "
                        "Sending evidence frame to road department…"
                    )
                    success, msg = send_report(
                        evidence_path=evidence_path,
                        coordinates=coords,
                        severity=best_result.severity,
                        reported_by=st.session_state["username"],
                    )
                    render_report_status(success, msg)

                    if success:
                        from app.database import increment_report_count

                        increment_report_count(st.session_state["username"])
                elif best_result.total_potholes == 0:
                    st.success("✅ Video analysis complete. No critical defects detected.")
                else:
                    st.info(
                        f"ℹ️ Detected **{best_result.total_potholes}** pothole(s) with "
                        f"**{best_result.severity.value}** severity — below reporting threshold."
                    )

                # Cleanup temp file
                try:
                    Path(video_path).unlink(missing_ok=True)
                except Exception:
                    pass


# =============================================================================
# Authentication Flow
# =============================================================================


def auth_interface() -> None:
    """Render the login / sign-up interface."""
    render_header()

    # Centre the auth form
    _, col, _ = st.columns([1, 2, 1])
    with col:
        tab_login, tab_signup = st.tabs(["🔐 Sign In", "📝 Sign Up"])
        with tab_login:
            render_login_page()
        with tab_signup:
            render_signup_page()


# =============================================================================
# Entry Point
# =============================================================================


def main() -> None:
    """Main application entry point."""
    # Bootstrap database and session
    init_db()
    init_session()

    if st.session_state["logged_in"]:
        pothole_detection_interface()
    else:
        auth_interface()


if __name__ == "__main__":
    main()
