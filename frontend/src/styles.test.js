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

describe('meal page contracts', () => {
  it('keeps ordering and cook claiming as separate home and detail actions', () => {
    const home = readFileSync(resolve(srcRoot, 'pages/home/index.vue'), 'utf8')
    const detail = readFileSync(resolve(srcRoot, 'pages/meal-detail/index.vue'), 'utf8')
    expect(home).toContain('开饭局')
    expect(detail).toContain('认领主厨')
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
      const withoutNativeSwitchException = source.replace("const NATIVE_SWITCH_COLOR = '#234c35'", '')
      expect(withoutNativeSwitchException, file).not.toMatch(rawColor)
    }
  })
})
