<template>
  <view class="page">
    <!-- 顶部问候 -->
    <header class="top">
      <Avatar :name="me?.name || '家'" :src="assetUrl(me?.avatar_path)" :size="84" />
      <view class="top-text">
        <text class="family">{{ settings.family_name || '我们的家' }}</text>
        <h1 class="greet">你好，{{ me?.name || '家人' }}</h1>
      </view>
    </header>
    <view class="prompt-row">
      <text class="date-chip">{{ dateLabel }}</text>
      <text class="prompt">今天想吃点什么？</text>
    </view>

    <!-- 下一顿聚光大卡 - 使用 MealCard 组件 -->
    <MealCard v-if="spotlightMeal" variant="spotlight" :meal="spotlightMeal" @open="openMeal"/>

    <!-- 接下来：饭局列表（使用 MealList 组件） -->
    <MealList :meals="agendaMeals" title="接下来" @open="openMeal"/>

    <!-- 空状态 -->
    <view v-if="!spotlightMeal && !agendaMeals.length && !loading" class="empty-state">
      <text>{{ error || '还没有临近的饭局' }}</text>
      <view v-if="error" class="btn tonal retry" @tap="load">重试</view>
    </view>
    <view v-if="loading && !formattedUpcoming.length" class="state">正在加载饭局...</view>

    <!-- 主操作按钮 -->
    <AppButton style="margin-top: var(--space-4)" block icon="Plus" @tap="showCreate = true">开饭局</AppButton>

    <!-- 底部链接 -->
    <view class="foot">
      <text @tap="goMeals">查看全部饭局</text>
      <text>{{ currentMonth }}月</text>
    </view>

    <!-- 错误提示 -->
    <view v-if="error && formattedUpcoming.length" class="inline-error">
      <text>{{ error }}</text>
      <text @tap="load">重试</text>
    </view>

    <AppTabBar active="home"/>

    <!-- 开饭局面板 -->
    <BottomSheet v-model="showCreate" @close="closeCreate">
      <view class="sheet-head">
        <view>
          <text class="sheet-title">开饭局</text>
          <text class="sheet-subtitle">点菜和主厨认领会在饭局中分别进行</text>
        </view>
      </view>
      <view class="chips">
        <view v-for="(label, key) in types" :key="key" class="chip" :class="{ on: form.meal_type === key }"
              @tap="form.meal_type = key">{{ label }}
        </view>
      </view>
      <view class="field">
        <text class="label">标题（可选）</text>
        <BaseInput v-model="form.title" placeholder="例如：周末聚餐"/>
      </view>
      <view class="grid3">
        <view class="field">
          <text class="label">日期</text>
          <BaseInput v-model="form.date" mode="date" placeholder="选择日期" prefix-icon="Calendar"/>
        </view>
        <view class="field">
          <text class="label">用餐时间</text>
          <BaseInput v-model="form.dining_time" mode="time" placeholder="选择时间" prefix-icon="Clock"/>
        </view>
        <view class="field">
          <text class="label">点菜截止</text>
          <BaseInput v-model="form.deadline" mode="time" placeholder="选择截止时间" prefix-icon="Clock"/>
        </view>
      </view>
      <AppButton block :loading="createPending" @tap="create">确认开饭局</AppButton>
    </BottomSheet>
  </view>
</template>

<script setup lang="js">
import {computed, onActivated, onMounted, reactive, ref} from 'vue'
import AppTabBar from '../../components/AppTabBar.vue'
import Avatar from '../../components/Avatar.vue'
import BottomSheet from '../../components/BottomSheet.vue'
import MealCard from '../../components/MealCard.vue'
import MealList from '../../components/MealList.vue'
import AppButton from '../../components/AppButton.vue'
import BaseInput from '../../components/BaseInput.vue'
import {assetUrl, bootstrap, currentUser, request, run} from '../../api/client'
import {localDateKey, sortMealsByDiningTime, validateMealDraft} from '../../utils/app'

const settings = ref({}), me = ref(currentUser()), showCreate = ref(false)
const loading = ref(false), error = ref(''), createPending = ref(false)
const types = {breakfast: '早餐', lunch: '午餐', dinner: '晚餐'}
const form = reactive({meal_type: 'dinner', date: localDateKey(), dining_time: '18:30', deadline: '16:30', title: ''})
const meals = ref([])

const now = new Date()
const currentMonth = computed(() => now.getMonth() + 1)

// 计算日期标签
const dateLabel = computed(() => {
  const m = now.getMonth() + 1
  const d = now.getDate()
  const weekdays = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']
  return `${m}月${d}日 ${weekdays[now.getDay()]}`
})

const formattedUpcoming = computed(() => {
  return sortMealsByDiningTime(
      meals.value.filter(item => item && item.status !== 'cancelled' && (item.status !== 'done' || item.date === localDateKey()))
  ).slice(0, 5)
})

// 聚光大卡数据（最近的一顿饭）
const spotlightMeal = computed(() => formattedUpcoming.value[0] || null)
// 议程列表（后面的饭局）
const agendaMeals = computed(() => formattedUpcoming.value.slice(1))

async function load() {
  loading.value = true;
  error.value = ''
  try {
    const [bootstrapData, loadedMeals] = await Promise.all([bootstrap(), request('/api/meals')])
    settings.value = bootstrapData?.settings || {};
    meals.value = Array.isArray(loadedMeals) ? loadedMeals : []
  } catch (loadError) {
    error.value = loadError?.message || '饭局加载失败'
  } finally {
    loading.value = false
  }
}

