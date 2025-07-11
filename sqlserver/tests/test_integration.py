# (C) Datadog, Inc. 2018-present
# All rights reserved
# Licensed under a 3-clause BSD style license (see LICENSE)
import logging
import re
from copy import copy, deepcopy

import mock
import pytest

from datadog_checks.sqlserver import SQLServer
from datadog_checks.sqlserver.__about__ import __version__
from datadog_checks.sqlserver.connection import SQLConnectionError
from datadog_checks.sqlserver.const import (
    DATABASE_INDEX_METRICS,
    ENGINE_EDITION_SQL_DATABASE,
    ENGINE_EDITION_STANDARD,
    INSTANCE_METRICS_DATABASE,
    INSTANCE_METRICS_DATABASE_SINGLE,
    STATIC_INFO_ENGINE_EDITION,
    STATIC_INFO_MAJOR_VERSION,
    STATIC_INFO_SERVERNAME,
    STATIC_INFO_VERSION,
    TABLE_SIZE_METRICS,
)

from .common import (
    CHECK_NAME,
    CUSTOM_METRICS,
    EXPECTED_DEFAULT_METRICS,
    OPERATION_TIME_METRIC_NAME,
    assert_metrics,
    get_operation_time_metrics,
)
from .conftest import DEFAULT_TIMEOUT
from .utils import always_on, not_windows_ci, windows_ci

try:
    import pyodbc
except ImportError:
    pyodbc = None


@pytest.mark.integration
@pytest.mark.usefixtures('dd_environment')
def test_check_invalid_password(aggregator, dd_run_check, init_config, instance_docker):
    instance_docker['password'] = 'FOO'
    sqlserver_check = SQLServer(CHECK_NAME, init_config, [instance_docker])

    with pytest.raises(SQLConnectionError) as excinfo:
        sqlserver_check.initialize_connection()
        sqlserver_check.check(instance_docker)
    aggregator.assert_service_check(
        'sqlserver.can_connect',
        status=sqlserver_check.CRITICAL,
        tags=[
            'sqlserver_host:{}'.format(sqlserver_check.resolved_hostname),
            'db:master',
            'connection_host:{}'.format(instance_docker.get('host')),
        ]
        + sqlserver_check._config.tags,
        message=re.escape(str(excinfo.value)),
    )


@pytest.mark.integration
@pytest.mark.usefixtures('dd_environment')
@pytest.mark.parametrize('dbm_enabled', [True, False, 'true', 'false', None])
def test_check_dbm_enabled_config(aggregator, dd_run_check, init_config, instance_docker, dbm_enabled):
    if dbm_enabled is not None:
        instance_docker['dbm'] = dbm_enabled
    sqlserver_check = SQLServer(CHECK_NAME, init_config, [instance_docker])
    assert isinstance(sqlserver_check._config.dbm_enabled, bool)


@pytest.mark.integration
@pytest.mark.usefixtures('dd_environment')
@pytest.mark.parametrize(
    'database_autodiscovery,dbm_enabled', [(True, True), (True, False), (False, True), (False, False)]
)
def test_check_docker(aggregator, dd_run_check, init_config, instance_docker, database_autodiscovery, dbm_enabled):
    instance_docker['database_autodiscovery'] = database_autodiscovery
    # test that all default integration metrics are sent regardless of
    # if dbm is enabled or not.
    instance_docker['dbm'] = dbm_enabled
    # no need to assert metrics that are emitted from the dbm portion of the
    # integration in this check as they are all internal
    instance_docker['query_metrics'] = {'enabled': False}
    instance_docker['procedure_metrics'] = {'enabled': False}
    instance_docker['query_activity'] = {'enabled': False}
    instance_docker['collect_settings'] = {'enabled': False}
    instance_docker['agent_jobs'] = {'enabled': False}
    autodiscovery_dbs = ['master', 'msdb', 'datadog_test-1']
    if database_autodiscovery:
        instance_docker['autodiscovery_include'] = autodiscovery_dbs
    sqlserver_check = SQLServer(CHECK_NAME, init_config, [instance_docker])
    dd_run_check(sqlserver_check)
    expected_check_tags = sqlserver_check._config.tags + [
        "database_hostname:{}".format("stubbed.hostname"),
        "database_instance:{}".format("stubbed.hostname"),
        "dd.internal.resource:database_instance:{}".format("stubbed.hostname"),
        "sqlserver_servername:{}".format(sqlserver_check.static_info_cache.get(STATIC_INFO_SERVERNAME)),
    ]
    expected_service_tags = expected_check_tags + [
        'connection_host:{}'.format(instance_docker.get('host')),
        'sqlserver_host:{}'.format(sqlserver_check.resolved_hostname),
        'db:master',
    ]
    assert_metrics(
        instance_docker,
        aggregator,
        check_tags=expected_check_tags,
        service_tags=expected_service_tags,
        dbm_enabled=dbm_enabled,
        hostname=sqlserver_check.resolved_hostname,
        database_autodiscovery=database_autodiscovery,
        dbs=autodiscovery_dbs,
    )


@pytest.mark.integration
@pytest.mark.usefixtures('dd_environment')
def test_check_stored_procedure(aggregator, dd_run_check, init_config, instance_docker):
    proc = 'pyStoredProc'
    sp_tags = "foo:bar,baz:qux"
    instance_docker['stored_procedure'] = proc

    sqlserver_check = SQLServer(CHECK_NAME, init_config, [instance_docker])
    dd_run_check(sqlserver_check)

    expected_tags = (
        sqlserver_check._config.tags
        + [
            "database_hostname:{}".format("stubbed.hostname"),
            "database_instance:{}".format("stubbed.hostname"),
            "dd.internal.resource:database_instance:{}".format("stubbed.hostname"),
            "sqlserver_servername:{}".format(sqlserver_check.static_info_cache.get(STATIC_INFO_SERVERNAME)),
        ]
        + sp_tags.split(',')
    )
    aggregator.assert_metric('sql.sp.testa', value=100, tags=expected_tags, count=1)
    aggregator.assert_metric('sql.sp.testb', tags=expected_tags, count=2)


