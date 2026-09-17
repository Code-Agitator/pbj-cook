# Frontend Full Audit and Repair Design

## Goal

Audit and repair the complete DaCook user interface across H5 and WeChat Mini Program targets. Cover every registered page, its shared components, API interactions, permissions, error states, and navigation flows. Backend changes are allowed only when an API contract or state rule directly causes a frontend defect.

## Scope

The audit covers application bootstrap, setup, login and registration, home, meal list, meal detail, dishes, dish editing, contribution wall, profile, and family administration. It also covers the shared API client, navigation components, PIN input, cards, avatar rendering, and relevant FastAPI endpoints.

The work preserves the current Vue 3, uni-app, and FastAPI architecture and existing visual language. It does not add unrelated features, introduce a new state-management dependency, or broadly redesign the interface.

## Application-Level Behavior

Shared request behavior will provide consistent authentication expiry handling, user-visible failures, and predictable loading cleanup. A 401 response clears the local session and takes the user to login once. Page loaders must catch expected failures and must not leave unhandled rejected promises.

Application bootstrap will wait for server state before selecting setup, login, or an authenticated page. Navigation must not redirect an authenticated user away from the intended route or flash an invalid page. Mutating actions will have an in-flight guard so repeated taps cannot create duplicate meals, orders, reviews, uploads, or settings updates.

## Page Behavior

### Setup and Login

Validate the configured server address, family and member fields, registration availability, join code, and six-digit PIN inputs. Failed PIN attempts reset the editable PIN without losing the selected member or form context. Setup and authentication submissions cannot overlap.

### Home and Meal List

Use local calendar dates consistently rather than UTC-derived dates. Sort meal timestamps numerically and keep active and historical sections deterministic. Validate that meal time and order deadline form a valid chronology. Refresh data when returning from detail or creation flows and show explicit loading, empty, and failure states.

### Meal Detail

Reject missing or invalid route identifiers cleanly. Gate ordering, cook assignment, skipping, status transitions, and reviews by the current meal state and current user's permissions. Prevent stale local selection state after request failures or concurrent taps. Destructive state transitions require confirmation where accidental activation would be costly.

### Dishes and Dish Form

Build action-sheet handlers from explicit action identifiers so permission-dependent menu contents cannot shift indexes. Correct the cuisine picker offset introduced by the synthetic unclassified option. Validate edit permission, required fields, tag normalization, source URL, dynamic ingredient and step limits, and image upload failures. Keep existing image data when editing without choosing a replacement.

### Contribution Wall

Generate heatmap dates using local date arithmetic to avoid timezone shifts. Handle absent or partial contribution data without rendering invalid dates.

### Profile and Family Administration

Refresh the current user and family settings safely on page show. Cancelled profile edits restore saved values. Validate both PIN entries before submission and apply server changes consistently. Server-address changes re-bootstrap the app. Administrative schedule fields obey backend ranges, weekdays cannot be accidentally invalid, failed toggle requests roll back visually, and member removal requires explicit confirmation.

## Backend Contract Repairs

Backend changes are limited to validation, authorization, lifecycle rules, and response data required by the audited frontend flows. Meal actions must reject invalid state transitions. Schedule and dish mutations must report missing resources rather than silently succeeding. Tests will define the accepted transition and permission matrix.

## Error Handling

Pages distinguish initial loading, empty results, recoverable request failure, authorization expiry, and successful content. User-triggered failures produce one actionable message. Background refresh failures retain usable existing data when possible. Loading overlays and disabled controls are always released in `finally` paths.

## Verification

Automated coverage will target pure frontend logic and backend API behavior, especially authentication, permissions, meal state transitions, date handling, form boundaries, and duplicate submission prevention. Production builds must pass for both `build:h5` and `build:mp-weixin`.

The H5 build will be exercised against a local backend through the main flows at desktop and narrow mobile viewports, including normal, empty, failure, and expired-session states. WeChat verification consists of a successful production build and inspection for unsupported browser-only APIs; interactive testing in WeChat Developer Tools remains outside the available automation environment.

## Completion Criteria

All registered pages load without unhandled runtime errors, every user-visible mutation has guarded and recoverable behavior, navigation and authentication are consistent, frontend requests match backend contracts, backend permission and state rules are enforced, automated tests pass, and both target builds succeed.
