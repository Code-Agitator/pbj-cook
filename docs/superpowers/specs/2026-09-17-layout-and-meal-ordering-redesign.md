# DaCook Layout and Meal Ordering Redesign

## Goal

Refactor the complete DaCook interface into a restrained modern Chinese private-dining experience while preserving its family collaboration model. The application should feel like browsing and composing a restaurant menu, but it must never imply prices, carts, checkout, payment, or commerce.

The redesign covers global layout, typography, spacing, navigation, every registered page, shared components, meal ordering, ordered-dish summaries, administrator dish management, responsive H5 behavior, and WeChat Mini Program compatibility.

## Product Model

A meal is the only context in which ordering happens:

1. A member creates a meal.
2. An eligible member may independently claim or leave the cook role.
3. Every member may independently select or remove dishes while ordering is open.
4. The cook may review the aggregated menu, mark dishes as not being prepared, and generate an ingredient list.
5. The meal may progress to cooking, completion, or cancellation according to the existing permission and state rules.
6. Members may review a completed meal.

Claiming the cook role and selecting dishes are fully decoupled. Neither operation enables, disables, or completes the other.

## Information Architecture

The bottom navigation contains exactly four destinations:

- `首页`: family overview, create a meal, and enter upcoming meals.
- `饭局`: active and historical meal lists.
- `贡献`: cooking and ordering contributions.
- `我的`: profile, account settings, and administrator tools.

`菜品` is removed from the bottom navigation. The existing dish-library route remains available but is entered from `我的 > 菜品管理`, which is visible only to administrators. Direct access to dish creation and editing continues to require administrator authorization.

Meal ordering is not a global navigation destination. It exists only inside a meal-detail page.

## Visual Direction

The visual language is a modern Chinese private dining room: quiet, precise, food-led, and warm without becoming rustic or decorative. One element carries the visual emphasis: dish photography. Surrounding navigation, controls, and typography remain restrained.

The design must avoid oversized soft cards, excessive pill shapes, ornamental gradients, decorative labels, price-like metadata, and generic SaaS dashboard composition.

### Color Tokens

- `--color-canvas: #F6F6F1`: warm-neutral page background.
- `--color-surface: #FFFFFF`: inputs, sheets, and elevated controls.
- `--color-ink: #19221C`: primary text.
- `--color-forest: #234C35`: primary action and active navigation.
- `--color-forest-strong: #173E2A`: pressed and high-contrast states.
- `--color-moss: #6F8074`: secondary text and inactive icons.
- `--color-line: #DCE0DA`: dividers and quiet borders.
- `--color-ivory: #F0EAD9`: selected dish control and subtle warm emphasis.
- `--color-danger: #B54747`: destructive actions only.
- `--color-warning: #A66B26`: cooking and attention states only.

Black gradients are reserved for text legibility over dish photography. They are not general page decoration.

### Typography

Use the platform Chinese system stack so H5 and Mini Program render consistently:

`-apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif`

The type scale uses stable sizes rather than viewport scaling:

- Display/page title: `48rpx`, weight `650`, line-height `1.2`.
- Primary heading: `40rpx`, weight `650`, line-height `1.25`.
- Section heading: `32rpx`, weight `620`, line-height `1.3`.
- Body: `28rpx`, weight `400`, line-height `1.6`.
- Supporting text: `24rpx`, weight `400`, line-height `1.5`.
- Metadata: `22rpx`, weight `400`, line-height `1.45`.
- Button text: `27rpx`, weight `600`, line-height `1`.

Letter spacing remains `0`. Text labels use sentence case and plain Chinese. Body copy should stay below roughly 80 characters per line on wide H5 layouts.

### Spacing and Shape

Use an `8rpx` base rhythm, with named steps at `8`, `12`, `16`, `24`, `32`, `48`, and `64rpx`.

