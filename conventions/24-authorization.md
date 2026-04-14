# Convention #24: Authorization

Authentication (#11) answers: who is this user?
Authorization (this convention) answers: can this user do this action on this resource?

## Principle

Authorization is enforced at the service layer, not the UI layer. A hidden button is not security — the service must verify permission before executing. Every resource access checks that the requesting user owns or has permission to access that specific resource. Authorization logic is centralized in a permission system, not scattered across handlers.

## Reusable System

Create an authorization foundation that establishes:
- A permission model (RBAC, ABAC, or hybrid) with roles and permissions defined centrally
- An authorization service that handlers and services call to check permissions
- Object-level access checks: verify the user owns or has access to the specific resource being requested (not just the resource TYPE but the specific INSTANCE)
- Middleware or decorators that enforce role requirements on routes/endpoints

## Rules

- Authorization checks happen at the service layer, not just the UI. A hidden button does not prevent a direct API call. The service must independently verify that the requesting user has permission for the specific action on the specific resource.
- Every resource access includes an object-level access check. A user should not be able to access another user's data by guessing an ID in the URL. The service verifies ownership or explicit permission grant.
- Define roles and permissions centrally in one place. Not scattered across 50 handlers with inline permission strings.
- Use the least privilege principle. Users get the minimum permissions needed for their role. New roles start with zero permissions and add only what's needed.
- Separate authentication from authorization. Authentication (who are you?) runs first in the middleware pipeline. Authorization (can you do this?) runs in the service layer where the business logic and resource context are available.
- Log authorization denials. Every time a user is denied access, log: who, what resource, what action, when, and the denial reason. This is critical for security auditing and detecting unauthorized access attempts.

## Violations

- Authorization check only in the UI: admin button hidden with CSS, but the API endpoint has no permission check. Any user who finds the endpoint can call it.
- User A accesses /api/users/456/profile and gets User B's profile because the handler returns the requested user without checking if User A has permission to view User B's data.
- Permission strings hardcoded across 30 different handlers: handler A checks role === 'admin', handler B checks role !== 'viewer', handler C checks isAdmin. No central permission model.
- Authorization denial returns 200 with empty data instead of 403. The user doesn't know they're denied, and the audit log has no denial record.

## Wrong vs Right

- WRONG: UI hides the "Delete User" button for non-admins. A non-admin opens browser dev tools, finds the API endpoint, calls DELETE /api/users/123, and the user is deleted because the handler has no permission check.
- RIGHT: UI hides the button AND the handler calls authorizationService.canDelete(requestingUser, 'users', userId). If the user doesn't have delete permission on users, the service throws a ForbiddenError. Both layers enforce.
- WRONG: GET /api/patients/456 returns patient 456's data to any authenticated user. User A (who should only see their own patients) can view any patient by changing the ID.
- RIGHT: GET /api/patients/456 calls authorizationService.canAccess(requestingUser, 'patient', 456). The service checks: does this user own this patient, or do they have a facility-level role that grants access? If not, 403.
- WRONG: permissions scattered: handler checks `if (user.role === 'admin')`, another checks `if (user.permissions.includes('manage_users'))`, another checks `if (user.type !== 'viewer')`. Three different approaches, inconsistent enforcement.
- RIGHT: one permission model: roles have permissions, permissions are checked through one service. authorizationService.hasPermission(user, 'users.delete') works the same everywhere.

## Research Notes

When bootstrapping this convention:
- Research authorization models suitable for the project (RBAC for most apps, ABAC for complex multi-tenant). Research the framework's recommended authorization libraries.
- Research the framework's patterns for middleware/decorator-based route protection (role requirements on endpoints).
- Research object-level access check patterns for the ORM (scoped queries, policy-based access).
- Research row-level security features in the database if applicable (PostgreSQL RLS, SQL Server row security).
- Document the permission model, authorization service location, role definitions, and access check patterns in References.md.
