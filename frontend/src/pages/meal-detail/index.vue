<template>
  <view class="page no-tab meal-page">
    <view v-if="invalidRoute" class="state panel">
      <text>饭局参数无效</text>
      <button class="btn tonal" @tap="back">返回饭局</button>
    </view>
    <view v-else-if="loading && !meal" class="state">正在准备饭局...</view>
    <view v-else-if="error && !meal" class="state panel">
      <text>{{ error }}</text>
      <button class="btn tonal" @tap="load">重新加载</button>
      <button class="btn ghost" @tap="back">返回饭局</button>
    </view>

    <template v-else-if="meal">
      <BackButton label="饭局" fallback-url="/pages/meals/index"/>
      <view class="meal-heading">
        <view class="meal-title">
          <text class="title">{{ meal.title || mealTypeLabels[meal.meal_type] || '饭局' }}</text>
          <view class="status-row">
            <view class="more-wrap" v-if="interaction.canManage || interaction.canCook">
              <view class="more-btn" @tap="showMore = !showMore">
                  <Icon icon="More" :size="18"/>
                </view>
              <view class="more-menu" v-if="showMore">
                <view v-if="interaction.isCook" class="more-item" @tap="setStatus('cooking')">结束点菜</view>
                <view v-if="interaction.canComplete" class="more-item" @tap="setStatus('done')">完成饭局</view>
                <view v-if="interaction.canCancel" class="more-item danger" @tap="setStatus('cancelled')">取消饭局</view>
              </view>
            </view>
          </view>
        </view>
        <text class="meal-time">{{ meal.date || '日期待定' }} · {{ formatMealTime(meal.dining_time) }} 开饭
          <StatusBadge :status="meal.status"/>
        </text>
        <text class="deadline">{{ deadlineText }}</text>
      </view>

      <view v-if="error" class="inline-error">
        <text>{{ error }}</text>
        <button @tap="load">重试</button>
      </view>

      <view class="cook-section">
        <view class="cook-members">
          <view v-for="(person, idx) in allMembers" :key="person.id || idx" class="member"
                :class="[memberColorClass(idx), { cook: person.isCook }]">
            <text v-if="person.isCook" class="chef-hat">🧑‍🍳</text>
            <text>{{ person.name || '成员' }}</text>
          </view>
        </view>
        <text class="cook-hint">认领只代表掌勺，不影响任何人点菜</text>
        <view v-if="interaction.canCook && !interaction.isCook" class="btn cook-claim"
              :class="{ disabled: pending('cook') }" @tap="toggleCook">
          {{ pending('cook') ? '更新中...' : '认领主厨' }}
        </view>
        <view v-if="interaction.isCook" class="btn tonal cook-claim"
              :class="{ disabled: pending('cook') }" @tap="toggleCook">
          {{ pending('cook') ? '更新中...' : '退出主厨' }}
        </view>
      </view>

      <view class="view-tabs">
        <view v-if="interaction.canOrder" :class="{ on: tab === 'pick' }" @tap="tab = 'pick'">点菜 {{ selected.size }}
        </view>
        <view :class="{ on: tab === 'ordered' }" @tap="tab = 'ordered'">已点菜品 {{ groups.length }}
        </view>
      </view>

      <view v-if="tab === 'pick' && interaction.canOrder">
        <MealDishFilters :query="query" :cuisines="cuisines" :cuisine-id="cuisineId" :tags="activeTags"
                         :available-tags="availableTags" :selected-count="selected.size"
                         :result-count="filteredDishes.length" @update:query="setQuery" @update:cuisine-id="setCuisine"
                         @toggle-tag="toggleTag" @reset="resetFilters"/>
        <view v-if="!dishes.length" class="state panel">
          <text class="section-title">菜品库还是空的</text>
          <text class="subtle">请联系管理员在"我的 > 菜品管理"中添加菜品。</text>
        </view>
        <view v-else-if="!filteredDishes.length" class="state panel">
          <text class="subtle">没有符合条件的菜品</text>
          <view class="reset-link" @tap="resetFilters">清除筛选</view>
        </view>
        <view v-else class="dish-grid">
          <DishImageCard v-for="dish in visibleDishes" :key="dish.id" :dish="dish" :src="assetUrl(dish.image_path)"
                         :selected="selected.has(dish.id)" :interest-count="interestCount(dish.id)" @open="openDish"
                         @toggle="toggleOrder"/>
        </view>
        <button v-if="visibleDishes.length < filteredDishes.length" class="load-more" @tap="page += 1">继续浏览</button>
      </view>

      <view v-else-if="tab === 'ordered'">
        <view class="ordered-heading">
          <text class="section-title">已点菜品</text>
        </view>
        <view v-if="!groups.length" class="state panel">还没有人点菜</view>
        <view v-else class="order-list">
          <view v-for="group in groups" :key="group.dishId" class="order-row"
                :class="{ skipped: skipped.has(group.dishId) }">
            <view class="order-img-wrap">
              <image v-if="group.image" :src="assetUrl(group.image)" mode="aspectFill"/>
              <view v-else class="order-placeholder">
                <Icon icon="ChefHat" :size="22"/>
              </view>
            </view>
            <view class="order-copy">
              <text class="order-name">{{ group.name }}</text>
              <text class="order-count">{{ group.people.length }} 人想吃</text>
              <view class="order-people">
                <view v-for="(person, pIdx) in group.people" :key="person.id || pIdx" class="person-pill"
                      :class="memberColorClass(getMemberIndex(person))">{{ person.name || '成员' }}
                </view>
              </view>
            </view>
          </view>
        </view>
      </view>

      <view v-if="interaction.canReview" class="reviews-section">
        <view class="reviews-heading">
          <text class="section-title">饭后评价</text>
          <text v-if="meal.reviews?.length" class="subtle">{{ reviewAverage }} 分 · {{ meal.reviews.length }} 人评价
          </text>
        </view>
        <view class="review-editor panel">
          <view class="stars">
            <button v-for="number in 5" :key="number" :class="{ on: rating >= number }" @tap="rating = number">★
            </button>
          </view>
          <textarea v-model="comment" class="input" maxlength="200" placeholder="说说这顿饭的味道"/>
          <button class="btn block" :disabled="pending('review')" @tap="submitReview">
            {{ pending('review') ? '保存中...' : '保存评价' }}
          </button>
        </view>
        <view v-for="review in meal.reviews || []" :key="review.id" class="review-row">
          <view class="review-line">
            <text>{{ review.user_name || '成员' }}</text>
            <text>{{ '★'.repeat(Number(review.rating) || 0) }}</text>
          </view>
          <text v-if="review.comment" class="subtle">{{ review.comment }}</text>
        </view>
      </view>
    </template>

    <view v-if="detailDish" class="modal-mask" @tap.self="detailDish = null">
      <view class="sheet dish-sheet">
        <view class="sheet-head">
          <text class="section-title">{{ detailDish.name || '菜品详情' }}</text>
          <button class="sheet-close" @tap="detailDish = null">
            <Icon icon="X" :size="18"/>
          </button>
        </view>
        <image v-if="detailDish.image_path" class="detail-image" :src="assetUrl(detailDish.image_path)"
               mode="aspectFill"/>
        <view class="detail-meta">
          <text v-if="detailDish.cuisine_name" class="badge">{{ detailDish.cuisine_name }}</text>
          <text v-for="tag in detailDish.tags || []" :key="tag" class="badge neutral">{{ tag }}</text>
        </view>
        <text v-if="detailDish.description" class="detail-description">{{ detailDish.description }}</text>
        <view v-if="detailDish.ingredients?.length" class="detail-section">
          <text class="section-title compact-title">食材</text>
          <text v-for="item in detailDish.ingredients" :key="`${item.name}-${item.unit}`" class="detail-row">
            {{ item.name }} {{ item.quantity || '' }}{{ item.unit || '' }}
          </text>
        </view>
        <view v-if="detailDish.steps?.length" class="detail-section">
          <text class="section-title compact-title">做法</text>
          <view v-for="(step, index) in detailDish.steps" :key="step.id || index" class="step-row">
            <text>{{ index + 1 }}</text>
            <text>{{ step.body }}</text>
          </view>
        </view>
        <button v-if="detailDish.source_url" class="source-link" @tap="copySource(detailDish.source_url)">复制菜谱来源
        </button>
        <button class="btn block sheet-primary" :disabled="pending(`order:${detailDish.id}`)"
                @tap="toggleOrder(detailDish.id)">{{ selected.has(detailDish.id) ? '取消这道菜' : '点这道菜' }}
        </button>
      </view>
    </view>

    <view v-if="ingredientSheet" class="modal-mask" @tap.self="ingredientSheet = false">
      <view class="sheet ingredient-sheet">
        <view class="sheet-head">
          <view>
            <text class="section-title">食材清单</text>
            <text class="subtle">已合并相同食材，不包含标记"不做"的菜品</text>
          </view>
          <button class="sheet-close" @tap="ingredientSheet = false">
            <Icon icon="X" :size="18"/>
          </button>
        </view>
        <view v-if="ingredientLoading" class="state">正在整理食材...</view>
        <view v-else-if="ingredientError" class="state panel">
          <text>{{ ingredientError }}</text>
          <button class="btn tonal" @tap="loadIngredients">重试</button>
        </view>
        <view v-else-if="!ingredientItems.length" class="state">当前没有需要准备的食材</view>
        <view v-else class="ingredient-list">
          <view v-for="item in ingredientItems" :key="`${item.name}-${item.unit}`" class="ingredient-row">
            <text>{{ item.name }}</text>
            <text>{{ ingredientAmount(item) }}</text>
          </view>
        </view>
        <button v-if="ingredientItems.length" class="btn block sheet-primary" @tap="copyIngredients">复制清单</button>
      </view>
    </view>
  </view>
