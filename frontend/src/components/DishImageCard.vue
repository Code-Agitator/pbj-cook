<template>
  <view class="dish-image-card" @tap="emit('open', dish)">
    <image v-if="src" class="dish-image" :src="src" mode="aspectFill" />
    <view v-else class="dish-placeholder">
      <Icon icon="ChefHat" :size="28" />
      <text>暂无图片</text>
    </view>
    <view class="dish-gradient" />
    <view class="dish-copy">
      <text class="dish-name">{{ dish.name || '未命名菜品' }}</text>
      <text v-if="flavorText" class="dish-flavors">{{ flavorText }}</text>
      <text v-if="interestCount > 0" class="dish-interest">{{ interestCount }} 人想吃</text>
    </view>
    <view
      v-if="selectable"
      class="dish-select"
      :class="{ selected }"
      :aria-label="selected ? '取消点菜' : '点这道菜'"
      @tap.stop="emit('toggle', dish.id)"
    >
      <Icon :icon="selected ? 'Check' : 'Plus'" :size="17" />
    </view>
  </view>
</template>

<script setup lang="js">
import { computed } from 'vue'
import Icon from './Icons.vue'

const props = defineProps({
  dish: { type: Object, default: () => ({}) },
  src: { type: String, default: '' },
  selected: { type: Boolean, default: false },
  selectable: { type: Boolean, default: true },
  interestCount: { type: Number, default: 0 }
})

const emit = defineEmits(['open', 'toggle'])

const flavorText = computed(() => {
  const tags = Array.isArray(props.dish?.tags) ? props.dish.tags.filter(Boolean).slice(0, 3) : []
  return tags.join(' / ') || props.dish?.cuisine_name || ''
})
</script>

<style scoped>
.dish-image-card {
  position: relative;
  width: 100%;
  aspect-ratio: 4 / 5;
  overflow: hidden;
  border-radius: 16rpx;
  background: var(--theme-bg-placeholder);
}
.dish-image,
.dish-placeholder,
.dish-gradient { position: absolute; inset: 0; width: 100%; height: 100%; }
.dish-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 10rpx;
  background: var(--theme-bg-placeholder);
  color: var(--theme-text-secondary);
  font-size: 22rpx;
}
.dish-gradient {
  background: var(--theme-image-overlay);
  pointer-events: none;
}
.dish-copy {
  position: absolute;
  right: 22rpx;
  bottom: 22rpx;
  left: 22rpx;
  display: flex;
  flex-direction: column;
  color: var(--theme-image-text);
}
.dish-name { font-size: 31rpx; font-weight: 650; line-height: 1.25; }
.dish-flavors { margin-top: 7rpx; color: var(--theme-image-text-muted); font-size: 21rpx; line-height: 1.35; }
.dish-interest { margin-top: 10rpx; color: var(--theme-image-text); font-size: 22rpx; line-height: 1.35; }
.dish-select {
  position: absolute;
  top: 16rpx;
  right: 16rpx;
  display: flex;
  width: 62rpx;
  height: 62rpx;
  min-height: 62rpx;
  padding: 0;
  align-items: center;
  justify-content: center;
  border: 1px solid var(--theme-image-control-border);
  border-radius: 50%;
  background: var(--theme-image-control);
  color: var(--theme-image-text);
  line-height: 1;
  backdrop-filter: blur(8px);
}
.dish-select.selected { border-color: var(--theme-image-text); background: var(--theme-action-primary); }
</style>
