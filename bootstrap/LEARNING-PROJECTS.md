# Learning Projects — the enterprise-infra-as-learning-vehicle exception

Routed from `ONBOARD.md` Step 3. Read this when the user's goal is to learn a technology rather than ship a product.

## Why this matters

Framework's default is "don't build what already exists as a platform" (see Convention #0). But learning a specific technology is a legitimate reason to use a custom stack that would otherwise be overkill. The technology choice IS the point.

This applies to any enterprise-infra-as-learning-vehicle: Kubernetes, Kafka, Istio, service mesh, stream processing, distributed systems, microservices orchestration, etc. Pattern is the same.

## Proactive Detection

If the user's OPENING message declares enterprise or complex infrastructure (any of the above, plus Redis, multi-region, self-managed clusters) for a personal-scale or small-scale project (one user, a blog, a personal tool, a portfolio), ask the ship-vs-learn question in your FIRST reply, not after red flags fire in later turns. Pattern: solo + enterprise-infra = learning intent >80% of the time.

Example first-reply script:
> "Stack noted — [their declared stack]. Before I proceed, one question that shapes everything: your opener combines solo user + enterprise infrastructure for a [small-scale project]. That combination is almost always one of two things: (a) you're optimizing for shipping and the stack is overkill — a platform or lighter stack ships in a weekend, or (b) this is an excuse to learn [technology] and the project is the vehicle. Both are legit, but they lead to very different recommendations. Which is it?"

## Learning Exception Flow

If user confirms learning intent:

1. **Skip Step 3 platform-vs-custom research.** The technology choice is the point, not a mistake.
2. **Scale-vs-cost still matters.** Custom stacks for learning can still be expensive. Recommend the cheapest way to exercise the target technology:
   - Learning Kubernetes: use kind, minikube, or k3s locally (free) before EKS / GKE / AKS (monthly floor).
   - Learning Kafka: use local docker-compose or Redpanda single-node before managed Kafka (Confluent, AWS MSK).
   - Learning service mesh: use local kind + linkerd before managed cloud options.
   - Research current cheapest-tier tooling for the specific technology at bootstrap time.
3. **Surface the cost of the learning exercise explicitly.** Quote the approximate delta between local learning and cloud learning. User makes an informed decision.
4. **Document the learning intent in References.md.** Future AI agents should not re-litigate the decision. Include:
   - What technology is being learned
   - Why the stack would be WRONG for a product build (reference Convention #0)
   - Why the stack is CORRECT for this learning project
   - Which components are load-driven (needed because of requirements) vs learning-driven (needed because of learning goal)
5. **Budget and timeline expectations.** Learning projects are measured in learning milestones, not feature velocity. User should not expect "weekend project" timelines on enterprise infra.

## Decision Documentation Template

In References.md under "Convention Overrides" or "Build Approach":

```
## Learning Intent (Convention #0 Exception)

This project deliberately uses a stack that would be over-engineered for
its user-facing scope. The stated goal is to learn [TECHNOLOGY].

- Target technology: [Kubernetes / Kafka / etc.]
- User-facing scope: [personal blog / 5 readers / etc.]
- Learning-driven components: [list]
- Load-driven components: [list]
- Cost of learning tier: [approximate range — verify at use]
- Escalation path: [when to move from local to cloud]

Future AI agents: do NOT challenge this stack on scale-mismatch grounds.
Read this file first. The mismatch is intentional.
```

## When NOT to apply the exception

The exception applies to technology-learning. It does NOT apply to:
- "I want to learn to code" (too broad — needs a specific tech target)
- "I want to learn to ship products" (product-build, not tech-learning — follow normal Step 3)
- "I want to learn a framework that a platform covers 80% of" (user should still consider the platform — learning the platform's customization layer is also valid learning)

If the user's learning target is ambiguous, ask: "What's the ONE technology you want to come out of this knowing well?" Their answer determines the exception scope.
