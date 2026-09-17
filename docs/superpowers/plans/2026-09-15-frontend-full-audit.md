# Frontend Full Audit and Repair Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Repair all registered DaCook pages and their directly related API contracts for reliable H5 and WeChat Mini Program behavior.

**Architecture:** Keep the existing Vue 3 and uni-app page structure. Extract only deterministic date, validation, and action-menu logic into a small utility module; centralize session expiry in the API client; enforce authoritative permission and lifecycle rules in FastAPI.

**Tech Stack:** Vue 3.5, uni-app 3, Vite 5, Vitest, FastAPI, SQLite, pytest, FastAPI TestClient

**Spec:** `docs/superpowers/specs/2026-09-15-frontend-full-audit-design.md`

## Global Constraints

- Support both H5 and WeChat Mini Program production builds.
- Preserve the existing visual language and page directory structure.
- Do not add a global state-management dependency.
- Backend changes must directly repair a frontend contract, permission, validation, or lifecycle defect.
- This workspace has no `.git` directory, so task checkpoints use test results and a changed-file inventory instead of commits.

## File Structure

- Create `frontend/src/utils/app.js`: deterministic local-date, form validation, picker mapping, and action-menu helpers.
- Create `frontend/src/utils/app.test.js`: unit coverage for those pure helpers.
- Modify `frontend/src/api/client.js`: normalize base URLs, redirect once on expired sessions, harden upload parsing, and support request options.
- Modify `frontend/src/App.vue`: deterministic bootstrap routing.
- Modify all files below `frontend/src/pages/`: page-specific loading, error, permission, validation, and duplicate-action behavior.
- Modify `frontend/src/components/PinPad.vue`: disabled state and input reset behavior.
- Modify `frontend/package.json` and `frontend/package-lock.json`: add the frontend test command and Vitest development dependency.
- Create `backend/tests/conftest.py`: isolated SQLite API fixture.
- Create `backend/tests/test_contracts.py`: authorization, state transition, and missing-resource contract tests.
- Modify `backend/app/main.py`: enforce the contracts required by the page flows.

---

### Task 1: Deterministic Frontend Logic

**Files:**
- Create: `frontend/src/utils/app.js`
- Create: `frontend/src/utils/app.test.js`
- Modify: `frontend/package.json`
- Modify: `frontend/package-lock.json`

**Interfaces:**
- Produces: `localDateKey(value?: Date): string`
- Produces: `validateMealDraft(draft): string`
- Produces: `cuisineIdFromPicker(cuisines, pickerIndex): string | null`
- Produces: `dishActions(dish, user): Array<{ key: string, label: string }>`
- Produces: `heatmapDateKey(start: string, offset: number): string`

- [ ] **Step 1: Add the frontend test runner**

Run `npm install --save-dev vitest@^2.1.9` in `frontend`, then add this script:

```json
"test": "vitest run"
```

- [ ] **Step 2: Write failing helper tests**

```js
import { describe, expect, it } from 'vitest'
import { cuisineIdFromPicker, dishActions, heatmapDateKey, localDateKey, validateMealDraft } from './app'

describe('frontend application helpers', () => {
  it('formats a local calendar date without UTC conversion', () => {
    expect(localDateKey(new Date(2026, 8, 15, 23, 30))).toBe('2026-09-15')
  })

  it('maps the synthetic unclassified picker item', () => {
    const cuisines = [{ id: 'home' }, { id: 'sichuan' }]
    expect(cuisineIdFromPicker(cuisines, 0)).toBeNull()
    expect(cuisineIdFromPicker(cuisines, 2)).toBe('sichuan')
  })

  it('does not expose edit actions to another member', () => {
    expect(dishActions({ created_by: 'u1' }, { id: 'u2', is_admin: false }))
      .toEqual([{ key: 'view', label: '查看详情' }])
  })

  it('rejects a deadline at or after dining time', () => {
    expect(validateMealDraft({ date: '2026-09-15', dining_time: '18:30', deadline: '18:30' }))
      .toBe('点菜截止时间必须早于用餐时间')
  })

  it('advances heatmap dates in local calendar space', () => {
    expect(heatmapDateKey('2026-09-15', 1)).toBe('2026-09-16')
  })
})
```

- [ ] **Step 3: Run tests and verify the missing module failure**

Run: `npm test -- --run frontend/src/utils/app.test.js`

Expected: FAIL because `frontend/src/utils/app.js` does not exist.

- [ ] **Step 4: Implement the pure helpers**

