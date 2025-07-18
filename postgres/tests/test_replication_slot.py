# (C) Datadog, Inc. 2023-present
# All rights reserved
# Licensed under a 3-clause BSD style license (see LICENSE)
import time

import psycopg
import pytest

from datadog_checks.dev.docker import get_container_ip
from datadog_checks.postgres.util import QUERY_PG_REPLICATION_SLOTS_STATS, QUERY_PG_REPLICATION_STATS_METRICS

from .common import (
    DB_NAME,
    HOST,
    REPLICA_LOGICAL_1_NAME,
    _get_expected_tags,
    _iterate_metric_name,
    assert_metric_at_least,
)
from .utils import requires_over_10, requires_over_14

pytestmark = [pytest.mark.integration, pytest.mark.usefixtures("dd_environment")]


@requires_over_10
def test_physical_replication_slots(aggregator, integration_check, pg_instance):
    check = integration_check(pg_instance)
    # It seemingly can take a small amount of time for the pg_replication_slots to be saturated
    # TODO: Poll for its existence as a ready check
    time.sleep(5)
    redo_lsn_age = 0
    xmin_age_higher_bound = 1
    # Keep the connection open so that the temporary replication slots are not dropped
    conn = psycopg.connect(host=HOST, dbname=DB_NAME, user="postgres", password="datad0g")
    with conn.cursor() as cur:
        cur.execute("select pg_wal_lsn_diff(pg_current_wal_lsn(), redo_lsn) from pg_control_checkpoint();")
        redo_lsn_age = int(cur.fetchall()[0][0])
        cur.execute("select age(xmin) FROM pg_replication_slots;")
        bound = cur.fetchall()[0][0]
        xmin_age_higher_bound += int(bound) if bound is not None else 0

        cur.execute("select * from pg_create_physical_replication_slot('phys_1');")
        cur.execute("select * from pg_create_physical_replication_slot('phys_2', true);")
        cur.execute("select * from pg_create_physical_replication_slot('phys_3', true, true);")

    check.check(pg_instance)

    #     slot_name     | slot_type | temporary | active | active_pid | xmin | restart_lsn
    # ------------------+-----------+-----------+--------+------------+------+-------------
    #  replication_slot | physical  | f         | t      |         99 |  806 | 0/30385B0
    #  phys_1           | physical  | f         | f      |            |      |
    #  phys_2           | physical  | f         | f      |            |      | 0/2000028
    #  phys_3           | physical  | t         | t      |        344 |      | 0/2000028

    # Nothing reported for phys_1
    base_tags = _get_expected_tags(check, pg_instance)
    expected_phys2_tags = base_tags + [
        "slot_name:phys_2",
        "slot_persistence:permanent",
        "slot_state:inactive",
        "slot_type:physical",
    ]
    expected_phys3_tags = base_tags + [
        "slot_name:phys_3",
        "slot_persistence:temporary",
        "slot_state:active",
        "slot_type:physical",
    ]
    expected_repslot_tags = base_tags + [
        "slot_name:replication_slot",
        "slot_persistence:permanent",
        "slot_state:active",
        "slot_type:physical",
    ]

    assert_metric_at_least(
        aggregator,
        "postgresql.replication_slot.restart_delay_bytes",
        lower_bound=redo_lsn_age,
        tags=expected_phys2_tags,
        count=1,
    )

    assert_metric_at_least(
        aggregator,
        "postgresql.replication_slot.restart_delay_bytes",
        lower_bound=redo_lsn_age,
        tags=expected_phys3_tags,
        count=1,
    )
    assert_metric_at_least(
        aggregator,
        "postgresql.replication_slot.xmin_age",
        higher_bound=xmin_age_higher_bound,
        tags=expected_repslot_tags,
        count=1,
    )

    conn.close()


@requires_over_10
def test_logical_replication_slots(aggregator, integration_check, pg_instance):
    check = integration_check(pg_instance)
    with psycopg.connect(host=HOST, dbname=DB_NAME, user="postgres", password="datad0g") as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT pg_wal_lsn_diff(pg_current_wal_lsn(), restart_lsn) FROM pg_replication_slots;")
            restart_age = cur.fetchall()[0][0]

    check.check(pg_instance)

    base_tags = _get_expected_tags(check, pg_instance)
    expected_tags = base_tags + [
        "slot_name:logical_slot",
        "slot_persistence:permanent",
        "slot_state:inactive",
        "slot_type:logical",
    ]
    # Both should be in the past
    assert_metric_at_least(
        aggregator,
        "postgresql.replication_slot.confirmed_flush_delay_bytes",
        count=1,
        lower_bound=50,
        tags=expected_tags,
    )
    assert_metric_at_least(
        aggregator,
        "postgresql.replication_slot.restart_delay_bytes",
        count=1,
        lower_bound=restart_age,
        tags=expected_tags,
    )


@requires_over_14
def test_replication_slot_stats(aggregator, integration_check, pg_instance):
    check = integration_check(pg_instance)
    check.check(pg_instance)

    expected_tags = _get_expected_tags(check, pg_instance) + [
        "slot_name:logical_slot",
        "slot_state:inactive",
        "slot_type:logical",
    ]
    for metric_name in _iterate_metric_name(QUERY_PG_REPLICATION_SLOTS_STATS):
        aggregator.assert_metric(metric_name, count=1, tags=expected_tags)


@requires_over_10
def test_replication_slot_information(aggregator, integration_check, pg_instance):
    client_address = None
    check = integration_check(pg_instance)
    client_address = get_container_ip(REPLICA_LOGICAL_1_NAME)
    check.check(pg_instance)
    base_tags = _get_expected_tags(check, pg_instance)
    expected_tags = base_tags + [
        "wal_app_name:subscription_cities",
        "wal_state:streaming",
        "wal_sync_state:async",
        "wal_client_addr:" + client_address,
        "slot_name:subscription_cities",
        "slot_type:logical",
    ]

    for metric_name in _iterate_metric_name(QUERY_PG_REPLICATION_STATS_METRICS):
        assert_metric_at_least(aggregator, metric_name, count=1, lower_bound=0, tags=expected_tags)
