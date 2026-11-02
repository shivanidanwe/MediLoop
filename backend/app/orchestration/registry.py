"""
MediLoop Multi-Agent Registry.
Central registry defining the six specialized agents, their schemas, versions,
health status, timeouts, retry policies, and dependency hierarchy.
"""
import logging
from typing import Any, Callable, Dict, List, Optional
from sqlalchemy.orm import Session
from app.models.orchestration import AgentRegistryModel
from app.schemas.orchestration import (
    AgentMetadataSchema,
    OCRAgentInput, OCRAgentOutput,
    PrescriptionIntelligenceInput, PrescriptionIntelligenceOutput,
    DrugSafetyInput, DrugSafetyOutput,
    OrderAgentInput, OrderAgentOutput
)

logger = logging.getLogger(__name__)


class AgentRegistration:
    """Metadata and execution pointer for a registered AI agent."""

    def __init__(
        self,
        agent_id: str,
        name: str,
        version: str,
        description: str,
        executor: Optional[Callable] = None,
        input_schema: Any = None,
        output_schema: Any = None,
        timeout_seconds: float = 60.0,
        max_retries: int = 3,
        dependencies: Optional[List[str]] = None,
        is_background: bool = False
    ):
        self.agent_id = agent_id
        self.name = name
        self.version = version
        self.description = description
        self.executor = executor
        self.input_schema = input_schema
        self.output_schema = output_schema
        self.timeout_seconds = timeout_seconds
        self.max_retries = max_retries
        self.dependencies = dependencies or []
        self.is_background = is_background
        self.status = "ACTIVE"


class MultiAgentRegistry:
    """Enterprise Registry managing the six MediLoop healthcare agents."""

    def __init__(self, db: Optional[Session] = None):
        self.db = db
        self._agents: Dict[str, AgentRegistration] = {}
        self._initialize_default_agents()

    def _initialize_default_agents(self) -> None:
        """Initializes the 6 production agents."""
        defaults = [
            AgentRegistration(
                agent_id="ocr_agent",
                name="OCR Agent",
                version="2.0.0",
                description="Extracts raw text and medicine regions from prescription images via Ollama Vision.",
                input_schema=OCRAgentInput,
                output_schema=OCRAgentOutput,
                timeout_seconds=90.0,
                max_retries=3,
                dependencies=[]
            ),
            AgentRegistration(
                agent_id="prescription_intelligence_agent",
                name="Prescription Intelligence Agent",
                version="2.0.0",
                description="Extracts structured medicines via Ollama JSON mode NER and matches to database catalogue.",
                input_schema=PrescriptionIntelligenceInput,
                output_schema=PrescriptionIntelligenceOutput,
                timeout_seconds=60.0,
                max_retries=2,
                dependencies=["ocr_agent"]
            ),
            AgentRegistration(
                agent_id="drug_safety_agent",
                name="Drug Safety Agent",
                version="2.0.0",
                description="Performs clinical screening for allergies, medication history, interactions, and contraindications.",
                input_schema=DrugSafetyInput,
                output_schema=DrugSafetyOutput,
                timeout_seconds=30.0,
                max_retries=2,
                dependencies=["prescription_intelligence_agent"]
            ),
            AgentRegistration(
                agent_id="order_agent",
                name="Order Agent",
                version="2.0.0",
                description="Prepares cart and draft READY_TO_PLACE order based on available stock and pricing.",
                input_schema=OrderAgentInput,
                output_schema=OrderAgentOutput,
                timeout_seconds=30.0,
                max_retries=2,
                dependencies=["drug_safety_agent"]
            ),
            AgentRegistration(
                agent_id="refill_reminder_agent",
                name="Refill Reminder Agent",
                version="2.0.0",
                description="Autonomous background worker predicting refill dates and dispatching deduplicated notifications.",
                timeout_seconds=120.0,
                max_retries=1,
                dependencies=[],
                is_background=True
            ),
            AgentRegistration(
                agent_id="procurement_agent",
                name="Procurement Agent",
                version="2.0.0",
                description="Autonomous background worker calculating shortages, drafting purchase orders, and generating PDFs.",
                timeout_seconds=120.0,
                max_retries=1,
                dependencies=[],
                is_background=True
            )
        ]
        for a in defaults:
            self._agents[a.agent_id] = a

    def register(self, agent: AgentRegistration) -> None:
        self._agents[agent.agent_id] = agent
        logger.info(f"[AgentRegistry] Registered agent: {agent.agent_id} (v{agent.version})")

    def get_agent(self, agent_id: str) -> AgentRegistration:
        if agent_id not in self._agents:
            raise KeyError(f"Agent '{agent_id}' is not registered in the orchestrator.")
        return self._agents[agent_id]

    def get_agent_metadata(self, agent_id: str) -> Optional[AgentMetadataSchema]:
        if agent_id not in self._agents:
            return None
        a = self._agents[agent_id]
        return AgentMetadataSchema(
            agent_id=a.agent_id,
            name=a.name,
            version=a.version,
            status=a.status,
            description=a.description,
            timeout_seconds=a.timeout_seconds,
            max_retries=a.max_retries,
            dependencies=a.dependencies
        )

    def list_agents(self) -> List[AgentRegistration]:
        return list(self._agents.values())

    def list_all_agents(self) -> List[AgentMetadataSchema]:
        return [
            AgentMetadataSchema(
                agent_id=a.agent_id,
                name=a.name,
                version=a.version,
                status=a.status,
                description=a.description,
                timeout_seconds=a.timeout_seconds,
                max_retries=a.max_retries,
                dependencies=a.dependencies
            )
            for a in self._agents.values()
        ]

    def sync_to_db(self, db: Optional[Session] = None) -> int:
        """Synchronizes in-memory agent metadata with the PostgreSQL agent_registry table."""
        target_db = db or self.db
        if not target_db:
            return len(self._agents)
        try:
            for agent in self._agents.values():
                record = target_db.query(AgentRegistryModel).filter(
                    AgentRegistryModel.agent_id == agent.agent_id
                ).first()

                if not record:
                    record = AgentRegistryModel(
                        agent_id=agent.agent_id,
                        name=agent.name,
                        version=agent.version,
                        status=agent.status,
                        description=agent.description,
                        timeout_seconds=agent.timeout_seconds,
                        max_retries=agent.max_retries,
                        dependencies_json=agent.dependencies,
                        input_schema_json={"schema": getattr(agent.input_schema, "__name__", str(agent.input_schema))},
                        output_schema_json={"schema": getattr(agent.output_schema, "__name__", str(agent.output_schema))}
                    )
                    target_db.add(record)
                else:
                    record.name = agent.name
                    record.version = agent.version
                    record.status = agent.status
                    record.description = agent.description
                    record.timeout_seconds = agent.timeout_seconds
                    record.max_retries = agent.max_retries
                    record.dependencies_json = agent.dependencies
            target_db.commit()
            logger.info("[AgentRegistry] Synchronized agents with PostgreSQL.")
            return len(self._agents)
        except Exception as e:
            target_db.rollback()
            logger.warning(f"[AgentRegistry] Database sync failed: {e}")
            return len(self._agents)

    def sync_to_database(self, db: Session) -> None:
        self.sync_to_db(db)


agent_registry = MultiAgentRegistry()