function openMeal(mealId) {
  uni.navigateTo({url: `/pages/meal-detail/index?id=${mealId}`})
}

function goMeals() {
  uni.reLaunch({url: '/pages/meals/index'})
}

function closeCreate() {
  showCreate.value = false
}

async function create() {
  if (createPending.value) return
  const validation = validateMealDraft(form)
  if (validation) return uni.showToast({title: validation, icon: 'none'})
  createPending.value = true
  try {
    const mealId = await run(async () => {
      const id = await request('/api/meals', {method: 'POST', data: {...form}});
      return typeof id === 'string' && id.trim() ? id : null
    }, '饭局已创建')
    if (mealId) {
      showCreate.value = false;
      setTimeout(() => {
        uni.navigateTo({url: `/pages/meal-detail/index?id=${mealId}`})
      }, 200)
    }
  } catch {
  } finally {
    createPending.value = false
  }
}

onMounted(load);
onActivated(load)
</script>

<style scoped>
/* 瓷 · 设计系统变量 -- 与 login 页面一致 */
.page {
  --card: #FFFFFF;
  --clay: #EFE5D8;
  --ink: #27211A;
  --muted: #8B7F70;
  --tomato: #D9482B;
  --tomato-deep: #B93517;

  background: var(--theme-bg-porcelain, #FAF7F1);
}

/* ---------- 顶部问候 ---------- */
.top {
  display: flex;
  align-items: center;
  gap: 24rpx;
  flex-direction: row;
}

.top-text {
  min-width: 0;
  flex: 1;
}

.family {
  font-size: 24rpx;
  color: var(--muted);
  letter-spacing: 1rpx;
}

.greet {
  font-family: "Songti SC", "STSong", "Noto Serif CJK SC", serif;
  font-size: 40rpx;
  font-weight: 700;
  line-height: 1.3;
  color: var(--ink);
  margin: 0;
}

.date-chip {
  font-size: 24rpx;
  color: var(--muted);
  background: var(--clay);
  border-radius: 1998rpx;
  padding: 12rpx 24rpx;
  white-space: nowrap;
}

.prompt-row {
  display: flex;
  align-items: center;
  gap: 16rpx;
  padding: 12rpx;
}

.prompt {
  font-size: 30rpx;
  color: var(--muted);
}

/* ---------- 主操作 ---------- */
/* AppButton 组件已接管按钮样式 */

.foot {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 36rpx 0;
  font-size: 26rpx;
  flex-direction: row;
}

.foot text {
  color: var(--ink);
  font-weight: 600;
}

.foot text:last-child {
  color: var(--muted);
  font-weight: 400;
}

/* ---------- 空状态 ---------- */
.empty-state {
  padding: 120rpx 48rpx;
  text-align: center;
  color: var(--muted);
  font-size: 28rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 24rpx;
}

.retry {
  min-height: 64rpx;
  padding: 0 32rpx;
  font-size: 26rpx;
}

.state {
  padding: 88rpx 0;
  text-align: center;
  color: var(--muted);
  font-size: 27rpx;
}

.inline-error {
  display: flex;
  margin: 24rpx 48rpx 0;
  align-items: center;
  justify-content: space-between;
  color: var(--tomato);
  font-size: 24rpx;
  flex-direction: row;
}

.inline-error text:last-child {
  color: var(--tomato);
  font-weight: 600;
}

/* ---------- 开饭局面板(内容样式，外壳由 BottomSheet 组件提供) ---------- */
.sheet-head {
  margin-bottom: 12rpx;
}

.sheet-head > view:first-child {
  display: flex;
  flex-direction: column;
}

.sheet-title {
  font-size: 40rpx;
  font-weight: 700;
  color: var(--ink);
}

.sheet-subtitle {
  font-size: 24rpx;
  color: var(--muted);
  margin-top: 6rpx;
}

.sheet-close {
  width: 64rpx;
  height: 64rpx;
  min-height: 64rpx;
  padding: 0;
  border: 0;
  border-radius: 50%;
  background: var(--clay);
  color: var(--ink);
  font-size: 30rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  cursor: pointer;
}

.chips {
  display: flex;
  gap: 20rpx;
  margin: 20rpx 0;
  flex-direction: row;
}

.chip {
  flex: 1;
  padding: 10rpx 0;
  border: 3rpx solid var(--clay);
  border-radius: 28rpx;
  background: var(--card);
  color: var(--muted);
  font-size: 28rpx;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s ease;
  text-align: center;
}

.chip.on {
  border-color: var(--tomato);
  color: var(--tomato);
  background: rgba(217, 72, 43, 0.06);
}

.field {
  margin-bottom: var(--space-4);
}

.field .label {
  display: block;
  font-size: 26rpx;
  font-weight: 600;
  margin-bottom: 14rpx;
  color: var(--ink);
}

.grid2 {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24rpx;
}

.grid3 {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr;
  gap: 20rpx;
}

.grid3 .field {
  width: 100%;
  min-width: 0;
}


/* ---------- 焦点可访问性 ---------- */
:focus-visible {
  outline: 4rpx solid var(--tomato);
  outline-offset: 6rpx;
  border-radius: 12rpx;
}
</style>
