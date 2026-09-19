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
