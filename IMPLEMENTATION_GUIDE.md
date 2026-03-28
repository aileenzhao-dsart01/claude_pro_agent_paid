# ORCHESTRATOR Supervisor Implementation Guide

## Current Status

✅ **Foundation Files Created:**
1. `src/core/portfolio.py` - Portfolio models, ChannelPerformance, MarginalEfficiencyResult
2. `src/core/artifacts.py` - DecisionMemo, ExperimentBrief, PortfolioReview, CompetitiveThreatMap
3. `src/agents/specialists.py` - Specialist definitions, capabilities, team model

✅ **Existing Supervisor:** `src/agents/supervisor.py` (263 lines) - Basic coordination framework

## Phase 1: Install Dependencies & Verify Baseline

### Step 1.1: Install Requirements
```bash
cd /Users/ranzhao/Documents/projects/test_project
pip install -r requirements.txt
```

### Step 1.2: Test Current Supervisor
```bash
python main.py
# Select option 1 to run supervisor demo
```

**Expected Output:**
- Supervisor initializes
- Research agent registers
- Task assignment works
- Workflow creation works

## Phase 2: Extend Supervisor with ORCHESTRATOR Core (Days 1-2)

### Step 2.1: Update Supervisor Class Definition
**File:** `src/agents/supervisor.py`

```python
# Add imports at top
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from collections import deque
import asyncio
import logging

from .base import BaseAgent, Task, TaskPriority, AgentStatus
from ..core.portfolio import Portfolio, ChannelPerformance, MarginalEfficiencyResult, AllocationRecommendation
from ..core.artifacts import DecisionMemo, ExperimentBrief, PortfolioReview
from .specialists import SpecialistType, SpecialistCapability, SPECIALIST_SPECS, SpecialistTask


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
        self.logger = logging.getLogger("supervisor")

        # NEW: ORCHESTRATOR attributes
        self.portfolio: Optional[Portfolio] = None
        self.decision_history: List[DecisionMemo] = []
        self.experiments: List[ExperimentBrief] = []
        self.competitive_intel: Dict[str, Any] = {}

        # Task board columns per ORCHESTRATOR spec
        self.task_board = {
            "backlog": [],
            "ready": [],
            "in_progress": [],
            "blocked": [],
            "review": [],
            "done": []
        }

        # Operating cadence
        self.last_daily_triage: Optional[datetime] = None
        self.last_weekly_review: Optional[datetime] = None
```

### Step 2.2: Add ORCHESTRATOR Task Types
**Add to `process_task` method:**

```python
async def process_task(self, task: Task) -> Dict[str, Any]:
    """Process ORCHESTRATOR coordination tasks."""
    # NEW ORCHESTRATOR task types
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

### Step 2.3: Implement Marginal Efficiency Calculator
**Add new method to Supervisor class:**

```python
async def _calculate_marginal_efficiency(
    self,
    portfolio: Portfolio,
    increment_percentage: float = 0.10
) -> Dict[str, MarginalEfficiencyResult]:
    """
    Calculate ΔProfit_i / ΔSpend_i for each channel.

    Implements ORCHESTRATOR marginal efficiency framework:
    1. For each channel, calculate next spend increment
    2. Estimate incremental outcome using best available evidence
    3. Compute marginal efficiency = ΔOutcome / ΔSpend
    4. Return sorted by marginal efficiency
    """
    results = {}

    for channel_id, channel_perf in portfolio.channels.items():
        current_spend = channel_perf.current_spend_daily
        increment = current_spend * increment_percentage
        proposed_spend = current_spend + increment

        # Estimate incremental outcome (placeholder - implement based on data)
        if channel_perf.incremental_roas:
            estimated_incremental_revenue = increment * channel_perf.incremental_roas
            estimated_incremental_profit = estimated_incremental_revenue * portfolio.unit_economics.gross_margin
        else:
            # Use attributed ROAS as proxy (with lower confidence)
            estimated_incremental_revenue = increment * (channel_perf.attributed_roas or 1.5)
            estimated_incremental_profit = estimated_incremental_revenue * portfolio.unit_economics.gross_margin * 0.7  # Discount for attribution bias

        marginal_profit_per_dollar = estimated_incremental_profit / increment if increment > 0 else 0

        results[channel_id] = MarginalEfficiencyResult(
            channel_id=channel_id,
            current_spend=current_spend,
            proposed_increment=increment,
            proposed_spend=proposed_spend,
            estimated_incremental_revenue=estimated_incremental_revenue,
            estimated_incremental_profit=estimated_incremental_profit,
            marginal_profit_per_dollar=marginal_profit_per_dollar,
            estimate_confidence=channel_perf.incrementality_confidence,
            data_source="historical_performance" if channel_perf.incremental_roas else "proxy_estimate",
            reversibility="reversible",
            feedback_speed_days=7,
            competitive_risk="medium"
        )

    return results
