<template>
  <view class="page no-tab">
    <view v-if="invalidRoute" class="card empty state-card"><text>饭局参数无效</text><button class="btn tonal" @tap="back">返回首页</button></view>
    <view v-else-if="loading && !meal" class="card empty state-card">正在加载饭局...</view>
    <view v-else-if="error && !meal" class="card empty state-card"><text>{{ error }}</text><button class="btn tonal" @tap="load">重试</button><button class="btn ghost" @tap="back">返回首页</button></view>
    <template v-else-if="meal">
      <view class="row between"><text class="back" @tap="back">‹ 饭局</text><text class="badge">{{ status[meal.status] || '状态未知' }}</text></view>
      <view v-if="error" class="card retry"><text>{{ error }}</text><button class="btn tonal small" @tap="load">重试</button></view>
      <view class="card info"><view class="meal-icon">{{ emoji[meal.meal_type] || '🍽️' }}</view><view><text class="meal-name">{{ meal.title || labels[meal.meal_type] || '饭局' }}</text><text class="subtle line">{{ meal.date || '日期待定' }} {{ fmt(meal.dining_time) }} 开饭</text></view><view class="divider"/><text class="subtle line">⏱ {{ deadlineText }}</text><text class="cook line">♨ {{ meal.cook && meal.cook.name ? `${meal.cook.name} 掌勺` : '还没人认领做饭' }}</text></view>
      <view class="actions"><button v-if="interaction.canCook" class="btn block" :class="{tonal:interaction.isCook}" :disabled="pending('cook')" @tap="cook"><Icon icon="ChefHat" :size="18"/>{{ pending('cook') ? '更新中...' : interaction.isCook ? '我不做了' : meal.cook ? '我来接手' : '我来做这顿' }}</button><view v-if="interaction.canManage" class="grid-2"><button v-if="interaction.canStartCooking" class="btn tonal" :disabled="pending('status:cooking')" @tap="setStatus('cooking')">截止并开做</button><button v-if="interaction.canComplete" class="btn tonal" :disabled="pending('status:done')" @tap="setStatus('done')">完成饭局</button><button v-if="interaction.canCancel" class="btn ghost" :disabled="pending('status:cancelled')" @tap="setStatus('cancelled')">取消饭局</button></view></view>
      <view class="tabs"><view :class="{on:tab==='pick'}" @tap="tab='pick'">点你想吃的 <text>{{ selected.size }}</text></view><view :class="{on:tab==='who'}" @tap="tab='who'">大家点了什么 <text>{{ groups.length }}</text></view></view>
      <template v-if="tab==='pick'">
        <view v-if="interaction.canOrder" class="filters"><scroll-view scroll-x class="scroll"><view class="chips"><view class="chip" :class="{on:filter==='all'}" @tap="filter='all'">全部</view><view v-for="c in cuisines" :key="c.id" class="chip" :class="{on:filter===c.id}" @tap="filter=c.id">{{ c.emoji || '' }} {{ c.name || '未命名菜系' }}</view></view></scroll-view><input v-model="q" class="input search" placeholder="搜索菜名 / 描述 / 标签"/></view>
        <view v-if="!interaction.canOrder" class="card empty">点菜已结束，去看看大家点了什么</view>
        <view v-else-if="!filtered.length" class="card empty">没有找到匹配的菜品</view>
        <view v-else class="dish-grid"><view v-for="d in filtered" :key="d.id" class="dish" :class="{selected:selected.has(d.id)}" @tap="toggleOrder(d.id)"><image v-if="d.image_path" :src="assetUrl(d.image_path)" mode="aspectFill"/><view v-else class="placeholder">♨</view><view class="dish-text"><text>{{ d.name || '未命名菜品' }}</text><text class="subtle">{{ d.cuisine_name || dishTags(d) || '家常菜' }}</text></view><view class="check">{{ selected.has(d.id)?'✓':'+' }}</view></view></view>
      </template>
      <template v-else>
        <view v-if="!groups.length" class="card empty">还没有人点菜</view>
        <view v-else class="groups"><view v-for="g in groups" :key="g.dish_id" class="card group" :class="{skipped:skipped.has(g.dish_id)}"><view class="row"><image v-if="g.dish_image" :src="assetUrl(g.dish_image)" mode="aspectFill"/><view v-else class="mini">♨</view><view class="grow"><text class="g-name">{{ g.dish_name || '未命名菜品' }}</text><text class="subtle">{{ peopleLabel(g.people) }} 想吃</text></view><button v-if="interaction.canSkip" class="chip" :disabled="pending(`skip:${g.dish_id}`)" @tap="toggleSkip(g.dish_id)">{{ pending(`skip:${g.dish_id}`) ? '更新中...' : skipped.has(g.dish_id)?'恢复':'不做' }}</button></view></view></view>
      </template>
      <view v-if="interaction.canReview" class="review card"><text class="section-title">饭后评价</text><view class="stars"><text v-for="n in 5" :key="n" :class="{on:rating>=n}" @tap="rating=n">★</text></view><textarea v-model="comment" class="input" maxlength="200" placeholder="这顿饭怎么样？"/><button class="btn block" :disabled="pending('review')" @tap="submitReview">{{ pending('review') ? '保存中...' : '提交评价' }}</button><view v-for="r in meal.reviews || []" :key="r.id" class="review-item"><text>{{ r.user_name || '成员' }} · {{ '★'.repeat(Number(r.rating) || 0) }}</text><text class="subtle">{{ r.comment || '' }}</text></view></view>
    </template>
  </view>
