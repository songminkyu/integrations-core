# (C) Datadog, Inc. 2023-present
# All rights reserved
# Licensed under a 3-clause BSD style license (see LICENSE)
from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING

import click

if TYPE_CHECKING:
    from ddev.cli.application import Application
    from ddev.integration.core import Integration
    from ddev.utils.fs import Path


def fix_coverage_report(report_file: Path):
    target_dir = report_file.parent.name
    report = report_file.read_bytes()

    # Make every target's `tests` directory path unique so they don't get combined in UI
    report = report.replace(b'"tests/', f'"{target_dir}/tests/'.encode('utf-8'))

    report_file.write_bytes(report)


epilog = '''
Examples

\b
List possible environments for postgres:
ddev test -l postgres

\b
Run only unit tests:
ddev test postgres:py3.11-9.6 -- -m unit

\b
Run specific test in multiple environments:
ddev test postgres:py3.11-9.6,py3.11-16.0 -- -k test_my_special_test
'''


def on_error_lint_callback(app: Application) -> Callable[[int, str], None]:
    def callback(code: int, stdout: str):
        output = "Linting failed. "
        if "`--unsafe-fixes`" in stdout:
            output += (
                "To fix any errors, run 'ddev test --fmt-unsafe'. "
                "This will fix even those errors marked as unsafe by ruff. "
                "Make sure that these fixes do not have any side effects."
            )
        else:
            output += "To fix any errors, run 'ddev test --fmt'."

        app.display_warning(output)

    return callback


def on_error_fmt_callback(app: Application) -> Callable[[int, str], None]:
    def callback(code: int, stdout: str):
        if "`--unsafe-fixes`" in stdout:
            app.display_warning(
                "Some formatting errors are still found that could be fixed with unsafe fixes. "
                "You can try running 'ddev test --fmt-unsafe' to fix them."
            )
        else:
            app.display_warning(
                "Some formatting errors are still found for which ruff has no fixes available. "
                "You would need to fix them manually."
            )

    return callback


