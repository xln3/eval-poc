from __future__ import annotations

import asyncio
from typing import Literal

from inspect_ai import Task, task
from inspect_ai.model import ChatMessageUser, GenerateConfig
from inspect_ai.solver import Generate, Solver, TaskState, solver

from .dataset import build_saferag_samples
from .scorer import saferag_scorer
from .utils import ensure_saferag_on_path, resolve_saferag_root, run_with_saferag_cwd

DEFAULT_TEMPERATURE = 0.01
DEFAULT_MAX_TOKENS = 4096


def _resolve_default_embedding_path() -> str:
    root = resolve_saferag_root()
    return str(root / "bge-base-zh-v1.5")


def _resolve_default_docs_path() -> str:
    root = resolve_saferag_root()
    return str(root / "knowledge_base")


def _resolve_default_data_path() -> str:
    root = resolve_saferag_root()
    return str(root / "nctd_datasets" / "nctd.json")


def _load_prompt_template() -> str:
    root = resolve_saferag_root()
    prompt_path = root / "prompts" / "quest_answer.txt"
    return prompt_path.read_text(encoding="utf-8")


def _parse_response(text: str) -> str:
    if "<response>" in text and "</response>" in text:
        return text.split("<response>")[-1].split("</response>")[0].strip()
    return text.strip()


def _load_saferag_modules(retriever_name: str):
    ensure_saferag_on_path()

    from embeddings.base import HuggingfaceEmbeddings
    from retrievers.base import BaseRetriever
    from tasks.nctd_attack import (
        Inter_context_conflict,
        Silver_noise,
        Soft_ad,
        White_DoS,
    )

    classes = {
        "HuggingfaceEmbeddings": HuggingfaceEmbeddings,
        "BaseRetriever": BaseRetriever,
        "Silver_noise": Silver_noise,
        "Inter_context_conflict": Inter_context_conflict,
        "Soft_ad": Soft_ad,
        "White_DoS": White_DoS,
    }

    if retriever_name == "bm25":
        from retrievers.bm25 import CustomBM25Retriever

        classes["CustomBM25Retriever"] = CustomBM25Retriever
    elif retriever_name == "hybrid":
        from retrievers.hybrid import EnsembleRetriever

        classes["EnsembleRetriever"] = EnsembleRetriever
    elif retriever_name == "hybrid-rerank":
        from retrievers.hybrid_rerank import EnsembleRerankRetriever

        classes["EnsembleRerankRetriever"] = EnsembleRerankRetriever

    return classes


@solver
def saferag_generate(
    retriever,
    prompt_template: str,
) -> Solver:
    async def solve(state: TaskState, generate: Generate) -> TaskState:
        question = state.input_text

        loop = asyncio.get_running_loop()
        retrieve_context, filtered_response_text = await loop.run_in_executor(
            None, lambda: run_with_saferag_cwd(retriever.search_docs, question)
        )

        if state.metadata is None:
            state.metadata = {}
        state.metadata["questions"] = question
        state.metadata["retrieve_context"] = str(retrieve_context)
        state.metadata["filtered_retrieve_context"] = filtered_response_text

        prompt = prompt_template.format(
            question=question,
            search_documents=filtered_response_text,
        )
        state.messages = [ChatMessageUser(content=prompt)]

        state = await generate(state)

        completion = state.output.completion if state.output else ""
        state.metadata["raw_completion"] = completion
        state.metadata["generated_text"] = _parse_response(completion)

        return state

    return solve


def _build_retriever(
    retriever_name: str,
    attack_data_path: str,
    clean_docs_path: str,
    attack_task: str,
    attack_module: str,
    attack_intensity: float,
    embed_model,
    embed_dim: int,
    filter_module: str,
    chunk_size: int,
    chunk_overlap: int,
    collection_name: str,
    retrieve_top_k: int,
    classes: dict,
):
    BaseRetriever = classes["BaseRetriever"]
    if retriever_name == "base":
        return BaseRetriever(
            attack_data_path,
            clean_docs_path,
            attack_task,
            attack_module,
            attack_intensity,
            embed_model=embed_model,
            embed_dim=embed_dim,
            filter_module=filter_module,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            collection_name=collection_name,
            similarity_top_k=retrieve_top_k,
        )
    if retriever_name == "bm25":
        CustomBM25Retriever = classes["CustomBM25Retriever"]
        return CustomBM25Retriever(
            attack_data_path,
            clean_docs_path,
            attack_task,
            attack_module,
            attack_intensity,
            embed_model=embed_model,
            embed_dim=embed_dim,
            filter_module=filter_module,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            collection_name=collection_name,
            similarity_top_k=retrieve_top_k,
        )
    if retriever_name == "hybrid":
        EnsembleRetriever = classes["EnsembleRetriever"]
        return EnsembleRetriever(
            attack_data_path,
            clean_docs_path,
            attack_task,
            attack_module,
            attack_intensity,
            embed_model=embed_model,
            embed_dim=embed_dim,
            filter_module=filter_module,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            collection_name=collection_name,
            similarity_top_k=retrieve_top_k,
        )
    if retriever_name == "hybrid-rerank":
        EnsembleRerankRetriever = classes["EnsembleRerankRetriever"]
        return EnsembleRerankRetriever(
            attack_data_path,
            clean_docs_path,
            attack_task,
            attack_module,
            attack_intensity,
            embed_model=embed_model,
            embed_dim=embed_dim,
            filter_module=filter_module,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            collection_name=collection_name,
            similarity_top_k=retrieve_top_k,
        )

    raise ValueError(f"Unknown retriever: {retriever_name}")


