<template>
  <view class="meal card" @tap="open">
    <view class="meal-emoji">{{ data.emoji }}</view>
    <view class="meal-main">
      <view class="row meal-title"><text>{{ data.title }}</text><text v-if="meal && meal.is_auto" class="badge">自动</text></view>
      <text class="subtle">{{ data.dateLabel }} {{ data.timeLabel }} · {{ data.participantCount }} 人点了</text>
      <text v-if="data.cookName" class="cook">♨ {{ data.cookName }}掌勺</text>
    </view>
    <text class="badge">{{ data.status }}</text>
  </view>
</template>
<script>
import { mealCardData } from '../utils/app'

export default {
  name: 'MealCard',
  props: { meal: { type: Object, default: function() { return {} } } },
  computed: {
    data() { return mealCardData(this.meal) }
  },
  methods: {
    open() {
      if (typeof (this.meal && this.meal.id) === 'string' && this.meal.id) {
        this.$emit('open', this.meal.id)
      }
    }
  }
}
</script>
<style scoped>
.meal { min-height: 150rpx; padding: 28rpx; display:flex; flex-direction: row; align-items:center; }.meal-emoji { width:92rpx;height:92rpx;border-radius:28rpx;background:#e7f4e9;display:flex;flex-direction: row;align-items:center;justify-content:center;font-size:42rpx; }.meal-main { flex:1;display:flex;flex-direction:column; }.meal-title { display: flex; flex-direction: row; font-size:31rpx;font-weight:750; }.cook { color:#43a367;font-size:24rpx; }
</style>