@click.command(epilog=epilog)
@click.argument('target_spec', required=False)
@click.argument('pytest_args', nargs=-1)
@click.option('--lint', '-s', is_flag=True, help='Run only lint & style checks')
@click.option('--lint-unsafe', '-su', is_flag=True, help='Show unsafe fixes proposed by the linter')
@click.option('--fmt', '-fs', is_flag=True, help='Fix formatting and linting errors')
@click.option('--fmt-unsafe', '-fsu', is_flag=True, help='Fix formatting and linting errors including unsafe fixes')
@click.option('--bench', '-b', is_flag=True, help='Run only benchmarks')
@click.option('--latest', is_flag=True, help='Only verify support of new product versions')
@click.option('--cov', '-c', 'coverage', is_flag=True, help='Measure code coverage')
@click.option(
    '--compat', is_flag=True, help='Check compatibility with the minimum allowed Agent version. Implies --recreate.'
)
@click.option('--ddtrace', is_flag=True, envvar='DDEV_TEST_ENABLE_TRACING', help='Enable tracing during test execution')
@click.option('--memray', is_flag=True, help='Measure memory usage during test execution')
@click.option('--recreate', '-r', is_flag=True, help='Recreate environments from scratch')
@click.option('--list', '-l', 'list_envs', is_flag=True, help='Show available test environments')
@click.option('--python-filter', envvar='PYTHON_FILTER', hidden=True)
@click.option('--junit', is_flag=True, hidden=True)
@click.option('--hide-header', is_flag=True, hidden=True)
@click.option('--e2e', is_flag=True, hidden=True)
@click.pass_obj
def test(
    app: Application,
    target_spec: str | None,
    pytest_args: tuple[str, ...],
    lint: bool,
    lint_unsafe: bool,
    fmt: bool,
    fmt_unsafe: bool,
    bench: bool,
    latest: bool,
    coverage: bool,
    compat: bool,
    ddtrace: bool,
    memray: bool,
    recreate: bool,
    list_envs: bool,
    python_filter: str | None,
    junit: bool,
    hide_header: bool,
    e2e: bool,
):
    """
    Run unit and integration tests.

    Please see these docs to know how to pass TARGET_SPEC and PYTEST_ARGS:

    \b
    https://datadoghq.dev/integrations-core/testing/
    """
    import json
    import os
    import sys

    from ddev.testing.constants import EndToEndEnvVars, TestEnvVars
    from ddev.testing.hatch import get_hatch_env_vars
    from ddev.utils.ci import running_in_ci

    if target_spec is None:
        target_spec = 'changed'

    target_name, _, environments = target_spec.partition(':')

    # target name -> target
    targets: dict[str, Integration] = {}
    if target_name == 'changed':
        for integration in app.repo.integrations.iter_changed():
            if integration.is_testable:
                targets[integration.name] = integration
    elif target_name == 'all':
        for integration in app.repo.integrations.iter_testable('all'):
            targets[integration.name] = integration
    else:
        try:
            integration = app.repo.integrations.get(target_name)
        except OSError:
            app.abort(f'Unknown target: {target_name}')

        if integration.is_testable:
            targets[integration.name] = integration

    if not targets:
        if target_name == 'changed':
            app.display_info('No changed testable targets found')
            return
        else:
            app.abort('No testable targets found')

    if list_envs:
        multiple_targets = len(targets) > 1
        for target in targets.values():
            with target.path.as_cwd():
                if multiple_targets:
                    app.display_header(target.display_name)

                app.platform.check_command([sys.executable, '-m', 'hatch', 'env', 'show'])

        return

    in_ci = running_in_ci()

    # Also recreate the environment in the `compat` mode to make sure we are using the right base
    # check version.
    if compat:
        recreate = True

    global_env_vars: dict[str, str] = get_hatch_env_vars(verbosity=app.verbosity + 1)

    # Disable unnecessary output from Docker
    global_env_vars['DOCKER_CLI_HINTS'] = 'false'

    api_key = app.config.org.config.get('api_key')
    if api_key and not (lint or fmt):
        global_env_vars['DD_API_KEY'] = api_key

    # Only enable certain functionality when running standard tests
    standard_tests = not (lint or lint_unsafe or fmt or fmt_unsafe or bench or latest)

    # Keep track of environments so that they can first be removed if requested
    chosen_environments = []

    # Define the on_error callback
    on_error = None

    base_command = [sys.executable, '-m', 'hatch', 'env', 'run']
    if environments and not standard_tests:
        app.abort('Cannot specify environments when using specific functionality like linting')
    elif lint:
        chosen_environments.append('lint')
        base_command.extend(('--env', 'lint', '--', 'all'))
        on_error = on_error_lint_callback(app)
    elif lint_unsafe:
        chosen_environments.append('lint')
        base_command.extend(('--env', 'lint', '--', 'style-unsafe'))
    elif fmt:
        chosen_environments.append('lint')
        base_command.extend(('--env', 'lint', '--', 'fmt'))
        on_error = on_error_fmt_callback(app)
    elif fmt_unsafe:
        chosen_environments.append('lint')
        base_command.extend(('--env', 'lint', '--', 'fmt-unsafe'))
        on_error = on_error_fmt_callback(app)
    elif bench:
        filter_data = json.dumps({'benchmark-env': True})
        base_command.extend(('--filter', filter_data, '--', 'benchmark'))
    elif latest:
        filter_data = json.dumps({'latest-env': True})
        base_command.extend(('--filter', filter_data, '--', 'test', '--run-latest-metrics'))
    else:
        if environments:
            for env_name in environments.split(','):
                chosen_environments.append(env_name)
                base_command.extend(('--env', env_name))
        else:
            chosen_environments.append('default')
            base_command.append('--ignore-compat')

        if python_filter:
            filter_data = json.dumps({'python': python_filter})
            base_command.extend(('--filter', filter_data))

        base_command.extend(('--', 'test-cov' if coverage else 'test'))

        if app.verbosity <= 0:
            base_command.extend(('--tb', 'short'))

        if memray:
            if app.platform.windows:
                app.abort('Memory profiling with `memray` is not supported on Windows')

            base_command.append('--memray')

        if e2e:
            # Convert pytest_args to a list if it's a tuple
            pytest_args_list = list(pytest_args) if isinstance(pytest_args, tuple) else pytest_args

            # Initialize a list to hold indices of '-m' options and their values to be removed
            indices_to_remove = []
            marker_values = []

            # Iterate over pytest_args_list to find '-m' or '--markers' options and their values
            for i, arg in enumerate(pytest_args_list):
                if arg in ('-m', '--markers') and i + 1 < len(pytest_args_list):
                    indices_to_remove.extend([i, i + 1])
                    marker_values.append(pytest_args_list[i + 1])

            # Reverse sort indices_to_remove to avoid index shifting issues during removal
            indices_to_remove.sort(reverse=True)

            # Remove the '-m' options and their values from pytest_args_list
            for index in indices_to_remove:
                pytest_args_list.pop(index)

            # After removing the '-m' options and their values
            # Convert the modified pytest_args_list back to a tuple
            pytest_args = tuple(pytest_args_list)

            # Construct the combined marker expression with extracted marker values and 'e2e'
            combined_marker = " and ".join(marker_values) + " and e2e" if marker_values else "e2e"
            base_command.extend(('-m', combined_marker))
            global_env_vars[EndToEndEnvVars.PARENT_PYTHON] = sys.executable

    app.display_debug(f'Targets: {", ".join(targets)}')
    for target in targets.values():
        if not hide_header:
            app.display_header(target.display_name)

        command = base_command.copy()
        env_vars = global_env_vars.copy()

        if standard_tests:
            if ddtrace and (target.is_integration or target.name == 'datadog_checks_base'):
                command.append('--ddtrace')
                env_vars['DDEV_TRACE_ENABLED'] = 'true'
                env_vars['DD_PROFILING_ENABLED'] = 'true'
                env_vars['DD_SERVICE'] = os.environ.get('DD_SERVICE', 'ddev-integrations')
                env_vars['DD_ENV'] = os.environ.get('DD_ENV', 'ddev-integrations')

            if junit:
                # In order to handle multiple environments the report files must contain the environment name.
                # Hatch injects the `HATCH_ENV_ACTIVE` environment variable, see:
                # https://hatch.pypa.io/latest/plugins/environment/reference/#hatch.env.plugin.interface.EnvironmentInterface.get_env_vars
                command.extend(('--junit-xml', f'junit/test-{"e2e" if e2e else "unit"}-$HATCH_ENV_ACTIVE.xml'))
                # Test results class prefix
                command.extend(('--junit-prefix', target.name))

            if (
                compat
                and target.is_package
                and target.is_integration
                and target.minimum_base_package_version is not None
            ):
                env_vars[TestEnvVars.BASE_PACKAGE_VERSION] = target.minimum_base_package_version

        command.extend(pytest_args)

        with target.path.as_cwd(env_vars=env_vars):
            app.display_debug(f'Command: {command}')

            if recreate:
                if bench or latest:
                    variable = 'benchmark-env' if bench else 'latest-env'
                    env_data = json.loads(
                        app.platform.check_command_output([sys.executable, '-m', 'hatch', 'env', 'show', '--json'])
                    )
                    for env_name, env_config in env_data.items():
                        if env_config.get(variable, False):
                            app.platform.check_command([sys.executable, '-m', 'hatch', 'env', 'remove', env_name])
                else:
                    for env_name in chosen_environments:
                        app.platform.check_command([sys.executable, '-m', 'hatch', 'env', 'remove', env_name])

            # We use check_command_output to get the output of the command on the on_error callback
            # And force color to be enabled
            env = os.environ.copy()
            env['FORCE_COLOR'] = '1'
            app.platform.check_command_output(command, on_error=on_error, print_output=True, env=env)
            if standard_tests and coverage:
                app.display_header('Coverage report')
                app.platform.check_command([sys.executable, '-m', 'coverage', 'report', '--rcfile=../.coveragerc'])

                if in_ci:
                    app.platform.check_command(
                        [sys.executable, '-m', 'coverage', 'xml', '-i', '--rcfile=../.coveragerc']
                    )
                    fix_coverage_report(target.path / 'coverage.xml')
                else:
                    (target.path / '.coverage').remove()

            if compat:
                # We destroy the environment since we edited it
                for env_name in chosen_environments:
                    app.platform.check_command([sys.executable, '-m', 'hatch', 'env', 'remove', env_name])