</template>

<script setup lang="js">
import {computed, onMounted, ref, watch} from 'vue'
import BackButton from '../../components/BackButton.vue'
import DishImageCard from '../../components/DishImageCard.vue'
import MealDishFilters from '../../components/MealDishFilters.vue'
import Icon from '../../components/Icons.vue'
import StatusBadge from '../../components/StatusBadge.vue'
import {assetUrl, currentUser, request, run} from '../../api/client'
import {formatMealTime, ingredientListText, mealInteractionState, numericTimestamp} from '../../utils/app'
import {
  availableDishTags,
  filterMealDishes,
  groupMealOrders,
  mealDetailInitialTab,
  sanitizeMealTags
} from '../../utils/meals'

const id = ref(''), meal = ref(null), dishes = ref([]), cuisines = ref([]), tab = ref('pick')
const cuisineId = ref(null), activeTags = ref(new Set()), query = ref(''), page = ref(1), detailDish = ref(null)
const rating = ref(5), comment = ref(''), loading = ref(false), error = ref(''), invalidRoute = ref(false)
const inFlight = ref(new Set()), selected = ref(new Set()), skipped = ref(new Set()), me = ref(currentUser())
const ingredientSheet = ref(false), ingredientLoading = ref(false), ingredientItems = ref([]), ingredientError = ref('')
const showMore = ref(false)
const mealTypeLabels = {breakfast: '早餐', lunch: '午餐', dinner: '晚餐'}
const memberColors = ['member-red', 'member-blue', 'member-green', 'member-amber', 'member-purple']