@pytest.mark.integration
@pytest.mark.usefixtures('dd_environment')
def test_check_stored_procedure_proc_if(aggregator, dd_run_check, init_config, instance_docker):
    proc = 'pyStoredProc'
    proc_only_fail = "select cntr_type from sys.dm_os_performance_counters where counter_name in ('FOO');"

    instance_docker['proc_only_if'] = proc_only_fail
    instance_docker['stored_procedure'] = proc

    sqlserver_check = SQLServer(CHECK_NAME, init_config, [instance_docker])
    dd_run_check(sqlserver_check)

    # apply a proc check that will never fail and assert that the metrics remain unchanged
    assert len(aggregator._metrics) == 0


@pytest.mark.integration
@pytest.mark.usefixtures('dd_environment')
def test_custom_metrics_object_name(aggregator, dd_run_check, init_config_object_name, instance_docker):
    sqlserver_check = SQLServer(CHECK_NAME, init_config_object_name, [instance_docker])
    dd_run_check(sqlserver_check)
    instance_tags = (
        sqlserver_check._config.tags
        + [
            "database_hostname:{}".format("stubbed.hostname"),
            "database_instance:{}".format("stubbed.hostname"),
            "dd.internal.resource:database_instance:{}".format("stubbed.hostname"),
            "sqlserver_servername:{}".format(sqlserver_check.static_info_cache.get(STATIC_INFO_SERVERNAME)),
        ]
        + ['optional_tag:tag1']
    )

    aggregator.assert_metric('sqlserver.cache.hit_ratio', tags=instance_tags, count=1)
    aggregator.assert_metric('sqlserver.broker_activation.tasks_running', tags=instance_tags, count=1)


@pytest.mark.integration
@pytest.mark.usefixtures('dd_environment')
def test_custom_metrics_alt_tables(aggregator, dd_run_check, init_config_alt_tables, instance_docker):
    instance_docker['include_task_scheduler_metrics'] = False

    sqlserver_check = SQLServer(CHECK_NAME, init_config_alt_tables, [instance_docker])
    dd_run_check(sqlserver_check)
    instance_tags = sqlserver_check._config.tags + [
        "database_hostname:{}".format("stubbed.hostname"),
        "database_instance:{}".format("stubbed.hostname"),
        "dd.internal.resource:database_instance:{}".format("stubbed.hostname"),
        "sqlserver_servername:{}".format(sqlserver_check.static_info_cache.get(STATIC_INFO_SERVERNAME)),
    ]

    aggregator.assert_metric('sqlserver.LCK_M_S.max_wait_time_ms', tags=instance_tags, count=1)
    aggregator.assert_metric('sqlserver.LCK_M_S.signal_wait_time_ms', tags=instance_tags, count=1)
    aggregator.assert_metric(
        'sqlserver.MEMORYCLERK_SQLGENERAL.virtual_memory_committed_kb',
        tags=['memory_node_id:0'] + instance_tags,
        count=1,
    )
    aggregator.assert_metric(
        'sqlserver.MEMORYCLERK_SQLGENERAL.virtual_memory_reserved_kb',
        tags=['memory_node_id:0'] + instance_tags,
        count=1,
    )

    # check a second time for io metrics to be processed
    dd_run_check(sqlserver_check)

    aggregator.assert_metric('sqlserver.io_file_stats.num_of_reads')
    aggregator.assert_metric('sqlserver.io_file_stats.num_of_writes')


@not_windows_ci
@pytest.mark.integration
@pytest.mark.usefixtures('dd_environment')
def test_autodiscovery_database_metrics(aggregator, dd_run_check, instance_autodiscovery):
    instance_autodiscovery['autodiscovery_include'] = ['master', 'msdb']
    check = SQLServer(CHECK_NAME, {}, [instance_autodiscovery])
    dd_run_check(check)
    instance_tags = check._config.tags + [
        "database_hostname:{}".format("stubbed.hostname"),
        "database_instance:{}".format("stubbed.hostname"),
        "dd.internal.resource:database_instance:{}".format("stubbed.hostname"),
        "sqlserver_servername:{}".format(check.static_info_cache.get(STATIC_INFO_SERVERNAME)),
    ]

    master_tags = [
        'database:master',
        'db:master',
        'database_files_state_desc:ONLINE',
        'file_id:1',
        'file_location:/var/opt/mssql/data/master.mdf',
        'file_type:data',
        'file_name:master',
    ] + instance_tags
    msdb_tags = [
        'database:msdb',
        'db:msdb',
        'database_files_state_desc:ONLINE',
        'file_id:1',
        'file_location:/var/opt/mssql/data/MSDBData.mdf',
        'file_type:data',
        'file_name:MSDBData',
    ] + instance_tags
    aggregator.assert_metric('sqlserver.database.files.size', tags=master_tags)
    aggregator.assert_metric('sqlserver.database.files.size', tags=msdb_tags)
    aggregator.assert_metric('sqlserver.database.files.state', tags=master_tags)
    aggregator.assert_metric('sqlserver.database.files.state', tags=msdb_tags)
    aggregator.assert_metric('sqlserver.database.files.space_used', tags=master_tags)
    aggregator.assert_metric('sqlserver.database.files.space_used', tags=msdb_tags)


