# Convention #24: Authorization

Authentication (#11) answers "who is this?". Authorization, this convention, answers "may they do this, to this?".

## Applies when

Any access is restricted: some people may see or change what others may not. What varies: the permission model the domain needs (roles, ownership, organizations, attributes of the record), and whether one deployment serves several customers. A product whose every user may do everything skips this convention, and records that.

## Principle

Every access to a restricted action or record is checked where the action happens, on the server or the owning service, against that specific record, not only its kind. Hiding a button is not security. Permissions are defined in one place and checked through one owner; they are never scattered across handlers.

## Reusable System

The authorization owner: the permission model, defined once, and the service that every handler and service calls to check it, including the object-level check that the caller may act on this particular record. References.md records the model, the owner's location, and how a handler asks it.

## Rules

- Check permission where the action runs, before it runs. An interface that hides an option does not stop a direct call.
- Check the specific record. A caller must not reach someone else's data by changing an identifier.
- Define roles and permissions once. Never write permission checks inline in many handlers.
- Grant the least privilege a role needs. A new role starts with nothing and gains only what it must.
- Identify first, then authorize: authentication runs before the handler; authorization runs in the service or domain layer, where the record and its context are known.
- Deny recognizably, never with an empty success, and log each denial: who, what, which record, when and why.

## Violations

- A permission enforced only in the interface.
- A handler that returns any record whose identifier it is given.
- Permission checks written differently in different handlers.
- A denial returned as an empty success, with nothing logged.

## Wrong vs Right

- WRONG: the interface hides "Delete user" from non-administrators, but the delete call has no check, and anyone who finds it can use it. RIGHT: the interface hides it, and the service asks the authorization owner whether this caller may delete this user before acting.
- WRONG: any signed-in person can read any patient's record by changing the number in the request. RIGHT: the service checks that this caller treats this patient, or holds a role that grants access, and denies otherwise.
- WRONG: one handler checks a role name, another a permission list, another a user type. RIGHT: one permission model, checked the same way everywhere through one owner.

## Research Notes

Research the permission models that fit the domain, the chosen stack's options for checking permissions in one place, how its data access can scope queries to what a caller may see, and whether the storage offers row-level protection worth using. Record the model, the owner and the check pattern in References.md.
