from typing import Literal
from pydantic import BaseModel, Field

class Config(BaseModel):
    """Configuration class for LongMemEval experiments."""

    memory_model_name: str = Field(default="ollama/gemma3:4b", description="Memory model name")
    embedding_model_name: str = Field(
        default="all-MiniLM-L6-v2", description="Name of the embedding model"
    )
    judge_model_name: str = Field(default="gemini/gemini-2.5-flash", description="Judge model name")

    longmemeval_dataset_type: Literal["oracle", "short", "long"] = Field(
        ..., description="Type of LongMemEval dataset to use"
    )

    agent_type: Literal["rag", "minirag"] = Field(
        default="rag", description="Type of agent to use"
    )

    longmemeval_dataset_set: Literal["longmemeval", "investigathon_evaluation", "investigathon_held_out"] = Field(
        ..., description="Set of LongMemEval dataset to use"
    )

    N: int = Field(default=10, description="Number of samples to process")

    class Config:
        """Pydantic configuration."""

        extra = "forbid"  # Prevent extra fields
        validate_assignment = True  # Validate on assignment
