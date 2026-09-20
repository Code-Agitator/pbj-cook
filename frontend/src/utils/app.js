function validLocalDate(value) {
  if (typeof value !== 'string' || !/^\d{4}-\d{2}-\d{2}$/.test(value)) return null

  const [year, month, day] = value.split('-').map(Number)
  const date = new Date(year, month - 1, day)
  if (date.getFullYear() !== year || date.getMonth() !== month - 1 || date.getDate() !== day) return null
  return date
}

function validTime(value) {
  if (typeof value !== 'string' || !/^(\d{2}):(\d{2})$/.test(value)) return null

  const [hours, minutes] = value.split(':').map(Number)
  if (hours > 23 || minutes > 59) return null
  return hours * 60 + minutes
}

function localDateParts(date) {
  if (!(date instanceof Date) || Number.isNaN(date.getTime())) throw new TypeError('Invalid date')

  return [date.getFullYear(), date.getMonth() + 1, date.getDate()]
}

function formatDateParts(year, month, day) {
  return `${String(year).padStart(4, '0')}-${String(month).padStart(2, '0')}-${String(day).padStart(2, '0')}`
}

function validHostname(hostname) {
  if (!hostname || hostname.length > 253) return false

  if (/^\d+(\.\d+){3}$/.test(hostname)) {
    return hostname.split('.').every((part) => Number(part) <= 255)
  }

  return hostname.split('.').every((label) => (
    /^[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?$/.test(label)
  ))
}

function validPort(port) {
  return port === undefined || (Number(port) <= 65535 && /^\d{1,5}$/.test(port))
}

export function localDateKey(value = new Date()) {
  return formatDateParts(...localDateParts(value))
}

export function numericTimestamp(value) {
  if (value === null || value === undefined || (typeof value === 'string' && !value.trim())) return null
  const timestamp = Number(value)
  return Number.isFinite(timestamp) ? timestamp : null
}

export function sortMealsByDiningTime(meals) {
  if (!Array.isArray(meals)) return []

  return [...meals].sort((left, right) => {
    const leftTime = numericTimestamp(left?.dining_time)
    const rightTime = numericTimestamp(right?.dining_time)
    return (leftTime ?? Number.POSITIVE_INFINITY) - (rightTime ?? Number.POSITIVE_INFINITY)
  })
}

const mealTypes = { breakfast: '早餐', lunch: '午餐', dinner: '晚餐' }
const mealEmojis = { breakfast: '🥪', lunch: '🍱', dinner: '🍲' }
const mealStatuses = { ordering: '点菜中', cooking: '做饭中', done: '已完成', cancelled: '已取消' }

export function formatMealTime(value) {
  const timestamp = numericTimestamp(value)
  if (timestamp === null) return '时间待定'

  const date = new Date(timestamp * 1000)
  if (Number.isNaN(date.getTime())) return '时间待定'
  const hours = String(date.getUTCHours()).padStart(2, '0')
  const minutes = String(date.getUTCMinutes()).padStart(2, '0')
  return `${hours}:${minutes}`
}

export function mealDateLabel(meal, now = new Date()) {
  const date = typeof meal?.date === 'string' ? validLocalDate(meal.date) : null
  if (date) {
    const key = localDateKey(date)
    return key === localDateKey(now) ? '今天' : `${date.getMonth() + 1}月${date.getDate()}日`
  }

  const timestamp = numericTimestamp(meal?.dining_time)
  if (timestamp === null) return '日期待定'
  const fallback = new Date(timestamp * 1000)
  if (Number.isNaN(fallback.getTime())) return '日期待定'
  const fallbackKey = `${String(fallback.getUTCFullYear()).padStart(4, '0')}-${String(fallback.getUTCMonth() + 1).padStart(2, '0')}-${String(fallback.getUTCDate()).padStart(2, '0')}`
  return fallbackKey === localDateKey(now) ? '今天' : `${fallback.getUTCMonth() + 1}月${fallback.getUTCDate()}日`
}

export function mealCardData(meal, now = new Date()) {
  const type = meal?.meal_type
  const participantCount = Number(meal?.participant_count)

  return {
    emoji: mealEmojis[type] || '🍽️',
    title: typeof meal?.title === 'string' && meal.title.trim() ? meal.title : (mealTypes[type] || '饭局'),
    status: mealStatuses[meal?.status] || '状态未知',
    dateLabel: mealDateLabel(meal, now),
    timeLabel: formatMealTime(meal?.dining_time),
    participantCount: Number.isFinite(participantCount) && participantCount >= 0 ? participantCount : 0,
    cookName: typeof meal?.cook?.name === 'string' && meal.cook.name ? meal.cook.name : '',
  }
}

export function mealInteractionState(meal, user, nowSeconds = Date.now() / 1000) {
  const status = meal?.status
  const actionable = status === 'ordering' || status === 'cooking'
  const isCook = Boolean(user?.id && meal?.cook_id === user.id)
  const canManage = actionable && Boolean(user?.is_admin || user?.id === meal?.created_by || isCook)
  const deadline = numericTimestamp(meal?.order_deadline)

  return {
    isCook,
    canCook: actionable && !meal?.cook_id,
    canOrder: status === 'ordering' && deadline !== null && nowSeconds < deadline,
    canManage,
    canStartCooking: canManage && status === 'ordering',
    canComplete: canManage && status === 'cooking',
    canCancel: canManage && Boolean(user?.is_admin),
    canSkip: isCook && actionable,
    canReview: status === 'done',
  }
}

export function ingredientListText(meal, items) {
  const title = typeof meal?.title === 'string' && meal.title.trim() ? meal.title.trim() : '本次饭局'
  const lines = (Array.isArray(items) ? items : []).map((item) => {
    const name = String(item?.name || '').trim()
    const unit = String(item?.unit || '').trim()
    const quantities = []
    if (Number.isFinite(Number(item?.total)) && item?.total !== null) quantities.push(`${Number(item.total)}${unit}`)
    if (Array.isArray(item?.fragments)) quantities.push(...item.fragments.map(value => String(value).trim()).filter(Boolean))
    return `${name}${quantities.length ? ` ${quantities.join('、')}` : ''}`.trim()
  }).filter(Boolean)
  return [`${title} - 食材清单`, ...lines].join('\n')
}

export function validateMealDraft(draft) {
  const date = validLocalDate(draft?.date)
  const diningTime = validTime(draft?.dining_time)
  const deadline = validTime(draft?.deadline)

  if (!date || diningTime === null || deadline === null) return '请填写完整的日期和时间'
  return deadline >= diningTime ? '点菜截止时间必须早于用餐时间' : ''
}

export function createdMealId(response) {
  if (typeof response?.id !== 'string' || !response.id.trim()) throw new Error('饭局创建失败，请重试')
  return response.id
}

export function cuisineIdFromPicker(cuisines, pickerIndex) {
  if (!Array.isArray(cuisines) || !Number.isInteger(pickerIndex) || pickerIndex < 0) return null
  if (pickerIndex === 0) return null

  const id = cuisines[pickerIndex - 1]?.id
  return typeof id === 'string' && id ? id : null
}

export function dishActions(dish, user) {
  const actions = [{ key: 'view', label: '查看详情' }]
  const isCreator = typeof dish?.created_by === 'string' && dish.created_by === user?.id

  if (isCreator || user?.is_admin === true) {
    actions.push({ key: 'edit', label: '编辑菜品' }, { key: 'archive', label: '归档菜品' })
  }

  return actions
}

export function normalizeDishSourceUrl(value) {
  if (typeof value !== 'string') return null

  const candidate = value.trim()
  if (!candidate) return ''

  const match = candidate.match(/^(https?):\/\/([^\/?#]+)(?:\/[^\s?#]*)?(?:\?[^\s#]*)?(?:#[^\s]*)?$/)
  if (!match) return null

  const authority = match[2]
  if (authority.includes('@')) return null

  const hostMatch = authority.match(/^([^:]+)(?::(\d+))?$/)
  if (!hostMatch) return null

  const [, hostname, port] = hostMatch
  if (!validHostname(hostname) || !validPort(port)) return null
  return candidate
}

export function normalizeDishDraft(draft) {
  const tags = Array.isArray(draft?.tags)
    ? draft.tags
    : (typeof draft?.tags === 'string' ? draft.tags.split(/[,，]/) : [])
  const ingredients = Array.isArray(draft?.ingredients) ? draft.ingredients : []
  const steps = Array.isArray(draft?.steps) ? draft.steps : []

  return {
    name: typeof draft?.name === 'string' ? draft.name.trim() : '',
    description: typeof draft?.description === 'string' ? draft.description.trim() : '',
    image_path: typeof draft?.image_path === 'string' && draft.image_path ? draft.image_path : null,
    tags: tags.map((tag) => String(tag ?? '').trim()).filter(Boolean),
    cuisine_id: typeof draft?.cuisine_id === 'string' && draft.cuisine_id ? draft.cuisine_id : null,
    source_url: normalizeDishSourceUrl(draft?.source_url),
    ingredients: ingredients.slice(0, 30).map((item) => ({
      name: String(item?.name ?? '').trim(),
      quantity: String(item?.quantity ?? '').trim(),
      unit: String(item?.unit ?? '').trim(),
    })).filter((item) => item.name),
    steps: steps.slice(0, 20).map((step) => (
      typeof step === 'object' ? String(step?.body ?? '').trim() : String(step ?? '').trim()
    )).filter(Boolean),
  }
}

export function heatmapDateKey(start, offset) {
  const date = validLocalDate(start)
  if (!date) throw new TypeError('Invalid date')
  if (!Number.isInteger(offset)) throw new TypeError('Invalid offset')

  date.setDate(date.getDate() + offset)
  return localDateKey(date)
}

export function validatePin(value) {
  return typeof value === 'string' && /^\d{6}$/.test(value) ? '' : '密码必须为 6 位数字'
}

export function validateProfileName(value) {
  return typeof value === 'string' && value.trim() ? '' : '请输入昵称'
}

export function validateScheduleDraft(draft) {
  if (typeof draft?.name !== 'string' || !draft.name.trim()) return '请填写规则名称'
  if (!['breakfast', 'lunch', 'dinner'].includes(draft.meal_type)) return '请选择有效的餐次'
  if (validTime(draft.dining_time) === null) return '请选择有效的用餐时间'
  if (!Array.isArray(draft.weekdays) || !draft.weekdays.some((day) => Number.isInteger(day) && day >= 0 && day <= 6)) return '请至少选择一个星期'
  if (!Number.isInteger(draft.create_lead_hours) || draft.create_lead_hours < 0 || draft.create_lead_hours > 72) return '提前创建需为 0 到 72 的整数小时'
  if (!Number.isInteger(draft.deadline_lead_minutes) || draft.deadline_lead_minutes < 0 || draft.deadline_lead_minutes > 1440) return '提前截止需为 0 到 1440 的整数分钟'
  return ''
}

export function normalizeApiBase(value) {
  if (typeof value !== 'string') return ''

  const candidate = value.trim()
  if (!candidate) return ''

  const match = candidate.match(/^(https?):\/\/([^/?#]+)(\/[^?#]*)?$/)
  if (!match) return ''

  const [, , authority] = match
  if (authority.includes('@')) return ''

  const hostMatch = authority.match(/^([^:]+)(?::(\d+))?$/)
  if (!hostMatch) return ''

  const [, hostname, port] = hostMatch
  if (!validHostname(hostname) || !validPort(port)) return ''

  return candidate.replace(/\/+$/, '')
}

export function bootstrapRedirectRoute({ setupNeeded, authenticated, route }) {
  const isSetupRoute = route === 'pages/setup/index'
  const isLoginRoute = route.startsWith('pages/login')

  if (setupNeeded && !isSetupRoute) return '/pages/setup/index'
  if (!setupNeeded && !authenticated && !isSetupRoute && !isLoginRoute) return '/pages/login/index'
  return ''
}