@pytest.mark.integration
@pytest.mark.parametrize(
    'service_check_enabled,default_count,extra_count',
    [(True, 4, 1), (False, 0, 0)],
)
@pytest.mark.usefixtures('dd_environment')
def test_autodiscovery_db_service_checks(
    aggregator, dd_run_check, instance_autodiscovery, service_check_enabled, default_count, extra_count
):
    instance_autodiscovery['autodiscovery_include'] = ['master', 'msdb', 'unavailable_db']
    instance_autodiscovery['autodiscovery_db_service_check'] = service_check_enabled
    check = SQLServer(CHECK_NAME, {}, [instance_autodiscovery])
    dd_run_check(check)
    instance_tags = check._config.tags + [
        "database_hostname:{}".format("stubbed.hostname"),
        "database_instance:{}".format("stubbed.hostname"),
        "dd.internal.resource:database_instance:{}".format("stubbed.hostname"),
        "sqlserver_servername:{}".format(check.static_info_cache.get(STATIC_INFO_SERVERNAME)),
    ]

    # verify that the old status check returns OK
    aggregator.assert_service_check(
        'sqlserver.can_connect',
        tags=[
            'db:master',
            'sqlserver_host:{}'.format(check.resolved_hostname),
            'connection_host:{}'.format(instance_autodiscovery.get('host')),
        ]
        + instance_tags,
        status=SQLServer.OK,
    )

    # verify all databases in autodiscovery have a service check
    aggregator.assert_service_check(
        'sqlserver.database.can_connect',
        count=extra_count,
        tags=[
            'db:msdb',
            'sqlserver_host:{}'.format(check.resolved_hostname),
            'connection_host:{}'.format(instance_autodiscovery.get('host')),
        ]
        + instance_tags,
        status=SQLServer.OK,
    )
    # unavailable_db is an 'offline' database which prevents connections, so we expect this service check to be
    # critical but not cause a failure of the check
    # TODO: add support to the assert_service_check function to take a message regex pattern
    # to match against, so this assertion does not require the exact string
    sc = aggregator.service_checks('sqlserver.database.can_connect')
    db_critical_exists = False
    critical_tags = instance_tags + [
        'db:unavailable_db',
        'sqlserver_host:{}'.format(check.resolved_hostname),
        'connection_host:{}'.format(instance_autodiscovery.get('host')),
    ]
    for c in sc:
        if c.status == SQLServer.CRITICAL:
            db_critical_exists = True
            assert sorted(c.tags) == sorted(critical_tags)
    if service_check_enabled:
        assert db_critical_exists


@pytest.mark.integration
@pytest.mark.usefixtures('dd_environment')
def test_autodiscovery_exclude_db_service_checks(aggregator, dd_run_check, instance_autodiscovery):
    instance_autodiscovery['autodiscovery_include'] = ['master']
    instance_autodiscovery['autodiscovery_exclude'] = ['msdb']
    check = SQLServer(CHECK_NAME, {}, [instance_autodiscovery])
    dd_run_check(check)

    instance_tags = check._config.tags + [
        "database_hostname:{}".format("stubbed.hostname"),
        "database_instance:{}".format("stubbed.hostname"),
        "dd.internal.resource:database_instance:{}".format("stubbed.hostname"),
        "sqlserver_servername:{}".format(check.static_info_cache.get(STATIC_INFO_SERVERNAME)),
    ]

    # assert no connection is created for an excluded database
    aggregator.assert_service_check(
        'sqlserver.database.can_connect',
        tags=[
            'db:msdb',
            'sqlserver_host:{}'.format(check.resolved_hostname),
            'connection_host:{}'.format(instance_autodiscovery.get('host')),
        ]
        + instance_tags,
        status=SQLServer.OK,
        count=0,
    )
    aggregator.assert_service_check(
        'sqlserver.database.can_connect',
        tags=[
            'db:master',
            'sqlserver_host:{}'.format(check.resolved_hostname),
            'connection_host:{}'.format(instance_autodiscovery.get('host')),
        ]
        + instance_tags,
        status=SQLServer.OK,
    )


@pytest.mark.integration
@pytest.mark.usefixtures('dd_environment')
def test_no_autodiscovery_service_checks(aggregator, dd_run_check, init_config, instance_docker):
    sqlserver_check = SQLServer(CHECK_NAME, init_config, [instance_docker])
    dd_run_check(sqlserver_check)

    # assert no database service checks
    aggregator.assert_service_check('sqlserver.database.can_connect', count=0)


@pytest.mark.integration
@pytest.mark.usefixtures('dd_environment')
def test_autodiscovery_perf_counters(aggregator, dd_run_check, instance_autodiscovery):
    instance_autodiscovery['autodiscovery_include'] = ['master', 'msdb']
    check = SQLServer(CHECK_NAME, {}, [instance_autodiscovery])
    dd_run_check(check)
    instance_tags = check._config.tags + [
        "database_hostname:{}".format("stubbed.hostname"),
        "database_instance:{}".format("stubbed.hostname"),
        "dd.internal.resource:database_instance:{}".format("stubbed.hostname"),
        "sqlserver_servername:{}".format(check.static_info_cache.get(STATIC_INFO_SERVERNAME)),
    ]

    expected_metrics = [m[0] for m in INSTANCE_METRICS_DATABASE_SINGLE]
    master_tags = ['database:master'] + instance_tags
    msdb_tags = ['database:msdb'] + instance_tags
    for metric in expected_metrics:
        aggregator.assert_metric(metric, tags=master_tags, hostname=check.resolved_hostname)
        aggregator.assert_metric(metric, tags=msdb_tags, hostname=check.resolved_hostname)


@pytest.mark.integration
@pytest.mark.usefixtures('dd_environment')
@always_on
def test_autodiscovery_perf_counters_ao(aggregator, dd_run_check, instance_autodiscovery):
    instance_autodiscovery['autodiscovery_include'] = ['datadog_test-1']
    check = SQLServer(CHECK_NAME, {}, [instance_autodiscovery])
    dd_run_check(check)
    instance_tags = check._config.tags + [
        "database_hostname:{}".format("stubbed.hostname"),
        "database_instance:{}".format("stubbed.hostname"),
        "dd.internal.resource:database_instance:{}".format("stubbed.hostname"),
        "sqlserver_servername:{}".format(check.static_info_cache.get(STATIC_INFO_SERVERNAME)),
    ]

    expected_metrics = [m[0] for m in INSTANCE_METRICS_DATABASE]
    tags = ['database:datadog_test-1'] + instance_tags
    for metric in expected_metrics:
        print(aggregator.metrics(metric))
        aggregator.assert_metric(metric, tags=tags, hostname=check.resolved_hostname)


