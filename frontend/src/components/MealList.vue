<template>
  <view v-if="meals?.length" class="meal-section">
    <!-- 可选标题区 -->
    <view v-if="title" class="section-head" :class="{ collapsible }" @tap="toggle">
      <text class="section-title">
        {{ title }}
        <text v-if="collapsible" class="arrow">{{ internalCollapsed ? '▼' : '▲' }}</text>
      </text>
      <text v-if="showCount" class="section-count">{{ meals.length }} 场</text>
    </view>

    <!-- 大圆角卡片容器 -->
    <view v-show="!collapsible || !internalCollapsed" class="meal-card-list">
      <MealCard v-for="meal in visibleMeals" :key="meal.id" :meal="meal" @open="onOpen" />
    </view>

    <!-- 懒加载：加载更多 -->
    <view v-if="hasMore" class="load-more" @tap="loadMore">
      <text>{{ loadingMore ? '加载中...' : '加载更多' }}</text>
    </view>
  </view>
</template>

<script setup lang="js">
import { computed, ref, watch } from 'vue'
import MealCard from './MealCard.vue'

const props = defineProps({
  meals: { type: Array, default: () => [] },
  title: { type: String, default: '' },
  showCount: { type: Boolean, default: true },
  collapsible: { type: Boolean, default: false },
  collapsed: { type: Boolean, default: false },
  lazyLoad: { type: Boolean, default: false },
  pageSize: { type: Number, default: 5 },
})

const emit = defineEmits(['open', 'toggle'])

const internalCollapsed = ref(props.collapsed)
const visibleCount = ref(props.pageSize)
const loadingMore = ref(false)

watch(() => props.collapsed, (val) => { internalCollapsed.value = val })

watch(() => props.meals, () => {
  visibleCount.value = props.pageSize
})

const visibleMeals = computed(() => {
  if (!props.lazyLoad) return props.meals
  return props.meals.slice(0, visibleCount.value)
})

const hasMore = computed(() => {
  return props.lazyLoad && visibleCount.value < props.meals.length
})

function loadMore() {
  if (loadingMore.value) return
  loadingMore.value = true
  // 模拟一下异步加载的延迟感
  setTimeout(() => {
    visibleCount.value = Math.min(visibleCount.value + props.pageSize, props.meals.length)
    loadingMore.value = false
  }, 200)
}

function toggle() {
  if (props.collapsible) {
    internalCollapsed.value = !internalCollapsed.value
    emit('toggle', internalCollapsed.value)
  }
}

function onOpen(mealId) {
  emit('open', mealId)
}
</script>

<style scoped>
/* ========== 标题区 ========== */
.section-head.collapsible { cursor: pointer; }

.section-title {
  font-size: 34rpx;
  font-weight: 700;
  color: #27211A;
}
.section-title .arrow {
  font-size: 20rpx;
  margin-left: 12rpx;
}
.section-count {
  font-size: 24rpx;
  color: #8B7F70;
}

/* ========== 大圆角卡片容器 ========== */
.meal-card-list {
  background: #FFFFFF;
  border: 1px solid #EFE5D8;
  border-radius: 48rpx;
  overflow: hidden;
}

/* ========== 加载更多 ========== */
.load-more {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 28rpx;
  margin-top: 20rpx;
  border-radius: 24rpx;
  background: rgba(255, 255, 255, .6);
  border: 1px solid rgba(180, 170, 155, .2);
  cursor: pointer;
  transition: background .15s ease;
}

.load-more:active {
  background: rgba(255, 255, 255, .8);
}

.load-more text {
  font-size: 26rpx;
  font-weight: 600;
  color: rgba(80, 70, 55, .6);
  letter-spacing: 0.5px;
}
</style>
