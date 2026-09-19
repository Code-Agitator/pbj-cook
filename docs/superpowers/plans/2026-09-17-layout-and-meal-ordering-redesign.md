# DaCook Layout and Meal Ordering Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rebuild DaCook around a four-destination application shell and a premium, meal-scoped ordering experience with image-led dish cards, complete filters, aggregated selections, cook tools, and consistent responsive typography and spacing.

**Architecture:** Keep the existing Vue 3 uni-app and FastAPI architecture. Add tested pure frontend helpers for filtering and aggregation, one cook-authorized ingredient-list endpoint, shared visual components for dish presentation and filters, and a tokenized global CSS shell consumed by the existing pages. Keep page-local state and the current API client; do not add a store or UI framework.

**Tech Stack:** Vue 3, uni-app, JavaScript, Vitest, FastAPI, SQLite, pytest, H5, WeChat Mini Program.

**Spec:** `docs/superpowers/specs/2026-09-17-layout-and-meal-ordering-redesign.md`

## Global Constraints

- Bottom navigation is exactly `首页 / 饭局 / 贡献 / 我的`.
- Dish management moves to the administrator section of `我的`; the dish route remains registered.
- Ordering exists only inside a meal and remains independent from claiming the cook role.
- Dish cards use full-bleed images, a bottom black gradient, white overlay text, and no price/cart/checkout language.
- Use the existing platform font stack; do not add a web-font or runtime UI dependency.
- Preserve H5 and WeChat Mini Program compatibility; avoid browser-only APIs without guarded fallback.
- Use existing icons through `Icons.vue`; extend the map only where a required symbol is missing.
- All created or materially rewritten `.vue` files use Vue 3 Composition API with `<script setup>`; do not add Options API `export default` blocks.
- The current workspace has no `.git` directory. The commit commands below become executable only if the user initializes or supplies a Git repository; do not initialize Git implicitly.

---

## File Structure

### New files

- `frontend/src/utils/meals.js`: pure dish filtering, tag derivation, tab selection, and order grouping.
- `frontend/src/utils/meals.test.js`: Vitest coverage for all meal-view helpers.
- `frontend/src/components/DishImageCard.vue`: reusable full-image dish card with overlay text and selection control.
- `frontend/src/components/MealDishFilters.vue`: cuisine, tag, selected-only, reset, and search controls.
- `backend/app/ingredients.py`: pure ingredient quantity normalization and aggregation.
- `backend/tests/test_ingredient_list.py`: endpoint authorization and aggregation contract tests.

### Modified files

- `frontend/src/styles.css`: global design tokens, shell, type scale, controls, states, and responsive rules.
- `frontend/src/App.vue`: align page background and default text with the token system.
- `frontend/src/components/AppTabBar.vue`: four-item navigation and non-floating safe-area layout.
- `frontend/src/components/PageHeader.vue`: stable title/subtitle/action alignment.
- `frontend/src/components/MealCard.vue`: compact meal-row presentation.
- `frontend/src/components/Icons.vue`: add only required menu/action symbols.
- `frontend/src/pages/home/index.vue`: meal-first home composition.
- `frontend/src/pages/meals/index.vue`: active/history list rhythm.
- `frontend/src/pages/meal-detail/index.vue`: independent cook module, ordering filters, image cards, selected summary, ingredient list, and reviews.
- `frontend/src/pages/dishes/index.vue`: administrator dish library using shared image cards and filters.
- `frontend/src/pages/dish-form/index.vue`: tokenized long-form layout.
- `frontend/src/pages/wall/index.vue`: aligned contribution statistics and stable heatmaps.
- `frontend/src/pages/me/index.vue`: grouped account/admin menu and dish-management entry.
- `frontend/src/pages/admin/index.vue`: section-based family administration layout.
- `frontend/src/pages/setup/index.vue`: tokenized setup layout.
- `frontend/src/pages/login/index.vue`: tokenized login/member selection layout.
- `frontend/src/pages.json`: preserve routes and update global background.
- `frontend/package.json`: add the stable `build:mp-weixin` script.
- `backend/app/main.py`: expose the cook-only ingredient-list endpoint.

---

### Task 1: Lock Meal Filtering and Aggregation Rules

**Files:**
- Create: `frontend/src/utils/meals.js`
- Create: `frontend/src/utils/meals.test.js`

**Interfaces:**
- Produces: `availableDishTags(dishes, cuisineId): string[]`
- Produces: `filterMealDishes({ dishes, cuisineId, tags, query, selectedIds }): object[]`
- Produces: `groupMealOrders(orders): Array<{ dishId, name, image, people }>`
- Produces: `mealDetailInitialTab({ canOrder, isCook }): 'pick' | 'ordered'`
- Produces: `sanitizeMealTags(tags, availableTags): Set<string>`
- Consumers: `pages/meal-detail/index.vue` and `components/MealDishFilters.vue`

