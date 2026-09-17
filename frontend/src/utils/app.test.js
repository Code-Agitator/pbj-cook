import { describe, expect, it } from 'vitest'
import {
  bootstrapRedirectRoute,
  createdMealId,
  cuisineIdFromPicker,
  dishActions,
  heatmapDateKey,
  localDateKey,
  mealCardData,
  mealInteractionState,
  normalizeApiBase,
  normalizeDishDraft,
  normalizeDishSourceUrl,
  sortMealsByDiningTime,
  validateMealDraft,
  validatePin,
  validateProfileName,
  validateScheduleDraft,
} from './app'

describe('bootstrapRedirectRoute', () => {
  it('keeps the completed-setup route public without a session', () => {
    expect(bootstrapRedirectRoute({
      setupNeeded: false,
      authenticated: false,
      route: 'pages/setup/index',
    })).toBe('')
  })

  it('only redirects protected unauthenticated routes to login', () => {
    expect(bootstrapRedirectRoute({ setupNeeded: false, authenticated: false, route: 'pages/home/index' })).toBe('/pages/login/index')
    expect(bootstrapRedirectRoute({ setupNeeded: false, authenticated: false, route: 'pages/login/index' })).toBe('')
    expect(bootstrapRedirectRoute({ setupNeeded: false, authenticated: true, route: 'pages/home/index' })).toBe('')
  })
})

describe('localDateKey', () => {
  it('formats dates using their local calendar values', () => {
    expect(localDateKey(new Date(2026, 8, 15, 23, 30))).toBe('2026-09-15')
  })

  it('uses the current local date when no value is provided', () => {
    expect(localDateKey()).toMatch(/^\d{4}-\d{2}-\d{2}$/)
  })

  it('rejects invalid dates', () => {
    expect(() => localDateKey(new Date('invalid'))).toThrow('Invalid date')
  })
})

describe('validateMealDraft', () => {
  it('requires valid date and time fields', () => {
    expect(validateMealDraft({ date: '', dining_time: '18:30', deadline: '17:30' })).toBe('请填写完整的日期和时间')
    expect(validateMealDraft({ date: '2026-02-30', dining_time: '18:30', deadline: '17:30' })).toBe('请填写完整的日期和时间')
    expect(validateMealDraft({ date: '2026-09-15', dining_time: '18:3', deadline: '17:30' })).toBe('请填写完整的日期和时间')
    expect(validateMealDraft({ date: '2026-09-15', dining_time: '24:00', deadline: '17:30' })).toBe('请填写完整的日期和时间')
  })

  it('requires the deadline to be before dining', () => {
    expect(validateMealDraft({ date: '2026-09-15', dining_time: '18:30', deadline: '18:30' })).toBe('点菜截止时间必须早于用餐时间')
    expect(validateMealDraft({ date: '2026-09-15', dining_time: '18:30', deadline: '19:00' })).toBe('点菜截止时间必须早于用餐时间')
  })

  it('accepts a complete draft with an earlier deadline', () => {
    expect(validateMealDraft({ date: '2026-09-15', dining_time: '18:30', deadline: '17:45' })).toBe('')
  })
})

describe('createdMealId', () => {
  it('rejects malformed creation responses before callers can report success', () => {
    expect(() => createdMealId()).toThrow('饭局创建失败，请重试')
    expect(() => createdMealId({ id: '' })).toThrow('饭局创建失败，请重试')
    expect(() => createdMealId({ id: 42 })).toThrow('饭局创建失败，请重试')
  })

  it('returns the created meal ID for a valid response', () => {
    expect(createdMealId({ id: 'meal-123' })).toBe('meal-123')
  })
})

