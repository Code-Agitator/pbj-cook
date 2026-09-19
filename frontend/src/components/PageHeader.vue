<template>
  <view class="page-header">
    <view class="page-title">{{ title }}</view>
    <text v-if="subtitle" class="page-subtitle">{{ subtitle }}</text>
    <view class="header-rule"></view>
  </view>
</template>
<script setup lang="js">
defineProps({ title: { type: String, default: '' }, subtitle: { type: String, default: '' } })
</script>
<style scoped>
.page-header {
  padding: 24rpx 0 32rpx;
}
.page-title {
  font-size: 40rpx;
  font-weight: 700;
  color: var(--palette-ink-900);
}
.page-subtitle {
  display: block;
  font-size: 24rpx;
  color: var(--palette-moss-600);
  margin-top: 8rpx;
  line-height: 1.5;
}
.header-rule {
  height: 6rpx;
  background: var(--palette-amber-500);
  margin-top: 24rpx;
  border-radius: 4rpx;
  width: 60rpx;
}
</style>
