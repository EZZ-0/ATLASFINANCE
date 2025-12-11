"""
LOADING ANIMATION - Warp Loader
================================
Custom loading animation for extraction.

Usage:
    from utils.loading_animation import show_loading, hide_loading
    
    placeholder = show_loading("Extracting AAPL...")
    # ... do work ...
    hide_loading(placeholder)
"""

import streamlit as st
import streamlit.components.v1 as components


WARP_LOADER_CSS = """
<style>
.warp-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 40px 20px;
}

.warp-loader {
    position: relative;
    width: 120px;
    height: 120px;
}

.ring {
    position: absolute;
    top: 50%;
    left: 50%;
    width: 100%;
    height: 100%;
    border-radius: 50%;
    transform: translate(-50%, -50%);
    background: radial-gradient(
        circle,
        rgba(47, 255, 255, 0.15) 30%,
        transparent 70%
    );
    animation: pulse 2.2s ease-out infinite;
    opacity: 0;
    box-shadow:
        0 0 12px rgba(47, 255, 255, 0.4),
        0 0 24px rgba(47, 255, 255, 0.2);
    border: 2px solid rgba(47, 255, 255, 0.2);
}

.ring:nth-child(1) { animation-delay: 0s; }
.ring:nth-child(2) { animation-delay: 0.4s; }
.ring:nth-child(3) { animation-delay: 0.8s; }
.ring:nth-child(4) { animation-delay: 1.2s; }

@keyframes pulse {
    0% {
        transform: translate(-50%, -50%) scale(0.3);
        opacity: 1;
    }
    70% {
        transform: translate(-50%, -50%) scale(1.1);
        opacity: 0.15;
    }
    100% {
        transform: translate(-50%, -50%) scale(1.4);
        opacity: 0;
    }
}

.core-glow {
    position: absolute;
    top: 50%;
    left: 50%;
    width: 20px;
    height: 20px;
    transform: translate(-50%, -50%);
    border-radius: 50%;
    background: radial-gradient(circle at center, #00e5ff, #0099cc);
    box-shadow:
        0 0 25px #00e5ff,
        0 0 60px rgba(0, 229, 255, 0.5),
        0 0 100px rgba(0, 229, 255, 0.2);
    animation: corePulse 1.6s ease-in-out infinite;
}

@keyframes corePulse {
    0%, 100% { transform: translate(-50%, -50%) scale(1); }
    50% { transform: translate(-50%, -50%) scale(1.2); }
}

.loading-text {
    color: #94a3b8;
    font-size: 1rem;
    margin-top: 20px;
    font-family: 'Plus Jakarta Sans', sans-serif;
}
</style>
"""


def show_loading(message: str = "Loading...", height: int = 200):
    """
    Show warp loading animation.
    
    Args:
        message: Text to display below animation
        height: Height of the component
        
    Returns:
        placeholder: st.empty() placeholder to clear later
    """
    placeholder = st.empty()
    
    html = f"""
    {WARP_LOADER_CSS}
    <div class="warp-container">
        <div class="warp-loader">
            <div class="ring"></div>
            <div class="ring"></div>
            <div class="ring"></div>
            <div class="ring"></div>
            <div class="core-glow"></div>
        </div>
        <div class="loading-text">{message}</div>
    </div>
    """
    
    with placeholder.container():
        components.html(html, height=height)
    
    return placeholder


def hide_loading(placeholder):
    """Clear the loading animation."""
    if placeholder:
        placeholder.empty()


# Simple fallback - progress bar style
def show_simple_loading(message: str = "Loading..."):
    """
    Show simple loading bar (fallback).
    
    Returns:
        placeholder: st.empty() placeholder to clear later
    """
    placeholder = st.empty()
    with placeholder.container():
        st.markdown(f"**{message}**")
        st.progress(0)
    return placeholder


def update_simple_loading(placeholder, progress: float, message: str = None):
    """Update simple loading bar progress (0.0 to 1.0)."""
    if placeholder:
        with placeholder.container():
            if message:
                st.markdown(f"**{message}**")
            st.progress(progress)



