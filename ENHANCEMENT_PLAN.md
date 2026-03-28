# ORCHESTRATOR Supervisor Enhancement Plan

## Current State Assessment

**File:** `src/agents/supervisor.py` (263 lines)

### ✅ Existing Foundation
- **Base Agent Structure**: Extends `BaseAgent` correctly
- **Task Coordination**: Basic capability-based routing with queue
- **Agent Management**: Registry with status tracking
- **Workflow Support**: Multi-step process orchestration
- **History & Audit**: Task history with results/errors
- **Performance Metrics**: Agent success rate tracking
- **Async Execution**: Non-blocking task processing

### ❌ Missing ORCHESTRATOR Capabilities

**Strategic Decision-Making (Critical)**
1. No portfolio modeling or budget allocation logic
2. No marginal efficiency calculations (ΔProfit/ΔSpend)
3. No competitive intel requirement gates for strategic moves
4. No measurement integrity validation before scaling
5. No experiment design framework

**Operational Rigor**
6. No standard artifacts (Decision Memo, Experiment Brief, Portfolio Review)
7. No operating cadence (daily triage, weekly allocation review)
8. No visibility reporting structure
9. No specialist agent definitions per ORCHESTRATOR team model
10. No assumption/confidence tracking

**Task Management Gaps**
11. No task board with columns (Backlog, Ready, In Progress, etc.)
12. No task metadata: owner, goal, inputs, deliverables, due date, success criteria
13. No dependency tracking between tasks
14. No reversible vs. irreversible move distinction

## Transformation Strategy

**Approach**: Enhance existing supervisor rather than rebuild
- Keep working coordination infrastructure
- Add ORCHESTRATOR decision layer on top
- Implement specialist agent interfaces
- Add portfolio management and marginal efficiency logic

## Phase 1: Core Decision Framework (Days 1-2)

### 1.1 Portfolio Data Models
```python
# New file: src/core/portfolio.py
class ChannelPerformance:
    channel_id: str
    current_spend: float
    estimated_iROAS: float
    marginal_CPA: float
    confidence: int  # 1-10
    measurement_integrity: int  # 1-10
    constraints: List[str]  # ["creative", "tracking", "budget"]

class Portfolio:
    channels: Dict[str, ChannelPerformance]
    total_budget: float
    unit_economics: Dict[str, float]  # LTV, gross_margin, payback_window
    capacity_constraints: Dict[str, Any]  # creative_throughput, dev_bandwidth
    competitive_intel_required: bool
```

### 1.2 Marginal Efficiency Calculator
```python
# Add to Supervisor class
async def calculate_marginal_efficiency(
    self,
    portfolio: Portfolio,
    increment_percentage: float = 0.10
) -> Dict[str, Dict[str, Any]]:
    """
    Calculate ΔProfit_i / ΔSpend_i for each channel.
    Return marginal efficiency table.
    """
```

### 1.3 Competitive Intel Gate
```python
# Add to Supervisor class
async def require_competitive_intel(
    self,
    change_type: str,  # "reallocation", "new_channel", "offer_change", "landing_page"
    change_magnitude: float  # percentage of total budget
) -> bool:
    """
    Return True if competitive intel required per ORCHESTRATOR rules:
    - Reallocations > 15% of total budget
    - New channel launch
    - Major offer change
    - Major landing page change
    """
```

### 1.4 Decision Memo Generator
```python
# New file: src/core/artifacts.py
class DecisionMemo:
    context: str
    options_considered: List[Dict[str, Any]]
    competitive_intel_summary: Optional[str]
    marginal_efficiency_table: Dict[str, Any]
    decision: str
    expected_impact: Dict[str, Any]
    monitoring_plan: Dict[str, Any]
    rollback_triggers: List[str]
    assumptions: Dict[str, str]
    confidence: int  # 1-10
```

## Phase 2: Specialist Agent Integration (Days 2-3)

