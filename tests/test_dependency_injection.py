from app.api import routes
from app.services.chat import ChatService
from app.services.project_service import ProjectService


def test_get_chat_service():
    service = routes.get_chat_service()
    assert isinstance(service, ChatService)


def test_get_project_service():
    service = routes.get_project_service()
    assert isinstance(service, ProjectService)