- [ ] **Step 1: Write failing helper tests**

Create `frontend/src/utils/meals.test.js` with concrete cases:

```js
import { describe, expect, it } from 'vitest'
import {
  availableDishTags,
  filterMealDishes,
  groupMealOrders,
  mealDetailInitialTab,
  sanitizeMealTags,
} from './meals'

const dishes = [
  { id: 'a', name: '翡翠虾仁', description: '清鲜', cuisine_id: 'home', tags: ['清淡', '快手'] },
  { id: 'b', name: '松茸炖鸡', description: '慢炖鲜香', cuisine_id: 'soup', tags: ['滋补', '清淡'] },
  { id: 'c', name: '辣子鸡', description: '香辣', cuisine_id: 'sichuan', tags: ['下饭'] },
]

describe('availableDishTags', () => {
  it('derives frequency-ordered tags from the active cuisine', () => {
    expect(availableDishTags(dishes, null)).toEqual(['清淡', '快手', '滋补', '下饭'])
    expect(availableDishTags(dishes, 'home')).toEqual(['清淡', '快手'])
  })
})

describe('filterMealDishes', () => {
  it('combines cuisine, OR tags, query, and selected-only filtering', () => {
    expect(filterMealDishes({ dishes, cuisineId: 'home', tags: new Set(), query: '', selectedIds: new Set() }).map(x => x.id)).toEqual(['a'])
    expect(filterMealDishes({ dishes, cuisineId: null, tags: new Set(['清淡', '下饭']), query: '', selectedIds: new Set() }).map(x => x.id)).toEqual(['a', 'b', 'c'])
    expect(filterMealDishes({ dishes, cuisineId: null, tags: new Set(['__mine__']), query: '', selectedIds: new Set(['b']) }).map(x => x.id)).toEqual(['b'])
    expect(filterMealDishes({ dishes, cuisineId: null, tags: new Set(), query: '慢炖', selectedIds: new Set() }).map(x => x.id)).toEqual(['b'])
  })
})

describe('groupMealOrders', () => {
  it('groups by dish and sorts by descending member count', () => {
    const result = groupMealOrders([
      { dish_id: 'a', dish_name: '虾仁', user_id: 'u1', user_name: '林一' },
      { dish_id: 'b', dish_name: '炖鸡', user_id: 'u2', user_name: '周禾' },
      { dish_id: 'a', dish_name: '虾仁', user_id: 'u2', user_name: '周禾' },
    ])
    expect(result.map(x => [x.dishId, x.people.length])).toEqual([['a', 2], ['b', 1]])
  })
})

describe('meal detail view state', () => {
  it('defaults cooks to summary and other members to ordering', () => {
    expect(mealDetailInitialTab({ canOrder: true, isCook: true })).toBe('ordered')
    expect(mealDetailInitialTab({ canOrder: true, isCook: false })).toBe('pick')
    expect(mealDetailInitialTab({ canOrder: false, isCook: false })).toBe('ordered')
  })

  it('removes tags that are unavailable after cuisine changes', () => {
    expect([...sanitizeMealTags(new Set(['清淡', '滋补', '__mine__']), ['清淡'])]).toEqual(['清淡', '__mine__'])
  })
})
```

- [ ] **Step 2: Run the tests and verify the module is missing**

Run:

```powershell
cd frontend
npx vitest run src/utils/meals.test.js
```

Expected: FAIL because `src/utils/meals.js` does not exist.

- [ ] **Step 3: Implement the pure helpers**

Create `frontend/src/utils/meals.js`:

