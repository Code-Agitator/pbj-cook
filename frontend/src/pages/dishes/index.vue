<template>
  <view class="page">
    <PageHeader :key="`header-${filtered.length}`" title="菜品库" :subtitle="`共 ${filtered.length} 道菜`">
      <button v-if="me && me.is_admin" class="btn" @tap="add"><Icon icon="Plus" :size="18" />添加</button>
    </PageHeader>
    <input v-model="q" class="input search" placeholder="搜索菜名 / 描述 / 标签" />
    <scroll-view scroll-x class="scroll"><view class="chips"><view class="chip" :class="{ on: activeCuisine === 'all' }" @tap="activeCuisine = 'all'">全部</view><view v-for="c in cuisines" :key="c.id" class="chip" :class="{ on: activeCuisine === c.id }" @tap="activeCuisine = c.id">{{ c.emoji || '' }} {{ c.name || '未命名菜系' }}</view></view></scroll-view>

    <view v-if="loading && !dishes.length" key="loading" class="card empty">正在加载菜品...</view>
    <view v-else-if="error && !dishes.length" key="error" class="card empty state-card"><text>{{ error }}</text><button class="btn tonal" @tap="load">重试</button></view>
    <view v-else-if="!filtered.length" key="empty" class="card empty">{{ dishes.length ? '没有找到匹配的菜品' : '菜品库还是空的' }}</view>
    <view v-else key="results" class="dish-grid"><view v-for="dish in filtered" :key="dish.id" class="dish card" @tap="openDish(dish)"><image v-if="dish.image_path" :src="assetUrl(dish.image_path)" mode="aspectFill" /><view v-else class="placeholder">♨</view><view class="dish-body"><text class="dish-name">{{ dish.name || '未命名菜品' }}</text><text class="subtle desc">{{ dish.description || dishTags(dish) || '家常好味道' }}</text></view></view></view>
    <view v-if="error && dishes.length" class="card retry"><text>{{ error }}</text><button class="btn tonal small" @tap="load">重试</button></view>
    <AppTabBar active="dishes" />
  </view>
</template>

<script>
import Icon from '../../components/Icons.vue'
import AppTabBar from '../../components/AppTabBar.vue'
import PageHeader from '../../components/PageHeader.vue'
import { assetUrl, currentUser, request, run } from '../../api/client'
import { dishActions } from '../../utils/app'

