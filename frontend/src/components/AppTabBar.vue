<template>
  <view class="tab-wrap">
    <view class="tabbar">
      <view v-for="item in tabs" :key="item.path" class="tab" :class="{ active: active === item.key }" @tap="go(item)">
        <view class="tab-icon">
          <Icon :icon="item.icon" :size="22"/>
        </view>
        <text class="tab-text">{{ item.label }}</text>
      </view>
    </view>
  </view>
</template>
<script setup lang="js">
import { onMounted } from 'vue'
import { onShow,onTabItemTap  } from '@dcloudio/uni-app'

import Icon from './Icons.vue'

const props = defineProps({active: {type: String, default: ''}})
const tabs = [
  {key: 'home', label: '首页', path: '/pages/home/index', icon: 'Home'},
  {key: 'meals', label: '饭局', path: '/pages/meals/index', icon: 'UtensilsCrossed'},
  {key: 'wall', label: '贡献', path: '/pages/wall/index', icon: 'Sprout'},
  {key: 'me', label: '我的', path: '/pages/me/index', icon: 'UserRound'}
]

onMounted(() => {
  uni.hideTabBar({ fail: () => {} })
})

onShow(() => {
  uni.hideTabBar({ fail: () => {} })
})
onTabItemTap(()=>{
  uni.hideTabBar({ fail: () => {} })
})

function go(item) {
  if (props.active !== item.key) uni.switchTab({url: item.path})
}
</script>
<style scoped>
/* ============================================================
   在 H5 端 rpx 按屏幕宽度等比换算，宽屏下整体会变大。
   关键尺寸用 min() 封顶，保证超宽屏下物理尺寸不变。
   ============================================================ */
.tab-wrap {
  position: fixed;
  z-index: 50;
  left: 50%;
  bottom: calc(32px + env(safe-area-inset-bottom));
  transform: translateX(-50%);
  display: flex;
  justify-content: center;
  padding: min(14rpx, 7px) min(28rpx, 14px);
  border-radius: 999px;
  background: rgba(255, 255, 255, .85);
  box-shadow:
    0 min(16rpx, 8px) min(40rpx, 20px) rgba(25, 34, 28, .12),
    0 min(2rpx, 1px) min(6rpx, 3px) rgba(25, 34, 28, .06),
    inset 0 1px 0 rgba(255, 255, 255, .4);
  backdrop-filter: blur(20px)
}

.tabbar {
  position: relative;
  width: auto;
  display: flex;
  align-items: center;
  gap: min(8rpx, 4px)
}

/* tab 项 */
.tab {
  position: relative;
  width: min(140rpx, 70px);
  height: min(80rpx, 40px);
  display: flex;
  align-items: center;
  justify-content: center;
  color: rgba(80, 70, 55, .55);
  z-index: 1;
  transition: color .25s ease, transform .35s cubic-bezier(.34, 1.56, .64, 1);
  overflow: visible;
  gap: min(8rpx, 4px);
  padding: 0 min(16rpx, 8px);
  box-sizing: border-box
}

/* 未选中文字：隐藏 */
.tab .tab-text {
  max-width: 0;
  opacity: 0;
  overflow: hidden;
  white-space: nowrap;
  font-size: min(26rpx, 13px);
  font-weight: 600;
  letter-spacing: 0.5px;
  transition: max-width .4s cubic-bezier(.32, .72, 0, 1), opacity .25s ease;
  flex-shrink: 0
}

/* 选中态：文字展开 + 变色 */
.tab.active {
  color: var(--theme-text-action);
  animation: tabPop .35s cubic-bezier(.34, 1.4, .5, 1)
}

/* 选中态白底胶囊 — 用 ::before 跟随 tab 自身宽度 */
.tab.active::before {
  content: '';
  position: absolute;
  z-index: -1;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(255, 255, 255, .92);
  border-radius: 999px;
  box-shadow:
    0 min(8rpx, 4px) min(24rpx, 12px) rgba(25, 34, 28, .13),
    0 min(2rpx, 1px) min(6rpx, 3px) rgba(25, 34, 28, .06);
  animation: capsuleIn .35s cubic-bezier(.34, 1.3, .5, 1)
}

/* 选中文字展开 */
.tab.active .tab-text {
  max-width: min(160rpx, 80px);
  opacity: 1
}

.tab-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0
}

.tab-wrap, .tabbar {
  flex-direction: row;
  overflow: visible
}

@keyframes tabPop {
  0% { transform: scale(0.94); }
  60% { transform: scale(1.04); }
  100% { transform: scale(1); }
}

@keyframes capsuleIn {
  0% { transform: scale(0.85); opacity: 0; }
  100% { transform: scale(1); opacity: 1; }
}
</style>
