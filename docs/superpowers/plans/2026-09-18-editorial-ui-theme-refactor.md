# DaCook Editorial UI Theme Refactor Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Recompose DaCook around the approved editorial private-dining layout while retaining its current palette and placing all component colors behind a maintainable semantic theme layer.

**Architecture:** `frontend/src/styles.css` will own primitive palette values, semantic roles, layout scales, and shared control primitives. Shared Vue components consume only semantic roles, while page styles define composition without raw colors; pure Vitest checks enforce the theme boundary and Vue 3 component convention. Existing routes, API calls, permissions, and page state remain untouched.

**Tech Stack:** Vue 3 Composition API, uni-app, CSS custom properties, Vitest, Vite H5 build, existing in-app browser at `http://localhost:5173`.

**Spec:** `docs/superpowers/specs/2026-09-18-editorial-ui-theme-design.md`

## Global Constraints

- Preserve exactly four bottom destinations: `首页 / 饭局 / 贡献 / 我的`.
- Preserve the meal-first model and keep cook claiming independent from ordering.
- Keep dish management under the administrator section of `我的`.
- Keep dish images with a bottom black gradient and overlaid text.
- Do not add prices, cart, checkout, payment, or transaction language.
- Use `<script setup lang="js">` in every Vue component; do not introduce `export default`.
- Do not change backend code, endpoints, schemas, route definitions, dependencies, or lockfiles.
- Preserve H5 and WeChat Mini Program-compatible CSS and uni-app primitives.
- Use the existing development server at `http://localhost:5173`; do not start another server.
- Preserve unrelated working-tree changes and stage only files belonging to the current task.

---

### Task 1: Establish Theme Layers and Automated Architecture Guards

**Files:**
- Modify: `frontend/src/styles.css`
- Modify: `frontend/src/App.vue`
- Create: `frontend/src/styles.test.js`

**Interfaces:**
- Produces: primitive tokens named `--palette-*`, semantic tokens named `--theme-*`, and layout tokens named `--space-*`, `--radius-*`, and `--shadow-*`.
- Produces: shared classes `.page`, `.page-main`, `.title`, `.page-title`, `.section-title`, `.body`, `.subtle`, `.meta`, `.panel`, `.card`, `.btn`, `.input`, `.chip`, `.badge`, `.modal-mask`, and `.sheet` backed by semantic tokens.
- Consumes: no new runtime dependency.

- [ ] **Step 1: Add a failing theme architecture test**

Create `frontend/src/styles.test.js`:

```js
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { describe, expect, it } from 'vitest'

const srcRoot = resolve(process.cwd(), 'src')
const styles = readFileSync(resolve(srcRoot, 'styles.css'), 'utf8')
const vueFiles = [
  'App.vue',
  'components/AppTabBar.vue',
  'components/Avatar.vue',
  'components/DishImageCard.vue',
  'components/Icons.vue',
  'components/MealCard.vue',
  'components/MealDishFilters.vue',
  'components/PageHeader.vue',
  'components/PinPad.vue',
  'pages/admin/index.vue',
  'pages/dish-form/index.vue',
  'pages/dishes/index.vue',
  'pages/home/index.vue',
  'pages/login/index.vue',
  'pages/me/index.vue',
  'pages/meal-detail/index.vue',
  'pages/meals/index.vue',
  'pages/setup/index.vue',
  'pages/wall/index.vue',
]

describe('theme architecture', () => {
  it('defines the required primitive and semantic roles', () => {
    for (const token of [
      '--palette-canvas', '--palette-forest-700', '--palette-ink-900',
      '--theme-bg-page', '--theme-bg-surface', '--theme-text-primary',
      '--theme-text-secondary', '--theme-action-primary',
      '--theme-border-subtle', '--theme-image-overlay', '--theme-nav-bg',
    ]) expect(styles).toContain(token)
  })

  it('keeps all Vue components on script setup', () => {
    for (const file of vueFiles) {
      const source = readFileSync(resolve(srcRoot, file), 'utf8')
      expect(source, file).toContain('<script setup lang="js">')
      expect(source, file).not.toMatch(/export\s+default/)
    }
  })
})
```

- [ ] **Step 2: Run the new test and verify it fails on the missing semantic layer and current raw colors**

Run:

```powershell
cd frontend
npm test -- src/styles.test.js
```

Expected: FAIL because the required `--palette-*` and `--theme-*` roles are missing.

- [ ] **Step 3: Replace the root color block with primitive and semantic layers**

