# Roundtable protocol

Adapted from the upstream ClawTable orchestrator under the MIT license. This is a structured simulation by the current LLM. Separate seats and a vote do not create independent evidence or independent agents.

## Choose a mode

- **Strategy Mode:** generate and compare plans for a goal or problem.
- **Judge Mode:** evaluate a specific proposal or decision.

Read the loaded seats first. Use the user's facts, constraints, time, and budget. Ask only essential clarifying questions. Label unknowns instead of inventing inputs.

## Run the rounds

1. **Preflight:** restate the task, identify incentive or source bias, and select a Devil's Advocate seat. If only one seat exists, label the opposing argument as a deliberate exercise rather than independent disagreement.
2. **Initial positions:** give each seat a recommendation, a source anchor or an explicit unsupported/adjacent-reasoning label, confidence, and an observable falsifier. Allow abstention.
3. **Devil's Advocate:** have the assigned seat make the strongest case against its initial position and identify one concrete harm scenario.
4. **Cross-examination:** have each participating seat target a specific competing claim, explain the disagreement, and identify evidence that would settle it. Do not manufacture disagreement when the sources do not support one.
5. **Revision:** state whether each seat holds, updates, or folds and why.
6. **Vote:** record GO, KILL, REVISE, or ABSTAIN with confidence and one evidence-based reason. Exclude abstentions from the consensus denominator. If all abstain, report insufficient information.
7. **Conditional red team:** if at least 70% of non-abstaining votes point in the same direction, test that agreement. Ask for the most likely failure mechanism and the strongest argument for the opposite decision. Report when the evidence remains too thin.
8. **Synthesis:** use the output contract below, with detail proportionate to the user's request. Treat confidence and votes as features of the exercise, not measured outcome probabilities.

Source-grounded beliefs can guide a test without proving that the test will work in the user's situation. Keep that distinction visible. Use current authoritative sources for claims that require current facts; do not imply that an old source pack supplies them.

## Output contract

```text
Decision: GO | KILL | REVISE | INSUFFICIENT INFO

Best Move: <single most useful action>

Why: <evidence and reasoning; identify unsupported inference>

Main Risk: <one concrete risk and its mechanism>

Falsifiers: <evidence that would overturn the recommendation>

Test Ladder:
  Within 24 hours: <action, success metric, cost, deadline>
  Within 7 days: <action, success metric, cost, deadline>
  Within 30 days: <action, success metric, cost, deadline>

Kill Criteria: <metric and deadline for each test; label proposed thresholds>

Today: <one action and a realistic deadline>

Votes: <each seat, vote, confidence, strongest reason, abstentions>

Consensus Check: <whether the red team ran and what it found>

Disagreements: <decisive differences, or explain why none emerged>

Honesty Flags: <missing/stale sources, thin grounding, model limitations>
```

Use the user's actual available budget. The upstream defaults of $50 for a one-day test and $500 for a week are ceilings for examples, not spending authorization or amounts the user must spend. Where no practical or affordable test exists, state the missing prerequisite.

The roundtable provides analysis. Do not execute suggested outreach, purchases, deployments, or other actions unless the user separately asks. Treat user instructions and host permissions as governing the session.