const interaction = computed(() => mealInteractionState(meal.value, me.value))
const deadlineText = computed(() => {
  const timestamp = numericTimestamp(meal.value?.order_deadline);
  if (timestamp === null) return '点菜截止时间待定';
  const date = new Date(timestamp * 1000);
  return Number.isNaN(date.getTime()) ? '点菜截止时间待定' : `${date.toLocaleString('zh-CN', {
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    hour12: false
  })} 截止点菜`
})
const availableTags = computed(() => availableDishTags(dishes.value, cuisineId.value))
const filteredDishes = computed(() => filterMealDishes({
  dishes: dishes.value,
  cuisineId: cuisineId.value,
  tags: activeTags.value,
  query: query.value,
  selectedIds: selected.value
}))
const visibleDishes = computed(() => filteredDishes.value.slice(0, page.value * 18))
const groups = computed(() => groupMealOrders(meal.value?.orders || []))
const reviewAverage = computed(() => {
  const reviews = Array.isArray(meal.value?.reviews) ? meal.value.reviews : [];
  return reviews.length ? (reviews.reduce((sum, review) => sum + (Number(review.rating) || 0), 0) / reviews.length).toFixed(1) : '0.0'
})

const allMembers = computed(() => {
  const members = []
  const seen = new Set()
  if (meal.value?.cook?.id) {
    members.push({...meal.value.cook, isCook: true})
    seen.add(meal.value.cook.id)
  }
  for (const order of (meal.value?.orders || [])) {
    for (const person of (order.people || [])) {
      if (person.id && !seen.has(person.id)) {
        members.push({...person, isCook: false})
        seen.add(person.id)
      }
    }
  }
  return members
})

