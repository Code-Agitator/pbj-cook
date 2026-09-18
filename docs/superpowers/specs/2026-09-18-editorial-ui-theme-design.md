# DaCook Editorial UI and Theme Architecture Design

## Goal

Refactor DaCook's presentation layer around the supplied restaurant-ordering reference: a prominent editorial greeting, generous whitespace, strongly ordered typography, focused meal cards, and a stable bottom navigation. Preserve the current green, ivory, white, and warm-neutral palette while making every color role centrally replaceable for a future theme.

This is a visual and CSS architecture change. Existing routes, permissions, APIs, meal state transitions, and ordering behavior remain unchanged.

## Product Constraints

- The bottom navigation remains exactly `首页 / 饭局 / 贡献 / 我的`.
- A meal exists before ordering; all members may order within that meal.
- Cook claiming and dish ordering remain fully independent.
- Dish management remains an administrator entry under `我的`.
- Meal detail does not show a process stepper.
- Dish cards retain real images with a bottom black gradient and overlaid text.
- The interface contains no prices, cart, checkout, payment, or transaction language.
- All Vue components continue to use Vue 3 Composition API with `<script setup lang="js">`; do not introduce `export default`.
- H5 and WeChat Mini Program compatibility must be preserved.

## Visual Direction

The visual language is "quiet private dining": hospitable rather than commercial, editorial rather than dashboard-like, and precise rather than decorative. The supplied reference informs hierarchy and spatial rhythm, not its gold palette or five-item information architecture.

The memorable visual element is the opening composition: a calm tinted greeting band followed by the nearest meal as a single, substantial row. Elsewhere, food photography carries emphasis while controls, lists, forms, and administration remain disciplined.

Avoid nested cards, repeated decorative pills, floating page sections, oversized shadows, ornamental labels, and gradients outside image-legibility overlays. Page sections are separated primarily by whitespace and hairline dividers.

## Theme Architecture

Color definitions live in `frontend/src/styles.css` in three layers.

### Primitive Palette

Primitive tokens contain the existing literal colors and are the only general-purpose theme declarations allowed to contain palette hex values:

```css
:root,
page {
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
}
```

Additional existing neutral shades may be named when migration reveals a distinct role. They must not change the perceived palette.

### Semantic Theme Tokens

Components consume semantic roles rather than primitives:

- Surfaces: `--theme-bg-page`, `--theme-bg-surface`, `--theme-bg-subtle`, `--theme-bg-elevated`.
- Text: `--theme-text-primary`, `--theme-text-secondary`, `--theme-text-inverse`, `--theme-text-action`.
- Actions: `--theme-action-primary`, `--theme-action-primary-strong`, `--theme-action-on-primary`.
- Structure: `--theme-border-subtle`, `--theme-border-strong`, `--theme-focus-ring`.
- States: `--theme-danger`, `--theme-danger-subtle`, `--theme-warning`, `--theme-success-subtle`.
- Media: `--theme-image-overlay`, `--theme-image-text`, `--theme-image-text-muted`, `--theme-image-control`.
- Chrome: `--theme-nav-bg`, `--theme-modal-scrim`, `--theme-shadow-soft`.

The default mapping lives under `:root, page, [data-theme="default"]`. A runtime theme picker is out of scope; the structure only prepares for adding another mapping later.

### Component Tokens

Component-specific tokens are introduced only when a component needs a stable contract that combines semantic roles, such as `--meal-card-bg` or `--tabbar-active-color`. Component tokens must resolve to semantic tokens and must not contain raw colors.

Legacy aliases such as `--color-forest`, `--green`, and `--surface` are removed after all consumers migrate. Raw colors remain permitted only for deliberately fixed photographic overlays when expressed through the media semantic tokens, and for platform APIs that require a literal color value, such as a native Mini Program switch. Those exceptions are documented beside the usage.

## Typography

Use a Chinese-first system stack for consistent H5 and Mini Program rendering:

```css
"Songti SC", "STSong", "Noto Serif CJK SC", serif
```

is used only for the editorial greeting and other display text when the platform supplies it. Interface headings, body copy, metadata, controls, and dense administration content use:

```css
-apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC",
"Hiragino Sans GB", "Microsoft YaHei", sans-serif
```

The stable type scale is:

- Greeting display: `52rpx`, weight `700`, line-height `1.2`.
- Page title: `42rpx`, weight `650`, line-height `1.25`.
- Section title: `32rpx`, weight `600`, line-height `1.35`.
- Card title: `30rpx`, weight `620`, line-height `1.3`.
- Body: `27rpx`, weight `400`, line-height `1.65`.
- Supporting text: `24rpx`, line-height `1.55`.
- Metadata and navigation label: `21-22rpx`, line-height `1.4`.

Letter spacing remains `0`. Text does not scale with viewport width. Long titles truncate only where the row has a fixed action area; descriptive text wraps naturally.

## Spacing and Shape

Retain the existing `8rpx` spacing base but expand its semantic use:

- Mobile page gutter: `36rpx`; tablet and desktop gutters: `48rpx`.
- Related inline content: `8-16rpx`.
- Content inside a row: `20-28rpx`.
- Section separation: `48-64rpx`.
- Major editorial separation: `72-88rpx`.
- Minimum interactive target: `80rpx` square.

Controls use `10-12rpx` radii, content panels use `16-20rpx`, meal focus cards use `28-32rpx`, and circular icon controls remain circular. Larger radii are reserved for the focused meal card and active bottom-navigation treatment; they are not repeated across every section.

## Shared Shell and Components

### Page Shell

The shared `.page` shell owns safe-area padding, responsive gutters, maximum widths, bottom-navigation clearance, background, and text color. Reading and form pages remain constrained; grid pages can use the existing wider modifier.

