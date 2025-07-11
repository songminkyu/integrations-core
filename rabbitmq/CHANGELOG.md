# CHANGELOG - rabbitmq

<!-- towncrier release notes start -->

## 8.0.0 / 2025-07-10

***Changed***:

* Bump datadog_checks_base to 37.16.0 ([#20711](https://github.com/DataDog/integrations-core/pull/20711))

## 7.2.0 / 2025-04-22 / Agent 7.66.0

***Added***:

* Add support for queue_delivery_metrics group ([#19963](https://github.com/DataDog/integrations-core/pull/19963))

## 7.1.0 / 2025-01-16 / Agent 7.63.0

***Added***:

* Add `tls_ciphers` param to integration ([#19334](https://github.com/DataDog/integrations-core/pull/19334))

## 7.0.0 / 2024-10-04 / Agent 7.59.0

***Removed***:

* Remove support for Python 2. ([#18580](https://github.com/DataDog/integrations-core/pull/18580))

***Fixed***:

* Bump the version of datadog-checks-base to 37.0.0 ([#18617](https://github.com/DataDog/integrations-core/pull/18617))

## 6.0.0 / 2024-10-01 / Agent 7.58.0

***Changed***:

* Bump minimum version of base check ([#18733](https://github.com/DataDog/integrations-core/pull/18733))

***Added***:

* Bump the python version from 3.11 to 3.12 ([#18212](https://github.com/DataDog/integrations-core/pull/18212))

## 5.3.2 / 2024-07-05 / Agent 7.55.0

***Fixed***:

* Update config model names ([#17802](https://github.com/DataDog/integrations-core/pull/17802))

## 5.3.1 / 2024-05-31

***Fixed***:

* Update the description for the `tls_ca_cert` config option to use `openssl rehash` instead of `c_rehash` ([#16981](https://github.com/DataDog/integrations-core/pull/16981))

## 5.3.0 / 2024-04-26 / Agent 7.54.0

***Added***:

* Add details on default node/queue/exchange maximums to the configuration example ([#17344](https://github.com/DataDog/integrations-core/pull/17344))

## 5.2.1 / 2024-03-22 / Agent 7.53.0

***Fixed***:

* Collect metrics that only appear in the detailed endpoint ([#17231](https://github.com/DataDog/integrations-core/pull/17231))

## 5.2.0 / 2024-02-16 / Agent 7.52.0

***Added***:

* Update the configuration file to include the new oauth options parameter ([#16835](https://github.com/DataDog/integrations-core/pull/16835))

## 5.1.0 / 2024-01-05 / Agent 7.51.0

***Added***:

* Bump the Python version from py3.9 to py3.11 ([#15997](https://github.com/DataDog/integrations-core/pull/15997))

## 5.0.0 / 2023-08-10 / Agent 7.48.0

***Changed***:

* Bump the minimum base check version ([#15427](https://github.com/DataDog/integrations-core/pull/15427))

***Added***:

* Update generated config models ([#15212](https://github.com/DataDog/integrations-core/pull/15212))

***Fixed***:

* Fix types for generated config models ([#15334](https://github.com/DataDog/integrations-core/pull/15334))

## 4.1.1 / 2023-07-10 / Agent 7.47.0

***Fixed***:

* Bump Python version from py3.8 to py3.9 ([#14701](https://github.com/DataDog/integrations-core/pull/14701))

## 4.1.0 / 2023-05-26 / Agent 7.46.0

***Added***:

* Add metric limit for rabbitmq ([#14541](https://github.com/DataDog/integrations-core/pull/14541))
* Add an ignore_connection_errors option to the openmetrics check ([#14504](https://github.com/DataDog/integrations-core/pull/14504))

***Fixed***:

* Expand migration docs ([#14549](https://github.com/DataDog/integrations-core/pull/14549))
* Update minimum datadog base package version ([#14463](https://github.com/DataDog/integrations-core/pull/14463))
* Adjust docs and tests based on customer feedback ([#14444](https://github.com/DataDog/integrations-core/pull/14444))
* Deprecate `use_latest_spec` option ([#14446](https://github.com/DataDog/integrations-core/pull/14446))

## 4.0.1 / 2023-03-07 / Agent 7.44.0

***Fixed***:

* Fix autodiscovery config instances ([#14112](https://github.com/DataDog/integrations-core/pull/14112))

## 4.0.0 / 2023-03-03

***Changed***:

* Remove support for /metrics/per-object endpoint ([#13869](https://github.com/DataDog/integrations-core/pull/13869))

***Added***:

* Add autodiscovery for docker containers ([#13960](https://github.com/DataDog/integrations-core/pull/13960))

***Fixed***:

* Improve descriptions of config fields to select objects ([#14045](https://github.com/DataDog/integrations-core/pull/14045))

## 3.3.1 / 2023-01-27

***Fixed***:

* Add validation for `include_aggregated_endpoint` ([#13793](https://github.com/DataDog/integrations-core/pull/13793))

## 3.3.0 / 2023-01-20

***Added***:

* Support RabbitMQ Prometheus Metrics ([#13662](https://github.com/DataDog/integrations-core/pull/13662))
* Add drop unroutable metric ([#13553](https://github.com/DataDog/integrations-core/pull/13553)) Thanks [laststem](https://github.com/laststem).

## 3.2.0 / 2022-09-16 / Agent 7.40.0

***Added***:

* Add new metric to track size of queues in bytes ([#12869](https://github.com/DataDog/integrations-core/pull/12869))
* Update HTTP config spec templates ([#12890](https://github.com/DataDog/integrations-core/pull/12890))

## 3.1.0 / 2022-04-05 / Agent 7.36.0

***Added***:

* Add metric_patterns options to filter all metric submission by a list of regexes ([#11695](https://github.com/DataDog/integrations-core/pull/11695))

***Fixed***:

* Remove outdated warning in the description for the `tls_ignore_warning` option ([#11591](https://github.com/DataDog/integrations-core/pull/11591))

## 3.0.0 / 2022-02-19 / Agent 7.35.0

***Changed***:

* Add tls_protocols_allowed option documentation ([#11251](https://github.com/DataDog/integrations-core/pull/11251))

***Added***:

* Add `pyproject.toml` file ([#11423](https://github.com/DataDog/integrations-core/pull/11423))

***Fixed***:

* Fix namespace packaging on Python 2 ([#11532](https://github.com/DataDog/integrations-core/pull/11532))

## 2.2.1 / 2022-01-08 / Agent 7.34.0

***Fixed***:

* Add comment to autogenerated model files ([#10945](https://github.com/DataDog/integrations-core/pull/10945))

## 2.2.0 / 2021-09-30 / Agent 7.32.0

***Added***:

* Minor refactor ([#10270](https://github.com/DataDog/integrations-core/pull/10270))
* Add HTTP option to control the size of streaming responses ([#10183](https://github.com/DataDog/integrations-core/pull/10183))
* Add allow_redirect option ([#10160](https://github.com/DataDog/integrations-core/pull/10160))

***Fixed***:

* Bump base package dependency ([#10218](https://github.com/DataDog/integrations-core/pull/10218))
* Fix the description of the `allow_redirects` HTTP option ([#10195](https://github.com/DataDog/integrations-core/pull/10195))

## 2.1.0 / 2021-09-17

***Added***:

* Disable generic tags ([#10027](https://github.com/DataDog/integrations-core/pull/10027))

## 2.0.0 / 2021-08-22 / Agent 7.31.0

***Changed***:

* Remove messages for integrations for OK service checks ([#9888](https://github.com/DataDog/integrations-core/pull/9888))

***Fixed***:

* Fix documented default value of `use_legacy_auth_encoding` ([#9880](https://github.com/DataDog/integrations-core/pull/9880))

## 1.18.0 / 2021-06-23 / Agent 7.30.0

***Added***:

* Add runtime configuration validation ([#8976](https://github.com/DataDog/integrations-core/pull/8976))

## 1.17.1 / 2021-03-07 / Agent 7.27.0

***Fixed***:

* Bump minimum base package version ([#8443](https://github.com/DataDog/integrations-core/pull/8443))

## 1.17.0 / 2020-10-31 / Agent 7.24.0

***Added***:

* Add support for named groups in regular expressions ([#7814](https://github.com/DataDog/integrations-core/pull/7814)) Thanks [lkobus](https://github.com/lkobus).
* Add ability to dynamically get authentication information ([#7660](https://github.com/DataDog/integrations-core/pull/7660))
* [doc] Add encoding in log config sample ([#7708](https://github.com/DataDog/integrations-core/pull/7708))

## 1.16.0 / 2020-09-21 / Agent 7.23.0

***Added***:

* Add config specs ([#7467](https://github.com/DataDog/integrations-core/pull/7467))

***Fixed***:

* Ensure basic auth encoding defaults to UTF-8 ([#7451](https://github.com/DataDog/integrations-core/pull/7451))
* Fix style for the latest release of Black ([#7438](https://github.com/DataDog/integrations-core/pull/7438))

## 1.15.1 / 2020-08-10 / Agent 7.22.0

***Fixed***:

* Update ntlm_domain example ([#7118](https://github.com/DataDog/integrations-core/pull/7118))

## 1.15.0 / 2020-06-29 / Agent 7.21.0

***Added***:

* Add note about warning concurrency ([#6967](https://github.com/DataDog/integrations-core/pull/6967))
* Add head_message_timestamp metric ([#6809](https://github.com/DataDog/integrations-core/pull/6809))

***Fixed***:

* Continue check execution when only a few vhosts are unhealthy ([#6954](https://github.com/DataDog/integrations-core/pull/6954))

## 1.14.0 / 2020-05-17 / Agent 7.20.0

***Added***:

* Allow optional dependency installation for all checks ([#6589](https://github.com/DataDog/integrations-core/pull/6589))

## 1.13.1 / 2020-04-04 / Agent 7.19.0

***Fixed***:

* Update deprecated imports ([#6088](https://github.com/DataDog/integrations-core/pull/6088))
* Remove logs sourcecategory ([#6121](https://github.com/DataDog/integrations-core/pull/6121))

## 1.13.0 / 2020-02-22 / Agent 7.18.0

***Added***:

* Add option to disable node metrics in rabbitmq ([#5750](https://github.com/DataDog/integrations-core/pull/5750))

## 1.12.0 / 2020-01-13 / Agent 7.17.0

***Added***:

* Use lazy logging format ([#5398](https://github.com/DataDog/integrations-core/pull/5398))
* Use lazy logging format ([#5377](https://github.com/DataDog/integrations-core/pull/5377))

## 1.11.0 / 2019-12-02 / Agent 7.16.0

***Added***:

* Add version metadata to RabbitMQ check ([#4918](https://github.com/DataDog/integrations-core/pull/4918))

## 1.10.1 / 2019-10-18 / Agent 6.15.0

***Fixed***:

* Fix for rabbit 3.1 queue_totals introduced in #4668 ([#4805](https://github.com/DataDog/integrations-core/pull/4805))

## 1.10.0 / 2019-10-11

***Added***:

* verifies if `root` is dict before doing `.get` ([#4668](https://github.com/DataDog/integrations-core/pull/4668))
* Add option to override KRB5CCNAME env var ([#4578](https://github.com/DataDog/integrations-core/pull/4578))

## 1.9.2 / 2019-09-18

***Fixed***:

* Ignore empty data for metrics limit ([#4544](https://github.com/DataDog/integrations-core/pull/4544))

## 1.9.1 / 2019-08-29 / Agent 6.14.0

***Fixed***:

* Revert "Fix queue, node and echange limit" ([#4467](https://github.com/DataDog/integrations-core/pull/4467))

## 1.9.0 / 2019-08-24

***Added***:

* Add mem_limit to RabbitMQ Checks ([#4250](https://github.com/DataDog/integrations-core/pull/4250)) Thanks [ParthKolekar](https://github.com/ParthKolekar).
* Add requests wrapper to RabbitMQ ([#4257](https://github.com/DataDog/integrations-core/pull/4257))

***Fixed***:

* Fix queue, node and echange limit ([#4108](https://github.com/DataDog/integrations-core/pull/4108))

## 1.8.0 / 2019-05-14 / Agent 6.12.0

***Added***:

* Adhere to code style ([#3561](https://github.com/DataDog/integrations-core/pull/3561))

***Fixed***:

* Fix default log path ([#3611](https://github.com/DataDog/integrations-core/pull/3611))

## 1.7.0 / 2019-01-04 / Agent 6.9.0

***Added***:

* Support Python 3 ([#2791][1])

***Fixed***:

* adds ignore_ssl_warning to rabbit file ([#2706][2])

## 1.6.0 / 2018-11-30 / Agent 6.8.0

***Added***:

* Option to ignore SSL warnings ([#2472][3]) Thanks [tebriel][4].
* Add cluster wide metrics ([#2449][6])

***Fixed***:

* Use raw string literals when \ is present ([#2465][5])

## 1.5.2 / 2018-09-04 / Agent 6.5.0

***Fixed***:

* Add data files to the wheel package ([#1727][7])

## 1.5.1 / 2018-03-23

***Fixed***:

* URL encode queue names that might have special characters like '#' ([#1100][8], thanks [@sylr][9])

## 1.5.0 / 2018-02-13

***Added***:

* begin deprecation of `no_proxy` config flag in favor of `skip_proxy` ([#1057][10])

## 1.4.0 / 2018-01-10

***Added***:

* Add data collection for exchanges ([#176][11]) (Thanks [@wholroyd][12])
* Add a metric illustrating the available disk space ([#902][13]) (Thanks [@dnavre][14])
* If vhosts are listed in the config, the check will only query for those specific vhosts, rather than querying for all of them ([#910][16])
* Add metrics to monitor a cluster. See [#924][17]

***Fixed***:

* Assume a protocol if there isn't one, fixing a bug if you don't use a protocol ([#909][15])

## 1.3.1 / 2017-10-10

***Fixed***:

* Add a key check before updating connection state metric ([#729][18]) (Thanks [@ian28223][19])

## 1.3.0 / 2017-08-28

***Added***:

* Add a metric to get the number of bindings for a queue. See [#674][20]

***Fixed***:

* Set aliveness service to CRITICAL if the rabbitmq server is down. See[#635][21]

## 1.2.0 / 2017-07-18

***Added***:

* Add a metric about the number of connections to rabbitmq. See [#504][22]
* Add custom tags to metrics, event and service checks. See [#506][23]
* Add a metric about the number of each connection states. See [#514][24] (Thanks [@jamescarr][25])

## 1.1.0 / 2017-06-05

***Added***:

* Disable proxy if so-desired. See [#407][26]

## 1.0.0 / 2017-03-22

***Added***:

* adds rabbitmq integration.

[1]: https://github.com/DataDog/integrations-core/pull/2791
[2]: https://github.com/DataDog/integrations-core/pull/2706
[3]: https://github.com/DataDog/integrations-core/pull/2472
[4]: https://github.com/tebriel
[5]: https://github.com/DataDog/integrations-core/pull/2465
[6]: https://github.com/DataDog/integrations-core/pull/2449
[7]: https://github.com/DataDog/integrations-core/pull/1727
[8]: https://github.com/DataDog/integrations-core/issues/1100
[9]: https://github.com/sylr
[10]: https://github.com/DataDog/integrations-core/pull/1057
[11]: https://github.com/DataDog/integrations-core/pull/176
[12]: https://github.com/wholroyd
[13]: https://github.com/DataDog/integrations-core/issues/902
[14]: https://github.com/dnavre
[15]: https://github.com/DataDog/integrations-core/issues/909
[16]: https://github.com/DataDog/integrations-core/issues/910
[17]: https://github.com/DataDog/integrations-core/issues/924
[18]: https://github.com/DataDog/integrations-core/issues/729
[19]: https://github.com/ian28223
[20]: https://github.com/DataDog/integrations-core/issues/674
[21]: https://github.com/DataDog/integrations-core/issues/635
[22]: https://github.com/DataDog/integrations-core/issues/504
[23]: https://github.com/DataDog/integrations-core/issues/506
[24]: https://github.com/DataDog/integrations-core/issues/514
[25]: https://github.com/jamescarr
[26]: https://github.com/DataDog/integrations-core/issues/407
