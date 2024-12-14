import pytest

from src.admin_panel.service import AdminPanelService


@pytest.fixture()
def admin_panel_service(cnn):
    return AdminPanelService(cnn=cnn)


async def test_user_has_history(admin_panel_service: AdminPanelService):
    assert await admin_panel_service.has_history("user")


async def test_user_history_doesnt_have_history(admin_panel_service: AdminPanelService):
    assert not await admin_panel_service.has_history("user_history")


async def test_user_columns(admin_panel_service: AdminPanelService):
    columns = await admin_panel_service.get_column_info("user")
    assert not columns["id"].is_required
    assert columns["email"].is_required