```js
const normalizedTags = (dish) => Array.isArray(dish?.tags) ? dish.tags.filter(Boolean) : []

export function availableDishTags(dishes, cuisineId) {
  const counts = new Map()
  for (const dish of Array.isArray(dishes) ? dishes : []) {
    if (cuisineId && dish?.cuisine_id !== cuisineId) continue
    for (const tag of normalizedTags(dish)) counts.set(tag, (counts.get(tag) || 0) + 1)
  }
  return [...counts].sort((a, b) => b[1] - a[1]).map(([tag]) => tag)
}

export function sanitizeMealTags(tags, availableTags) {
  const valid = new Set(availableTags)
  return new Set([...tags].filter(tag => tag === '__mine__' || valid.has(tag)))
}

export function filterMealDishes({ dishes, cuisineId, tags, query, selectedIds }) {
  const activeTags = tags instanceof Set ? tags : new Set()
  const selected = selectedIds instanceof Set ? selectedIds : new Set()
  const needle = String(query || '').trim().toLocaleLowerCase()
  return (Array.isArray(dishes) ? dishes : []).filter((dish) => {
    if (!dish || (cuisineId && dish.cuisine_id !== cuisineId)) return false
    if (activeTags.size) {
      const mine = activeTags.has('__mine__') && selected.has(dish.id)
      const tagMatch = [...activeTags].some(tag => tag !== '__mine__' && normalizedTags(dish).includes(tag))
      if (!mine && !tagMatch) return false
    }
    if (!needle) return true
    return `${dish.name || ''} ${dish.description || ''} ${normalizedTags(dish).join(' ')}`.toLocaleLowerCase().includes(needle)
  })
}

export function groupMealOrders(orders) {
  const grouped = new Map()
  for (const order of Array.isArray(orders) ? orders : []) {
    if (!order?.dish_id) continue
    if (!grouped.has(order.dish_id)) grouped.set(order.dish_id, {
      dishId: order.dish_id,
      name: order.dish_name || '未命名菜品',
      image: order.dish_image || null,
      people: [],
    })
    grouped.get(order.dish_id).people.push({ id: order.user_id, name: order.user_name || '成员', avatar: order.user_avatar || null })
  }
  return [...grouped.values()].sort((a, b) => b.people.length - a.people.length || a.name.localeCompare(b.name, 'zh-CN'))
}

export function mealDetailInitialTab({ canOrder, isCook }) {
  return canOrder && !isCook ? 'pick' : 'ordered'
}
```

- [ ] **Step 4: Run focused and full frontend tests**

Run:

```powershell
npx vitest run src/utils/meals.test.js
npm test
```

Expected: PASS.

- [ ] **Step 5: Commit when Git is available**

```powershell
git add frontend/src/utils/meals.js frontend/src/utils/meals.test.js
git commit -m "test: define meal ordering view rules"
```

---

### Task 2: Add the Cook-Only Ingredient List Contract

**Files:**
- Create: `backend/app/ingredients.py`
- Create: `backend/tests/test_ingredient_list.py`
- Modify: `backend/app/main.py:487-541`

**Interfaces:**
- Produces: `aggregate_ingredients(rows: list[dict]) -> list[dict]`
- Produces: `GET /api/meals/{meal_id}/ingredient-list`
- Response: `{ "meal_id": str, "items": [{ "name": str, "unit": str, "total": float | null, "fragments": list[str] }] }`
- Consumer: `frontend/src/pages/meal-detail/index.vue`

- [ ] **Step 1: Write pure aggregation and endpoint contract tests**

Create `backend/tests/test_ingredient_list.py`. Use `family`, `register_member`, and `create_meal`; add a small local `create_dish()` helper that POSTs `/api/dishes` with ingredients.

Required assertions:

```python
from app.ingredients import aggregate_ingredients
from conftest import create_meal, register_member


def test_aggregate_ingredients_sums_compatible_numeric_quantities():
    assert aggregate_ingredients([
        {"name": "鸡蛋", "quantity": "2", "unit": "个"},
        {"name": " 鸡蛋 ", "quantity": "1.5", "unit": "个"},
        {"name": "盐", "quantity": "少许", "unit": ""},
    ]) == [
        {"name": "鸡蛋", "unit": "个", "total": 3.5, "fragments": []},
        {"name": "盐", "unit": "", "total": None, "fragments": ["少许"]},
    ]


def test_ingredient_list_requires_the_assigned_cook(client, family):
    meal_id = create_meal(client, family["admin_headers"])
    _, member_headers = register_member(client)
    assert client.get(f"/api/meals/{meal_id}/ingredient-list", headers=family["admin_headers"]).status_code == 403
    assert client.post(f"/api/meals/{meal_id}/cook", headers=member_headers).status_code == 200
    assert client.get(f"/api/meals/{meal_id}/ingredient-list", headers=member_headers).status_code == 200
```

Add endpoint cases for:

- missing meal returns `404`;
- an empty meal returns `items: []`;
- multiple members selecting the same dish do not duplicate that dish's ingredients;
- skipped dishes are excluded;
- same ingredient name with different units produces separate rows;
- nonnumeric quantities are preserved in `fragments` without duplication.

- [ ] **Step 2: Run the new backend tests and verify failure**

Run:

```powershell
cd backend
.venv\Scripts\python -m pytest tests/test_ingredient_list.py -q
```

Expected: FAIL because `app.ingredients` and the endpoint do not exist.

- [ ] **Step 3: Implement deterministic aggregation**

