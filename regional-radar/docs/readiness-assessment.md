# Regional Radar: Readiness Assessment

Generated 2026-10-08 21:56 UTC from public data by `scripts/readiness_report.py`. No LLM was used; every number comes from the scoring rules in `app/sentinel_tools.py`.

*Early indicators for readiness planning, not outage predictions.*

## Risk by region

| Region | Location | Level | Score | Drivers |
|---|---|---|---|---|
| asia-south1 | Mumbai, India | 🟠 Elevated | 30 | calendar, weather |
| us-east1 | Moncks Corner, South Carolina | 🟠 Elevated | 20 | weather |
| us-central1 | Council Bluffs, Iowa | 🟠 Elevated | 20 | weather |
| us-west1 | The Dalles, Oregon | 🟠 Elevated | 20 | weather |
| us-west3 | Salt Lake City, Utah | 🟠 Elevated | 20 | weather |
| us-west4 | Las Vegas, Nevada | 🟠 Elevated | 20 | weather |
| europe-west4 | Eemshaven, Netherlands | 🟠 Elevated | 20 | weather |
| europe-west9 | Paris, France | 🟠 Elevated | 20 | unrest |
| asia-northeast1 | Tokyo, Japan | 🟠 Elevated | 20 | unrest |
| asia-southeast1 | Jurong West, Singapore | 🟠 Elevated | 10 | calendar |
| us-east4 | Ashburn, Virginia | 🟢 Low | 0 | none |
| us-east5 | Columbus, Ohio | 🟢 Low | 0 | none |
| us-south1 | Dallas, Texas | 🟢 Low | 0 | none |
| us-west2 | Los Angeles, California | 🟢 Low | 0 | none |
| northamerica-northeast1 | Montreal, Canada | 🟢 Low | 0 | none |
| northamerica-northeast2 | Toronto, Canada | 🟢 Low | 0 | none |
| southamerica-east1 | Sao Paulo, Brazil | 🟢 Low | 0 | none |
| europe-west1 | St. Ghislain, Belgium | 🟢 Low | 0 | none |
| europe-west2 | London, UK | 🟢 Low | 0 | none |
| europe-west3 | Frankfurt, Germany | 🟢 Low | 0 | none |
| australia-southeast1 | Sydney, Australia | 🟢 Low | 0 | none |

```
Readiness risk score by region (0-100)

asia-south1             │ ████████████████████████████ 30 pts
us-east1                │ ███████████████████ 20 pts
us-central1             │ ███████████████████ 20 pts
us-west1                │ ███████████████████ 20 pts
us-west3                │ ███████████████████ 20 pts
us-west4                │ ███████████████████ 20 pts
europe-west4            │ ███████████████████ 20 pts
europe-west9            │ ███████████████████ 20 pts
asia-northeast1         │ ███████████████████ 20 pts
asia-southeast1         │ █████████ 10 pts
us-east4                │ ▏ 0 pts
us-east5                │ ▏ 0 pts
us-south1               │ ▏ 0 pts
us-west2                │ ▏ 0 pts
northamerica-northeast1 │ ▏ 0 pts
```

## Top regions in detail

### asia-south1 (Mumbai, India): 🟠 Elevated, score 30

- **Demand:** no retail terms among the top rising searches, week of 2026-10-04. Top rising: slotin.fit, dewiqis.lol, france vs belgium
- **Calendar:** Diwali in 31 days
- **Weather (2026-10-08 to 2026-10-14):** heat 38.1 °C on 2026-10-09 (Elevated)
- **Unrest, country (India):** 16.0% of news events were protest or conflict in the last 7 days vs 13.0% over the prior 30 (ratio 1.23, data through 2026-10-08)

```
asia-south1 forecast peak wind gust by day (km/h)

10-08 │ ██████████████████████ 30.6 km/h
10-09 │ ███████████████████████ 32.8 km/h
10-10 │ ███████████████████ 26.3 km/h
10-11 │ █████████████████████ 29.5 km/h
10-12 │ █████████████████████████ 35.3 km/h
10-13 │ █████████████████████████ 35.3 km/h
10-14 │ ████████████████████████████ 39.2 km/h
```

```
asia-south1 protest/conflict share of GDELT news events, country (India)

Trend: ▁▁▂▄▂▂▁▃█▃▃▆▅▃▃▆▆▆▄▅▄

09-17 │ ████████████████ 10.7%
09-18 │ █████████████████ 11.4%
09-19 │ ███████████████████ 12.7%
09-20 │ █████████████████████ 14.6%
09-21 │ ██████████████████ 12.4%
09-22 │ ███████████████████ 13.0%
09-23 │ █████████████████ 11.8%
09-24 │ ████████████████████ 13.9%
09-25 │ ████████████████████████████ 19.2%
09-26 │ █████████████████████ 14.3%
09-27 │ ████████████████████ 13.7%
09-28 │ █████████████████████████ 17.2%
09-29 │ ███████████████████████ 15.6%
09-30 │ ████████████████████ 13.7%
10-01 │ █████████████████████ 14.2%
10-02 │ ██████████████████████████ 17.5%
10-03 │ █████████████████████████ 17.2%
10-04 │ █████████████████████████ 16.9%
10-05 │ ██████████████████████ 15.2%
10-06 │ ████████████████████████ 16.6%
10-07 │ ██████████████████████ 15.1%
```

