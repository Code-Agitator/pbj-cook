<template>
  <view class="page no-tab meal-page" @tap="showMore = false">
    <view v-if="invalidRoute" class="state panel">
      <text>饭局参数无效</text>
      <view class="btn tonal" @tap="back">返回饭局</view>
    </view>
    <view v-else-if="loading && !meal" class="state">正在准备饭局...</view>
    <view v-else-if="error && !meal" class="state panel">
      <text>{{ error }}</text>
      <view class="btn tonal" @tap="load">重新加载</view>
      <view class="btn ghost" @tap="back">返回饭局</view>
    </view>

    <template v-else-if="meal">
      <view class="topbar">
        <BackButton label="饭局" />
        <view class="more-wrap" v-if="hasMoreMenuItems" @tap.stop>
          <view class="more-btn" @tap="showMore = !showMore">⋯</view>
          <view class="more-menu" v-if="showMore">
            <view v-if="interaction.isCook" class="more-item" @tap="setStatus('cooking')">结束点菜</view>
            <view v-if="interaction.canComplete" class="more-item" @tap="setStatus('done')">完成饭局</view>
            <view v-if="interaction.canCancel" class="more-item danger" @tap="setStatus('cancelled')">取消饭局</view>
          </view>
        </view>
      </view>

      <header class="heading">

        <text class="title">{{ meal.title || mealTypeLabels[meal.meal_type] || '饭局' }}</text>
        <view class="when"><text class="date-text">{{ meal.date || '日期待定' }}</text> · {{ formatMealTime(meal.dining_time) }} 开饭 · {{ cookStatusText }} · <text class="status-chip">{{ statusLabel }}</text></view>
        <view class="deadline">点菜截止 <text class="deadline-strong">{{ deadlineStrong }}</text> · {{ deadlineCountdown }}</view>
      </header>

      <view class="panel">
        <text class="panel-label">本局阵容 · 认领只代表掌勺，不影响任何人点菜</text>
        <view class="crew">
          <view v-for="(person, idx) in allMembers" :key="person.id || idx" class="mate"
                :class="{ cook: person.isCook, you: person.id === me?.id }">
            <text class="face" :class="memberColorClass(idx)">{{ getInitial(person.name) }}<text v-if="person.isCook" class="hat">🧑‍🍳</text></text>
            <text class="mate-name">{{ person.name || '成员' }}<text v-if="person.id === me?.id">（你）</text></text>
          </view>
        </view>
        <view v-if="interaction.canCook && !interaction.isCook" class="claim-btn" :class="{ disabled: pending('cook') }" @tap="toggleCook">
          {{ pending('cook') ? '更新中...' : '认领主厨' }}
        </view>
        <view v-if="interaction.isCook" class="claim-btn on" @tap="toggleCook">
          {{ pending('cook') ? '更新中...' : '退出主厨' }}
        </view>
      </view>

      <view class="view-tabs">
        <view v-if="interaction.canOrder" :class="{ on: tab === 'pick' }" @tap="tab = 'pick'">点菜 <text class="tab-count">{{ selected.size }}</text></view>
        <view :class="{ on: tab === 'ordered' }" @tap="tab = 'ordered'">已点菜品 <text class="tab-count">{{ groups.length }}</text></view>
      </view>

      <!-- 点菜 -->
      <view v-if="tab === 'pick' && interaction.canOrder" class="view-section">
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
        <view v-if="visibleDishes.length < filteredDishes.length" class="load-more" @tap="page += 1">继续浏览</view>
        <text class="pick-done">点击卡片选中，再点一次取消 · 点菜截止前可随时修改</text>
      </view>

      <!-- 已点 -->
      <view v-else-if="tab === 'ordered'" class="view-section">
        <view class="order-list">
          <view v-if="groups.length" class="ordered-actions">
            <view class="ghost-btn" @tap="openIngredients">
              <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 6h16M4 12h16M4 18h10"/></svg>
              查看食材清单
            </view>
          </view>
          <view v-if="!groups.length" class="state panel">还没有人点菜</view>
          <view v-for="group in groups" :key="group.dishId" class="order-row">
            <view class="order-thumb"><image v-if="group.image" :src="assetUrl(group.image)" mode="aspectFill"/></view>
            <view class="order-main">
              <view class="order-title-line">
                <text class="order-name">{{ group.name }}</text>
                <text class="order-count">{{ group.people.length }} 人想吃</text>
              </view>
              <view class="people">
                <view v-for="(person, pIdx) in group.people" :key="person.id || pIdx" class="person-pill"
                      :class="memberColorClass(getMemberIndex(person))">{{ person.name || '成员' }}
                </view>
              </view>
            </view>
          </view>
        </view>
      </view>

      <view class="section-gap"></view>

      <!-- 饭后评价 -->
      <view v-if="interaction.canReview" class="panel reviews-panel">
        <text class="panel-label">饭后评价 · 饭局结束后可打分</text>
        <view class="review-editor">
          <view class="stars-edit">
            <view v-for="number in 5" :key="number" :class="{ on: rating >= number }" @tap="rating = number">★</view>
          </view>
          <textarea v-model="comment" class="review-textarea" maxlength="200" placeholder="说说这顿饭的味道"/>
          <view class="btn review-submit" :class="{ disabled: pending('review') }" @tap="submitReview">
            {{ pending('review') ? '保存中...' : '保存评价' }}
          </view>
        </view>
        <view class="section-gap"></view>
        <view v-for="review in meal.reviews || []" :key="review.id" class="review-row">
          <view class="review-line">
            <text>{{ review.user_name || '成员' }}</text>
            <text class="review-stars">{{ '★'.repeat(Number(review.rating) || 0) }}{{ '☆'.repeat(5 - (Number(review.rating) || 0)) }}</text>
          </view>
          <text v-if="review.comment" class="review-comment">{{ review.comment }}</text>
        </view>
      </view>
    </template>

    <!-- 菜品详情弹层 -->
    <BottomSheet v-model="showDishSheet" @close="detailDish = null">
      <view class="sheet-head">
        <view class="sheet-head-info">
          <text class="sheet-title">{{ detailDish?.name || '菜品详情' }}</text>
          <text class="sheet-sub">{{ detailDish?.cuisine_name || '' }}<text v-if="detailDish && interestCount(detailDish.id)"> · {{ interestCount(detailDish.id) }} 人想吃</text></text>
        </view>
      </view>
      <view v-if="detailDish?.image_path" class="detail-photo">
        <image :src="assetUrl(detailDish.image_path)" mode="aspectFill" class="detail-photo-image"/>
      </view>
      <view v-else class="detail-photo placeholder">
        <Icon icon="ChefHat" :size="42"/>
      </view>
      <view class="detail-meta">
        <text v-if="detailDish?.cuisine_name" class="badge inline">{{ detailDish.cuisine_name }}</text>
        <text v-for="tag in detailDish?.tags || []" :key="tag" class="badge neutral inline">{{ tag }}</text>
      </view>
      <text v-if="detailDish?.description" class="detail-description">{{ detailDish.description }}</text>
      <view v-if="detailDish?.ingredients?.length" class="detail-section">
        <text class="sub-title inline-title">食材</text>
        <view v-for="item in detailDish.ingredients" :key="`${item.name}-${item.unit}`" class="ing-row">
          <text>{{ item.name }}</text>
          <text class="ing-leader"></text>
          <text class="ing-amt">{{ item.quantity || '' }}{{ item.unit || '' }}</text>
        </view>
      </view>
      <view v-if="detailDish?.steps?.length" class="detail-section">
        <text class="sub-title inline-title">做法</text>
        <view v-for="(step, index) in detailDish.steps" :key="step.id || index" class="step-row">
          <text class="step-num">{{ index + 1 }}</text>
          <text>{{ step.body }}</text>
        </view>
      </view>
      <view v-if="detailDish?.source_url" class="source-link" @tap="copySource(detailDish.source_url)">复制菜谱来源</view>
      <view class="btn block primary" :class="{ disabled: detailDish && pending(`order:${detailDish.id}`), off: !selected.has(detailDish?.id) }"
            @tap="detailDish && toggleOrder(detailDish.id)">{{ selected.has(detailDish?.id) ? '取消这道菜' : '点这道菜' }}
      </view>
    </BottomSheet>

    <!-- 食材清单弹层 -->
    <BottomSheet v-model="ingredientSheet" @close="ingredientSheet = false">
      <view class="sheet-head">
        <view class="sheet-head-info">
          <text class="sheet-title">食材清单</text>
          <text class="sheet-sub">已合并相同食材，按已点菜品统计</text>
        </view>
      </view>
      <view v-if="ingredientLoading" class="state">正在整理食材...</view>
      <view v-else-if="ingredientError" class="state panel">
        <text>{{ ingredientError }}</text>
        <view class="btn tonal" @tap="loadIngredients">重试</view>
      </view>
      <view v-else-if="!ingredientItems.length" class="state">当前没有需要准备的食材</view>
      <view v-else class="ingredient-content">
        <text class="ing-note">{{ ingredientNote }}</text>
        <view v-for="item in ingredientItems" :key="`${item.name}-${item.unit}`" class="ing-row">
          <text>{{ item.name }}</text>
          <text class="ing-leader"></text>
          <text class="ing-amt">{{ ingredientAmount(item) }}</text>
        </view>
      </view>
      <view v-if="ingredientItems.length" class="btn block primary" @tap="copyIngredients">复制清单</view>
    </BottomSheet>
  </view>
