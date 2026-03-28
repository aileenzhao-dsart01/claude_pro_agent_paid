"""ORCHESTRATOR specialist agent definitions and specifications."""

from typing import Dict, List, Any
from enum import Enum
from pydantic import BaseModel, Field

from .base import BaseAgent, Task


class SpecialistType(str, Enum):
    """Types of specialist agents in ORCHESTRATOR team model."""
    MEASUREMENT_ANALYST = "measurement_analyst"
    COMPETITIVE_INTEL = "competitive_intel"
    CHANNEL_STRATEGIST_SEARCH = "channel_strategist_search"
    CHANNEL_STRATEGIST_PMAX = "channel_strategist_pmax"
    CHANNEL_STRATEGIST_PAID_SOCIAL = "channel_strategist_paid_social"
    CHANNEL_STRATEGIST_PROGRAMMATIC = "channel_strategist_programmatic"
    CREATIVE_STRATEGIST = "creative_strategist"
    LANDING_PAGE_CRO = "landing_page_cro"
    DATA_ENGINEER = "data_engineer"
    FINANCE_GUARDIAN = "finance_guardian"
    QA_AUDITOR = "qa_auditor"


class SpecialistCapability(str, Enum):
    """Capabilities of specialist agents."""
    # Measurement Analyst
    TRACKING_AUDIT = "tracking_audit"
    ATTRIBUTION_ANALYSIS = "attribution_analysis"
    LIFT_TEST_DESIGN = "lift_test_design"
    MMM_MTA_GOVERNANCE = "mmm_mta_governance"
    DATA_QUALITY_CHECK = "data_quality_check"

    # Competitive Intel
    COMPETITOR_SCAN = "competitor_scan"
    AUCTION_ANALYSIS = "auction_analysis"
    CREATIVE_PATTERNS = "creative_patterns"
    MESSAGING_ANALYSIS = "messaging_analysis"
    SERP_ANALYSIS = "serp_analysis"

    # Channel Strategists
    KEYWORD_OPTIMIZATION = "keyword_optimization"
    BID_MANAGEMENT = "bid_management"
    STRUCTURE_AUDIT = "structure_audit"
    EXPERIMENT_DESIGN = "experiment_design"
    PERFORMANCE_ANALYSIS = "performance_analysis"
    BUDGET_OPTIMIZATION = "budget_optimization"

    # Creative Strategist
    HOOK_IDENTIFICATION = "hook_identification"
    ANGLE_DEVELOPMENT = "angle_development"
    SCRIPT_WRITING = "script_writing"
    ASSET_TEST_MATRIX = "asset_test_matrix"
    CREATIVE_BRIEF = "creative_brief"

    # Landing Page CRO
    UX_AUDIT = "ux_audit"
    CONVERSION_FRICTION = "conversion_friction"
    PAGE_SPEED = "page_speed"
    EXPERIMENTATION = "experimentation"
    PERSONALIZATION = "personalization"

    # Data Engineer
    FEED_MANAGEMENT = "feed_management"
    TAGGING_IMPLEMENTATION = "tagging_implementation"
    SERVER_SIDE = "server_side"
    EVENT_SCHEMAS = "event_schemas"
    DATA_PIPELINE = "data_pipeline"

    # Finance Guardian
    UNIT_ECONOMICS = "unit_economics"
    LTV_CAC = "ltv_cac"
    PAYBACK_WINDOWS = "payback_windows"
    MARGIN_CONSTRAINTS = "margin_constraints"
    ROI_ANALYSIS = "roi_analysis"

    # QA Auditor
    POLICY_COMPLIANCE = "policy_compliance"
    BRAND_SAFETY = "brand_safety"
    ERROR_DETECTION = "error_detection"
    QUALITY_ASSURANCE = "quality_assurance"
    PROCESS_AUDIT = "process_audit"


class SpecialistSpec(BaseModel):
    """Specification for a specialist agent."""
    specialist_type: SpecialistType
    name: str
    description: str
    capabilities: List[SpecialistCapability]
    input_requirements: List[str]
    output_deliverables: List[str]
    typical_task_duration_hours: Dict[str, int] = Field(
        default_factory=lambda: {
            "quick": 2,
            "standard": 8,
            "complex": 24
        }
    )
    dependencies: List[SpecialistType] = Field(default_factory=list)


