#  (C) Datadog, Inc. 2022-present
#  All rights reserved
#  Licensed under a 3-clause BSD style license (see LICENSE)

import json
import uuid

from datadog_checks.dev.fs import write_file
from datadog_checks.dev.tooling.commands.console import abort
from datadog_checks.dev.tooling.datastructures import JSONDict
from datadog_checks.dev.tooling.utils import get_manifest_file, load_manifest

# This means the value is either not present in the old manifest, or there's logic needed to compute it
SKIP_IF_FOUND = "SKIP"

# Static text to let users know these values need updating by hand
TODO_FILL_IN = "TODO Please Fill In"

# Validate what manifest versions we can support and what we can upgrade from->to
SUPPORTED_MANIFEST_VERSIONS = ["1.0.0", "2.0.0"]
SUPPORTED_VERSION_UPGRADE_PATHS = {"1.0.0": ["2.0.0"]}

# JSONDict map all v2 fields to their v1 counterparts
# Skipping any fields that need manual intervention of custom logic
V2_TO_V1_MAP = JSONDict(
    {
        "/manifest_version": SKIP_IF_FOUND,
        "/app_id": "/integration_id",
        "/display_on_public_website": "/is_public",
        "/tile": {},
        "/tile/overview": "README.md#Overview",
        "/tile/configuration": "README.md#Setup",
        "/tile/support": "README.md#Support",
        "/tile/changelog": "CHANGELOG.md",
        "/tile/description": "/short_description",
        "/tile/title": "/public_title",
        "/tile/media": [],
        "/tile/classifier_tags": [],
        "/author": {},
        "/author/homepage": "/author/homepage",
        "/author/name": "/author/name",
        "/author/support_email": "/maintainer",
        "/assets": {},
        "/assets/integration": {},
        "/assets/integration/source_type_name": "/display_name",
        "/assets/integration/configuration": {},
        "/assets/integration/configuration/spec": "/assets/configuration/spec",
        "/assets/integration/events": {},
        "/assets/integration/events/creates_events": "/creates_events",
        "/assets/integration/metrics": {},
        "/assets/integration/metrics/prefix": "/metric_prefix",
        "/assets/integration/metrics/check": "/metric_to_check",
        "/assets/integration/metrics/metadata_path": "/assets/metrics_metadata",
        "/assets/integration/service_checks": {},
        "/assets/integration/service_checks/metadata_path": "/assets/service_checks",
        "/assets/integration/process_signatures": "/process_signatures",
        "/assets/dashboards": "/assets/dashboards",
        "/assets/monitors": "/assets/monitors",
        "/assets/saved_views": "/assets/saved_views",
        "/assets/logs": "/assets/logs",
    }
)

OS_TO_CLASSIFIER_TAGS = {
    "linux": "Supported OS::Linux",
    "mac_os": "Supported OS::macOS",
    "windows": "Supported OS::Windows",
}

CATEGORIES_TO_CLASSIFIER_TAGS = {
    "alerting": "Category::Alerting",
    "autodiscovery": "Category::Autodiscovery",
    "automation": "Category::Automation",
    "aws": "Category::AWS",
    "azure": "Category::Azure",
    "caching": "Category::Caching",
    "cloud": "Category::Cloud",
    "collaboration": "Category::Collaboration",
    "compliance": "Category::Compliance",
    "configuration & deployment": "Category::Configuration & Deployment",
    "containers": "Category::Containers",
    "cost management": "Category::Cost Management",
    "data store": "Category::Data Stores",
    "developer tools": "Category::Developer Tools",
    "event management": "Category::Event Management",
    "exceptions": "Category::Exceptions",
    "google cloud": "Category::Google Cloud",
    "incidents": "Category::Incidents",
    "iot": "Category::IoT",
    "isp": "Category::ISP",
    "issue tracking": "Category::Issue Tracking",
    "languages": "Category::Languages",
    "log collection": "Category::Log Collection",
    "marketplace": "Category::Marketplace",
    "messaging": "Category::Messaging",
    "metrics": "Category::Metrics",
    "monitoring": "Category::Monitoring",
    "network": "Category::Network",
    "notification": "Category::Notifications",
    "oracle": "Category::Oracle",
    "orchestration": "Category::Orchestration",
    "os & system": "Category::OS System",
    "processing": "Category::Processing",
    "profiling": "Category::Profiling",
    "provisioning": "Category::Provisioning",
    "security": "Category::Security",
    "snmp": "Category::SNMP",
    "source control": "Category::Source Control",
    "testing": "Category::Testing",
    "web": "Category::Web",
}


