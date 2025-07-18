# (C) Datadog, Inc. 2018-present
# All rights reserved
# Licensed under a 3-clause BSD style license (see LICENSE)
import os
from datetime import datetime, timezone
from operator import attrgetter
from uuid import uuid4

from datadog_checks.dev.fs import (
    create_file,
    dir_exists,
    ensure_parent_dir_exists,
    path_join,
    read_file,
    read_file_binary,
    write_file,
    write_file_binary,
)

from .constants import REPO_CHOICES, integration_type_links
from .utils import (
    get_config_models_documentation,
    get_license_header,
    kebab_case_name,
    normalize_display_name,
    normalize_package_name,
    normalize_project_name,
)

TEMPLATES_DIR = path_join(os.path.dirname(os.path.abspath(__file__)), 'templates', 'integration')
BINARY_EXTENSIONS = ('.png',)
SIMPLE_NAME = r'^\w+$'
EXCLUDE_TEMPLATES = {"marketplace"}


class TemplateType(object):
    def __init__(self, name, templates_dir):
        self.name = name
        self.path = os.path.join(templates_dir, name)
        readme_path = os.path.join(self.path, "README.md")
        if os.path.exists(readme_path):
            with open(readme_path) as fh:
                self.description = fh.read().strip()
        else:
            self.description = "No description yet. Please reach out to agent-integrations to add one."


def get_valid_templates():
    templates = [
        TemplateType(template, TEMPLATES_DIR)
        for template in os.listdir(TEMPLATES_DIR)
        if template not in EXCLUDE_TEMPLATES
    ]
    return sorted(templates, key=attrgetter('name'))


def prefill_template_fields_for_check_only(manifest: dict, normalized_integration_name: str) -> dict:
    author = manifest.get("author", {}).get("name")
    if author is not None:
        author = normalize_display_name(author)
    check_name = normalize_package_name(f"{author}_{normalized_integration_name}") if author is not None else None
    return {
        k: v
        for k, v in {
            'author_name': author,
            'check_name': check_name,
            'email': manifest.get("author", {}).get("support_email"),
            'homepage': manifest.get("author", {}).get("homepage"),
            'sales_email': manifest.get("author", {}).get("sales_email"),
        }.items()
        if v is not None
    }


def construct_template_fields(integration_name, repo_choice, integration_type, **kwargs):
    normalized_integration_name = normalize_package_name(integration_name)
    check_name_kebab = kebab_case_name(integration_name)

    third_party_install_info = f"""\
To install the {integration_name} check on your host:


1. Install the [developer toolkit]
(https://docs.datadoghq.com/developers/integrations/python/)
 on any machine.

2. Run `ddev release build {normalized_integration_name}` to build the package.

3. [Download the Datadog Agent][2].

4. Upload the build artifact to any host with an Agent and
 run `datadog-agent integration install -w
 path/to/{normalized_integration_name}/dist/<ARTIFACT_NAME>.whl`."""
    if integration_type == 'check_only':
        # check_name, author, email come from kwargs due to prefill
        check_name = ''
        author = ''
        email = ''
        email_packages = ''
        install_info = third_party_install_info
        # Static fields
        license_header = ''
        support_type = 'partner'
        integration_links = ''
    if repo_choice == 'core':
        check_name = normalized_integration_name
        author = 'Datadog'
        email = 'help@datadoghq.com'
        email_packages = 'packages@datadoghq.com'
        install_info = (
            'The {integration_name} check is included in the [Datadog Agent][2] package.\n'
            'No additional installation is needed on your server.'.format(integration_name=integration_name)
        )
        license_header = get_license_header()
        support_type = 'core'
        integration_links = integration_type_links.get(integration_type).format(
            name=normalized_integration_name, repository="integrations-core"
        )
    elif repo_choice == 'integrations-internal-core':
        check_name = normalized_integration_name
        author = 'Datadog'
        email = 'help@datadoghq.com'
        email_packages = ''
        install_info = ''
        license_header = ''
        support_type = 'core'
        integration_links = integration_type_links.get(integration_type).format(
            name=normalized_integration_name, repository="integrations-internal-core"
        )
    elif repo_choice == 'marketplace':
        check_name = normalize_package_name(f"{kwargs.get('author')}_{normalized_integration_name}")
        # Updated by the kwargs passed in
        author = ''
        email = ''
        email_packages = ''
        install_info = third_party_install_info
        # Static fields
        license_header = ''
        support_type = 'partner'
        integration_links = ''
    else:
        check_name = normalized_integration_name
        author = 'U.N. Owen'
        email = email_packages = 'friend@datadog.community'
        install_info = third_party_install_info
        license_header = ''
        support_type = 'contrib'
        integration_links = integration_type_links.get(integration_type)

        if repo_choice == 'internal':
            integration_links = integration_links.format(
                name=normalized_integration_name, repository="integrations-internal"
            )
        else:
            integration_links = integration_links.format(
                name=normalized_integration_name, repository="integrations-extras"
            )

    config = {
        'author': author,
        'auto_install': 'false' if repo_choice == 'marketplace' or integration_type == 'metrics_crawler' else 'true',
        'check_class': f"{''.join(part.capitalize() for part in normalized_integration_name.split('_'))}Check",
        'check_name': check_name,
        'project_name': normalize_project_name(normalized_integration_name),
        'documentation': get_config_models_documentation(),
        'integration_name': integration_name,
        'check_name_kebab': check_name_kebab,
        'email': email,
        'email_packages': email_packages,
        'app_uuid': uuid4(),
        'license_header': license_header,
        'install_info': install_info,
        'repo_choice': repo_choice,
        'repo_name': REPO_CHOICES.get(repo_choice, ''),
        'support_type': support_type,
        'integration_links': integration_links,
        # Source Type IDs are unique-per-integration integers
        # Based on current timestamp with subtraction to start the IDs at around a few million, allowing room to grow.
        "source_type_id": int(datetime.now(timezone.utc).timestamp()) - 1700000000,
    }
    config.update(kwargs)

    return config


