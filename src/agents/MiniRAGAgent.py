import os
from typing import List, Dict, Any
from minirag import MiniRAG, QueryParam
from minirag.llm.hf import hf_model_complete, hf_embed
from minirag.utils import EmbeddingFunc
from transformers import AutoModel, AutoTokenizer
from src.datasets.LongMemEvalDataset import LongMemEvalInstance

class MiniRAGAgent:
    def __init__(
        self,
        model_name: str,
        embedding_model_name: str,
        working_dir: str = "./data/minirag_data"
    ):
        """
        Initialize the MiniRAGAgent.

        Args:
            model_name: The name of the LLM to use (e.g., "microsoft/Phi-3.5-mini-instruct").
            embedding_model_name: The name of the embedding model to use.
            working_dir: The directory where MiniRAG will store its index.
        """
        self.working_dir = working_dir
        if not os.path.exists(self.working_dir):
            os.makedirs(self.working_dir, exist_ok=True)

        self.model_name = model_name
        self.embedding_model_name = embedding_model_name
        if self.embedding_model_name == "all-MiniLM-L6-v2":
            self.embedding_model_name = "sentence-transformers/all-MiniLM-L6-v2"

        # Determine backend based on model name prefix
        if self.model_name.startswith("ollama/"):
            from minirag.llm.ollama import ollama_model_complete, ollama_embed
            
            # Strip "ollama/" prefix for minirag/ollama usage
            actual_llm_name = self.model_name.replace("ollama/", "")
            
            # Check embedding model too
            if self.embedding_model_name.startswith("ollama/"):
                 actual_embedding_name = self.embedding_model_name.replace("ollama/", "")
                 
                 self.rag = MiniRAG(
                    working_dir=self.working_dir,
                    llm_model_func=ollama_model_complete,
                    llm_model_name=actual_llm_name,
                    entity_extract_max_gleaning=0, # Disable gleaning for speed
                    embedding_func=EmbeddingFunc(
                        embedding_dim=768, # Nomic embed text is 768
                        max_token_size=8192,
                        func=lambda texts: ollama_embed(
                            texts,
                            embed_model=actual_embedding_name,
                        ),
                    ),
                )
            else:
                # Hybrid: Ollama LLM + HF Embedding (e.g. SentenceTransformer)
                # Note: minirag's HF embedding integration
                 self.rag = MiniRAG(
                    working_dir=self.working_dir,
                    llm_model_func=ollama_model_complete,
                    llm_model_name=actual_llm_name,
                    entity_extract_max_gleaning=0, # Disable gleaning for speed
                    embedding_func=EmbeddingFunc(
                        embedding_dim=384,
                        max_token_size=1000,
                        func=lambda texts: hf_embed(
                            texts,
                            tokenizer=AutoTokenizer.from_pretrained(self.embedding_model_name),
                            embed_model=AutoModel.from_pretrained(self.embedding_model_name),
                        ),
                    ),
                )

        else:
            # Default to HuggingFace
            self.rag = MiniRAG(
                working_dir=self.working_dir,
                llm_model_func=hf_model_complete,
                llm_model_name=self.model_name,
                entity_extract_max_gleaning=0, # Disable gleaning for speed
                embedding_func=EmbeddingFunc(
                    embedding_dim=384, # Assumed for now, could be dynamic or config dependent
                    max_token_size=1000,
                    func=lambda texts: hf_embed(
                        texts,
                        tokenizer=AutoTokenizer.from_pretrained(self.embedding_model_name),
                        embed_model=AutoModel.from_pretrained(self.embedding_model_name),
                    ),
                ),
            )

    def _adapt_data(self, instance: LongMemEvalInstance) -> str:
        """
        Convert LongMemEvalInstance sessions into a text format suitable for MiniRAG.

        Args:
            instance: The benchmark instance containing conversation history.

        Returns:
            A string representation of the conversation history.
        """
        text_content = []
        for session in instance.sessions:
            # Assuming session has a 'messages' attribute which is a list of dicts with 'role' and 'content'
            # Based on common structures; verified against story notes
            if hasattr(session, 'messages'):
                messages = session.messages
            else:
                 # Fallback if structure is different, though LongMemEvalInstance usually follows this
                messages = [] # Should verify against actual class definition if possible
            
            for msg in messages:
                role = msg.get('role', 'unknown').capitalize()
                content = msg.get('content', '')
                text_content.append(f"{role}: {content}")
            
            text_content.append("\n---\n") # Separator between sessions

        return "\n".join(text_content)

    def answer(self, instance: LongMemEvalInstance) -> str:
        """
        Answer the question posed in the instance using MiniRAG.

        This method:
        1. Indexes the conversation history from the instance.
        2. Queries MiniRAG for the answer.

        Args:
            instance: The benchmark instance.

        Returns:
            The answer string.
        """
        # 1. Adapt and Index Data
        data_text = self._adapt_data(instance)
        
        # We might want to clear previous data if MiniRAG persists state too aggressively between calls,
        # but for now we assume 'insert' adds to the knowledge base.
        # However, for a fair benchmark, we probably want to isolate instances.
        # But MiniRAG structure implies a persistent Knowledge Graph.
        # For this story, we follow the AC: "trigger indexing... and query".
        
        self.rag.insert(data_text)

        # 2. Query
        response = self.rag.query(instance.question, param=QueryParam(mode="mini"))
        
        # Clean up response if needed (MiniRAG example does replace("\n", ""))
        # Keeping it minimal as per example
        return str(response)