@pytest.mark.integration
@pytest.mark.usefixtures('dd_environment')
def test_autodiscovery_perf_counters_doesnt_duplicate_names_of_metrics_to_collect(dd_run_check, instance_autodiscovery):
    instance_autodiscovery['autodiscovery_include'] = ['master', 'msdb']
    check = SQLServer(CHECK_NAME, {}, [instance_autodiscovery])
    dd_run_check(check)

    for _cls, metric_names in check.instance_per_type_metrics.items():
        expected = list(set(metric_names))
        assert sorted(metric_names) == sorted(expected)


@pytest.mark.integration
@pytest.mark.usefixtures('dd_environment')
def test_autodiscovery_multiple_instances(aggregator, dd_run_check, instance_autodiscovery, caplog):
    caplog.clear()
    caplog.set_level(logging.DEBUG)

    instance_1 = deepcopy(instance_autodiscovery)
    instance_2 = deepcopy(instance_autodiscovery)

    instance_1['autodiscovery_include'] = ['master']
    instance_2['autodiscovery_include'] = ['msdb']

    check = SQLServer(CHECK_NAME, {}, instances=[instance_1, instance_2])
    dd_run_check(check)

    check = SQLServer(CHECK_NAME, {}, instances=[instance_2, instance_1])
    dd_run_check(check)

    found_log = 0
    for _, _, message in caplog.record_tuples:
        # make sure master and msdb is only queried once
        if "Restoring the original database context master" in message:
            found_log += 1

    assert found_log == 2


@pytest.mark.integration
@pytest.mark.usefixtures('dd_environment')
@pytest.mark.parametrize(
    "custom_query, assert_metrics",
    [
        (
            {
                'query': "SELECT letter, num FROM (VALUES (97, 'a'), (98, 'b')) AS t (num,letter)",
                'columns': [{'name': 'customtag', 'type': 'tag'}, {'name': 'num', 'type': 'gauge'}],
                'tags': ['query:custom'],
            },
            [
                ("sqlserver.num", {"value": 97, "tags": ["customtag:a", "query:custom"]}),
                ("sqlserver.num", {"value": 98, "tags": ["customtag:b", "query:custom"]}),
            ],
        ),
        (
            {
                'query': "EXEC exampleProcWithoutNocount",
                'columns': [{'name': 'value', 'type': 'gauge'}],
                'tags': ['hello:there'],
            },
            [
                ("sqlserver.value", {"value": 1, "tags": ["hello:there"]}),
            ],
        ),
    ],
)
def test_custom_queries(aggregator, dd_run_check, instance_docker, custom_query, assert_metrics):
    instance = copy(instance_docker)
    instance['custom_queries'] = [custom_query]
    instance['procedure_metrics'] = {'enabled': False}

    check = SQLServer(CHECK_NAME, {}, [instance])
    dd_run_check(check)

    for metric_name, kwargs in assert_metrics:
        kwargs = copy(kwargs)
        kwargs['tags'] = (
            check._config.tags
            + [
                "database_hostname:{}".format("stubbed.hostname"),
                "database_instance:{}".format("stubbed.hostname"),
                "dd.internal.resource:database_instance:{}".format("stubbed.hostname"),
                "sqlserver_servername:{}".format(check.static_info_cache.get(STATIC_INFO_SERVERNAME)),
            ]
            + kwargs.get('tags', [])
        )
        aggregator.assert_metric(metric_name, **kwargs)


@pytest.mark.integration
@pytest.mark.usefixtures('dd_environment')
def test_load_static_information(aggregator, dd_run_check, instance_docker):
    instance = copy(instance_docker)
    check = SQLServer(CHECK_NAME, {}, [instance])
    dd_run_check(check)
    assert 'version' in check.static_info_cache, "missing version static information"
    assert check.static_info_cache['version'], "empty version in static information"


@windows_ci
@pytest.mark.integration
def test_check_windows_defaults(aggregator, dd_run_check, init_config, instance_docker_defaults):
    check = SQLServer(CHECK_NAME, init_config, [instance_docker_defaults])
    dd_run_check(check)

    aggregator.assert_metric_has_tag('sqlserver.db.commit_table_entries', 'db:master')

    for mname in EXPECTED_DEFAULT_METRICS + CUSTOM_METRICS:
        # These require extra setup to test
        if mname not in DATABASE_INDEX_METRICS and mname not in [m[0] for m in TABLE_SIZE_METRICS]:
            aggregator.assert_metric(mname)

    aggregator.assert_service_check('sqlserver.can_connect', status=SQLServer.OK)

    for operation_name in get_operation_time_metrics(instance_docker_defaults):
        aggregator.assert_metric(
            OPERATION_TIME_METRIC_NAME,
            tags=['operation:{}'.format(operation_name)] + check.debug_stats_kwargs()['tags'],
            hostname=check.resolved_hostname,
            count=1,
        )

    aggregator.assert_all_metrics_covered()


@pytest.mark.integration
@pytest.mark.usefixtures('dd_environment')
@pytest.mark.parametrize('database_autodiscovery', [True, False])
def test_index_fragmentation_metrics(aggregator, dd_run_check, instance_docker, database_autodiscovery):
    instance_docker['database_autodiscovery'] = database_autodiscovery
    sqlserver_check = SQLServer(CHECK_NAME, {}, [instance_docker])
    dd_run_check(sqlserver_check)
    seen_databases = set()
    for m in aggregator.metrics("sqlserver.database.avg_fragmentation_in_percent"):
        tags_by_key = dict([t.split(':', 1) for t in m.tags])
        seen_databases.add(tags_by_key['database_name'])
        assert tags_by_key['object_name'].lower() != 'none'

    assert 'master' in seen_databases
    if database_autodiscovery:
        assert 'datadog_test-1' in seen_databases