```js
const pad2 = value => String(value).padStart(2, '0')

export function localDateKey(value = new Date()) {
  return `${value.getFullYear()}-${pad2(value.getMonth() + 1)}-${pad2(value.getDate())}`
}

export function validateMealDraft({ date, dining_time, deadline }) {
  if (!date || !/^\d{2}:\d{2}$/.test(dining_time) || !/^\d{2}:\d{2}$/.test(deadline)) return '请填写完整的日期和时间'
  if (deadline >= dining_time) return '点菜截止时间必须早于用餐时间'
  return ''
}

export function cuisineIdFromPicker(cuisines, pickerIndex) {
  const index = Number(pickerIndex)
  return index === 0 ? null : cuisines[index - 1]?.id || null
}

export function dishActions(dish, user) {
  const actions = [{ key: 'view', label: '查看详情' }]
  if (user?.is_admin || dish.created_by === user?.id) {
    actions.push({ key: 'edit', label: '编辑菜品' }, { key: 'archive', label: '归档菜品' })
  }
  return actions
}

export function heatmapDateKey(start, offset) {
  const [year, month, day] = start.split('-').map(Number)
  const value = new Date(year, month - 1, day)
  value.setDate(value.getDate() + offset)
  return localDateKey(value)
}
```

- [ ] **Step 5: Run helper tests**

Run: `npm test`

Expected: all helper tests PASS.

### Task 2: API Client and Authentication Lifecycle

**Files:**
- Modify: `frontend/src/api/client.js`
- Modify: `frontend/src/App.vue`
- Modify: `frontend/src/components/PinPad.vue`
- Modify: `frontend/src/pages/setup/index.vue`
- Modify: `frontend/src/pages/login/index.vue`

**Interfaces:**
- Consumes: `localDateKey` only indirectly through later pages.
- Produces: `normalizeApiBase(value: string): string`
- Produces: `request(path, options)` with `redirectOnUnauthorized?: boolean`
- Produces: `run(action, success)` with unchanged resolved and rejected semantics.

- [ ] **Step 1: Extend helper tests for server URL normalization**

```js
expect(normalizeApiBase('  http://192.168.1.8:8000/ ')).toBe('http://192.168.1.8:8000')
expect(normalizeApiBase('ftp://bad')).toBe('')
```

- [ ] **Step 2: Implement URL normalization and single 401 redirect**

Add `normalizeApiBase` to `utils/app.js`. In `api/client.js`, use a module-level `redirectingToLogin` flag. On a 401, clear the session and call `uni.reLaunch({ url: '/pages/login/index' })` once unless `options.redirectOnUnauthorized === false`. Reset the flag when `setSession` succeeds.

```js
if (res.statusCode === 401) {
  clearSession()
  if (options.redirectOnUnauthorized !== false && !redirectingToLogin) {
    redirectingToLogin = true
    uni.reLaunch({ url: '/pages/login/index' })
  }
}
```

- [ ] **Step 3: Harden upload responses**

Parse `uni.uploadFile` response JSON inside `try/catch`, handle 401 through the same session-expiry path, and reject with `Error('上传响应格式不正确')` when the body is invalid.

- [ ] **Step 4: Make bootstrap routing deterministic**

In `App.vue`, treat bootstrap as public, preserve setup and login routes, and only route authenticated users away when required. On bootstrap failure, retain the current page and display a connection message instead of logging silently.

- [ ] **Step 5: Guard setup and login submissions**

Add `submitting` refs, bind `:disabled="submitting"` to PIN input and relevant buttons, trim names and family names, validate normalized API base values, and restore `submitting` in `finally`. `PinPad` ignores press and erase events while disabled.

- [ ] **Step 6: Run focused and production checks**

Run: `npm test && npm run build:h5 && npm run build:mp-weixin`

Expected: tests pass and both builds exit 0.

### Task 3: Home and Meal Flows

**Files:**
- Modify: `frontend/src/pages/home/index.vue`
- Modify: `frontend/src/pages/meals/index.vue`
- Modify: `frontend/src/pages/meal-detail/index.vue`
- Modify: `frontend/src/components/MealCard.vue`

**Interfaces:**
- Consumes: `localDateKey`, `validateMealDraft`, `request`, and `run`.
- Produces: guarded meal creation, ordering, cook assignment, status changes, skipping, and review behavior.

- [ ] **Step 1: Replace UTC date comparisons and validate meal creation**

Use `localDateKey()` for defaults and labels. Before POST, call `validateMealDraft(form)` and show its returned message. Guard creation with `creating`; on failure retain the sheet and entered values.

