"""
Test Agent Standard v1 Compliance for all agents.

This test suite validates that all agent manifests conform to the Agent Standard v1
specification as defined in docs/AGENT_STANDARD_EXTENSIONS_PROPOSAL.md.

Required fields (minimal core):
- id, name, description, version, entrypoint, input_schema, output_schema, contract

Recommended/Optional extensions:
- ethics, desires, authority, tools, authentication, marketplace, pricing, io
- a2a, runtime, revisions (extensions we currently use)
- addresses, contracts, marketplaces, llm_models (future extensions)
"""

import json
from pathlib import Path
from typing import Any

import pytest


# Discover all agent manifest files
AGENTS_DIR = Path(__file__).parent.parent.parent / "platform" / "agentify" / "agents"
AGENT_MANIFESTS = list(AGENTS_DIR.glob("*/manifest.json"))


def load_manifest(manifest_path: Path) -> dict[str, Any]:
    """Load and parse a manifest JSON file."""
    with open(manifest_path, "r", encoding="utf-8") as f:
        return json.load(f)


class TestAgentStandardV1Core:
    """Test required core fields per Agent Standard v1."""

    @pytest.mark.parametrize("manifest_path", AGENT_MANIFESTS, ids=lambda p: p.parent.name)
    def test_required_core_fields(self, manifest_path: Path):
        """Validate that all required core fields are present."""
        manifest = load_manifest(manifest_path)
        agent_name = manifest_path.parent.name

        # Required core fields from Agent Standard v1
        required_fields = [
            "agent_id",  # id in spec, but we use agent_id
            "name",
            "version",
        ]

        for field in required_fields:
            assert field in manifest, (
                f"{agent_name}: Missing required field '{field}'"
            )
            assert manifest[field], f"{agent_name}: Field '{field}' is empty"

    @pytest.mark.parametrize("manifest_path", AGENT_MANIFESTS, ids=lambda p: p.parent.name)
    def test_overview_section(self, manifest_path: Path):
        """Validate overview section (contains description)."""
        manifest = load_manifest(manifest_path)
        agent_name = manifest_path.parent.name

        assert "overview" in manifest, f"{agent_name}: Missing 'overview' section"
        overview = manifest["overview"]

        assert "description" in overview, f"{agent_name}: Missing overview.description"
        assert overview["description"], f"{agent_name}: overview.description is empty"

        # Recommended overview fields
        if "owner" in overview:
            assert "name" in overview["owner"], f"{agent_name}: owner missing 'name'"
            assert "email" in overview["owner"], f"{agent_name}: owner missing 'email'"

        if "lifecycle" in overview:
            assert "stage" in overview["lifecycle"], f"{agent_name}: lifecycle missing 'stage'"


