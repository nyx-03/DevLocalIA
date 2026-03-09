import pytest
from pydantic import ValidationError

from app.models.schema import ChatRequest, ProjectIndexRequest, RefactorRequest, TestRequest


def test_chat_request_rejects_empty_query():
    with pytest.raises(ValidationError):
        ChatRequest(project_id=1, query="   ", max_chunks=5)


def test_chat_request_rejects_bad_chunks():
    with pytest.raises(ValidationError):
        ChatRequest(project_id=1, query="hello", max_chunks=0)


def test_project_index_request_strips_path():
    req = ProjectIndexRequest(root_path="  /tmp/project  ")
    assert req.root_path == "/tmp/project"


def test_refactor_request_invalid_style():
    with pytest.raises(ValidationError):
        RefactorRequest(project_id=1, target="x", style="wild")


def test_test_request_framework_only_pytest():
    with pytest.raises(ValidationError):
        TestRequest(project_id=1, target="x", framework="unittest")
