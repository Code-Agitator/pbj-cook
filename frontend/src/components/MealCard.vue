<template>
  <view class="meal-row" :class="{ compact }" @tap="open">
    <view class="meal-date">
      <text class="date-num">{{ dateInfo.num }}</text>
      <text class="date-day">{{ dateInfo.day }}</text>
    </view>
    <view class="meal-main">
      <view class="title-line"><text class="meal-title">{{ data.title }}</text></view>
      <text class="meal-meta">{{ data.participantCount }} 人点菜<template v-if="data.cookName"> · {{ data.cookName }}掌勺</template><template v-else> · 无人掌勺</template></text>
    </view>
    <view class="row-tail"><StatusBadge :status="props.meal?.status" /><Icon icon="ChevronRight" :size="18" /></view>
  </view>
</template>

<script setup lang="js">
import { computed } from 'vue'
import Icon from './Icons.vue'
import StatusBadge from './StatusBadge.vue'
import { mealCardData } from '../utils/app'
const props = defineProps({ meal: { type: Object, default: () => ({}) }, compact: { type: Boolean, default: false } })
const emit = defineEmits(['open'])
const data = computed(() => mealCardData(props.meal))
const dayNames = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']
const dateInfo = computed(() => {
  if (typeof props.meal?.date === 'string' && /^\d{4}-\d{2}-\d{2}$/.test(props.meal.date)) {
    const d = new Date(...props.meal.date.split('-').map(Number))
    return { num: String(d.getDate()), day: dayNames[d.getDay()] }
  }
  return { num: '', day: '' }
})
function open() { if (typeof props.meal?.id === 'string' && props.meal.id) emit('open', props.meal.id) }
</script>

<style scoped>
.meal-row{display:flex;flex-direction:row;align-items:center;padding:24rpx 0;border-bottom:1px solid var(--palette-line-200)}
.meal-date{display:flex;flex-direction:column;align-items:center;width:72rpx;margin-right:24rpx;flex-shrink:0}
.date-num{color:var(--palette-amber-500);font-size:28rpx;font-weight:700;line-height:1.1}
.date-day{margin-top:4rpx;color:var(--palette-moss-600);font-size:16rpx;line-height:1.2}
.meal-main{display:flex;min-width:0;flex-direction:column;flex:1}
.title-line{display:flex;min-width:0;align-items:center;justify-content:flex-start}
.meal-title{overflow:hidden;color:var(--palette-ink-900);font-size:28rpx;font-weight:650;line-height:1.3;text-overflow:ellipsis;white-space:nowrap;text-align:left}
.meal-meta{margin-top:4rpx;overflow:hidden;color:var(--palette-moss-600);font-size:20rpx;line-height:1.4;text-overflow:ellipsis;white-space:nowrap;text-align:left}
.row-tail{display:flex;align-items:center;color:var(--palette-moss-600);flex-shrink:0;margin-left:8rpx}.meal-row.compact{padding:18rpx 0;border-width:0 0 1px;background:transparent;box-shadow:none}
.meal-row.compact .meal-date{width:72rpx;margin-right:24rpx}
.meal-main{flex-direction:column}
</style>
