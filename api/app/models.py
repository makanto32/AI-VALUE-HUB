from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import List, Optional
from uuid import uuid4

from pydantic import BaseModel, Field


class IdeaStatus(str, Enum):
    draft = "draft"
    needs_clarification = "needs_clarification"
    business_viable = "business_viable"
    rejected = "rejected"


class DeploymentStatus(str, Enum):
    development = "development"
    funding = "funding"
    production = "production"


class IdeaStage(str, Enum):
    idea_intake = "idea_intake"
    business_validation = "business_validation"
    technical_validation = "technical_validation"


class RejectionPhase(str, Enum):
    business = "business"
    technical = "technical"


class RejectionInfo(BaseModel):
    phase: RejectionPhase
    reason: str = Field(..., min_length=5)


class ClarificationQuestion(BaseModel):
    question_id: str = Field(..., min_length=1)
    prompt: str = Field(..., min_length=8)
    rationale: str = Field(..., min_length=8)
    suggested_answers: List[str] = Field(default_factory=list)


class ClarificationAnswerInput(BaseModel):
    question_id: str = Field(..., min_length=1)
    answer: str = Field(..., min_length=5)


class ClarificationInteraction(BaseModel):
    asked_questions: List[ClarificationQuestion] = Field(default_factory=list)
    answers: List[ClarificationAnswerInput] = Field(default_factory=list)
    agent_summary: str = Field(..., min_length=10)
    decided_status: IdeaStatus
    decided_stage: IdeaStage
    created_at: datetime


class BusinessIntakeRequest(BaseModel):
    tenant_id: str = Field(..., min_length=1)
    title: str = Field(..., min_length=3, max_length=120)
    problem_statement: str = Field(..., min_length=10)
    expected_value: str = Field(..., min_length=5)
    affected_users: List[str] = Field(default_factory=list)
    source_language: str = Field(default="es", min_length=2, max_length=5)


class BusinessValidation(BaseModel):
    value_score: int = Field(ge=0, le=100)
    risk_score: int = Field(ge=0, le=100)
    assumptions: List[str] = Field(default_factory=list)
    open_questions: List[str] = Field(default_factory=list)
    context_signals: List[str] = Field(default_factory=list)
    score_breakdown: List[str] = Field(default_factory=list)
    recommendation: str


class ContextSnapshot(BaseModel):
    tenant_id: str
    company_name: str
    industry: str
    risk_tolerance: str
    strategic_priorities: List[str] = Field(default_factory=list)
    prohibited_domains: List[str] = Field(default_factory=list)
    regulatory_constraints: List[str] = Field(default_factory=list)
    evaluated_at: datetime


class TechnicalValidationRequest(BaseModel):
    systems_in_scope: List[str] = Field(default_factory=list)
    data_sources: List[str] = Field(default_factory=list)
    integration_constraints: List[str] = Field(default_factory=list)
    security_requirements: List[str] = Field(default_factory=list)
    timeline_weeks: int = Field(default=8, ge=1, le=52)
    notes: str = ""


class TechnicalValidation(BaseModel):
    feasibility_score: int = Field(ge=0, le=100)
    integration_complexity: int = Field(ge=0, le=100)
    security_risk: int = Field(ge=0, le=100)
    data_readiness: int = Field(ge=0, le=100)
    recommendation: str
    blockers: List[str] = Field(default_factory=list)
    assumptions: List[str] = Field(default_factory=list)


class TechnicalQuestion(BaseModel):
    question_id: str = Field(..., min_length=1)
    prompt: str = Field(..., min_length=8)
    rationale: str = Field(..., min_length=8)
    suggested_answers: List[str] = Field(default_factory=list)


class TechnicalInteraction(BaseModel):
    asked_questions: List[TechnicalQuestion] = Field(default_factory=list)
    answers: List[ClarificationAnswerInput] = Field(default_factory=list)
    agent_summary: str = Field(..., min_length=10)
    technical_validation: TechnicalValidation
    created_at: datetime


class ArchitectureComponent(BaseModel):
    name: str = Field(..., min_length=2)
    purpose: str = Field(..., min_length=5)


class ArchitectureConsumptionEstimate(BaseModel):
    monthly_executions: int = Field(..., ge=1)
    prompt_tokens_per_execution: int = Field(..., ge=1)
    completion_tokens_per_execution: int = Field(..., ge=1)
    monthly_prompt_tokens: int = Field(..., ge=1)
    monthly_completion_tokens: int = Field(..., ge=1)
    estimated_monthly_cost_usd: float = Field(..., ge=0)
    assumptions: List[str] = Field(default_factory=list)


class ArchitecturePackage(BaseModel):
    solution_name: str = Field(..., min_length=5)
    summary: str = Field(..., min_length=20)
    components: List[ArchitectureComponent] = Field(default_factory=list)
    suggested_component_catalog: List[ArchitectureComponent] = Field(default_factory=list)
    monthly_production_consumption: ArchitectureConsumptionEstimate | None = None
    integration_points: List[str] = Field(default_factory=list)
    deployment_steps: List[str] = Field(default_factory=list)
    risks: List[str] = Field(default_factory=list)
    generated_at: datetime