```

### Step 2.4: Implement Competitive Intel Gate
**Add new method:**

```python
async def _require_competitive_intel(
    self,
    change_type: str,
    change_magnitude: float,
    portfolio: Portfolio
) -> Dict[str, Any]:
    """
    Determine if competitive intel required per ORCHESTRATOR rules.

    Rules:
    - Reallocations > 15% of total budget
    - New channel launch
    - Major offer change
    - Major landing page change
    """
    requires_intel = False
    rationale = ""

    if change_type == "reallocation" and change_magnitude > 0.15:
        requires_intel = True
        rationale = f"Reallocation of {change_magnitude*100}% exceeds 15% threshold"
    elif change_type == "new_channel":
        requires_intel = True
        rationale = "New channel launch requires competitive analysis"
    elif change_type in ["offer_change", "landing_page_change"]:
        requires_intel = True
        rationale = f"Major {change_type.replace('_', ' ')} requires competitive context"

    return {
        "requires_competitive_intel": requires_intel,
        "rationale": rationale,
        "change_type": change_type,
        "change_magnitude": change_magnitude,
        "portfolio_id": portfolio.portfolio_id if portfolio else None
    }
```

### Step 2.5: Implement Budget Allocation Method
**Add new method:**

```python
async def _allocate_budget(self, payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Allocate budget using ORCHESTRATOR marginal efficiency framework.

    Steps:
    1. Validate measurement integrity
    2. Check competitive intel requirements
    3. Calculate marginal efficiency
    4. Make allocation decision
    5. Generate decision memo
    6. Create monitoring plan
    """
    portfolio = payload.get("portfolio")
    if not portfolio:
        return {"error": "Portfolio required for allocation"}

    # 1. Check measurement integrity
    measurement_confidence = min(
        channel.measurement_confidence
        for channel in portfolio.channels.values()
    )
    if measurement_confidence < 5:
        return {
            "warning": "Measurement confidence low (<5). Prioritize tracking audit.",
            "measurement_confidence": measurement_confidence,
            "recommendation": "Run MEASUREMENT_ANALYST tracking audit first"
        }

    # 2. Check competitive intel requirements
    total_budget = portfolio.total_budget_daily
    proposed_changes = payload.get("proposed_changes", {})

    competitive_intel_required = False
    for channel_id, change in proposed_changes.items():
        if abs(change) / total_budget > 0.15:
            competitive_intel_required = True
            break

    if competitive_intel_required and not portfolio.competitive_intel_available:
        return {
            "warning": "Competitive intel required for >15% reallocations",
            "competitive_intel_required": True,
            "recommendation": "Delegate to COMPETITIVE_INTEL agent first"
        }

    # 3. Calculate marginal efficiency
    marginal_efficiency = await self._calculate_marginal_efficiency(
        portfolio,
        increment_percentage=0.10
    )

    # 4. Sort by marginal efficiency
    sorted_channels = sorted(
        marginal_efficiency.items(),
        key=lambda x: x[1].marginal_profit_per_dollar or 0,
        reverse=True
    )

    # 5. Generate allocation recommendations
    recommendations = []
    remaining_budget = total_budget
    allocated_budget = 0

    for channel_id, efficiency in sorted_channels:
        channel_perf = portfolio.channels[channel_id]
        current_allocation = channel_perf.current_spend_daily

        # Allocate based on marginal efficiency
        if efficiency.marginal_profit_per_dollar and efficiency.marginal_profit_per_dollar > 0:
            recommended_increment = efficiency.proposed_increment
            recommended_allocation = current_allocation + recommended_increment

            # Check constraints
            if recommended_allocation <= remaining_budget:
                recommendations.append({
                    "channel_id": channel_id,
                    "current_allocation": current_allocation,
                    "recommended_allocation": recommended_allocation,
                    "allocation_change": recommended_increment,
                    "allocation_change_percentage": recommended_increment / current_allocation if current_allocation > 0 else 1.0,
                    "marginal_efficiency": efficiency.dict(),
                    "rationale": f"Marginal profit per dollar: ${efficiency.marginal_profit_per_dollar:.2f}"
                })
                allocated_budget += recommended_allocation
                remaining_budget -= recommended_allocation

    # 6. Generate decision memo
    decision_memo = await self._generate_decision_memo({
        "portfolio": portfolio,
        "marginal_efficiency": marginal_efficiency,
        "recommendations": recommendations,
        "competitive_intel_available": portfolio.competitive_intel_available
    })

    return {
        "status": "allocated",
        "recommendations": recommendations,
        "total_allocated": allocated_budget,
        "remaining_budget": remaining_budget,
        "marginal_efficiency_summary": {
            channel_id: {
                "marginal_profit_per_dollar": eff.marginal_profit_per_dollar,
                "confidence": eff.estimate_confidence
            }
            for channel_id, eff in marginal_efficiency.items()
        },
        "decision_memo_id": decision_memo.memo_id if decision_memo else None
    }
```

## Phase 3: Implement Operating Cadence (Days 2-3)

### Step 3.1: Daily Triage Method
```python
async def daily_triage(self) -> Dict[str, Any]:
    """
    ORCHESTRATOR daily triage process.

    1. Review task board status
    2. Resolve blockers
    3. Prioritize tasks
    4. Assign tasks to available agents
    5. Update visibility report
    """
    # Move ready tasks to in_progress if agents available
    tasks_assigned = 0
    for task in self.task_board["ready"][:]:  # Copy for iteration
        capable_agents = self._find_capable_agents(task.type)
        available_agents = [
            agent_id for agent_id in capable_agents
            if self.agent_status.get(agent_id) == AgentStatus.IDLE
        ]

        if available_agents:
            agent_id = available_agents[0]
            await self._assign_task_to_agent(task, agent_id)
            self._move_task_on_board(task.id, "ready", "in_progress")
            tasks_assigned += 1

    # Check for blocked tasks
    blocked_tasks = self.task_board["blocked"]
    for task in blocked_tasks:
        # Check if dependencies resolved
        if self._check_dependencies_resolved(task):
            self._move_task_on_board(task.id, "blocked", "ready")

    # Generate visibility report
    visibility_report = await self._generate_visibility_report()

    return {
        "status": "triage_completed",
        "tasks_assigned": tasks_assigned,
        "blocked_tasks_resolved": len(blocked_tasks) - len(self.task_board["blocked"]),
        "visibility_report": visibility_report,
        "timestamp": datetime.utcnow().isoformat()
    }
```

### Step 3.2: Weekly Allocation Review
```python
async def weekly_allocation_review(self) -> Dict[str, Any]:
    """
    ORCHESTRATOR weekly portfolio review.

    1. Review past week performance
    2. Calculate marginal efficiency
    3. Make reallocation decisions
    4. Generate portfolio review artifact
    5. Update playbook
    """
    if not self.portfolio:
        return {"error": "No portfolio configured for review"}

    # Calculate performance vs. previous week
    # (Implementation depends on data source)

    # Calculate marginal efficiency
    marginal_efficiency = await self._calculate_marginal_efficiency(
        self.portfolio,
        increment_percentage=0.10
    )

    # Identify scaling winners and cutting losers
    scaling_winners = []
    cutting_losers = []

    for channel_id, efficiency in marginal_efficiency.items():
        if efficiency.marginal_profit_per_dollar and efficiency.marginal_profit_per_dollar > 0.5:
            scaling_winners.append({
                "channel_id": channel_id,
                "marginal_profit_per_dollar": efficiency.marginal_profit_per_dollar,
                "recommended_increment": efficiency.proposed_increment
            })
        elif efficiency.marginal_profit_per_dollar and efficiency.marginal_profit_per_dollar < 0:
            cutting_losers.append({
                "channel_id": channel_id,
                "marginal_profit_per_dollar": efficiency.marginal_profit_per_dollar,
                "recommended_reduction": -efficiency.proposed_increment
            })

    # Generate portfolio review
    portfolio_review = PortfolioReview(
        review_id=f"review_{datetime.utcnow().strftime('%Y%m%d')}",
        review_period_start=datetime.utcnow() - timedelta(days=7),
        review_period_end=datetime.utcnow(),
        total_spend=self.portfolio.total_budget_daily * 7,  # Weekly spend
        channel_performance={},  # Populate with actual data
        marginal_efficiency_signals=[
            {
                "channel_id": channel_id,
                "marginal_profit_per_dollar": eff.marginal_profit_per_dollar,
                "confidence": eff.estimate_confidence
            }
            for channel_id, eff in marginal_efficiency.items()
        ],
        scaling_recommendations=scaling_winners,
        reduction_recommendations=cutting_losers,
        next_week_budget_plan={},  # Calculate based on recommendations
        key_learnings=[],
        next_actions=[]
    )

    self.last_weekly_review = datetime.utcnow()

    return {
        "status": "review_completed",
        "portfolio_review_id": portfolio_review.review_id,
        "scaling_winners": len(scaling_winners),
        "cutting_losers": len(cutting_losers),
        "marginal_efficiency_calculated": len(marginal_efficiency),
        "timestamp": datetime.utcnow().isoformat()
    }
```

## Phase 4: Integration & Testing (Days 3-5)

### Step 4.1: Update API Endpoints
**File:** `src/web/dashboard/app.py`

Add new endpoints:
- `POST /api/portfolio` - Create/update portfolio
- `POST /api/allocate` - Allocate budget using marginal efficiency
- `GET /api/decisions` - List decision memos
- `POST /api/daily-triage` - Trigger daily triage
- `POST /api/weekly-review` - Trigger weekly review

### Step 4.2: Create Test Suite
**File:** `tests/test_orchestrator.py`

Test:
1. Marginal efficiency calculations
2. Competitive intel gate logic
3. Budget allocation decisions
4. Task board management
5. Operating cadence methods

### Step 4.3: Create Example Workflow
**File:** `examples/orchestrator_workflow.py`

Demonstrate full ORCHESTRATOR workflow:
1. Intake & context snapshot
2. Portfolio creation
3. Competitive intel requirement check
4. Marginal efficiency calculation
5. Budget allocation decision
6. Monitoring plan creation

## Immediate Next Steps (First 4 Hours)

### 1. Install Dependencies & Verify Baseline (30 min)
```bash
pip install -r requirements.txt
python main.py  # Select option 1
```

### 2. Implement Core ORCHESTRATOR Methods (2 hours)
- Add imports and class definition updates to `supervisor.py`
- Implement `_calculate_marginal_efficiency()` method
- Implement `_require_competitive_intel()` method
- Implement `_allocate_budget()` method skeleton

### 3. Create Simple Test (1 hour)
- Create test portfolio data
- Test marginal efficiency calculations
- Verify competitive intel gate logic

### 4. Run Integration Test (30 min)
- Test supervisor with new ORCHESTRATOR methods
- Verify existing functionality still works

## Success Checklist

**Phase 1 Complete When:**
- [ ] Dependencies installed successfully
- [ ] Current supervisor demo runs without errors
- [ ] New portfolio and artifacts modules import correctly

**Phase 2 Complete When:**
- [ ] Supervisor class updated with ORCHESTRATOR identity
- [ ] Marginal efficiency calculator working
- [ ] Competitive intel gate logic implemented
- [ ] Budget allocation method skeleton complete

**Phase 3 Complete When:**
- [ ] Daily triage method implemented
- [ ] Weekly review method implemented
- [ ] Task board management working
- [ ] Visibility reports generated

**Phase 4 Complete When:**
- [ ] API endpoints updated
- [ ] Test suite passes
- [ ] Example workflow documented
- [ ] All existing functionality preserved

## Quick Start Command

```bash
# 1. Install
pip install -r requirements.txt

# 2. Test current supervisor
python main.py

# 3. Run ORCHESTRATOR enhanced tests
python -m pytest tests/test_orchestrator.py -v
```

---

**Ready to begin implementation.** Start with Step 1 (install dependencies) and proceed through the phases sequentially.