</template>

<script setup lang="js">
import {computed, onMounted, ref, watch} from 'vue'
import BottomSheet from '../../components/BottomSheet.vue'
import DishImageCard from '../../components/DishImageCard.vue'
import MealDishFilters from '../../components/MealDishFilters.vue'
import Icon from '../../components/Icons.vue'
import BackButton from '../../components/BackButton.vue'
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
let isFirstLoad = true
const cuisineId = ref(null), activeTags = ref(new Set()), query = ref(''), page = ref(1), detailDish = ref(null)
const rating = ref(5), comment = ref(''), loading = ref(false), error = ref(''), invalidRoute = ref(false)
const inFlight = ref(new Set()), selected = ref(new Set()), skipped = ref(new Set()), me = ref(currentUser())
const ingredientSheet = ref(false), ingredientLoading = ref(false), ingredientItems = ref([]), ingredientError = ref('')
const showMore = ref(false)
const mealTypeLabels = {breakfast: '早餐', lunch: '午餐', dinner: '晚餐'}
const memberColors = ['member-a1', 'member-a2', 'member-a3', 'member-a4', 'member-a5']

const statusLabels = {
  ordering: '点菜中',
  cooking: '做饭中',
  done: '已完成',
  cancelled: '已取消'
}

const interaction = computed(() => mealInteractionState(meal.value, me.value))

