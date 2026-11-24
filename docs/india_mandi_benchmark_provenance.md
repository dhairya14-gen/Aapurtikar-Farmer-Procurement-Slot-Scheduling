# Aapurtikar — Indian Mandi Benchmark Provenance

## Public source used

- Publisher/repository: ICTD–IIT Delhi, `Commodity_Analysis`
- Source commodity: Potato
- State: Punjab, India
- Period: 1–30 November 2021
- Source file: `Data/Original/WholesaleRaw/POTATO/PUNJAB/mynewdata_2021_November.csv`
- Repository: https://github.com/ICTD-IITD/Commodity_Analysis
- Raw source URL: https://raw.githubusercontent.com/ICTD-IITD/Commodity_Analysis/main/Data/Original/WholesaleRaw/POTATO/PUNJAB/mynewdata_2021_November.csv

The cleaned public source profile includes 1,410 market-day records across 81 Punjab markets and 25,582.56 tonnes of reported potato arrivals. The cleaned input SHA-256 recorded by the benchmark package is `bdce7c601133243099902eec22cee4b2577cfbee7141a504d53c009a2b73c6c6`. This is historical aggregate market-day data, not live data. Top-five market totals and the compact policy summary used by the UI are retained under `data/benchmark/`; the raw source CSV and event-level simulation trace are not included in this source package.

## Why the farmer-level stream is synthetic

The public dataset contains market name, date and daily market-level arrival tonnage/price information. It does not contain individual farmer identities, individual arrival timestamps, procurement service-start timestamps, service durations or observed waiting times. To test a farmer-level queue policy without presenting invented records as real, the benchmark generated 10,981 synthetic farmer visit events using explicit assumptions.

- Synthetic farmer count per market-day: `ceil(arrivals_tonnes / 2.5)` with a minimum of one.
- Assumed lot threshold: 2.5 tonnes; individual synthetic lots are not observed lot records.
- Intraday synthetic arrivals: 06:00–14:00 using a morning-weighted Beta(2.2, 2.8) profile.
- Synthetic service duration: lognormal distribution with 15-minute arithmetic mean and coefficient of variation 0.35.
- Primary capacity scenario: eight parallel service bays; this is assumed, not observed.
- Policy comparison: unmanaged FCFS, hourly batches, 30-minute slots and 15-minute staggered slots.
- Monte Carlo replications: 30, using the same generated natural arrival/service sequence within each policy comparison.

## Aggregate results displayed in the app

| Policy | Mean on-site queue wait | P95 on-site queue wait | Mean booking lead | Mean generated-arrival to service-start |
|---|---:|---:|---:|---:|
| FCFS | 8.84 min | 64.17 min | — | 8.84 min |
| Hourly batches | 7.66 min | 41.87 min | 37.79 min | 45.44 min |
| 30-minute slots | 3.31 min | 20.98 min | 23.32 min | 26.63 min |
| 15-minute slots | 1.63 min | 11.51 min | 16.15 min | 17.78 min |

The 15-minute scenario reduces modelled mean on-site queue wait by 81.6% and P95 on-site queue wait by 82.1% relative to FCFS. However, mean booking lead time is 16.15 minutes and mean time from the generated unplanned-arrival reference to service start is 17.78 minutes. The on-site waiting benefit assumes the appointment is issued before the farmer travels; it is not a universal reduction in total elapsed time.

## Public redistribution caution

The inspected upstream ICTD-IIT Delhi repository did not contain an explicit `LICENSE` file. The benchmark retains attribution and source links. Do not assume that the source CSV is licensed for public redistribution; confirm permission before publishing cleaned source records. The application's UI embeds only aggregate summary statistics and does not bundle the cleaned source CSV or synthetic event-level trace.

## Required wording

The data source is real historical Indian mandi arrival-volume data. Farmer-level visits, lot records, service durations, appointment times and wait durations are generated synthetic simulation inputs/outputs. Results are scenario-based and are not observed performance at CMS Kapurthala or any real procurement centre.
