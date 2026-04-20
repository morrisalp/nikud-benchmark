# nikud-benchmark

Benchmark for Hebrew diacritization (nikud). Gold data in `data/gold.tsv` (`plain`, `nikud` columns). Model predictions in `data/preds.tsv` (one column per model).

## Scripts

```
uv run src/stats.py           # dataset statistics (word counts, diacritics by type)
uv run src/check_integrity.py # verify nikud matches plain (ktiv male/haser)
uv run src/metrics.py         # WER, CER, DER, EM — per sample and aggregated
```

Metrics apply NFC + sorted-diacritics normalization before comparison (Hebrew combining marks share Unicode combining class 220, so NFC alone leaves their order undefined).
