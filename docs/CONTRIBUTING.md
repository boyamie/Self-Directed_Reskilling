# Working rules

1. **Append, don't rewrite.** Logs and the protocol are evidence. A correction
   is a new dated entry, not an edit to an old one. `PROTOCOL.md` §6 is the
   amendment log.
2. **Commit the week's log in its own commit,** message `W03 candidate-action
   log`. Gate rulings likewise: `M2 gate ruling (second author)`. Clean
   history is what makes the record readable at review time.
3. **Tag the fixed points.** `w0` before W1; `gate-M1` … `gate-M5` at each
   ruling; `w12` at the end. Tags are what the paper cites.
4. **Never backdate.** `recorded_at` is the real moment of writing. A late
   entry is fine and is reported as late; a backdated one is fabrication.
5. **Run `make validate` before committing.** It catches the failure modes
   that are invisible later.