describe('meal display and flow helpers', () => {
  it('sorts a copy by numeric dining timestamps and places invalid times last', () => {
    const meals = [{ id: 'late', dining_time: '20' }, { id: 'bad', dining_time: 'nope' }, { id: 'early', dining_time: 10 }]
    expect(sortMealsByDiningTime(meals).map((meal) => meal.id)).toEqual(['early', 'late', 'bad'])
    expect(meals.map((meal) => meal.id)).toEqual(['late', 'bad', 'early'])
  })

  it('formats partial meal cards without invalid dates or undefined labels', () => {
    const data = mealCardData({ meal_type: 'surprise', status: 'mystery', dining_time: 'bad', participant_count: null }, new Date(2026, 8, 15))
    expect(data).toMatchObject({ emoji: '🍽️', title: '饭局', status: '状态未知', dateLabel: '日期待定', timeLabel: '时间待定', participantCount: 0 })
    expect(mealCardData({ date: '2026-09-15', dining_time: 0 }, new Date(2026, 8, 15)).dateLabel).toBe('今天')
  })

  it('derives only legal interactions from meal state and user permissions', () => {
    expect(mealInteractionState({ status: 'ordering', order_deadline: 200, cook_id: 'u1' }, { id: 'u1' }, 100)).toMatchObject({ isCook: true, canCook: true, canOrder: true, canSkip: true, canReview: false })
    expect(mealInteractionState({ status: 'done', order_deadline: 200, cook_id: 'u1' }, { id: 'u1' }, 100)).toMatchObject({ canCook: false, canOrder: false, canSkip: false, canReview: true })
    expect(mealInteractionState({ status: 'ordering', order_deadline: '' }, { id: 'u2' }, 100).canOrder).toBe(false)
  })
})

describe('cuisineIdFromPicker', () => {
  const cuisines = [{ id: 'home' }, { id: 'sichuan' }]

  it('maps the synthetic option and cuisine options', () => {
    expect(cuisineIdFromPicker(cuisines, 0)).toBeNull()
    expect(cuisineIdFromPicker(cuisines, 2)).toBe('sichuan')
  })

  it('rejects malformed picker inputs', () => {
    expect(cuisineIdFromPicker(cuisines, -1)).toBeNull()
    expect(cuisineIdFromPicker(cuisines, 1.5)).toBeNull()
    expect(cuisineIdFromPicker(cuisines, '1')).toBeNull()
    expect(cuisineIdFromPicker([{ id: 7 }], 1)).toBeNull()
    expect(cuisineIdFromPicker(null, 1)).toBeNull()
  })
})

describe('dishActions', () => {
  it('limits unrelated users to viewing details', () => {
    expect(dishActions({ created_by: 'u1' }, { id: 'u2', is_admin: false })).toEqual([
      { key: 'view', label: '查看详情' },
    ])
  })

  it('includes edit and archive actions for the creator and an admin', () => {
    const privilegedActions = [
      { key: 'view', label: '查看详情' },
      { key: 'edit', label: '编辑菜品' },
      { key: 'archive', label: '归档菜品' },
    ]

    expect(dishActions({ created_by: 'u1' }, { id: 'u1', is_admin: false })).toEqual(privilegedActions)
    expect(dishActions({ created_by: 'u1' }, { id: 'admin', is_admin: true })).toEqual(privilegedActions)
  })
})

describe('dish draft helpers', () => {
  it('accepts only trimmed HTTP(S) recipe links without using URL', () => {
    const originalUrl = globalThis.URL
    globalThis.URL = undefined

    try {
      expect(normalizeDishSourceUrl(' https://recipes.example.com/noodles?video=1#method ')).toBe('https://recipes.example.com/noodles?video=1#method')
    } finally {
      globalThis.URL = originalUrl
    }

    expect(normalizeDishSourceUrl('')).toBe('')
    expect(normalizeDishSourceUrl('ftp://recipes.example.com/noodles')).toBeNull()
    expect(normalizeDishSourceUrl('https://user:pass@recipes.example.com')).toBeNull()
    expect(normalizeDishSourceUrl('https://recipes.example.com/noodles with spaces')).toBeNull()
  })

  it('creates a backend-safe payload without UI row keys or empty children', () => {
    const draft = normalizeDishDraft({
      name: '  番茄炒蛋  ', description: '  家常菜  ', image_path: '/uploads/dish.jpg',
      tags: ' 快手， 下饭, , 快手 ', cuisine_id: 'home', source_url: ' https://recipes.example.com/tomato ',
      ingredients: [
        { key: 'ingredient-1', name: ' 鸡蛋 ', quantity: ' 2 ', unit: ' 个 ' },
        { key: 'ingredient-2', name: ' ', quantity: ' 3 ', unit: ' 个 ' },
      ],
      steps: [{ key: 'step-1', body: ' 打散鸡蛋 ' }, { key: 'step-2', body: ' ' }],
    })

    expect(draft).toEqual({
      name: '番茄炒蛋', description: '家常菜', image_path: '/uploads/dish.jpg',
      tags: ['快手', '下饭', '快手'], cuisine_id: 'home', source_url: 'https://recipes.example.com/tomato',
      ingredients: [{ name: '鸡蛋', quantity: '2', unit: '个' }], steps: ['打散鸡蛋'],
    })
  })

  it('caps child arrays before sending the payload', () => {
    const draft = normalizeDishDraft({
      ingredients: Array.from({ length: 31 }, (_, index) => ({ name: `食材${index}` })),
      steps: Array.from({ length: 21 }, (_, index) => ({ body: `步骤${index}` })),
    })

    expect(draft.ingredients).toHaveLength(30)
    expect(draft.steps).toHaveLength(20)
  })
})