### 2.1 ORCHESTRATOR Team Model Implementation
```python
# New file: src/agents/specialists.py
SPECIALIST_AGENTS = {
    "MEASUREMENT_ANALYST": {
        "capabilities": [
            "tracking_audit",
            "attribution_analysis",
            "lift_test_design",
            "data_quality_check"
        ],
        "deliverables": ["Tracking_Health_Report", "Lift_Test_Design"]
    },
    "COMPETITIVE_INTEL": {
        "capabilities": [
            "competitor_scan",
            "auction_analysis",
            "creative_patterns",
            "messaging_analysis"
        ],
        "deliverables": ["Competitive_Threat_Map", "SERP_Analysis"]
    },
    "CHANNEL_STRATEGIST_SEARCH": {
        "capabilities": [
            "keyword_optimization",
            "bid_management",
            "structure_audit",
            "experiment_design"
        ],
        "deliverables": ["Keyword_Strategy", "Bid_Recommendations"]
    },
    "CHANNEL_STRATEGIST_PMAX": {...},
    "CHANNEL_STRATEGIST_PAIDSOCIAL": {...},
    "CREATIVE_STRATEGIST": {...},
    "FINANCE_GUARDIAN": {...},
    "QA_AUDITOR": {...}
}
```

### 2.2 Enhanced Task Model
```python
# Extend src/agents/base.py Task class
class OrchestratorTask(Task):
    """Task with ORCHESTRATOR metadata."""
    owner: str  # Agent ID
    goal: str  # What we're trying to achieve
    inputs: List[str]  # Required inputs/dependencies
    deliverable_format: str  # "decision_memo", "experiment_brief", "portfolio_review"
    due_date: datetime
    success_criteria: Dict[str, Any]  # Quantifiable success metrics
    assumptions: Dict[str, str]  # Documented assumptions
    confidence: int  # 1-10 confidence rating
    reversibility: str  # "reversible", "irreversible", "partially_reversible"

    # Task board status
    board_column: str = "Backlog"  # Backlog, Ready, In Progress, Blocked, Review, Done
    dependencies: List[str] = []  # Task IDs this depends on
    blocks: List[str] = []  # Task IDs blocked by this
```

### 2.3 Task Board Management
```python
# Add to Supervisor class
class TaskBoard:
    columns: Dict[str, List[OrchestratorTask]]

    def add_task(self, task: OrchestratorTask, column: str = "Backlog"):
    def move_task(self, task_id: str, from_column: str, to_column: str):
    def get_blocked_tasks(self) -> List[OrchestratorTask]:
    def get_due_soon(self, hours: int = 24) -> List[OrchestratorTask]:
```

## Phase 3: Operational Cadence (Days 3-4)

### 3.1 Operating Workflow Implementation
```python
# Add to Supervisor class
async def run_orchestrator_workflow(self, business_context: Dict[str, Any]):
    """
    Implement ORCHESTRATOR 6-step workflow:
    1. Step 0 — Intake & Context Snapshot
    2. Step 1 — Create Decision Frame (Portfolio View)
    3. Step 2 — Require Competitive Research (if needed)
    4. Step 3 — Delegate Specialist Work in Parallel
    5. Step 4 — Synthesize → Decide Using Marginal Efficiency
    6. Step 5 — Execution Plan + Monitoring
    7. Step 6 — Retrospective Learning Loop
    """
```

### 3.2 Cadence Methods
```python
async def daily_triage(self):
    """Daily task prioritization and blocker resolution."""

async def weekly_allocation_review(self):
    """Weekly budget reallocation based on marginal efficiency."""

async def experiment_retrospective(self, experiment_id: str):
    """Learning loop for completed experiments."""
```

### 3.3 Visibility Reporting
```python
async def generate_visibility_report(self) -> Dict[str, Any]:
    """
    Return ORCHESTRATOR visibility requirements:
    A) Current objective + KPI
    B) What's in motion (top 3–7 tasks)
    C) Key decisions made + rationale (incl. marginal efficiency)
    D) Risks / blockers / missing data
    E) Next actions + owners + deadlines
    """
```

## Phase 4: Integration & Testing (Days 4-5)

### 4.1 API Endpoint Updates
- Extend `/api/system/status` to include ORCHESTRATOR visibility report
- Add `/api/portfolio` endpoints for budget allocation
- Add `/api/decisions` for decision memo storage/retrieval
- Add `/api/experiments` for experiment management

### 4.2 Database Schema Updates
- Extend `tasks` table with ORCHESTRATOR metadata
- Add `portfolios` table for budget allocation history
- Add `decisions` table for decision memo storage
- Add `experiments` table for experiment tracking

### 4.3 Enhanced Testing
- Test marginal efficiency calculations
- Test competitive intel gate logic
- Test task board functionality
- Test operating cadence workflows

## Specific Code Changes to supervisor.py

