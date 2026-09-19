<template>
  <view class="page">
    <view class="hero">
      <text class="family">{{ settings.family_name || '我们的家' }}</text>
      <h1 class="greeting">你好，{{ me?.name || '家人' }}</h1>
      <text class="prompt">今天想吃点什么？</text>
      <div class="amber-accent"></div>
    </view>

    <text class="section-title">临近的饭局</text>

    <view v-if="loading && !formattedUpcoming.length" class="state">正在加载饭局...</view>
    <view v-else-if="error && !formattedUpcoming.length" class="state panel">
      <text>{{ error }}</text>
      <button class="btn tonal" @tap="load">重试</button>
    </view>
    <view v-else-if="!formattedUpcoming.length" class="state empty-line">
      <text>还没有临近的饭局</text>
      <button @tap="showCreate = true">现在开一场</button>
    </view>

    <view v-else class="meal-list">
      <MealCard v-for="item in formattedUpcoming" :key="item.id" :meal="item" @open="openMeal" />
    </view>

    <button v-if="formattedUpcoming.length" class="cta" @tap="showCreate = true"><Icon icon="Plus" :size="16" /><text>开饭局</text></button>

    <view v-if="formattedUpcoming.length" class="footer">
      <text @tap="goMeals">查看全部饭局</text>
      <text>{{ currentMonth }}月</text>
    </view>

    <view v-if="error && formattedUpcoming.length" class="inline-error">
      <text>{{ error }}</text>
      <button @tap="load">重试</button>
    </view>

    <AppTabBar active="home" />

    <view v-if="showCreate" class="modal-mask" @tap.self="closeCreate">
      <view class="sheet create-sheet">
        <view class="sheet-head">
          <view><text class="section-title">开饭局</text><text class="subtle">点菜和主厨认领会在饭局中分别进行</text></view>
          <button class="close" @tap="closeCreate"><Icon icon="X" :size="18" /></button>
        </view>
        <view class="types">
          <button v-for="(label, key) in types" :key="key" class="chip" :class="{ on: form.meal_type === key }" @tap="form.meal_type = key">{{ label }}</button>
        </view>
        <view class="form-group">
          <text class="label">标题（可选）</text>
          <input v-model="form.title" class="input" placeholder="例如：周末聚餐" />
        </view>
        <view class="time-grid">
          <view>
            <text class="label">日期</text>
            <picker mode="date" :value="form.date" @change="form.date = $event.detail.value">
              <view class="input picker">{{ form.date }}</view>
            </picker>
          </view>
          <view>
            <text class="label">用餐时间</text>
            <picker mode="time" :value="form.dining_time" @change="form.dining_time = $event.detail.value">
              <view class="input picker">{{ form.dining_time }}</view>
            </picker>
          </view>
        </view>
        <view class="form-group deadline">
          <text class="label">点菜截止</text>
          <picker mode="time" :value="form.deadline" @change="form.deadline = $event.detail.value">
            <view class="input picker">{{ form.deadline }}</view>
          </picker>
        </view>
        <button class="btn block" :disabled="createPending" @tap="create">
          {{ createPending ? '创建中...' : '确认开饭局' }}
        </button>
      </view>
    </view>
  </view>
</template>

<script setup lang="js">
import { computed, onActivated, onMounted, reactive, ref } from 'vue'
import Icon from '../../components/Icons.vue'
import AppTabBar from '../../components/AppTabBar.vue'
import MealCard from '../../components/MealCard.vue'
import { bootstrap, currentUser, request, run } from '../../api/client'
import { localDateKey, sortMealsByDiningTime, validateMealDraft } from '../../utils/app'

const settings = ref({}), me = ref(currentUser()), showCreate = ref(false)
const loading = ref(false), error = ref(''), createPending = ref(false)
const types = { breakfast: '早餐', lunch: '午餐', dinner: '晚餐' }
const form = reactive({ meal_type: 'dinner', date: localDateKey(), dining_time: '18:30', deadline: '16:30', title: '' })
const meals = ref([])

const now = new Date()
const currentMonth = computed(() => now.getMonth() + 1)

const formattedUpcoming = computed(() => {
  return sortMealsByDiningTime(
    meals.value.filter(item => item && item.status !== 'cancelled' && (item.status !== 'done' || item.date === localDateKey()))
  ).slice(0, 5)
})

async function load() {
  loading.value = true; error.value = ''
  try {
    const [bootstrapData, loadedMeals] = await Promise.all([bootstrap(), request('/api/meals')])
    settings.value = bootstrapData?.settings || {}; meals.value = Array.isArray(loadedMeals) ? loadedMeals : []
  } catch (loadError) { error.value = loadError?.message || '饭局加载失败' }
  finally { loading.value = false }
}

function openMeal(mealId) { uni.navigateTo({ url: `/pages/meal-detail/index?id=${mealId}` }) }
function goMeals() { uni.reLaunch({ url: '/pages/meals/index' }) }
function closeCreate() { if (!createPending.value) showCreate.value = false }

async function create() {
  if (createPending.value) return
  const validation = validateMealDraft(form)
  if (validation) return uni.showToast({ title: validation, icon: 'none' })
  createPending.value = true
  try {
    const mealId = await run(async () => { const id = await request('/api/meals', { method: 'POST', data: { ...form } }); return typeof id === 'string' && id.trim() ? id : null }, '饭局已创建')
    if (mealId) { showCreate.value = false; uni.navigateTo({ url: `/pages/meal-detail/index?id=${mealId}` }) }
  } catch {} finally { createPending.value = false }
}

