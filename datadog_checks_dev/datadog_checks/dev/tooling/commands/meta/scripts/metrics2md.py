# (C) Datadog, Inc. 2020-present
# All rights reserved
# Licensed under a 3-clause BSD style license (see LICENSE)
import csv
from io import StringIO

import click

from datadog_checks.dev.tooling.commands.console import CONTEXT_SETTINGS, abort, echo_info
from datadog_checks.dev.tooling.utils import read_metric_data_file

VALID_FIELDS = {
    'metric_name',
    'metric_type',
    'interval',
    'unit_name',
    'per_unit_name',
    'description',
    'orientation',
    'integration',
    'short_name',
    'curated_metric',
}

DEFAULT_FIELDS = ('metric_name', 'description', 'metric_type', 'unit_name')


@click.command(context_settings=CONTEXT_SETTINGS, short_help='Convert metadata.csv files to Markdown tables')
@click.argument('check')
@click.argument('fields', nargs=-1)
def metrics2md(check, fields):
    """Convert a check's metadata.csv file to a Markdown table, which will be copied to your clipboard.

    By default it will be compact and only contain the most useful fields. If you wish to use arbitrary
    metric data, you may set the check to `cb` to target the current contents of your clipboard.
    """
    if not fields:
        fields = DEFAULT_FIELDS
    else:
        chosen_fields = set(fields)
        if chosen_fields - VALID_FIELDS:
            abort(f"You must select only from the following fields: {', '.join(VALID_FIELDS)}")

        # Deduplicate and retain order
        old_fields = fields
        fields = []
        for field in old_fields:
            if field not in chosen_fields:
                continue

            fields.append(field)
            chosen_fields.discard(field)

    metric_data = read_metric_data_file(check)

    reader = csv.DictReader(StringIO(metric_data), delimiter=',')

    rows = []
    for csv_row in reader:
        rows.append(' | '.join(csv_row[field] or 'N/A' for field in fields))

    rows.sort()
    md_table_rows = [' | '.join(fields), ' | '.join('---' for _ in fields)]
    md_table_rows.extend(rows)

    echo_info('\n'.join(md_table_rows))