export default {
  components: { Icon, AppTabBar, PageHeader },
  created() {
    // expose to template
    this.assetUrl = assetUrl
  },
  data() {
    return {
      me: currentUser(),
      dishes: [],
      cuisines: [],
      q: '',
      activeCuisine: 'all',
      loading: false,
      error: '',
      archivePending: new Set()
    }
  },
  computed: {
    filtered() {
      const query = this.q.trim().toLocaleLowerCase()
      return this.dishes.filter((dish) => {
        if (!dish || (this.activeCuisine !== 'all' && dish.cuisine_id !== this.activeCuisine)) return false
        if (!query) return true
        return `${dish.name || ''} ${dish.description || ''} ${this.dishTags(dish)}`.toLocaleLowerCase().includes(query)
      })
    }
  },
  onShow() { this.load() },
  methods: {
    dishTags(dish) {
      return Array.isArray(dish?.tags) ? dish.tags.filter(Boolean).join(' · ') : (dish?.tags || '')
    },
    async load() {
      if (this.loading) return false
      this.loading = true
      this.error = ''
      try {
        const [loadedDishes, loadedCuisines] = await Promise.all([request('/api/dishes'), request('/api/cuisines')])
        this.dishes = Array.isArray(loadedDishes) ? loadedDishes : []
        this.cuisines = Array.isArray(loadedCuisines) ? loadedCuisines : []
        return true
      } catch (loadError) {
        this.error = loadError?.message || '菜品加载失败'
        return false
      } finally {
        this.loading = false
      }
    },
    add() {
      try { uni.navigateTo({ url: '/pages/dish-form/index' }) } catch (e) { this.showMessage(e?.message || '无法打开菜品编辑页') }
    },
    openDish(dish) {
      const actions = dishActions(dish, this.me)
      try {
        uni.showActionSheet({
          itemList: actions.map((action) => action.label),
          success: (result) => {
            const action = actions[Number(result?.tapIndex)]
            if (action && action.key) this.dispatchDishAction(action.key, dish)
          },
          fail: () => {}
        })
      } catch (e) { this.showMessage(e?.message || '无法打开菜品操作') }
    },
    async dispatchDishAction(key, dish) {
      try {
        if (key === 'view') await this.showDetail(dish)
        else if (key === 'edit') uni.navigateTo({ url: `/pages/dish-form/index?id=${dish.id}` })
        else if (key === 'archive') await this.archiveDish(dish)
      } catch (e) { this.showMessage(e?.message || '菜品操作失败') }
    },
    async showDetail(dish) {
      try {
        const detail = await request(`/api/dishes/${dish.id}`)
        if (!detail || typeof detail !== 'object') throw new Error('菜品详情加载失败')
        const ingredients = (Array.isArray(detail.ingredients) ? detail.ingredients : []).map((item) => `${item?.name || ''} ${item?.quantity || ''}${item?.unit || ''}`.trim()).filter(Boolean).join('\n') || '暂无食材记录'
        const steps = (Array.isArray(detail.steps) ? detail.steps : []).map((step, index) => step?.body ? `${index + 1}. ${step.body}` : '').filter(Boolean).join('\n') || '暂无做法记录'
        uni.showModal({ title: detail.name || '菜品详情', content: `${detail.description || ''}\n\n食材\n${ingredients}\n\n做法\n${steps}`, showCancel: false })
      } catch (e) { this.showMessage(e?.message || '菜品详情加载失败') }
    },
    confirmArchive() {
      return new Promise((resolve) => {
        try {
          uni.showModal({ title: '归档菜品', content: '归档后将不再出现在菜品库中，确定继续吗？', success: (result) => resolve(Boolean(result && result.confirm)), fail: () => resolve(false) })
        } catch (e) { resolve(false) }
      })
    },
    async archiveDish(dish) {
      if (!dish || !dish.id || this.archivePending.has(dish.id)) return
      this.setArchivePending(dish.id, true)
      try {
        if (!await this.confirmArchive()) return
        await run(() => request(`/api/dishes/${dish.id}/status`, { method: 'PATCH', data: { status: 'archived' } }), '已归档')
        this.dishes = this.dishes.filter((item) => item && item.id !== dish.id)
      } catch (e) {
        // run has already presented the request failure to the user.
      } finally {
        this.setArchivePending(dish.id, false)
      }
    },
    setArchivePending(id, pending) {
      const next = new Set(this.archivePending)
      if (pending) next.add(id)
      else next.delete(id)
      this.archivePending = next
    },
    showMessage(title) {
      try { uni.showToast({ title, icon: 'none' }) } catch (e) {}
    }
  }
}
</script>

<style scoped>
.search { margin-bottom: 18rpx }
.scroll { white-space: nowrap; margin-bottom: 22rpx }
.chips { display: flex; flex-direction: row }
.chips .chip { margin-right: 12rpx }
.state-card .btn { margin-top: 22rpx }
.retry { display: flex; flex-direction: row; align-items: center; justify-content: space-between; margin-top: 20rpx }
.dish-grid { display: flex; flex-direction: row; flex-wrap: wrap }
.dish { width: 48%; margin: 0 1% 20rpx; overflow: hidden }
.dish image, .placeholder { width: 100%; height: 265rpx }
.placeholder { display: flex; flex-direction: row; align-items: center; justify-content: center; background: #e7ede8; color: #9bcdaa; font-size: 60rpx }
.dish-body { padding: 22rpx }
.dish-name { display: block; font-size: 31rpx; font-weight: 750 }
.desc { display: block; margin-top: 7rpx; white-space: nowrap; overflow: hidden; text-overflow: ellipsis }
</style>