onMounted(load); onActivated(load)
</script>

<style scoped>
@keyframes heroReveal {
  from { opacity: 0; transform: translateY(12rpx); }
  to { opacity: 1; transform: translateY(0); }
}
@keyframes mealSlideIn {
  from { opacity: 0; transform: translateY(16rpx); }
  to { opacity: 1; transform: translateY(0); }
}

.hero {
  padding: 64rpx 24rpx 56rpx;
  background: var(--palette-hero-900);
  color: var(--palette-neutral-0);
  border-radius: 0 0 32rpx 32rpx;
  animation: heroReveal 0.6s ease-out both;
}
.family {
  margin-bottom: 16rpx;
  color: var(--theme-hero-text-muted);
  font-size: 22rpx;
  font-weight: 500;
  letter-spacing: 2rpx;
}
.greeting {
  margin: 0;
  color: var(--palette-neutral-0);
  font-family: "Songti SC", "STSong", "Noto Serif CJK SC", serif;
  font-size: 56rpx;
  font-weight: 700;
  line-height: 1.15;
  letter-spacing: 0;
}
.prompt {
  margin-top: 20rpx;
  color: var(--theme-hero-text-subtle);
  font-size: 26rpx;
  line-height: 1.5;
}
.amber-accent {
  margin-top: 22rpx;
  width: 40rpx;
  height: 6rpx;
  background: var(--palette-amber-500);
  border-radius: 3rpx;
}

.section-title {
  display: block;
  padding: 40rpx 0 8rpx;
  color: var(--palette-ink-900);
  font-size: 32rpx;
  font-weight: 650;
  line-height: 1.3;
}

.meal-list {
  margin: 8rpx 0 0;
}
.meal-list :deep(.meal-row):first-child {
  border-top: 1px solid var(--palette-line-200);
  animation: mealSlideIn 0.5s ease-out both;
}
.meal-list :deep(.meal-row) { animation: mealSlideIn 0.5s ease-out both; }
.meal-list :deep(.meal-row:nth-child(2)) { animation-delay: 0.08s; }
.meal-list :deep(.meal-row:nth-child(3)) { animation-delay: 0.16s; }
.meal-list :deep(.meal-row:nth-child(4)) { animation-delay: 0.24s; }
.meal-list :deep(.meal-row:nth-child(5)) { animation-delay: 0.32s; }
.meal-list :deep(.meal-row:nth-child(6)) { animation-delay: 0.40s; }

.cta {
  display: flex;
  min-height: 64rpx;
  margin: 28rpx 0;
  padding: 0 24rpx;
  align-items: center;
  justify-content: center;
  gap: 6rpx;
  border: 0;
  border-radius: 10rpx;
  background: var(--palette-amber-500);
  color: var(--palette-cream-50);
  font-size: 24rpx;
  font-weight: 700;
  line-height: 1;
}
.cta text { color: var(--palette-cream-50); }

.footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 24rpx 0 40rpx;
  font-size: 22rpx;
  color: var(--palette-moss-600);
}
.footer text {
  background: none;
  border: 0;
  font-size: inherit;
  color: var(--palette-moss-600);
  cursor: pointer;
}

.state { padding: 64rpx 0; text-align: center; color: var(--palette-amber-500); font-size: 27rpx; }
.state.panel { padding: 64rpx 0; }
.empty-line button {
  min-height: 64rpx;
  margin-top: 16rpx;
  background: transparent;
  color: var(--palette-amber-500);
  font-size: 24rpx;
}
.inline-error {
  display: flex;
  margin: 24rpx 0 0;
  align-items: center;
  justify-content: space-between;
  color: var(--palette-danger-600);
  font-size: 23rpx;
}
.inline-error button {
  background: transparent;
  color: var(--palette-danger-600);
  font-size: 24rpx;
}

.create-sheet { width: 100%; padding: 40rpx 40rpx calc(var(--space-6) + env(safe-area-inset-bottom)); }
.sheet-head { display: flex; align-items: flex-start; justify-content: space-between; margin-bottom: var(--space-6); }
.sheet-head > view { display: flex; flex-direction: column; }
.close {
  display: flex; width: 56rpx; height: 56rpx; min-height: 56rpx; padding: 0;
  align-items: center; justify-content: center; border-radius: 50%;
  background: var(--palette-control-subtle); color: var(--palette-text-primary); border: 0;
}
.types { display: flex; margin: 28rpx 0; gap: 12rpx; }
.time-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20rpx; }
.form-group { margin-bottom: var(--space-5); }
.deadline { margin-top: 24rpx; }
.picker { display: flex; align-items: center; }

@media (min-width: 700px) {
  .hero { padding: 80rpx 24rpx; }
  .greeting { font-size: 64rpx; }
  .section-title, .meal-list, .cta, .footer, .inline-error { padding-left: 0; padding-right: 0; margin-left: 0; margin-right: 0; }
  .meal-list { margin-left: 0; }
  .page { max-width: 880px; margin: 0 auto; }
}
@media (min-width: 1024px) {
  .page.page-wide { max-width: 1040px; }
}

@media (hover: hover) { button:hover { filter: brightness(.97); } }
button:focus-visible, input:focus-visible, textarea:focus-visible { outline: 2px solid var(--palette-amber-500); outline-offset: 3px; }
/* #ifndef MP-WEIXIN */
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after { animation-duration: .01ms !important; animation-delay: 0s !important; transition-duration: .01ms !important; }
}
/* #endif */

.section-title, .cta, .footer, .inline-error, .sheet-head, .types, .time-grid { flex-direction: row; }
</style>
