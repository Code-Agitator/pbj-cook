<template>
  <view class="page">
    <PageHeader title="贡献墙" subtitle="谁在为这个家下厨与张罗"/>
    <view v-if="loading && !members.length" class="card state">正在加载贡献记录…</view>
    <view v-else-if="error && !members.length" class="card state"><text>{{error}}</text><button class="btn block" @tap="load">重试</button></view>
    <view v-else-if="!members.length" class="card empty">饭局完成后，这里会长出第一片绿叶</view>
    <view v-else class="members">
      <view v-for="m in members" :key="m.id" class="card member">
        <view class="row">
          <Avatar :name="m.name" :src="assetUrl(m.avatar_path)" :size="88"/>
          <view class="meta">
            <text class="name">{{m.name}}</text>
            <text class="subtle">♨ 做饭 {{m.cook_total || 0}} 次　🍴 点菜 {{m.order_total || 0}} 次</text>
            <text v-if="m.streak" class="streak">连续 {{m.streak}} 天</text>
          </view>
        </view>
        <view class="heat">
          <text class="heat-label">做饭</text>
          <view class="squares">
            <view v-for="(cls, i) in heatClasses(m.cook_by_date, start)" :key="'c'+i" class="square" :class="cls"/>
          </view>
        </view>
        <view class="heat">
          <text class="heat-label">点菜</text>
          <view class="squares">
            <view v-for="(cls, i) in heatClasses(m.order_by_date, start)" :key="'o'+i" class="square" :class="cls"/>
          </view>
        </view>
      </view>
      <view v-if="error" class="card state"><text>{{error}}</text><button class="btn block" @tap="load">重试</button></view>
    </view>
    <AppTabBar active="wall"/>
  </view>
</template>
<script>
import AppTabBar from '../../components/AppTabBar.vue'
import PageHeader from '../../components/PageHeader.vue'
import Avatar from '../../components/Avatar.vue'
import { assetUrl, request } from '../../api/client'
import { heatmapDateKey } from '../../utils/app'

export default {
  components: { AppTabBar, PageHeader, Avatar },
  data() {
    return { members: [], start: '', loading: false, error: '' }
  },
  onShow() { this.load() },
  methods: {
    assetUrl(path) { return assetUrl(path) },
    heatClasses(data, start) {
      const result = []
      for (let i = 0; i < 112; i++) {
        let key = ''
        try { key = heatmapDateKey(start, i) } catch (e) {}
        const n = key && data && typeof data === 'object' ? Number(data[key]) || 0 : 0
        result.push(n ? 'l' + Math.min(n, 4) : '')
      }
      return result
    },
    async load() {
      if (this.loading) return
      this.loading = true
      this.error = ''
      try {
        const d = await request('/api/contributions')
        this.members = Array.isArray(d?.members) ? d.members : []
        this.start = typeof d?.start === 'string' ? d.start : ''
      } catch (e) {
        this.error = e?.message || '贡献记录加载失败'
      } finally {
        this.loading = false
      }
    }
  }
}
</script>
<style scoped>.members{display:flex;flex-direction:column}.member{padding:28rpx;display:flex;flex-direction:row}.meta{display:flex;flex-direction:column;margin-left:20rpx}.name{font-size:32rpx;font-weight:750}.streak{color:#c45320;font-size:23rpx}.heat{margin-top:28rpx}.heat-label{display:block;margin-bottom:12rpx;color:#59685f;font-size:25rpx}.squares{display:flex;flex-wrap:wrap;overflow:hidden}.square{width:18rpx;height:18rpx;margin:3rpx;border-radius:5rpx;background:#e8ebe8}.square.l1{background:#cae8d3}.square.l2{background:#9cd1ad}.square.l3{background:#68b985}.square.l4{background:#37985c}.state{padding:32rpx;text-align:center}.state .btn{margin-top:24rpx}</style>
