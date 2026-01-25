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
    """Test recommended/optional extension fields."""

    @pytest.mark.parametrize("manifest_path", AGENT_MANIFESTS, ids=lambda p: p.parent.name)
    def test_capabilities_section(self, manifest_path: Path):
        """Validate capabilities section exists and is non-empty."""
        manifest = load_manifest(manifest_path)
        agent_name = manifest_path.parent.name

        assert "capabilities" in manifest, f"{agent_name}: Missing 'capabilities' section"
        assert isinstance(manifest["capabilities"], list), (
            f"{agent_name}: 'capabilities' must be a list"
        )
        assert len(manifest["capabilities"]) > 0, (
            f"{agent_name}: 'capabilities' must contain at least one capability"
        )

        # Validate capability structure
        for cap in manifest["capabilities"]:
            assert "name" in cap, f"{agent_name}: capability missing 'name'"
            assert "description" in cap, f"{agent_name}: capability missing 'description'"

    @pytest.mark.parametrize("manifest_path", AGENT_MANIFESTS, ids=lambda p: p.parent.name)
    def test_ethics_section(self, manifest_path: Path):
        """Validate ethics section (Ethical Core)."""
        manifest = load_manifest(manifest_path)
        agent_name = manifest_path.parent.name

        assert "ethics" in manifest, f"{agent_name}: Missing 'ethics' section"
        ethics = manifest["ethics"]

        assert "framework" in ethics, f"{agent_name}: ethics missing 'framework'"
        assert ethics["framework"], f"{agent_name}: ethics.framework is empty"

        # Ethics should have constraints
        if "hard_constraints" not in ethics and "soft_constraints" not in ethics:
            pytest.fail(
                f"{agent_name}: ethics must have either 'hard_constraints' or 'soft_constraints'"
            )

    @pytest.mark.parametrize("manifest_path", AGENT_MANIFESTS, ids=lambda p: p.parent.name)
    def test_desires_section(self, manifest_path: Path):
        """Validate desires section (Intent Profile)."""
        manifest = load_manifest(manifest_path)
        agent_name = manifest_path.parent.name

        assert "desires" in manifest, f"{agent_name}: Missing 'desires' section"
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
        """Validate authority section (Split Authority)."""
        manifest = load_manifest(manifest_path)
        agent_name = manifest_path.parent.name

        assert "authority" in manifest, f"{agent_name}: Missing 'authority' section"
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
        """Validate authentication section exists."""
        manifest = load_manifest(manifest_path)
        agent_name = manifest_path.parent.name

        assert "authentication" in manifest, f"{agent_name}: Missing 'authentication' section"
        auth = manifest["authentication"]

        assert "required" in auth, f"{agent_name}: authentication missing 'required' field"
        assert isinstance(auth["required"], bool), (
            f"{agent_name}: authentication.required must be boolean"
        )

    @pytest.mark.parametrize("manifest_path", AGENT_MANIFESTS, ids=lambda p: p.parent.name)
    def test_marketplace_section(self, manifest_path: Path):
        """Validate marketplace section exists."""
        manifest = load_manifest(manifest_path)
        agent_name = manifest_path.parent.name

        assert "marketplace" in manifest, f"{agent_name}: Missing 'marketplace' section"
        marketplace = manifest["marketplace"]

        assert "discoverable" in marketplace, f"{agent_name}: marketplace missing 'discoverable'"
        assert isinstance(marketplace["discoverable"], bool), (
            f"{agent_name}: marketplace.discoverable must be boolean"
        )

    @pytest.mark.parametrize("manifest_path", AGENT_MANIFESTS, ids=lambda p: p.parent.name)
    def test_pricing_section(self, manifest_path: Path):
        """Validate pricing section exists."""
        manifest = load_manifest(manifest_path)
        agent_name = manifest_path.parent.name

        assert "pricing" in manifest, f"{agent_name}: Missing 'pricing' section"
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
        """Validate I/O contracts section."""
        manifest = load_manifest(manifest_path)
        agent_name = manifest_path.parent.name

        assert "io" in manifest, f"{agent_name}: Missing 'io' section"
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