const hasMoreMenuItems = computed(() => {
  const it = interaction.value
  return it.isCook || it.canComplete || it.canCancel
})

// 菜品详情面板的 v-model 桥接（detailDish 为对象/null，需转为 boolean）
const showDishSheet = computed({
  get: () => !!detailDish.value,
  set: (val) => { if (!val) detailDish.value = null }
})

const statusLabel = computed(() => statusLabels[meal.value?.status] || '状态未知')

const cookStatusText = computed(() => {
  if (!meal.value) return '无人掌勺'
  return meal.value.cook?.name ? meal.value.cook.name + ' 掌勺' : '无人掌勺'
})

const deadlineStrong = computed(() => {
  const timestamp = numericTimestamp(meal.value?.order_deadline)
  if (timestamp === null) return '待定'
  const date = new Date(timestamp * 1000)
  if (Number.isNaN(date.getTime())) return '待定'
  const hours = date.getUTCHours()
  const minutes = String(date.getUTCMinutes()).padStart(2, '0')
  return `${hours}:${minutes}`
})

const deadlineCountdown = computed(() => {
  const timestamp = numericTimestamp(meal.value?.order_deadline)
  if (timestamp === null) return ''
  const now = Math.floor(Date.now() / 1000)
  const diff = timestamp - now
  if (diff <= 0) return '已截止'
  const hours = Math.floor(diff / 3600)
  const minutes = Math.floor((diff % 3600) / 60)
  if (hours >= 24) {
    const days = Math.floor(hours / 24)
    return `还剩 ${days} 天`
  }
  if (hours > 0) return `还剩 ${hours} 小时`
  return `还剩 ${minutes} 分钟`
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

const ingredientNote = computed(() => {
  if (!ingredientItems.value.length) return ''
  return `共 ${ingredientItems.value.length} 种食材`
})

const allMembers = computed(() => {
  const members = []
  const seen = new Set()
  if (meal.value?.cook?.id) {
    members.push({...meal.value.cook, isCook: true})
    seen.add(meal.value.cook.id)
  }
  for (const order of (meal.value?.orders || [])) {
    if (order.user_id && !seen.has(order.user_id)) {
      members.push({
        id: order.user_id,
        name: order.user_name,
        avatar_path: order.user_avatar,
        isCook: false
      })
      seen.add(order.user_id)
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

function getInitial(name) {
  if (!name) return '?'
  return name.charAt(0)
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

function back() {
  try {
    if (typeof getCurrentPages === 'function' && getCurrentPages().length > 1) {
      return uni.navigateBack()
    }
  } catch {}
  uni.reLaunch({url: '/pages/meals/index'})
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
    if (isFirstLoad) {
      tab.value = mealDetailInitialTab({canOrder: interaction.value.canOrder, isCook: interaction.value.isCook})
      if (!interaction.value.canOrder) tab.value = 'ordered'
      isFirstLoad = false
    }
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
  if (interaction.value.canCook || interaction.value.isCook) await mutate('cook', async () => {
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
  max-width: 980px;
}

.state.panel {
  padding: 64rpx 30rpx;
}

.state .btn {
  margin-top: 22rpx;
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

/* ---------- Topbar ---------- */
.topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.more-wrap {
  position: relative;
}

.more-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 76rpx;
  height: 76rpx;
  min-height: 76rpx;
  border: 0;
  border-radius: 50%;
  background: #FFFFFF;
  background: var(--theme-bg-card, #FFFFFF);
  box-shadow: 0 4rpx 16rpx rgba(39, 33, 26, 0.12);
  color: var(--theme-text-primary);
  font-size: 34rpx;
  font-weight: 600;
}

.more-btn:active {
  transform: scale(0.95);
  box-shadow: 0 2rpx 8rpx rgba(39, 33, 26, 0.1);
}

.more-menu {
  position: absolute;
  top: 88rpx;
  right: 0;
  width: 280rpx;
  background: var(--theme-bg-surface);
  border: 1px solid var(--theme-border-subtle);
  border-radius: 16rpx;
  box-shadow: var(--theme-shadow-soft);
  overflow: hidden;
  z-index: 30;
  min-width: 280rpx;
}

.more-item {
  display: block;
  width: 100%;
  padding: 24rpx 32rpx;
  background: transparent;
  border: none;
  border-bottom: 1px solid var(--theme-border-subtle);
  text-align: left;
  color: var(--theme-text-primary);
  font-size: 28rpx;
}

.more-item:last-child {
  border-bottom: 0;
}

.more-item:active {
  background: var(--theme-bg-subtle);
}

.more-item.danger {
  color: var(--theme-danger);
}

/* ---------- Heading ---------- */
.heading {
  margin-top: 24rpx;
}

.chip-row {
  display: flex;
  align-items: center;
  gap: 20rpx;
  margin-bottom: 16rpx;
}

.status-chip {
  font-size: 24rpx;
  font-weight: 700;
  color: var(--theme-danger);
  background: rgba(181, 71, 71, 0.09);
  border-radius: 999px;
  padding: 8rpx 24rpx;
}

.heading .title {
  font-size: 54rpx;
  font-weight: 800;
  line-height: 1.3;
  color: var(--theme-text-primary);
  font-family: "Songti SC", "STSong", "Serif";
}

.heading .when {
  margin-top: 8rpx;
  font-size: 28rpx;
  color: var(--theme-text-secondary);
  line-height: 1.5;
}

.date-text {
  color: var(--theme-text-primary);
  font-weight: 650;
}

.deadline {
  margin-top: 28rpx;
  padding: 20rpx 28rpx;
  border-radius: 14rpx;
  background: rgba(181, 71, 71, 0.07);
  font-size: 26rpx;
  color: var(--theme-danger);
}

.deadline-strong {
  font-weight: 750;
}

/* ---------- Panel ---------- */
.panel {
  margin: 24rpx 0;
  padding: 30rpx 40rpx;
  background: #FFFFFF;
  background: var(--theme-bg-card, #FFFFFF);
  border: 0;
  border-radius: 32rpx;
  box-shadow: 0 4rpx 16rpx rgba(39, 33, 26, 0.08);
  flex-direction: column;
}

.panel-label {
  display: block;
  font-size: 24rpx;
  color: var(--theme-text-secondary);
}

/* ---------- Crew ---------- */
.crew {
  display: flex;
  flex-wrap: wrap;
  gap: 28rpx;
  margin-top: 12rpx;
}

.mate {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12rpx;
  font-size: 24rpx;
  color: var(--theme-text-secondary);
  width: 112rpx;
}

.mate .face {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 92rpx;
  height: 92rpx;
  border-radius: 50%;
  font-size: 34rpx;
  font-weight: 800;
  color: #fff;
}

.face .hat {
  position: absolute;
  top: -18rpx;
  right: -14rpx;
  font-size: 30rpx;
  display: none;
}

.mate.cook .face {
  box-shadow: 0 0 0 5rpx var(--theme-bg-surface), 0 0 0 9rpx var(--theme-danger);
}

.mate.cook .face .hat {
  display: block;
}

.mate-name {
  font-size: 22rpx;
  white-space: nowrap;
}

.claim-btn {
  display: block;
  width: 100%;
  margin-top: 18rpx;
  padding: 12rpx;
  border-radius: 28rpx;
  border: 2rpx solid var(--theme-action-primary);
  background: transparent;
  color: var(--theme-action-primary);
  font-size: 30rpx;
  font-weight: 700;
  text-align: center;
}

.claim-btn:active {
  background: rgba(232, 130, 74, 0.06);
}

.claim-btn.on {
  border-color: var(--theme-danger);
  background: transparent;
  color: var(--theme-danger);
}

.claim-btn.disabled {
  opacity: 0.48;
  pointer-events: none;
}

/* Member colors for face avatars */
.member-a1 {
  background: var(--theme-danger);
}

.member-a2 {
  background: #56735A;
}

.member-a3 {
  background: #C98A2D;
}

.member-a4 {
  background: #7A6AAE;
}

.member-a5 {
  background: #4a7c9b;
}

/* ---------- View Tabs ---------- */
.view-tabs {
  display: flex;
  padding: 6rpx;
  background: rgba(180, 170, 155, 0.18);
  border-radius: 999px;
}

.view-tabs view {
  flex: 1;
  padding: 20rpx 0;
  border: 0;
  border-radius: 999px;
  background: transparent;
  font-size: 27rpx;
  font-weight: 650;
  color: rgba(80, 70, 55, 0.55);
  text-align: center;
  transition: all 0.25s cubic-bezier(.34, 1.3, .5, 1);
}

.view-tabs view.on {
  background: #fff;
  color: #3d3326;
  box-shadow: 0 6rpx 20rpx rgba(90, 60, 30, 0.12);
}

.tab-count {
  color: #c4593c;
  font-size: 22rpx;
  vertical-align: super;
}

/* ---------- View Section ---------- */
.view-section {
  padding: 0;
}

/* ---------- Dish Grid ---------- */
.dish-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16rpx;
}

@media (min-width: 700px) {
  .dish-grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 22rpx;
  }
}

@media (min-width: 1024px) {
  .dish-grid {
    grid-template-columns: repeat(4, minmax(0, 1fr));
  }
}

.load-more {
  width: 100%;
  margin: 24rpx 0;
  padding: 20rpx;
  border: 1px dashed var(--theme-border-subtle);
  border-radius: var(--radius-control);
  background: transparent;
  color: var(--theme-text-secondary);
  font-size: 27rpx;
  text-align: center;
}

.pick-done {
  display: block;
  margin: 36rpx 40rpx 0;
  font-size: 24rpx;
  color: var(--theme-text-secondary);
  text-align: center;
}

/* ---------- Ordered ---------- */
.ordered-actions {
  padding: 12rpx 0;
}

.ghost-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 14rpx;
  width: 100%;
  padding: 12rpx 0;
  border: 2rpx dashed var(--theme-action-primary);
  border-radius: 28rpx;
  background: transparent;
  color: var(--theme-action-primary);
  font-size: 29rpx;
  font-weight: 700;
}

.order-list {
  padding: 12rpx 0;
}

.order-row {
  display: flex;
  gap: 28rpx;
  padding: 22rpx 0;
  border-bottom: 1px solid var(--theme-border-subtle);
  flex-direction: row;
}

.order-row:last-child {
  border-bottom: 0;
}

.order-thumb {
  width: 108rpx;
  height: 108rpx;
  border-radius: 28rpx;
  overflow: hidden;
  flex-shrink: 0;
  background: var(--theme-bg-placeholder);
}

.order-thumb image {
  width: 100%;
  height: 100%;
}

.order-main {
  flex: 1;
  min-width: 0;
}

.order-title-line {
  display: flex;
  align-items: baseline;
  gap: 16rpx;
}

.order-name {
  font-size: 30rpx;
  font-weight: 700;
  color: var(--theme-text-primary);
}

.order-count {
  font-size: 24rpx;
  color: var(--theme-danger);
  font-weight: 600;
}

.people {
  display: flex;
  flex-wrap: wrap;
  gap: 12rpx;
  margin-top: 16rpx;
}

.person-pill {
  font-size: 23rpx;
  font-weight: 650;
  padding: 6rpx 20rpx;
  border-radius: 999px;
  color: #fff;
  white-space: nowrap;
}

/* ---------- Reviews ---------- */
.reviews-panel {
}

.review-editor {
  margin-top: 8rpx;
}

.stars-edit {
  display: flex;
  gap: 12rpx;
}

.stars-edit view {
  border: 0;
  background: none;
  font-size: 48rpx;
  color: var(--theme-star-empty);
  cursor: pointer;
  padding: 4rpx;
}

.stars-edit view.on {
  color: var(--theme-star-active);
}

.review-textarea {
  width: 100%;
  margin-top: 24rpx;
  padding: 24rpx 28rpx;
  border: 1.5rpx solid var(--theme-border-subtle);
  border-radius: 14rpx;
  background: var(--theme-bg-page);
  color: var(--theme-text-primary);
  font-size: 28rpx;
  min-height: 144rpx;
  resize: none;
  font-family: inherit;
}

.review-textarea:focus {
  border-color: var(--theme-action-primary);
  outline: none;
}

.review-submit {
  display: block;
  width: 100%;
  margin-top: 24rpx;
  padding: 26rpx;
  border: 0;
  border-radius: 28rpx;
  background: var(--theme-action-primary);
  color: var(--theme-action-on-primary);
  font-size: 30rpx;
  font-weight: 700;
  text-align: center;
}

.review-submit.disabled {
  opacity: 0.48;
  pointer-events: none;
}

.review-row {
  padding: 26rpx 0;
  border-bottom: 1px solid var(--theme-border-subtle);
}

.review-row:last-child {
  border-bottom: 0;
}

.review-line {
  display: flex;
  justify-content: space-between;
  font-size: 28rpx;
  font-weight: 650;
  color: var(--theme-text-primary);
}

.review-stars {
  color: #C98A2D;
  font-size: 26rpx;
  letter-spacing: 2rpx;
}

.review-comment {
  margin-top: 6rpx;
  font-size: 26rpx;
  color: var(--theme-text-secondary);
  display: block;
}

.section-gap {
  height: 52rpx;
}

/* ---------- Detail Sheet (内容样式，外壳由 BottomSheet 组件提供) ---------- */
.sheet-head {
  margin-bottom: 28rpx;
}

.sheet-head-info {
}

.sheet-title {
  font-size: 60rpx;
  font-weight: 750;
  color: var(--theme-text-primary);
}

.sheet-sub {
  font-size: 24rpx;
  color: var(--theme-text-secondary);
  margin-top: 4rpx;
}

.sheet-close {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 64rpx;
  height: 64rpx;
  border: 0;
  border-radius: 50%;
  background: var(--theme-bg-subtle);
  color: var(--theme-text-primary);
  font-size: 30rpx;
  cursor: pointer;
  flex-shrink: 0;
}

.detail-photo {
  border-radius: 36rpx;
  overflow: hidden;
  height: 300rpx;
  margin-bottom: 28rpx;
}

.detail-photo-image {
  width: 100%;
  height: 100%;
}

.detail-photo.placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--theme-bg-placeholder);
  color: var(--theme-text-secondary);
}

.detail-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 16rpx;
  margin-bottom: 24rpx;
}

.badge.inline {
  margin-bottom: 0;
}

.badge.neutral.inline {
  margin-bottom: 0;
}

.detail-description {
  margin-top: 24rpx;
  margin-bottom: 24rpx;
  font-size: 27rpx;
  color: var(--theme-text-secondary);
  line-height: 1.65;
}

.detail-section {
  margin-bottom: 24rpx;
}

.sub-title {
  font-size: 29rpx;
  font-weight: 750;
  color: var(--theme-text-primary);
  margin: 16rpx 0 8rpx;
  display: block;
}

.sub-title.inline-title {
  margin: 40rpx 0 0;
}

/* Ingredient row with leader dots */
.ing-row {
  display: flex;
  align-items: baseline;
  gap: 16rpx;
  padding: 12rpx 0;
  font-size: 28rpx;
  color: var(--theme-text-primary);
}

.ing-row .ing-leader {
  flex: 1;
  border-bottom: 2rpx dotted var(--theme-border-subtle);
  transform: translateY(-6rpx);
  min-width: 40rpx;
}

.ing-row .ing-amt {
  font-weight: 650;
}

/* Steps */
.step-row {
  display: flex;
  gap: 20rpx;
  padding: 14rpx 0;
  font-size: 28rpx;
  color: var(--theme-text-primary);
  flex-direction: row;
}

.step-row .step-num {
  flex-shrink: 0;
  width: 44rpx;
  height: 44rpx;
  border-radius: 50%;
  background: var(--theme-bg-subtle);
  font-size: 24rpx;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--theme-text-primary);
}

.step-row text:last-child {
  flex: 1;
  line-height: 1.6;
}

.source-link {
  display: block;
  margin-bottom: 16rpx;
  color: var(--theme-text-action);
  font-size: 26rpx;
}

/* Primary button in sheet */
.btn.block.primary {
  display: block;
  width: 100%;
  margin-top: 44rpx;
  padding: 30rpx;
  border: 0;
  border-radius: 32rpx;
  background: var(--theme-action-primary);
  color: #fff;
  font-size: 31rpx;
  font-weight: 700;
  text-align: center;
}

.btn.block.primary.disabled {
  opacity: 0.48;
  pointer-events: none;
}

.btn.block.primary.off {
  background: var(--theme-bg-subtle);
  color: var(--theme-text-primary);
}

/* Ingredient Sheet */
.ingredient-content {
  margin-top: 20rpx;
}

.ing-note {
  font-size: 25rpx;
  color: var(--theme-text-secondary);
  margin-bottom: 12rpx;
  display: block;
}

/* Section title for empty states */
.section-title {
  color: var(--theme-text-primary);
  font-size: 30rpx;
  font-weight: 600;
}

.subtle {
  color: var(--theme-text-secondary);
  font-size: 24rpx;
}

.btn {
  display: inline-flex;
  min-height: 80rpx;
  padding: 0 var(--space-5);
  align-items: center;
  justify-content: center;
  border-radius: 16rpx;
  background: var(--theme-action-primary);
  color: var(--theme-action-on-primary);
  font-size: 27rpx;
  font-weight: 600;
  align-self: center;
}

.btn.disabled {
  opacity: .48;
  pointer-events: none;
}

.btn.tonal {
  border: 1px solid var(--theme-border-subtle);
  background: var(--theme-bg-surface);
  color: var(--theme-text-action);
}

.btn.ghost {
  background: transparent;
  color: var(--theme-text-secondary);
}

.btn.block {
  width: 100%;
}

.input {
  display: flex;
  width: 100%;
  min-height: 84rpx;
  padding: 0 var(--space-4);
  align-items: center;
  border: 1px solid var(--theme-border-subtle);
  border-radius: var(--radius-control);
  background: var(--theme-bg-surface);
  color: var(--theme-text-primary);
  font-size: 27rpx;
}

.badge {
  display: inline-flex;
  padding: 6rpx 16rpx;
  border-radius: 6rpx;
  background: var(--theme-success-subtle);
  color: var(--theme-text-action);
  font-size: 22rpx;
}

.badge.neutral {
  background: var(--theme-bg-subtle);
  color: var(--theme-text-secondary);
}

/* Row flex direction helpers */
.topbar, .more-wrap, .chip-row, .crew, .view-tabs, .order-row, .order-title-line, .people,
.review-line, .sheet-head, .detail-meta, .ing-row, .step-row, .ordered-actions {
  flex-direction: row;
}
</style>