class TestAgentStandardV1Extensions:
    """Test mandatory extension fields per Agent Standard v1."""

    @pytest.mark.parametrize("manifest_path", AGENT_MANIFESTS, ids=lambda p: p.parent.name)
    def test_capabilities_section(self, manifest_path: Path):
        """Validate capabilities section (MANDATORY per Agent Standard v1)."""
        manifest = load_manifest(manifest_path)
        agent_name = manifest_path.parent.name

        assert "capabilities" in manifest, (
            f"{agent_name}: Missing MANDATORY 'capabilities' section"
        )
        assert isinstance(manifest["capabilities"], list), (
            f"{agent_name}: 'capabilities' must be a list"
        )
        assert len(manifest["capabilities"]) > 0, (
            f"{agent_name}: 'capabilities' must contain at least one capability (MANDATORY)"
        )

        # Validate capability structure
        for cap in manifest["capabilities"]:
            assert "name" in cap, f"{agent_name}: capability missing 'name'"
            assert "description" in cap, f"{agent_name}: capability missing 'description'"

    @pytest.mark.parametrize("manifest_path", AGENT_MANIFESTS, ids=lambda p: p.parent.name)
    def test_ethics_section(self, manifest_path: Path):
        """Validate ethics section (MANDATORY - Ethical Core)."""
        manifest = load_manifest(manifest_path)
        agent_name = manifest_path.parent.name

        assert "ethics" in manifest, (
            f"{agent_name}: Missing MANDATORY 'ethics' section"
        )
        ethics = manifest["ethics"]

        assert "framework" in ethics, (
            f"{agent_name}: ethics missing MANDATORY 'framework'"
        )
        assert ethics["framework"], f"{agent_name}: ethics.framework is empty"

        # Ethics should have constraints
        if "hard_constraints" not in ethics and "soft_constraints" not in ethics:
            pytest.fail(
                f"{agent_name}: ethics must have either 'hard_constraints' or 'soft_constraints' (MANDATORY)"
            )

    @pytest.mark.parametrize("manifest_path", AGENT_MANIFESTS, ids=lambda p: p.parent.name)
    def test_desires_section(self, manifest_path: Path):
        """Validate desires section (MANDATORY - Intent Profile)."""
        manifest = load_manifest(manifest_path)
        agent_name = manifest_path.parent.name

        assert "desires" in manifest, (
            f"{agent_name}: Missing MANDATORY 'desires' section"
        )
        desires = manifest["desires"]

        assert "profile" in desires, f"{agent_name}: desires missing 'profile'"
        assert isinstance(desires["profile"], list), f"{agent_name}: desires.profile must be a list"
        assert len(desires["profile"]) > 0, f"{agent_name}: desires.profile must not be empty"

        # Validate profile structure
        for desire in desires["profile"]:
            assert "id" in desire, f"{agent_name}: desire missing 'id'"
            assert "weight" in desire, f"{agent_name}: desire missing 'weight'"
            assert 0 <= desire["weight"] <= 1, (
                f"{agent_name}: desire weight must be between 0 and 1"
            )

        # Validate health signals if present
        if "health_signals" in desires:
            health = desires["health_signals"]
            assert "tension_thresholds" in health, (
                f"{agent_name}: health_signals missing 'tension_thresholds'"
            )

    @pytest.mark.parametrize("manifest_path", AGENT_MANIFESTS, ids=lambda p: p.parent.name)
    def test_authority_section(self, manifest_path: Path):
        """Validate authority section (MANDATORY - Split Authority / Four-Eyes Principle)."""
        manifest = load_manifest(manifest_path)
        agent_name = manifest_path.parent.name

        assert "authority" in manifest, (
            f"{agent_name}: Missing MANDATORY 'authority' section"
        )
        authority = manifest["authority"]

        # Split Authority: instruction and oversight must be separate
        assert "instruction" in authority, f"{agent_name}: authority missing 'instruction'"
        assert "oversight" in authority, f"{agent_name}: authority missing 'oversight'"

        instruction = authority["instruction"]
        oversight = authority["oversight"]

        assert "type" in instruction, f"{agent_name}: instruction missing 'type'"
        assert "id" in instruction, f"{agent_name}: instruction missing 'id'"

        assert "type" in oversight, f"{agent_name}: oversight missing 'type'"
        assert "id" in oversight, f"{agent_name}: oversight missing 'id'"

        # Oversight should be independent
        if "independent" in oversight:
            assert oversight["independent"] is True, (
                f"{agent_name}: oversight should be independent (Split Authority principle)"
            )

    @pytest.mark.parametrize("manifest_path", AGENT_MANIFESTS, ids=lambda p: p.parent.name)
    def test_authentication_section(self, manifest_path: Path):
        """Validate authentication section (MANDATORY)."""
        manifest = load_manifest(manifest_path)
        agent_name = manifest_path.parent.name

        assert "authentication" in manifest, (
            f"{agent_name}: Missing MANDATORY 'authentication' section"
        )
        auth = manifest["authentication"]

        assert "required" in auth, f"{agent_name}: authentication missing 'required' field"
        assert isinstance(auth["required"], bool), (
            f"{agent_name}: authentication.required must be boolean"
        )

    @pytest.mark.parametrize("manifest_path", AGENT_MANIFESTS, ids=lambda p: p.parent.name)
    def test_marketplace_section(self, manifest_path: Path):
        """Validate marketplace section (MANDATORY)."""
        manifest = load_manifest(manifest_path)
        agent_name = manifest_path.parent.name

        assert "marketplace" in manifest, (
            f"{agent_name}: Missing MANDATORY 'marketplace' section"
        )
        marketplace = manifest["marketplace"]

        assert "discoverable" in marketplace, f"{agent_name}: marketplace missing 'discoverable'"
        assert isinstance(marketplace["discoverable"], bool), (
            f"{agent_name}: marketplace.discoverable must be boolean"
        )

    @pytest.mark.parametrize("manifest_path", AGENT_MANIFESTS, ids=lambda p: p.parent.name)
    def test_pricing_section(self, manifest_path: Path):
        """Validate pricing section (MANDATORY)."""
        manifest = load_manifest(manifest_path)
        agent_name = manifest_path.parent.name

        assert "pricing" in manifest, (
            f"{agent_name}: Missing MANDATORY 'pricing' section"
        )
        pricing = manifest["pricing"]

        assert "model" in pricing, f"{agent_name}: pricing missing 'model'"
        assert pricing["model"] in ["free", "per_request", "usage_based", "subscription"], (
            f"{agent_name}: pricing.model must be one of: free, per_request, usage_based, subscription"
        )

        if "currency" in pricing:
            assert len(pricing["currency"]) == 3, (
                f"{agent_name}: pricing.currency should be 3-letter ISO code (e.g., 'EUR', 'USD')"
            )

    @pytest.mark.parametrize("manifest_path", AGENT_MANIFESTS, ids=lambda p: p.parent.name)
    def test_io_section(self, manifest_path: Path):
        """Validate I/O contracts section (MANDATORY)."""
        manifest = load_manifest(manifest_path)
        agent_name = manifest_path.parent.name

        assert "io" in manifest, (
            f"{agent_name}: Missing MANDATORY 'io' section"
        )
        io = manifest["io"]

        assert "input_formats" in io, f"{agent_name}: io missing 'input_formats'"
        assert "output_formats" in io, f"{agent_name}: io missing 'output_formats'"

        assert isinstance(io["input_formats"], list), f"{agent_name}: io.input_formats must be a list"
        assert isinstance(io["output_formats"], list), f"{agent_name}: io.output_formats must be a list"


