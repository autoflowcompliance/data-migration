"""Branding layer: white-label reports and agency settings.

The core reporter is frozen, so branding is applied by post-processing the
rendered HTML — see :func:`inject_branding`. Templates opt in by carrying the
``{{BRAND_*}}`` placeholders; unmodified templates simply pass through.
"""

from app_files.branding.injector import (
    inject_branding,
    inject_branding_into_bytes,
    inject_demo_watermark,
    logo_data_uri,
)
from app_files.branding.profiles import (
    PROFILES_FILENAME,
    BrandProfileError,
    delete_profile,
    load_profiles,
    profile_names,
    profiles_path,
    resolve_profile,
    save_profile,
)
from app_files.branding.settings import (
    BRANDING_FILENAME,
    Branding,
    branding_path,
    load_branding,
    normalise_colour,
    save_branding,
)

__all__ = [
    "BRANDING_FILENAME",
    "PROFILES_FILENAME",
    "BrandProfileError",
    "Branding",
    "branding_path",
    "delete_profile",
    "inject_branding",
    "inject_branding_into_bytes",
    "inject_demo_watermark",
    "load_branding",
    "load_profiles",
    "logo_data_uri",
    "normalise_colour",
    "profile_names",
    "profiles_path",
    "resolve_profile",
    "save_branding",
    "save_profile",
]