@pytest.mark.integration
@pytest.mark.usefixtures('dd_environment')
@pytest.mark.parametrize('database_autodiscovery', [True, False])
def test_table_size_metrics(aggregator, dd_run_check, instance_docker, database_autodiscovery):
    instance_docker['database_autodiscovery'] = database_autodiscovery
    sqlserver_check = SQLServer(CHECK_NAME, {}, [instance_docker])
    dd_run_check(sqlserver_check)
    seen_databases = set()
    for m in aggregator.metrics("sqlserver.table.row_count"):
        tags_by_key = dict([t.split(':', 1) for t in m.tags])
        seen_databases.add(tags_by_key['database'])
        assert tags_by_key['table'].lower() != 'none'
        assert tags_by_key['schema'].lower() != 'none'

    for m in aggregator.metrics("sqlserver.table.data_size"):
        tags_by_key = dict([t.split(':', 1) for t in m.tags])
        seen_databases.add(tags_by_key['database'])
        assert tags_by_key['table'].lower() != 'none'
        assert tags_by_key['schema'].lower() != 'none'

    for m in aggregator.metrics("sqlserver.table.total_size"):
        tags_by_key = dict([t.split(':', 1) for t in m.tags])
        seen_databases.add(tags_by_key['database'])
        assert tags_by_key['table'].lower() != 'none'
        assert tags_by_key['schema'].lower() != 'none'

    for m in aggregator.metrics("sqlserver.table.used_size"):
        tags_by_key = dict([t.split(':', 1) for t in m.tags])
        seen_databases.add(tags_by_key['database'])
        assert tags_by_key['table'].lower() != 'none'
        assert tags_by_key['schema'].lower() != 'none'

    assert 'master' in seen_databases
    if database_autodiscovery:
        assert 'datadog_test-1' in seen_databases


@pytest.mark.integration
@pytest.mark.usefixtures('dd_environment')
def test_custom_metrics_fraction_counters(aggregator, dd_run_check, instance_docker, caplog):
    caplog.clear()
    caplog.set_level(logging.DEBUG)
    instance_docker['procedure_metrics'] = {'enabled': False}
    sqlserver_check = SQLServer(
        CHECK_NAME,
        {
            'custom_metrics': [
                {
                    'name': 'sqlserver.custom.plan_cache_test',
                    'counter_name': 'Cache Hit Ratio',
                    'instance_name': 'ALL',
                    'object_name': 'SQLServer:Plan Cache',
                    'tag_by': 'plan_type',
                    'tags': ['optional_tag:tagx'],
                },
            ]
        },
        [instance_docker],
    )
    dd_run_check(sqlserver_check)
    seen_plan_type = set()
    for m in aggregator.metrics("sqlserver.custom.plan_cache_test"):
        tags_by_key = dict([t.split(':', 1) for t in m.tags])
        seen_plan_type.add(tags_by_key['plan_type'])
        assert tags_by_key['optional_tag'].lower() == 'tagx'
    assert 'SQL Plans' in seen_plan_type
    assert 'Object Plans' in seen_plan_type


@pytest.mark.integration
@pytest.mark.usefixtures('dd_environment')
@pytest.mark.parametrize('database_autodiscovery', [True, False])
def test_file_space_usage_metrics(aggregator, dd_run_check, instance_docker, database_autodiscovery):
    instance_docker['database_autodiscovery'] = database_autodiscovery
    sqlserver_check = SQLServer(CHECK_NAME, {}, [instance_docker])
    dd_run_check(sqlserver_check)
    seen_databases = set()
    for m in aggregator.metrics("sqlserver.tempdb.file_space_usage.free_space"):
        tags_by_key = dict([t.split(':', 1) for t in m.tags])
        seen_databases.add(tags_by_key['database'])
        assert tags_by_key['database_id']

    assert 'tempdb' in seen_databases


