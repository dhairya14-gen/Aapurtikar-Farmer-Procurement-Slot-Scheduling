/**
 * Reproducible aggregate outputs from the India-grounded synthetic queue benchmark.
 * These are research-simulation results, NOT live or observed farmer/centre data.
 * Raw source data and synthetic event-level trace are not bundled in the public UI.
 */
export const benchmark = {
  source: {
    publisher: 'ICTD–IIT Delhi',
    marketDays: 1410,
    markets: 81,
    arrivalsTonnes: 25582.56,
    period: '1–30 November 2021',
    repositoryUrl: 'https://github.com/ICTD-IITD/Commodity_Analysis',
    rawUrl: 'https://raw.githubusercontent.com/ICTD-IITD/Commodity_Analysis/main/Data/Original/WholesaleRaw/POTATO/PUNJAB/mynewdata_2021_November.csv',
  },
  synthetic: {
    farmerEvents: 10981,
    lotSizeTonnes: 2.5,
    serviceMeanMinutes: 15,
    serviceCv: 0.35,
    intradayProfile: 'Morning-weighted Beta(2.2, 2.8)',
    bays: 8,
    replications: 30,
    window: '06:00–14:00',
  },
  improvement: {
    meanWaitReduction: 81.6,
    p95WaitReduction: 82.1,
  },
  topMarkets: [
    { name: 'Ludhiana', arrivalsTonnes: 9201.00 },
    { name: 'Jalandhar City', arrivalsTonnes: 4104.30 },
    { name: 'Amritsar Mewa Mandi', arrivalsTonnes: 1637.90 },
    { name: 'Khanna', arrivalsTonnes: 1212.10 },
    { name: 'Bathinda', arrivalsTonnes: 816.10 },
  ],
  chartMax: 70,
  marketChartMax: 9201,
  policies: [
    { key: 'fcfs', label: 'FCFS', mean: 8.84, p95: 64.17, worstObserved: 174.64, throughput: 0.965, bookingLead: null, elapsed: 8.84, p5: 0.00 },
    { key: 'hourly', label: 'Hourly batches', mean: 7.66, p95: 41.87, worstObserved: 85.77, throughput: 0.942, bookingLead: 37.79, elapsed: 45.44, p5: 0.00 },
    { key: '30m', label: '30-minute slots', mean: 3.31, p95: 20.98, worstObserved: 59.37, throughput: 0.958, bookingLead: 23.32, elapsed: 26.63, p5: 0.00 },
    { key: '15m', label: '15-minute slots', mean: 1.63, p95: 11.51, worstObserved: 46.08, throughput: 0.961, bookingLead: 16.15, elapsed: 17.78, p5: 0.00 },
  ],
} as const
