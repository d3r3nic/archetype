# Convention #21: Routing & Navigation

## Applies when

The product has places people navigate between: pages, screens, deep links, tabs. What varies: the platform's navigation model (addresses in a browser, a stack of screens on a device, views in a desktop tool) and whether places can be shared or opened from outside. A product with a single view skips this convention.

## Principle

Every place in the product is defined once and reached through that definition. Access to protected places is decided in one guard, not by each place, and the server checks every request regardless, because a guard in the interface is a convenience, not security. People always see where they are, what is loading, and what failed.

## Reusable System

The navigation system: the one set of route or screen definitions, the guard that decides access to protected places, the layouts that stay in place while their content changes, and the rule for which view state survives a refresh, a back step or a shared link. References.md records where each lives.

## Rules

- Define each route or screen once, and build every link and navigation from that definition. Never scatter path strings through the code.
- Decide access to protected places in the one guard. Never repeat the check in each page or screen.
- Treat interface guards as help for people. The server verifies authorization on every request (#11, #24).
- Keep shared frames (navigation, sidebars, headers) in place while only the content changes, where the platform supports it.
- Every place shows its waiting and error states (#8); nobody navigates into nothing.
- Decide per view which state survives a refresh, a back step or a shared link (#5). Where a web view's filters or position should be shareable, the address carries them; sensitive values never do.

## Violations

- The same access check copied into many pages or screens.
- Path strings written by hand across the code.
- A protected place relying only on an interface guard.
- A place that shows nothing while it loads.
- View state that people expect to keep lost on refresh or back, or sensitive values placed in an address.

## Wrong vs Right

- WRONG: twenty pages each begin with "if not signed in, redirect". RIGHT: one guard protects them; changing the rule changes one place.
- WRONG: a link to an edit page is written as a literal path in eight places. RIGHT: one definition builds every link to it.
- WRONG: every filter is moved into the address because a general rule said so. RIGHT: the filters people share or return to live in the address; private or momentary ones do not.

## Research Notes

Research the chosen platform's navigation model, how its router defines places and guards access, how it keeps layouts in place, and how it restores and shares view state. Record the route definitions, the guard and the view-state rule in References.md.