@pytest.mark.integration
@pytest.mark.parametrize(
    "dbm_enabled, database, reported_hostname, engine_edition, expected_hostname, cloud_metadata, metric_names",
    [
        (
            True,
            None,
            '',
            None,
            'stubbed.hostname',
            {},
            [],
        ),
        (
            False,
            None,
            '',
            ENGINE_EDITION_STANDARD,
            'stubbed.hostname',
            {
                'azure': {
                    'deployment_type': 'managed_instance',
                    'name': 'my-instance',
                },
            },
            ["dd.internal.resource:azure_sql_server_managed_instance:my-instance"],
        ),
        (
            True,
            None,
            '',
            ENGINE_EDITION_STANDARD,
            'stubbed.hostname',
            {
                'azure': {
                    'deployment_type': 'managed_instance',
                    'name': 'my-instance',
                },
            },
            ["dd.internal.resource:azure_sql_server_managed_instance:my-instance"],
        ),
        (
            True,
            None,
            'forced_hostname',
            None,
            'forced_hostname',
            {},
            [],
        ),
        (
            False,
            None,
            'forced_hostname',
            None,
            'forced_hostname',
            {},
            [],
        ),
        (
            True,
            'datadog_test-1',
            'forced_hostname',
            ENGINE_EDITION_SQL_DATABASE,
            'forced_hostname',
            {
                'azure': {
                    'deployment_type': 'sql_database',
                    'name': 'my-instance.database.windows.net',
                },
            },
            [
                "dd.internal.resource:azure_sql_server_database:my-instance.database.windows.net/datadog_test-1",
                "dd.internal.resource:azure_sql_server:my-instance.database.windows.net",
            ],
        ),
        (
            True,
            'datadog_test-1',
            None,
            ENGINE_EDITION_SQL_DATABASE,
            'stubbed.hostname',
            {
                'azure': {
                    'deployment_type': 'sql_database',
                    'name': 'my-instance.database.windows.net',
                },
            },
            [
                "dd.internal.resource:azure_sql_server_database:my-instance.database.windows.net/datadog_test-1",
                "dd.internal.resource:azure_sql_server:my-instance.database.windows.net",
            ],
        ),
        (
            True,
            'datadog_test-1',
            None,
            ENGINE_EDITION_SQL_DATABASE,
            'stubbed.hostname',
            {
                'azure': {
                    'deployment_type': 'sql_database',
                    'fully_qualified_domain_name': 'my-instance.database.windows.net',
                },
            },
            [
                "dd.internal.resource:azure_sql_server_database:my-instance.database.windows.net/datadog_test-1",
                "dd.internal.resource:azure_sql_server:my-instance.database.windows.net",
            ],
        ),
        (
            True,
            'datadog_test-1',
            None,
            ENGINE_EDITION_SQL_DATABASE,
            'stubbed.hostname',
            {
                'azure': {
                    'deployment_type': 'sql_database',
                    'fully_qualified_domain_name': 'my-instance.database.windows.net',
                    'aggregate_sql_databases': True,
                },
            },
            [
                "dd.internal.resource:azure_sql_server_database:my-instance.database.windows.net/datadog_test-1",
                "dd.internal.resource:azure_sql_server:my-instance.database.windows.net",
            ],
        ),
        (
            True,
            'master',
            None,
            ENGINE_EDITION_SQL_DATABASE,
            'stubbed.hostname',
            {},
            [],
        ),
        (
            False,
            'master',
            None,
            ENGINE_EDITION_SQL_DATABASE,
            'stubbed.hostname',
            {},
            [],
        ),
        (
            False,
            '',
            None,
            ENGINE_EDITION_SQL_DATABASE,
            'stubbed.hostname',
            {
                'aws': {
                    'instance_endpoint': 'foo.aws.com',
                },
                'azure': {
                    'deployment_type': 'sql_database',
                    'name': 'my-instance.database.windows.net',
                },
            },
            [
                "dd.internal.resource:aws_rds_instance:foo.aws.com",
                "dd.internal.resource:azure_sql_server_database:my-instance.database.windows.net",
                "dd.internal.resource:azure_sql_server:my-instance.database.windows.net",
            ],
        ),
        (
            False,
            'master',
            None,
            None,
            'stubbed.hostname',
            {
                'gcp': {
                    'project_id': 'foo-project',
                    'instance_id': 'bar',
                    'extra_field': 'included',
                },
            },
            [
                "dd.internal.resource:gcp_sql_database_instance:foo-project:bar",
            ],
        ),
    ],
)
@pytest.mark.integration
def test_resolved_hostname_set(
    aggregator,
    dd_run_check,
    instance_docker,
    dbm_enabled,
    database,
    reported_hostname,
    engine_edition,
    expected_hostname,
    cloud_metadata,
    metric_names,
):
    if cloud_metadata:
        for k, v in cloud_metadata.items():
            instance_docker[k] = v
    instance_docker['dbm'] = dbm_enabled
    if dbm_enabled:
        # set a very small collection interval so the tests go fast
        instance_docker['procedure_metrics'] = {'collection_interval': 0.1}
        instance_docker['collect_settings'] = {'collection_interval': 0.1}
        instance_docker['query_activity'] = {'collection_interval': 0.1}
        instance_docker['query_metrics'] = {'collection_interval': 0.1}
    if database:
        instance_docker['database'] = database
    if reported_hostname:
        instance_docker['reported_hostname'] = reported_hostname
    sqlserver_check = SQLServer(CHECK_NAME, {}, [instance_docker])
    if engine_edition:
        sqlserver_check.static_info_cache[STATIC_INFO_VERSION] = "Microsoft SQL Server 2019"
        sqlserver_check.static_info_cache[STATIC_INFO_MAJOR_VERSION] = 2019
        sqlserver_check.static_info_cache[STATIC_INFO_ENGINE_EDITION] = engine_edition
    dd_run_check(sqlserver_check)
    assert sqlserver_check.resolved_hostname == expected_hostname
    for m in metric_names:
        aggregator.assert_metric_has_tag("sqlserver.stats.batch_requests", m)
    aggregator.assert_metric_has_tag(
        "sqlserver.stats.batch_requests", "dd.internal.resource:database_instance:{}".format(expected_hostname)
    )


@pytest.mark.parametrize(
    'dbm_enabled, reported_hostname',
    [
        (True, None),
        (False, None),
        (True, 'forced_hostname'),
        (True, 'forced_hostname'),
    ],
)
@pytest.mark.integration
@pytest.mark.usefixtures('dd_environment')
def test_database_instance_metadata(aggregator, dd_run_check, instance_docker, dbm_enabled, reported_hostname):
    instance_docker['dbm'] = dbm_enabled
    if dbm_enabled:
        # set a very small collection interval so the tests go fast
        instance_docker['procedure_metrics'] = {'collection_interval': 0.1}
        instance_docker['collect_settings'] = {'collection_interval': 0.1}
        instance_docker['query_activity'] = {'collection_interval': 0.1}
        instance_docker['query_metrics'] = {'collection_interval': 0.1}
    if reported_hostname:
        instance_docker['reported_hostname'] = reported_hostname
    expected_host = reported_hostname if reported_hostname else 'stubbed.hostname'
    check = SQLServer(CHECK_NAME, {}, [instance_docker])
    dd_run_check(check)

    dbm_metadata = aggregator.get_event_platform_events("dbm-metadata")
    event = next((e for e in dbm_metadata if e['kind'] == 'database_instance'), None)
    assert event is not None
    assert event['host'] == expected_host
    assert event['dbms'] == "sqlserver"
    assert len(event['tags']) == 5
    assert event['tags'][0] == 'optional:tag1'
    assert any(tag.startswith('sqlserver_servername:') for tag in event['tags'])
    assert event['integration_version'] == __version__
    assert event['collection_interval'] == 300
    assert event['metadata'] == {
        'dbm': dbm_enabled,
        'connection_host': instance_docker['host'],
    }

    # Run a second time and expect the metadata to not be emitted again because of the cache TTL
    aggregator.reset()
    dd_run_check(check)

    dbm_metadata = aggregator.get_event_platform_events("dbm-metadata")
    event = next((e for e in dbm_metadata if e['kind'] == 'database_instance'), None)
    assert event is None


