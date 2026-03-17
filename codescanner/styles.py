from rich.theme import Theme

# Muted, professional Cybersecurity Analysis theme
BRAND_COLOR = "#3B82F6"   # Secure Blue (Blue 500)
SUCCESS_COLOR = "#10B981" # Risk Filtered (Emerald 500)
WARNING_COLOR = "#F59E0B" # High Risk (Amber 500)
ERROR_COLOR = "#EF4444"   # Critical Risk (Red 500)
NOISE_COLOR = "#64748B"   # Theoretical Noise (Slate 500)

THEME = Theme({
    "brand": BRAND_COLOR,
    "success": SUCCESS_COLOR,
    "warning": WARNING_COLOR,
    "error": ERROR_COLOR,
    "noise": NOISE_COLOR,
    "progress.description": "white",
    "progress.percentage": BRAND_COLOR,
})
