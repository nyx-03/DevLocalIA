from app.llm.prompts import chat_prompt, join_context_blocks


def test_join_context_blocks_empty():
    assert join_context_blocks([]) == "(aucun contexte trouvé)"


def test_chat_prompt_contains_sections():
    prompt = chat_prompt("question", "contexte")
    assert "Question utilisateur" in prompt
    assert "Contexte code" in prompt
