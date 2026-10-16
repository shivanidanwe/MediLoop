"""
MediLoop AI Health Companion Agent.
Conversational AI interface that classifies user intent, orchestrates specialized downstream agents
via the AgentOrchestrator, tracks conversational session history, and formats healthcare responses.
"""
from datetime import datetime
import re
from typing import Any, Dict, List, Tuple
from app.agents.base_agent import BaseAgent
from app.agents.context import AgentContext
from app.agents.events import AgentEvent
from app.agents.exceptions import AgentValidationError
from app.core.ollama_client import ollama_client


DISCLAIMER_TEXT = (
    "Disclaimer: This information is provided by MediLoop AI for educational and convenience purposes. "
    "Always consult your prescribing doctor or a licensed pharmacist for personalized clinical guidance."
)


class AIHealthCompanionAgent(BaseAgent):
    """
    Conversational agent acting as the primary natural language interface to MediLoop.
    Detects user intent and communicates with downstream specialized agents via the orchestrator.
    """

    @property
    def name(self) -> str:
        return "health_companion_agent"

    @property
    def description(self) -> str:
        return (
            "Conversational interface agent that detects user intent, orchestrates downstream "
            "AI agents through the orchestrator, tracks session conversation history, and formats healthcare responses."
        )

    @property
    def handled_events(self) -> List[AgentEvent]:
        return [
            AgentEvent.AI_CHAT_REQUEST,
            AgentEvent.AI_QUERY,
            AgentEvent.ORDER_RECOMMENDED,
            AgentEvent.REFILL_REMINDER,
            AgentEvent.SAFETY_VALIDATION_COMPLETED,
            AgentEvent.INVENTORY_CHECKED,
            AgentEvent.ORDER_CREATED,
            AgentEvent.ORDER_CONFIRMED,
            AgentEvent.MEDICINES_MATCHED,
            AgentEvent.MEDICINES_EXTRACTED,
            AgentEvent.OCR_COMPLETED,
            AgentEvent.PRESCRIPTION_UPLOADED,
        ]

    async def can_handle(self, event: AgentEvent, context: AgentContext) -> bool:
        """
        Agent handles conversational AI queries or orchestrator event responses.
        """
        return event in self.handled_events

    async def validate(self, context: AgentContext) -> bool:
        """
        Validates presence of prompt message or metadata context.
        """
        user_msg = context.metadata.get("user_message", "")
        if not user_msg and not context.metadata and not context.ocr_text and not context.matched_medicines:
            raise AgentValidationError(
                "AIHealthCompanionAgent validation failed: Prompt message or context metadata is required."
            )
        return True

    async def execute(self, context: AgentContext) -> AgentContext:
        """
        Classifies intent, synthesizes responses, tracks conversation history, and updates context.
        """
        user_msg = context.metadata.get("user_message", "") or "Help me with my prescription"
        intent = self._classify_intent(user_msg, context)

        agents_used, response_text, suggested_actions = await self._generate_response(intent, context, user_msg)

        assistant_response = {
            "intent": intent,
            "user_message": user_msg,
            "response": response_text,
            "agents_used": agents_used,
            "suggested_actions": suggested_actions,
            "timestamp": datetime.now().isoformat(),
            "disclaimer": DISCLAIMER_TEXT,
        }

        context.metadata["assistant_response"] = assistant_response

        # Update Conversation History Memory
        history = context.metadata.get("conversation_history", [])
        history.append({"role": "user", "content": user_msg, "timestamp": datetime.now().isoformat()})
        history.append({"role": "assistant", "content": response_text, "intent": intent, "timestamp": datetime.now().isoformat()})
        context.metadata["conversation_history"] = history

        context.add_recommendation(f"AI Health Companion Response Generated [{intent}]")

        return context

    def _classify_intent(self, user_msg: str, context: AgentContext) -> str:
        """Classifies natural language prompt into functional intent categories."""
        msg_norm = user_msg.lower()

        # Check specific functional queries first
        if any(kw in msg_norm for kw in ["safe", "interaction", "allergy", "together", "side effect", "dosage safe"]):
            return "SAFETY_QUERY"
        if any(kw in msg_norm for kw in ["stock", "available", "pharmacy", "buy", "have"]):
            return "INVENTORY_QUERY"
        if any(kw in msg_norm for kw in ["order", "checkout", "recommend", "best pharmacy", "cart"]):
            return "ORDER_RECOMMENDATION"
        if any(kw in msg_norm for kw in ["refill", "finish", "reorder", "run out", "schedule"]):
            return "REFILL_QUERY"
        if any(kw in msg_norm for kw in ["prescription", "scan", "rx", "doctor", "analyze", "read"]):
            return "PRESCRIPTION_ASSISTANCE"

        # Contextual Fallback based on metadata
        if "drug_safety" in context.metadata:
            return "SAFETY_QUERY"
        if "order_recommendation" in context.metadata:
            return "ORDER_RECOMMENDATION"
        if "refill_report" in context.metadata:
            return "REFILL_QUERY"

        return "GENERAL_HEALTH_INFO"

    async def _generate_response(
        self, intent: str, context: AgentContext, user_msg: str = ""
    ) -> Tuple[List[str], str, List[str]]:
        """Synthesizes agent outputs into conversational natural language responses."""
        agents_used: List[str] = ["health_companion_agent"]
        suggested_actions: List[str] = []
        response_lines: List[str] = []

        if intent == "PRESCRIPTION_ASSISTANCE":
            agents_used.extend(["ocr_agent", "prescription_intelligence_agent", "medicine_matching_agent"])
            extracted_count = len(context.extracted_medicines)
            matched_count = len(context.matched_medicines)

            response_lines.append(f"I've analyzed your prescription scan!")
            if matched_count > 0:
                response_lines.append(f"Identified {matched_count} verified medicines in our inventory catalog:")
                for m in context.matched_medicines[:4]:
                    response_lines.append(f" • {m.get('name')} ({m.get('generic_name')}) - {m.get('strength', '')}")
            elif extracted_count > 0:
                response_lines.append(f"Extracted {extracted_count} medicine items from your prescription.")
            else:
                response_lines.append("No clear medicine entries were detected. Please upload a clear prescription photo.")
            suggested_actions = ["Review Extracted Medicines", "Proceed to Safety Check"]

        elif intent == "SAFETY_QUERY":
            agents_used.append("drug_safety_agent")
            safety_meta = context.metadata.get("drug_safety", {})
            risk = safety_meta.get("risk_level", "LOW")
            errors = safety_meta.get("errors", [])

            response_lines.append(f"I performed a clinical safety evaluation of your medicines.")
            response_lines.append(f"Overall Risk Assessment: **{risk}**.")
            if errors:
                response_lines.append(f"⚠️ Clinical Safety Alerts Identified:")
                for err in errors:
                    response_lines.append(f" • [{err.get('severity')}] {err.get('description')}")
            else:
                response_lines.append("No critical drug interactions or allergy conflicts were detected.")
            suggested_actions = ["Speak to Pharmacist", "View Safety Details"]

        elif intent == "INVENTORY_QUERY":
            agents_used.append("inventory_availability_agent")
            inv_meta = context.metadata.get("inventory", {})
            pharm_name = inv_meta.get("selected_pharmacy", {}).get("name", "MediLoop Central")
            status = inv_meta.get("overall_status", "AVAILABLE")

            response_lines.append(f"Inventory status at **{pharm_name}**: {status}.")
            unavail = inv_meta.get("unavailable_items", [])
            if unavail:
                response_lines.append(f"Some items are currently out of stock:")
                for u in unavail:
                    response_lines.append(f" • {u.get('name')}: Out of Stock")
            else:
                response_lines.append("All prescribed items are in stock and ready for fulfillment.")
            suggested_actions = ["Switch Pharmacy", "Proceed to Checkout"]

        elif intent == "ORDER_RECOMMENDATION":
            agents_used.extend(["order_recommendation_agent", "inventory_availability_agent"])
            order_rec = context.metadata.get("order_recommendation", {})
            rec_pharm = order_rec.get("recommended_pharmacy", {}).get("name", "MediLoop Pharmacy")
            order_status = order_rec.get("order_status", "READY_FOR_CHECKOUT")

            response_lines.append(f"Here is my recommended order strategy:")
            response_lines.append(f"Best Pharmacy: **{rec_pharm}**")
            response_lines.append(f"Checkout Status: **{order_status}**")
            if order_rec.get("reasoning"):
                response_lines.append("Reasoning:")
                for r in order_rec["reasoning"]:
                    response_lines.append(f" • {r}")
            suggested_actions = ["Proceed to One-Tap Checkout", "View Cart"]

        elif intent == "REFILL_QUERY":
            agents_used.append("refill_reminder_agent")
            refill_meta = context.metadata.get("refill_report", {})
            days_rem = refill_meta.get("days_remaining", 0)
            comp_date = refill_meta.get("expected_completion_date", "N/A")

            response_lines.append(f"Medication Refill Tracking Report:")
            response_lines.append(f"Estimated Supply Completion: **{comp_date}** ({days_rem} days remaining).")
            response_lines.append(f"Adherence Status: **{refill_meta.get('status', 'MONITORING')}**.")
            suggested_actions = ["Auto-Refill Setup", "Reorder Medicines"]

        else:
            system_prompt = (
                "You are the MediLoop AI Clinical Health Companion, an empathetic, highly trained, and professional healthcare assistant. "
                "Provide accurate, safe medical and prescription guidance. "
                "Always advise patients to consult a licensed physician or pharmacist for definitive diagnosis or emergency care."
            )
            chat_messages = []
            for h in (context.metadata.get("conversation_history") or [])[-6:]:
                chat_messages.append({"role": h.get("role", "user"), "content": h.get("content", "")})
            if user_msg and not any(m.get("content") == user_msg for m in chat_messages):
                chat_messages.append({"role": "user", "content": user_msg})

            llm_text = await ollama_client.chat(messages=chat_messages, system_prompt=system_prompt)
            if llm_text and "unable to connect" not in llm_text.lower():
                response_lines.append(llm_text)
            else:
                response_lines.append("Hello! I am your MediLoop AI Health Companion.")
                response_lines.append("How can I assist you with your prescriptions, drug safety, inventory, or refills today?")
            suggested_actions = ["Upload Prescription", "Check Drug Safety", "View Active Refills"]

        response_lines.append(f"\n*{DISCLAIMER_TEXT}*")
        response_text = "\n".join(response_lines)

        return agents_used, response_text, suggested_actions
