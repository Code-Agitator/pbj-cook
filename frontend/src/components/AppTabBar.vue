<template>
  <view class="tab-wrap">
    <view class="tabbar">
      <view class="slide-bg" :style="slideStyle" />
      <view v-for="item in tabs" :key="item.path" class="tab" :class="{ active: active === item.key }" @tap="go(item)">
        <view class="tab-icon">
          <Icon :icon="item.icon" :size="22"/>
        </view>
      </view>
    </view>
  </view>
</template>
<script setup lang="js">
import { computed,onMounted } from 'vue'
import Icon from './Icons.vue'

const props = defineProps({active: {type: String, default: ''}})
const tabs = [
  {key: 'home', label: '首页', path: '/pages/home/index', icon: 'Home'},
  {key: 'meals', label: '饭局', path: '/pages/meals/index', icon: 'UtensilsCrossed'},
  {key: 'wall', label: '贡献', path: '/pages/wall/index', icon: 'Sprout'},
  {key: 'me', label: '我的', path: '/pages/me/index', icon: 'UserRound'}
]
onMounted(()=>{
  uni.hideTabBar({ fail: () => {} })
})
const slideStyle = computed(() => {
  const index = tabs.findIndex(t => t.key === props.active)
  const left = index >= 0 ? index * 88 : 0
  return { transform: `translateX(${left}rpx)` }
})

function go(item) {
  if (props.active !== item.key) uni.switchTab({url: item.path})
}
</script>
<style scoped>
.tab-wrap {
  position: fixed;
  z-index: 50;
  left: 50%;
  bottom: calc(32rpx + env(safe-area-inset-bottom));
  transform: translateX(-50%);
  display: flex;
  justify-content: center;
  padding: 8rpx;
  border-radius: 28rpx;
  background: rgba(235, 228, 215, .92);
  box-shadow:
    0 16rpx 40rpx rgba(25, 34, 28, .12),
    0 2rpx 6rpx rgba(25, 34, 28, .06),
    inset 0 1px 0 rgba(255, 255, 255, .4);
  backdrop-filter: blur(20px)
}

.tabbar {
  position: relative;
  width: auto;
  display: flex;
  align-items: center;
  gap: 0
}

.slide-bg {
  position: absolute;
  top: 50%;
  margin-top: -32rpx;
  width: 88rpx;
  height: 64rpx;
  border-radius: 22rpx;
  background: rgba(255, 255, 255, .9);
  box-shadow:
    0 8rpx 24rpx rgba(25, 34, 28, .15),
    0 2rpx 6rpx rgba(25, 34, 28, .08);
  transition: transform .5s cubic-bezier(.34, 1.56, .64, 1);
  z-index: 0;
  overflow: visible
}

.tab {
  position: relative;
  width: 88rpx;
  height: 64rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  color: rgba(80, 70, 55, .6);
  z-index: 1;
  transition: color .2s ease;
  overflow: visible
}

.tab.active {
  color: var(--theme-text-action)
}

.tab-icon {
  display: flex;
  align-items: center;
  justify-content: center
}

.tab-wrap, .tabbar {
  flex-direction: row;
  overflow: visible
}
</style>