</template>
<script>
import Icon from '../../components/Icons.vue'
import { assetUrl, currentUser, request, run } from '../../api/client'
import { formatMealTime, mealInteractionState, numericTimestamp } from '../../utils/app'

export default {
  components: { Icon },
  created() {
    this.assetUrl = assetUrl
  },
  data() {
    return {
      id: '',
      meal: null,
      dishes: [],
      cuisines: [],
      tab: 'pick',
      filter: 'all',
      q: '',
      rating: 5,
      comment: '',
      loading: false,
      error: '',
      invalidRoute: false,
      inFlight: new Set(),
      selected: new Set(),
      skipped: new Set(),
      me: currentUser(),
      emoji: { breakfast: '🥪', lunch: '🍱', dinner: '🍲' },
      labels: { breakfast: '早餐', lunch: '午餐', dinner: '晚餐' },
      status: { ordering: '点菜中', cooking: '做饭中', done: '已完成', cancelled: '已取消' }
    }
  },
  computed: {
    interaction() { return mealInteractionState(this.meal, this.me) },
    deadlineText() {
      const timestamp = numericTimestamp(this.meal && this.meal.order_deadline)
      if (timestamp === null) return '点菜截止时间待定'
      const date = new Date(timestamp * 1000)
      if (Number.isNaN(date.getTime())) return '点菜截止时间待定'
      return date.toLocaleString('zh-CN', { month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit', hour12: false }) + ' 截止'
    },
    filtered() {
      const query = this.q.trim().toLocaleLowerCase()
      return this.dishes.filter(dish => {
        if (!dish || (this.filter !== 'all' && dish.cuisine_id !== this.filter)) return false
        if (!query) return true
        const tags = Array.isArray(dish.tags) ? dish.tags.join(' ') : (dish.tags || '')
        return `${dish.name || ''} ${dish.description || ''} ${tags}`.toLocaleLowerCase().includes(query)
      })
    },
    groups() {
      const grouped = {}
      const orders = this.meal && this.meal.orders || []
      for (const order of orders) {
        if (!order || !order.dish_id) continue
        if (!grouped[order.dish_id]) grouped[order.dish_id] = Object.assign({}, order, { people: [] })
        grouped[order.dish_id].people.push(order)
      }
      return Object.values(grouped).sort((left, right) => right.people.length - left.people.length)
    }
  },
  mounted() {
    const pages = typeof getCurrentPages === 'function' ? getCurrentPages() : []
    const page = pages[pages.length - 1]
    this.id = page && page.options && typeof page.options.id === 'string' ? page.options.id : ''
    if (!this.id) {
      this.invalidRoute = true
      this.error = '饭局参数无效'
      return
    }
    this.load()
  },
  methods: {
    fmt(value) { return formatMealTime(value) },
    dishTags(dish) {
      return Array.isArray(dish && dish.tags) ? dish.tags.filter(Boolean).join(' · ') : ((dish && dish.tags) || '')
    },
    peopleLabel(people) {
      return (people || []).map(person => (person && person.user_name) || '成员').join('、') || '成员'
    },
    pending(key) { return this.inFlight.has(key) },
    relaunchHome() { uni.reLaunch({ url: '/pages/home/index' }) },
    back() {
      try {
        const pages = typeof getCurrentPages === 'function' ? getCurrentPages() : []
        if (pages.length > 1) {
          uni.navigateBack({ fail: this.relaunchHome })
          return
        }
      } catch (e) {}
      this.relaunchHome()
    },
    async load() {
      if (!this.id) {
        this.invalidRoute = true
        this.error = '饭局参数无效'
        return false
      }
      this.loading = true
      this.error = ''
      try {
        const [loadedMeal, loadedDishes, loadedCuisines] = await Promise.all([
          request(`/api/meals/${this.id}`), request('/api/dishes'), request('/api/cuisines')
        ])
        if (!loadedMeal || typeof loadedMeal !== 'object') throw new Error('饭局加载失败')
        this.meal = loadedMeal
        this.dishes = Array.isArray(loadedDishes) ? loadedDishes : []
        this.cuisines = Array.isArray(loadedCuisines) ? loadedCuisines : []
        this.selected = new Set(Array.isArray(loadedMeal.my_ordered_dish_ids) ? loadedMeal.my_ordered_dish_ids : [])
        this.skipped = new Set(Array.isArray(loadedMeal.skipped_dish_ids) ? loadedMeal.skipped_dish_ids : [])
        const reviews = Array.isArray(loadedMeal.reviews) ? loadedMeal.reviews : []
        const mine = reviews.find(review => review && review.user_id === (this.me && this.me.id))
        if (mine) {
          this.rating = Number(mine.rating) || 5
          this.comment = mine.comment || ''
        }
        return true
      } catch (loadError) {
        this.error = (loadError && loadError.message) || '饭局加载失败'
        return false
      } finally {
        this.loading = false
      }
    },
    async mutate(key, action, success) {
      if (this.pending(key)) return false
      const next = new Set(this.inFlight)
      next.add(key)
      this.inFlight = next
      try {
        await run(action, success)
        return true
      } catch (e) {
        return false
      } finally {
        const finished = new Set(this.inFlight)
        finished.delete(key)
        this.inFlight = finished
      }
    },
    async reloadAfterMutation() {
      if (!await this.load()) throw new Error('饭局已更新，请重试刷新')
    },
    async cook() {
      if (!this.interaction.canCook) return
      await this.mutate('cook', async () => {
        await request(`/api/meals/${this.id}/cook`, { method: 'POST' })
        await this.reloadAfterMutation()
      }, '已更新')
    },
    confirmCancellation() {
      return new Promise((resolve) => {
        try {
          uni.showModal({
            title: '取消饭局', content: '确定要取消这场饭局吗？',
            success: (result) => resolve(Boolean(result && result.confirm)), fail: () => resolve(false)
          })
        } catch (e) { resolve(false) }
      })
    },
    async setStatus(nextStatus) {
      const allowed = (nextStatus === 'cooking' && this.interaction.canStartCooking)
        || (nextStatus === 'done' && this.interaction.canComplete)
        || (nextStatus === 'cancelled' && this.interaction.canCancel)
      if (!allowed) return
      if (nextStatus === 'cancelled' && !await this.confirmCancellation()) return
      await this.mutate(`status:${nextStatus}`, async () => {
        await request(`/api/meals/${this.id}/status`, { method: 'PATCH', data: { status: nextStatus } })
        await this.reloadAfterMutation()
      }, '状态已更新')
    },
    async toggleOrder(dishId) {
      if (!this.interaction.canOrder || !dishId) return
      await this.mutate(`order:${dishId}`, async () => {
        const result = await request(`/api/meals/${this.id}/orders/${dishId}`, { method: 'POST' })
        if (typeof (result && result.selected) !== 'boolean') throw new Error('点菜更新失败')
        const next = new Set(this.selected)
        if (result.selected) next.add(dishId)
        else next.delete(dishId)
        this.selected = next
        if (this.meal) this.meal.my_ordered_dish_ids = [...next]
      })
    },
    async toggleSkip(dishId) {
      if (!this.interaction.canSkip || !dishId) return
      await this.mutate(`skip:${dishId}`, async () => {
        const result = await request(`/api/meals/${this.id}/skips/${dishId}`, { method: 'POST' })
        if (typeof (result && result.skipped) !== 'boolean') throw new Error('菜品状态更新失败')
        const next = new Set(this.skipped)
        if (result.skipped) next.add(dishId)
        else next.delete(dishId)
        this.skipped = next
      })
    },
    async submitReview() {
      if (!this.interaction.canReview) return
      await this.mutate('review', async () => {
        await request(`/api/meals/${this.id}/review`, { method: 'PUT', data: { rating: this.rating, comment: this.comment } })
        await this.reloadAfterMutation()
      }, '评价已保存')
    }
  }
}
</script>
<style scoped>.state-card{margin-top:80rpx}.state-card .btn{margin-top:22rpx}.retry{display:flex;flex-direction:row;align-items:center;justify-content:space-between;margin:20rpx 0}.info{display:flex;flex-direction:row;flex-wrap:wrap;padding:34rpx;align-items:flex-start}.info > view:first-child{margin-right:24rpx}.info > view:nth-child(2){flex:1}.meal-icon{width:110rpx;height:110rpx;border-radius:30rpx;background:#e5f3e9;display:flex;flex-direction:row;align-items:center;justify-content:center;font-size:50rpx}.meal-name{display:block;font-size:36rpx;font-weight:800;margin:8rpx 0}.line{display:block;margin-top:8rpx}.divider{width:100%;border-top:1px solid #e7ebe8;margin:18rpx 0}.cook{color:#43a367}.actions{display:flex;flex-direction:column;margin:24rpx 0 36rpx}.tabs{display:flex;flex-direction:row;background:#e9ece9;border-radius:34rpx;padding:7rpx;margin-bottom:24rpx}.tabs view{flex:1;text-align:center;padding:20rpx 4rpx;border-radius:28rpx;font-size:25rpx}.tabs .on{background:white;color:#297648;font-weight:700;box-shadow:0 3rpx 10rpx rgba(30,50,38,.08)}.filters{margin-bottom:22rpx}.scroll{white-space:nowrap}.chips{display:flex;flex-direction:row;padding:4rpx 0 18rpx}.chips .chip{margin-right:12rpx}.search{min-height:75rpx}.dish-grid{display:flex;flex-direction:row;flex-wrap:wrap}.dish{width:48%;margin:0 1% 18rpx;position:relative;overflow:hidden;border-radius:28rpx;background:white;border:3rpx solid transparent}.dish.selected{border-color:#43a367}.dish image,.placeholder{width:100%;height:240rpx}.placeholder{display:flex;flex-direction:row;align-items:center;justify-content:center;background:#e7ede8;color:#9bcdaa;font-size:55rpx}.dish-text{display:flex;flex-direction:column;padding:20rpx;font-weight:700}.dish-text .subtle{white-space:nowrap;overflow:hidden;text-overflow:ellipsis;font-weight:400}.check{position:absolute;right:14rpx;top:210rpx;width:56rpx;height:56rpx;border-radius:50%;background:#43a367;color:#fff;display:flex;flex-direction:row;align-items:center;justify-content:center;font-size:30rpx}.groups{display:flex;flex-direction:column}.group{padding:20rpx;display:flex;flex-direction:row}.group.skipped{opacity:.5}.group image,.mini{width:90rpx;height:90rpx;border-radius:22rpx}.mini{display:flex;flex-direction:row;align-items:center;justify-content:center;background:#e7ede8}.grow{flex:1;display:flex;flex-direction:column;margin-left:18rpx}.g-name{font-weight:700}.review{padding:30rpx;margin-top:40rpx}.stars{display:flex;flex-direction:row;margin:22rpx 0}.stars text{font-size:54rpx;color:#dfe4df;margin-right:14rpx}.stars .on{color:#f0ae3b}.review .btn{margin-top:20rpx}.review-item{display:flex;flex-direction:column;padding-top:24rpx;margin-top:24rpx;border-top:1px solid #e7ebe8}</style>
