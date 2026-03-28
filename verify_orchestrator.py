#!/usr/bin/env python3
"""Verify ORCHESTRATOR components can be imported and have correct structure."""

import sys

def verify_imports():
    """Verify all ORCHESTRATOR modules can be imported."""
    print("=== ORCHESTRATOR Component Verification ===\n")

    modules_to_test = [
        ("src.core.portfolio", ["Portfolio", "ChannelPerformance", "MarginalEfficiencyResult"]),
        ("src.core.artifacts", ["DecisionMemo", "ExperimentBrief", "PortfolioReview"]),
        ("src.agents.specialists", ["SpecialistType", "SPECIALIST_SPECS", "SpecialistCapability"]),
        ("src.agents.supervisor", ["Supervisor"]),
        ("src.agents.base", ["BaseAgent", "Task", "AgentStatus", "TaskPriority"]),
    ]

    all_passed = True

    for module_name, attributes in modules_to_test:
        try:
            module = __import__(module_name, fromlist=attributes)
            print(f"✅ {module_name}")

            # Verify attributes exist
            for attr in attributes:
                if hasattr(module, attr):
                    print(f"   ✓ {attr}")
                else:
                    print(f"   ✗ Missing: {attr}")
                    all_passed = False

        except ImportError as e:
            print(f"❌ {module_name}: {e}")
            all_passed = False
        except Exception as e:
            print(f"❌ {module_name}: Unexpected error - {e}")
            all_passed = False

    return all_passed


def verify_specialist_definitions():
    """Verify specialist definitions are complete."""
    print("\n=== Specialist Definitions ===\n")

    try:
        from src.agents.specialists import SPECIALIST_SPECS, SpecialistType

        print(f"Defined {len(SPECIALIST_SPECS)} specialist types:\n")

        required_specialists = {
            "MEASUREMENT_ANALYST": "Ensures tracking integrity and incrementality measurement",
            "COMPETITIVE_INTEL": "Analyzes competitor spend signals and creative patterns",
            "CHANNEL_STRATEGIST_SEARCH": "Manages search campaigns and keyword strategy",
            "CHANNEL_STRATEGIST_PMAX": "Manages Performance Max campaigns",
            "CHANNEL_STRATEGIST_PAID_SOCIAL": "Manages paid social campaigns",
            "CREATIVE_STRATEGIST": "Develops hooks, angles, and asset testing matrices",
            "FINANCE_GUARDIAN": "Ensures unit economics and margin constraints",
            "QA_AUDITOR": "Ensures policy compliance and brand safety",
        }

        all_present = True
        for specialist_name, description in required_specialists.items():
            try:
                spec_type = SpecialistType[specialist_name]
                spec = SPECIALIST_SPECS.get(spec_type)
                if spec:
                    print(f"✅ {spec.name}")
                    print(f"   Description: {spec.description}")
                    print(f"   Capabilities: {len(spec.capabilities)}")
                    print(f"   Deliverables: {len(spec.output_deliverables)}")
                else:
                    print(f"❌ {specialist_name}: Specification missing")
                    all_present = False
            except KeyError:
                print(f"❌ {specialist_name}: Not in SpecialistType enum")
                all_present = False

        return all_present

    except ImportError as e:
        print(f"❌ Failed to import specialists: {e}")
        return False


def verify_portfolio_models():
    """Verify portfolio models have required fields."""
    print("\n=== Portfolio Models ===\n")

    try:
        from src.core.portfolio import Portfolio, ChannelPerformance, UnitEconomics

        # Check ChannelPerformance has required fields
        required_channel_fields = [
            "channel_id", "current_spend_daily", "incremental_roas",
            "marginal_cpa", "measurement_confidence", "incrementality_confidence"
        ]

        channel_fields = ChannelPerformance.__fields__.keys()
        missing_fields = [f for f in required_channel_fields if f not in channel_fields]

        if missing_fields:
            print(f"❌ ChannelPerformance missing fields: {missing_fields}")
            return False
        else:
            print("✅ ChannelPerformance has all required fields")

        # Check Portfolio has required fields
        required_portfolio_fields = [
            "portfolio_id", "channels", "total_budget_daily",
            "unit_economics", "capacity_constraints"
        ]

        portfolio_fields = Portfolio.__fields__.keys()
        missing_fields = [f for f in required_portfolio_fields if f not in portfolio_fields]

        if missing_fields:
            print(f"❌ Portfolio missing fields: {missing_fields}")
            return False
        else:
            print("✅ Portfolio has all required fields")

        return True

    except ImportError as e:
        print(f"❌ Failed to import portfolio models: {e}")
        return False


def verify_artifact_templates():
    """Verify artifact templates have required structure."""
    print("\n=== Artifact Templates ===\n")

    try:
        from src.core.artifacts import DecisionMemo, ExperimentBrief, PortfolioReview

        # Check DecisionMemo has ORCHESTRATOR required sections
        required_memo_fields = [
            "context", "options_considered", "marginal_efficiency_table",
            "decision", "expected_impact", "monitoring_plan",
            "rollback_triggers", "assumptions", "confidence_level"
        ]

        memo_fields = DecisionMemo.__fields__.keys()
        missing_fields = [f for f in required_memo_fields if f not in memo_fields]

        if missing_fields:
            print(f"❌ DecisionMemo missing fields: {missing_fields}")
            return False
        else:
            print("✅ DecisionMemo has all ORCHESTRATOR required sections")

        # Check ExperimentBrief has required fields
        required_experiment_fields = [
            "hypothesis", "primary_metric", "minimum_duration_days",
            "success_threshold", "early_stop_rules"
        ]

        experiment_fields = ExperimentBrief.__fields__.keys()
        missing_fields = [f for f in required_experiment_fields if f not in experiment_fields]

        if missing_fields:
            print(f"❌ ExperimentBrief missing fields: {missing_fields}")
            return False
        else:
            print("✅ ExperimentBrief has all required fields")

        return True

    except ImportError as e:
        print(f"❌ Failed to import artifact templates: {e}")
        return False


def main():
    """Run all verification checks."""
    print("ORCHESTRATOR Supervisor Verification")
    print("=" * 40 + "\n")

    checks = [
        ("Module Imports", verify_imports),
        ("Specialist Definitions", verify_specialist_definitions),
        ("Portfolio Models", verify_portfolio_models),
        ("Artifact Templates", verify_artifact_templates),
    ]

    results = []
    for check_name, check_func in checks:
        print(f"\n{check_name}:")
        print("-" * 30)
        try:
            result = check_func()
            results.append((check_name, result))
            if result:
                print(f"✅ {check_name} PASSED")
            else:
                print(f"❌ {check_name} FAILED")
        except Exception as e:
            print(f"❌ {check_name} ERROR: {e}")
            results.append((check_name, False))

    # Summary
    print("\n" + "=" * 40)
    print("VERIFICATION SUMMARY:")
    print("=" * 40)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for check_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {check_name}")

    print(f"\n{passed}/{total} checks passed")

    if passed == total:
        print("\n✅ ORCHESTRATOR components are ready for implementation!")
        print("Next: Install dependencies and begin enhancing supervisor.py")
        return 0
    else:
        print(f"\n❌ {total - passed} checks failed")
        print("Fix the issues above before proceeding.")
        return 1


if __name__ == "__main__":
    sys.exit(main())