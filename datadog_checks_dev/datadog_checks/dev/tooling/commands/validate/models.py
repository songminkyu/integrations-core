# (C) Datadog, Inc. 2021-present
# All rights reserved
# Licensed under a 3-clause BSD style license (see LICENSE)
import click

from datadog_checks.dev.fs import (
    chdir,
    dir_exists,
    ensure_parent_dir_exists,
    file_exists,
    path_join,
    read_file,
    read_file_lines,
    write_file_lines,
)
from datadog_checks.dev.tooling.commands.console import (
    CONTEXT_SETTINGS,
    abort,
    annotate_display_queue,
    annotate_error,
    echo_debug,
    echo_failure,
    echo_info,
    echo_success,
)
from datadog_checks.dev.tooling.configuration import ConfigSpec
from datadog_checks.dev.tooling.configuration.consumers import ModelConsumer
from datadog_checks.dev.tooling.constants import get_root
from datadog_checks.dev.tooling.testing import process_checks_option
from datadog_checks.dev.tooling.utils import (
    CUSTOM_FILES,
    complete_valid_checks,
    get_config_models_documentation,
    get_license_header,
    get_models_location,
    get_version_string,
)

LICENSE_HEADER = "(C) Datadog, Inc."

INTEGRATIONS_WITHOUT_MODELS = {
    'snmp',  # Deprecated
    'tokumx',  # Python 2 only
}


def standardize_new_lines(lines):
    # If a new line is at the start or end of a line, remove it and add it to the list
    # This way a file is the same regardless of how newlines are added when it's generated
    result = []
    for line in lines:
        if line == '\n':
            result.append(line)
        elif line.endswith('\n'):
            result.append(line[:-1])
            result.append('\n')
        elif line.startswith('\n'):
            result.append('\n')
            result.append(line[1:])
        else:
            result.append(line)
    return result


def content_matches(current_model_file_lines, expected_model_file_lines):
    all_current_lines = standardize_new_lines(current_model_file_lines)
    all_expected_lines = standardize_new_lines(expected_model_file_lines)

    return all_current_lines == all_expected_lines


@click.command(context_settings=CONTEXT_SETTINGS, short_help='Validate configuration data models')
@click.argument('check', shell_complete=complete_valid_checks, required=False)
@click.option('--sync', '-s', is_flag=True, help='Generate data models based on specifications')
@click.option('--verbose', '-v', is_flag=True, help='Verbose mode')
@click.pass_context
def models(ctx, check, sync, verbose):
    """Validate configuration data models.

    If `check` is specified, only the check will be validated, if check value is 'changed' will only apply to changed
    checks, an 'all' or empty `check` value will validate all README files.
    """
    root = get_root()
    is_community_check = ctx.obj['repo_choice'] not in ('core', 'internal')
    is_core_check = ctx.obj['repo_choice'] == 'core'

    checks = set(process_checks_option(check, source='valid_checks', extend_changed=True))

    echo_info(f"Validating data models for {len(checks)} checks ...")

    specs_failed = {}
    files_failed = {}
    num_files = 0

    license_header_lines = get_license_header().splitlines(True) + ['\n', '\n']
    documentation_header_lines = get_config_models_documentation().splitlines(True) + ['\n']

    code_formatter = ModelConsumer.create_code_formatter()

    if is_core_check:
        checks = checks.difference(INTEGRATIONS_WITHOUT_MODELS)

    for check in sorted(checks):
        display_queue = {}
        if check == 'datadog_checks_base':
            spec_path = path_join(root, 'datadog_checks_base', 'tests', 'models', 'data', 'spec.yaml')
            source = 'test'
            version = '0.0.1'
        else:
            spec_path = path_join(root, check, 'assets', 'configuration', 'spec.yaml')
            if not file_exists(spec_path):
                echo_debug(f"Skipping validation for check: {check}; 'spec.yaml' file doesn't exist")
                continue

            source = check
            version = get_version_string(check)

        spec_file = read_file(spec_path)
        spec = ConfigSpec(spec_file, source=source, version=version)
        spec.load()

        if spec.errors:
            annotate_error(spec_path, '\n'.join(spec.errors))
            specs_failed[spec_path] = True
            echo_info(f'{check}:')
            for error in spec.errors:
                echo_failure(error, indent=True)
            continue

        if check == 'datadog_checks_base':
            models_location = path_join(root, 'datadog_checks_base', 'tests', 'models', 'config_models')
        else:
            models_location = get_models_location(check)

            if not sync and not dir_exists(models_location) and not is_core_check:
                continue

        model_consumer = ModelConsumer(spec.data, code_formatter)

        # So formatters see config files
        with chdir(root):
            model_definitions = model_consumer.render()

        model_files = model_definitions.get(f'{source}.yaml')
        if not model_files:
            continue

        for model_file, (contents, errors) in model_files.items():
            check_display_queue = []
            num_files += 1

            model_file_path = path_join(models_location, model_file)
            if errors:
                files_failed[model_file_path] = True
                for error in errors:
                    check_display_queue.append((echo_failure, error))
                continue

            generated_model_file_lines = contents.splitlines(True)
            current_model_file_lines = []
            expected_model_file_lines = []

            if file_exists(model_file_path):
                if not contents:
                    continue

                current_model_file_lines = read_file_lines(model_file_path)

                if model_file in CUSTOM_FILES and (len(current_model_file_lines) + 1) > len(license_header_lines):
                    # validators.py and deprecations.py are custom files, they should only be rendered the first time
                    continue

            if not is_community_check:
                expected_model_file_lines.extend(license_header_lines)

            if model_file not in CUSTOM_FILES:
                expected_model_file_lines.extend(documentation_header_lines)

            expected_model_file_lines.extend(generated_model_file_lines)

            # If we're re-generating a file, we should ensure we do not change the license date
            # We also want to handle the case where there is no license header
            if not is_community_check:
                if len(current_model_file_lines) > 0 and LICENSE_HEADER in current_model_file_lines[0]:
                    expected_model_file_lines[0] = current_model_file_lines[0]

            if not current_model_file_lines or not content_matches(current_model_file_lines, expected_model_file_lines):
                if sync:
                    check_display_queue.append(
                        (
                            echo_info,
                            f'Writing data model file to `{model_file_path}`',
                        )
                    )
                    ensure_parent_dir_exists(model_file_path)
                    write_file_lines(model_file_path, expected_model_file_lines)
                else:
                    files_failed[model_file_path] = True
                    check_display_queue.append(
                        (
                            echo_failure,
                            f'File `{model_file}` is not in sync, run "ddev validate models {check} -s"',
                        )
                    )

            if not check_display_queue and verbose:
                check_display_queue.append((echo_info, f"Valid spec: {model_file}"))

            display_queue[model_file_path] = check_display_queue

        if display_queue:
            echo_info(f'{check}:')
            for model_path, queue in display_queue.items():
                annotate_display_queue(model_path, queue)
                for func, message in queue:
                    func(message, indent=True)

    specs_failed_count = len(specs_failed)
    files_failed_count = len(files_failed)
    files_passed_count = num_files - files_failed_count

    if specs_failed_count or files_failed_count:
        click.echo()

    if specs_failed_count:
        echo_failure(f'Specs with errors: {specs_failed}')

    if files_failed_count:
        echo_failure(f'Files with errors: {files_failed_count}')

    if files_passed_count:
        if specs_failed_count or files_failed_count:
            echo_success(f'Files valid: {files_passed_count}')
        else:
            echo_success(f'All {num_files} data model files are in sync!')

    if specs_failed_count or files_failed_count:
        abort()