- Mobile page gutters: `32rpx`.
- Compact control gaps: `12–16rpx`.
- Related content gaps: `24rpx`.
- Section gaps: `48–64rpx`.
- Minimum touch target: `80rpx` square.
- Standard controls: `8–12rpx` radius.
- Panels and sheets: `16–20rpx` radius.
- Circular controls and avatars remain circular.

Large `30–54rpx` radii are removed from general cards, inputs, navigation, and buttons. Shadows are limited to overlays and image-card separation; content structure should primarily use spacing and dividers.

## Responsive Layout

The application remains mobile-first for WeChat Mini Program, with deliberate H5 behavior rather than a simply enlarged phone column.

- Below `700px`: one content column, `32rpx` gutters, fixed safe-area bottom navigation.
- From `700px` to `1023px`: content width up to `760px`, larger horizontal breathing room, modal sheets centered.
- At `1024px` and above: shell width up to `1040px`; dish grids and administration settings use multiple columns, while reading and form content remains between `640px` and `760px`.
- Dish grids use two columns on mobile, three columns when their container is at least `700px`, and never stretch cards beyond a useful food-photo size.
- Fixed navigation, sheets, and action bars must account for `env(safe-area-inset-bottom)`.

No breakpoint may hide required actions, overlap text, or leave fixed navigation covering page content.

## Shared Application Shell

### Page Structure

All pages use the same shell tokens for safe-area top padding, horizontal gutters, maximum width, bottom-navigation clearance, and section rhythm. `PageHeader` owns consistent title, subtitle, back action, and optional trailing command alignment.

### Bottom Navigation

`AppTabBar` renders four evenly spaced destinations. It uses a quiet full-width bottom surface rather than a floating oversized capsule. Active state is communicated by forest-colored icon and label with a restrained indicator; it must not resize or shift the layout.

Navigation icons come from the existing icon component. Labels remain visible because this is a small family application with four stable destinations.

### Controls

- Primary buttons use forest fill and compact radius.
- Secondary buttons use a surface background and line border.
- Destructive commands use danger text and require confirmation where data or meal state is affected.
- Segmented controls are used for mutually exclusive views or meal types.
- Chips are used only for filters and tags, not general commands.
- Icon buttons use familiar symbols and accessible labels.
- All interactive states include pressed, disabled, pending, keyboard-focus, and reduced-motion behavior.

## Page Designs

### Setup and Login

Setup and login keep their existing behavior but adopt the shared type scale, field spacing, and compact radii. The brand and family name are the first viewport signal. Member selection remains easy to scan; PIN controls keep stable dimensions and clear error recovery.

### Home

Home opens with the family name and a concise greeting. Its primary command is `创建饭局`. The remaining first viewport shows upcoming meals with date, time, status, participant count, and cook when available.

Home does not expose the full dish library or global ordering controls. Selecting a meal opens that meal's detail page.

### Meal List

Active and historical meals are separated by clear headings and spacing, not nested cards. Meal rows use a compact date block, title, time, participant count, cook, and status. Empty, loading, recoverable failure, and retained-data refresh states remain explicit.

### Meal Detail Header and Cook Module

The meal header shows title, date, dining time, ordering deadline, and current meal status. It does not display a process stepper.

The cook module is a compact independent region below the meal information:

- No cook: show `还没有人认领` and `我来掌勺` when allowed.
- Current user is cook: show their identity and an overflow action to leave the role.
- Another cook exists: show their avatar and name; show `我来接手` only when the existing permission model allows it.

Cook actions do not change the availability of member ordering. Meal-state actions such as `截止并开做`, `完成饭局`, and `取消饭局` remain permission-gated and visually separate from dish selection.

### Meal Detail Views

Meal detail contains two views:

- `点菜`: available while ordering is open.
- `已点菜品`: always available, shows a directional empty state before the first selection, and remains available after ordering closes.

The tab badge for `点菜` is the current user's selected count. The badge for `已点菜品` is the number of distinct selected dishes.

