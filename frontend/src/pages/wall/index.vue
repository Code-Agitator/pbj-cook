<template>
  <view class="page">
    <!-- 页面头部 -->
    <PageHeader title="贡献" subtitle="记录每一次掌勺与点菜" />

    <!-- 成员卡片列表 -->
    <view v-if="members.length" class="members">
      <view v-for="member in members" :key="member.id" class="member-card">
        <!-- 成员信息顶部 -->
        <view class="member-top">
          <Avatar :name="member.name" :src="assetUrl(member.avatar_path)" :size="104" class="member-avatar" />
          <view class="member-main">
            <text class="member-name">{{ member.name || '家人' }}</text>
            <view class="totals">
              <text class="total-tag">做饭 {{ member.cook_total || 0 }} 次</text>
              <text class="total-tag">点菜 {{ member.order_total || 0 }} 次</text>
              <text v-if="member.streak" class="total-tag hot">连续 {{ member.streak }} 天</text>
            </view>
          </view>
        </view>

        <!-- 热力图 -->
        <view class="heat">
          <view class="heat-label">
            <span>做饭记录 · 近 16 周</span>
            <span class="legend">少 <i class="legend-square l1" /><i class="legend-square l2" /><i class="legend-square l3" /><i class="legend-square l4" /> 多</span>
          </view>
          <view class="squares">
            <view v-for="(level, index) in heatClasses(member.cook_by_date, start)" :key="'c' + index" class="square" :class="level" />
          </view>
        </view>
      </view>
    </view>

    <!-- 加载中状态 -->
    <view v-else-if="loading" class="loading-state">
      <view class="loading-text">正在加载贡献记录...</view>
    </view>

    <!-- 错误状态 -->
    <view v-else-if="error" class="error-state">
      <view class="error-text">{{ error }}</view>
      <view class="btn tonal" @tap="load">重试</view>
    </view>

    <!-- 空状态 -->
    <view v-else class="empty-state">
      <view class="empty-icon">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" aria-hidden="true"><path d="M12 21V9M12 9c0-4-3-6-7-6 0 5 3 7 7 7M12 13c0-4 3-6 7-6 0 5-3 7-7 7" /></svg>
      </view>
      <view class="empty-text">完成第一场饭局后</view>
      <view class="empty-sub">这里会出现每位成员的记录</view>
    </view>

    <!-- 底部标签栏 -->
    <AppTabBar active="wall" />
  </view>
</template>

<script setup lang="js">
import { onActivated, onMounted, ref } from 'vue'
import AppTabBar from '../../components/AppTabBar.vue'
import Avatar from '../../components/Avatar.vue'
import PageHeader from '../../components/PageHeader.vue'
import { assetUrl, request } from '../../api/client'
import { heatmapDateKey } from '../../utils/app'

const members = ref([])
const start = ref('')
const loading = ref(false)
const error = ref('')

function heatClasses(data, startDate) {
  const result = []
  for (let index = 0; index < 112; index += 1) {
    let key = ''
    try {
      key = heatmapDateKey(startDate, index)
    } catch (e) { /* skip */ }
    const count = key && data && typeof data === 'object' ? Number(data[key]) || 0 : 0
    result.push(count ? `l${Math.min(count, 4)}` : '')
  }
  return result
}

async function load() {
  if (loading.value) return
  loading.value = true
  error.value = ''
  try {
    const data = await request('/api/contributions')
    members.value = Array.isArray(data?.members) ? data.members : []
    start.value = typeof data?.start === 'string' ? data.start : ''
  } catch (loadError) {
    error.value = loadError?.message || '贡献记录加载失败'
  } finally {
    loading.value = false
  }
}

onMounted(load)
onActivated(load)
</script>

<style scoped>
.page {
  min-height: 100vh;
  background: var(--theme-bg-page);
}

/* ---------- 成员卡片列表 ---------- */
.members {
  margin-top: var(--space-5);
  display: flex;
  flex-direction: column;
}

.member-card {
  background: var(--theme-bg-surface);
  margin-bottom: var(--space-4);
  border-radius: 48rpx;
  padding: 40rpx;
  box-shadow: 0 8rpx 24rpx rgba(90, 60, 30, 0.06);
}

.member-top {
  display: flex;
  align-items: center;
  gap: 28rpx;
}

.member-avatar {
  flex-shrink: 0;
}

.member-main {
  flex: 1;
  min-width: 0;
}

