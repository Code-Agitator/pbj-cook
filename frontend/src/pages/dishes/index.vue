<template>
  <view class="page no-tab page-wide">
    <BackButton label="我的" fallback-url="/pages/me/index" />
    <view v-if="isAdmin" class="page-action"><view class="btn add" @tap="add"><Icon icon="Plus" :size="18" /> 添加菜品</view></view>
    <MealDishFilters :query="query" :cuisines="cuisines" :cuisine-id="cuisineId" :tags="activeTags" :available-tags="availableTags" :selected-count="0" :show-selected-only="false" :result-count="filtered.length" @update:query="query = $event" @update:cuisine-id="cuisineId = $event" @toggle-tag="toggleTag" @reset="resetFilters" />
    <view v-if="!isAdmin" class="state panel">仅管理员可管理菜品</view>
    <view v-else-if="loading && !dishes.length" class="state">正在加载菜品...</view>
    <view v-else-if="error && !dishes.length" class="state panel"><text>{{ error }}</text><view class="btn tonal" @tap="load">重试</view></view>
    <view v-else-if="!filtered.length" class="state panel">{{ dishes.length ? '没有符合条件的菜品' : '菜品库还是空的' }}</view>
    <view v-else class="dish-grid"><DishImageCard v-for="dish in filtered" :key="dish.id" :dish="dish" :src="assetUrl(dish.image_path)" :selectable="false" @open="openDish" /></view>
    <view v-if="error && dishes.length" class="inline-error"><text>{{ error }}</text><view @tap="load">重试</view></view>
  </view>
</template>

<script setup lang="js">
import { computed, onActivated, onMounted, ref } from 'vue'
import BackButton from '../../components/BackButton.vue'
import DishImageCard from '../../components/DishImageCard.vue'
import MealDishFilters from '../../components/MealDishFilters.vue'
import Icon from '../../components/Icons.vue'
import PageHeader from '../../components/PageHeader.vue'
import { assetUrl, currentUser, request, run } from '../../api/client'
import { availableDishTags, filterMealDishes } from '../../utils/meals'

const me = ref(currentUser()), dishes = ref([]), cuisines = ref([]), query = ref(''), cuisineId = ref(null), activeTags = ref(new Set())
const loading = ref(false), error = ref(''), archivePending = ref(new Set())
const isAdmin = computed(() => me.value?.is_admin === true)
const availableTags = computed(() => availableDishTags(dishes.value, cuisineId.value))
const filtered = computed(() => filterMealDishes({ dishes: dishes.value, cuisineId: cuisineId.value, tags: activeTags.value, query: query.value, selectedIds: new Set() }))
function add() { if (isAdmin.value) uni.navigateTo({ url: '/pages/dish-form/index' }) }
function toggleTag(tag) { if (tag === '__mine__') return; const next = new Set(activeTags.value); next.has(tag) ? next.delete(tag) : next.add(tag); activeTags.value = next }
function resetFilters() { query.value = ''; cuisineId.value = null; activeTags.value = new Set() }
async function load() {
  me.value = currentUser(); if (!isAdmin.value) return false
  loading.value = true; error.value = ''
  try { const [loadedDishes, loadedCuisines] = await Promise.all([request('/api/dishes'), request('/api/cuisines')]); dishes.value = Array.isArray(loadedDishes) ? loadedDishes : []; cuisines.value = Array.isArray(loadedCuisines) ? loadedCuisines : []; return true }
  catch (loadError) { error.value = loadError?.message || '菜品加载失败'; return false } finally { loading.value = false }
}
function openDish(dish) { if (!isAdmin.value) return; uni.showActionSheet({ itemList: ['查看详情', '编辑菜品', '归档菜品'], success: result => { const action = Number(result?.tapIndex); if (action === 0) showDetail(dish); else if (action === 1) uni.navigateTo({ url: `/pages/dish-form/index?id=${dish.id}` }); else if (action === 2) archiveDish(dish) } }) }
async function showDetail(dish) { try { const detail = await request(`/api/dishes/${dish.id}`); const ingredients = (detail?.ingredients || []).map(item => `${item.name || ''} ${item.quantity || ''}${item.unit || ''}`.trim()).filter(Boolean).join('\n') || '暂无食材记录'; const steps = (detail?.steps || []).map((step, index) => step?.body ? `${index + 1}. ${step.body}` : '').filter(Boolean).join('\n') || '暂无做法记录'; uni.showModal({ title: detail?.name || '菜品详情', content: `${detail?.description || ''}\n\n食材\n${ingredients}\n\n做法\n${steps}`, showCancel: false }) } catch (detailError) { uni.showToast({ title: detailError?.message || '菜品详情加载失败', icon: 'none' }) } }
function confirmArchive() { return new Promise(resolve => uni.showModal({ title: '归档菜品', content: '归档后将不再出现在菜品库中，确定继续吗？', success: result => resolve(Boolean(result?.confirm)), fail: () => resolve(false) })) }
async function archiveDish(dish) { if (!dish?.id || archivePending.value.has(dish.id) || !await confirmArchive()) return; const next = new Set(archivePending.value); next.add(dish.id); archivePending.value = next; try { await run(() => request(`/api/dishes/${dish.id}/status`, { method: 'PATCH', data: { status: 'archived' } }), '已归档'); dishes.value = dishes.value.filter(item => item?.id !== dish.id) } catch {} finally { const done = new Set(archivePending.value); done.delete(dish.id); archivePending.value = done } }
onMounted(load)
onActivated(load)
</script>

<style scoped>
.page-action{display:flex;justify-content:flex-end;padding:0 24rpx 12rpx}.add{min-height:70rpx;padding:0 22rpx;gap:8rpx}.dish-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:18rpx}.state .btn{margin-top:20rpx}.inline-error{display:flex;margin:22rpx 24rpx 0;padding:18rpx 20rpx;align-items:center;justify-content:space-between;border-left:4rpx solid var(--theme-danger);background:var(--theme-danger-surface);color:var(--theme-danger);font-size:23rpx}.inline-error view{min-height:56rpx;background:transparent;color:var(--theme-danger);cursor:pointer}@media(min-width:700px){.dish-grid{grid-template-columns:repeat(3,minmax(0,1fr));gap:22rpx}}@media(min-width:1024px){.dish-grid{grid-template-columns:repeat(4,minmax(0,1fr))}}
.inline-error{flex-direction:row}
</style>
