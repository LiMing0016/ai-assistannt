from app.core.config import Settings
from app.core.dependencies import build_backend_client
from app.integrations.backend_client import JavaBackendClient, MockBackendClient


def test_build_backend_client_returns_java_client_in_live_mode() -> None:
    client = build_backend_client(
        Settings(
            _env_file=None,
            backend_mode="live",
            backend_base_url="http://backend.test",
        )
    )

    assert isinstance(client, JavaBackendClient)


def test_build_backend_client_returns_mock_client_in_mock_mode() -> None:
    client = build_backend_client(
        Settings(
            _env_file=None,
            backend_mode="mock",
        )
    )

    assert isinstance(client, MockBackendClient)