Create `backend/app/ingredients.py`:

```python
from decimal import Decimal, InvalidOperation


def _number(value):
    try:
        return Decimal(str(value).strip())
    except (InvalidOperation, ValueError):
        return None


def aggregate_ingredients(rows):
    grouped = {}
    for row in rows:
        name = str(row.get("name", "")).strip()
        unit = str(row.get("unit", "")).strip()
        quantity = str(row.get("quantity", "")).strip()
        if not name:
            continue
        key = (name.casefold(), unit.casefold())
        item = grouped.setdefault(key, {"name": name, "unit": unit, "numbers": [], "fragments": []})
        numeric = _number(quantity)
        if numeric is not None:
            item["numbers"].append(numeric)
        elif quantity and quantity not in item["fragments"]:
            item["fragments"].append(quantity)

    result = []
    for item in grouped.values():
        total = sum(item["numbers"], Decimal(0)) if item["numbers"] and not item["fragments"] else None
        result.append({
            "name": item["name"],
            "unit": item["unit"],
            "total": float(total) if total is not None else None,
            "fragments": item["fragments"] + ([str(sum(item["numbers"], Decimal(0)))] if item["numbers"] and item["fragments"] else []),
        })
    return result
```

- [ ] **Step 4: Implement the authorized endpoint**

In `backend/app/main.py`, import `aggregate_ingredients` and add the route after `get_meal`:

```python
@app.get("/api/meals/{meal_id}/ingredient-list")
def meal_ingredient_list(meal_id: str, me=Depends(auth_dependency)):
    with db() as conn:
        meal = conn.execute("SELECT id,cook_id FROM meals WHERE id=?", (meal_id,)).fetchone()
        if not meal:
            raise HTTPException(404, "饭局不存在")
        if meal["cook_id"] != me["id"]:
            raise HTTPException(403, "仅掌勺人可查看食材清单")
        ingredient_rows = rows(conn.execute("""
            SELECT i.name,i.quantity,i.unit
            FROM dish_ingredients i
            JOIN (
              SELECT DISTINCT o.dish_id FROM orders o
              WHERE o.meal_id=? AND NOT EXISTS (
                SELECT 1 FROM meal_dish_skips s
                WHERE s.meal_id=o.meal_id AND s.dish_id=o.dish_id
              )
            ) picked ON picked.dish_id=i.dish_id
            ORDER BY i.name,i.unit,i.ord
        """, (meal_id,)).fetchall())
        return {"meal_id": meal_id, "items": aggregate_ingredients(ingredient_rows)}
```

- [ ] **Step 5: Run focused and full backend tests**

Run:

```powershell
.venv\Scripts\python -m pytest tests/test_ingredient_list.py -q
.venv\Scripts\python -m pytest -q
```

Expected: PASS.

- [ ] **Step 6: Commit when Git is available**

```powershell
git add backend/app/ingredients.py backend/app/main.py backend/tests/test_ingredient_list.py
git commit -m "feat: add cook ingredient list endpoint"
```

---

### Task 3: Establish the Global Visual System and Four-Item Shell

**Files:**
- Modify: `frontend/src/styles.css`
- Modify: `frontend/src/App.vue`
- Modify: `frontend/src/components/AppTabBar.vue`
- Modify: `frontend/src/components/PageHeader.vue`
- Modify: `frontend/src/components/Icons.vue`
- Modify: `frontend/src/pages.json`
- Modify: `frontend/package.json`

**Interfaces:**
- Produces: global CSS tokens and utility classes consumed by every page.
- Produces: `AppTabBar(active: 'home' | 'meals' | 'wall' | 'me')`.

- [ ] **Step 1: Add the Mini Program build script**

Add to `frontend/package.json`:

```json
"build:mp-weixin": "uni build -p mp-weixin"
```

- [ ] **Step 2: Replace ad hoc global values with the approved tokens**

Rewrite the top of `styles.css` with the exact palette and stable scale from the spec:

```css
:root {
  --color-canvas: #f6f6f1;
  --color-surface: #ffffff;
  --color-ink: #19221c;
  --color-forest: #234c35;
  --color-forest-strong: #173e2a;
  --color-moss: #6f8074;
  --color-line: #dce0da;
  --color-ivory: #f0ead9;
  --color-danger: #b54747;
  --color-warning: #a66b26;
  --space-1: 8rpx;
  --space-2: 12rpx;
  --space-3: 16rpx;
  --space-4: 24rpx;
  --space-5: 32rpx;
  --space-6: 48rpx;
  --space-7: 64rpx;
  --radius-control: 10rpx;
  --radius-panel: 18rpx;
}
```