```
Top rising searches, IN: regions where rising

slotin.fit            │ ████████████████████████████ 36
dewiqis.lol           │ ████████████████████████████ 36
france vs belgium     │ ████████████████████████████ 36
world space week 2026 │ ████████████████████████████ 36
argentina vs benin    │ ████████████████████████████ 36
kamil pooran          │ ████████████████████████████ 36
india vs uruguay      │ ████████████████████████████ 36
mawarusf.ink          │ ████████████████████████████ 36
```

### us-east1 (Moncks Corner, South Carolina): 🟠 Elevated, score 20

- **Demand:** no retail terms among the top rising searches, week of 2026-10-04. Top rising: saints vs falcons, freddie jackson, world space week 2026
- **Calendar:** Black Friday in 50 days, Cyber Monday in 53 days
- **Weather (2026-10-08 to 2026-10-14):** wind gusts 64.1 km/h on 2026-10-10 (Elevated)
- **Unrest, state (Moncks Corner, South Carolina):** 17.3% of news events were protest or conflict in the last 7 days vs 17.8% over the prior 30 (ratio 0.97, data through 2026-10-08)

```
us-east1 forecast peak wind gust by day (km/h)

10-08 │ ██████ 14.4 km/h
10-09 │ ██████████████ 32.8 km/h
10-10 │ ████████████████████████████ 64.1 km/h
10-11 │ ██████████████████ 41 km/h
10-12 │ █████████████████ 39.2 km/h
10-13 │ █████████ 20.2 km/h
10-14 │ ███ 6.5 km/h
```

```
us-east1 protest/conflict share of GDELT news events, state (Moncks Corner, South Carolina)

Trend: ▁▅▄▃▂▁▂▃▃█▁▂▃▃▃▃▁▁▁▃▃

09-17 │ ████████████ 12.4%
09-18 │ █████████████████████ 22.3%
09-19 │ ███████████████████ 19.9%
09-20 │ ████████████████ 16.8%
09-21 │ █████████████ 14.0%
09-22 │ ██████████ 11.2%
09-23 │ █████████████ 14.2%
09-24 │ ██████████████████ 18.7%
09-25 │ ██████████████████ 19.0%
09-26 │ ████████████████████████████ 29.9%
09-27 │ ████████████ 13.0%
09-28 │ ███████████████ 15.8%
09-29 │ █████████████████ 18.4%
09-30 │ █████████████████ 18.0%
10-01 │ █████████████████ 18.2%
10-02 │ ██████████████████ 18.7%
10-03 │ ███████████ 11.3%
10-04 │ ███████████ 11.4%
10-05 │ █████████████ 13.8%
10-06 │ ██████████████████ 19.1%
10-07 │ █████████████████ 18.4%
```

```
Top rising searches, US: metro areas (DMAs) where rising

saints vs falcons     │ ████████████████████████████ 210
freddie jackson       │ ████████████████████████████ 210
world space week 2026 │ ████████████████████████████ 210
eames                 │ ████████████████████████████ 210
argentina vs benin    │ ████████████████████████████ 210
france vs belgium     │ ████████████████████████████ 210
pianoforte            │ ████████████████████████████ 210
steve gleason         │ ████████████████████████████ 210
```

### us-central1 (Council Bluffs, Iowa): 🟠 Elevated, score 20

- **Demand:** no retail terms among the top rising searches, week of 2026-10-04. Top rising: saints vs falcons, freddie jackson, world space week 2026
- **Calendar:** Black Friday in 50 days, Cyber Monday in 53 days
- **Weather (2026-10-08 to 2026-10-14):** wind gusts 81.4 km/h on 2026-10-14 (Elevated)
- **Unrest, state (Council Bluffs, Iowa):** 12.9% of news events were protest or conflict in the last 7 days vs 11.7% over the prior 30 (ratio 1.1, data through 2026-10-08)

```
us-central1 forecast peak wind gust by day (km/h)

10-08 │ █████████ 24.8 km/h
10-09 │ ███████████ 32.4 km/h
10-10 │ ██████████████████ 53.7 km/h
10-11 │ ████████████████████ 59.4 km/h
10-12 │ █████████████████████ 60.5 km/h
10-13 │ █████████████ 36.7 km/h
10-14 │ ████████████████████████████ 81.4 km/h
```

