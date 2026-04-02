# Convention #8: Error Handling, Recovery & Async

## Principle

All errors flow through one centralized system. Features never catch, display, or recover from errors on their own. The system classifies errors, logs them, reports them, shows user-friendly messages, and provides retry capability. Async operations always have explicit loading, error, and success states.

## Reusable System

Create a reusable error service that:
- Catches all errors from any source (API calls, runtime exceptions, user input validation)
- Classifies errors by type: network errors, validation errors, authentication errors, not-found errors, server errors
- Logs errors with context: what operation was happening, what data was involved, who was affected
- Reports errors to a monitoring service for tracking and alerting
- Displays user-friendly messages to the user. Never show stack traces or technical details in the UI. Technical details go to logs only.
- Provides automatic retry with exponential backoff for transient failures (network errors, server errors). Never retries client errors except rate limiting.
- Cancels pending operations when the user navigates away or the component unmounts

Create unified state components that all features share:
- A loading component for full-screen loading (app initialization, page loads)
- A loading component for inline loading (data fetching within a page, form submissions)
- A skeleton component for content-shaped placeholders while data loads
- An error state component that shows a friendly message and a retry button
- An empty state component that shows when data loads successfully but there are no results
- An offline state component for when the network is unavailable

Features declare what data they need. The data layer and error system handle everything else.

## Rules

- Create one error service. Always use it. Never handle errors per feature.
- Create unified loading, error, empty, and offline components. Reuse them everywhere. Never build a custom spinner or error message for a single feature.
- User-facing error messages must be friendly and actionable. Tell the user what happened and what they can do. "We couldn't load your data. Please try again." not "Error: ECONNREFUSED."
- Every async operation must handle three states: loading, error, and success. No operation should leave the user staring at a blank screen.
- Empty state is different from error state. "No results found" is not an error.
- Retry transient errors automatically with exponential backoff. Stop after a reasonable limit and show the error state with a manual retry option.
- Never swallow errors. Every error must be logged, reported, or handled meaningfully. A catch block with only a console.log is a violation.
- Cancel pending operations when the user navigates away. Stale responses arriving after navigation cause bugs.

## Violations

- try/catch scattered across features with different error handling in each
- A feature with its own custom loading spinner instead of the shared one
- catch blocks that only contain console.log (silently swallowed errors)
- Technical error messages shown to users (stack traces, error codes, connection strings)
- Async operations with no loading state (blank screen while fetching)
- No distinction between empty state and error state
- Missing retry capability on transient failures
- Pending operations not cancelled on navigation (stale data arriving late)

## Wrong vs Right

- WRONG: Feature A catches errors with an alert, Feature B logs to console, Feature C sets a boolean. Three features, three different approaches.
- RIGHT: All features use the same error system. The system decides how to classify, log, display, and retry. Features don't think about errors at all.
- WRONG: a generic spinner for every loading state across the app, or worse, each feature builds its own spinner.
- RIGHT: content-shaped skeleton placeholders that match the layout of the data being loaded. One set of unified loading components, configured per context.
- WRONG: server returns a validation error, feature shows a generic "Something went wrong" toast.
- RIGHT: server returns field-specific validation errors, the error system maps them back to the specific form fields that caused them.

## Research Notes

When bootstrapping this convention:
- Research the framework's latest error handling patterns and error boundary equivalents. Understand how the framework recommends catching errors at different levels (app-wide, per-route, per-feature).
- Research the framework's async state management. Find how the framework handles loading, error, and success states for data fetching operations. Look for patterns where the framework manages these states automatically rather than manually.
- Research cancellation patterns for the framework. How do you cancel pending operations when a user navigates away?
- Research error reporting and monitoring services that integrate well with the framework. Find the recommended way to capture errors with context and send them to a monitoring dashboard.
- Research retry patterns. Find the framework's recommended approach for automatic retry with exponential backoff on transient failures.
- Document the error service, error types, unified components, and usage pattern in References.md.
