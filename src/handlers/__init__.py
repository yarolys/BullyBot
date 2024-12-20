from .start import router as start_router
from .join2group import router as join2group_router

from .panel_for_admin.admin_panel import router as admin_panel_router
from .panel_for_admin.add_sound import router as add_sound_router
from .panel_for_admin.check_sounds import router as check_sounds_router
from .panel_for_admin.delete_sound import router as delete_sound_router
from .panel_for_admin.welcome_message import router as welcome_message_router

from .audio.voice import router as voice_router
from .panel_for_admin.dynamic_buttons import router as dynamic_buttons_router