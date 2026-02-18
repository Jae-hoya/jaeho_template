from langgraph.graph import END, START, StateGraph

from app.flows.copy_lite_generation.nodes import (
    BuildRequestNode,
    BuildResponseNode,
    CollectLandingContextNode,
    GenerateCopyNode,
    InferChannelNode,
    InferLanguageNode,
    InferObjectiveNode,
    ParsePromptNode,
)
from app.flows.copy_lite_generation.states import (
    BuildLandingContextFn,
    CopyLiteGraphState,
    GenerateCopyFn,
    InferChannelFn,
    InferLanguageFn,
    InferObjectiveFn,
    ParsePromptFn,
)
from app.schemas.copy import CopyLiteRequest, CopyLiteResponse


class CopyLiteGenerationGraph:
    def __init__(
        self,
        parse_prompt: ParsePromptFn,
        build_landing_context: BuildLandingContextFn,
        infer_objective_from_prompt: InferObjectiveFn,
        infer_channel_from_prompt: InferChannelFn,
        infer_language_from_prompt: InferLanguageFn,
        generate_copy: GenerateCopyFn,
    ) -> None:
        builder = StateGraph(CopyLiteGraphState)
        builder.add_node("parse_prompt", ParsePromptNode(parse_prompt))
        builder.add_node("landing_context", CollectLandingContextNode(build_landing_context))
        builder.add_node("infer_objective", InferObjectiveNode(infer_objective_from_prompt))
        builder.add_node("infer_channel", InferChannelNode(infer_channel_from_prompt))
        builder.add_node("infer_language", InferLanguageNode(infer_language_from_prompt))
        builder.add_node("build_request", BuildRequestNode(parse_prompt))
        builder.add_node("generate_copy", GenerateCopyNode(generate_copy))
        builder.add_node("build_response", BuildResponseNode())

        builder.add_edge(START, "parse_prompt")
        builder.add_edge("parse_prompt", "landing_context")
        builder.add_edge("landing_context", "infer_objective")
        builder.add_edge("infer_objective", "infer_channel")
        builder.add_edge("infer_channel", "infer_language")
        builder.add_edge("infer_language", "build_request")
        builder.add_edge("build_request", "generate_copy")
        builder.add_edge("generate_copy", "build_response")
        builder.add_edge("build_response", END)

        self._graph = builder.compile()

    async def run(self, payload: CopyLiteRequest) -> CopyLiteResponse:
        state = await self._graph.ainvoke(
            {
                "payload": payload,
                "parsed": None,
                "assumptions": [],
                "extra_context_blocks": [],
                "extra_sources": [],
                "landing_source_exists": False,
                "objective": None,
                "channel": None,
                "language": payload.language,
                "request": None,
                "result": None,
                "assistant_message": "",
                "response": None,
            }
        )
        response = state.get("response")
        if response is None:
            raise RuntimeError("Copy-lite graph failed to produce a response")
        return response