def migrate_manifest(repo_name, integration, to_version):
    loaded_manifest = JSONDict(load_manifest(integration))
    manifest_version = loaded_manifest.get_path("/manifest_version")

    if to_version not in SUPPORTED_MANIFEST_VERSIONS:
        abort(f"    Unknown to_version: `{to_version}`. Valid options are: {SUPPORTED_MANIFEST_VERSIONS}")
    if to_version == manifest_version:
        abort(f"    {integration} is already on version `{manifest_version}`")
    if to_version not in SUPPORTED_VERSION_UPGRADE_PATHS.get(manifest_version, []):
        abort(
            f"    Can't migrate from version `{manifest_version}` to version: `{to_version}`. Unsupported upgrade path"
        )

    migrated_manifest = JSONDict()

    # Explicitly set the manifest_version first so it appears at the top of the manifest
    migrated_manifest.set_path("/manifest_version", "2.0.0")

    # Generate and introduce a uuid
    app_uuid = str(uuid.uuid4())
    migrated_manifest.set_path("/app_uuid", app_uuid)

    for key, val in V2_TO_V1_MAP.items():
        if val == SKIP_IF_FOUND:
            continue
        # If the value is a string and is a JSONPath, then load the value from the JSON Path
        elif isinstance(val, str) and val.startswith("/"):
            final_value = loaded_manifest.get_path(val)
        else:
            final_value = val

        # We need to remove any of the underlying "assets" that are just an empty dictionary
        if key in ["/assets/dashboards", "/assets/logs", "/assets/monitors", "/assets/saved_views"] and not final_value:
            continue

        if final_value is not None:
            migrated_manifest.set_path(key, final_value)

    # Update any previously skipped field in which we can use logic to assume the value of
    # Also iterate through any lists to include new/updated fields at each index of the list
    migrated_manifest.set_path("/tile/classifier_tags", TODO_FILL_IN)

    # Retrieve and map all categories from other fields
    classifier_tags = []
    supported_os = loaded_manifest.get_path("/supported_os")
    for os in supported_os:
        os_tag = OS_TO_CLASSIFIER_TAGS.get(os.lower())
        if os_tag:
            classifier_tags.append(os_tag)

    categories = loaded_manifest.get_path("/categories")
    for category in categories:
        category_tag = CATEGORIES_TO_CLASSIFIER_TAGS.get(category.lower())
        if category_tag:
            classifier_tags.append(category_tag)

    # Write the manifest back to disk
    migrated_manifest.set_path("/tile/classifier_tags", classifier_tags)

    # Temporarily required official fields
    if repo_name == "integrations-core":
        migrated_manifest.set_path("/author/name", "Datadog")
        migrated_manifest.set_path("/author/homepage", "https://www.datadoghq.com")
        migrated_manifest.set_path("/author/sales_email", "info@datadoghq.com")
    # Marketplace-only fields
    elif repo_name == "marketplace":
        migrated_manifest.set_path("/author/vendor_id", TODO_FILL_IN)
        migrated_manifest.set_path("/author/sales_email", loaded_manifest.get_path("/terms/legal_email"))

        migrated_manifest.set_path("/pricing", loaded_manifest.get_path("/pricing"))
        migrated_manifest.set_path("/legal_terms", {})
        migrated_manifest.set_path("/legal_terms/eula", loaded_manifest.get_path("/terms/eula"))

        for idx, _ in enumerate(migrated_manifest.get_path("/pricing") or []):
            migrated_manifest.set_path(f"/pricing/{idx}/product_id", TODO_FILL_IN)
            migrated_manifest.set_path(f"/pricing/{idx}/short_description", TODO_FILL_IN)
            migrated_manifest.set_path(f"/pricing/{idx}/includes_assets", True)

    write_file(get_manifest_file(integration), f"{json.dumps(migrated_manifest, indent=2)}\n")
