# Evaluation

This doc tracks how the app behaves on a small set of curated log samples. The goal is **evidence**, not academic rigor: can the parser pick the right format, does the model infer a sensible root cause, and is the suggested fix actionable?

Samples live under `sample_data/` (nginx, syslog). Run analysis via the UI or `POST /api/analyze` with the file.

---

## Summary table

| Sample name      | Log type | Parser used | Expected issue              | Root cause correct? | Suggested fix actionable? | Notes                          |
|------------------|----------|-------------|-----------------------------|---------------------|---------------------------|---------------------------------|
| nginx/example    | Nginx    | NginxParser | Upstream down + disk full   | Yes                 | Yes                       | Connection refused, 502, no space |
| syslog/example   | Syslog   | SyslogParser| OOM kill, SSH fail, DB pool | Yes                 | Partially                 | Mixed BSD + RFC5424; fix quality varies |
| nginx upstream   | Nginx    | NginxParser | Backend connection refused  | Yes                 | Yes                       | Same as README example           |
| nginx disk       | Nginx    | NginxParser | No space left on device      | Yes                 | Yes                       | Single error line                |
| syslog OOM       | Syslog   | SyslogParser| Kernel OOM killing process  | Yes                 | Yes                       | Single line; clear cause         |
| syslog SSH       | Syslog   | SyslogParser| Failed password (auth)      | Yes                 | Yes                       | Security-related                 |
| syslog DB pool   | Syslog   | SyslogParser| Connection pool exhausted   | Yes                 | Yes                       | App-level; actionable fix        |
| syslog disk warn | Syslog   | SyslogParser| Disk usage above 90%        | Yes                 | Yes                       | Warning only                     |
| mixed short      | Mixed    | Auto (Nginx or Syslog) | Depends on first lines | Varies            | Varies                  | Parser hint can help             |

---

## Sample details

### 1. nginx/example.log

- **Log type:** Nginx (error + access).
- **Parser used:** NginxParser (auto-detected from `[error]` / `[warn]` and access pattern).
- **Expected issue:** Upstream connection refused; upstream temporarily disabled; disk full on cache; 502 on `/api/users`; 404 on `/missing`.
- **Model output summary (typical):** Errors and warnings extracted; root cause “upstream down or unreachable” and “no space on device”; fix “check upstream process and disk”.
- **Root cause correct?** Yes.
- **Suggested fix actionable?** Yes (check upstream, health checks, free disk).
- **Notes:** Good stress test: multiple failure modes in one file.

### 2. syslog/example.log

- **Log type:** Syslog (BSD-style + one RFC 5424 line).
- **Parser used:** SyslogParser.
- **Expected issue:** OOM kill, SSH failed password, DB pool exhausted, disk warning, critical timeout.
- **Model output summary (typical):** Multiple root causes (memory, auth, connection pool, disk, timeout); fixes vary in specificity.
- **Root cause correct?** Yes for main issues.
- **Suggested fix actionable?** Partially; some fixes are generic (“restart service”) vs specific (“increase pool size”, “investigate memory”).
- **Notes:** Mixed severity; good for checking that the model doesn’t collapse everything into one cause.

### 3. Nginx upstream only (subset)

- **Log type:** Nginx error + access.
- **Content:** Same as README example (connection refused, upstream disabled, 502).
- **Expected issue:** Backend unreachable.
- **Root cause correct?** Yes.
- **Suggested fix actionable?** Yes.
- **Notes:** Matches the README “before/after” example.

### 4. Nginx disk full (single line)

- **Log type:** Nginx error.
- **Content:** `open() ".../0000000001" failed (28: No space left on device)`.
- **Expected issue:** Disk full.
- **Root cause correct?** Yes.
- **Suggested fix actionable?** Yes (free space, clean cache, monitor disk).
- **Notes:** Single-line case; parser and model should still surface it.

### 5. Syslog OOM (single line)

- **Log type:** Syslog (kernel).
- **Content:** `Out of memory: Kill process 12345 (nginx) score 800 or sacrifice child`.
- **Expected issue:** Out-of-memory kill.
- **Root cause correct?** Yes.
- **Suggested fix actionable?** Yes (tune memory, limits, or scale).
- **Notes:** Very clear cause.

### 6. Syslog SSH failed password

- **Log type:** Syslog (sshd).
- **Content:** `Failed password for root from 10.0.0.1 port 22 ssh2`.
- **Expected issue:** Failed authentication / possible brute force.
- **Root cause correct?** Yes.
- **Suggested fix actionable?** Yes (auth hardening, fail2ban, restrict root).
- **Notes:** Security-sensitive; fix should recommend locking down SSH.

### 7. Syslog DB pool exhausted

- **Log type:** Syslog (app).
- **Content:** `database connection pool exhausted`.
- **Expected issue:** App can’t get DB connections.
- **Root cause correct?** Yes.
- **Suggested fix actionable?** Yes (pool size, timeouts, connection leaks).
- **Notes:** App-level; good test for actionable remediation.

### 8. Syslog disk warning

- **Log type:** Syslog (app).
- **Content:** `warning: disk usage above 90%`.
- **Expected issue:** Disk space warning.
- **Root cause correct?** Yes.
- **Suggested fix actionable?** Yes (cleanup, expand disk, alerts).
- **Notes:** Warning only; should still get a fix suggestion.

### 9. Mixed / short log

- **Log type:** Few lines; may be Nginx or Syslog or plain.
- **Parser used:** Auto-detection (or parser hint if provided).
- **Expected issue:** Depends on content.
- **Root cause correct?** Varies.
- **Suggested fix actionable?** Varies.
- **Notes:** Parser hint (`parser_hint` in API) can improve consistency when format is ambiguous.

---

## How to run and update

1. Use logs from `sample_data/nginx/` and `sample_data/syslog/`.
2. Call `POST /api/analyze` (or use the UI) and capture the response.
3. Fill or update the table above: expected issue, model summary, root cause correct?, fix actionable?, notes.
4. When adding new samples, add a row to the summary table and a short subsection below.

No formal metrics are required; the aim is to show that the system behaves sensibly on real-world-style logs and to spot regressions when changing parsers or prompts.