function memberColorClass(idx) {
  return memberColors[idx % memberColors.length]
}

function getMemberIndex(person) {
  const idx = allMembers.value.findIndex(m => m.id === person.id)
  return idx >= 0 ? idx : 0
}

watch([query, cuisineId], () => {
  page.value = 1
})
watch(availableTags, tags => {
  activeTags.value = sanitizeMealTags(activeTags.value, tags)
})

function pending(key) {
  return inFlight.value.has(key)
}

function setPending(key, value) {
  const next = new Set(inFlight.value);
  value ? next.add(key) : next.delete(key);
  inFlight.value = next
}

function setQuery(value) {
  query.value = value;
  page.value = 1
}

function setCuisine(value) {
  cuisineId.value = value;
  page.value = 1
}

function toggleTag(tag) {
  const next = new Set(activeTags.value);
  next.has(tag) ? next.delete(tag) : next.add(tag);
  activeTags.value = next;
  page.value = 1
}

function resetFilters() {
  query.value = '';
  cuisineId.value = null;
  activeTags.value = new Set();
  page.value = 1
}

function interestCount(dishId) {
  return groups.value.find(group => group.dishId === dishId)?.people.length || 0
}

function routeMealId() {
  try {
    const pages = typeof getCurrentPages === 'function' ? getCurrentPages() : [];
    const current = pages[pages.length - 1];
    return typeof current?.options?.id === 'string' ? current.options.id.trim() : ''
  } catch {
    return ''
  }
}

async function load() {
  if (!id.value) {
    invalidRoute.value = true;
    error.value = '饭局参数无效';
    return false
  }
  loading.value = true;
  error.value = ''
  try {
    const [loadedMeal, loadedDishes, loadedCuisines] = await Promise.all([request(`/api/meals/${id.value}`), request('/api/dishes'), request('/api/cuisines')])
    if (!loadedMeal || typeof loadedMeal !== 'object') throw new Error('饭局加载失败')
    meal.value = loadedMeal;
    dishes.value = Array.isArray(loadedDishes) ? loadedDishes : [];
    cuisines.value = Array.isArray(loadedCuisines) ? loadedCuisines : []
    selected.value = new Set(Array.isArray(loadedMeal.my_ordered_dish_ids) ? loadedMeal.my_ordered_dish_ids : [])
    skipped.value = new Set(Array.isArray(loadedMeal.skipped_dish_ids) ? loadedMeal.skipped_dish_ids : [])
    const mine = (Array.isArray(loadedMeal.reviews) ? loadedMeal.reviews : []).find(review => review?.user_id === me.value?.id)
    if (mine) {
      rating.value = Number(mine.rating) || 5;
      comment.value = mine.comment || ''
    }
    tab.value = mealDetailInitialTab({canOrder: interaction.value.canOrder, isCook: interaction.value.isCook})
    if (!interaction.value.canOrder) tab.value = 'ordered'
    return true
  } catch (loadError) {
    error.value = loadError?.message || '饭局加载失败';
    return false
  } finally {
    loading.value = false
  }
}

async function mutate(key, action, success = '') {
  if (pending(key)) return false;
  setPending(key, true);
  try {
    await run(action, success);
    return true
  } catch {
    return false
  } finally {
    setPending(key, false)
  }
}

