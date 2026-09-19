const dishTags = (dish) => Array.isArray(dish?.tags) ? dish.tags.filter(Boolean) : []

export function availableDishTags(dishes, cuisineId) {
  const counts = new Map()
  for (const dish of Array.isArray(dishes) ? dishes : []) {
    if (cuisineId && dish?.cuisine_id !== cuisineId) continue
    for (const tag of dishTags(dish)) counts.set(tag, (counts.get(tag) || 0) + 1)
  }
  return [...counts].sort((left, right) => right[1] - left[1]).map(([tag]) => tag)
}

export function sanitizeMealTags(tags, availableTags) {
  const valid = new Set(Array.isArray(availableTags) ? availableTags : [])
  return new Set([...(tags instanceof Set ? tags : [])].filter(tag => tag === '__mine__' || valid.has(tag)))
}

export function filterMealDishes({ dishes, cuisineId, tags, query, selectedIds }) {
  const activeTags = tags instanceof Set ? tags : new Set()
  const selected = selectedIds instanceof Set ? selectedIds : new Set()
  const needle = String(query || '').trim().toLocaleLowerCase()

  return (Array.isArray(dishes) ? dishes : []).filter((dish) => {
    if (!dish || (cuisineId && dish.cuisine_id !== cuisineId)) return false
    if (activeTags.size) {
      const mine = activeTags.has('__mine__') && selected.has(dish.id)
      const tagMatch = [...activeTags].some(tag => tag !== '__mine__' && dishTags(dish).includes(tag))
      if (!mine && !tagMatch) return false
    }
    if (!needle) return true
    return `${dish.name || ''} ${dish.description || ''} ${dishTags(dish).join(' ')}`.toLocaleLowerCase().includes(needle)
  })
}

export function groupMealOrders(orders) {
  const grouped = new Map()
  for (const order of Array.isArray(orders) ? orders : []) {
    if (!order?.dish_id) continue
    if (!grouped.has(order.dish_id)) {
      grouped.set(order.dish_id, {
        dishId: order.dish_id,
        name: order.dish_name || '未命名菜品',
        image: order.dish_image || null,
        people: []
      })
    }
    grouped.get(order.dish_id).people.push({
      id: order.user_id,
      name: order.user_name || '成员',
      avatar: order.user_avatar || null
    })
  }
  return [...grouped.values()].sort((left, right) => (
    right.people.length - left.people.length || left.name.localeCompare(right.name, 'zh-CN')
  ))
}

export function mealDetailInitialTab({ canOrder, isCook }) {
  return canOrder && !isCook ? 'pick' : 'ordered'
}