At the beginning of `frontend/src/styles.css`, define the approved existing palette and mappings:

```css
:root,
page,
[data-theme="default"] {
  --palette-neutral-0: #ffffff;
  --palette-canvas: #f6f6f1;
  --palette-forest-700: #234c35;
  --palette-forest-800: #173e2a;
  --palette-ink-900: #19221c;
  --palette-moss-600: #6f8074;
  --palette-line-200: #dce0da;
  --palette-ivory-100: #f0ead9;
  --palette-danger-600: #b54747;
  --palette-warning-600: #a66b26;
  --palette-green-050: #e7ebe4;
  --palette-green-100: #e2e9e2;
  --palette-danger-050: #f8eceb;
  --palette-overlay-900: rgba(5, 8, 6, 0.92);
  --palette-overlay-600: rgba(6, 9, 7, 0.65);
  --palette-overlay-200: rgba(7, 9, 8, 0.18);

  --theme-bg-page: var(--palette-canvas);
  --theme-bg-surface: var(--palette-neutral-0);
  --theme-bg-subtle: var(--palette-green-050);
  --theme-bg-elevated: var(--palette-neutral-0);
  --theme-text-primary: var(--palette-ink-900);
  --theme-text-secondary: var(--palette-moss-600);
  --theme-text-inverse: var(--palette-neutral-0);
  --theme-text-action: var(--palette-forest-700);
  --theme-action-primary: var(--palette-forest-700);
  --theme-action-primary-strong: var(--palette-forest-800);
  --theme-action-on-primary: var(--palette-neutral-0);
  --theme-border-subtle: var(--palette-line-200);
  --theme-border-strong: var(--palette-moss-600);
  --theme-danger: var(--palette-danger-600);
  --theme-danger-subtle: var(--palette-danger-050);
  --theme-warning: var(--palette-warning-600);
  --theme-success-subtle: var(--palette-green-100);
  --theme-focus-ring: var(--palette-forest-700);
  --theme-image-overlay: linear-gradient(to top, var(--palette-overlay-900) 0%, var(--palette-overlay-600) 27%, var(--palette-overlay-200) 54%, transparent 70%);
  --theme-image-text: var(--palette-neutral-0);
  --theme-image-text-muted: rgba(255, 255, 255, 0.78);
  --theme-image-control: rgba(16, 22, 18, 0.68);
  --theme-nav-bg: rgba(255, 255, 252, 0.97);
  --theme-modal-scrim: rgba(10, 16, 12, 0.48);
  --theme-shadow-soft: 0 16rpx 42rpx rgba(25, 34, 28, 0.08);
}
```

Keep raw values confined to this centralized theme block. Replace all shared primitive usages below it with semantic roles. Set `.page` mobile gutters to `36rpx`, preserve safe areas, and add visible H5 `:focus-visible` treatment using `--theme-focus-ring`.

- [ ] **Step 4: Remove the duplicate raw page colors from App.vue**

Delete the `<style>` block in `frontend/src/App.vue`; `main.js` already loads `styles.css`, which owns the page surface and text color.

- [ ] **Step 5: Run the focused test and confirm the theme foundation passes**

Run:

```powershell
npm test -- src/styles.test.js
```

Expected: PASS for the required theme roles and Vue 3 component convention.

- [ ] **Step 6: Commit the theme foundation and guard**

```powershell
git add frontend/src/styles.css frontend/src/App.vue frontend/src/styles.test.js
git commit -m "refactor: establish semantic frontend theme"
```

---

### Task 2: Refactor Shared Navigation, Headers, Meal Rows, and Media Cards

**Files:**
- Modify: `frontend/src/components/AppTabBar.vue`
- Modify: `frontend/src/components/PageHeader.vue`
- Modify: `frontend/src/components/MealCard.vue`
- Modify: `frontend/src/components/DishImageCard.vue`
- Modify: `frontend/src/components/MealDishFilters.vue`
- Modify: `frontend/src/components/Avatar.vue`
- Modify: `frontend/src/components/PinPad.vue`

**Interfaces:**
- Consumes: semantic tokens from Task 1.
- Produces: `MealCard` Boolean prop `compact`, default `false`, for dense full-list rendering.
- Preserves: all existing props, emits, routes, labels, and tap behavior.

- [ ] **Step 1: Extend the static test with structural component assertions**

Append to `frontend/src/styles.test.js`:

