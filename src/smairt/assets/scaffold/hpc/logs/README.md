# HPC Job Records

Scheduler stdout and stderr should normally be written to `results/logs/` so execution
evidence is part of the main audit trail. Use this directory for cluster-specific metadata,
submission notes, resource summaries, or job identifiers that support reproducibility.

Record the cluster, scheduler, allocation, job ID, submission command, environment, source
commit, input data version, and corresponding analysis. Follow institutional rules for logs
that contain sensitive paths or data.