When ordering closes, hide the `点菜` tab and show only `已点菜品`. While ordering is open, the cook initially sees `已点菜品`; other members initially see `点菜`. This is only a default view choice and does not couple cook assignment to ordering permissions.

### Dish Filters

The ordering view provides:

- Search across dish name, description, and tags.
- Single-select cuisine filter with `全部` as the default.
- Multi-select tag filters.
- A synthetic `只看我点的` filter with the current selected count.
- `清除筛选` when any non-default filter is active.
- A visible result count.

Tag options are computed from dishes in the selected cuisine. If a cuisine change makes a selected tag invalid, remove that tag automatically. Multiple tags use OR semantics, matching the reference implementation. Search combines with cuisine and tag filters using AND semantics.

Filter changes reset incremental pagination and return the result list to its start. Render dishes in batches of 18 and load the next batch as the sentinel approaches the viewport. H5 shows a return-to-top control after the document has scrolled more than `400px`; Mini Program uses its native page-to-top behavior.

### Dish Cards

Dish cards are the main visual signature:

- Aspect ratio approximately `4:5`.
- The image fills the entire card using `aspectFill`/cover.
- Radius is `8–10px` equivalent, not a large soft radius.
- A black gradient begins near the lower 70% and reaches roughly 90% opacity at the bottom.
- White text inside the gradient contains the dish name, at most two or three flavor tags, and optional interest count.
- The upper-right circular icon toggles selection. Unselected uses translucent dark glass with a white icon; selected uses an ivory surface with a forest check.
- No price, cart, checkout, quantity stepper, or purchase terminology appears.

Tapping the image body opens dish details with a larger image, cuisine, all tags, description, ingredients, preparation steps, source link when present, and a contextual select/cancel action. Tapping the selection control does not open the detail sheet.

When an image is absent, preserve card dimensions and use a quiet cuisine-based placeholder with an existing icon. Do not fabricate food photography.

Selection updates optimistically, prevents duplicate requests, rolls back on failure, and shows one actionable error.

### Ordered Dishes

`已点菜品` groups orders by dish and sorts by descending member count. Each row shows dish thumbnail, dish name, member names or avatars, and total count.

Ordinary members see a read-only summary. The current cook may mark a dish `不做` and later `恢复`. Skipped dishes remain visible with reduced emphasis and a clear status; they are excluded from the ingredient list.

### Ingredient List

The assigned cook can open `食材清单` from `已点菜品`. This feature is a preparation aid, not a purchasing flow.

The backend returns ingredients from distinct, non-skipped selected dishes. Items are grouped by normalized ingredient name and unit. Numeric quantities with matching units are summed; nonnumeric or incompatible quantities remain readable fragments. The sheet supports copying a plain-text or Markdown list and falls back to a selectable text area when clipboard access is unavailable.

The endpoint is available only to the assigned cook:

`GET /api/meals/{meal_id}/ingredient-list`

The response shape is:

```json
{
  "meal_id": "string",
  "items": [
    {
      "name": "string",
      "unit": "string",
      "total": 2,
      "fragments": []
    }
  ]
}
```

`total` is numeric when quantities can be summed; otherwise it is `null` and `fragments` contains the original nonempty quantities.

### Reviews

Reviews appear only for completed meals, below the meal summary. Show average rating when reviews exist, the current member's editable rating/comment, and other members' reviews. Save actions retain pending, success, and failure feedback without moving surrounding content.

### Contribution Wall

Contribution cards use quieter surfaces, aligned statistics, and stable heatmap dimensions. The heatmap remains horizontally contained on narrow screens and includes non-color cues or labels for the two activity types.

### My and Administrator Tools

`我的` contains the profile summary followed by grouped menu sections.

Administrators see:

- `菜品管理`: opens the existing dish-library page.
- `家庭管理`: opens member and automatic-meal settings.