async function reloadAfterMutation() {
  if (!await load()) throw new Error('饭局已更新，请重新加载')
}

async function toggleCook() {
  showMore.value = false;
  if (interaction.value.canCook) await mutate('cook', async () => {
    await request(`/api/meals/${id.value}/cook`, {method: 'POST'});
    await reloadAfterMutation()
  }, '主厨已更新')
}

function confirmCancellation() {
  return new Promise(resolve => {
    try {
      uni.showModal({
        title: '取消饭局',
        content: '确定取消这场饭局吗？',
        success: result => resolve(Boolean(result?.confirm)),
        fail: () => resolve(false)
      })
    } catch {
      resolve(false)
    }
  })
}

async function setStatus(nextStatus) {
  showMore.value = false
  const allowed = (nextStatus === 'cooking' && interaction.value.canStartCooking) || (nextStatus === 'done' && interaction.value.canComplete) || (nextStatus === 'cancelled' && interaction.value.canCancel)
  if (!allowed || (nextStatus === 'cancelled' && !await confirmCancellation())) return
  await mutate(`status:${nextStatus}`, async () => {
    await request(`/api/meals/${id.value}/status`, {method: 'PATCH', data: {status: nextStatus}});
    await reloadAfterMutation()
  }, '饭局状态已更新')
}

async function refreshMealOnly() {
  const loaded = await request(`/api/meals/${id.value}`);
  if (!loaded || typeof loaded !== 'object') throw new Error('饭局刷新失败');
  meal.value = loaded;
  skipped.value = new Set(Array.isArray(loaded.skipped_dish_ids) ? loaded.skipped_dish_ids : [])
}

async function toggleOrder(dishId) {
  if (!interaction.value.canOrder || !dishId || pending(`order:${dishId}`)) return
  const before = new Set(selected.value), optimistic = new Set(before);
  optimistic.has(dishId) ? optimistic.delete(dishId) : optimistic.add(dishId);
  selected.value = optimistic
  await mutate(`order:${dishId}`, async () => {
    try {
      const result = await request(`/api/meals/${id.value}/orders/${dishId}`, {method: 'POST'});
      if (typeof result?.selected !== 'boolean') throw new Error('点菜更新失败');
      const next = new Set(selected.value);
      result.selected ? next.add(dishId) : next.delete(dishId);
      selected.value = next;
      await refreshMealOnly()
    } catch (requestError) {
      selected.value = before;
      throw requestError
    }
  })
}

async function toggleSkip(dishId) {
  if (!interaction.value.canSkip || !dishId) return;
  await mutate(`skip:${dishId}`, async () => {
    const result = await request(`/api/meals/${id.value}/skips/${dishId}`, {method: 'POST'});
    if (typeof result?.skipped !== 'boolean') throw new Error('菜品状态更新失败');
    const next = new Set(skipped.value);
    result.skipped ? next.add(dishId) : next.delete(dishId);
    skipped.value = next
  })
}

async function openDish(dish) {
  if (!dish?.id) return;
  detailDish.value = dish;
  try {
    const detail = await request(`/api/dishes/${dish.id}`);
    if (detail && typeof detail === 'object') detailDish.value = detail
  } catch {
  }
}

function copySource(value) {
  if (typeof uni.setClipboardData === 'function') uni.setClipboardData({data: value})
}

function ingredientAmount(item) {
  const parts = [];
  if (item?.total !== null && item?.total !== undefined) parts.push(`${Number(item.total)}${item.unit || ''}`);
  if (Array.isArray(item?.fragments)) parts.push(...item.fragments.filter(Boolean));
  return parts.join('、') || '按需'
}

async function openIngredients() {
  ingredientSheet.value = true;
  await loadIngredients()
}

async function loadIngredients() {
  ingredientLoading.value = true;
  ingredientError.value = '';
  try {
    const result = await request(`/api/meals/${id.value}/ingredient-list`);
    ingredientItems.value = Array.isArray(result?.items) ? result.items : []
  } catch (loadError) {
    ingredientError.value = loadError?.message || '食材清单加载失败'
  } finally {
    ingredientLoading.value = false
  }
}