Define `.page`, `.page-main`, `.title`, `.section-title`, `.body`, `.subtle`, `.panel`, `.btn`, `.input`, `.chip`, `.badge`, `.state`, `.sheet`, and breakpoint rules. Keep body line-height at `1.6`, letter-spacing `0`, page bottom padding large enough for the tab bar, and minimum interactive height at `80rpx`.

- [ ] **Step 3: Rebuild the tab bar with four destinations**

In `AppTabBar.vue`:

```js
tabs: [
  { key: 'home', label: '首页', path: '/pages/home/index', icon: 'Home' },
  { key: 'meals', label: '饭局', path: '/pages/meals/index', icon: 'UtensilsCrossed' },
  { key: 'wall', label: '贡献', path: '/pages/wall/index', icon: 'Sprout' },
  { key: 'me', label: '我的', path: '/pages/me/index', icon: 'UserRound' },
]
```

Use a full-width safe-area surface, fixed stable dimensions, and active color/indicator without a floating capsule or active-item resize.

- [ ] **Step 4: Normalize header and icon behavior**

Update `PageHeader.vue` to support stable wrapping and a `compact` boolean prop. Add icon-map entries needed by the account menu and dish controls, such as `BookOpen`, `ChevronRight`, `Search`, `Check`, `X`, `ListFilter`, and `ClipboardList`, using the existing code-native icon pattern.

- [ ] **Step 5: Align application backgrounds and route metadata**

Set `App.vue` and `pages.json` backgrounds to `#F6F6F1`. Keep all ten routes registered, including `pages/dishes/index` and `pages/dish-form/index`.

- [ ] **Step 6: Build both targets**

Run:

```powershell
cd frontend
npm run build:h5
npm run build:mp-weixin
```

Expected: both builds complete without CSS or template errors.

- [ ] **Step 7: Commit when Git is available**

```powershell
git add frontend/package.json frontend/src/styles.css frontend/src/App.vue frontend/src/components/AppTabBar.vue frontend/src/components/PageHeader.vue frontend/src/components/Icons.vue frontend/src/pages.json
git commit -m "refactor: establish responsive application shell"
```

---

### Task 4: Build Shared Premium Dish Presentation and Filters

**Files:**
- Create: `frontend/src/components/DishImageCard.vue`
- Create: `frontend/src/components/MealDishFilters.vue`

**Interfaces:**
- `DishImageCard` props: `dish: Object`, `src: String`, `selected: Boolean`, `selectable: Boolean`, `interestCount: Number`.
- `DishImageCard` emits: `open(dish)`, `toggle(dish.id)`.
- `MealDishFilters` props: `query`, `cuisines`, `cuisineId`, `tags`, `availableTags`, `selectedCount`, `resultCount`.
- `MealDishFilters` emits: `update:query`, `update:cuisineId`, `toggle-tag`, `reset`.

- [ ] **Step 1: Implement `DishImageCard.vue` semantics**

The template must separate the body and selection actions:

```vue
<view class="dish-image-card" @tap="$emit('open', dish)">
  <image v-if="dish.image_path" class="dish-image" :src="src" mode="aspectFill" />
  <view v-else class="dish-placeholder"><Icon icon="ChefHat" :size="26" /></view>
  <view class="dish-gradient" />
  <view class="dish-copy">
    <text class="dish-name">{{ dish.name || '未命名菜品' }}</text>
    <text v-if="flavorText" class="dish-flavors">{{ flavorText }}</text>
    <text v-if="interestCount > 0" class="dish-interest">{{ interestCount }} 人想吃</text>
  </view>
  <button v-if="selectable" class="dish-select" :class="{ selected }" @tap.stop="$emit('toggle', dish.id)">
    <Icon :icon="selected ? 'Check' : 'Plus'" :size="17" />
  </button>
</view>
```

The card uses `aspect-ratio: 4 / 5`, `8–10px` equivalent radius, cover imagery, and:

```css
.dish-gradient {
  position: absolute;
  inset: 0;
  background: linear-gradient(to top, rgba(5,8,6,.92) 0%, rgba(6,9,7,.65) 27%, rgba(7,9,8,.18) 54%, transparent 70%);
}
```

Keep overlay text to the dish name, first two or three tags, and optional interest count. Do not render management controls on the image.

- [ ] **Step 2: Implement `MealDishFilters.vue` as controlled UI**

Render:

- search input with clear icon;
- horizontal cuisine single-select including `全部`;
- tag multi-select including `只看我点的 (N)`;
- visible result count;
- `清除筛选` only when query, cuisine, or tags are active.

Use chips only for filter values. Maintain stable input and chip heights; use horizontal scrolling instead of wrapping into unpredictable card heights on narrow screens.

