import os
from typing import Any, Dict, Optional


class SharingService:
    """Small backend service for optional peer-to-peer sharing features.

    This keeps the app logic separate from Flask routes and allows the app to
    support:
    - connecting to a preconfigured Talescale network
    - uploading backups to a private Pi or server
    - sharing a public profile with friends
    - enabling AI-based recommendations when an external backend is available
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.tailscale_network = self.config.get("tailscale_network") or os.getenv("TAILSCALE_NETWORK")
        self.pi_host = self.config.get("pi_host") or os.getenv("PI_HOST")
        self.pi_user = self.config.get("pi_user") or os.getenv("PI_USER")
        self.pi_path = self.config.get("pi_path") or os.getenv("PI_PATH", "/home/pi/bookscan-backups")
        self.recommendation_backend = self.config.get("recommendation_backend") or os.getenv("RECOMMENDATION_BACKEND")

    def enable_sharing(self, user_id: int, enabled: bool) -> Dict[str, Any]:
        if not enabled:
            return {"ok": True, "status": "disabled"}

        if not self.tailscale_network:
            return {
                "ok": False,
                "status": "config_missing",
                "message": "Talescale network is not configured. Set TAILSCALE_NETWORK or pass it in config.",
            }

        return {
            "ok": True,
            "status": "enabled",
            "message": "Sharing is enabled. The app will attempt to join the configured Talescale network.",
            "tailscale_network": self.tailscale_network,
            "pi_host": self.pi_host,
        }

    def upload_backup(self, user_id: int, backup_path: str) -> Dict[str, Any]:
        if not backup_path:
            return {"ok": False, "status": "missing_backup", "message": "No backup path provided."}

        if not self.pi_host:
            return {
                "ok": False,
                "status": "config_missing",
                "message": "No Pi host configured. Set PI_HOST or pass it in config.",
            }

        return {
            "ok": True,
            "status": "queued",
            "message": f"Backup upload requested for {backup_path} to {self.pi_host}",
            "remote_path": self._build_remote_path(backup_path),
        }

    def enable_recommendations(self, user_id: int) -> Dict[str, Any]:
        if not self.recommendation_backend:
            return {
                "ok": False,
                "status": "requires_installation",
                "message": "No recommendation backend configured. Install or configure an AI service before enabling recommendations.",
            }

        return {
            "ok": True,
            "status": "enabled",
            "message": f"Recommendation backend {self.recommendation_backend} is ready.",
        }

    def build_public_profile(self, user_id: int, db: Any, username: str) -> Dict[str, Any]:
        book_count = db.count_books() if hasattr(db, "count_books") else 0
        read_count = db.get_read_count() if hasattr(db, "get_read_count") else 0
        if hasattr(read_count, "__getitem__") and not isinstance(read_count, int):
            try:
                read_count = read_count[0]
            except (TypeError, IndexError):
                read_count = 0
        return {
            "user_id": user_id,
            "username": username,
            "sharing_enabled": True,
            "book_count": book_count,
            "read_count": read_count,
            "recommendations_enabled": False,
            "profile_visible": True,
        }

    def _build_remote_path(self, backup_path: str) -> str:
        filename = os.path.basename(backup_path)
        return os.path.join(self.pi_path, filename)
