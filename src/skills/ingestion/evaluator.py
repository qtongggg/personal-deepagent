import json
import logging
import re
import uuid
from typing import Any, Dict, List, Optional
import chromadb
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import HumanMessage
from src.utils.models import get_default_model
from src.skills.ingestion.schemas import EvaluationProbe, EvaluationResult, IngestionChunk

logger = logging.getLogger(__name__)


def generate_section_probes(
    chunk: IngestionChunk,
    model: Optional[BaseChatModel] = None,
) -> List[EvaluationProbe]:
    """Generate 3 distinct paraphrased probe questions for a chunk."""
    active_model = model or get_default_model()

    prompt = (
        f"You are an evaluator assessing search retrieval quality.\n"
        f"Generate exactly 3 semantically distinct, paraphrased search questions that directly ask about "
        f"the concepts, definitions, or mechanisms described in this text passage.\n"
        f"Vary the vocabulary and angle between the 3 questions.\n\n"
        f"Section Header: {chunk.header_path}\n"
        f"Passage Text:\n{chunk.chunk_content[:1500]}\n\n"
        f"Return ONLY a JSON list of 3 strings, e.g. [\"question 1\", \"question 2\", \"question 3\"]."
    )

    try:
        response = active_model.invoke([HumanMessage(content=prompt)])
        content = response.content
        if isinstance(content, list):
            content = "".join(str(b.get("text", "")) if isinstance(b, dict) else str(b) for b in content)

        cleaned_json = re.sub(r"^```(?:json)?\s*|\s*```$", "", str(content).strip(), flags=re.MULTILINE)
        raw_list = json.loads(cleaned_json)

        if isinstance(raw_list, list) and len(raw_list) >= 1:
            probes = []
            for i, q in enumerate(raw_list[:3]):
                probes.append(
                    EvaluationProbe(
                        probe_id=f"{chunk.chunk_id}_probe_{i+1}",
                        target_header_path=chunk.header_path,
                        query_text=str(q),
                        variation_idx=i + 1,
                    )
                )
            return probes
    except Exception as e:
        logger.debug(f"LLM probe generation failed ({e}), using heuristic probes.")

    # Heuristic fallback probes from section title and content
    words = [w for w in re.findall(r"\w+", chunk.chunk_content) if len(w) > 4][:10]
    sample_phrase = " ".join(words[:4]) if words else "overview"
    section_name = chunk.header_path.split(">")[-1].strip()

    return [
        EvaluationProbe(
            probe_id=f"{chunk.chunk_id}_probe_1",
            target_header_path=chunk.header_path,
            query_text=f"What does the paper explain about {section_name}?",
            variation_idx=1,
        ),
        EvaluationProbe(
            probe_id=f"{chunk.chunk_id}_probe_2",
            target_header_path=chunk.header_path,
            query_text=f"Describe the framework and key mechanisms in {section_name} {sample_phrase}.",
            variation_idx=2,
        ),
        EvaluationProbe(
            probe_id=f"{chunk.chunk_id}_probe_3",
            target_header_path=chunk.header_path,
            query_text=f"How does the study address {sample_phrase}?",
            variation_idx=3,
        ),
    ]


def evaluate_chunks(
    chunks: List[IngestionChunk],
    model: Optional[BaseChatModel] = None,
    threshold: float = 0.8,
) -> EvaluationResult:
    """Evaluate candidate chunks in an ephemeral staging vector index using paraphrased probes."""
    if not chunks:
        return EvaluationResult(
            total_probes=0,
            successful_retrievals=0,
            recall_score=0.0,
            passed=False,
            failing_sections=["Empty document"],
        )

    # 1. Spin up an in-memory ephemeral Chroma client
    client = chromadb.EphemeralClient()
    staging_coll_name = f"staging_{uuid.uuid4().hex[:12]}"
    collection = client.create_collection(staging_coll_name)

    try:
        # 2. Stage candidate chunks
        ids = [c.chunk_id for c in chunks]
        docs = [c.chunk_content for c in chunks]
        metas = [
            {
                "chunk_id": c.chunk_id,
                "document_name": c.document_name,
                "header_path": c.header_path,
            }
            for c in chunks
        ]
        collection.add(ids=ids, documents=docs, metadatas=metas)

        # 3. Generate probes and test retrieval
        total_probes = 0
        successful = 0
        failing_sections_set = set()
        diagnostics = []

        for chunk in chunks:
            probes = generate_section_probes(chunk, model=model)
            section_successes = 0

            for probe in probes:
                total_probes += 1
                res = collection.query(query_texts=[probe.query_text], n_results=1)

                hit = False
                retrieved_header = None
                if res and res["metadatas"] and res["metadatas"][0]:
                    retrieved_header = res["metadatas"][0][0].get("header_path")
                    dist = res["distances"][0][0] if res.get("distances") and res["distances"][0] else 0.0
                    # Match if the target header matches AND semantic distance is within relevance bound
                    if (retrieved_header == probe.target_header_path or probe.target_header_path in str(retrieved_header)) and dist <= 1.25:
                        hit = True

                if hit:
                    successful += 1
                    section_successes += 1
                else:
                    diagnostics.append({
                        "probe": probe.query_text,
                        "expected_header": probe.target_header_path,
                        "got_header": retrieved_header,
                    })

            if probes and (section_successes / len(probes)) < threshold:
                failing_sections_set.add(chunk.header_path)

        recall_score = round(successful / total_probes, 4) if total_probes > 0 else 0.0
        passed = recall_score >= threshold
        failing_sections = list(failing_sections_set) if not passed else []

        return EvaluationResult(
            total_probes=total_probes,
            successful_retrievals=successful,
            recall_score=recall_score,
            passed=passed,
            failing_sections=failing_sections,
            diagnostic_logs=diagnostics,
        )
    finally:
        try:
            client.delete_collection(staging_coll_name)
        except Exception:
            pass