```
us-central1 protest/conflict share of GDELT news events, state (Council Bluffs, Iowa)

Trend: ▅▄▃▂▃▄▆▅█▄▂▃▃▅▅▅▁▄▅▆▅

09-17 │ ██████████████████████ 13.7%
09-18 │ ██████████████████ 11.1%
09-19 │ ███████████████ 9.4%
09-20 │ ██████████████ 8.5%
09-21 │ ████████████████ 9.8%
09-22 │ ██████████████████ 11.2%
09-23 │ █████████████████████████ 15.4%
09-24 │ ██████████████████████ 13.7%
09-25 │ ████████████████████████████ 17.5%
09-26 │ ████████████████████ 12.3%
09-27 │ █████████████ 8.3%
09-28 │ ████████████████ 9.9%
09-29 │ ███████████████ 9.6%
09-30 │ ██████████████████████ 13.8%
10-01 │ █████████████████████ 13.4%
10-02 │ ██████████████████████ 13.5%
10-03 │ ██████████ 6.0%
10-04 │ ███████████████████ 11.6%
10-05 │ █████████████████████ 13.1%
10-06 │ ███████████████████████ 14.6%
10-07 │ ██████████████████████ 13.6%
```

```
Top rising searches, US: metro areas (DMAs) where rising

saints vs falcons     │ ████████████████████████████ 210
freddie jackson       │ ████████████████████████████ 210
world space week 2026 │ ████████████████████████████ 210
eames                 │ ████████████████████████████ 210
argentina vs benin    │ ████████████████████████████ 210
france vs belgium     │ ████████████████████████████ 210
pianoforte            │ ████████████████████████████ 210
steve gleason         │ ████████████████████████████ 210
```

## Recommended actions

1. Review regional quotas in asia-south1 and request increases ahead of the peak ([docs](https://cloud.google.com/docs/quotas/view-manage)). *Owner: Customer platform team, TAM to track.* Applies to: asia-south1.
2. Secure capacity with future reservations for the peak window ([docs](https://cloud.google.com/compute/docs/instances/future-reservations-overview)). *Owner: Customer platform team.* Applies to: asia-south1, asia-southeast1.
3. Load-test and raise autoscaler max limits so scale-out is not capped ([docs](https://cloud.google.com/kubernetes-engine/docs/concepts/cluster-autoscaler)). *Owner: Customer SRE.* Applies to: asia-south1, asia-southeast1.
4. Agree a code-freeze window and enforce it with Cloud Deploy deploy policies ([docs](https://cloud.google.com/deploy/docs/deploy-policy)). *Owner: Customer release management.* Applies to: asia-south1, asia-southeast1.
5. Add Cloud Armor rate limiting to absorb bot and scalper traffic ([docs](https://cloud.google.com/armor/docs/rate-limiting-overview)). *Owner: Customer security team.* Applies to: asia-south1, asia-southeast1.
6. Register the event with Google Cloud support for event management ([docs](https://cloud.google.com/support/docs/premium)). *Owner: TAM.* Applies to: asia-south1, asia-southeast1.
7. Walk through the DR runbook and confirm failover to a second region is tested ([docs](https://cloud.google.com/architecture/dr-scenarios-planning-guide)). *Owner: Customer SRE, TAM to facilitate.* Applies to: asia-south1, us-east1, us-central1, us-west1, us-west3, us-west4, europe-west4.
8. Confirm on-call coverage for staff and offices in the affected area ([docs](https://cloud.google.com/architecture/dr-scenarios-planning-guide)). *Owner: Customer operations.* Applies to: asia-south1, us-east1, us-central1, us-west1, us-west3, us-west4, europe-west4.
9. Review multi-region traffic steering so user traffic can shift away quickly ([docs](https://cloud.google.com/architecture/dr-scenarios-planning-guide)). *Owner: Customer SRE.* Applies to: europe-west9, asia-northeast1.
10. Subscribe incident channels to the Google Cloud status dashboard ([docs](https://status.cloud.google.com/)). *Owner: Customer operations.* Applies to: europe-west9, asia-northeast1.
11. Review regional quotas in asia-southeast1 and request increases ahead of the peak ([docs](https://cloud.google.com/docs/quotas/view-manage)). *Owner: Customer platform team, TAM to track.* Applies to: asia-southeast1.
12. No special action this week; keep the standard ORR cadence ([docs](https://cloud.google.com/architecture/dr-scenarios-planning-guide)). *Owner: TAM.* Applies to: us-east4, us-east5, us-south1, us-west2, northamerica-northeast1, northamerica-northeast2, southamerica-east1, europe-west1, europe-west2, europe-west3, australia-southeast1.

## Sources

- Google Trends top rising terms (bigquery-public-data.google_trends), weekly
- GDELT 2.0 events (gdelt-bq.gdeltv2), daily
- Open-Meteo 7-day forecast (open-meteo.com)
- Published retail peak-event dates