- [ ] **Step 3: Integrate assets without network dependencies**

Pass `assetUrl(dish.image_path)` through the required `src` prop. The final product must never hotlink external sample photography.

- [ ] **Step 4: Build and inspect the shared components in H5**

Run:

```powershell
npm run build:h5
```

Expected: PASS. Temporarily render the card from an existing page during implementation or proceed directly to Task 5 before visual sign-off; do not keep fixture markup in production.

- [ ] **Step 5: Commit when Git is available**

```powershell
git add frontend/src/components/DishImageCard.vue frontend/src/components/MealDishFilters.vue
git commit -m "feat: add premium dish browsing components"
```

---

### Task 5: Rebuild the Meal Detail Workflow

**Files:**
- Modify: `frontend/src/pages/meal-detail/index.vue`
- Modify: `frontend/src/utils/app.test.js`
- Modify: `frontend/src/utils/app.js`
- Consume: `frontend/src/utils/meals.js`
- Consume: `frontend/src/components/DishImageCard.vue`
- Consume: `frontend/src/components/MealDishFilters.vue`

**Interfaces:**
- Consumes existing meal, dish, cuisine, order, skip, status, and review endpoints.
- Consumes `GET /api/meals/{id}/ingredient-list` from Task 2.
- Produces the complete meal-detail view without changing route shape.

- [ ] **Step 1: Add failing permission-state assertions**

Extend the existing `mealInteractionState` tests to make decoupling explicit:

```js
it('does not couple ordering to cook assignment', () => {
  const noCook = mealInteractionState({ status: 'ordering', order_deadline: 200, cook_id: null }, { id: 'u2' }, 100)
  const otherCook = mealInteractionState({ status: 'ordering', order_deadline: 200, cook_id: 'u1' }, { id: 'u2' }, 100)
  expect(noCook.canOrder).toBe(true)
  expect(otherCook.canOrder).toBe(true)
  expect(otherCook.canSkip).toBe(false)
})
```

Run `npx vitest run src/utils/app.test.js`; it should pass against the intended existing behavior and guard the rewrite.

- [ ] **Step 2: Replace the page header and independent cook module**

Restructure the template into:

1. back action and meal status;
2. meal title/date/deadline summary;
3. independent cook module with identity and claim/leave/takeover action;
4. permission-gated meal status actions;
5. `点菜 / 已点菜品` views;
6. completed-meal reviews.

Do not add a stepper or any visual sequence linking cook assignment and ordering.

- [ ] **Step 3: Integrate pure filtering and 18-item batching**

Add page state:

```js
tab: 'pick',
cuisineId: null,
activeTags: new Set(),
query: '',
page: 1,
detailDish: null,
ingredientSheet: false,
ingredientItems: [],
ingredientError: '',
```

Computed values call `availableDishTags`, `sanitizeMealTags`, `filterMealDishes`, and `groupMealOrders`. `visibleDishes` returns `filteredDishes.slice(0, page * 18)`. Reset `page` to `1` whenever cuisine, tags, or query changes. Use `scroll-view` or page reach-bottom behavior supported by uni-app instead of an H5-only `IntersectionObserver` on Mini Program.

- [ ] **Step 4: Render the full-image ordering grid and detail sheet**

Use `DishImageCard` for every result. The page owns selected IDs, optimistic toggles, rollback, and pending keys. Card-body tap opens a sheet with large image, cuisine, all tags, description, ingredients, steps, source link, and a full-width select/cancel action.

When filtered results are empty, show `没有符合条件的菜品` and a `清除筛选` command. When the dish library is empty, show administrator-directed guidance without exposing admin controls to ordinary members.

- [ ] **Step 5: Replace the old `who` view with `已点菜品`**

Render grouped rows with thumbnail, dish name, member names, count, and cook-only skip/restore icon. Keep skipped rows visible with opacity plus explicit `不做` text so state is not color-only.

Show both tabs while ordering is open. Set the first tab after load with:

```js
this.tab = mealDetailInitialTab({ canOrder: this.interaction.canOrder, isCook: this.interaction.isCook })
```

When ordering closes, force `tab = 'ordered'` and hide the pick tab.

- [ ] **Step 6: Add the cook-only ingredient sheet**

From `已点菜品`, show `生成食材清单` only when `interaction.isCook`. Fetch the endpoint on demand, render rows with formatted totals/fragments, and add `复制清单`.

Use guarded H5 clipboard support and Mini Program clipboard support:

```js
copyIngredientList() {
  const text = ingredientListText(this.meal, this.ingredientItems)
  if (typeof uni.setClipboardData === 'function') return uni.setClipboardData({ data: text })
  this.ingredientFallback = text
}
```