def create_template_files(template_name, new_root, config, repo_choice, read=False):
    files = []

    template_root = path_join(TEMPLATES_DIR, template_name)
    if not dir_exists(template_root):
        return files

    for root, _, template_files in os.walk(template_root):
        for template_file in template_files:
            if template_file.endswith('1.added') and repo_choice != 'core':
                continue
            if template_root == root and template_file == "README.md":
                continue
            if not template_file.endswith(('.pyc', '.pyo')):
                if template_file == 'README.md' and config.get('support_type') in ('partner', 'contrib'):
                    # Custom README for the marketplace/partner support_type integrations
                    if config.get('support_type') == 'partner':
                        template_path = path_join(TEMPLATES_DIR, 'marketplace/', 'README.md')
                        file_path = path_join(config.get('check_name'), "README.md")

                    # Custom README for tile apps
                    elif config.get('support_type') == 'contrib':
                        template_path = path_join(TEMPLATES_DIR, 'tile/{check_name}', 'README.md')
                        file_path = path_join(config.get('check_name'), "README.md")
                    else:
                        template_path = path_join(root, template_file)
                        file_path = template_path.replace(template_root, '')

                # Use a special readme file for media carousel information
                # .gitkeep currently only used for images, but double check anyway
                elif template_file == '.gitkeep' and 'images' in root:
                    image_guidelines = 'IMAGES_README.md'
                    template_path = path_join(TEMPLATES_DIR, 'marketplace/', image_guidelines)
                    file_path = path_join(config.get('check_name'), "images", image_guidelines)
                else:
                    template_path = path_join(root, template_file)
                    file_path = os.path.relpath(template_path, template_root)
                file_path = os.path.join(new_root, file_path.format(**config))
                files.append(File(file_path, template_path, config, read=read))

    return files


class File(object):
    def __init__(self, file_path, template_path, config, read=False):
        self.file_path = file_path
        self.template_path = template_path
        self.config = config
        self.binary = template_path.endswith(BINARY_EXTENSIONS)
        self._read = read_file_binary if self.binary else read_file
        self._write = write_file_binary if self.binary else write_file
        self.contents = None

        if read:
            self.read()

    def read(self):
        contents = self._read(self.template_path)
        if self.binary:
            self.contents = contents
        else:
            self.contents = contents.format(**self.config)

    def write(self):
        if self.contents is None:
            create_file(self.file_path)
        else:
            ensure_parent_dir_exists(self.file_path)
            self._write(self.file_path, self.contents)