class TestAgentStandardV1ExtensionsInUse:
    """Test extensions we currently implement (a2a, runtime, revisions)."""

    @pytest.mark.parametrize("manifest_path", AGENT_MANIFESTS, ids=lambda p: p.parent.name)
    def test_a2a_section(self, manifest_path: Path):
        """Validate A2A communication section (for agents that support it)."""
        manifest = load_manifest(manifest_path)
        agent_name = manifest_path.parent.name

        # A2A is optional but recommended
        if "a2a" not in manifest:
            pytest.skip(f"{agent_name}: A2A section not present (optional)")

        a2a = manifest["a2a"]
        assert "supported" in a2a, f"{agent_name}: a2a missing 'supported'"
        assert isinstance(a2a["supported"], bool), f"{agent_name}: a2a.supported must be boolean"

        if a2a["supported"]:
            assert "protocol" in a2a, f"{agent_name}: a2a missing 'protocol'"
            assert "endpoint" in a2a, f"{agent_name}: a2a missing 'endpoint'"

    @pytest.mark.parametrize("manifest_path", AGENT_MANIFESTS, ids=lambda p: p.parent.name)
    def test_runtime_section(self, manifest_path: Path):
        """Validate runtime section (for containerized agents)."""
        manifest = load_manifest(manifest_path)
        agent_name = manifest_path.parent.name

        # Runtime is optional but recommended for production agents
        if "runtime" not in manifest:
            pytest.skip(f"{agent_name}: Runtime section not present (optional)")

        runtime = manifest["runtime"]
        assert "containerized" in runtime, f"{agent_name}: runtime missing 'containerized'"
        assert isinstance(runtime["containerized"], bool), (
            f"{agent_name}: runtime.containerized must be boolean"
        )

        if runtime.get("containerized"):
            # If containerized, should have base_image
            if "base_image" not in runtime:
                pytest.skip(f"{agent_name}: runtime.base_image not specified")

    @pytest.mark.parametrize("manifest_path", AGENT_MANIFESTS, ids=lambda p: p.parent.name)
    def test_revisions_section(self, manifest_path: Path):
        """Validate revisions section (version history)."""
        manifest = load_manifest(manifest_path)
        agent_name = manifest_path.parent.name

        # Revisions is optional but recommended
        if "revisions" not in manifest:
            pytest.skip(f"{agent_name}: Revisions section not present (optional)")

        revisions = manifest["revisions"]
        assert "current" in revisions, f"{agent_name}: revisions missing 'current'"
        assert "history" in revisions, f"{agent_name}: revisions missing 'history'"

        assert isinstance(revisions["history"], list), (
            f"{agent_name}: revisions.history must be a list"
        )


