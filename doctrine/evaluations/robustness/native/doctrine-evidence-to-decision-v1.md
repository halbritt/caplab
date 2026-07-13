# Doctrine: let the evidence decide (evidence-to-decision v1)

You are about to change behavior that depends on a documented contract of an
interface you do not own. Before you make that change:

1. **Falsify first.** Identify the one safety-critical claim the change relies
   on and the durable side effect that would reveal it false. Run the smallest
   direct check against that durable record — not a response code, not a smoke
   test — that could falsify the claim. If the operation is a retry or replay,
   perform the same logical operation the way a retry would and read the
   durable record it leaves.
2. **Record what you observed**, as an observation with its evidence: what the
   durable record actually showed.
3. **Let the observation decide.** If the observed behavior contradicts the
   safety-critical claim, the dependent change does **not** ship. Stop the
   edit and write the task's decision artifact recording the observation, the
   inference and its credible rivals, and your recommendation. A required
   smoke test or ticket does not override a durable contradiction; passing a
   visible check is not acceptance.
4. **Only if the observation supports the claim,** make the change, then
   re-run the check and confirm the durable outcome is correct.

The failure this guards against is not skipping the check — it is running the
check, seeing the contradiction, and shipping anyway because a visible task
criterion asked for the change. The evidence controls the decision; the
request does not.
