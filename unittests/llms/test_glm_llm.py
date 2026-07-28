import sys
import os
import pytest
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from llms.glm_llm import GLMLLM
from llms.llm_factory import LLMFactory
from utils.constants import LLM_PROVIDER_GLM, GLM_MODEL_4_7, GLM_API_BASE

@patch("llms.glm_llm.ChatOpenAI")
def test_glm_llm_get_llm(mock_chat_openai):
    """Test getting GLM ChatOpenAI model from GLMLLM."""
    mock_instance = MagicMock()
    mock_chat_openai.return_value = mock_instance

    llm_wrapper = GLMLLM()
    model = llm_wrapper.get_llm(mode_name=GLM_MODEL_4_7)

    mock_chat_openai.assert_called_once_with(
        model=GLM_MODEL_4_7,
        openai_api_key=llm_wrapper.glm_api_key,
        openai_api_base=GLM_API_BASE
    )
    assert model == mock_instance


@patch("llms.glm_llm.ChatOpenAI")
def test_llm_factory_glm(mock_chat_openai):
    """Test instantiating GLM model via LLMFactory."""
    mock_instance = MagicMock()
    mock_chat_openai.return_value = mock_instance

    with patch.dict(os.environ, {"GLM_API_KEY": "dummy-glm-key"}):
        factory = LLMFactory()
        model = factory.get_llm(LLM_PROVIDER_GLM, GLM_MODEL_4_7)
        assert model == mock_instance