- [ ] **Step 2: Add safe loaders to both meal lists**

Each `onShow` loader uses `loading`, `loadError`, and `try/catch/finally`. Sort on copied arrays with `Number(a.dining_time) - Number(b.dining_time)` so computed properties do not mutate source state.

- [ ] **Step 3: Harden detail loading and route validation**

If `o.id` is absent, show `饭局参数无效` and navigate back. Wrap the parallel requests in `try/catch/finally`, show a retry state, and avoid reading `meal` fields until data exists.

- [ ] **Step 4: Enforce client-side state gates and in-flight keys**

Derive `canClaimCook`, `orderingOpen`, `canManage`, and `canReview`. Track mutation keys in `Set<string>` and ignore duplicate taps. Wrap each action in `try/finally`, reloading authoritative meal data after a successful change.

```js
async function mutate(key, action) {
  if (pending.value.has(key)) return
  pending.value = new Set(pending.value).add(key)
  try { await action() }
  finally {
    const next = new Set(pending.value)
    next.delete(key)
    pending.value = next
  }
}
```

- [ ] **Step 5: Confirm destructive transitions**

Require confirmation before cancelling a meal. Hide cook assignment after `done` or `cancelled`, hide skip actions outside cooking-relevant states, and disable review submission while pending.

- [ ] **Step 6: Run frontend checks**

Run: `npm test && npm run build:h5 && npm run build:mp-weixin`

Expected: all commands exit 0.

### Task 4: Dish Library and Editor

**Files:**
- Modify: `frontend/src/pages/dishes/index.vue`
- Modify: `frontend/src/pages/dish-form/index.vue`

**Interfaces:**
- Consumes: `dishActions`, `cuisineIdFromPicker`, `request`, `run`, and `uploadImage`.
- Produces: permission-correct action dispatch and index-correct cuisine editing.

- [ ] **Step 1: Replace action-sheet index assumptions**

Create an action array with `dishActions(d, me)`, render its labels, and dispatch using `actions[r.tapIndex]?.key`. Await each selected action and report request errors through `run`.

- [ ] **Step 2: Correct cuisine picker mapping**

Pass `$event.detail.value` to `cuisineIdFromPicker(cuisines, value)`. Provide a picker `:value` computed from the current `cuisine_id`, including zero for unclassified.

- [ ] **Step 3: Harden editor initialization and saving**

Use `loading`, `loadError`, and `saving`. Normalize tags, drop empty ingredient and step rows, cap them at backend limits, and keep existing `image_path` unless a new upload succeeds. Reject inaccessible edit IDs with a visible error and safe back action.

- [ ] **Step 4: Guard list loading and archive confirmation**

Keep existing list data on refresh failure. Confirm archive, block a repeated archive tap, and remove the item only after the API succeeds.

- [ ] **Step 5: Run frontend checks**

Run: `npm test && npm run build:h5 && npm run build:mp-weixin`

Expected: all commands exit 0.

### Task 5: Contribution, Profile, and Administration

**Files:**
- Modify: `frontend/src/pages/wall/index.vue`
- Modify: `frontend/src/pages/me/index.vue`
- Modify: `frontend/src/pages/admin/index.vue`

**Interfaces:**
- Consumes: `heatmapDateKey`, `normalizeApiBase`, `request`, `run`, and `uploadImage`.
- Produces: timezone-stable heatmaps, cancellable profile drafts, validated admin operations.

- [ ] **Step 1: Use local heatmap date arithmetic**

Replace `new Date(start + 'T00:00:00').toISOString()` with `heatmapDateKey(start, i)`. Show loading, retry, empty, and partial-data states without constructing an invalid date.

- [ ] **Step 2: Reset profile drafts on every modal open**

Replace direct `showProfile = true` with `openProfile()`, which copies saved `me` fields into the draft and clears `localAvatar`. Validate non-empty trimmed names and preserve the modal after failed saves.

- [ ] **Step 3: Validate PIN and server changes**

Require both PINs to match `/^\d{6}$/` before calling the API. Normalize the server address and relaunch to login after saving so bootstrap and cached authentication cannot continue against different servers.

- [ ] **Step 4: Validate schedule drafts**

Require name, at least one weekday, `create_lead_hours` from 0 through 72, and `deadline_lead_minutes` from 0 through 1440. Convert numeric input values before the request and guard save/tick/delete operations.

- [ ] **Step 5: Roll back toggles and confirm member removal**

