import sys
from unittest.mock import MagicMock

# Mock minirag modules BEFORE importing MiniRAGAgent to avoid ImportErrors due to missing dependencies
mock_minirag_module = MagicMock()
sys.modules["minirag"] = mock_minirag_module
sys.modules["minirag.llm"] = MagicMock()
sys.modules["minirag.llm.hf"] = MagicMock()
sys.modules["minirag.utils"] = MagicMock()

# Mock transformers
mock_transformers = MagicMock()
sys.modules["transformers"] = mock_transformers

# Mock pandas
sys.modules["pandas"] = MagicMock()



import pytest
from unittest.mock import patch
from src.agents.MiniRAGAgent import MiniRAGAgent
from src.datasets.LongMemEvalDataset import LongMemEvalInstance, Session

# Mock dependencies
@pytest.fixture
def mock_minirag():
    with patch("src.agents.MiniRAGAgent.MiniRAG") as mock:
        yield mock

@pytest.fixture
def mock_hf_model_complete():
    with patch("src.agents.MiniRAGAgent.hf_model_complete") as mock:
        yield mock

@pytest.fixture
def mock_hf_embed():
    with patch("src.agents.MiniRAGAgent.hf_embed") as mock:
        yield mock

@pytest.fixture
def mock_auto_tokenizer():
    with patch("src.agents.MiniRAGAgent.AutoTokenizer") as mock:
        yield mock

@pytest.fixture
def mock_auto_model():
    with patch("src.agents.MiniRAGAgent.AutoModel") as mock:
        yield mock

@pytest.fixture
def mock_embedding_func():
    with patch("src.agents.MiniRAGAgent.EmbeddingFunc") as mock:
        yield mock

def test_initialization(mock_minirag, mock_hf_model_complete, mock_embedding_func):
    """Test that MiniRAGAgent initializes MiniRAG with correct parameters."""
    model_name = "test-model"
    embedding_model_name = "test-embedding-model"
    working_dir = "./test_data"
    
    agent = MiniRAGAgent(model_name, embedding_model_name, working_dir)
    
    mock_minirag.assert_called_once()
    _, kwargs = mock_minirag.call_args
    assert kwargs["working_dir"] == working_dir
    assert kwargs["llm_model_name"] == model_name
    assert kwargs["llm_model_func"] == mock_hf_model_complete
    # We can't easily check equal on the lambda, but we check EmbeddingFunc was called
    mock_embedding_func.assert_called_once()

def test_adapt_data():
    """Test converting LongMemEvalInstance to text format."""
    # Create sample instance
    sessions = [
        Session(
            session_id="s1",
            date="2023-01-01",
            messages=[
                {"role": "user", "content": "Hello"},
                {"role": "assistant", "content": "Hi there"}
            ]
        ),
        Session(
            session_id="s2",
            date="2023-01-02",
            messages=[
                {"role": "user", "content": "How are you?"},
                # Testing fallback or missing assistant reply
            ]
        )
    ]
    instance = LongMemEvalInstance(
        question_id="q1",
        question="What happened?",
        sessions=sessions,
        t_question="2023-01-03",
        answer="Something"
    )
    
    # We strip external dependencies for this unit test of private method
    # But since it's private, we test it via what logic we know, or by exposing it.
    # Python allows calling private methods for testing.
    agent = MiniRAGAgent("model", "embed", "./tmp")
    adapted_text = agent._adapt_data(instance)
    
    expected_text = (
        "User: Hello\n"
        "Assistant: Hi there\n"
        "\n---\n\n"
        "User: How are you?\n"
        "\n---\n"
    )
    
    assert adapted_text == expected_text

def test_answer_flow(mock_minirag):
    """Test the answer method flow: adapt -> insert -> query."""
    # Setup mocks
    mock_rag_instance = MagicMock()
    mock_minirag.return_value = mock_rag_instance
    mock_rag_instance.query.return_value = "The answer is 42"
    
    agent = MiniRAGAgent("model", "embed", "./tmp")
    
    # Setup Input
    sessions = [
        Session("s1", "date", [{"role": "user", "content": "Context"}])
    ]
    instance = LongMemEvalInstance("q1", "Question?", sessions, "date", "Answer")
    
    # Execute
    result = agent.answer(instance)
    
    # Verify
    assert result == "The answer is 42"
    
    # Verify insert was called with adapted text
    mock_rag_instance.insert.assert_called_once()
    args, _ = mock_rag_instance.insert.call_args
    assert "User: Context" in args[0]
    
    # Verify query was called with question
    mock_rag_instance.query.assert_called_once()
    q_args, q_kwargs = mock_rag_instance.query.call_args
    assert q_args[0] == "Question?"
    
    # Verify QueryParam was called with mode="mini"
    # We access the mocked QueryParam class via sys.modules
    sys.modules["minirag"].QueryParam.assert_called_with(mode="mini")

