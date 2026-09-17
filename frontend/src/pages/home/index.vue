<template>
  <view class="page">
    <view class="hero"><text class="family">{{ settings.family_name }}</text><text class="hello">你好，{{ me && me.name }}</text><text class="subtle">今天想吃点什么？</text></view>
    <view class="row between section"><text class="section-title">临近的饭局</text><button class="btn tonal small" @tap="showCreate=true"><Icon icon="Plus" :size="18"/>开饭局</button></view>
    <view v-if="loading && !upcoming.length" class="card empty">正在加载饭局...</view>
    <view v-else-if="error && !upcoming.length" class="card empty"><text>{{ error }}</text><button class="btn tonal" @tap="load">重试</button></view>
    <view v-else-if="!upcoming.length" class="card empty">还没有临近的饭局<br/><button class="btn tonal" @tap="showCreate=true">开一顿饭局</button></view>
    <view v-else class="list"><MealCard v-for="item in upcoming" :key="item.id" :meal="item" @open="openMeal"/><view v-if="error" class="card retry"><text>{{ error }}</text><button class="btn tonal small" @tap="load">重试</button></view></view>
    <text class="all" @tap="goMeals">查看全部饭局 →</text>
    <AppTabBar active="home" />
    <view v-if="showCreate" class="modal-mask" @tap.self="closeCreate"><view class="sheet"><text class="section-title">开饭局</text><view class="types"><view v-for="(label,key) in types" :key="key" class="chip" :class="{on:form.meal_type===key}" @tap="form.meal_type=key">{{label}}</view></view><view class="form-group"><text class="label">标题（可选）</text><input v-model="form.title" class="input" placeholder="例如：周末聚餐"/></view><view class="grid-2"><view><text class="label">日期</text><picker mode="date" :value="form.date" @change="form.date=$event.detail.value"><view class="input picker">{{form.date}}</view></picker></view><view><text class="label">用餐时间</text><picker mode="time" :value="form.dining_time" @change="form.dining_time=$event.detail.value"><view class="input picker">{{form.dining_time}}</view></picker></view></view><view class="form-group deadline"><text class="label">点菜截止</text><picker mode="time" :value="form.deadline" @change="form.deadline=$event.detail.value"><view class="input picker">{{form.deadline}}</view></picker></view><button class="btn block" :disabled="createPending" @tap="create">{{ createPending ? '创建中...' : '确认开饭局' }}</button></view></view>
  </view>
</template>

<script>
import Icon from '../../components/Icons.vue'
import AppTabBar from '../../components/AppTabBar.vue'
import MealCard from '../../components/MealCard.vue'
import { bootstrap, currentUser, request, run } from '../../api/client'
import { createdMealId, localDateKey, sortMealsByDiningTime, validateMealDraft } from '../../utils/app'

export default {
  components: { Icon, AppTabBar, MealCard },
  data() {
    return {
      meals: [],
      settings: {},
      me: currentUser(),
      showCreate: false,
      loading: false,
      error: '',
      createPending: false,
      types: { breakfast: '早餐', lunch: '午餐', dinner: '晚餐' },
      form: { meal_type: 'dinner', date: localDateKey(), dining_time: '18:30', deadline: '16:30', title: '' }
    }
  },
  computed: {
    upcoming() {
      return sortMealsByDiningTime(this.meals.filter(x => x && x.status !== 'cancelled' && (x.status !== 'done' || x.date === localDateKey()))).slice(0, 5)
    }
  },
  onShow() { this.load() },
  methods: {
    async load() {
      this.loading = true
      this.error = ''
      try {
        const [b, m] = await Promise.all([bootstrap(), request('/api/meals')])
        this.settings = b && b.settings || {}
        this.meals = Array.isArray(m) ? m : []
      } catch (e) {
        this.error = e && e.message || '饭局加载失败'
      } finally {
        this.loading = false
      }
    },
    openMeal(id) { uni.navigateTo({ url: `/pages/meal-detail/index?id=${id}` }) },
    goMeals() { uni.reLaunch({ url: '/pages/meals/index' }) },
    closeCreate() { if (!this.createPending) this.showCreate = false },
    async create() {
      if (this.createPending) return
      const validation = validateMealDraft(this.form)
      if (validation) { uni.showToast({ title: validation, icon: 'none' }); return }
      this.createPending = true
      try {
        const mealId = await run(async () => createdMealId(await request('/api/meals', { method: 'POST', data: Object.assign({}, this.form) })), '饭局已创建')
        this.showCreate = false
        this.openMeal(mealId)
      } catch (e) {
        // run already showed error
      } finally {
        this.createPending = false
      }
    }
  }
}
</script>
<style scoped>.family{display:block;color:#43a367;font-size:25rpx;font-weight:650}.hello{display:block;margin:10rpx 0;font-size:50rpx;font-weight:800}.section{margin:54rpx 0 24rpx}.small{min-height:66rpx;font-size:25rpx}.list{display:flex;flex-direction:column}.list > *{margin-bottom:22rpx}.empty .btn{margin-top:28rpx}.all{display:block;margin:34rpx 0;color:#43a367;font-size:27rpx}.types{display:flex;flex-direction:row;margin:28rpx 0}.types .chip{margin-right:15rpx}.picker{display:flex;flex-direction:row;align-items:center}.deadline{margin-top:26rpx}</style>
