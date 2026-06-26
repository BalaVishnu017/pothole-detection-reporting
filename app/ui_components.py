"""
InfraVision AI — UI Components
================================
Reusable Streamlit UI components for the premium dark glassmorphism theme.
All components are stateless functions — they render markup and return values.
"""

import streamlit as st

from app.detection import SEVERITY_COLORS, SEVERITY_EMOJIS, DetectionResult
from app.gps_service import Coordinates

# =============================================================================
# Page Header
# =============================================================================


def render_header() -> None:
    """Render the animated app header with logo and tagline."""
    st.markdown(
        """
        <div class="app-header">
            <div class="header-icon">🚧</div>
            <h1 class="header-title">InfraVision AI</h1>
            <p class="header-tagline">
                AI-Powered Road Defect Detection &amp; Automated Reporting System
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


# =============================================================================
# Sidebar
# =============================================================================


def render_sidebar(username: str, role: str) -> None:
    """
    Render the sidebar with user info, settings, and logout button.

    Args:
        username: Current logged-in username.
        role:     User role ('user' or 'admin').
    """
    with st.sidebar:
        st.markdown(
            f"""
            <div class="sidebar-user-card">
                <div class="user-avatar">👤</div>
                <div class="user-info">
                    <p class="user-name">{username}</p>
                    <p class="user-role">{role.upper()}</p>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("---")
        st.markdown("### ⚙️ Detection Settings")
        confidence = st.slider(
            "Confidence Threshold",
            min_value=0.1,
            max_value=1.0,
            value=0.5,
            step=0.05,
            help="Minimum confidence score for a detection to be accepted.",
        )
        st.markdown("---")
        if st.button("🚪 Logout", use_container_width=True, key="logout_btn"):
            from app.auth import logout

            logout()

    return confidence


# =============================================================================
# Metrics Panel
# =============================================================================


def render_metrics_panel(result: DetectionResult) -> None:
    """
    Display a row of metric cards summarising the detection result.

    Args:
        result: DetectionResult from the detection module.
    """
    col1, col2, col3, col4 = st.columns(4)
    severity_color = SEVERITY_COLORS.get(result.severity, "#607d8b")
    severity_emoji = SEVERITY_EMOJIS.get(result.severity, "⚠️")

    with col1:
        st.metric("🕳️ Potholes Found", result.total_potholes)
    with col2:
        st.metric("🎯 Max Confidence", f"{result.max_confidence:.0%}")
    with col3:
        st.metric("📐 Max Area Ratio", f"{result.max_area_ratio:.1%}")
    with col4:
        st.markdown(
            f"""
            <div style="
                background: {severity_color}22;
                border: 1px solid {severity_color};
                border-radius: 8px;
                padding: 12px;
                text-align: center;
            ">
                <p style="margin:0; font-size:12px; color:#94a3b8;">SEVERITY</p>
                <p style="margin:4px 0 0; font-size:20px; font-weight:700; color:{severity_color};">
                    {severity_emoji} {result.severity.value}
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )


# =============================================================================
# Detection Result Card
# =============================================================================


def render_detection_result(result: DetectionResult, coordinates: Coordinates) -> None:
    """
    Render a full detection result card with image, metrics, and map link.

    Args:
        result:      DetectionResult from the detection module.
        coordinates: GPS location of the detection.
    """
    if result.annotated_image is not None:
        st.image(result.annotated_image, channels="BGR", use_container_width=True)

    render_metrics_panel(result)

    if result.total_potholes > 0:
        st.markdown(
            f"""
            <div class="result-card result-danger">
                <h3>📍 Location Details</h3>
                <p><strong>Coordinates:</strong> {coordinates}</p>
                <a href="{coordinates.to_google_maps_url()}" target="_blank"
                   class="maps-link">🗺️ Open in Google Maps</a>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.success("✅ No significant potholes detected in this input.")


# =============================================================================
# Status Alerts
# =============================================================================


def render_report_status(success: bool, message: str) -> None:
    """Show a success or error banner for email report status."""
    if success:
        st.markdown(
            f"""
            <div class="alert-success">
                ✅ <strong>Report Filed Successfully!</strong><br/>
                <span style="font-size:13px;">{message}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f"""
            <div class="alert-error">
                ❌ <strong>Report Failed</strong><br/>
                <span style="font-size:13px;">{message}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )


# =============================================================================
# Info Banner
# =============================================================================


def render_welcome_banner(username: str) -> None:
    """Render a personalised welcome banner after login."""
    st.markdown(
        f"""
        <div class="welcome-banner">
            <h2>Welcome back, <span style="color:#60a5fa;">{username}</span> 👋</h2>
            <p>Upload an image or video below to start AI-powered pothole detection.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
