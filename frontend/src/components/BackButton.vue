<template>
  <view class="back" @tap="back">{{ arrow }} {{ label }}</view>
</template>

<script setup lang="js">
const props = defineProps({
  label: { type: String, default: '返回' },
  arrow: { type: String, default: '‹' },
  fallbackUrl: { type: String, default: '' },
})

function back() {
  try {
    if (typeof getCurrentPages === 'function' && getCurrentPages().length > 1) {
      return uni.navigateBack()
    }
  } catch {}
  if (props.fallbackUrl) {
    uni.reLaunch({ url: props.fallbackUrl })
  } else {
    uni.reLaunch({ url: '/pages/home/index' })
  }
}
</script>

<style scoped>
.back {
  display: flex;
  flex-direction: row;
  justify-content: flex-start;
  min-height: 60rpx;
  align-items: center;
  background: transparent;
  border: none;
  color: var(--theme-text-secondary);
  font-size: 32rpx;
}
</style>
