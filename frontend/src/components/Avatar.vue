<template>
  <view class="avatar-root" :style="rootStyle">
    <view class="avatar" :style="containerStyle">
      <image v-if="src" :src="src" mode="aspectFill" />
      <text v-else>{{ firstChar }}</text>
    </view>
    <view v-if="$slots.overlay" class="avatar-overlay"><slot name="overlay" /></view>
  </view>
</template>
<script setup lang="js">
import { computed } from 'vue'
const props = defineProps({ name: { type: String, default: '' }, src: { type: String, default: '' }, size: { type: Number, default: 84 }, bgColor: { type: String, default: '' } })
const rootStyle = computed(() => ({ width: `${props.size}rpx`, height: `${props.size}rpx` }))
const containerStyle = computed(() => {
  const style = { width: `${props.size}rpx`, height: `${props.size}rpx`, fontSize: `${props.size * .4}rpx` }
  if (props.bgColor) style.background = props.bgColor
  return style
})
const firstChar = computed(() => props.name ? props.name.slice(0, 1) : '')
</script>
<style scoped>
.avatar-root {
  position: relative;
  flex-shrink: 0;
}
.avatar {
  width: 100%;
  height: 100%;
  position: relative;
  border-radius: 50%;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--theme-action-primary, #E8824A);
  color: #fff;
  font-weight: 700;
}
.avatar image {
  width: 100%;
  height: 100%;
  border-radius: 50%;
}
.avatar-overlay {
  position: absolute;
  top: -18rpx;
  right: -14rpx;
  font-size: 30rpx;
  z-index: 2;
  line-height: 1;
}
</style>
