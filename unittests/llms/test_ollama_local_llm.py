import sys
import os
import pytest
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from llms.ollama_local_llm import OllamaLocalLLM
from llms.llm_factory import LLMFactory
from utils.constants import LLM_PROVIDER_OLLAMA, OLLAMA_MODEL_DEFAULT

@patch("llms.ollama_local_llm.ChatOllama")
def test_ollama_local_llm_get_llm(mock_chat_ollama):
    """Test getting ChatOllama model from OllamaLocalLLM."""
    mock_instance = MagicMock()
    mock_chat_ollama.return_value = mock_instance

    llm_wrapper = OllamaLocalLLM()
    model = llm_wrapper.get_llm(model_name="llama3", base_url="http://localhost:11434")

    mock_chat_ollama.assert_called_once_with(
        model="llama3",
        base_url="http://localhost:11434"
    )
    assert model == mock_instance


@patch("llms.ollama_local_llm.ChatOllama")
def test_llm_factory_ollama(mock_chat_ollama):
    """Test instantiating Ollama model via LLMFactory."""
    mock_instance = MagicMock()
    mock_chat_ollama.return_value = mock_instance

    factory = LLMFactory()
    model = factory.get_llm(LLM_PROVIDER_OLLAMA, "llama3")

    assert model == mock_instance