Only update `s.enabled` after a successful PUT. For member management, use separate explicit actions; require a second modal confirmation before DELETE and reload members only after successful mutations.

- [ ] **Step 6: Run frontend checks**

Run: `npm test && npm run build:h5 && npm run build:mp-weixin`

Expected: all commands exit 0.

### Task 6: Backend Contract Enforcement

**Files:**
- Create: `backend/tests/conftest.py`
- Create: `backend/tests/test_contracts.py`
- Modify: `backend/app/main.py`
- Modify: `backend/requirements.txt`

**Interfaces:**
- Produces: API errors with status 404 for absent resources, 403 for insufficient permission, 409 for lifecycle conflicts, and 422 for invalid values.

- [ ] **Step 1: Add isolated API test dependencies and fixture**

Add `pytest` and `httpx` to `backend/requirements.txt`. In `conftest.py`, monkeypatch `app.database.DB_PATH` to a temporary SQLite file, call `init_db()`, and yield `TestClient(app)`.

- [ ] **Step 2: Write failing lifecycle and resource tests**

```python
def test_cannot_claim_cook_after_meal_is_done(client, auth_headers, done_meal):
    response = client.post(f"/api/meals/{done_meal}/cook", headers=auth_headers)
    assert response.status_code == 409

def test_update_missing_schedule_returns_404(client, admin_headers):
    response = client.put("/api/admin/schedules/missing", headers=admin_headers, json=valid_schedule())
    assert response.status_code == 404

def test_delete_missing_dish_returns_404(client, auth_headers):
    response = client.delete("/api/dishes/missing", headers=auth_headers)
    assert response.status_code == 404
```

- [ ] **Step 3: Write the transition matrix tests**

Verify `ordering -> cooking -> done`, allow `ordering|cooking -> cancelled`, and reject transitions out of `done` or `cancelled`. Verify only creator, current cook, or admin can perform an allowed status transition.

- [ ] **Step 4: Implement minimal contract checks**

Add explicit existence checks before update/delete. Reject cook toggles unless status is `ordering` or `cooking`. Use an allowed-transition map in `update_meal_status`:

```python
allowed = {
    "ordering": {"cooking", "cancelled"},
    "cooking": {"done", "cancelled"},
    "done": set(),
    "cancelled": set(),
}
if status not in allowed[meal["status"]]:
    raise HTTPException(409, "当前状态不能执行该操作")
```

- [ ] **Step 5: Run backend tests**

Run: `.venv\Scripts\python -m pytest -q`

Expected: all contract tests PASS.

### Task 7: End-to-End Build and Browser Regression

**Files:**
- Modify only files implicated by a reproduced regression.

**Interfaces:**
- Consumes: completed frontend and backend behavior from Tasks 1 through 6.
- Produces: verified H5 and WeChat build artifacts and a final issue inventory.

- [ ] **Step 1: Run all automated checks**

Run in `backend`: `.venv\Scripts\python -m pytest -q`

Run in `frontend`: `npm test`, `npm run build:h5`, and `npm run build:mp-weixin`

Expected: every command exits 0 without unhandled rejection or compiler warnings caused by application code.

- [ ] **Step 2: Start isolated local services**

Start FastAPI with a temporary acceptance database on port 8000 and H5 on the first available port at or above 5173. Record both process IDs for clean shutdown.

- [ ] **Step 3: Exercise every page in a desktop browser**

Complete setup, logout/login, registration, meal creation, meal ordering, cook assignment, state completion, review, dish creation/edit/archive, profile edit, contribution wall, and admin schedule/member flows. Inspect browser console and failed network requests after each flow.

- [ ] **Step 4: Repeat responsive checks at a narrow viewport**

Verify 375 by 812 and 320 by 568 viewports. Check fixed tab bar clearance, modal scrolling, PIN controls, two-column dish grids, ingredient rows, and long family/member/dish text for overlap.

- [ ] **Step 5: Verify failure states**

Exercise an invalid server URL, expired token, missing route ID, rejected permission, failed upload, empty lists, and repeated taps. Confirm one actionable error, released loading state, and no duplicate records.

- [ ] **Step 6: Inspect WeChat compatibility**

Search application code for browser-only globals and unsupported APIs. Confirm `dist/build/mp-weixin` contains all ten registered pages and no compilation errors.

- [ ] **Step 7: Record the final checkpoint**

List every changed file, test command and result, browser scenario result, remaining environment limitation, and any defect intentionally left unresolved with its reason.