class TestAgentStandardV1FutureExtensions:
    """Test future extensions (not yet implemented, but check if present)."""

    @pytest.mark.parametrize("manifest_path", AGENT_MANIFESTS, ids=lambda p: p.parent.name)
    def test_addresses_section_optional(self, manifest_path: Path):
        """Check if addresses section exists (future extension)."""
        manifest = load_manifest(manifest_path)
        agent_name = manifest_path.parent.name

        if "addresses" not in manifest:
            pytest.skip(f"{agent_name}: Addresses section not present (future extension)")

        addresses = manifest["addresses"]
        assert "primary" in addresses, f"{agent_name}: addresses missing 'primary'"

    @pytest.mark.parametrize("manifest_path", AGENT_MANIFESTS, ids=lambda p: p.parent.name)
    def test_contracts_section_optional(self, manifest_path: Path):
        """Check if contracts section exists (future extension)."""
        manifest = load_manifest(manifest_path)
        agent_name = manifest_path.parent.name

        if "contracts" not in manifest:
            pytest.skip(f"{agent_name}: Contracts section not present (future extension)")

        contracts = manifest["contracts"]
        assert "offered" in contracts, f"{agent_name}: contracts missing 'offered'"

    @pytest.mark.parametrize("manifest_path", AGENT_MANIFESTS, ids=lambda p: p.parent.name)
    def test_marketplaces_section_optional(self, manifest_path: Path):
        """Check if marketplaces section exists (future extension - Extension #7)."""
        manifest = load_manifest(manifest_path)
        agent_name = manifest_path.parent.name

        if "marketplaces" not in manifest:
            pytest.skip(f"{agent_name}: Marketplaces section not present (future extension)")

        marketplaces = manifest["marketplaces"]
        assert "discovery_enabled" in marketplaces, (
            f"{agent_name}: marketplaces missing 'discovery_enabled'"
        )


