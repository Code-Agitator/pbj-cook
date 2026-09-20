<template>
  <view class="back-btn" @tap="goBack">
    <text class="back-arrow">‹</text>
    <text class="back-label">{{ label }}</text>
  </view>
</template>

<script setup lang="js">
const props = defineProps({
  label: { type: String, default: '返回' },
  fallbackUrl: { type: String, default: '' },
})

function goBack() {
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
.back-btn {
  display: inline-flex;
  align-items: center;
  gap: 8rpx;
  padding: 12rpx 32rpx;
  border-radius: 999px;
  background: #FFFFFF;
  box-shadow: 0 4rpx 16rpx rgba(39, 33, 26, 0.12);
  flex-direction: row;
}

.back-btn:active {
  transform: scale(0.97);
  box-shadow: 0 2rpx 8rpx rgba(39, 33, 26, 0.1);
}

.back-arrow {
  font-size: 44rpx;
  font-weight: 700;
  color: var(--theme-text-primary, #27211A);
  line-height: 1;
}

.back-label {
  font-size: 32rpx;
  font-weight: 600;
  color: var(--theme-text-primary, #27211A);
}
</style>
