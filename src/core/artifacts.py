"""ORCHESTRATOR standard artifacts and templates."""

from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field

from .portfolio import ChannelPerformance, MarginalEfficiencyResult


class ArtifactType(str, Enum):
    """Standard ORCHESTRATOR artifact types."""
    DECISION_MEMO = "decision_memo"
    EXPERIMENT_BRIEF = "experiment_brief"
    PORTFOLIO_REVIEW = "portfolio_review"
    COMPETITIVE_THREAT_MAP = "competitive_threat_map"
    TRACKING_HEALTH_REPORT = "tracking_health_report"
    CREATIVE_TEST_MATRIX = "creative_test_matrix"


class DecisionMemo(BaseModel):
    """ORCHESTRATOR Decision Memo (1-page format)."""

    # Header
    memo_id: str
    title: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    decision_maker: str = Field("ORCHESTRATOR", description="Agent making the decision")
    stakeholders: List[str] = Field(default_factory=list)

    # Context
    context: str = Field(..., description="Business context and problem statement")
    objective: str = Field(..., description="What we're trying to achieve")
    constraints: List[str] = Field(default_factory=list, description="Budget, creative, time constraints")

    # Options considered
    options_considered: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="List of options with pros/cons"
    )

    # Competitive intel (if required)
    competitive_intel_summary: Optional[str] = None
    competitive_intel_source: Optional[str] = None
    competitive_intel_date: Optional[datetime] = None

    # Marginal efficiency analysis
    marginal_efficiency_table: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Channel-by-channel marginal efficiency"
    )
    efficiency_calculation_method: str = Field(
        "historical_performance",
        description="historical, experiment, proxy, assumption"
    )

    # Decision
    decision: str = Field(..., description="The chosen course of action")
    decision_rationale: str = Field(..., description="Why this option was chosen")

    # Expected impact
    expected_impact: Dict[str, Any] = Field(
        default_factory=dict,
        description="Expected outcomes and metrics"
    )
    confidence_level: int = Field(7, ge=1, le=10, description="Confidence in decision (1-10)")

    # Monitoring plan
    monitoring_plan: Dict[str, Any] = Field(
        default_factory=dict,
        description="How we'll monitor results"
    )
    success_metrics: List[str] = Field(default_factory=list)
    guardrail_metrics: List[str] = Field(default_factory=list)

    # Rollback triggers
    rollback_triggers: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Conditions that trigger rollback"
    )
    rollback_plan: Optional[str] = None

    # Assumptions
    assumptions: List[Dict[str, str]] = Field(
        default_factory=list,
        description="Key assumptions with confidence"
    )
    risks: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Identified risks and mitigations"
    )

    # Execution
    execution_owner: Optional[str] = None
    execution_timeline: Optional[str] = None
    dependencies: List[str] = Field(default_factory=list)

    # Learning objectives
    learning_questions: List[str] = Field(
        default_factory=list,
        description="What we hope to learn"
    )


class ExperimentBrief(BaseModel):
    """ORCHESTRATOR Experiment Brief."""

    # Identification
    experiment_id: str
    title: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    owner: str

    # Hypothesis
    hypothesis: str = Field(..., description="Clear if-then statement")
    rationale: str = Field(..., description="Why we believe this hypothesis")
    learning_objective: str = Field(..., description="What we want to learn")

    # Design
    control_description: str
    variant_description: str
    test_design: str = Field("a_b_test", description="a_b_test, multivariate, sequential")

    # Targeting
    target_audience: str
    audience_size_estimate: Optional[int] = None
    geographic_targeting: Optional[str] = None
    exclusion_criteria: Optional[str] = None

    # Metrics
    primary_metric: str
    primary_metric_definition: str
    guardrail_metrics: List[str] = Field(default_factory=list)
    secondary_metrics: List[str] = Field(default_factory=list)

    # Success criteria
    success_threshold: Optional[float] = None
    neutral_threshold: Optional[float] = None
    failure_threshold: Optional[float] = None

    # Statistical design
    minimum_sample_size: Optional[int] = None
    minimum_duration_days: int = Field(7, ge=1)
    statistical_power: Optional[float] = Field(0.8, ge=0, le=1)
    significance_level: Optional[float] = Field(0.05, ge=0, le=1)

    # Stop rules
    early_stop_rules: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Rules for stopping experiment early"
    )
    max_duration_days: int = Field(30, ge=1)

    # Data requirements
    data_requirements: List[str] = Field(default_factory=list)
    tracking_requirements: List[str] = Field(default_factory=list)
    analytics_requirements: List[str] = Field(default_factory=list)

    # Execution
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    implementation_owner: Optional[str] = None
    analysis_owner: Optional[str] = None

    # Budget impact
    incremental_spend: Optional[float] = None
    opportunity_cost: Optional[float] = None

    # Risk assessment
    risks: List[Dict[str, Any]] = Field(default_factory=list)
    risk_mitigations: List[Dict[str, Any]] = Field(default_factory=list)

    # Communication plan
    stakeholders: List[str] = Field(default_factory=list)
    update_frequency: str = Field("weekly", description="daily, weekly, milestone")


