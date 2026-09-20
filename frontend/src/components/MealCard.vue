<template>
  <!-- 聚光大卡模式：用于首页"下一顿" -->
  <view v-if="variant === 'spotlight'" class="spotlight" @tap="open">
    <view class="spot-head">
      <text class="spot-tag">{{ timeOfDay }} · {{ typeLabel }}</text>
      <text class="spot-status">{{ statusLabel }}</text>
    </view>
    <view class="spot-time">
      <text class="spot-clock">{{ timeLabel }}</text>
      <text class="spot-title">{{ title }}</text>
    </view>
    <view class="spot-chef">
      <view class="chef-dot" aria-hidden="true">{{ firstChar }}</view>
      <text><text class="chef-name">{{ cookName }}</text> 掌勺 · {{ participantCount }} 人点菜 · 已选 {{ dishCount }} 道</text>
    </view>
    <view v-if="dishes.length" class="dishes">
      <text v-for="(dish, i) in displayDishes" :key="i" class="dish">{{ dish }}</text>
      <text v-if="dishes.length > 3" class="dish more">+{{ dishes.length - 3 }}</text>
    </view>
  </view>

  <!-- 议程行模式：默认，用于列表 -->
  <view v-else class="agenda-row" @tap="open">
    <view class="date-stub">
      <text class="d">{{ dateInfo.num }}</text>
      <text class="w">{{ dateInfo.day }}</text>
    </view>
    <view class="agenda-main">
      <text class="t">{{ title }}</text>
      <text class="m">{{ metaText }}</text>
    </view>
    <view class="agenda-tail">
      <text class="clock">{{ timeLabel }}</text>
      <text class="pill" :class="meal?.status === 'ordering' ? 'open' : 'plan'">{{ statusLabel }}</text>
    </view>
  </view>
</template>

<script setup lang="js">
import { computed } from 'vue'

const props = defineProps({
  meal: { type: Object, default: () => ({}) },
  variant: { type: String, default: 'agenda' }, // 'agenda' | 'spotlight'
})

const emit = defineEmits(['open'])

const mealTypes = { breakfast: '早餐', lunch: '午餐', dinner: '晚餐' }
const mealStatuses = { ordering: '点菜中', cooking: '做饭中', done: '已完成', cancelled: '已取消' }

// 基础数据
const title = computed(() => props.meal?.title || mealTypes[props.meal?.meal_type] || '饭局')
const typeLabel = computed(() => mealTypes[props.meal?.meal_type] || '饭局')
const statusLabel = computed(() => mealStatuses[props.meal?.status] || '')
const participantCount = computed(() => props.meal?.participant_count || 0)
const cookName = computed(() => props.meal?.cook?.name || '暂无主厨')
const firstChar = computed(() => cookName.value.charAt(0) || '?')
const timeOfDay = computed(() => {
  const t = props.meal?.meal_type
  if (t === 'breakfast') return '早餐'
  if (t === 'lunch') return '午餐'
  if (t === 'dinner') return '晚餐'
  return '饭局'
})

// 时间格式化
const timeLabel = computed(() => {
  if (!props.meal?.dining_time) return '--:--'
  const timestamp = Number(props.meal.dining_time)
  if (!Number.isFinite(timestamp)) return '--:--'
  const date = new Date(timestamp * 1000)
  if (Number.isNaN(date.getTime())) return '--:--'
  return `${String(date.getUTCHours()).padStart(2, '0')}:${String(date.getUTCMinutes()).padStart(2, '0')}`
})

// 日期信息
const dayNames = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']
const localDateKey = (value = new Date()) => {
  const y = value.getFullYear()
  const m = String(value.getMonth() + 1).padStart(2, '0')
  const d = String(value.getDate()).padStart(2, '0')
  return `${y}-${m}-${d}`
}

const dateInfo = computed(() => {
  if (typeof props.meal?.date === 'string' && /^\d{4}-\d{2}-\d{2}$/.test(props.meal.date)) {
    const d = new Date(...props.meal.date.split('-').map(Number))
    const today = new Date()
    const key = localDateKey(d)
    let dayStr = dayNames[d.getDay()]
    if (key === localDateKey(today)) dayStr = '今天'
    else if (key === localDateKey(new Date(today.getTime() + 86400000))) dayStr = '明天'
    return { num: String(d.getDate()), day: dayStr }
  }
  return { num: '', day: '' }
})

// 议程行 meta 文本
const metaText = computed(() => {
  const count = props.meal?.participant_count || 0
  const deadline = props.meal?.order_deadline
  const deadlineTs = deadline !== undefined && deadline !== null && deadline !== '' ? Number(deadline) : NaN
  if (Number.isFinite(deadlineTs)) {
    const d = new Date(deadlineTs * 1000)
    if (!Number.isNaN(d.getTime())) {
      const hh = String(d.getUTCHours()).padStart(2, '0')
      const mm = String(d.getUTCMinutes()).padStart(2, '0')
      return `${count} 人点菜 · 点菜截止 ${hh}:${mm}`
    }
  }
  return `${count} 人点菜 · 筹备中`
})

