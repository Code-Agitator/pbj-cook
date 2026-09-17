<template>
  <view class="tab-wrap">
    <view class="tabbar">
      <view v-for="item in tabs" :key="item.path" class="tab" :class="{ active: active === item.key }" @tap="go(item)">
        <view class="tab-icon">
          <Icon :icon="item.icon" :size="21" />
        </view>
        <text>{{ item.label }}</text>
      </view>
    </view>
  </view>
</template>

<script>
import Icon from './Icons.vue'

export default {
  name: 'AppTabBar',
  components: { Icon },
  props: { active: String },
  data() {
    return {
      tabs: [
        { key: 'home', label: '首页', path: '/pages/home/index', icon: 'Home' },
        { key: 'meals', label: '饭局', path: '/pages/meals/index', icon: 'UtensilsCrossed' },
        { key: 'dishes', label: '菜品', path: '/pages/dishes/index', icon: 'ChefHat' },
        { key: 'wall', label: '贡献', path: '/pages/wall/index', icon: 'Sprout' },
        { key: 'me', label: '我的', path: '/pages/me/index', icon: 'UserRound' }
      ]
    }
  },
  methods: {
    go(item) { uni.reLaunch({ url: item.path }) }
  }
}
</script>

<style scoped>
.tab-wrap { position: fixed; z-index: 50; left: 0; right: 0; bottom: 0; display: flex; flex-direction: row; justify-content: center; pointer-events: none; padding: 0 22rpx calc(20rpx + env(safe-area-inset-bottom)); }
.tabbar { pointer-events: auto; width: 100%; max-width: 700rpx; display: flex; flex-direction: row; align-items: center; justify-content: space-around; padding: 10rpx; border-radius: 54rpx; background: rgba(233,237,233,.96); box-shadow: 0 14rpx 48rpx rgba(45,61,51,.18); }
.tab { position: relative; width: 112rpx; height: 88rpx; display: flex; flex-direction: column; align-items: center; justify-content: center; border-radius: 44rpx; color: #5e6b63; font-size: 22rpx; }
.tab.active { color: #43a367; background: white; }
.tab-icon { height: 40rpx; }
</style>
