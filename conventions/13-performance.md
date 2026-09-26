# Convention #13: Performance & Optimization

## Applies when

Every project. What varies is the workload that matters: how fast a screen answers, how many requests a service carries, how smoothly a simulation runs, how much a job costs to run, how much battery an app uses. The facts gathered at setup (who uses it, how many, how often) size it.

## Principle

Speed, capacity and cost are sized to the real workload: measured, budgeted where a regression would matter, and never built far beyond need or left to grow unchecked. Identify what must stay responsive, timely or economical in the product's actual contexts, then measure it. Select budgets and techniques from those needs, not from a generic page or application template.

## Reusable System

Define representative workloads, environments, measurements and acceptable limits with their reasons in References.md. Use repeatable checks for the dimensions whose regression would matter. A small experiment may need a focused measurement; a continuously used service may need ongoing observation.

## Rules

- Identify relevant dimensions: startup, response time, frame pacing, throughput, memory, storage, network, energy or operating cost. Investigate the ones the product's behavior and constraints make material.
- Measure before choosing an optimization. Compare expected benefit, complexity and correctness risks; retain a simpler implementation when it meets the need.
- Choose loading, caching, batching and resource-lifetime strategies appropriate to the runtime. Consider consistency, latency and failure behavior as well as average speed.
- For page-based interfaces, evaluate route loading, assets, visual stability and interaction responsiveness. For continuous simulations or other workloads, use their own representative operations and timing constraints.
- Set justified budgets with a repeatable measurement method. Enforce accepted budgets where reliable checks exist; interpret noisy results rather than silently loosening thresholds.
- Recheck the user-visible behavior after optimization. A faster result that changes the promised semantics is not a performance improvement.

## Violations

- Applying page bundle advice to a workload without page bundles
- Optimizing remembered bottlenecks without inspecting the actual workload
- Measuring only an empty or unrealistically small case
- Caching away required freshness or correctness
- Quoting a performance improvement without comparable measurements

## Wrong vs Right

- WRONG: lazy-load every resource because an app template recommends it. RIGHT: measure startup and later interaction costs, then choose a loading strategy that fits the experience.
- WRONG: issue a repeated remote query per item without measuring growing input sizes. RIGHT: inspect the access pattern and evaluate batching or a changed query where the measurements justify it.
- WRONG: use a web page score to approve a continuously animated simulation. RIGHT: measure the intended interaction and workload on the committed contexts.

## Research Notes

Research current measurement tools and runtime behavior for the selected workload. Read primary documentation for proposed optimizations and reproduce material claims in a representative experiment. Record the method, environment and limits alongside results (#18).