@pytest.mark.integration
@pytest.mark.usefixtures('dd_environment')
@pytest.mark.parametrize('database_autodiscovery', [True, False])
def test_index_usage_statistics(aggregator, dd_run_check, instance_docker, database_autodiscovery):
    instance_docker['database_autodiscovery'] = database_autodiscovery
    if not database_autodiscovery:
        instance_docker['database'] = "datadog_test-1"
    # currently the `thingsindex` index on the `name` column in the ϑings table
    # in order to generate user seeks, scans, updates and lookups we can run a variety
    # of queries against this table
    conn_str = 'DRIVER={};Server={};Database=datadog_test-1;UID={};PWD={};TrustServerCertificate=yes;'.format(
        instance_docker['driver'], instance_docker['host'], "bob", "Password12!"
    )
    conn = pyodbc.connect(conn_str, timeout=DEFAULT_TIMEOUT, autocommit=True)
    queries = {
        "INSERT INTO dbo.ϑings (name) VALUES (?);": ("NewName",),
        "SELECT * FROM dbo.ϑings WHERE name LIKE '%NewName%';": (),
        "SELECT * FROM dbo.ϑings;": (),
        "SELECT id, name FROM ϑings WHERE name = ?;": ("NewName",),
    }

    def execute_query(query, params):
        cursor = conn.cursor()
        cursor.execute(query, params)

    for query, params in queries.items():
        execute_query(query, params)

    check = SQLServer(CHECK_NAME, {}, [instance_docker])
    dd_run_check(check)
    expected_tags = (
        check._config.tags
        + [
            "database_hostname:{}".format("stubbed.hostname"),
            "database_instance:{}".format("stubbed.hostname"),
            "dd.internal.resource:database_instance:{}".format("stubbed.hostname"),
            "sqlserver_servername:{}".format(check.static_info_cache.get(STATIC_INFO_SERVERNAME)),
        ]
        + [
            'db:datadog_test-1',
            'table:ϑings',
            'schema:dbo',
            'index_name:thingsindex',
        ]
    )
    for m in DATABASE_INDEX_METRICS:
        aggregator.assert_metric(m, tags=expected_tags, count=1)


@pytest.mark.integration
@pytest.mark.usefixtures('dd_environment')
def test_database_state(aggregator, dd_run_check, init_config, instance_docker):
    instance_docker['database'] = 'master'
    sqlserver_check = SQLServer(CHECK_NAME, init_config, [instance_docker])
    dd_run_check(sqlserver_check)
    expected_tags = (
        sqlserver_check._config.tags
        + [
            "database_hostname:{}".format("stubbed.hostname"),
            "database_instance:{}".format("stubbed.hostname"),
            "dd.internal.resource:database_instance:{}".format("stubbed.hostname"),
            "sqlserver_servername:{}".format(sqlserver_check.static_info_cache.get(STATIC_INFO_SERVERNAME)),
        ]
        + [
            'database_recovery_model_desc:SIMPLE',
            'database_state_desc:ONLINE',
            'database:{}'.format(instance_docker['database']),
            'db:{}'.format(instance_docker['database']),
        ]
    )
    aggregator.assert_metric('sqlserver.database.state', tags=expected_tags, hostname=sqlserver_check.resolved_hostname)


@pytest.mark.parametrize(
    'instance_propagate_agent_tags,init_config_propagate_agent_tags,should_propagate_agent_tags',
    [
        pytest.param(True, True, True, id="both true"),
        pytest.param(True, False, True, id="instance config true prevails"),
        pytest.param(False, True, False, id="instance config false prevails"),
        pytest.param(False, False, False, id="both false"),
        pytest.param(None, True, True, id="init_config true applies to all instances"),
        pytest.param(None, False, False, id="init_config false applies to all instances"),
        pytest.param(None, None, False, id="default to false"),
        pytest.param(True, None, True, id="instance config true prevails, init_config is None"),
        pytest.param(False, None, False, id="instance config false prevails, init_config is None"),
    ],
)
@pytest.mark.integration
def test_propagate_agent_tags(
    aggregator,
    dd_run_check,
    instance_docker,
    instance_propagate_agent_tags,
    init_config_propagate_agent_tags,
    should_propagate_agent_tags,
):
    init_config = {}
    if instance_propagate_agent_tags is not None:
        instance_docker['propagate_agent_tags'] = instance_propagate_agent_tags
    if init_config_propagate_agent_tags is not None:
        init_config['propagate_agent_tags'] = init_config_propagate_agent_tags

    agent_tags = ['my-env:test-env', 'random:tag', 'bar:foo']

    with mock.patch('datadog_checks.sqlserver.config.get_agent_host_tags', return_value=agent_tags):
        check = SQLServer(CHECK_NAME, init_config, [instance_docker])
        assert check._config._should_propagate_agent_tags(instance_docker, init_config) == should_propagate_agent_tags
        if should_propagate_agent_tags:
            assert all(tag in check.tag_manager.get_tags() for tag in agent_tags)
            dd_run_check(check)
            expected_tags = (
                check._config.tags
                + [
                    "database_hostname:{}".format("stubbed.hostname"),
                    "database_instance:{}".format("stubbed.hostname"),
                    "dd.internal.resource:database_instance:{}".format("stubbed.hostname"),
                    "sqlserver_servername:{}".format(check.static_info_cache.get(STATIC_INFO_SERVERNAME)),
                ]
                + [
                    'connection_host:{}'.format(instance_docker.get('host')),
                    'sqlserver_host:{}'.format(check.resolved_hostname),
                    'db:master',
                ]
            )
            aggregator.assert_service_check(
                'sqlserver.can_connect',
                status=SQLServer.OK,
                tags=expected_tags,
            )


@pytest.mark.integration
@pytest.mark.usefixtures('dd_environment')
def test_check_static_information_expire(aggregator, dd_run_check, init_config, instance_docker):
    sqlserver_check = SQLServer(CHECK_NAME, init_config, [instance_docker])
    dd_run_check(sqlserver_check)
    assert sqlserver_check.static_info_cache is not None
    assert len(sqlserver_check.static_info_cache.keys()) == 7
    assert sqlserver_check.resolved_hostname == 'stubbed.hostname'

    # manually clear static information cache
    sqlserver_check.static_info_cache.clear()
    dd_run_check(sqlserver_check)
    assert sqlserver_check.static_info_cache is not None
    assert len(sqlserver_check.static_info_cache.keys()) == 7
    assert sqlserver_check.resolved_hostname == 'stubbed.hostname'

    # manually pop STATIC_INFO_ENGINE_EDITION to make sure it is reloaded
    sqlserver_check.static_info_cache.pop(STATIC_INFO_ENGINE_EDITION)
    dd_run_check(sqlserver_check)
    assert sqlserver_check.static_info_cache is not None
    assert len(sqlserver_check.static_info_cache.keys()) == 7
    assert sqlserver_check.resolved_hostname == 'stubbed.hostname'


