from typing import TypedDict

from langgraph.graph import StateGraph, START, END

from app.services.llm_service import generate_answer as call_llm


class AgentState(TypedDict):
    question: str
    evidence: list[dict]
    answer: str
    sufficient_evidence: bool


def analyze_question(state: AgentState):
    return state


def evaluate_evidence(state: AgentState):
    evidence = state["evidence"]

    sufficient = len(evidence) > 0

    return {
        "sufficient_evidence": sufficient
    }


def generate_answer(state: AgentState):
    answer = call_llm(
        state["question"],
        state["evidence"],
    )

    return {
        "answer": answer
    }


def insufficient_evidence(state: AgentState):
    return {
        "answer": (
            "I cannot provide a grounded answer because "
            "the available knowledge base does not contain "
            "sufficient evidence for this question."
        )
    }


def route_after_evaluation(state: AgentState):
    if state["sufficient_evidence"]:
        return "generate_answer"

    return "insufficient_evidence"


def build_agent():

    graph = StateGraph(AgentState)

    graph.add_node(
        "analyze_question",
        analyze_question,
    )

    graph.add_node(
        "evaluate_evidence",
        evaluate_evidence,
    )

    graph.add_node(
        "generate_answer",
        generate_answer,
    )

    graph.add_node(
        "insufficient_evidence",
        insufficient_evidence,
    )

    graph.add_edge(
        START,
        "analyze_question",
    )

    graph.add_edge(
        "analyze_question",
        "evaluate_evidence",
    )

    graph.add_conditional_edges(
        "evaluate_evidence",
        route_after_evaluation,
        {
            "generate_answer": "generate_answer",
            "insufficient_evidence": "insufficient_evidence",
        },
    )

    graph.add_edge(
        "generate_answer",
        END,
    )

    graph.add_edge(
        "insufficient_evidence",
        END,
    )

    return graph.compile()


agent = build_agent()