class TestAgentComplianceSummary:
    """Generate comprehensive compliance summary for each agent."""

    @pytest.mark.parametrize("manifest_path", AGENT_MANIFESTS, ids=lambda p: p.parent.name)
    def test_generate_compliance_summary(self, manifest_path: Path):
        """Generate and print comprehensive compliance summary."""
        manifest = load_manifest(manifest_path)
        agent_name = manifest_path.parent.name
        agent_id = manifest.get("agent_id", "N/A")
        version = manifest.get("version", "N/A")
        status = manifest.get("status", "N/A")

        print(f"\n{'='*80}")
        print(f"AGENT STANDARD V1 COMPLIANCE REPORT: {agent_name}")
        print(f"{'='*80}")
        print(f"Agent ID:      {agent_id}")
        print(f"Version:       {version}")
        print(f"Status:        {status}")
        print(f"Manifest Path: {manifest_path}")
        print(f"\n{'─'*80}")
        print("REQUIRED CORE FIELDS")
        print(f"{'─'*80}")

        # Required core fields
        core_fields = {
            "agent_id": "✅" if "agent_id" in manifest else "❌",
            "name": "✅" if "name" in manifest else "❌",
            "version": "✅" if "version" in manifest else "❌",
            "overview": "✅" if "overview" in manifest and "description" in manifest.get("overview", {}) else "❌",
        }

        for field, status_icon in core_fields.items():
            print(f"  {status_icon} {field}")

        print(f"\n{'─'*80}")
        print("MANDATORY EXTENSIONS")
        print(f"{'─'*80}")

        # Mandatory extensions
        extensions = {
            "capabilities": manifest.get("capabilities", []),
            "ethics": manifest.get("ethics"),
            "desires": manifest.get("desires"),
            "authority": manifest.get("authority"),
            "authentication": manifest.get("authentication"),
            "marketplace": manifest.get("marketplace"),
            "pricing": manifest.get("pricing"),
            "io": manifest.get("io"),
        }

        for ext_name, ext_value in extensions.items():
            if ext_value:
                if isinstance(ext_value, list):
                    print(f"  ✅ {ext_name} ({len(ext_value)} items)")
                elif isinstance(ext_value, dict):
                    keys = list(ext_value.keys())[:3]
                    keys_str = ", ".join(keys)
                    if len(ext_value) > 3:
                        keys_str += "..."
                    print(f"  ✅ {ext_name} ({keys_str})")
                else:
                    print(f"  ✅ {ext_name}")
            else:
                print(f"  ❌ {ext_name} (MISSING - MANDATORY)")

        print(f"\n{'─'*80}")
        print("OPTIONAL EXTENSIONS (CURRENTLY IN USE)")
        print(f"{'─'*80}")

        # Optional but currently used extensions
        optional_in_use = {
            "a2a": manifest.get("a2a"),
            "runtime": manifest.get("runtime"),
            "revisions": manifest.get("revisions"),
            "tools": manifest.get("tools"),
        }

        for opt_name, opt_value in optional_in_use.items():
            if opt_value:
                if isinstance(opt_value, list):
                    print(f"  ✅ {opt_name} ({len(opt_value)} items)")
                elif isinstance(opt_value, dict):
                    supported = opt_value.get("supported", True)
                    if opt_name == "a2a" and not supported:
                        print(f"  ⚠️  {opt_name} (declared but not supported)")
                    else:
                        print(f"  ✅ {opt_name}")
                else:
                    print(f"  ✅ {opt_name}")
            else:
                print(f"  ⚠️  {opt_name} (not present - optional)")

        print(f"\n{'─'*80}")
        print("FUTURE EXTENSIONS")
        print(f"{'─'*80}")

        # Future extensions
        future_extensions = {
            "addresses": manifest.get("addresses"),
            "contracts": manifest.get("contracts"),
            "marketplaces": manifest.get("marketplaces"),
            "llm_models": manifest.get("llm_models"),
        }

        for future_name, future_value in future_extensions.items():
            if future_value:
                print(f"  ✅ {future_name} (implemented early)")
            else:
                print(f"  ─  {future_name} (not yet implemented)")

        print(f"\n{'─'*80}")
        print("DETAILED COMPLIANCE CHECKS")
        print(f"{'─'*80}")

        # Ethics framework
        if "ethics" in manifest:
            framework = manifest["ethics"].get("framework", "N/A")
            hard_constraints = len(manifest["ethics"].get("hard_constraints", []))
            soft_constraints = len(manifest["ethics"].get("soft_constraints", []))
            print(f"  Ethics Framework:      {framework}")
            print(f"  Hard Constraints:      {hard_constraints}")
            print(f"  Soft Constraints:      {soft_constraints}")

        # Desires profile
        if "desires" in manifest:
            profile = manifest["desires"].get("profile", [])
            if profile:
                desires_str = ", ".join([f"{d['id']} ({d['weight']})" for d in profile[:3]])
                print(f"  Desires Profile:       {desires_str}")

        # Authority
        if "authority" in manifest:
            instruction_type = manifest["authority"].get("instruction", {}).get("type", "N/A")
            oversight_type = manifest["authority"].get("oversight", {}).get("type", "N/A")
            independent = manifest["authority"].get("oversight", {}).get("independent", False)
            print(f"  Instruction Authority: {instruction_type}")
            print(f"  Oversight Authority:   {oversight_type} {'(independent)' if independent else '(not independent)'}")

        # Pricing
        if "pricing" in manifest:
            pricing_model = manifest["pricing"].get("model", "N/A")
            currency = manifest["pricing"].get("currency", "N/A")
            print(f"  Pricing Model:         {pricing_model} ({currency})")

        print(f"\n{'─'*80}")
        print("OVERALL COMPLIANCE")
        print(f"{'─'*80}")

        # Calculate compliance score
        total_required = len(core_fields) + len(extensions)
        compliant = sum(1 for v in core_fields.values() if v == "✅")
        compliant += sum(1 for v in extensions.values() if v)
        compliance_percent = (compliant / total_required) * 100

        if compliance_percent == 100:
            print(f"  ✅ FULLY COMPLIANT: {compliant}/{total_required} required fields ({compliance_percent:.0f}%)")
        elif compliance_percent >= 90:
            print(f"  ⚠️  MOSTLY COMPLIANT: {compliant}/{total_required} required fields ({compliance_percent:.0f}%)")
        else:
            print(f"  ❌ NON-COMPLIANT: {compliant}/{total_required} required fields ({compliance_percent:.0f}%)")

        print(f"{'='*80}\n")

        # This test always passes - it's just for reporting
        assert True


