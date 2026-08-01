# Execution Logs

Logs are the canonical raw record of command execution. Generated experiment scripts capture
stdout, stderr, warnings, and uncaught tracebacks in timestamped `.log` files.

Track ordinary text logs in Git so evidence survives commits, clones, and handoffs. Explicitly
ignore a log only when it is sensitive or unreasonably large, and record the reason plus a
safe summary in the corresponding analysis.

Do not edit a raw log to improve the result. Run a corrected experiment and preserve the
relationship among hypothesis, script, input data, log, and analysis.

| Log | Script | Inputs/Version | Exit Status | Analysis | Notes |
|---|---|---|---|---|---|
| [Path] | [Path] | [Data/config] | [Status] | [Path] | [Selected/failed/exploratory] |