Non-administrators do not see either administrator-only entry unless existing permissions explicitly allow part of family management. Account actions include profile, PIN, server settings, and logout.

### Dish Management

The dish library reuses the full-image card language for browsing, but it does not place edit, archive, or destructive controls on top of the photograph. Tapping a card opens detail or an administrator action sheet. Search, cuisine, and tag filters use the same semantics as meal ordering where relevant.

Dish create/edit keeps image, name, cuisine, tags, description, ingredients, steps, and source URL. Long dynamic forms use section headings, compact remove icons, stable input widths, and a persistent but non-obstructive save action on mobile.

### Family Administration

Family settings, schedules, and members use full-width sections rather than stacked decorative cards. Destructive member actions remain confirmed. Schedule controls retain existing backend limits and validation.

## Data and State Boundaries

Existing meal, order, skip, dish, cuisine, and review endpoints remain authoritative. Frontend filtering operates on the loaded active-dish list and current user's selected IDs. Aggregated order display operates on meal detail orders.

Add only the ingredient-list endpoint described above. Do not add a global state-management dependency. Page-local state remains sufficient for filters, selected IDs, pending operations, sheets, and tab choice.

Add a `build:mp-weixin` script to `frontend/package.json` using `uni build -p mp-weixin` so the required target has a stable verification command.

Shared pure helpers should own:

- Cuisine, tag, selected-only, and search filtering.
- Available tag derivation.
- Ordered-dish grouping and sorting.
- Ingredient display formatting.
- Navigation and permission-derived display state.

## Loading, Empty, and Error States

- Initial loading uses stable-height content placeholders or a restrained state region; it does not resize the page shell.
- Empty ordering explains that an administrator must add dishes and links administrators to dish management.
- Empty filtered results offer `清除筛选`.
- Empty ordered dishes explain that no one has selected a dish yet.
- Refresh failures retain usable content when possible and present a compact retry action.
- Mutation failures roll back optimistic state and present one specific message.
- Expired authentication continues to use the shared API-client redirect behavior.

## Accessibility and Interaction Quality

- Text and controls meet WCAG AA contrast against their actual backgrounds.
- Gradient overlays must keep dish-card text readable over both light and dark photographs.
- All icon-only buttons include accessible names.
- Focus indicators are visible on H5.
- Tap targets are at least `80rpx` square.
- Selected filters, active tabs, and skipped dishes are not communicated by color alone.
- Motion is limited to direct interaction feedback and respects reduced-motion preferences.

## Verification

Automated frontend tests cover filtering combinations, available-tag derivation, selected-only behavior, pagination reset, ordered-dish grouping, permission-derived visibility, and rollback after failed selection.

Backend tests cover ingredient-list authorization, exclusion of skipped dishes, deduplication of dish ingredients across multiple selectors, numeric aggregation, incompatible-unit handling, missing meals, and empty lists.

Required verification commands:

```powershell
cd frontend
npm test
npm run build:h5
npm run build:mp-weixin

cd ..\backend
.venv\Scripts\python -m pytest
```

Browser verification covers home, meal list, meal detail ordering, filters, selected dishes, cook-only tools, reviews, contribution wall, profile, dish management, and administration at approximately `390x844`, `768x1024`, and `1440x900` viewports. Screenshots must show no overlap, clipped labels, fixed-navigation obstruction, blank image regions, or layout shifts during selection.

## Completion Criteria

- The application uses the four-item navigation and administrator-only dish-management entry.
- Every page follows the shared typography, spacing, radius, and responsive shell.
- Cook assignment and ordering remain independent.
- Dish cards use full-image photography with bottom black gradient text treatment.
- Cuisine, tag, search, selected-only, ordered-dish summary, skip/restore, ingredient list, and review workflows are complete.
- No pricing, cart, checkout, payment, or commerce language appears.
- H5 and Mini Program builds pass, automated tests pass, and mobile/tablet/desktop visual verification is complete.