Add `ingredientListText()` to `utils/app.js` with a focused test that checks title, numeric total/unit, and fragment formatting.

- [ ] **Step 7: Restyle reviews and all page states**

Keep the current PUT review contract. Use stable stars, comment field, save button/pending state, average if derivable, and member review rows. Restyle loading, error, invalid route, empty orders, closed ordering, and partial refresh errors using the shared state classes.

- [ ] **Step 8: Run frontend tests and both builds**

```powershell
npm test
npm run build:h5
npm run build:mp-weixin
```

Expected: PASS.

- [ ] **Step 9: Commit when Git is available**

```powershell
git add frontend/src/pages/meal-detail/index.vue frontend/src/utils/app.js frontend/src/utils/app.test.js
git commit -m "feat: rebuild meal ordering experience"
```

---

### Task 6: Move Dish Management Under the Administrator Profile

**Files:**
- Modify: `frontend/src/pages/me/index.vue`
- Modify: `frontend/src/pages/dishes/index.vue`
- Modify: `frontend/src/pages/dish-form/index.vue`
- Modify: `frontend/src/components/AppTabBar.vue`
- Consume: `frontend/src/components/DishImageCard.vue`
- Consume: `frontend/src/utils/meals.js`

**Interfaces:**
- `我的 > 菜品管理` navigates to `/pages/dishes/index` only for administrators.
- Dish and dish-form routes remain registered, but do not render `AppTabBar`.

- [ ] **Step 1: Add the administrator menu entry**

In `me/index.vue`, group menu rows into `管理员功能` and `账户`. Under the admin guard add:

```vue
<view class="menu-row" @tap="goDishes">
  <view class="menu-icon"><Icon icon="BookOpen" :size="20" /></view>
  <view class="menu-copy"><text>菜品管理</text><text class="subtle">菜品、菜系与做法</text></view>
  <Icon icon="ChevronRight" :size="18" />
</view>
```

and:

```js
goDishes() { if (this.me?.is_admin) uni.navigateTo({ url: '/pages/dishes/index' }) }
```

- [ ] **Step 2: Remove all dish-library tab-bar assumptions**

Remove `<AppTabBar active="dishes" />` and its import from `dishes/index.vue`. Add a standard back header. Confirm `AppTabBar.vue` contains no `dishes` tab.

- [ ] **Step 3: Apply shared image cards and filtering to the administrator library**

Use `DishImageCard` with `selectable=false`. Reuse search, cuisine, and tag filter semantics but keep administrator commands in the detail/action sheet. Card imagery must contain no edit/archive overlay.

- [ ] **Step 4: Guard dish-form entry in the frontend**

At load, read `currentUser()`. If `is_admin !== true`, show `仅管理员可管理菜品` and return to `我的`. Continue relying on backend authorization for mutations; do not treat the UI guard as security.

- [ ] **Step 5: Restyle the long form**

Keep all current fields and limits. Use shared form spacing, compact remove icon buttons, stable ingredient columns, section dividers, and a safe-area-aware save action that does not cover the last form row.

- [ ] **Step 6: Run tests and builds**

```powershell
npm test
npm run build:h5
npm run build:mp-weixin
```

- [ ] **Step 7: Commit when Git is available**

```powershell
git add frontend/src/pages/me/index.vue frontend/src/pages/dishes/index.vue frontend/src/pages/dish-form/index.vue frontend/src/components/AppTabBar.vue
git commit -m "refactor: move dish management under profile"
```

---

### Task 7: Apply the Layout System Across Remaining Pages

**Files:**
- Modify: `frontend/src/components/MealCard.vue`
- Modify: `frontend/src/pages/home/index.vue`
- Modify: `frontend/src/pages/meals/index.vue`
- Modify: `frontend/src/pages/wall/index.vue`
- Modify: `frontend/src/pages/admin/index.vue`
- Modify: `frontend/src/pages/setup/index.vue`
- Modify: `frontend/src/pages/login/index.vue`

**Interfaces:**
- Consumes only existing page APIs and the global shell from Task 3.
- Produces no API contract changes.

- [ ] **Step 1: Rebuild `MealCard.vue` as a compact meal row**

Preserve `mealCardData()` and the `open(id)` event. Present a stable date/status block, title, time, participant count, cook, auto badge, and chevron. Use dividers and spacing instead of a large rounded card.

- [ ] **Step 2: Restructure home around meals**

Keep create-meal behavior and validation. Use family name, greeting, a restrained dark-forest create-meal command, upcoming meal rows, and `查看全部饭局`. Do not expose dish browsing from home.

