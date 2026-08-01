# HPC Guidance

HPC support supplies editable configuration, logging guidance, and SLURM templates. SMAIRT
does not submit, cancel, monitor, synchronize, or manage scheduler jobs.

1. Adapt `config.yaml` to the actual cluster and allocation.
2. Review `templates/slurm_basic.sh` and copy or edit `slurm_job.sh` for the experiment.
3. Submit using your institution's documented scheduler command.
4. Write scheduler output to `results/logs/` and record job metadata in the analysis.
5. Use `scripts/monitor_template.py` only for project-controlled progress files.

Cluster policies, modules, partitions, storage, and notification settings vary. Verify every
directive locally before submission.