```js
describe('shared editorial components', () => {
  it('keeps the four-item product navigation', () => {
    const tabbar = readFileSync(resolve(srcRoot, 'components/AppTabBar.vue'), 'utf8')
    expect(tabbar.match(/label:\s*'[^']+'/g)).toEqual([
      "label: '首页'", "label: '饭局'", "label: '贡献'", "label: '我的'",
    ])
  })

  it('supports a compact meal-row variant without changing its public event', () => {
    const mealCard = readFileSync(resolve(srcRoot, 'components/MealCard.vue'), 'utf8')
    expect(mealCard).toContain("compact: { type: Boolean, default: false }")
    expect(mealCard).toContain("defineEmits(['open'])")
  })
})
```

- [ ] **Step 2: Run the focused test and verify the compact-card assertion fails**

```powershell
cd frontend
npm test -- src/styles.test.js
```

Expected: FAIL because `MealCard` does not yet expose `compact`.

- [ ] **Step 3: Recompose the bottom navigation and page header**

Keep the existing `tabs` array and routing. In `AppTabBar.vue`, use semantic tokens for the full-width translucent surface, subtle top shadow, inactive labels, and active forest treatment. Give the active tab an internal elevated surface without changing its `25%` column width or the bar height.

In `PageHeader.vue`, retain `title`, `subtitle`, `compact`, and the default slot. Use the shared page-title scale, a stable `min-height`, a `48-64rpx` lower gap, and an action column that does not compress the title.

- [ ] **Step 4: Recompose MealCard around stable regions**

Add the prop and root modifier:

```vue
<view class="meal-row" :class="{ compact }" @tap="open">
```

```js
const props = defineProps({
  meal: { type: Object, default: () => ({}) },
  compact: { type: Boolean, default: false },
})
```

Use a three-region grid, `28-32rpx` focus-card radius, semantic surface/border/shadow tokens, and a visually distinct date block. The compact modifier reduces padding and radius for the full list but does not remove metadata.

- [ ] **Step 5: Migrate image cards, filters, avatars, and PIN controls to semantic roles**

In `DishImageCard.vue`, replace the raw gradient and white/dark literals with `--theme-image-*` tokens while preserving `4 / 5`, text placement, and isolated toggle behavior. Update `MealDishFilters.vue`, `Avatar.vue`, and `PinPad.vue` to use the same semantic border, surface, text, action, focus, and state tokens. Do not alter their scripts or emitted events unless required for the `compact` prop above.

- [ ] **Step 6: Run focused and full unit tests**

```powershell
npm test -- src/styles.test.js
npm test
```

Expected: shared-component assertions and the full suite pass.

- [ ] **Step 7: Commit shared component styling**

```powershell
git add frontend/src/components frontend/src/styles.test.js
git commit -m "refactor: unify editorial UI components"
```

---

### Task 3: Recompose Home, Meal List, and Meal Detail

**Files:**
- Modify: `frontend/src/pages/home/index.vue`
- Modify: `frontend/src/pages/meals/index.vue`
- Modify: `frontend/src/pages/meal-detail/index.vue`

**Interfaces:**
- Consumes: `MealCard` with optional `compact` and all semantic theme roles.
- Preserves: existing API requests, computed properties, creation sheet, filters, ordering mutations, cook actions, tabs, reviews, and ingredient-list behavior.
- Produces: the reference-inspired opening hierarchy and unified meal-page rhythm.

- [ ] **Step 1: Add page-contract tests before changing templates**

Append to `frontend/src/styles.test.js`:

```js
describe('meal page contracts', () => {
  it('keeps ordering and cook claiming as separate home and detail actions', () => {
    const home = readFileSync(resolve(srcRoot, 'pages/home/index.vue'), 'utf8')
    const detail = readFileSync(resolve(srcRoot, 'pages/meal-detail/index.vue'), 'utf8')
    expect(home).toContain('开饭局')
    expect(detail).toContain('我来掌勺')
    expect(detail).toContain('点菜')
    expect(detail).toContain('已点菜品')
  })

  it('uses compact meal rows only on the full meal list', () => {
    const home = readFileSync(resolve(srcRoot, 'pages/home/index.vue'), 'utf8')
    const meals = readFileSync(resolve(srcRoot, 'pages/meals/index.vue'), 'utf8')
    expect(home).not.toMatch(/<MealCard[^>]*\scompact/)
    expect(meals).toMatch(/<MealCard[^>]*\scompact/)
  })
})
```

- [ ] **Step 2: Run the focused test and verify the list-density assertion fails**

```powershell
cd frontend
npm test -- src/styles.test.js
```

