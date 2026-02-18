from app.schemas.copy import CopyGenerateRequest


def build_retrieval_query(request: CopyGenerateRequest) -> str:
    parts = [request.product_name, request.target_audience, request.pain_point]
    return " ".join(part.strip() for part in parts if part and part.strip())


def build_web_search_query(request: CopyGenerateRequest) -> str:
    parts = [request.product_name, request.channel]
    return " ".join(part.strip() for part in parts if part and part.strip())


def merge_context_blocks(existing_blocks: list[str], new_block: str | None) -> list[str]:
    merged = list(existing_blocks)
    if new_block and new_block.strip():
        merged.append(new_block)
    return merged