class ResponseComposition(BaseModel):
    language: str = Field(default="es", min_length=2, max_length=5)
    message: str = Field(..., min_length=20)
    next_actions: List[str] = Field(default_factory=list)
    generated_at: datetime


class CompanyContext(BaseModel):
    tenant_id: str = Field(..., min_length=1)
    company_name: str = Field(..., min_length=2, max_length=120)
    industry: str = Field(..., min_length=2, max_length=120)
    strategic_priorities: List[str] = Field(default_factory=list)
    prohibited_domains: List[str] = Field(default_factory=list)
    regulatory_constraints: List[str] = Field(default_factory=list)
    operating_model_summary: str = Field(..., min_length=10)
    risk_tolerance: str = Field(default="medium", min_length=3, max_length=20)
    created_at: datetime
    updated_at: datetime


class UpsertCompanyContextRequest(BaseModel):
    company_name: str = Field(..., min_length=2, max_length=120)
    industry: str = Field(..., min_length=2, max_length=120)
    strategic_priorities: List[str] = Field(default_factory=list)
    prohibited_domains: List[str] = Field(default_factory=list)
    regulatory_constraints: List[str] = Field(default_factory=list)
    operating_model_summary: str = Field(..., min_length=10)
    risk_tolerance: str = Field(default="medium", min_length=3, max_length=20)


class IdeaCase(BaseModel):
    idea_id: str
    tenant_id: str
    owner_user_id: str
    owner_display_name: str
    title: str
    canonical_language: str
    supported_languages: List[str] = Field(default_factory=list)
    source_language: str
    detected_language: str
    response_language: str
    original_text: str
    canonical_summary: str
    current_stage: IdeaStage
    status: IdeaStatus
    problem_statement: str
    expected_value: str
    affected_users: List[str] = Field(default_factory=list)
    context_snapshot: Optional[ContextSnapshot] = None
    business_validation: BusinessValidation
    technical_questions: List[TechnicalQuestion] = Field(default_factory=list)
    technical_interactions: List[TechnicalInteraction] = Field(default_factory=list)
    technical_validation: Optional[TechnicalValidation] = None
    architecture_package: Optional[ArchitecturePackage] = None
    response_composition: Optional[ResponseComposition] = None
    rejection: Optional[RejectionInfo] = None
    deployment_status: DeploymentStatus = Field(default=DeploymentStatus.development)
    monthly_token_quota_base: int = Field(default=250000, ge=1000)
    extra_quota_current_month: int = Field(default=0, ge=0)
    quota_month: str = Field(default="")
    quota_adjustments: List[QuotaAdjustment] = Field(default_factory=list)
    clarification_questions: List[ClarificationQuestion] = Field(default_factory=list)
    clarification_interactions: List[ClarificationInteraction] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime


class SubmitBusinessValidationRequest(BaseModel):
    idea_id: str
    approve: bool
    notes: str = ""


class TechnicalValidationResponse(BaseModel):
    idea_id: str
    technical_validation: TechnicalValidation
    status: IdeaStatus
    current_stage: IdeaStage
    rejection: Optional[RejectionInfo] = None


class TechnicalQuestionsResponse(BaseModel):
    idea_id: str
    questions: List[TechnicalQuestion] = Field(default_factory=list)


class TechnicalChatSubmitRequest(BaseModel):
    answers: List[ClarificationAnswerInput] = Field(default_factory=list, min_length=1)


class ArchitecturePackageResponse(BaseModel):
    idea_id: str
    architecture_package: ArchitecturePackage
    response_composition: ResponseComposition


class DeploymentStatusUpdateRequest(BaseModel):
    deployment_status: DeploymentStatus

class QuotaAdjustment(BaseModel):
    adjustment_type: str = Field(..., min_length=3, max_length=30)
    delta_tokens: int = Field(..., ge=1)
    reason: str = Field(default="", max_length=240)
    adjusted_by_user_id: str = Field(..., min_length=1)
    adjusted_by_display_name: str = Field(..., min_length=1)
    adjusted_at: datetime

class TokenQuotaUpdateRequest(BaseModel):
    monthly_token_quota_base: int = Field(..., ge=1000, le=50000000)

class TokenQuotaExtraRequest(BaseModel):
    extra_tokens: int = Field(..., ge=1, le=50000000)
    reason: str = Field(default="", max_length=240)


class MessageResponse(BaseModel):
    message: str


class ClarificationQuestionsResponse(BaseModel):
    idea_id: str
    questions: List[ClarificationQuestion] = Field(default_factory=list)


class ClarificationSubmitRequest(BaseModel):
    answers: List[ClarificationAnswerInput] = Field(default_factory=list, min_length=1)


class LoginRequest(BaseModel):
    username: str = Field(..., min_length=3)
    password: str = Field(..., min_length=4)


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    display_name: str
    tenant_id: str
    role: str


class UserProfile(BaseModel):
    user_id: str
    username: str
    display_name: str
    tenant_id: str
    role: str


class ContextFileUploadResponse(BaseModel):
    filename: str
    content_type: str
    blob_path: str
    blob_url: str


def new_idea_id() -> str:
    return str(uuid4())