.member-name {
  font-size: 34rpx;
  font-weight: 750;
  color: var(--theme-text-primary);
  line-height: 1.3;
}

.totals {
  display: flex;
  flex-wrap: wrap;
  gap: 12rpx;
  margin-top: 12rpx;
}

.total-tag {
  display: inline-flex;
  align-items: center;
  font-size: 22rpx;
  font-weight: 600;
  color: var(--theme-text-tertiary);
  background: var(--theme-bg-page);
  border: 1px solid var(--theme-border-subtle);
  padding: 4rpx 18rpx;
  border-radius: 999rpx;
}

.total-tag.hot {
  color: #D9482B;
  border-color: rgba(217, 72, 43, 0.3);
  background: rgba(217, 72, 43, 0.05);
}

/* ---------- 热力图 ---------- */
.heat {
  margin-top: 36rpx;
}

.heat-label {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  font-size: 22rpx;
  color: var(--theme-text-tertiary);
  margin-bottom: 12rpx;
}

.legend {
  display: flex;
  align-items: center;
  gap: 6rpx;
  font-size: 20rpx;
}

.legend-square {
  width: 18rpx;
  height: 18rpx;
  border-radius: 4rpx;
  display: inline-block;
}

.legend-square.l1 { background: var(--theme-heat-1); }
.legend-square.l2 { background: var(--theme-heat-2); }
.legend-square.l3 { background: var(--theme-heat-3); }
.legend-square.l4 { background: var(--theme-heat-4); }

.squares {
  display: grid;
  grid-template-columns: repeat(16, 1fr);
  gap: 6rpx;
}

.square {
  aspect-ratio: 1;
  border-radius: 6rpx;
  background: var(--theme-heat-0);
  transition: transform 0.15s ease;
}

.square.l1 { background: var(--theme-heat-1); }
.square.l2 { background: var(--theme-heat-2); }
.square.l3 { background: var(--theme-heat-3); }
.square.l4 { background: var(--theme-heat-4); }

/* ---------- 加载状态 ---------- */
.loading-state {
  padding: 120rpx 40rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 24rpx;
}

.loading-text {
  font-size: 26rpx;
  color: var(--theme-text-tertiary);
}

/* ---------- 错误状态 ---------- */
.error-state {
  padding: 80rpx 40rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 24rpx;
}

.error-text {
  font-size: 26rpx;
  color: #D9482B;
  text-align: center;
}

/* ---------- 空状态 ---------- */
.empty-state {
  padding: 120rpx 40rpx 80rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16rpx;
}

.empty-icon {
  width: 120rpx;
  height: 120rpx;
  border-radius: 50%;
  background: var(--theme-heat-1);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 16rpx;
}

.empty-icon svg {
  width: 56rpx;
  height: 56rpx;
  color: #D9482B;
}

.empty-text {
  font-size: 30rpx;
  font-weight: 650;
  color: var(--theme-text-secondary);
}

.empty-sub {
  font-size: 24rpx;
  color: var(--theme-text-tertiary);
}

/* ---------- 按钮样式 ---------- */
.btn {
  display: inline-flex;
  min-height: 80rpx;
  padding: 0 var(--space-5);
  align-items: center;
  justify-content: center;
  border-radius: 16rpx;
  background: var(--theme-action-primary);
  color: var(--theme-action-on-primary);
  font-size: 27rpx;
  font-weight: 600;
  line-height: 1;
  align-self: center;
  box-shadow: 0 2px 8rpx rgba(25, 34, 28, 0.12), 0 1px 2rpx rgba(25, 34, 28, 0.08);
  transition: transform 0.1s ease, box-shadow 0.1s ease, filter 0.15s ease;
  margin-top: 16rpx;
}

.btn::after {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: inherit;
  background: linear-gradient(to bottom, rgba(255, 255, 255, 0.18) 0%, rgba(255, 255, 255, 0) 45%);
  pointer-events: none;
}

.btn:active {
  transform: translateY(2rpx);
  box-shadow: 0 1px 3rpx rgba(25, 34, 28, 0.1), 0 1px 1rpx rgba(25, 34, 28, 0.06);
}

.btn.tonal {
  background: var(--theme-bg-page);
  color: var(--theme-text-primary);
  border: 1px solid var(--theme-border-subtle);
  box-shadow: 0 2px 6rpx rgba(25, 34, 28, 0.06);
}
</style>
