import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime
from app.schemas.case import InvestigationCase
from app.schemas.task import InvestigationTask
from app.schemas.case_revision import CaseRevision

class InvestigationPlanner:
    """
    Domain-Specific Cyber Investigation Planner.
    Decomposes cybercrime cases into prioritized, dependency-linked investigation tasks,
    tracks task execution progress, and manages goal/hypothesis revisions when new evidence arrives.
    """

    def create_initial_plan(self, case: InvestigationCase, description: str, context: Optional[Dict[str, Any]] = None) -> List[InvestigationTask]:
        tasks = []

        # 1. Understanding Task (No dependencies)
        task_understand = InvestigationTask(
            case_id=case.case_id,
            agent_type="UnderstandingAgent",
            objective=f"Analyze initial report: '{description[:100]}...' and extract incident parameters.",
            priority=1,
            dependencies=[],
            required_tools=["nlp_extractor", "incident_classifier"]
        )
        tasks.append(task_understand)

        # 2. Evidence Processing Task (Depends on Understanding)
        task_evidence = InvestigationTask(
            case_id=case.case_id,
            agent_type="EvidenceAgent",
            objective="Extract entities (UPIs, phone numbers, URLs, wallets) and perform OCR on attached evidence.",
            priority=2,
            dependencies=[task_understand.task_id],
            required_tools=["vision_ocr_engine", "entity_regex_extractor"]
        )
        tasks.append(task_evidence)

        # 3. Threat Intel & Longitudinal Search Task (Depends on Evidence)
        task_intel = InvestigationTask(
            case_id=case.case_id,
            agent_type="ThreatIntelAgent",
            objective="Query longitudinal threat memory and external OSINT feeds for matched repeat threat actors.",
            priority=2,
            dependencies=[task_evidence.task_id],
            required_tools=["memory_service_check", "duckduckgo_osint_search"]
        )
        tasks.append(task_intel)

        # 4. Resolution Strategy Task (Depends on Evidence & Intel)
        task_strategy = InvestigationTask(
            case_id=case.case_id,
            agent_type="StrategyAgent",
            objective="Formulate multi-phase containment, securing, and recovery lifecycle plan.",
            priority=3,
            dependencies=[task_evidence.task_id, task_intel.task_id],
            required_tools=["lifecycle_strategy_builder"]
        )
        tasks.append(task_strategy)

        # 5. Recovery Guidance Task (Depends on Strategy)
        task_recovery = InvestigationTask(
            case_id=case.case_id,
            agent_type="RecoveryAgent",
            objective="Generate step-by-step emergency action guide for victim containment.",
            priority=4,
            dependencies=[task_strategy.task_id],
            required_tools=["recovery_guide_builder"]
        )
        tasks.append(task_recovery)

        # 6. Authority Mapping Task (Depends on Strategy)
        task_authority = InvestigationTask(
            case_id=case.case_id,
            agent_type="AuthorityMapperAgent",
            objective="Map relevant law enforcement cyber cells, bank fraud departments, and regulatory portals.",
            priority=4,
            dependencies=[task_strategy.task_id],
            required_tools=["authority_jurisdiction_mapper"]
        )
        tasks.append(task_authority)

        # 7. Prevention Task (Depends on Strategy)
        task_prevention = InvestigationTask(
            case_id=case.case_id,
            agent_type="PreventionAgent",
            objective="Synthesize actionable security tips to prevent future recurring incidents.",
            priority=5,
            dependencies=[task_strategy.task_id],
            required_tools=["prevention_insights_generator"]
        )
        tasks.append(task_prevention)

        return tasks

    def revise_investigation_goal(
        self,
        case: InvestigationCase,
        new_evidence_desc: str,
        reason: str,
        new_hypothesis: Optional[str] = None
    ) -> CaseRevision:
        """
        Executes goal revision when new contradictory or higher-priority evidence arrives,
        creating an audit record and updating the active case objective.
        """
        previous_goal = case.investigation_goal
        new_goal = f"Revised Goal: Investigate '{new_evidence_desc}' and mitigate newly identified risk factors."
        
        previous_hypo = case.active_hypotheses[0] if case.active_hypotheses else "Initial Fraud Hypothesis"
        
        revision = CaseRevision(
            case_id=case.case_id,
            previous_goal=previous_goal,
            new_goal=new_goal,
            previous_hypothesis=previous_hypo,
            new_hypothesis=new_hypothesis or f"Hypothesis updated based on {reason}",
            triggering_evidence=[new_evidence_desc],
            reason=reason,
            affected_agents=["UnderstandingAgent", "StrategyAgent", "ThreatIntelAgent"],
            affected_tasks=[]
        )

        case.investigation_goal = new_goal
        if new_hypothesis:
            case.active_hypotheses.insert(0, new_hypothesis)
        case.updated_at = datetime.utcnow()
        
        return revision

planner = InvestigationPlanner()
