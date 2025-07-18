# CHANGELOG - Cilium

<!-- towncrier release notes start -->

## 6.0.0 / 2025-07-10

***Changed***:

* Bump datadog_checks_base to 37.16.0 ([#20711](https://github.com/DataDog/integrations-core/pull/20711))

## 5.2.0 / 2025-02-20 / Agent 7.64.0

***Added***:

* Added Cilium 1.16 metrics ([#19520](https://github.com/DataDog/integrations-core/pull/19520))

## 5.1.0 / 2025-01-16 / Agent 7.63.0

***Added***:

* Add `tls_ciphers` param to integration ([#19334](https://github.com/DataDog/integrations-core/pull/19334))

## 5.0.0 / 2024-10-04 / Agent 7.59.0

***Removed***:

* Remove support for Python 2. ([#18580](https://github.com/DataDog/integrations-core/pull/18580))

***Fixed***:

* Bump the version of datadog-checks-base to 37.0.0 ([#18617](https://github.com/DataDog/integrations-core/pull/18617))

## 4.0.0 / 2024-10-01 / Agent 7.58.0

***Changed***:

* Bump minimum version of base check ([#18733](https://github.com/DataDog/integrations-core/pull/18733))

***Added***:

* Bump the python version from 3.11 to 3.12 ([#18212](https://github.com/DataDog/integrations-core/pull/18212))

## 3.6.0 / 2024-09-05

***Added***:

* Add new metrics with v1.15+ ([#18406](https://github.com/DataDog/integrations-core/pull/18406))

## 3.5.1 / 2024-07-05 / Agent 7.55.0

***Fixed***:

* Update config model names ([#17802](https://github.com/DataDog/integrations-core/pull/17802))

## 3.5.0 / 2024-05-31

***Added***:

* Add support for Cilumn v1.14 metrics ([#17447](https://github.com/DataDog/integrations-core/pull/17447))

***Fixed***:

* Update the description for the `tls_ca_cert` config option to use `openssl rehash` instead of `c_rehash` ([#16981](https://github.com/DataDog/integrations-core/pull/16981))

## 3.4.0 / 2024-02-16 / Agent 7.52.0

***Added***:

* Add additional ipam metrics for Cilium 1.13+ ([#16261](https://github.com/DataDog/integrations-core/pull/16261))
* Update the configuration file to include the new oauth options parameter ([#16835](https://github.com/DataDog/integrations-core/pull/16835))

## 3.3.0 / 2024-01-05 / Agent 7.51.0

***Added***:

* Bump the Python version from py3.9 to py3.11 ([#15997](https://github.com/DataDog/integrations-core/pull/15997))

## 3.2.0 / 2023-11-10 / Agent 7.50.0

***Added***:

* Add more FQDN and L7 metrics ([#16164](https://github.com/DataDog/integrations-core/pull/16164))

## 3.1.0 / 2023-10-26

***Added***:

* Add missing Azure metrics ([#16073](https://github.com/DataDog/integrations-core/pull/16073))

## 3.0.0 / 2023-08-10 / Agent 7.48.0

***Changed***:

* Bump the minimum base check version ([#15427](https://github.com/DataDog/integrations-core/pull/15427))

***Added***:

* Add more kvstore metrics ([#15483](https://github.com/DataDog/integrations-core/pull/15483)) Thanks [antonipp](https://github.com/antonipp).
* Add missing cilium metrics ([#15284](https://github.com/DataDog/integrations-core/pull/15284))
* Update generated config models ([#15212](https://github.com/DataDog/integrations-core/pull/15212))

***Fixed***:

* Fix types for generated config models ([#15334](https://github.com/DataDog/integrations-core/pull/15334))

## 2.4.1 / 2023-07-10 / Agent 7.47.0

***Fixed***:

* Bump Python version from py3.8 to py3.9 ([#14701](https://github.com/DataDog/integrations-core/pull/14701))

## 2.4.0 / 2023-05-26 / Agent 7.46.0

***Added***:

* Add an ignore_connection_errors option to the openmetrics check ([#14504](https://github.com/DataDog/integrations-core/pull/14504))

***Fixed***:

* Add DEFAULT_METRIC_LIMIT for OpenMetrics-based checks ([#14527](https://github.com/DataDog/integrations-core/pull/14527))
* Update minimum datadog base package version ([#14463](https://github.com/DataDog/integrations-core/pull/14463))
* Deprecate `use_latest_spec` option ([#14446](https://github.com/DataDog/integrations-core/pull/14446))

## 2.3.0 / 2022-09-16 / Agent 7.40.0

***Added***:

* Refactor tooling for getting the current env name ([#12939](https://github.com/DataDog/integrations-core/pull/12939))
* Update HTTP config spec templates ([#12890](https://github.com/DataDog/integrations-core/pull/12890))

## 2.2.1 / 2022-05-18 / Agent 7.37.0

***Fixed***:

* Fix extra metrics description example ([#12043](https://github.com/DataDog/integrations-core/pull/12043))

## 2.2.0 / 2022-05-15

***Added***:

* Support dynamic bearer tokens (Bound Service Account Token Volume) ([#11915](https://github.com/DataDog/integrations-core/pull/11915))

## 2.1.0 / 2022-04-05 / Agent 7.36.0

***Added***:

* Add metric_patterns options to filter all metric submission by a list of regexes ([#11695](https://github.com/DataDog/integrations-core/pull/11695))

***Fixed***:

* Remove outdated warning in the description for the `tls_ignore_warning` option ([#11591](https://github.com/DataDog/integrations-core/pull/11591))

## 2.0.0 / 2022-02-19 / Agent 7.35.0

***Changed***:

* Add tls_protocols_allowed option documentation ([#11251](https://github.com/DataDog/integrations-core/pull/11251))

***Added***:

* Add `pyproject.toml` file ([#11324](https://github.com/DataDog/integrations-core/pull/11324))
* Add new operator metrics ([#11193](https://github.com/DataDog/integrations-core/pull/11193))

***Fixed***:

* Fix namespace packaging on Python 2 ([#11532](https://github.com/DataDog/integrations-core/pull/11532))

## 1.10.2 / 2022-01-21 / Agent 7.34.0

***Fixed***:

* Fix license header dates in autogenerated files ([#11187](https://github.com/DataDog/integrations-core/pull/11187))

## 1.10.1 / 2022-01-18

***Fixed***:

* Fix the type of `bearer_token_auth` ([#11144](https://github.com/DataDog/integrations-core/pull/11144))

## 1.10.0 / 2022-01-08

***Added***:

* Support the new OpenMetrics V2 implementation ([#10840](https://github.com/DataDog/integrations-core/pull/10840))

***Fixed***:

* Add comment to autogenerated model files ([#10945](https://github.com/DataDog/integrations-core/pull/10945))

## 1.9.0 / 2021-11-13 / Agent 7.33.0

***Added***:

* Document new include_labels option ([#10617](https://github.com/DataDog/integrations-core/pull/10617))
* Document new use_process_start_time option ([#10601](https://github.com/DataDog/integrations-core/pull/10601))
* Add runtime configuration validation ([#8893](https://github.com/DataDog/integrations-core/pull/8893))

## 1.8.0 / 2021-10-04 / Agent 7.32.0

***Added***:

* Add HTTP option to control the size of streaming responses ([#10183](https://github.com/DataDog/integrations-core/pull/10183))
* Add allow_redirect option ([#10160](https://github.com/DataDog/integrations-core/pull/10160))
* Allow Kubernetes port forwarding to support any resource ([#10127](https://github.com/DataDog/integrations-core/pull/10127))

***Fixed***:

* Fix the description of the `allow_redirects` HTTP option ([#10195](https://github.com/DataDog/integrations-core/pull/10195))

## 1.7.2 / 2021-08-22 / Agent 7.31.0

***Fixed***:

* Re-revert cilium AD change ([#9901](https://github.com/DataDog/integrations-core/pull/9901))

## 1.7.1 / 2021-07-13 / Agent 7.30.0

***Fixed***:

* Revert cilium AD change ([#9683](https://github.com/DataDog/integrations-core/pull/9683))

## 1.7.0 / 2021-07-12

***Added***:

* Update container identifier ([#9512](https://github.com/DataDog/integrations-core/pull/9512))

***Fixed***:

* Use cilium-agent and cilium as autodiscover identifiers ([#9518](https://github.com/DataDog/integrations-core/pull/9518))

## 1.6.0 / 2021-05-28 / Agent 7.29.0

***Added***:

* Support "ignore_tags" configuration ([#9392](https://github.com/DataDog/integrations-core/pull/9392))

## 1.5.3 / 2021-03-07 / Agent 7.27.0

***Fixed***:

* Rename config spec example consumer option `default` to `display_default` ([#8593](https://github.com/DataDog/integrations-core/pull/8593))

## 1.5.2 / 2021-01-25 / Agent 7.26.0

***Fixed***:

* Update prometheus_metrics_prefix documentation ([#8236](https://github.com/DataDog/integrations-core/pull/8236))

## 1.5.1 / 2020-12-11 / Agent 7.25.0

***Fixed***:

* Fix openmetrics integrations config specs ([#8000](https://github.com/DataDog/integrations-core/pull/8000))

## 1.5.0 / 2020-10-31 / Agent 7.24.0

***Added***:

* Sync openmetrics config specs with new option ignore_metrics_by_labels ([#7823](https://github.com/DataDog/integrations-core/pull/7823))
* Add ability to dynamically get authentication information ([#7660](https://github.com/DataDog/integrations-core/pull/7660))

## 1.4.0 / 2020-09-21 / Agent 7.23.0

***Added***:

* Add RequestsWrapper option to support UTF-8 for basic auth ([#7441](https://github.com/DataDog/integrations-core/pull/7441))

***Fixed***:

* Do not render null defaults for config spec example consumer ([#7503](https://github.com/DataDog/integrations-core/pull/7503))
* Update proxy section in conf.yaml ([#7336](https://github.com/DataDog/integrations-core/pull/7336))

## 1.3.0 / 2020-08-10 / Agent 7.22.0

***Added***:

* Add config specs ([#7319](https://github.com/DataDog/integrations-core/pull/7319))

## 1.2.0 / 2020-05-17 / Agent 7.20.0

***Added***:

* Add environment runner for Kubernetes' `kind` ([#6522](https://github.com/DataDog/integrations-core/pull/6522))
* Allow optional dependency installation for all checks ([#6589](https://github.com/DataDog/integrations-core/pull/6589))

## 1.1.0 / 2020-04-04 / Agent 7.19.0

***Added***:

* Add Cilium version metadata ([#5408](https://github.com/DataDog/integrations-core/pull/5408))

***Fixed***:

* Update deprecated imports ([#6088](https://github.com/DataDog/integrations-core/pull/6088))

## 1.0.2 / 2020-01-13 / Agent 7.17.0

***Fixed***:

* Remove unused variables ([#5173](https://github.com/DataDog/integrations-core/pull/5173))

## 1.0.1 / 2019-12-06 / Agent 7.16.1

***Fixed***:

* Raise configuration errors ([#5163](https://github.com/DataDog/integrations-core/pull/5163))

## 1.0.0 / 2019-11-19

***Added***:

* New Integration: Cilium ([#4665](https://github.com/DataDog/integrations-core/pull/4665))
