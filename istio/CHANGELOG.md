# CHANGELOG - istio

<!-- towncrier release notes start -->

## 9.0.0 / 2025-07-10

***Changed***:

* Bump datadog_checks_base to 37.16.0 ([#20711](https://github.com/DataDog/integrations-core/pull/20711))

## 8.1.0 / 2025-01-16 / Agent 7.63.0

***Added***:

* Add `tls_ciphers` param to integration ([#19334](https://github.com/DataDog/integrations-core/pull/19334))

## 8.0.0 / 2024-10-04 / Agent 7.59.0

***Removed***:

* Remove support for Python 2. ([#18580](https://github.com/DataDog/integrations-core/pull/18580))

***Fixed***:

* Bump the version of datadog-checks-base to 37.0.0 ([#18617](https://github.com/DataDog/integrations-core/pull/18617))

## 7.0.0 / 2024-10-01 / Agent 7.58.0

***Changed***:

* Bump minimum version of base check ([#18733](https://github.com/DataDog/integrations-core/pull/18733))

***Added***:

* Bump the python version from 3.11 to 3.12 ([#18212](https://github.com/DataDog/integrations-core/pull/18212))

## 6.1.2 / 2024-07-05 / Agent 7.55.0

***Fixed***:

* Update config model names ([#17802](https://github.com/DataDog/integrations-core/pull/17802))

## 6.1.1 / 2024-05-31

***Fixed***:

* Update the description for the `tls_ca_cert` config option to use `openssl rehash` instead of `c_rehash` ([#16981](https://github.com/DataDog/integrations-core/pull/16981))

## 6.1.0 / 2024-04-26 / Agent 7.54.0

***Added***:

* Add the citadel_server_cert_chain_expiry_timestamp metric ([#17268](https://github.com/DataDog/integrations-core/pull/17268))

## 6.0.0 / 2024-03-22 / Agent 7.53.0

***Changed***:

* Disable `exclude_labels` by default ([#17225](https://github.com/DataDog/integrations-core/pull/17225))

## 5.4.0 / 2024-02-16 / Agent 7.52.0

***Added***:

* Update the configuration file to include the new oauth options parameter ([#16835](https://github.com/DataDog/integrations-core/pull/16835))

## 5.3.0 / 2024-01-05 / Agent 7.51.0

***Added***:

* Bump the Python version from py3.9 to py3.11 ([#15997](https://github.com/DataDog/integrations-core/pull/15997))

## 5.2.0 / 2023-09-29 / Agent 7.49.0

***Added***:

* Add additional Istio metrics ([#15820](https://github.com/DataDog/integrations-core/pull/15820))

## 5.1.0 / 2023-08-18 / Agent 7.48.0

***Added***:

* Add support for namespace in istio check ([#14611](https://github.com/DataDog/integrations-core/pull/14611))

## 5.0.0 / 2023-08-10

***Changed***:

* Bump the minimum base check version ([#15427](https://github.com/DataDog/integrations-core/pull/15427))

***Added***:

* Update generated config models ([#15212](https://github.com/DataDog/integrations-core/pull/15212))

***Fixed***:

* Fix types for generated config models ([#15334](https://github.com/DataDog/integrations-core/pull/15334))

## 4.4.1 / 2023-07-10 / Agent 7.47.0

***Fixed***:

* Bump Python version from py3.8 to py3.9 ([#14701](https://github.com/DataDog/integrations-core/pull/14701))

## 4.4.0 / 2023-05-26 / Agent 7.46.0

***Added***:

* Add an ignore_connection_errors option to the openmetrics check ([#14504](https://github.com/DataDog/integrations-core/pull/14504))

***Fixed***:

* Update minimum datadog base package version ([#14463](https://github.com/DataDog/integrations-core/pull/14463))
* Deprecate `use_latest_spec` option ([#14446](https://github.com/DataDog/integrations-core/pull/14446))

## 4.3.1 / 2023-03-03 / Agent 7.44.0

***Fixed***:

* Add port for merged telemetry endpoint in Istio auto_conf ([#13204](https://github.com/DataDog/integrations-core/pull/13204))

## 4.3.0 / 2022-09-16 / Agent 7.40.0

***Added***:

* Update HTTP config spec templates ([#12890](https://github.com/DataDog/integrations-core/pull/12890))

## 4.2.1 / 2022-05-18 / Agent 7.37.0

***Fixed***:

* Fix extra metrics description example ([#12043](https://github.com/DataDog/integrations-core/pull/12043))

## 4.2.0 / 2022-05-15

***Added***:

* Add more tags to default exclude_labels and disable tag_by_endpoint in autoconf ([#11953](https://github.com/DataDog/integrations-core/pull/11953))
* Support dynamic bearer tokens (Bound Service Account Token Volume) ([#11915](https://github.com/DataDog/integrations-core/pull/11915))

## 4.1.0 / 2022-04-05 / Agent 7.36.0

***Added***:

* Add metric_patterns options to filter all metric submission by a list of regexes ([#11695](https://github.com/DataDog/integrations-core/pull/11695))
* Add image for OpenShift Service Mesh Proxy to ad_identifiers ([#11662](https://github.com/DataDog/integrations-core/pull/11662))

***Fixed***:

* Remove outdated warning in the description for the `tls_ignore_warning` option ([#11591](https://github.com/DataDog/integrations-core/pull/11591))

## 4.0.0 / 2022-02-19 / Agent 7.35.0

***Changed***:

* Add tls_protocols_allowed option documentation ([#11251](https://github.com/DataDog/integrations-core/pull/11251))

***Added***:

* Add `pyproject.toml` file ([#11374](https://github.com/DataDog/integrations-core/pull/11374))

***Fixed***:

* Fix namespace packaging on Python 2 ([#11532](https://github.com/DataDog/integrations-core/pull/11532))

## 3.17.2 / 2022-01-21 / Agent 7.34.0

***Fixed***:

* Fix license header dates in autogenerated files ([#11187](https://github.com/DataDog/integrations-core/pull/11187))

## 3.17.1 / 2022-01-18

***Fixed***:

* Fix the type of `bearer_token_auth` ([#11144](https://github.com/DataDog/integrations-core/pull/11144))

## 3.17.0 / 2022-01-08

***Added***:

* Support istio_agent metrics in sidecars ([#10702](https://github.com/DataDog/integrations-core/pull/10702))

***Fixed***:

* Add comment to autogenerated model files ([#10945](https://github.com/DataDog/integrations-core/pull/10945))

## 3.16.0 / 2021-11-13 / Agent 7.33.0

***Added***:

* Document new include_labels option ([#10617](https://github.com/DataDog/integrations-core/pull/10617))
* Document new use_process_start_time option ([#10601](https://github.com/DataDog/integrations-core/pull/10601))
* Update Istio to use OpenMetrics v2 by default ([#10304](https://github.com/DataDog/integrations-core/pull/10304))

## 3.15.0 / 2021-10-04 / Agent 7.32.0

***Added***:

* Add HTTP option to control the size of streaming responses ([#10183](https://github.com/DataDog/integrations-core/pull/10183))
* Add allow_redirect option ([#10160](https://github.com/DataDog/integrations-core/pull/10160))
* Allow Kubernetes port forwarding to support any resource ([#10127](https://github.com/DataDog/integrations-core/pull/10127))
* Disable generic tags ([#10027](https://github.com/DataDog/integrations-core/pull/10027))
* Enable exclude_labels and update documentation ([#10020](https://github.com/DataDog/integrations-core/pull/10020))

***Fixed***:

* Fix the description of the `allow_redirects` HTTP option ([#10195](https://github.com/DataDog/integrations-core/pull/10195))

## 3.14.0 / 2021-08-22 / Agent 7.31.0

***Added***:

* Allow the use of the new OpenMetrics implementation ([#9588](https://github.com/DataDog/integrations-core/pull/9588))
* Use `display_default` as a fallback for `default` when validating config models ([#9739](https://github.com/DataDog/integrations-core/pull/9739))

## 3.13.0 / 2021-07-12 / Agent 7.30.0

***Added***:

* Add more pilot metrics ([#9337](https://github.com/DataDog/integrations-core/pull/9337)) Thanks [hari2192](https://github.com/hari2192).

***Fixed***:

* Bump base package requirement ([#9606](https://github.com/DataDog/integrations-core/pull/9606))

## 3.12.0 / 2021-05-28 / Agent 7.29.0

***Added***:

* Support "ignore_tags" configuration ([#9392](https://github.com/DataDog/integrations-core/pull/9392))

***Fixed***:

* Fix `metrics` option type for legacy OpenMetrics config spec ([#9318](https://github.com/DataDog/integrations-core/pull/9318)) Thanks [jejikenwogu](https://github.com/jejikenwogu).

## 3.11.0 / 2021-04-19 / Agent 7.28.0

***Added***:

* Update defaults for legacy OpenMetrics config spec template ([#9065](https://github.com/DataDog/integrations-core/pull/9065))
* Add runtime configuration validation ([#8939](https://github.com/DataDog/integrations-core/pull/8939))

## 3.10.0 / 2021-03-07 / Agent 7.27.0

***Added***:

* Add sidecar injection failed and skipped metrics ([#8751](https://github.com/DataDog/integrations-core/pull/8751))

## 3.9.1 / 2021-02-26

***Fixed***:

* Allow custom metrics for legacy istio ([#8700](https://github.com/DataDog/integrations-core/pull/8700))
* Rename config spec example consumer option `default` to `display_default` ([#8593](https://github.com/DataDog/integrations-core/pull/8593))

## 3.9.0 / 2021-01-24 / Agent 7.26.0

***Added***:

* Revert "Update base package pin (#8426)" ([#8436](https://github.com/DataDog/integrations-core/pull/8436))

***Fixed***:

* Remove class substitution logic for new OpenMetrics base class ([#8435](https://github.com/DataDog/integrations-core/pull/8435))

## 3.8.0 / 2021-01-22

***Added***:

* Update base package pin ([#8426](https://github.com/DataDog/integrations-core/pull/8426))

***Fixed***:

* Update prometheus_metrics_prefix documentation ([#8236](https://github.com/DataDog/integrations-core/pull/8236))

## 3.7.0 / 2020-10-31 / Agent 7.24.0

***Added***:

* Sync openmetrics config specs with new option ignore_metrics_by_labels ([#7823](https://github.com/DataDog/integrations-core/pull/7823))
* Add ability to dynamically get authentication information ([#7660](https://github.com/DataDog/integrations-core/pull/7660))

***Fixed***:

* Update default port ([#7796](https://github.com/DataDog/integrations-core/pull/7796))

## 3.6.0 / 2020-09-21 / Agent 7.23.0

***Added***:

* Add RequestsWrapper option to support UTF-8 for basic auth ([#7441](https://github.com/DataDog/integrations-core/pull/7441))

***Fixed***:

* Update proxy section in conf.yaml ([#7336](https://github.com/DataDog/integrations-core/pull/7336))

## 3.5.0 / 2020-08-10 / Agent 7.22.0

***Added***:

* Support "*" wildcard in type_overrides configuration ([#7071](https://github.com/DataDog/integrations-core/pull/7071))

***Fixed***:

* DOCS-838 Template wording ([#7038](https://github.com/DataDog/integrations-core/pull/7038))
* Update ntlm_domain example ([#7118](https://github.com/DataDog/integrations-core/pull/7118))

## 3.4.0 / 2020-06-29 / Agent 7.21.0

***Added***:

* Add note about warning concurrency ([#6967](https://github.com/DataDog/integrations-core/pull/6967))

***Fixed***:

* Fix template specs typos ([#6912](https://github.com/DataDog/integrations-core/pull/6912))

## 3.3.0 / 2020-06-09

***Added***:

* Enable `send_monotonic_with_gauge` to submit mesh metrics as monotonic counts ([#5707](https://github.com/DataDog/integrations-core/pull/5707))

## 3.2.1 / 2020-05-22 / Agent 7.20.0

***Fixed***:

* Remove `destination_service` and `source_workload` from label blacklist ([#6712](https://github.com/DataDog/integrations-core/pull/6712))

## 3.2.0 / 2020-05-17

***Added***:

* Allow optional dependency installation for all checks ([#6589](https://github.com/DataDog/integrations-core/pull/6589))
* Add TCP mesh metrics mapping ([#6466](https://github.com/DataDog/integrations-core/pull/6466))

## 3.1.0 / 2020-04-23

***Added***:

* Add autodiscovery config and default tag exclusion ([#6375](https://github.com/DataDog/integrations-core/pull/6375))
* Support istiod metrics ([#6426](https://github.com/DataDog/integrations-core/pull/6426))
* Refactor to support different versions of istio ([#6360](https://github.com/DataDog/integrations-core/pull/6360))
* Add configuration template spec ([#6320](https://github.com/DataDog/integrations-core/pull/6320))
* Refactor check and support new Agent signature ([#6341](https://github.com/DataDog/integrations-core/pull/6341))

## 3.0.0 / 2020-04-04 / Agent 7.19.0

***Changed***:

* Blacklist metric `mcp_source.request_acks_total` due to high cardinality ([#6185](https://github.com/DataDog/integrations-core/pull/6185))

***Fixed***:

* Update deprecated imports ([#6088](https://github.com/DataDog/integrations-core/pull/6088))
* Do not fail on octet stream content type for OpenMetrics ([#5843](https://github.com/DataDog/integrations-core/pull/5843))

## 2.4.2 / 2019-08-26 / Agent 6.14.0

***Fixed***:

* Blacklist `galley_mcp_source_message_size_bytes` histogram ([#4433](https://github.com/DataDog/integrations-core/pull/4433))

## 2.4.1 / 2019-07-16 / Agent 6.13.0

***Fixed***:

* Comment out mixer and mesh by default from configuration ([#4121](https://github.com/DataDog/integrations-core/pull/4121))

## 2.4.0 / 2019-06-24

***Added***:

* Support citadel endpoint ([#3962](https://github.com/DataDog/integrations-core/pull/3962))

## 2.3.1 / 2019-06-19

***Fixed***:

* Istio Mixer and Mesh endpoints should be optional ([#3875](https://github.com/DataDog/integrations-core/pull/3875)) Thanks [mikekatica](https://github.com/mikekatica).

## 2.3.0 / 2019-05-31 / Agent 6.12.0

***Added***:

* Support pilot and galley metrics ([#3734](https://github.com/DataDog/integrations-core/pull/3734))

## 2.2.0 / 2019-05-14

***Added***:

* Adhere to code style ([#3522](https://github.com/DataDog/integrations-core/pull/3522))

## 2.1.0 / 2019-02-18 / Agent 6.10.0

***Added***:

* Support Python 3 ([#3014](https://github.com/DataDog/integrations-core/pull/3014))

***Fixed***:

* Update example config to match docs ([#3046](https://github.com/DataDog/integrations-core/pull/3046))

## 2.0.0 / 2018-09-04 / Agent 6.5.0

***Changed***:

* Update istio to use the new OpenMetricsBaseCheck ([#1979][1])

***Added***:

* Limit Prometheus/OpenMetrics checks to 2000 metrics per run by default ([#2093][2])
* Update istio mapped metrics ([#1993][3]) Thanks [bobbytables][4].

***Fixed***:

* Add data files to the wheel package ([#1727][5])

## 1.1.0 / 2018-06-07

***Added***:

* Support for gathering metrics from prometheus endpoint for the kubelet itself. ([#1581][6])

## 1.0.0 / 2018-03-23

***Added***:

* Adds Istio Integration

[1]: https://github.com/DataDog/integrations-core/pull/1979
[2]: https://github.com/DataDog/integrations-core/pull/2093
[3]: https://github.com/DataDog/integrations-core/pull/1993
[4]: https://github.com/bobbytables
[5]: https://github.com/DataDog/integrations-core/pull/1727
[6]: https://github.com/DataDog/integrations-core/pull/1581
