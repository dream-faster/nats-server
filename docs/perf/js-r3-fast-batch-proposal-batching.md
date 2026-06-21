# JS R3 Fast-Batch Proposal Batching

Date: 2026-06-17

## Summary

This report compares `origin/main` against the feature branch `perf/js-r3-fast-batch-propose-multi` for the JetStream R3 fast-batch hot path.

The branch adds stream-layer proposal batching for fast-batch publishes, so the benchmark below targets the fast-batch protocol instead of the ordinary async publish control path.

## Method

Benchmark command:

```sh
go test ./server -run '^$' -bench 'BenchmarkJetStreamFastBatchPublish$' -benchmem -count=1 -benchtime=2s
```

Control benchmark command:

```sh
go test ./server -run '^$' -bench 'BenchmarkJetStreamPublish/N=3,R=3,MsgSz=1024b,Subjs=1/Async\[W:4000\]$' -benchmem -count=1 -benchtime=2s
```

Environment:

- Host: Apple M3
- OS: macOS
- Go package: `./server`
- Stream shape for the fast-batch benchmark: `N=3`, `R=3`, `MsgSz=1024b`, `Subjs=1`, `Batch[W:64]`

## Results

### Fast-batch benchmark

| Target | ns/op | MB/s | B/op | allocs/op |
| --- | ---: | ---: | ---: | ---: |
| `origin/main` | 16200 | 63.21 | 13080 | 30 |
| `perf/js-r3-fast-batch-propose-multi` | 7391 | 138.55 | 13080 | 30 |

Observed speedup on the targeted hot path: `2.19x`.

### Async publish control benchmark

| Target | ns/op | MB/s | B/op | allocs/op |
| --- | ---: | ---: | ---: | ---: |
| `origin/main` | 9941 | 103.01 | 13184 | 54 |
| `perf/js-r3-fast-batch-propose-multi` | 10583 | 96.76 | 11201 | 52 |

This is a control path, not the fast-batch path the change targets. It is included only to show that the branch-specific optimization should be judged on the fast-batch benchmark above.

## Notes

- The fast-batch benchmark is the relevant indicator for this PR because the change batches fast-batch proposals at the stream-to-RAFT boundary.
- The control async benchmark does not exercise the new batching path, so its numbers should not be used as the primary success metric for this work.
