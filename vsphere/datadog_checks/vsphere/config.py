# (C) Datadog, Inc. 2020-present
# All rights reserved
# Licensed under a 3-clause BSD style license (see LICENSE)

import re
from typing import Any, Dict, List  # noqa: F401

from pyVmomi import vim

from datadog_checks.base import ConfigurationError, is_affirmative
from datadog_checks.base.log import CheckLoggingAdapter  # noqa: F401
from datadog_checks.base.types import InitConfigType  # noqa: F401
from datadog_checks.vsphere.constants import (
    ALL_RESOURCES_WITH_METRICS,
    ALLOWED_FILTER_PROPERTIES,
    ALLOWED_FILTER_TYPES,
    BOTH,
    DEFAULT_BATCH_COLLECTOR_SIZE,
    DEFAULT_EVENT_RESOURCES,
    DEFAULT_MAX_QUERY_METRICS,
    DEFAULT_METRICS_PER_QUERY,
    DEFAULT_REFRESH_INFRASTRUCTURE_CACHE_INTERVAL,
    DEFAULT_REFRESH_METRICS_METADATA_CACHE_INTERVAL,
    DEFAULT_TAGS_COLLECTOR_SIZE,
    DEFAULT_THREAD_COUNT,
    DEFAULT_VSPHERE_ATTR_PREFIX,
    DEFAULT_VSPHERE_TAG_PREFIX,
    EXCLUDE_FILTERS,
    EXTRA_FILTER_PROPERTIES_FOR_VMS,
    HISTORICAL,
    HOSTNAME_CASE_OPTIONS,
    MOR_TYPE_AS_STRING,
    OBJECT_PROPERTIES_BY_RESOURCE_TYPE,
    PROPERTY_METRICS_BY_RESOURCE_TYPE,
    REALTIME,
    SIMPLE_PROPERTIES_BY_RESOURCE_TYPE,
)
from datadog_checks.vsphere.metrics import RESOURCES_WITH_HISTORICAL_METRICS, RESOURCES_WITH_REALTIME_METRICS
from datadog_checks.vsphere.resource_filters import ResourceFilter, create_resource_filter  # noqa: F401
from datadog_checks.vsphere.types import (  # noqa: F401
    InstanceConfig,
    MetricFilterConfig,
    MetricFilters,
    ResourceFilterConfig,
)
from datadog_checks.vsphere.utils import (
    object_properties_to_collect,
    property_metrics_to_collect,
    simple_properties_to_collect,
)