### 1. Class Definition Update
```python
class Supervisor(BaseAgent):
    """ORCHESTRATOR — Supervision Agent for Digital Marketing Advertising Team."""

    def __init__(self):
        super().__init__(
            agent_id="orchestrator_001",
            name="ORCHESTRATOR",
            description=(
                "Operating system of a high-performance advertising team: "
                "part air-traffic controller, part chief-of-staff, "
                "part finance-minded growth strategist."
            )
        )
        # Existing attributes
        self.agents: Dict[str, BaseAgent] = {}
        self.task_queue = deque()
        self.task_history: Dict[str, Task] = {}
        self.agent_status: Dict[str, AgentStatus] = {}

        # NEW: ORCHESTRATOR attributes
        self.portfolio: Optional[Portfolio] = None
        self.task_board: TaskBoard = TaskBoard()
        self.decision_history: List[DecisionMemo] = []
        self.experiments: List[ExperimentBrief] = []
        self.operating_cadence: Dict[str, datetime] = {}
```

### 2. Enhanced process_task Method
```python
async def process_task(self, task: Task) -> Dict[str, Any]:
    """Process ORCHESTRATOR coordination tasks."""
    if task.type == "allocate_budget":
        return await self._allocate_budget(task.payload)
    elif task.type == "create_experiment":
        return await self._create_experiment(task.payload)
    elif task.type == "require_competitive_intel":
        return await self._require_competitive_intel(task.payload)
    elif task.type == "calculate_marginal_efficiency":
        return await self._calculate_marginal_efficiency(task.payload)
    elif task.type == "generate_decision_memo":
        return await self._generate_decision_memo(task.payload)
    elif task.type == "run_daily_triage":
        return await self.daily_triage()
    elif task.type == "run_weekly_review":
        return await self.weekly_allocation_review()
    # Existing task types
    elif task.type == "assign_task":
        return await self._assign_task(task.payload)
    elif task.type == "register_agent":
        return await self._register_agent(task.payload)
    elif task.type == "get_system_status":
        return await self._get_system_status()
    elif task.type == "create_workflow":
        return await self._create_workflow(task.payload)
    else:
        raise ValueError(f"Unknown task type: {task.type}")
```

### 3. New ORCHESTRATOR Methods
```python
async def _allocate_budget(self, payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Allocate budget using marginal efficiency framework.
    Requires competitive intel for >15% reallocations.
    """
    # 1. Validate measurement integrity
    # 2. Check if competitive intel required
    # 3. Calculate marginal efficiency
    # 4. Make allocation decision
    # 5. Generate decision memo
    # 6. Create monitoring plan
    pass

async def _create_experiment(self, payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create experiment brief following ORCHESTRATOR standards.
    """
    # 1. Validate hypothesis
    # 2. Design variant
    # 3. Set success metrics + guardrails
    # 4. Calculate minimum sample size
    # 5. Define stop rules
    # 6. Assign owner + timeline
    pass
```

## Immediate Next Actions (First 24 Hours)

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Verify Current Supervisor Works**
   ```bash
   python main.py  # Select option 1
   ```

3. **Implement Phase 1 Core Components**
   - Create `src/core/portfolio.py`
   - Add marginal efficiency calculator to supervisor
   - Add competitive intel gate logic
   - Create decision memo template

4. **Test Enhanced Supervisor**
   - Write tests for marginal efficiency calculations
   - Test competitive intel gate
   - Verify decision memo generation

## Success Metrics

**Phase 1 Complete When:**
- [ ] Supervisor can calculate marginal efficiency from portfolio data
- [ ] Competitive intel gate correctly triggers for >15% reallocations
- [ ] Decision memos generated with required sections
- [ ] All existing functionality preserved

**Phase 2 Complete When:**
- [ ] All ORCHESTRATOR specialist agents defined
- [ ] Enhanced task model with ORCHESTRATOR metadata
- [ ] Task board with column management implemented
- [ ] Specialist tasks routed correctly

**Phase 3 Complete When:**
- [ ] Operating workflow (6 steps) implemented
- [ ] Daily triage and weekly review methods working
- [ ] Visibility reports generated correctly
- [ ] Retrospective learning loop functional

## Risk Mitigation

1. **Preserve Existing Functionality**: All changes additive; existing API unchanged
2. **Incremental Implementation**: Phase-based approach with testing at each phase
3. **Backward Compatibility**: New features optional; old tasks still work
4. **Documentation**: Each new component documented with examples

---

**Estimated Timeline**: 5 days for full ORCHESTRATOR implementation
**Priority Order**: Phase 1 (Decision Framework) → Phase 2 (Specialists) → Phase 3 (Cadence)

**Ready to begin Phase 1 implementation.**