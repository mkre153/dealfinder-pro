#!/usr/bin/env python3
"""
GoHighLevel Setup Validator

Validates that all required GHL configuration, custom fields, tags, and workflows
are properly set up before running the integration.
"""

import json
import logging
from typing import Dict, List, Tuple
from integrations import GoHighLevelConnector
from integrations.ghl_config_example import get_config, validate_config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GHLSetupValidator:
    """Validates GHL setup for DealFinder Pro integration"""

    def __init__(self, ghl_connector: GoHighLevelConnector):
        self.ghl = ghl_connector
        self.errors = []
        self.warnings = []
        self.validated_items = []

    def validate_all(self) -> bool:
        """
        Run all validation checks

        Returns:
            True if all validations pass
        """
        print("\n" + "="*60)
        print("GoHighLevel Setup Validator")
        print("="*60 + "\n")

        # Test connection
        if not self._validate_connection():
            return False

        # Validate custom fields
        self._validate_custom_fields()

        # Validate pipeline stages
        self._validate_pipeline_stages()

        # Print results
        self._print_results()

        return len(self.errors) == 0

    def _validate_connection(self) -> bool:
        """Test API connection"""
        print("📡 Testing API Connection...")

        try:
            if self.ghl.test_connection():
                print("✓ API connection successful\n")
                self.validated_items.append("API Connection")
                return True
            else:
                print("✗ API connection failed\n")
                self.errors.append("Cannot connect to GoHighLevel API")
                return False
        except Exception as e:
            print(f"✗ Connection error: {e}\n")
            self.errors.append(f"Connection error: {str(e)}")
            return False

    def _validate_custom_fields(self):
        """Validate that all required custom fields exist"""
        print("📋 Validating Custom Fields...")

        # Load field mapping
        try:
            with open('mappings/ghl_field_mapping.json', 'r') as f:
                mapping = json.load(f)
        except FileNotFoundError:
            self.errors.append("Field mapping file not found: mappings/ghl_field_mapping.json")
            print("✗ Field mapping file not found\n")
            return

        # Get custom fields from GHL
        try:
            ghl_fields = self.ghl.get_custom_fields()
            ghl_field_keys = {f.get("key"): f for f in ghl_fields}
        except Exception as e:
            self.errors.append(f"Failed to fetch custom fields: {str(e)}")
            print(f"✗ Failed to fetch custom fields: {e}\n")
            return

        # Check contact fields
        print("\n  Contact/Buyer Fields:")
        contact_fields = mapping.get("contact_fields", {})
        for field_name, field_key in contact_fields.items():
            # Extract actual key (remove customField. prefix if present)
            actual_key = field_key.replace("customField.", "").replace("tag.", "")

            if "tag." in field_key:
                # Tag, not a custom field
                print(f"    ℹ {field_name}: Tag (skipped)")
                continue

            if actual_key in ghl_field_keys:
                field_info = ghl_field_keys[actual_key]
                field_type = field_info.get("dataType", "unknown")
                print(f"    ✓ {field_name} ({field_type})")
                self.validated_items.append(f"Contact field: {field_name}")
            else:
                print(f"    ✗ {field_name} - MISSING")
                self.errors.append(f"Missing contact custom field: {field_name} (key: {actual_key})")

        # Check opportunity fields
        print("\n  Opportunity/Property Fields:")
        opp_fields = mapping.get("opportunity_fields", {})
        for field_name, field_key in opp_fields.items():
            actual_key = field_key.replace("customField.", "")

            if actual_key in ghl_field_keys:
                field_info = ghl_field_keys[actual_key]
                field_type = field_info.get("dataType", "unknown")
                print(f"    ✓ {field_name} ({field_type})")
                self.validated_items.append(f"Opportunity field: {field_name}")
            else:
                print(f"    ✗ {field_name} - MISSING")
                self.errors.append(f"Missing opportunity custom field: {field_name} (key: {actual_key})")

        # Check required fields
        print("\n  Required Fields:")
        required_contact = mapping.get("required_contact_fields", [])
        required_opp = mapping.get("required_opportunity_fields", [])

        all_required_exist = True
        for field in required_contact:
            field_key = contact_fields.get(field, "").replace("customField.", "")
            if field_key not in ghl_field_keys and "tag." not in contact_fields.get(field, ""):
                print(f"    ✗ Required contact field missing: {field}")
                all_required_exist = False
            else:
                print(f"    ✓ Required contact field exists: {field}")

        for field in required_opp:
            field_key = opp_fields.get(field, "").replace("customField.", "")
            if field_key not in ghl_field_keys:
                print(f"    ✗ Required opportunity field missing: {field}")
                all_required_exist = False
            else:
                print(f"    ✓ Required opportunity field exists: {field}")

        if all_required_exist:
            self.validated_items.append("All required fields exist")

        print()

    def _validate_pipeline_stages(self):
        """Validate pipeline and stages"""
        print("🔄 Validating Pipeline & Stages...")

        config = get_config()
        pipeline_id = config.get("pipeline_id")

        if not pipeline_id or pipeline_id == "your_pipeline_id":
            print("✗ Pipeline ID not configured\n")
            self.errors.append("Pipeline ID not configured in ghl_config.py")
            return

        try:
            stages = self.ghl.get_pipeline_stages(pipeline_id)

            if not stages:
                print("✗ No stages found in pipeline\n")
                self.errors.append("No stages found in configured pipeline")
                return

            print(f"\n  Found {len(stages)} stages in pipeline:")
            stage_ids = {s.get("id"): s.get("name") for s in stages}

            # Check configured stages
            configured_stages = config.get("stages", {})
            for stage_name, stage_id in configured_stages.items():
                if stage_id in stage_ids:
                    print(f"    ✓ {stage_name}: {stage_ids[stage_id]}")
                    self.validated_items.append(f"Stage: {stage_name}")
                elif stage_id.startswith("stage_id_"):
                    print(f"    ✗ {stage_name}: NOT CONFIGURED")
                    self.errors.append(f"Stage '{stage_name}' ID not configured")
                else:
                    print(f"    ✗ {stage_name}: NOT FOUND IN PIPELINE")
                    self.errors.append(f"Stage '{stage_name}' (ID: {stage_id}) not found in pipeline")

        except Exception as e:
            print(f"✗ Failed to validate pipeline: {e}\n")
            self.errors.append(f"Pipeline validation failed: {str(e)}")
            return

        print()

    def _print_results(self):
        """Print validation results summary"""
        print("\n" + "="*60)
        print("Validation Results")
        print("="*60 + "\n")

        if self.validated_items:
            print(f"✓ Validated Items ({len(self.validated_items)}):")
            for item in self.validated_items[:10]:  # Show first 10
                print(f"  • {item}")
            if len(self.validated_items) > 10:
                print(f"  ... and {len(self.validated_items) - 10} more")
            print()

        if self.warnings:
            print(f"⚠ Warnings ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"  • {warning}")
            print()

        if self.errors:
            print(f"✗ Errors ({len(self.errors)}):")
            for error in self.errors:
                print(f"  • {error}")
            print()
            print("❌ VALIDATION FAILED - Please fix the errors above")
        else:
            print("✅ ALL VALIDATIONS PASSED")
            print("\nYour GoHighLevel integration is properly configured!")

        print("\n" + "="*60 + "\n")

    def generate_setup_instructions(self) -> str:
        """Generate setup instructions based on missing items"""
        if not self.errors:
            return "Setup is complete!"

        instructions = []
        instructions.append("\n📝 Setup Instructions\n")
        instructions.append("="*60 + "\n")

        # Check for missing custom fields
        missing_fields = [e for e in self.errors if "custom field" in e.lower()]
        if missing_fields:
            instructions.append("1. Create Missing Custom Fields in GoHighLevel:\n")
            instructions.append("   Go to: Settings → Custom Fields → Add Field\n")

            for error in missing_fields:
                field_name = error.split(":")[-1].strip().split("(")[0].strip()
                instructions.append(f"   • {field_name}")

            instructions.append("\n   Field types should match the mapping in ghl_field_mapping.json\n")

        # Check for pipeline issues
        pipeline_errors = [e for e in self.errors if "pipeline" in e.lower() or "stage" in e.lower()]
        if pipeline_errors:
            instructions.append("\n2. Configure Pipeline & Stages:\n")
            instructions.append("   Go to: Opportunities → Settings → Pipelines\n")

            for error in pipeline_errors:
                instructions.append(f"   • {error}")

        # Check for config issues
        config_errors = [e for e in self.errors if "not configured" in e.lower()]
        if config_errors:
            instructions.append("\n3. Update Configuration File:\n")
            instructions.append("   Edit: integrations/ghl_config.py\n")

            for error in config_errors:
                instructions.append(f"   • {error}")

        instructions.append("\n" + "="*60 + "\n")

        return "\n".join(instructions)


def main():
    """Run validation"""

    # First validate configuration
    is_valid, errors = validate_config()
    if not is_valid:
        print("\n❌ Configuration Errors Found:\n")
        for error in errors:
            print(f"  • {error}")
        print("\nPlease update integrations/ghl_config.py with your credentials")
        print("Use ghl_config_example.py as a template\n")
        return

    # Initialize connector
    config = get_config()
    ghl = GoHighLevelConnector(
        api_key=config["api_key"],
        location_id=config["location_id"],
        test_mode=config.get("test_mode", False)
    )

    # Run validation
    validator = GHLSetupValidator(ghl)
    validation_passed = validator.validate_all()

    # Print setup instructions if validation failed
    if not validation_passed:
        print(validator.generate_setup_instructions())
    else:
        print("🎉 Your GoHighLevel integration is ready to use!")
        print("\nNext steps:")
        print("  1. Run example_usage.py to test the integration")
        print("  2. Integrate with your property analysis module")
        print("  3. Set up database for buyer caching and SMS tracking")


if __name__ == "__main__":
    main()