Expected: FAIL until the full meal list passes `compact`.

- [ ] **Step 3: Recompose the home page without changing its script logic**

Change the template composition to:

```vue
<view class="home-intro">
  <text class="family">{{ settings.family_name || '我们的饭桌' }}</text>
  <text class="home-title">你好，{{ me?.name || '家人' }}</text>
  <text class="home-prompt">今天想吃点什么？</text>
</view>
<view class="section-head home-section-head">
  <text class="section-title">临近的饭局</text>
  <button class="section-action" @tap="showCreate = true">
    <Icon icon="Plus" :size="18" />
    <text>开饭局</text>
  </button>
</view>
```

Remove the separate dark create banner. Keep the existing loading, error, empty, list, modal, `load`, `create`, and navigation functions. Place `查看全部饭局` after populated results as a text command. Style the greeting as the single tinted editorial band and keep upcoming `MealCard` instances in focus mode.

- [ ] **Step 4: Apply compact rows and editorial grouping to the meal list**

Pass `compact` to every `MealCard` on `pages/meals/index.vue`. Retain current active/history derivation and page actions. Replace raw page colors with semantic roles, use the shared `PageHeader`, and separate groups using whitespace plus one divider rather than nested cards.

- [ ] **Step 5: Align meal detail hierarchy without changing its flow**

Keep all existing script state and request functions. Update only template wrappers/classes needed to express: back/status line, strong title/meta band, independent cook section, meal actions, stable view tabs, filters, dish grid, ordered list, reviews, and sheets. Migrate all raw colors to semantic roles, including errors, stars, placeholders, detail-sheet text, and skipped states.

- [ ] **Step 6: Run unit tests and H5 build**

```powershell
npm test
npm run build:h5
```

Expected: all Vitest tests pass and H5 build exits successfully.

- [ ] **Step 7: Commit the meal experience composition**

```powershell
git add frontend/src/pages/home/index.vue frontend/src/pages/meals/index.vue frontend/src/pages/meal-detail/index.vue frontend/src/styles.test.js
git commit -m "refactor: compose editorial meal experience"
```

---

### Task 4: Unify Profile, Contribution, Administration, Authentication, and Dish Management

**Files:**
- Modify: `frontend/src/pages/wall/index.vue`
- Modify: `frontend/src/pages/me/index.vue`
- Modify: `frontend/src/pages/admin/index.vue`
- Modify: `frontend/src/pages/dishes/index.vue`
- Modify: `frontend/src/pages/dish-form/index.vue`
- Modify: `frontend/src/pages/login/index.vue`
- Modify: `frontend/src/pages/setup/index.vue`

**Interfaces:**
- Consumes: shared theme and layout primitives from Tasks 1-2.
- Preserves: page scripts, administrator visibility rules, routes, form models, validation, and all API operations.
- Produces: no new public runtime interface.

- [ ] **Step 1: Extend static tests for administrator placement and commerce exclusions**

Append to `frontend/src/styles.test.js`:

```js
describe('product navigation and copy constraints', () => {
  it('keeps dish management in the administrator section of My', () => {
    const mePage = readFileSync(resolve(srcRoot, 'pages/me/index.vue'), 'utf8')
    expect(mePage).toContain('管理员功能')
    expect(mePage).toContain('菜品管理')
  })

  it('does not introduce commerce terminology', () => {
    for (const file of vueFiles) {
      const source = readFileSync(resolve(srcRoot, file), 'utf8')
      expect(source, file).not.toMatch(/价格|购物车|结算|付款|支付/)
    }
  })

  it('keeps raw component colors inside the centralized theme', () => {
    const rawColor = /#[0-9a-f]{3,8}\b|rgba?\(/i
    for (const file of vueFiles) {
      const source = readFileSync(resolve(srcRoot, file), 'utf8')
      const withoutNativeSwitchException = source.replace(
        "const NATIVE_SWITCH_COLOR = '#234c35'",
        '',
      )
      expect(withoutNativeSwitchException, file).not.toMatch(rawColor)
    }
  })
})
```

- [ ] **Step 2: Run the focused tests before page migration**

```powershell
cd frontend
npm test -- src/styles.test.js
```

Expected: business-contract assertions pass; raw-color guard fails on the remaining page styles.

- [ ] **Step 3: Migrate contribution and profile pages**