class VSphereConfig(object):
    def __init__(self, instance, init_config, log):
        # type: (InstanceConfig, InitConfigType, CheckLoggingAdapter) -> None
        self.log = log

        # Connection parameters
        self.hostname = instance['host']
        self.username = instance['username']
        self.password = instance['password']
        self.ssl_verify = is_affirmative(instance.get('ssl_verify', True))
        self.ssl_capath = instance.get('ssl_capath')
        self.ssl_cafile = instance.get('ssl_cafile')
        self.tls_ignore_warning = instance.get('tls_ignore_warning', False)

        self.rest_api_options = {
            'username': self.username,
            'password': self.password,
            'tls_ca_cert': self.ssl_capath,
            'tls_verify': self.ssl_verify,
            'tls_ignore_warning': self.tls_ignore_warning,
        }
        if isinstance(instance.get('rest_api_options'), dict):
            self.rest_api_options.update(instance['rest_api_options'])
        self.shared_rest_api_options = init_config.get('rest_api_options', {})  # type: Dict[str, Any]

        # vSphere options
        self.collection_level = instance.get("collection_level", 1)
        self.collection_type = instance.get("collection_type", "realtime")
        self.use_guest_hostname = instance.get("use_guest_hostname", False)
        self.vm_hostname_suffix_tag = instance.get("vm_hostname_suffix_tag", None)
        self.max_historical_metrics = instance.get("max_historical_metrics", DEFAULT_MAX_QUERY_METRICS)

        # Check option
        self.threads_count = instance.get("threads_count", DEFAULT_THREAD_COUNT)
        self.metrics_per_query = instance.get("metrics_per_query", DEFAULT_METRICS_PER_QUERY)
        self.batch_collector_size = instance.get('batch_property_collector_size', DEFAULT_BATCH_COLLECTOR_SIZE)
        self.batch_tags_collector_size = instance.get('batch_tags_collector_size', DEFAULT_TAGS_COLLECTOR_SIZE)
        self.collect_events_only = is_affirmative(instance.get("collect_events_only", False))
        self.should_collect_events = instance.get("collect_events", self.collection_type == 'realtime')
        self.use_collect_events_fallback = instance.get("use_collect_events_fallback", False)
        self.should_collect_tags = is_affirmative(instance.get("collect_tags", False))
        self.tags_prefix = instance.get("tags_prefix", DEFAULT_VSPHERE_TAG_PREFIX)
        self.should_collect_attributes = is_affirmative(instance.get("collect_attributes", False))
        self.collect_property_metrics = is_affirmative(instance.get("collect_property_metrics", False))
        self.collect_vsan = is_affirmative(instance.get("collect_vsan_data", False))
        self.attr_prefix = instance.get("attributes_prefix", DEFAULT_VSPHERE_ATTR_PREFIX)
        self.excluded_host_tags = instance.get("excluded_host_tags", [])
        self.empty_default_hostname = instance.get("empty_default_hostname", False)
        self.base_tags = instance.get("tags", []) + ["vcenter_server:{}".format(self.hostname)]
        self.refresh_infrastructure_cache_interval = instance.get(
            'refresh_infrastructure_cache_interval', DEFAULT_REFRESH_INFRASTRUCTURE_CACHE_INTERVAL
        )
        self.refresh_metrics_metadata_cache_interval = instance.get(
            'refresh_metrics_metadata_cache_interval', DEFAULT_REFRESH_METRICS_METADATA_CACHE_INTERVAL
        )
        self.connection_reset_timeout = instance.get("connection_reset_timeout", 900)

        # Always collect events if `collect_events_only` is true
        if self.collect_events_only:
            self.should_collect_events = True

        # Utility
        if self.collection_type == BOTH:
            self.collected_resource_types = ALL_RESOURCES_WITH_METRICS
            self.collected_metric_types = [REALTIME, HISTORICAL]
        elif self.collection_type == HISTORICAL:
            self.collected_resource_types = RESOURCES_WITH_HISTORICAL_METRICS
            self.collected_metric_types = [HISTORICAL]
        else:
            self.collected_resource_types = RESOURCES_WITH_REALTIME_METRICS
            self.collected_metric_types = [REALTIME]

        # Filters
        self.resource_filters = self._parse_resource_filters(instance.get("resource_filters", []))
        self.metric_filters = self._parse_metric_regex_filters(instance.get("metric_filters", {}))
        self.event_resource_filters = self._normalize_event_resource_filters(
            instance.get("event_resource_filters", DEFAULT_EVENT_RESOURCES)
        )
        self.include_events = instance.get("include_events", None)
        if self.include_events is None:
            self.exclude_filters = EXCLUDE_FILTERS
        else:
            self.exclude_filters = {}
            for item in self.include_events:
                event_name = item["event"]
                excluded_messages = [r'{}'.format(msg) for msg in item.get("excluded_messages", [])]
                self.exclude_filters[event_name] = excluded_messages

        # Since `collect_per_instance_filters` have the same structure as `metric_filters` we use the same parser
        self.collect_per_instance_filters = self._parse_metric_regex_filters(
            instance.get("collect_per_instance_filters", {})
        )
        self.include_datastore_cluster_folder_tag = instance.get("include_datastore_cluster_folder_tag", True)
        self.custom_tags = instance.get('tags', [])
        self.hostname_transform = instance.get('hostname_transform', 'default')
        if self.hostname_transform not in HOSTNAME_CASE_OPTIONS:
            raise ConfigurationError(
                "Invalid value for `hostname_transform` in the configuration file: "
                + "use one of: `default`, `lower`, or `upper`"
            )
        self.validate_config()

    def is_historical(self):
        # type: () -> bool
        return self.collection_type in (HISTORICAL, BOTH)

    def validate_config(self):
        # type: () -> None
        if not self.ssl_verify and self.ssl_capath:
            self.log.warning(
                "Your configuration is incorrectly attempting to "
                "specify both a CA path, and to disable SSL "
                "verification. You cannot do both. Proceeding with "
                "disabling ssl verification."
            )

        if self.collection_type not in (REALTIME, HISTORICAL, BOTH):
            raise ConfigurationError(
                "Your configuration is incorrectly attempting to "
                "set the `collection_type` to {}. It should be either "
                "'realtime', 'historical' or 'both'.".format(self.collection_type)
            )

        if self.collection_level not in (1, 2, 3, 4):
            raise ConfigurationError(
                "Your configuration is incorrectly attempting to "
                "set the collection_level to something different than a "
                "integer between 1 and 4."
            )

        all_valid_resource_types = list(MOR_TYPE_AS_STRING.values())
        for resource_type in self.event_resource_filters:
            if resource_type not in all_valid_resource_types:
                raise ConfigurationError(
                    "Invalid resource type specified in `event_resource_filters`: {}. Valid resource types: {}".format(
                        resource_type, all_valid_resource_types
                    ),
                )

    def _parse_resource_filters(self, all_resource_filters):
        # type: (List[ResourceFilterConfig]) -> List[ResourceFilter]

        # Keep a list of resource filters ids (tuple of resource, property and type) that are already registered.
        # This is to prevent users to define the same filter twice with different patterns.
        resource_filters_ids = []
        formatted_resource_filters = []  # type: List[ResourceFilter]
        allowed_resource_types = [MOR_TYPE_AS_STRING[k] for k in self.collected_resource_types]

        for resource_filter in all_resource_filters:
            # Optional fields:
            if 'type' not in resource_filter:
                resource_filter['type'] = 'whitelist'
            if 'property' not in resource_filter:
                resource_filter['property'] = 'name'

            if resource_filter['property'] == 'tag' and not self.should_collect_tags:
                raise ConfigurationError(
                    'Your configuration is incorrectly attempting to filter resources '
                    'by the `tag` property but `collect_tags` is disabled.'
                )
            if resource_filter['property'] == 'attribute' and not self.should_collect_attributes:
                raise ConfigurationError(
                    'Your configuration is incorrectly attempting to filter resources '
                    'by the `attribute` property but `collect_attributes` is disabled.'
                )

            # Check required fields and their types
            for field, field_type in {'resource': str, 'property': str, 'type': str, 'patterns': list}.items():
                if field not in resource_filter:
                    self.log.warning(
                        "Ignoring filter %r because it doesn't contain a %s field.", resource_filter, field
                    )
                    continue
                if not isinstance(resource_filter[field], field_type):  # type: ignore
                    self.log.warning(
                        "Ignoring filter %r because field %s should have type %s.", resource_filter, field, field_type
                    )
                    continue

            # Check `resource` validity
            if resource_filter['resource'] not in allowed_resource_types:
                self.log.warning(
                    "Ignoring filter %r because resource %s is not collected when collection_type is %s.",
                    resource_filter,
                    resource_filter['resource'],
                    self.collection_type,
                )
                continue

            # Check `property` validity
            allowed_prop_names = ALLOWED_FILTER_PROPERTIES
            if resource_filter['resource'] == MOR_TYPE_AS_STRING[vim.VirtualMachine]:
                allowed_prop_names += EXTRA_FILTER_PROPERTIES_FOR_VMS

            if resource_filter['property'] not in allowed_prop_names:
                self.log.warning(
                    "Ignoring filter %r because property '%s' is not valid for resource type %s. Should be one of %r.",
                    resource_filter,
                    resource_filter['property'],
                    resource_filter['resource'],
                    allowed_prop_names,
                )
                continue

            # Check `type` validity
            if resource_filter['type'] not in ALLOWED_FILTER_TYPES:
                self.log.warning(
                    "Ignoring filter %r because type '%s' is not valid. Should be one of %r.",
                    resource_filter,
                    resource_filter['type'],
                    ALLOWED_FILTER_TYPES,
                )
            patterns = [re.compile(r) for r in resource_filter['patterns']]
            filter_instance = create_resource_filter(
                resource_filter['resource'],
                resource_filter['property'],
                patterns,
                is_whitelist=(resource_filter['type'] == 'whitelist'),
            )
            if filter_instance.unique_key() in resource_filters_ids:
                self.log.warning(
                    "Ignoring filter %r because you already have a `%s` filter for resource type %s and property %s.",
                    resource_filter,
                    resource_filter['type'],
                    resource_filter['resource'],
                    resource_filter['property'],
                )
                continue

            formatted_resource_filters.append(filter_instance)
            resource_filters_ids.append(filter_instance.unique_key())

        return formatted_resource_filters

    def _parse_metric_regex_filters(self, all_metric_filters):
        # type: (MetricFilterConfig) -> MetricFilters
        allowed_resource_types = [MOR_TYPE_AS_STRING[k] for k in self.collected_resource_types]
        metric_filters = {}
        for resource_type, filters in all_metric_filters.items():
            if resource_type not in allowed_resource_types:
                self.log.warning(
                    "Ignoring metric_filter for resource '%s'. When collection_type is '%s', it should be one of '%s'",
                    resource_type,
                    self.collection_type,
                    ",".join(allowed_resource_types),
                )
                continue
            metric_filters[resource_type] = filters

        return {k: [re.compile(r) for r in v] for k, v in metric_filters.items()}

    def _normalize_event_resource_filters(self, filters):
        return [filter.lower() for filter in filters]

    @property
    def object_properties_to_collect_by_mor(self):
        return {
            mor_string: object_properties_to_collect(mor_string, self.metric_filters)
            for mor_string in OBJECT_PROPERTIES_BY_RESOURCE_TYPE.keys()
        }

    @property
    def simple_properties_to_collect_by_mor(self):
        return {
            mor_string: simple_properties_to_collect(mor_string, self.metric_filters)
            for mor_string in SIMPLE_PROPERTIES_BY_RESOURCE_TYPE.keys()
        }

    @property
    def property_metrics_to_collect_by_mor(self):
        return {
            mor_string: property_metrics_to_collect(mor_string, self.metric_filters)
            for mor_string in PROPERTY_METRICS_BY_RESOURCE_TYPE.keys()
        }