# ORCHESTRATOR Team Model Specifications
SPECIALIST_SPECS: Dict[SpecialistType, SpecialistSpec] = {
    SpecialistType.MEASUREMENT_ANALYST: SpecialistSpec(
        specialist_type=SpecialistType.MEASUREMENT_ANALYST,
        name="Measurement Analyst",
        description="Ensures tracking integrity, attribution accuracy, and incrementality measurement",
        capabilities=[
            SpecialistCapability.TRACKING_AUDIT,
            SpecialistCapability.ATTRIBUTION_ANALYSIS,
            SpecialistCapability.LIFT_TEST_DESIGN,
            SpecialistCapability.MMM_MTA_GOVERNANCE,
            SpecialistCapability.DATA_QUALITY_CHECK
        ],
        input_requirements=[
            "Current tracking implementation",
            "Conversion data sources",
            "Attribution model configuration"
        ],
        output_deliverables=[
            "Tracking Health Report",
            "Attribution Analysis",
            "Lift Test Design",
            "Measurement Confidence Score"
        ],
        dependencies=[]
    ),

    SpecialistType.COMPETITIVE_INTEL: SpecialistSpec(
        specialist_type=SpecialistType.COMPETITIVE_INTEL,
        name="Competitive Intelligence",
        description="Analyzes competitor spend signals, messaging, offers, and creative patterns",
        capabilities=[
            SpecialistCapability.COMPETITOR_SCAN,
            SpecialistCapability.AUCTION_ANALYSIS,
            SpecialistCapability.CREATIVE_PATTERNS,
            SpecialistCapability.MESSAGING_ANALYSIS,
            SpecialistCapability.SERP_ANALYSIS
        ],
        input_requirements=[
            "Target market/vertical",
            "Competitor names (optional)",
            "Channel focus (search, social, etc.)"
        ],
        output_deliverables=[
            "Competitive Threat Map",
            "SERP Analysis",
            "Creative Pattern Analysis",
            "Differentiation Opportunities"
        ],
        dependencies=[]
    ),

    SpecialistType.CHANNEL_STRATEGIST_SEARCH: SpecialistSpec(
        specialist_type=SpecialistType.CHANNEL_STRATEGIST_SEARCH,
        name="Search Channel Strategist",
        description="Manages Google/Bing search campaigns, keywords, bids, and structure",
        capabilities=[
            SpecialistCapability.KEYWORD_OPTIMIZATION,
            SpecialistCapability.BID_MANAGEMENT,
            SpecialistCapability.STRUCTURE_AUDIT,
            SpecialistCapability.EXPERIMENT_DESIGN,
            SpecialistCapability.PERFORMANCE_ANALYSIS,
            SpecialistCapability.BUDGET_OPTIMIZATION
        ],
        input_requirements=[
            "Campaign performance data",
            "Keyword lists",
            "Conversion data",
            "Budget constraints"
        ],
        output_deliverables=[
            "Keyword Strategy",
            "Bid Recommendations",
            "Structure Audit Report",
            "Experiment Results",
            "Budget Allocation Recommendation"
        ],
        dependencies=[
            SpecialistType.MEASUREMENT_ANALYST,
            SpecialistType.COMPETITIVE_INTEL
        ]
    ),

    SpecialistType.CHANNEL_STRATEGIST_PMAX: SpecialistSpec(
        specialist_type=SpecialistType.CHANNEL_STRATEGIST_PMAX,
        name="PMax Channel Strategist",
        description="Manages Performance Max campaigns, asset groups, and bidding",
        capabilities=[
            SpecialistCapability.PERFORMANCE_ANALYSIS,
            SpecialistCapability.BUDGET_OPTIMIZATION,
            SpecialistCapability.EXPERIMENT_DESIGN,
            SpecialistCapability.STRUCTURE_AUDIT
        ],
        input_requirements=[
            "Asset groups",
            "Performance data",
            "Conversion data",
            "Feed quality"
        ],
        output_deliverables=[
            "Asset Group Recommendations",
            "Bid Strategy",
            "Performance Analysis",
            "Feed Optimization Suggestions"
        ],
        dependencies=[
            SpecialistType.MEASUREMENT_ANALYST,
            SpecialistType.CREATIVE_STRATEGIST
        ]
    ),

    SpecialistType.CHANNEL_STRATEGIST_PAID_SOCIAL: SpecialistSpec(
        specialist_type=SpecialistType.CHANNEL_STRATEGIST_PAID_SOCIAL,
        name="Paid Social Channel Strategist",
        description="Manages Facebook/Instagram/Linkedin/TikTok campaigns",
        capabilities=[
            SpecialistCapability.PERFORMANCE_ANALYSIS,
            SpecialistCapability.BUDGET_OPTIMIZATION,
            SpecialistCapability.EXPERIMENT_DESIGN,
            SpecialistCapability.STRUCTURE_AUDIT
        ],
        input_requirements=[
            "Creative assets",
            "Audience definitions",
            "Performance data",
            "Platform insights"
        ],
        output_deliverables=[
            "Audience Strategy",
            "Creative Testing Plan",
            "Budget Recommendations",
            "Performance Analysis"
        ],
        dependencies=[
            SpecialistType.MEASUREMENT_ANALYST,
            SpecialistType.CREATIVE_STRATEGIST,
            SpecialistType.COMPETITIVE_INTEL
        ]
    ),

    SpecialistType.CREATIVE_STRATEGIST: SpecialistSpec(
        specialist_type=SpecialistType.CREATIVE_STRATEGIST,
        name="Creative Strategist",
        description="Develops hooks, angles, scripts, and asset testing matrices",
        capabilities=[
            SpecialistCapability.HOOK_IDENTIFICATION,
            SpecialistCapability.ANGLE_DEVELOPMENT,
            SpecialistCapability.SCRIPT_WRITING,
            SpecialistCapability.ASSET_TEST_MATRIX,
            SpecialistCapability.CREATIVE_BRIEF
        ],
        input_requirements=[
            "Product/offer details",
            "Target audience",
            "Competitive insights",
            "Brand guidelines"
        ],
        output_deliverables=[
            "Creative Brief",
            "Hook Library",
            "Angle Matrix",
            "Script Templates",
            "Asset Testing Plan"
        ],
        dependencies=[
            SpecialistType.COMPETITIVE_INTEL
        ]
    ),

    SpecialistType.FINANCE_GUARDIAN: SpecialistSpec(
        specialist_type=SpecialistType.FINANCE_GUARDIAN,
        name="Finance Guardian",
        description="Ensures unit economics, LTV/CAC, payback windows, and margin constraints",
        capabilities=[
            SpecialistCapability.UNIT_ECONOMICS,
            SpecialistCapability.LTV_CAC,
            SpecialistCapability.PAYBACK_WINDOWS,
            SpecialistCapability.MARGIN_CONSTRAINTS,
            SpecialistCapability.ROI_ANALYSIS
        ],
        input_requirements=[
            "Cost data",
            "Revenue data",
            "Customer lifetime value",
            "Margin requirements"
        ],
        output_deliverables=[
            "Unit Economics Report",
            "CAC/LTV Analysis",
            "Payback Period Calculation",
            "Margin Guardrails",
            "ROI Projections"
        ],
        dependencies=[]
    ),

    SpecialistType.QA_AUDITOR: SpecialistSpec(
        specialist_type=SpecialistType.QA_AUDITOR,
        name="QA Auditor",
        description="Ensures policy compliance, brand safety, and error detection",
        capabilities=[
            SpecialistCapability.POLICY_COMPLIANCE,
            SpecialistCapability.BRAND_SAFETY,
            SpecialistCapability.ERROR_DETECTION,
            SpecialistCapability.QUALITY_ASSURANCE,
            SpecialistCapability.PROCESS_AUDIT
        ],
        input_requirements=[
            "Campaign configurations",
            "Creative assets",
            "Landing pages",
            "Tracking implementation"
        ],
        output_deliverables=[
            "Compliance Report",
            "Brand Safety Audit",
            "Error Log",
            "Quality Score",
            "Process Improvement Recommendations"
        ],
        dependencies=[]
    )
}


