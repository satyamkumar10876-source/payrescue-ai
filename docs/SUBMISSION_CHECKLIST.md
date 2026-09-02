# Razorpay Buildathon Submission Checklist

## Completed In This Repo

- Working Flask product demo.
- Manual merchant payment-case input form.
- Synthetic dataset with 1,000 payment cases.
- Trust-safe recovery agent.
- Payment-limbo and late-authorisation risk detection.
- Downtime/degradation-aware decisioning.
- Guardrail engine for unsafe money actions.
- Audit trail with signals, confidence, reason, decision, and guardrail.
- Webhook Timeline Simulator for explaining payment lifecycle.
- Metrics dashboard with:
  - accuracy
  - recovery precision
  - recovery recall
  - recovered revenue
  - protected revenue
  - duplicate debit prevention
  - false positive cost
  - human review cases
- Architecture documentation.
- Metrics documentation.
- Five-minute pitch script.
- Local tests and compile checks.

## Still Needed Before Final Submission

- Public GitHub repository upload.
- Five-minute pitch video link.
- Optional screenshots in README.
- Optional architecture diagram image.

## Recommended Video Proof

Show these exact flows:

1. Run the app locally.
2. Click `Run Recovery Agent`.
3. Add a custom payment-limbo case:
   - UPI
   - failed or pending
   - payment timed out
   - UPI/auth completed
   - customer reported debit
   - webhook not received
   - downtime active
4. Show the agent blocks retry and chooses `WAIT_FOR_STATUS`.
5. Open the audit trail and explain why.
6. Show the Webhook Timeline Simulator.
7. Show metrics: recovered revenue, protected revenue, accuracy, precision, recall, false positive cost.

## Honest Limitation

This demo uses synthetic payment data. In production, Razorpay-style payment attempts, webhooks, downtime signals, and support signals would feed the same decision pipeline automatically.