describe('heatmapDateKey', () => {
  it('advances dates in local calendar space', () => {
    expect(heatmapDateKey('2026-09-15', 1)).toBe('2026-09-16')
    expect(heatmapDateKey('2026-12-31', 1)).toBe('2027-01-01')
  })

  it('rejects invalid dates and offsets', () => {
    expect(() => heatmapDateKey('2026-02-30', 1)).toThrow('Invalid date')
    expect(() => heatmapDateKey('2026-09-15', 1.5)).toThrow('Invalid offset')
  })
})

describe('profile, PIN, and schedule validation', () => {
  it('requires a trimmed profile name and an exact six-digit PIN', () => {
    expect(validateProfileName('  ')).toBe('请输入昵称')
    expect(validateProfileName(' 小满 ')).toBe('')
    expect(validatePin('123456')).toBe('')
    expect(validatePin('12345')).toBe('密码必须为 6 位数字')
    expect(validatePin('12345a')).toBe('密码必须为 6 位数字')
  })

  it('validates all schedule draft constraints', () => {
    const valid = {
      name: ' 工作日午餐 ', meal_type: 'lunch', dining_time: '12:30', weekdays: [1, 2],
      create_lead_hours: 24, deadline_lead_minutes: 90,
    }

    expect(validateScheduleDraft(valid)).toBe('')
    expect(validateScheduleDraft({ ...valid, weekdays: [] })).toBe('请至少选择一个星期')
    expect(validateScheduleDraft({ ...valid, meal_type: 'snack' })).toBe('请选择有效的餐次')
    expect(validateScheduleDraft({ ...valid, dining_time: '24:00' })).toBe('请选择有效的用餐时间')
    expect(validateScheduleDraft({ ...valid, create_lead_hours: 72.5 })).toBe('提前创建需为 0 到 72 的整数小时')
    expect(validateScheduleDraft({ ...valid, deadline_lead_minutes: 1441 })).toBe('提前截止需为 0 到 1440 的整数分钟')
  })
})

describe('normalizeApiBase', () => {
  it('normalizes a valid HTTP API base', () => {
    expect(normalizeApiBase('  http://192.168.1.8:8000/ ')).toBe('http://192.168.1.8:8000')
    expect(normalizeApiBase('https://example.com/api///')).toBe('https://example.com/api')
  })

  it('does not depend on the URL global available in browser runtimes', () => {
    const originalUrl = globalThis.URL
    globalThis.URL = undefined

    try {
      expect(normalizeApiBase('https://example.com/api///')).toBe('https://example.com/api')
    } finally {
      globalThis.URL = originalUrl
    }
  })

  it('rejects unsupported or unsafe API base values', () => {
    expect(normalizeApiBase('ftp://bad')).toBe('')
    expect(normalizeApiBase('https://')).toBe('')
    expect(normalizeApiBase('https://user:pass@example.com')).toBe('')
    expect(normalizeApiBase('https://example.com/api?debug=1')).toBe('')
    expect(normalizeApiBase('https://example.com/api#section')).toBe('')
    expect(normalizeApiBase('not a url')).toBe('')
  })
})
