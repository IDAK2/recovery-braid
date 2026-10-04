# Recovery Braid

## Read this like a runbook, not a scorecard

An incident may have ten correct actions and still fail because two ran together or one ran before its prerequisite. Recovery Braid freezes an incident, indexed actions, dependency edges, safety constraints, and a maximum number of execution batches. Its output is an executable order, not a prose recommendation.

## The braid

Validators decide which independent actions may safely share a batch. Deterministic checks then take over: every action must appear exactly once, every dependency must finish in an earlier batch, no batch may be empty, and the plan cannot exceed its declared bound. A syntactically complete but semantically unsafe plan is rejected by independent validator review.

Execution proceeds one batch at a time. Any wallet may provide an HTTPS completion receipt, so a missing creator cannot stall recovery. The receipt is fetched inside consensus, its digest is stored in order, and validators must confirm evidence for every action in the current batch before the pointer advances.

## State strip

`OPEN -> EXECUTING -> RECOVERED`

The owner can cancel only an unplanned incident. Once execution begins, batches cannot be skipped, replayed, reordered, or replaced. Unreadable receipts, incomplete evidence, dependency inversions, missing actions, duplicate indexes, unsafe concurrency, and forged digests fail explicitly.

## Test the interlock

```text
genvm-lint contracts/contract.py
python -m pytest -q
```

The suite includes a full four-batch lifecycle plus adversarial coverage for missing actions, duplicates, forward dependencies, unsafe validator output, incomplete receipts, forged approval, replay, duplicate IDs, and unauthorized cancellation.

## Field rehearsal

The canonical StudioNet contract is `0xF966D2968DAE6d00a8197e70d4e687c486119879`. Live recovery `RB-LIVE-20261004B` was opened from the owner wallet, planned through validator consensus, and read back in `EXECUTING` with four dependency-safe batches: fence, verify, promote, restore.

The deployment, initialization, and intelligent-planning transaction hashes live in [`deployment.json`](deployment.json).