class PortfolioReview(BaseModel):
    """ORCHESTRATOR Weekly Portfolio Review."""

    # Identification
    review_id: str
    review_period_start: datetime
    review_period_end: datetime
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Portfolio summary
    total_spend: float
    total_incremental_conversions: Optional[int] = None
    total_incremental_revenue: Optional[float] = None
    portfolio_iROAS: Optional[float] = None
    portfolio_marginal_cpa: Optional[float] = None

    # Channel performance
    channel_performance: Dict[str, Dict[str, Any]] = Field(
        default_factory=dict,
        description="Channel-by-channel performance"
    )

    # Marginal efficiency signals
    marginal_efficiency_signals: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Recent marginal efficiency changes"
    )

    # Scaling winners / cutting losers
    scaling_recommendations: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Channels to scale with rationale"
    )
    reduction_recommendations: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Channels to reduce with rationale"
    )

    # Next week's plan
    next_week_budget_plan: Dict[str, float] = Field(
        default_factory=dict,
        description="Planned budget by channel"
    )
    budget_changes: Dict[str, Dict[str, float]] = Field(
        default_factory=dict,
        description="Budget changes vs. previous week"
    )

    # Measurement status
    measurement_status: Dict[str, Any] = Field(
        default_factory=dict,
        description="Tracking health and data quality"
    )
    measurement_issues: List[str] = Field(default_factory=list)

    # Creative pipeline
    creative_pipeline_status: Dict[str, Any] = Field(
        default_factory=dict,
        description="Creative production and testing status"
    )
    creative_bottlenecks: List[str] = Field(default_factory=list)

    # Experiment status
    active_experiments: List[Dict[str, Any]] = Field(default_factory=list)
    completed_experiments: List[Dict[str, Any]] = Field(default_factory=list)
    experiment_learnings: List[str] = Field(default_factory=list)

    # Competitive insights
    competitive_insights: Optional[str] = None
    competitive_threats: List[str] = Field(default_factory=list)
    competitive_opportunities: List[str] = Field(default_factory=list)

    # Key decisions made
    key_decisions: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Decisions made during review period"
    )

    # Next actions
    next_actions: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Action items with owners and deadlines"
    )

    # Risks and blockers
    risks: List[Dict[str, Any]] = Field(default_factory=list)
    blockers: List[Dict[str, Any]] = Field(default_factory=list)

    # Learning and insights
    key_learnings: List[str] = Field(default_factory=list)
    playbook_updates: List[str] = Field(default_factory=list, description="Updates to team playbook")


class CompetitiveThreatMap(BaseModel):
    """COMPETITIVE_INTEL agent output."""

    # Identification
    threat_map_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    analyst: str = Field("COMPETITIVE_INTEL")
    scope: str = Field(..., description="Geographic, vertical, or channel scope")

    # Competitor set
    competitors: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="List of competitors with rationale for inclusion"
    )

    # Messaging analysis
    messaging_angles: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Competitor messaging themes"
    )
    proof_points: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Evidence and social proof used"
    )

    # Offer mechanics
    offer_mechanics: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Pricing, discounts, guarantees"
    )
    pricing_strategies: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Price points and structures"
    )

    # Creative patterns
    creative_formats: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Ad formats and creative approaches"
    )
    visual_patterns: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Visual and design patterns"
    )
    copy_patterns: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Copywriting patterns and hooks"
    )

    # Auction dynamics (for search/shopping)
    serp_analysis: Optional[Dict[str, Any]] = None
    auction_pressure_indicators: Optional[Dict[str, Any]] = None
    keyword_competition: Optional[Dict[str, Any]] = None

    # Differentiation opportunities
    gaps_in_market: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Market gaps and unmet needs"
    )
    competitive_weaknesses: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Competitor weaknesses to exploit"
    )
    differentiation_opportunities: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Areas for differentiation"
    )

    # Threats
    competitive_threats: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Competitive threats to address"
    )
    market_trends: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Emerging market trends"
    )

    # Implications
    channel_implications: Dict[str, List[str]] = Field(
        default_factory=dict,
        description="Implications for each channel"
    )
    creative_testing_implications: List[str] = Field(
        default_factory=list,
        description="Ideas for creative tests"
    )
    messaging_implications: List[str] = Field(
        default_factory=list,
        description="Messaging recommendations"
    )

    # Confidence and limitations
    confidence_level: int = Field(7, ge=1, le=10)
    data_limitations: List[str] = Field(default_factory=list)
    assumptions: List[Dict[str, str]] = Field(default_factory=list)