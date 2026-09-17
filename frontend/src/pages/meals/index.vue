<template><view class="page"><PageHeader title="饭局" subtitle="看看最近吃什么"/><view v-if="loading&&!meals.length" class="card empty">正在加载饭局...</view><view v-else-if="error&&!meals.length" class="card empty"><text>{{error}}</text><button class="btn tonal" @tap="load">重试</button></view><template v-else><view v-if="upcoming.length"><text class="section-title group">进行中</text><view class="list"><MealCard v-for="m in upcoming" :key="m.id" :meal="m" @open="open"/></view></view><view v-if="history.length"><text class="section-title group">历史饭局</text><view class="list"><MealCard v-for="m in history" :key="m.id" :meal="m" @open="open"/></view></view><view v-if="!meals.length" class="card empty">还没有饭局记录</view><view v-if="error&&meals.length" class="card retry"><text>{{error}}</text><button class="btn tonal small" @tap="load">重试</button></view></template><AppTabBar active="meals"/></view></template>
<script>
import AppTabBar from '../../components/AppTabBar.vue'
import MealCard from '../../components/MealCard.vue'
import PageHeader from '../../components/PageHeader.vue'
import { request } from '../../api/client'
import { sortMealsByDiningTime } from '../../utils/app'

export default {
  components: { AppTabBar, MealCard, PageHeader },
  data() {
    return { meals: [], loading: false, error: '' }
  },
  computed: {
    upcoming() { return sortMealsByDiningTime(this.meals.filter(x => ['ordering', 'cooking'].includes(x?.status))) },
    history() { return sortMealsByDiningTime(this.meals.filter(x => ['done', 'cancelled'].includes(x?.status))) }
  },
  onShow() { this.load() },
  methods: {
    async load() {
      this.loading = true
      this.error = ''
      try {
        const result = await request('/api/meals')
        this.meals = Array.isArray(result) ? result : []
      } catch (e) {
        this.error = e?.message || '饭局加载失败'
      } finally {
        this.loading = false
      }
    },
    open(id) { uni.navigateTo({ url: `/pages/meal-detail/index?id=${id}` }) }
  }
}
</script>
<style scoped>.group{display:block;margin:30rpx 0 20rpx}.list{display:flex;flex-direction:column}</style>
