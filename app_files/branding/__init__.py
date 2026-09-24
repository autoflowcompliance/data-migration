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
    BrandProfile,
    PortalEntry,
    ProfileError,
    ProfileSet,
    apply_profile_to_report,
    build_portal,
    load_profiles,
    portal_entries_from_directory,
    profiles_path,
    save_profiles,
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
    "BrandProfile",
    "Branding",
    "PortalEntry",
    "ProfileError",
    "ProfileSet",
    "apply_profile_to_report",
    "branding_path",
    "build_portal",
    "inject_branding",
    "inject_branding_into_bytes",
    "inject_demo_watermark",
    "load_branding",
    "load_profiles",
    "logo_data_uri",
    "normalise_colour",
    "portal_entries_from_directory",
    "profiles_path",
    "save_branding",
    "save_profiles",
]