"""Portfolio models for ORCHESTRATOR decision framework."""

from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field


class ChannelType(str, Enum):
    """Advertising channel types."""
    SEARCH = "search"
    PMAX = "pmax"
    PAID_SOCIAL = "paid_social"
    PROGRAMMATIC = "programmatic"
    DISPLAY = "display"
    VIDEO = "video"
    SHOPPING = "shopping"


class MeasurementMaturity(str, Enum):
    """Measurement maturity levels."""
    BASIC = "basic"  # Pixel only, last-click attribution
    INTERMEDIATE = "intermediate"  # CAPI + basic offline conversions
    ADVANCED = "advanced"  ​# MTA/MMM, lift tests, incrementality measurement
    EXPERT = "expert"  # Full incrementality framework, experiment platform


class ChannelPerformance(BaseModel):
    """Performance data for a single channel."""
    channel_id: str
    channel_type: ChannelType
    current_spend_daily: float = Field(..., description="Daily spend in currency")
    current_spend_monthly: float = Field(..., description="Monthly spend in currency")

    # Performance metrics
    attributed_conversions: Optional[int] = None
    attributed_revenue: Optional[float] = None
    attributed_roas: Optional[float] = Field(None, description="Attributed ROAS (vanilla)")

    # Incremental metrics (preferred)
    incremental_conversions: Optional[int] = None
    incremental_revenue: Optional[float] = None
    incremental_roas: Optional[float] = Field(None, description="Incremental ROAS")

    # Efficiency metrics
    marginal_cpa: Optional[float] = Field(None, description="Marginal CPA at current spend level")
    marginal_roas: Optional[float] = Field(None, description="Marginal iROAS at current spend level")

    # Confidence scores (1-10)
    measurement_confidence: int = Field(5, ge=1, le=10, description="Confidence in measurement accuracy")
    incrementality_confidence: int = Field(3, ge=1, le=10, description="Confidence in incrementality estimates")
    scaling_confidence: int = Field(5, ge=1, le=10, description="Confidence in ability to scale")

    # Constraints
    constraints: List[str] = Field(default_factory=list, description="e.g., ['creative', 'tracking', 'budget', 'audience']")

    # Diminishing returns indicators
    recent_efficiency_trend: str = Field("stable", description="trend: improving, stable, declining")
    spend_velocity: float = Field(0.0, description="% change in spend over last 7 days")

    # Metadata
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    data_source: str = Field("platform_api", description="Source of performance data")


class UnitEconomics(BaseModel):
    """Unit economics guardrails."""
    gross_margin: float = Field(..., ge=0, le=1, description="Gross margin percentage (0-1)")
    customer_lifetime_value: float = Field(..., ge=0, description="LTV in currency")
    target_cac: float = Field(..., ge=0, description="Target customer acquisition cost")
    payback_window_days: int = Field(30, ge=1, description="Maximum allowed payback period")
    minimum_roas: float = Field(1.0, ge=0, description="Minimum ROAS for breakeven")


class CapacityConstraints(BaseModel):
    """Operational capacity constraints."""
    creative_throughput: int = Field(..., description="Number of new creatives per week")
    dev_bandwidth_hours: int = Field(..., description="Development hours available per week")
    analytics_bandwidth_hours: int = Field(..., description="Analytics hours available per week")
    max_active_experiments: int = Field(3, description="Maximum concurrent experiments")
    qa_capacity: int = Field(5, description="Number of QA checks per week")


class Portfolio(BaseModel):
    """Advertising investment portfolio for ORCHESTRATOR decision-making."""

    # Portfolio identity
    portfolio_id: str
    name: str
    description: Optional[str] = None

    # Channels in portfolio
    channels: Dict[str, ChannelPerformance] = Field(default_factory=dict)

    # Budget constraints
    total_budget_daily: float = Field(..., ge=0, description="Total daily budget across all channels")
    total_budget_monthly: float = Field(..., ge=0, description="Total monthly budget across all channels")

    # Business objectives
    primary_kpi: str = Field("incremental_profit", description="incremental_profit, incremental_conversions, etc.")
    secondary_kpis: List[str] = Field(default_factory=lambda: ["cac", "payback_period"])

    # Guardrails
    unit_economics: UnitEconomics
    capacity_constraints: CapacityConstraints

    # Measurement context
    measurement_maturity: MeasurementMaturity = MeasurementMaturity.BASIC
    has_lift_test_capability: bool = False
    offline_conversion_tracking: bool = False

    # Competitive context
    competitive_intel_available: bool = False
    competitive_intel_last_updated: Optional[datetime] = None

    # Risk tolerance
    risk_tolerance: str = Field("moderate", description="conservative, moderate, aggressive")
    max_single_channel_allocation: float = Field(0.5, ge=0, le=1, description="Max % of total budget to single channel")

    # Temporal context
    seasonality_factor: float = Field(1.0, description="Multiplier for seasonal effects")
    planning_horizon_days: int = Field(30, description="Decision horizon in days")

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    assumptions: Dict[str, str] = Field(default_factory=dict, description="Key assumptions")


class MarginalEfficiencyResult(BaseModel):
    """Result of marginal efficiency calculation."""
    channel_id: str
    current_spend: float
    proposed_increment: float
    proposed_spend: float

    # Incremental estimates
    estimated_incremental_conversions: Optional[float] = None
    estimated_incremental_revenue: Optional[float] = None
    estimated_incremental_profit: Optional[float] = None

    # Efficiency metrics
    marginal_cpa: Optional[float] = None
    marginal_roas: Optional[float] = None
    marginal_profit_per_dollar: Optional[float] = None

    # Confidence
    estimate_confidence: int = Field(5, ge=1, le=10)
    data_source: str = Field("historical_performance", description="historical, experiment, proxy, assumption")

    # Risk factors
    reversibility: str = Field("reversible", description="reversible, partially_reversible, irreversible")
    feedback_speed_days: int = Field(7, description="Days to get signal")
    competitive_risk: str = Field("low", description="low, medium, high")


class AllocationRecommendation(BaseModel):
    """Budget allocation recommendation based on marginal efficiency."""
    channel_id: str
    current_allocation: float
    recommended_allocation: float
    allocation_change: float
    allocation_change_percentage: float

    marginal_efficiency: MarginalEfficiencyResult
    rationale: str

    # Monitoring plan
    success_metrics: List[str]
    stop_loss_triggers: List[str]
    review_schedule_days: List[int] = Field(default_factory=lambda: [1, 3, 7])

    # Competitive intel requirement
    competitive_intel_required: bool = False
    competitive_intel_status: str = Field("not_required", description="not_required, pending, completed")

    # Execution plan
    execution_actions: List[str]
    owner: Optional[str] = None
    deadline: Optional[datetime] = None