- [ ] **Step 3: Normalize active and historical meal lists**

Use consistent group headings and vertical rhythm in `meals/index.vue`. Keep existing loading, retained-data retry, empty, and navigation behavior.

- [ ] **Step 4: Rebuild contribution wall layout**

Align avatar, member statistics, streak, and the two heatmaps. Give heatmaps stable grid dimensions and prevent overflow at `390px`. Keep distinct text labels for cooking and ordering so color is not the only cue.

- [ ] **Step 5: Rebuild administration as sections**

Use full-width sections for family settings, schedules, and members. Keep validation, optimistic rollback, confirmation, and permissions intact. Replace decorative nested cards with dividers and grouped controls.

- [ ] **Step 6: Align setup and login**

Apply the type scale, field spacing, compact radius, stable member tiles, PIN pad dimensions, and accessible error states. Preserve bootstrap, registration, login, reset, and server-address behavior.

- [ ] **Step 7: Run automated checks**

```powershell
npm test
npm run build:h5
npm run build:mp-weixin
```

Expected: PASS.

- [ ] **Step 8: Commit when Git is available**

```powershell
git add frontend/src/components/MealCard.vue frontend/src/pages/home/index.vue frontend/src/pages/meals/index.vue frontend/src/pages/wall/index.vue frontend/src/pages/admin/index.vue frontend/src/pages/setup/index.vue frontend/src/pages/login/index.vue
git commit -m "refactor: unify application layouts"
```

---

### Task 8: End-to-End Verification and Visual Critique

**Files:**
- Modify only files with defects discovered during verification.

**Interfaces:**
- Verifies all interfaces from Tasks 1–7.

- [ ] **Step 1: Run the complete automated suite**

```powershell
cd backend
.venv\Scripts\python -m pytest -q

cd ..\frontend
npm test
npm run build:h5
npm run build:mp-weixin
```

Expected: all tests and builds pass.

- [ ] **Step 2: Start local services on available ports**

Use the existing backend when `http://127.0.0.1:8000/api/health` responds. Otherwise start:

```powershell
cd backend
.venv\Scripts\python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Start H5 on the next free Vite port:

```powershell
cd frontend
npm run dev:h5
```

Record the actual URL from Vite output.

- [ ] **Step 3: Verify all routes and role variants**

Exercise:

- setup and login;
- home create/enter meal;
- active/history meal lists;
- meal with no cook, current user as cook, and another cook;
- search, cuisine, multiple tags, selected-only, reset, and empty results;
- optimistic select/cancel and failure rollback;
- selected summary, skip/restore, empty summary, and ordering closed;
- ingredient list authorization, generation, and copy;
- completed-meal reviews;
- contribution wall;
- administrator and ordinary-member profile menus;
- dish list/detail/create/edit/archive;
- family administration.

- [ ] **Step 4: Capture and critique responsive screenshots**

Use browser viewport overrides at `390x844`, `768x1024`, and `1440x900`. Capture home, meal detail pick view, meal detail ordered view, dish management, contribution wall, and administration.

For every screenshot verify:

- no text overlap or clipped Chinese labels;
- tab bar does not cover content;
- dish images are nonblank and cropped around their subject;
- bottom gradients keep white text readable;
- card heights and selection icons do not shift;
- wide layouts use deliberate columns without stretching reading content;
- palette remains warm-neutral/forest rather than monochrome green;
- no price, cart, checkout, or payment language appears.

- [ ] **Step 5: Check browser console and canvas/image pixels**

Confirm there are no unhandled promise rejections, missing asset errors, or Vue warnings. For image-card screenshots, inspect pixel variance in the image regions to confirm the photographs rendered rather than leaving solid placeholders.

- [ ] **Step 6: Fix defects and rerun affected checks**

Keep fixes scoped to the failing page or shared component. Rerun its focused test, both frontend builds when CSS/templates changed, and backend tests when API behavior changed.

- [ ] **Step 7: Final commit when Git is available**

```powershell
git add frontend backend
git commit -m "fix: complete responsive redesign verification"
```

---

## Plan Self-Review

- Spec coverage: navigation, administrator dish entry, visual tokens, responsive shell, independent cook/order behavior, full-image cards, filters, selected summary, skip/restore, ingredient list, reviews, states, accessibility, and verification are each assigned to a task.
- Placeholder scan: every implementation step contains concrete files, commands, and expected behavior; no deferred markers remain.
- Interface consistency: frontend helper names, component props/events, ingredient endpoint path, and response fields are identical wherever referenced.
- Scope: the plan preserves current frameworks and APIs except for the single specified ingredient-list endpoint.