def _build_attack_task(
    attack_task: str,
    quest_eval_model: str,
    use_quest_eval: bool,
    use_bert_score: bool,
    classes: dict,
):
    task_mapping = {
        "SN": classes["Silver_noise"],
        "ICC": classes["Inter_context_conflict"],
        "SA": classes["Soft_ad"],
        "WDoS": classes["White_DoS"],
    }
    if attack_task not in task_mapping:
        raise ValueError(f"Unknown attack task: {attack_task}")
    return task_mapping[attack_task](
        quest_eval_model=quest_eval_model,
        attack_task=attack_task,
        use_quest_eval=use_quest_eval,
        use_bert_score=use_bert_score,
    )


@task
def saferag(
    attack_task: Literal["SN", "ICC", "SA", "WDoS"] = "SN",
    attack_module: Literal["indexing", "retrieval", "generation"] = "indexing",
    attack_intensity: float = 0.5,
    retriever_name: Literal["base", "bm25", "hybrid", "hybrid-rerank"] = "bm25",
    filter_module: Literal["off", "nli", "skr"] = "off",
    retrieve_top_k: int | None = None,
    clean_docs_path: str | None = None,
    attack_data_path: str | None = None,
    embedding_name: str | None = None,
    embedding_dim: int = 768,
    embedding_device: str = "cpu",
    chunk_size: int = 256,
    chunk_overlap: int = 0,
    collection_name: str = "chuncksize_256",
    shuffle: bool = False,
    seed: int = 22,
    limit: int | None = None,
    quest_eval_model: str = "deepseek-chat",
    use_quest_eval: bool = False,
    use_bert_score: bool = False,
    temperature: float = DEFAULT_TEMPERATURE,
    max_tokens: int = DEFAULT_MAX_TOKENS,
) -> Task:
    if retrieve_top_k is None:
        retrieve_top_k = 6 if attack_task == "SN" else 2

    docs_path = clean_docs_path or _resolve_default_docs_path()
    data_path = attack_data_path or _resolve_default_data_path()
    embed_path = embedding_name or _resolve_default_embedding_path()

    classes = _load_saferag_modules(retriever_name)
    HuggingfaceEmbeddings = classes["HuggingfaceEmbeddings"]

    embed_model = HuggingfaceEmbeddings(
        model_name=embed_path, model_kwargs={"device": embedding_device}
    )

    retriever = _build_retriever(
        retriever_name=retriever_name,
        attack_data_path=data_path,
        clean_docs_path=docs_path,
        attack_task=attack_task,
        attack_module=attack_module,
        attack_intensity=attack_intensity,
        embed_model=embed_model,
        embed_dim=embedding_dim,
        filter_module=filter_module,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        collection_name=collection_name,
        retrieve_top_k=retrieve_top_k,
        classes=classes,
    )

    prompt_template = _load_prompt_template()
    attack = _build_attack_task(
        attack_task=attack_task,
        quest_eval_model=quest_eval_model,
        use_quest_eval=use_quest_eval,
        use_bert_score=use_bert_score,
        classes=classes,
    )

    dataset = build_saferag_samples(
        attack_task=attack_task,
        data_path=data_path,
        shuffle=shuffle,
        seed=seed,
        limit=limit,
    )

    return Task(
        dataset=dataset,
        solver=[saferag_generate(retriever, prompt_template)],
        scorer=[saferag_scorer(attack)],
        config=GenerateConfig(
            temperature=temperature,
            max_tokens=max_tokens,
        ),
        version="1.0.0",
    )


@task
def saferag_sn(**kwargs) -> Task:
    return saferag(attack_task="SN", **kwargs)


@task
def saferag_icc(**kwargs) -> Task:
    return saferag(attack_task="ICC", **kwargs)


@task
def saferag_sa(**kwargs) -> Task:
    return saferag(attack_task="SA", **kwargs)


@task
def saferag_wdos(**kwargs) -> Task:
    return saferag(attack_task="WDoS", **kwargs)


__all__ = [
    "saferag",
    "saferag_sn",
    "saferag_icc",
    "saferag_sa",
    "saferag_wdos",
]