function copyIngredients() {
  if (typeof uni.setClipboardData === 'function') uni.setClipboardData({data: ingredientListText(meal.value, ingredientItems.value)})
}

async function submitReview() {
  if (interaction.value.canReview) await mutate('review', async () => {
    await request(`/api/meals/${id.value}/review`, {
      method: 'PUT',
      data: {rating: rating.value, comment: comment.value}
    });
    await refreshMealOnly()
  }, '评价已保存')
}

onMounted(() => {
  id.value = routeMealId();
  if (!id.value) {
    invalidRoute.value = true;
    error.value = '饭局参数无效';
    return
  }
  load()
})
</script>

<style scoped>
.meal-page {
  max-width: 980px
}

.state.panel {
  padding: 64rpx 30rpx
}

.state .btn {
  margin-top: 22rpx
}

.reset-link {
  display: inline-flex;
  min-height: 58rpx;
  padding: 0;
  padding-left: 12rpx;
  align-items: center;
  background: transparent;
  color: var(--theme-text-action);
  font-size: 23rpx;
}

/* Heading */
.meal-heading {
  display: flex;
  flex-direction: column;
  border-bottom: 1px solid var(--theme-border-subtle)
}

.meal-title {
  display: flex;
  align-items: center;
  flex-direction: row;
  justify-content: space-between;
  gap: 8rpx
}

.meal-title .title {
  font-family: "Songti SC", "STSong", "Noto Serif CJK SC", serif;
  flex: 1;
  overflow: hidden;
}

.status-row {
  display: flex;
  align-items: center;
  gap: 16rpx;
  position: relative;
  z-index: 10;
}

.more-wrap {
  position: relative
}

.more-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 60rpx;
  min-width: 60rpx;
  padding: 0 12rpx;
  background: transparent;
  border: 1px solid var(--theme-border-subtle);
  border-radius: 8rpx;
  color: var(--theme-text-secondary);
}
.more-btn :deep(svg) {
  pointer-events: none;
}

.more-menu {
  position: absolute;
  top: 70rpx;
  right: 0;
  background: var(--theme-bg-surface);
  border: 1px solid var(--theme-border-subtle);
  border-radius: 12rpx;
  box-shadow: var(--theme-shadow-soft);
  z-index: 20;
  min-width: 200rpx
}

.more-item {
  display: block;
  width: 100%;
  padding: 20rpx 24rpx;
  background: transparent;
  border: none;
  text-align: left;
  color: var(--theme-text-primary);
  font-size: 27rpx
}

.more-item:active {
  background: var(--theme-bg-subtle)
}

.more-item.danger {
  color: var(--theme-danger)
}

.meal-time {
  margin-top: 18rpx;
  color: var(--theme-text-primary);
  font-size: 27rpx
}

.deadline {
  margin-top: 6rpx;
  color: var(--theme-text-secondary);
  font-size: 23rpx
}

/* Inline error */
.inline-error {
  display: flex;
  margin: 22rpx 24rpx 0;
  padding: 18rpx 20rpx;
  align-items: center;
  justify-content: space-between;
  border-left: 4rpx solid var(--theme-danger);
  background: var(--theme-danger-surface);
  color: var(--theme-danger);
  font-size: 23rpx
}

.inline-error button {
  min-height: 56rpx;
  padding: 0 12rpx;
  background: transparent;
  color: var(--theme-danger);
  font-size: 23rpx
}

/* Cook section */
.cook-section {
  padding: 24rpx 0
}

.cook-members {
  display: flex;
  flex-wrap: wrap;
  gap: 12rpx
}

.member {
  display: inline-flex;
  align-items: center;
  padding: 10rpx 20rpx;
  border-radius: 28rpx;
  font-size: 24rpx;
  color: #fff;
  line-height: 1.2
}

.member.cook {
  position: relative
}

.chef-hat {
  font-size: 20rpx;
  margin-right: 4rpx;
  transform: rotate(15deg)
}

.cook-hint {
  display: block;
  color: var(--theme-text-secondary);
  font-size: 22rpx
}

