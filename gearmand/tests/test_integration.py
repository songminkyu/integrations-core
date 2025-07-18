# (C) Datadog, Inc. 2018-present
# All rights reserved
# Licensed under a 3-clause BSD style license (see LICENSE)

import pytest

from datadog_checks.base.constants import ServiceCheck

from . import common


def test_service_check_broken(aggregator, check, dd_run_check):
    check = check(common.BAD_INSTANCE)

    tags = ['server:{}'.format(common.HOST), 'port:{}'.format(common.BAD_PORT)] + common.TAGS2

    with pytest.raises(Exception):
        dd_run_check(check)

    aggregator.assert_service_check('gearman.can_connect', status=ServiceCheck.CRITICAL, tags=tags, count=1)
    aggregator.assert_all_metrics_covered()


@pytest.mark.integration
@pytest.mark.usefixtures("dd_environment")
def test_version_metadata(check, instance, aggregator, datadog_agent, dd_run_check):
    check = check(instance)
    check.check_id = 'test:123'
    dd_run_check(check)

    # hardcoded because we only support one docker image for test env
    raw_version = common.GEARMAND_VERSION

    major, minor, patch = raw_version.split('.')
    version_metadata = {
        'version.scheme': 'semver',
        'version.major': major,
        'version.minor': minor,
        'version.patch': patch,
        'version.raw': raw_version,
    }

    datadog_agent.assert_metadata('test:123', version_metadata)
