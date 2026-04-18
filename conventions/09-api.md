# Convention #9: API Integration & Data Fetching

**Scope:** this convention covers CLIENT-SIDE API consumption — the project calls external APIs and needs a reusable layer for that. For server-side API design (the project IS the API — REST endpoints, GraphQL schemas, response shapes, pagination, versioning), see `backend/conventions/B2-api-design.md`. For GraphQL server specifically, B2 includes routing to GraphQL patterns (schema design, query-complexity limits, field-level authorization, DataLoader) — research current GraphQL tooling for the chosen language at bootstrap time.

If the project is backend-only (no client), this convention mostly does not apply — mark it as "not needed" in feature-tree.md and focus on B2.

## Principle

All client-side communication with external services goes through one centralized API layer. Features never make direct HTTP calls. The layer handles authentication headers, request and response transformation, caching, deduplication, error normalization, and retry logic. Features declare what data they need, the layer handles everything else.

## Reusable System

Create an API layer that establishes:
- A configured HTTP client with base URL, authentication header injection, and request/response interceptors. Configured once, used everywhere.
- Automatic data transformation at the boundary. If the API uses different naming conventions than the project (snake_case vs camelCase), the transformation happens in the layer, not in features.
- Automatic date parsing at the boundary. Features receive date objects, not strings.
- Integration with the server-state library for caching, deduplication, and revalidation (see convention #5)
- A consistent response format across all endpoints. Every API call returns data in the same structure.
- Retry logic for transient failures built into the layer
- Real-time data handling (websockets, server-sent events) through the same centralized layer if the project needs it

## Rules

- Never make direct HTTP calls in feature code. Always go through the API layer.
- All API functions live in a dedicated API directory or in the feature's API file. Not scattered in components.
- Name API functions by domain action: getUser, createOrder, updateProfile. Not generic names like fetchData or makeRequest.
- Transform data at the boundary. If the API returns snake_case and the project uses camelCase, the API layer converts it. Features never see the raw API format.
- Type every request and response. No untyped API calls.
- Cache strategy is configured once in the layer. Only invalidate cache manually when the user stays on the same page and expects an instant update. If the user navigates after a change, the next page load auto-refetches.

## Violations

- Direct HTTP calls in feature components (fetch or axios called directly)
- Different authentication header logic in different features
- Raw API response format leaking into feature code (features parsing nested API structures)
- Manual cache management (storing API data in local state or global store) instead of using the server-state library
- Untyped API responses
- API functions with generic names that don't describe what they do

## Wrong vs Right

- WRONG: a feature component directly calls the HTTP library with manually constructed headers, manually handles errors, and manually caches the result in component state. Ten features doing this means ten slightly different implementations.
- RIGHT: the API layer is configured once with authentication, error handling, and caching. A feature just declares "I need the users list" and gets back typed data with loading, error, and refresh states handled automatically.
- WRONG: the API returns data in a deeply nested format. Feature components traverse the nesting (response.data.attributes.profile.displayName) throughout their code. The API shape is embedded everywhere.
- RIGHT: the API layer transforms the response into a clean, flat shape at the boundary. Feature components receive simple objects (user.name). If the API format changes, only the transformation layer changes.
- WRONG: after creating a user, the feature manually invalidates the cache, refetches the user list, updates the store, and navigates away. Complex manual orchestration.
- RIGHT: after creating a user, the feature navigates to the user list page. The server-state library automatically refetches fresh data on mount. No manual invalidation needed.

## File Upload & Download

File operations follow the same reusability principle as everything else. One file management service handles all uploads and downloads across the entire project. Features never implement their own file handling.

Create a reusable file management service that:
- Uploads files using presigned URLs or the platform's equivalent. Files go directly from the client to storage, never proxied through the application server.
- Tracks upload progress and displays it in a unified progress indicator (not per-feature custom progress bars).
- Validates files on the client side before uploading (type, size, dimensions). Re-validates on the server side after upload (never trust client-side validation alone).
- Handles uploads in the background. The UI that initiated the upload closes immediately. The user sees upload progress in a global indicator. Upload does not block the user.
- Limits concurrent uploads to prevent overwhelming the server.
- Provides a reusable file viewing component that any feature can use to display files for any entity type.

Rules:
- Never proxy file content through application servers. Use presigned URLs or direct storage upload.
- Never block the UI waiting for an upload to complete. Upload in background, close the form.
- Never create a custom file uploader per feature. Use the shared file management service.
- Validate file type and size on client AND server.

## Research Notes

When bootstrapping this convention:
- Research the framework's recommended HTTP client and how to configure it with interceptors for auth tokens and data transformation
- Research the framework's recommended server-state and data fetching library. Find how it handles caching, deduplication, background refetching, and optimistic updates.
- Research real-time data patterns for the framework if the project needs live updates (websockets, server-sent events, reconnection strategies)
- Research the framework's patterns for data transformation at the API boundary (snake_case to camelCase, date string parsing)
- Research the platform's file upload patterns: presigned URLs, direct storage upload, progress tracking, background upload
- Research the framework's patterns for file viewing and download (previews, galleries, document viewers)
- Document the API layer location, client configuration, data fetching patterns, cache strategy, and file management service in References.md