.cook-claim {
  margin-top: 20rpx;
  width: 100%;
  min-height: 72rpx;
  padding: 0 32rpx;
  font-size: 26rpx;
  display: flex;
  align-items: center;
  justify-content: center
}

/* Member colors */
.member-red {
  background: #b54747
}

.member-blue {
  background: #4a7c9b
}

.member-green {
  background: #5a8a6a
}

.member-amber {
  background: #c47832
}

.member-purple {
  background: #7b6199
}

/* Tabs */
.view-tabs {
  display: flex;
  border-bottom: 1px solid var(--theme-border-subtle)
}

.view-tabs view {
  position: relative;
  display: flex;
  flex: 1;
  min-height: 76rpx;
  padding: 0 10rpx;
  align-items: center;
  justify-content: center;
  background: transparent;
  color: var(--theme-text-secondary);
  font-size: 27rpx
}

.view-tabs view.on {
  color: var(--theme-text-primary);
  font-weight: 600
}

.view-tabs view.on::after {
  content: '';
  position: absolute;
  bottom: -1px;
  left: 0;
  right: 0;
  height: 3rpx;
  background: var(--theme-action-primary)
}

.view-tabs text {
  margin-left: 8rpx;
  color: var(--theme-text-secondary);
  font-weight: 400
}

/* Ordered section */
.ordered-heading {
  padding: 24rpx 24rpx 16rpx
}

.order-list {
  padding: 0 24rpx
}

.order-row {
  display: flex;
  padding: 20rpx 0;
  border-bottom: 1px solid var(--theme-border-subtle);
  gap: 20rpx
}

.order-row:last-child {
  border: none
}

.order-img-wrap {
  width: 88rpx;
  height: 88rpx;
  border-radius: 12rpx;
  overflow: hidden;
  flex-shrink: 0;
  background: var(--theme-bg-placeholder)
}

.order-img-wrap image {
  width: 100%;
  height: 100%
}

.order-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--theme-text-secondary)
}

.order-copy {
  flex: 1;
  min-width: 0
}

.order-name {
  font-size: 28rpx;
  font-weight: 600;
  color: var(--theme-text-primary)
}

.order-count {
  display: block;
  margin-top: 4rpx;
  color: var(--theme-text-secondary);
  font-size: 22rpx
}

.order-people {
  display: flex;
  flex-direction: row;
  flex-wrap: wrap;
  align-items: flex-start;
  justify-content: flex-start;
  gap: 5rpx;
}

.person-pill {
  flex-shrink: 0;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 4rpx 14rpx;
  border-radius: 20rpx;
  font-size: 20rpx;
  color: #fff;
  line-height: 1.4;
  white-space: nowrap
}

/* Reviews */
.reviews-section {
  padding: 32rpx 24rpx;
  border-top: 1px solid var(--theme-border-subtle)
}

.reviews-heading {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  margin-bottom: 20rpx
}

.review-editor {
  padding: 24rpx
}

.stars {
  display: flex;
  gap: 8rpx;
  margin-bottom: 16rpx
}

.stars button {
  background: none;
  border: none;
  font-size: 36rpx;
  color: var(--theme-star-empty)
}

.stars button.on {
  color: var(--theme-star-active)
}

.review-editor .input {
  min-height: 140rpx
}

.review-row {
  padding: 20rpx 0;
  border-bottom: 1px solid var(--theme-border-subtle)
}

.review-row:last-child {
  border: none
}

.review-line {
  display: flex;
  justify-content: space-between;
  font-size: 27rpx
}

/* Common */
.section-title {
  color: var(--theme-text-primary);
  font-size: 30rpx;
  font-weight: 600
}

.subtle {
  color: var(--theme-text-secondary);
  font-size: 23rpx
}

.btn {
  display: inline-flex;
  min-height: 80rpx;
  padding: 0 32rpx;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-control);
  background: var(--theme-action-primary);
  color: var(--theme-action-on-primary);
  font-size: 27rpx;
  font-weight: 600
}

.btn[disabled] {
  opacity: .48
}

.btn.tonal {
  border: 1px solid var(--theme-border-subtle);
  background: var(--theme-bg-surface);
  color: var(--theme-text-action)
}

