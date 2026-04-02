# Convention #21: Routing & Navigation

## Principle

Routes define the application's URL structure and map to pages. Layouts persist across child routes. Route guards protect authenticated content. URL parameters encode state that should survive refresh and sharing. Loading and error states are defined per route segment.

## Reusable System

- Route guard component: auth check that redirects unauthenticated users
- Layout components: persistent shells (sidebar, header) across child routes
- URL state utilities: helpers for reading/writing filters and pagination to URL params

## Rules

- Nested layouts for persistent UI across child routes.
- Route guards protect authenticated routes at the routing level.
- Every route has its own loading and error state.
- Filters, pagination, and view state live in URL search params.
- Typed routes prevent broken links at compile time when possible.
- Prefetch route data on link hover for perceived instant navigation.

## Violations

- Auth check in every page component instead of route guard
- Filters stored in component state instead of URL (lost on refresh)
- Route without loading state (blank screen during data fetch)
- Hardcoded route paths as strings scattered across the codebase
- Client-side route guards as sole protection (no server-side authorization)

## Right vs Wrong

Examples are illustrative.

```
WRONG (auth check duplicated in every page):
function SettingsPage() {
  const { user } = useAuth();
  if (!user) return <Navigate to="/login" />;  // duplicated everywhere
  return <Settings />;
}
function ProfilePage() {
  const { user } = useAuth();
  if (!user) return <Navigate to="/login" />;  // again
  return <Profile />;
}

RIGHT (route guard at routing level):
<Route element={<RequireAuth />}>
  <Route path="settings" element={<Settings />} />
  <Route path="profile" element={<Profile />} />
</Route>
```

```
WRONG (hardcoded route strings):
navigate('/dashboard/users/123/edit');
<Link to="/dashboard/users">Users</Link>

RIGHT (typed route constants):
const routes = {
  users: '/dashboard/users',
  userEdit: (id: string) => `/dashboard/users/${id}/edit`,
};
navigate(routes.userEdit(user.id));
<Link to={routes.users}>Users</Link>
```

## References.md Section

- Router: which one (React Router, TanStack Router, Next.js, etc.)
- Route guard: path to auth route wrapper
- Layout: where layout components live
- Route definitions: where routes are defined