// 菜品数据
const dishes = computed(() => {
  const items = props.meal?.dishes
  return Array.isArray(items) ? items.map(d => d.name || d).filter(Boolean) : []
})
const dishCount = computed(() => dishes.value.length)
const displayDishes = computed(() => dishes.value.slice(0, 3))

function open() {
  if (typeof props.meal?.id === 'string' && props.meal.id) emit('open', props.meal.id)
}
</script>

<style scoped>
/* ========== 聚光大卡样式（spotlight） ========== */
.spotlight {
  margin: 20rpx 0;
  background: #FFFFFF;
  border: 1px solid #EFE5D8;
  border-radius: 56rpx;
  padding: 48rpx;
  box-shadow: 0 24rpx 64rpx rgba(90, 60, 30, 0.07);
  display: flex;
  flex-direction: column;
}
.spot-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20rpx;
  flex-direction: row;
}
.spot-tag {
  display: inline-flex;
  align-items: center;
  gap: 12rpx;
  font-size: 26rpx;
  font-weight: 700;
  color: #D9482B;
  background: rgba(217, 72, 43, 0.09);
  padding: 10rpx 24rpx;
  border-radius: 1998rpx;
}
.spot-tag::before {
  content: "";
  width: 12rpx;
  height: 12rpx;
  border-radius: 50%;
  background: #D9482B;
}
.spot-status {
  font-size: 24rpx;
  color: #8B7F70;
}
.spot-time {
  display: flex;
  align-items: baseline;
  gap: 28rpx;
  flex-direction: row;
}
.spot-clock {
  font-size: 128rpx;
  font-weight: 800;
  letter-spacing: -4rpx;
  line-height: 1;
  font-variant-numeric: tabular-nums;
  color: #27211A;
}
.spot-title {
  font-size: 36rpx;
  font-weight: 700;
  line-height: 1.35;
  color: #27211A;
  max-width: 360rpx;
}
.spot-chef {
  display: flex;
  align-items: center;
  gap: 16rpx;
  margin-top: 20rpx;
  flex-direction: row;
}
.chef-dot {
  width: 56rpx;
  height: 56rpx;
  border-radius: 50%;
  background: #F3C64B;
  color: #6B4A00;
  font-size: 24rpx;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
}
.spot-chef text { font-size: 26rpx; color: #8B7F70; }
.chef-name { color: #27211A; font-weight: 600; }

.dishes {
  display: flex;
  flex-wrap: wrap;
  gap: 16rpx;
  margin-top: 32rpx;
}
.dish {
  font-size: 26rpx;
  color: #27211A;
  background: #FAF7F1;
  border: 1px solid #EFE5D8;
  padding: 12rpx 24rpx;
  border-radius: 1998rpx;
}
.dish.more {
  color: #8B7F70;
  border-style: dashed;
}

/* ========== 议程行样式（agenda） ========== */
.agenda-row {
  display: flex;
  align-items: center;
  gap: 32rpx;
  width: 100%;
  padding: 26rpx 30rpx;
  background: none;
  border: 0;
  border-bottom: 1px solid #EFE5D8;
  text-align: left;
  cursor: pointer;
  flex-direction: row;
}
.agenda-row:last-child { border-bottom: 0; }
.agenda-row:active { background: #FDFBF7; }

.date-stub {
  padding: 0 10rpx;
  text-align: center;
  flex-shrink: 0;
}
.date-stub .d {
  display: block;
  font-size: 48rpx;
  font-weight: 800;
  line-height: 1.1;
  font-variant-numeric: tabular-nums;
  color: #27211A;
}
.date-stub .w {
  display: block;
  font-size: 22rpx;
  color: #8B7F70;
  margin-top: 4rpx;
}
.agenda-main { flex: 1; min-width: 0; display: flex; flex-direction: column; }
.agenda-main .t {
  display: block;
  font-size: 30rpx;
  font-weight: 650;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  color: #27211A;
}
.agenda-main .m {
  display: block;
  font-size: 24rpx;
  color: #8B7F70;
  margin-top: 6rpx;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.agenda-tail { flex-shrink: 0; text-align: right; }
.agenda-tail .clock {
  font-size: 30rpx;
  font-weight: 700;
  font-variant-numeric: tabular-nums;
  color: #27211A;
  padding-right: 8rpx;
}
.pill {
  display: inline-block;
  margin-top: 8rpx;
  font-size: 22rpx;
  padding: 6rpx 20rpx;
  border-radius: 1998rpx;
}
.pill.open { color: #D9482B; background: rgba(217, 72, 43, 0.09); }
.pill.plan { color: #8B7F70; background: #FAF7F1; }
</style>
