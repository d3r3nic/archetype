# Bootstrap: example conversations

Illustrations of the discovery posture. They do not replace the stepped questions or Step 3 research.

## Owner with a broad idea

Owner: "I want to build something for my restaurant."

AI: "I will first understand what it needs to accomplish. What should customers be able to do, who updates the information, and where will each person use it?"

Owner: "Customers should see our menu and book a table online. My manager updates the menu."

AI: "The primary outcomes are a menu customers can read and a booking flow, with a separate update path for the manager. I still need the booking rules, access needs, data involved, expected usage and budget. Then I will research current hosted, hybrid and custom approaches and recommend the one whose tradeoffs fit those priorities."

The AI records requirements before naming an implementation. A current booking service may be the best answer, or ownership, integration and workflow needs may justify custom work. Discovery does not decide that in advance.

## Owner with a preferred stack

Owner: "I am building healthcare software with a component-based frontend, a cloud backend, a managed relational database and managed identity. I know the stack."

AI: "I will preserve those preferences and their reasons. Before committing, I need the product's central workflow, the applicable data regime, required integrations, vendor agreements, operating constraints and which parts of this stack are already settled commitments. Step 3 will verify the current capabilities, terms and costs of the preferred path and compare credible alternatives where they could materially change the outcome."

Owner: "The central workflow is our proprietary analysis pipeline. We must integrate with two existing systems, and the named cloud is already an organizational commitment."

AI: "Those facts make the pipeline, integrations and cloud commitment decisive inputs. I will research the remaining choices within that boundary, verify the required agreements and controls for the actual regime, and record why the resulting approach serves the product."

The AI neither discards a knowledgeable owner's commitments nor treats technical vocabulary as proof that every choice is correct. Research tests the unsettled parts against the goal.

## Owner whose purpose is learning

Owner: "This is a small personal application, but I am building it to learn container orchestration."

AI: "Learning container orchestration is part of the product purpose, so I will evaluate approaches by what they teach as well as what the application needs. I will research current local and hosted learning paths, their costs and the operational topics each exposes. We will choose the path that teaches the named subject without adding unrelated burden, while keeping the normal safety and spending gates."

The audience size does not erase the learning goal, and the infrastructure choice is not inferred from audience size alone.