.btn.ghost {
  background: transparent;
  color: var(--theme-text-secondary)
}

.btn.block {
  width: 100%
}

.input {
  display: flex;
  width: 100%;
  min-height: 84rpx;
  padding: 0 24rpx;
  align-items: center;
  border: 1px solid var(--theme-border-subtle);
  border-radius: var(--radius-control);
  background: var(--theme-bg-surface);
  color: var(--theme-text-primary);
  font-size: 27rpx
}

.panel {
  background: var(--theme-bg-surface);
  border: 1px solid var(--theme-border-subtle);
  border-radius: var(--radius-panel);
  flex-direction: column
}

.load-more {
  width: 100%;
  margin: 24rpx 0;
  padding: 20rpx;
  border: 1px dashed var(--theme-border-subtle);
  border-radius: var(--radius-control);
  background: transparent;
  color: var(--theme-text-secondary);
  font-size: 27rpx
}

.modal-mask {
  position: fixed;
  z-index: 90;
  inset: 0;
  display: flex;
  align-items: flex-end;
  background: var(--theme-modal-scrim)
}

.sheet {
  width: 100%;
  max-height: 88%;
  overflow-y: auto;
  padding: 48rpx;
  border-radius: 24rpx 24rpx 0 0;
  background: var(--theme-bg-surface);
  flex-direction: column
}

.sheet-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24rpx
}

.sheet-close {
  background: transparent;
  border: none;
  color: var(--theme-text-secondary);
  padding: 8rpx
}

.sheet-primary {
  margin-top: 24rpx
}

.detail-image {
  width: 100%;
  height: 400rpx;
  border-radius: 16rpx;
  margin-bottom: 20rpx
}

.detail-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 8rpx;
  margin-bottom: 16rpx
}

.badge {
  display: inline-flex;
  padding: 6rpx 16rpx;
  border-radius: 6rpx;
  background: var(--theme-success-subtle);
  color: var(--theme-text-action);
  font-size: 22rpx
}

.badge.neutral {
  background: var(--theme-bg-subtle);
  color: var(--theme-text-secondary)
}

.detail-description {
  color: var(--theme-text-primary);
  font-size: 27rpx;
  line-height: 1.65;
  margin-bottom: 24rpx
}

.detail-section {
  margin-bottom: 24rpx
}

.compact-title {
  font-size: 26rpx;
  margin-bottom: 12rpx
}

.detail-row {
  display: block;
  padding: 8rpx 0;
  border-bottom: 1px solid var(--theme-border-subtle);
  color: var(--theme-text-primary);
  font-size: 26rpx
}

.step-row {
  display: flex;
  gap: 16rpx;
  margin-bottom: 16rpx
}

.step-row text:first-child {
  width: 36rpx;
  height: 36rpx;
  border-radius: 50%;
  background: var(--theme-bg-subtle);
  color: var(--theme-text-action);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22rpx;
  font-weight: 600;
  flex-shrink: 0
}

.step-row text:last-child {
  flex: 1;
  color: var(--theme-text-primary);
  font-size: 26rpx;
  line-height: 1.5
}

.source-link {
  display: block;
  margin-bottom: 16rpx;
  color: var(--theme-text-action);
  font-size: 24rpx
}

.ingredient-list {
  margin: 20rpx 0
}

.ingredient-row {
  display: flex;
  justify-content: space-between;
  padding: 14rpx 0;
  border-bottom: 1px solid var(--theme-border-subtle)
}

.ingredient-row text {
  font-size: 26rpx
}

@media (min-width: 700px) {
  .dish-grid {
    grid-template-columns:repeat(3, minmax(0, 1fr));
    gap: 22rpx
  }
}

@media (min-width: 1024px) {
  .dish-grid {
    grid-template-columns:repeat(4, minmax(0, 1fr))
  }
}

.dish-grid {
  display: grid;
  grid-template-columns:repeat(2, 1fr);
  gap: 16rpx
}

.status-row, .inline-error, .cook-section, .view-tabs, .ordered-heading, .stars, .review-line, .sheet-head, .detail-meta, .ingredient-row {
  flex-direction: row
}
</style>