class TestPydanticModelValidation:
    """Test that manifests can be loaded by Pydantic models."""

    @pytest.mark.parametrize("manifest_path", AGENT_MANIFESTS, ids=lambda p: p.parent.name)
    def test_pydantic_model_loading(self, manifest_path: Path):
        """Attempt to load manifest with Pydantic AgentManifest model."""
        manifest = load_manifest(manifest_path)
        agent_name = manifest_path.parent.name

        try:
            from core.agent_standard.models.manifest import AgentManifest
            
            # Try to load the manifest with Pydantic
            agent = AgentManifest(**manifest)
            print(f"\n✅ {agent_name}: Successfully loaded by Pydantic AgentManifest model")
            
        except ImportError as e:
            pytest.skip(f"{agent_name}: Cannot import AgentManifest model: {e}")
            
        except Exception as e:
            # Print detailed error for devs to see
            print(f"\n❌ {agent_name}: FAILED to load with Pydantic model")
            print(f"   Error: {type(e).__name__}: {str(e)}")
            print(f"\n   🔧 ACTION REQUIRED: Fix manifest or update AgentManifest model")
            pytest.fail(
                f"{agent_name}: Manifest cannot be loaded by Pydantic AgentManifest model: {e}"
            )


class TestSchemaConsistency:
    """Test consistency between JSON manifests and Pydantic schema."""

    @pytest.mark.parametrize("manifest_path", AGENT_MANIFESTS, ids=lambda p: p.parent.name)
    def test_unmodeled_fields_warning(self, manifest_path: Path):
        """Warn about fields in JSON that aren't in Pydantic model."""
        manifest = load_manifest(manifest_path)
        agent_name = manifest_path.parent.name

        # Known fields that should be in AgentManifest model
        known_pydantic_fields = {
            "agent_id", "name", "version", "status", "revisions", "overview",
            "capabilities", "ethics", "desires", "authority", "io",
            "ai_model", "framework_adapter", "tools", "knowledge", "memory",
            "schedule", "activities", "prompt", "guardrails", "team",
            "customers", "pricing", "observability",
            # Extensions we currently use
            "authentication", "marketplace", "a2a", "runtime"
        }

        # Fields in the JSON that aren't in the Pydantic model
        json_fields = set(manifest.keys())
        unmodeled_fields = json_fields - known_pydantic_fields

        if unmodeled_fields:
            print(f"\n⚠️  {agent_name}: Fields in JSON but NOT in Pydantic AgentManifest model:")
            for field in sorted(unmodeled_fields):
                print(f"   - {field}")
            print(f"\n   🔧 ACTION: Add these fields to core/agent_standard/models/manifest.py")
            print(f"          OR remove them from the manifest if they're not needed\n")

        # Always pass - this is just a warning
        assert True

    @pytest.mark.parametrize("manifest_path", AGENT_MANIFESTS, ids=lambda p: p.parent.name)
    def test_dict_any_fields_warning(self, manifest_path: Path):
        """Warn about dict[str, Any] fields that should have proper Pydantic models."""
        manifest = load_manifest(manifest_path)
        agent_name = manifest_path.parent.name

        # Fields in AgentManifest that use dict[str, Any] instead of proper models
        dict_any_fields = {
            "io": "IOContract model exists but not used in manifest.py",
            "knowledge": "Needs a Knowledge model",
            "memory": "Needs a Memory model",
            "schedule": "Needs a Schedule model",
            "team": "Needs a Team model",
            "customers": "Needs a Customers model",
            "pricing": "Needs a Pricing model (basic dict currently)",
            "observability": "Needs an Observability model",
        }

        present_dict_fields = {k: v for k, v in dict_any_fields.items() if k in manifest}

        if present_dict_fields:
            print(f"\n⚠️  {agent_name}: Fields using dict[str, Any] instead of proper Pydantic models:")
            for field, note in present_dict_fields.items():
                print(f"   - {field}: {note}")
            print(f"\n   🔧 RECOMMENDATION: Create proper Pydantic models for type safety")
            print(f"          See: core/agent_standard/models/ for examples\n")

        # Always pass - this is just a warning
        assert True

    @pytest.mark.parametrize("manifest_path", AGENT_MANIFESTS, ids=lambda p: p.parent.name)
    def test_io_model_not_used(self, manifest_path: Path):
        """Specific check: IOContract model exists but manifest.py uses dict[str, Any]."""
        manifest = load_manifest(manifest_path)
        agent_name = manifest_path.parent.name

        if "io" in manifest:
            print(f"\n⚠️  {agent_name}: 'io' field is present")
            print(f"   ℹ️  IOContract model exists at: core/agent_standard/models/io_contracts.py")
            print(f"   ⚠️  But manifest.py uses: io: dict[str, Any] = Field(...)")
            print(f"\n   🔧 ACTION: Update manifest.py to use IOContract model:")
            print(f"          io: IOContract = Field(..., description='Input/output configuration')\n")

        # Always pass - this is just a warning
        assert True