@pytest.mark.integration
@pytest.mark.usefixtures('dd_environment')
def test_xe_collection_integration(aggregator, dd_run_check, bob_conn, instance_docker, caplog):
    """Test that XE sessions collect and process events properly."""
    # Configure instance to enable XE collection
    instance = copy(instance_docker)
    instance['dbm'] = True
    instance['xe_collection'] = {
        'query_completions': {
            'enabled': True,
            'collection_interval': 0.1,
        },
        'query_errors': {
            'enabled': True,
            'collection_interval': 0.1,
        },
    }
    # Ensure raw query collection is enabled
    instance['collect_raw_query_statement'] = {"enabled": True, "cache_max_size": 100, "samples_per_hour_per_query": 10}

    check = SQLServer(CHECK_NAME, {}, [instance])

    # Run check once to initialize sessions if needed
    dd_run_check(check)

    # Execute a query that will be captured (long enough to exceed the threshold)
    test_query = "WAITFOR DELAY '00:00:02'; SELECT 1;"
    bob_conn.execute_with_retries(test_query)

    # Execute a query that will generate an error
    error_query = "SELECT 1/0;"  # Division by zero error
    try:
        bob_conn.execute_with_retries(error_query)
    except:
        pass  # We expect this to fail

    # Run check again to collect the events
    dd_run_check(check)

    # Get events from the platform events API
    dbm_activity = aggregator.get_event_platform_events("dbm-activity")

    # Filter completion events (now each event may contain multiple query details)
    query_completion_batches = [e for e in dbm_activity if e.get('dbm_type') == 'query_completion']

    # Filter error events (now each event may contain multiple query details)
    error_batches = [e for e in dbm_activity if e.get('dbm_type') == 'query_error']

    # We should have at least one batch of completion events
    assert len(query_completion_batches) > 0, "No query completion batches collected"

    # We should have at least one batch of error events
    assert len(error_batches) > 0, "No error event batches collected"

    # Extract all individual completion events from batches
    query_completion_events = []
    for batch in query_completion_batches:
        events = batch.get('sqlserver_query_completions', [])
        if events:
            query_completion_events.extend(events)

    # Extract all individual error events from batches
    error_events = []
    for batch in error_batches:
        events = batch.get('sqlserver_query_errors', [])
        if events:
            error_events.extend(events)

    # We should have at least one query completion event
    assert len(query_completion_events) > 0, "No query completion events collected"

    # We should have at least one error event
    assert len(error_events) > 0, "No error events collected"

    # Verify specific query completion event details
    found_test_query = False
    for event in query_completion_events:
        # Look at query_details field which contains the XE event info
        query_details = event.get('query_details', {})
        sql_text = query_details.get('sql_text', '')

        if "WAITFOR DELAY" in sql_text and "SELECT 1" in sql_text:
            found_test_query = True
            # Check for expected properties
            assert "bob" in query_details.get('username', ''), "Username 'bob' not found in event"
            assert 'duration_ms' in query_details, "Duration not found in event"
            # The duration should be at least 2000ms (2 seconds)
            duration = float(query_details.get('duration_ms', 0))
            assert duration >= 2000, f"Expected duration >= 2000ms, but got {duration}ms"
            # Verify raw_query_signature is present when collect_raw_query is enabled
            assert 'raw_query_signature' in query_details, "raw_query_signature not found in query details"
            assert query_details.get('raw_query_signature'), "raw_query_signature is empty"

            # Verify primary_sql_field is present
            assert 'primary_sql_field' in query_details, "primary_sql_field not found in query details"
            assert query_details.get('primary_sql_field') in [
                'batch_text',
                'sql_text',
                'statement',
            ], f"Unexpected primary_sql_field value: {query_details.get('primary_sql_field')}"

            # Verify metadata is present
            assert 'metadata' in query_details, "metadata not found in query details"
            metadata = query_details.get('metadata', {})
            assert isinstance(metadata, dict), "metadata is not a dictionary"
            assert 'tables' in metadata, "tables not found in metadata"
            assert 'commands' in metadata, "commands not found in metadata"
            assert 'comments' in metadata, "comments not found in metadata"

    assert found_test_query, "Could not find our specific test query in the completion events"

    # Verify specific error event details
    found_error_query = False
    for event in error_events:
        # Look at query_details field which contains the XE event info
        query_details = event.get('query_details', {})
        sql_text = query_details.get('sql_text', '')

        if "SELECT 1/0" in sql_text:
            found_error_query = True
            # Check for expected properties
            assert "bob" in query_details.get('username', ''), "Username 'bob' not found in error event"
            assert "Divide by zero" in query_details.get('message', ''), "Expected error message not found"
            assert query_details.get('error_number') == 8134, "Expected error number 8134 not found"
            # Verify raw_query_signature is present when collect_raw_query is enabled
            assert 'raw_query_signature' in query_details, "raw_query_signature not found in error query details"
            assert query_details.get('raw_query_signature'), "raw_query_signature is empty"

            # Verify primary_sql_field is present
            assert 'primary_sql_field' in query_details, "primary_sql_field not found in error query details"
            assert query_details.get('primary_sql_field') in [
                'batch_text',
                'sql_text',
                'statement',
            ], f"Unexpected primary_sql_field value: {query_details.get('primary_sql_field')}"

            # Verify metadata is present
            assert 'metadata' in query_details, "metadata not found in error query details"
            metadata = query_details.get('metadata', {})
            assert isinstance(metadata, dict), "metadata is not a dictionary"
            assert 'tables' in metadata, "tables not found in metadata"
            assert 'commands' in metadata, "commands not found in metadata"
            assert 'comments' in metadata, "comments not found in metadata"

    assert found_error_query, "Could not find our specific error query in the error events"