### Page Header

`PageHeader` becomes the consistent non-home heading primitive. It supports title, optional subtitle, compact mode, and a trailing command on one stable baseline. Back navigation stays outside or above the heading when required by the native route structure.

### Bottom Navigation

`AppTabBar` remains a fixed, full-width four-item navigation surface. The active item receives a quiet elevated treatment inspired by the reference while all four columns retain identical dimensions, preventing layout shift. Its surface may use translucency and a restrained shadow, both through semantic theme tokens. The navigation never becomes a detached floating capsule.

### Meal Card

`MealCard` becomes a rounded focus row with three stable regions:

1. A compact date/time or meal-type block.
2. Title and participant/cook metadata.
3. Status and chevron.

The full row remains the tap target. Status styling communicates state using text plus tone, not color alone. Cards are substantial on the home page and may use a denser modifier in the full meal list.

### Dish Image Card

`DishImageCard` retains its `4:5` image composition, black bottom overlay, white text, and isolated top-right selection control. Its colors migrate to media semantic tokens. Missing images preserve dimensions and use the subdued theme surface rather than fabricated photography.

### Controls and Forms

Buttons, chips, inputs, sheets, badges, empty states, and feedback messages consume the same semantic tokens and sizing rules. Chips remain filters or selectable tags, not generic actions. Icon-only actions retain accessible names and stable dimensions.

## Page Composition

### Home

Home most closely follows the reference composition:

- A broad, lightly tinted greeting band contains family name, `你好，{成员名}`, and one concise dining prompt.
- The following section puts `临近的饭局` and `开饭局` on one baseline.
- The nearest meal is visually primary; additional upcoming meals follow with consistent spacing rather than becoming nested cards.
- `查看全部饭局` remains a clear text action after the list.
- Creating a meal continues to open the existing sheet and does not change its data flow.

### Meal List and Detail

The meal list uses the shared editorial header and denser meal rows for scanning. Active and historical groups are separated by rhythm and dividers.

Meal detail uses a strong title and restrained metadata band, followed by the independent cook module, meal actions, view tabs, dish grid or ordered-dish list, and reviews. No process steps are introduced. The existing order filters and ordered-dish behavior remain intact.

### Contribution, My, and Administration

Contribution keeps stable heatmaps and aligns names and totals with the new type rhythm. `我的` uses a clear profile lead followed by unframed grouped menu rows. Administrator pages use section bands and dividers rather than decorative card stacks; forms become denser than consumer pages without dropping touch-target requirements.

### Setup, Login, Dish Library, and Dish Form

Setup and login adopt the common spacing, surface, and typography system while preserving authentication behavior. The dish library retains photo-led cards. Dish forms use consistent section headers, field spacing, and action placement without altering fields or permissions.

## Responsive Behavior

- Below `700px`: one column, `36rpx` gutters, safe-area-aware fixed bottom navigation, two-column dish grids.
- From `700px`: content is capped near `760px`; modal sheets center; dish grids use three columns when space permits.
- From `1024px`: explicitly wide pages may reach `1040px`; forms and reading content remain narrower.
- Home's greeting band and meal cards grow in padding, not font size, on wider screens.
- Fixed navigation and sheets never cover interactive content.

## Interaction and State Handling

No API or state-model changes are required. Loading, empty, retry, pending, disabled, error, and retained-data states preserve their current behavior but use shared visual primitives. Theme refactoring must not change click targets, route destinations, permissions, or optimistic update semantics.

Keyboard focus is visible on H5. Selected tabs, filters, navigation items, and skipped dishes use at least one non-color cue. Motion is limited to direct interaction feedback and respects `prefers-reduced-motion`.

## Implementation Boundaries

Primary implementation areas are:

- `frontend/src/styles.css`: palette, semantic theme, typography, spacing, shared primitives, responsive shell.
- `frontend/src/App.vue`: remove duplicate raw global color declarations and rely on the theme.
- Shared components: `AppTabBar`, `PageHeader`, `MealCard`, `DishImageCard`, `Avatar`, and `PinPad`.
- Registered pages under `frontend/src/pages`: migrate raw colors and align page composition without changing behavior.

No backend code, database schema, endpoints, route definitions, or package upgrades are part of this refactor.

## Verification

Automated checks:

```powershell
cd frontend
npm test
npm run build:h5
```

Static checks confirm every Vue component still uses `<script setup lang="js">`, no Vue file contains `export default`, and raw color literals outside the centralized theme and documented native-platform exceptions are removed.

Visual browser checks use the existing user-run server at `http://localhost:5173` and cover approximately `390x844`, `768x1024`, and `1440x900`. Verify home, meal list, meal detail, contribution, profile, dish management, administration, login, and setup. Screenshots must show readable text, consistent gutters, stable navigation, no overlap, no clipped labels, no blank image regions, and no bottom-bar obstruction.

The existing Mini Program dependency mismatch is not resolved by this work. The theme implementation must avoid introducing additional Mini Program incompatibilities, and the known build blocker must be reported separately if it remains.

## Completion Criteria

- The interface visibly follows the reference's editorial hierarchy and spatial rhythm while retaining the current palette.
- All color roles are centralized behind primitive, semantic, and narrowly scoped component tokens.
- Shared typography, spacing, controls, meal cards, and navigation are consistent across registered pages.
- The four-item bottom navigation and all existing product behavior remain unchanged.
- Dish imagery retains the required black-gradient text treatment.
- H5 tests and build pass, and all target viewports pass visual inspection.
- No Vue Options API component, commerce language, backend change, or dependency upgrade is introduced.