class SpecialistTask(BaseModel):
    """Task definition for specialist agents."""
    task_id: str
    specialist_type: SpecialistType
    objective: str
    inputs: Dict[str, Any]
    deliverable_format: str
    priority: str = "medium"
    deadline_hours: int = 24
    dependencies: List[str] = Field(default_factory=list)
    success_criteria: Dict[str, Any]
    assumptions: Dict[str, str] = Field(default_factory=dict)
    context: Optional[str] = None


def get_specialist_for_capability(capability: SpecialistCapability) -> List[SpecialistType]:
    """Get specialist types that have a specific capability."""
    specialists = []
    for spec in SPECIALIST_SPECS.values():
        if capability in spec.capabilities:
            specialists.append(spec.specialist_type)
    return specialists


def get_capabilities_for_specialist(specialist_type: SpecialistType) -> List[SpecialistCapability]:
    """Get capabilities for a specific specialist type."""
    spec = SPECIALIST_SPECS.get(specialist_type)
    if spec:
        return spec.capabilities
    return []


def validate_specialist_task(task: SpecialistTask) -> bool:
    """Validate that a task can be handled by the specified specialist."""
    spec = SPECIALIST_SPECS.get(task.specialist_type)
    if not spec:
        return False

    # Check if specialist has required capabilities (implied by specialist type)
    # Additional validation could be added here
    return True