Use `PageHeader`, semantic text/surface roles, consistent `48-64rpx` section spacing, and stable dividers. Keep contribution heatmap dimensions and add a visible text distinction between contribution totals so meaning is not color-only. On `我的`, retain the profile lead and existing grouped menu rows; keep `管理员功能` and `菜品管理` visibility logic unchanged.

- [ ] **Step 4: Migrate administration and dish-management pages**

Use unframed full-width sections with dividers for settings, schedules, members, dish lists, and forms. Because the native uni-app `switch` requires a literal runtime color rather than a CSS custom property, declare the single documented exception in `pages/admin/index.vue` and bind both switches to it:

```js
const NATIVE_SWITCH_COLOR = '#234c35'
```

```vue
<switch :checked="settings.registration_open" :color="NATIVE_SWITCH_COLOR" @change="settings.registration_open = $event.detail.value" />
<switch :checked="schedule.enabled" :color="NATIVE_SWITCH_COLOR" @change="toggleSchedule(schedule, $event.detail.value)" />
```

The test from Step 1 removes only that exact constant declaration before checking for raw colors; it does not broadly allow component literals.

Keep dish image cards photo-led. Do not overlay edit/archive controls on images. Preserve every existing form field, picker, ingredient row, step row, save action, permission check, and navigation target.

- [ ] **Step 5: Migrate setup and login pages**

Apply the shared shell, type scale, semantic surfaces, field rhythm, and stable tap targets. Keep bootstrap, member selection, registration, PIN, server setting, and redirect behavior identical. The family/brand name remains the first meaningful visual signal.

- [ ] **Step 6: Run the theme guard, full unit suite, and H5 build**

```powershell
npm test -- src/styles.test.js
npm test
npm run build:h5
```

Expected: all tests pass, no unapproved raw color remains in Vue styles, every Vue file uses script setup, and the H5 build succeeds.

- [ ] **Step 7: Commit the remaining page migration**

```powershell
git add frontend/src/pages frontend/src/styles.test.js
git commit -m "refactor: unify supporting frontend pages"
```

---

### Task 5: Perform Responsive Visual QA and Final Regression

**Files:**
- Modify as findings require: `frontend/src/styles.css`
- Modify as findings require: files already listed in Tasks 2-4
- Do not modify: backend files, package manifests, route definitions

**Interfaces:**
- Consumes: the complete themed UI from Tasks 1-4 and the existing server at `http://localhost:5173`.
- Produces: verified responsive behavior with no new runtime API.

- [ ] **Step 1: Verify the existing server before browser testing**

Open `http://localhost:5173` in the existing in-app browser. If it is unavailable, report the unavailable user-owned service instead of starting another one.

- [ ] **Step 2: Capture and inspect the mobile experience at approximately 390x844**

Inspect home, meals, one meal detail in both tabs, contribution, My, dish management, admin, login, and setup. Confirm:

```text
No text overlap or clipped controls
36rpx-equivalent side gutters remain consistent
Bottom navigation does not cover content
Active navigation does not resize the bar
Meal status, titles, and actions fit their regions
Dish images render with readable black-gradient copy
Sheets respect bottom safe area
```

- [ ] **Step 3: Capture and inspect tablet and desktop widths**

Repeat at approximately `768x1024` and `1440x900`. Confirm content width caps, centered sheets, wider grids, readable line lengths, and that typography does not scale with viewport width.

- [ ] **Step 4: Fix visual defects with the smallest owning selector**

For each defect, edit the shared component or token that owns it. Use page-local CSS only when the issue is genuinely unique to that page. Do not add raw colors or behavior changes while correcting layout.

- [ ] **Step 5: Run final automated verification**

```powershell
cd frontend
npm test
npm run build:h5
rg -n "export\s+default" src -g "*.vue"
```

Expected: all tests pass; H5 build succeeds; ripgrep returns no Vue matches.

- [ ] **Step 6: Attempt the known Mini Program check without changing dependencies**

```powershell
npm run build:mp-weixin
```

Expected: either the build passes, or it reproduces the pre-existing `injectHook` export mismatch between the pinned alpha uni-app packages and `vue@3.4.20`. Do not upgrade or rewrite dependencies as part of this plan.

- [ ] **Step 7: Review the final diff for scope and commit visual corrections**

```powershell
git diff --check
git diff --stat
git status --short
git add frontend/src/styles.css frontend/src/App.vue frontend/src/components frontend/src/pages frontend/src/styles.test.js
git commit -m "refactor: complete responsive dining UI"
```

Confirm the final diff contains no backend, database, dependency, lockfile, or route-definition changes from this refactor.
