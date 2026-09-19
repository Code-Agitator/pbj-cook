<template>
  <view class="page">
    <PageHeader title="饭局" subtitle="选择饭局，自由点菜"/>

    <view v-if="loading && !meals.length" class="state">正在加载饭局...</view>
    <view v-else-if="error && !meals.length" class="state panel">
      <text>{{ error }}</text>
      <button class="btn tonal" @tap="load">重试</button>
    </view>

    <template v-else>
      <view class="section">
        <view class="section-head">
          <text class="section-title">进行中</text>
          <text class="section-count">{{ upcoming.length }} 场</text>
        </view>
        <view class="meal-zone">
          <MealCard v-for="item in upcoming" :key="item.id" :meal="item" compact @open="open"/>
        </view>
      </view>

      <view class="section">
        <view class="section-head" @tap="historyOpen = !historyOpen">
          <text class="section-title">历史饭局
            <text class="collapse-arrow">{{ historyOpen ? '▲' : '▼' }}</text>
          </text>
          <text class="section-count">{{ history.length }} 场</text>
        </view>
        <view v-show="historyOpen" class="meal-zone">
          <MealCard v-for="item in history" :key="item.id" :meal="item" compact @open="open"/>
        </view>
      </view>

      <view v-if="!meals.length" class="state">还没有饭局记录</view>
      <view v-if="error && meals.length" class="inline-error">
        <text>{{ error }}</text>
        <button @tap="load">重试</button>
      </view>
    </template>

    <AppTabBar active="meals"/>
  </view>
</template>

<script setup lang="js">
import {computed, onActivated, onMounted, ref} from 'vue'
import AppTabBar from '../../components/AppTabBar.vue'
import MealCard from '../../components/MealCard.vue'
import PageHeader from '../../components/PageHeader.vue'
import {request} from '../../api/client'
import {sortMealsByDiningTime} from '../../utils/app'

const meals = ref([]), loading = ref(false), error = ref('')
const historyOpen = ref(true)

const upcoming = computed(() => sortMealsByDiningTime(meals.value.filter(item => ['ordering', 'cooking'].includes(item?.status))))
const history = computed(() => sortMealsByDiningTime(meals.value.filter(item => ['done', 'cancelled'].includes(item?.status))).reverse())

const formattedUpcoming = computed(() => upcoming.value)
const formattedHistory = computed(() => history.value.slice(0, 5))

async function load() {
  loading.value = true;
  error.value = ''
  try {
    const result = await request('/api/meals')
    meals.value = Array.isArray(result) ? result : []
  } catch (loadError) {
    error.value = loadError?.message || '饭局加载失败'
  } finally {
    loading.value = false
  }
}

function open(mealId) {
  uni.navigateTo({url: `/pages/meal-detail/index?id=${mealId}`})
}

onMounted(load);
onActivated(load)
</script>

<style scoped>
.page {
  padding-top: calc(var(--status-bar-height, 24px) + var(--space-5));
}

.section {
  margin-bottom: 32rpx;
}

.section-head { display: flex; align-items: baseline; justify-content: space-between; padding: 0; }

.section-title {
  font-size: 30rpx;
  font-weight: 500;
  color: var(--palette-ink-900);
}

.section-title .collapse-arrow {
  font-size: 20rpx;
  margin-left: 8rpx;
}

.section-count {
  font-size: 22rpx;
  color: var(--palette-amber-500);
}

.section-head {
  cursor: pointer;
}

.meal-zone { margin-top: 0; }

.state {
  padding: 64rpx 40rpx;
  text-align: center;
  color: var(--palette-amber-500);
  font-size: 27rpx;
}

.state.panel {
  padding: 64rpx 40rpx;
}

.inline-error {
  display: flex;
  margin: 24rpx 40rpx 0;
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

@media (min-width: 700px) {
  .page-header, .section-head, .meal-zone, .inline-error {
    padding-left: 60rpx;
    padding-right: 60rpx;
  }

  .page {
    max-width: 880px;
    margin: 0 auto;
    padding-left: 24rpx;
    padding-right: 24rpx;
  }
}

@media (min-width: 1024px) {
  .page {
    padding-left: 12rpx;
    padding-right: 12rpx;
  }
}

@media (hover: hover) {
  button:hover {
    filter: brightness(.97);
  }
}

button:focus-visible, input:focus-visible, textarea:focus-visible {
  outline: 2px solid var(--palette-amber-500);
  outline-offset: 3px;
}

/* #ifndef MP-WEIXIN */
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: .01ms !important;
    animation-delay: 0s !important;
    transition-duration: .01ms !important;
  }
}
/* #endif */
</style>
