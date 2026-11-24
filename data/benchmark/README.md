# Embedded benchmark aggregates

These compact aggregate files supply the Analytics page. They are outputs derived from the project benchmark, not a substitute for the source records.

- `policy_comparison.csv`: averages across 30 Monte Carlo replays using the India-grounded synthetic farmer event stream.
- `top_market_arrivals_nov_2021.csv`: top-five market totals derived from the 1,410-row Punjab potato market-day demand profile for November 2021.

Public source: ICTD–IIT Delhi `Commodity_Analysis`, Punjab potato wholesale arrivals (November 2021). Source URLs, input checksum, field limitations, generation assumptions and licence caution are documented in `docs/india_mandi_benchmark_provenance.md`.

Do not label the synthetic farmer-level events or queue results as real farmer records or observed centre performance. The source repository did not include an explicit licence file in the inspected version; confirm permission before redistributing the cleaned source CSV. These aggregate UI exports do not contain the raw source CSV or event-level trace.