class TestManifestConsistency:
    """Test internal consistency of manifests."""

    @pytest.mark.parametrize("manifest_path", AGENT_MANIFESTS, ids=lambda p: p.parent.name)
    def test_agent_id_format(self, manifest_path: Path):
        """Validate agent_id follows naming convention."""
        manifest = load_manifest(manifest_path)
        agent_name = manifest_path.parent.name

        agent_id = manifest.get("agent_id", "")
        
        # agent_id should start with "agent."
        assert agent_id.startswith("agent."), (
            f"{agent_name}: agent_id should start with 'agent.' (got: {agent_id})"
        )

        # Should have at least 3 parts (agent.domain.name)
        parts = agent_id.split(".")
        assert len(parts) >= 3, (
            f"{agent_name}: agent_id should have format 'agent.domain.name' (got: {agent_id})"
        )

    @pytest.mark.parametrize("manifest_path", AGENT_MANIFESTS, ids=lambda p: p.parent.name)
    def test_version_format(self, manifest_path: Path):
        """Validate version follows semver format."""
        manifest = load_manifest(manifest_path)
        agent_name = manifest_path.parent.name

        version = manifest.get("version", "")
        
        # Simple semver check: should be X.Y.Z
        parts = version.split(".")
        assert len(parts) == 3, (
            f"{agent_name}: version should follow semver (X.Y.Z) (got: {version})"
        )

        for part in parts:
            assert part.isdigit(), (
                f"{agent_name}: version parts must be numeric (got: {version})"
            )

    @pytest.mark.parametrize("manifest_path", AGENT_MANIFESTS, ids=lambda p: p.parent.name)
    def test_status_valid(self, manifest_path: Path):
        """Validate status field has valid value."""
        manifest = load_manifest(manifest_path)
        agent_name = manifest_path.parent.name

        if "status" in manifest:
            valid_statuses = ["active", "deprecated", "development", "testing"]
            assert manifest["status"] in valid_statuses, (
                f"{agent_name}: status must be one of: {valid_statuses} (got: {manifest['status']})"
            )
