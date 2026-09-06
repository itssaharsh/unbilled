# Demo video script — target 3:00, hard cap 5:00

Pre-recorded, pre-seeded, no login, no UI tour, no title card. Lead with the outcome. Record at 1920×1080, OBS on the Windows host capturing the WSLg windows (test first). Voice-over recorded separately if easier. Replace bracketed numbers with the real ones from `evals/results.md`.

| Time | Screen | Voice-over |
|---|---|---|
| 0:00–0:12 | Split screen: June row `Acme Legal — no invoice received — accrual booked $[18,400]` \| July: invoice arrives `$[18,112]`, variance badge flips green **[1.6%]** | "That liability didn't exist when the agent booked it. The invoice showed up a month later, and it was off by [one and a half] percent." |
| 0:12–0:24 | Close calendar + one architecture card: Estimator → confidence gate → Controller → Reflector → Validator → Precedent Ledger | "Accruals are the second-biggest bottleneck in the month-end close; half of finance teams take six days or more. The accountant guesses what hasn't been invoiced yet, and nobody writes down how they guessed." |
| 0:24–0:52 | April close: 12 vendors stream in, variance column red, mean [34%], [10] escalations. Approve 3, Edit 2 with reason *wrong method* + note "Acme bills in arrears at a run rate, not off the PO" | "April. Empty memory. It guesses like a first-week junior." |
| 0:52–1:14 | Reflector fires; delta ops stream into the ledger; Validator banner `canary MAPE [0.31 → 0.19], cost [−8%] → COMMIT`; one card `REJECTED · rolled back · +[0.04] MAPE` | "Every rule has to beat the incumbent on periods where we already know the answer. This close: [nine] committed, [five] rolled back. Memory can't just accumulate — it has to earn its place." |
| 1:14–1:42 | July close: green column, mean [8%], [2] escalations. Click a posted JE → workpaper cites PRE-014 ("learned 2026-05 from Dana's edit on Acme Legal · applied 19×"). Highlight PRE-031 `inferred_from_data`; cut to the sealed file: inferred lag [22] d vs generated [21.4] d | "Nobody told it that. It read twelve months of invoice-arrival dates. And we can check, because that parameter was sealed before the run and the agent never saw it." |
| 1:42–2:06 | Convergence chart: MAPE [34→8%], touches [10→2], $/close [0.25→0.10], pass^2 [0.4→0.85]; memory-OFF flat; validator-OFF noisier; one regression annotated; pre-registration commit hash on screen | "May got worse — a rule over-generalized, the harmful counter fired, it was deprecated. The variance number isn't graded against labels I wrote. It's graded against the invoice that actually arrived." |
| 2:06–2:22 | Reject a proposal → harmful counter ticks → rule greys to deprecated. Unpost an accrual → reversing entry shown. Hand-edit a rule. (If QBO worked: one cut to the sandbox JournalEntry.) | "The memory is the workpaper. An auditor can read the policy. A controller can change it without touching code." |
| 2:22–2:36 | Neatlogs analytics: error rate and cost per trace falling across closes (or the accountant clip if secured) | "Independent traces, same curve." |
| 2:36–2:56 | AO proof beat: pan the kanban board (lane counts + Archive), terminal `ao session ls --all --include-terminated \| wc -l`, `ao orchestrator ls`, `git branch -r \| grep ao/` | "Built in [N] AO sessions — one orchestrator, [N−1] workers, each on its own branch, all in the public repo. A reviewer session caught [a bug] in the validator PR." |
| 2:56–3:00 | Repo URL | "Unbilled. It books the invoice before it arrives — and next month, reality tells it how it did." |

**The one number, said three times:** accrual estimate error [34%] → [8%], measured against the invoices that actually arrived.

**Do not say:** "AI month-end close agent" (it is not a categorization agent), or any metric not in `evals/results.md`.

**Rehearsal checklist (22:15 IST):** data pre-loaded; drawer open/close smooth; the Reject → deprecate moment works on the real ledger; AO board screenshot + terminal outputs captured as stills in case the live pan fails; memorization-control clip on disk; 5 dry runs.
