<template>
  <view class="page">
    <PageHeader title="饭局" subtitle="选择饭局，自由点菜" />

    <view v-if="loading && !meals.length" class="state">正在加载饭局...</view>
    <view v-else-if="error && !meals.length" class="state panel">
      <text>{{ error }}</text>
      <view class="btn tonal" @tap="load">重试</view>
    </view>

    <template v-else>
      <!-- 进行中 -->
      <MealList :meals="upcoming" title="进行中" @open="open" />

      <!-- 历史饭局（可折叠 + 懒加载） -->
      <MealList :meals="history" title="历史饭局" :collapsible="true" :collapsed="!historyOpen" :lazy-load="true" :page-size="5" @open="open" @toggle="historyOpen = !historyOpen" />

      <view v-if="!meals.length" class="state">还没有饭局记录</view>
      <view v-if="error && meals.length" class="inline-error">
        <text>{{ error }}</text>
        <view @tap="load">重试</view>
      </view>
    </template>

    <AppTabBar active="meals" />
  </view>
</template>

<script setup lang="js">
import { computed, onActivated, onMounted, ref } from 'vue'
import AppTabBar from '../../components/AppTabBar.vue'
import MealList from '../../components/MealList.vue'
import PageHeader from '../../components/PageHeader.vue'
import { request } from '../../api/client'
import { sortMealsByDiningTime } from '../../utils/app'

const meals = ref([]), loading = ref(false), error = ref('')
const historyOpen = ref(true)

const upcoming = computed(() => sortMealsByDiningTime(meals.value.filter(item => ['ordering', 'cooking'].includes(item?.status))))
const history = computed(() => sortMealsByDiningTime(meals.value.filter(item => ['done', 'cancelled'].includes(item?.status))).reverse())

async function load() {
  loading.value = true
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
  uni.navigateTo({ url: `/pages/meal-detail/index?id=${mealId}` })
}

onMounted(load)
onActivated(load)
</script>

<style scoped>
.page {
  background: var(--theme-bg-page);
}

.state {
  padding: 64rpx 40rpx;
  text-align: center;
  color: #8B7F70;
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
  color: #D9482B;
  font-size: 23rpx;
}
.inline-error view {
  background: transparent;
  color: #D9482B;
  font-size: 24rpx;
  cursor: pointer;
}

@media (min-width: 700px) {
  .page {
    max-width: 880px;
    margin: 0 auto;
    padding-left: 24rpx;
    padding-right: 24rpx;
  }
}

view:focus-visible, input:focus-visible, textarea:focus-visible {
  outline: 2px solid #F3C64B;
  outline-offset: 3px;
}
</style>
