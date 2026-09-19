<template>
  <view class="page no-tab form-page">
    <BackButton label="菜品管理" fallback-url="/pages/dishes/index" />
    <view v-if="unauthorized" class="state panel"><text>仅管理员可管理菜品</text><button class="btn tonal" @tap="back">返回我的</button></view>
    <view v-else-if="loading && !ready" class="state">正在加载菜品编辑器...</view>
    <view v-else-if="error && !ready" class="state panel"><text>{{ error }}</text><button class="btn tonal" @tap="load">重试</button><button class="btn ghost" @tap="back">返回菜品管理</button></view>
    <template v-else-if="ready">
      <PageHeader :title="id ? '编辑菜品' : '添加菜品'" subtitle="完整记录食材与做法，方便每次饭局使用" />
      <view class="photo" @tap="choose"><image v-if="preview" :src="preview" mode="aspectFill" /><view v-else><Icon icon="Camera" :size="30" /><text>拍照或选择图片</text></view></view>
      <view class="form-section">
        <view class="form-group"><text class="label">菜名</text><input v-model="form.name" class="input" maxlength="30" placeholder="例如：番茄炒蛋" /></view>
        <view class="form-group"><text class="label">一句话介绍</text><textarea v-model="form.description" class="input" maxlength="300" placeholder="口味、特色或家人的偏好" /></view>
        <view class="form-grid"><view class="form-group"><text class="label">菜系</text><picker :range="cuisineNames" :value="cuisinePickerValue" @change="selectCuisine"><view class="input picker">{{ selectedCuisine || '未分类' }}</view></picker></view><view class="form-group"><text class="label">标签</text><input v-model="tags" class="input" placeholder="荤菜, 下饭, 快手" /></view></view>
      </view>

      <view class="form-section"><view class="section-head"><view><text class="section-title">食材</text><text class="subtle">最多 30 项</text></view><button class="chip" :disabled="form.ingredients.length >= 30" @tap="addIngredient"><Icon icon="Plus" :size="15" /> 添加</button></view>
        <view v-for="item in form.ingredients" :key="item.key" class="ingredient"><input v-model="item.name" class="input ingredient-name" placeholder="食材" /><input v-model="item.quantity" class="input quantity" placeholder="用量" /><input v-model="item.unit" class="input unit" placeholder="单位" /><button class="remove" @tap="removeIngredient(item.key)"><Icon icon="X" :size="16" /></button></view>
      </view>

      <view class="form-section"><view class="section-head"><view><text class="section-title">做法</text><text class="subtle">最多 20 步</text></view><button class="chip" :disabled="form.steps.length >= 20" @tap="addStep"><Icon icon="Plus" :size="15" /> 添加</button></view>
        <view v-for="(step, index) in form.steps" :key="step.key" class="step"><text class="step-number">{{ index + 1 }}</text><textarea v-model="step.body" class="input" placeholder="描述这一步怎么做" /><button class="remove" @tap="removeStep(step.key)"><Icon icon="X" :size="16" /></button></view>
      </view>

      <view class="form-section"><view class="form-group"><text class="label">来源链接（可选）</text><input v-model="form.source_url" class="input" placeholder="菜谱或视频链接" /></view></view>
      <button class="btn block save" :disabled="saving" @tap="save">{{ saving ? '保存中...' : '保存菜品' }}</button>
    </template>
  </view>
</template>

<script setup lang="js">
import { computed, onMounted, reactive, ref } from 'vue'
import BackButton from '../../components/BackButton.vue'
import Icon from '../../components/Icons.vue'
import PageHeader from '../../components/PageHeader.vue'
import { assetUrl, currentUser, request, run, uploadImage } from '../../api/client'
import { cuisineIdFromPicker, normalizeDishDraft } from '../../utils/app'

let rowSequence = 0
function newIngredient(item = {}) { rowSequence += 1; return { key: `ingredient-${rowSequence}`, name: typeof item.name === 'string' ? item.name : '', quantity: typeof item.quantity === 'string' ? item.quantity : '', unit: typeof item.unit === 'string' ? item.unit : '' } }
function newStep(body = '') { rowSequence += 1; return { key: `step-${rowSequence}`, body: typeof body === 'string' ? body : '' } }

const id = ref(''), cuisines = ref([]), tags = ref(''), preview = ref(''), localImage = ref('')
const loading = ref(false), ready = ref(false), error = ref(''), saving = ref(false), unauthorized = ref(false)
const form = reactive({ name: '', description: '', image_path: null, cuisine_id: null, source_url: '', ingredients: [newIngredient()], steps: [newStep()] })
const cuisineNames = computed(() => ['未分类', ...cuisines.value.map(cuisine => `${cuisine?.emoji || ''} ${cuisine?.name || '未命名菜系'}`)])
const selectedCuisine = computed(() => cuisines.value.find(cuisine => cuisine?.id === form.cuisine_id)?.name || '')
const cuisinePickerValue = computed(() => { const index = cuisines.value.findIndex(cuisine => cuisine?.id === form.cuisine_id); return index < 0 ? 0 : index + 1 })

async function load() {
  if (currentUser()?.is_admin !== true) { unauthorized.value = true; ready.value = false; return false }
  if (loading.value) return false
  loading.value = true; ready.value = false; error.value = ''
  try { const loadedCuisines = await request('/api/cuisines'); if (!Array.isArray(loadedCuisines)) throw new Error('菜系加载失败'); cuisines.value = loadedCuisines; if (id.value) { const dish = await request(`/api/dishes/${id.value}`); if (!dish || typeof dish !== 'object') throw new Error('菜品加载失败'); applyDish(dish) } ready.value = true; return true }
  catch (loadError) { error.value = loadError?.message || '菜品加载失败'; return false } finally { loading.value = false }
}
function applyDish(dish) { form.name = typeof dish.name === 'string' ? dish.name : ''; form.description = typeof dish.description === 'string' ? dish.description : ''; form.image_path = typeof dish.image_path === 'string' ? dish.image_path : null; form.cuisine_id = typeof dish.cuisine_id === 'string' ? dish.cuisine_id : null; form.source_url = typeof dish.source_url === 'string' ? dish.source_url : ''; form.ingredients = (Array.isArray(dish.ingredients) ? dish.ingredients : []).map(newIngredient); form.steps = (Array.isArray(dish.steps) ? dish.steps : []).map(step => newStep(step?.body)); tags.value = Array.isArray(dish.tags) ? dish.tags.filter(Boolean).join(', ') : ''; preview.value = assetUrl(form.image_path); localImage.value = '' }
function selectCuisine(event) { form.cuisine_id = cuisineIdFromPicker(cuisines.value, Number(event?.detail?.value)) }
function showMessage(title) { uni.showToast({ title, icon: 'none' }) }
function addIngredient() { if (form.ingredients.length >= 30) return showMessage('食材最多 30 项'); form.ingredients.push(newIngredient()) }
function removeIngredient(key) { form.ingredients = form.ingredients.filter(item => item.key !== key) }
function addStep() { if (form.steps.length >= 20) return showMessage('步骤最多 20 项'); form.steps.push(newStep()) }
function removeStep(key) { form.steps = form.steps.filter(step => step.key !== key) }
function choose() { uni.chooseImage({ count: 1, sizeType: ['compressed'], success: result => { const path = result?.tempFilePaths?.[0]; if (!path) return showMessage('未选择图片'); localImage.value = path; preview.value = path }, fail: chooseError => showMessage(chooseError?.errMsg || '选择图片失败') }) }
async function save() {
  if (saving.value || unauthorized.value) return
  const draft = normalizeDishDraft({ ...form, tags: tags.value }); if (!draft.name) return showMessage('请填写菜名'); if (draft.source_url === null) return showMessage('来源链接格式不正确')
  saving.value = true
  try { let imagePath = form.image_path; if (localImage.value) { const uploaded = await uploadImage(localImage.value); if (!uploaded?.path) throw new Error('上传图片失败'); imagePath = uploaded.path } const payload = normalizeDishDraft({ ...form, tags: tags.value, image_path: imagePath }); await run(() => request(id.value ? `/api/dishes/${id.value}` : '/api/dishes', { method: id.value ? 'PUT' : 'POST', data: payload }), '菜品已保存'); uni.navigateBack() }
  catch (saveError) { if (saveError?.message) showMessage(saveError.message) } finally { saving.value = false }
}
onMounted(() => {
  try {
    const pages = typeof getCurrentPages === 'function' ? getCurrentPages() : []
    const options = pages[pages.length - 1]?.options || {}
    id.value = typeof options.id === 'string' ? options.id.trim() : ''
  } catch {}
  load()
})
</script>

<style scoped>
.form-page{max-width:820px}.state .btn{margin-top:20rpx}.photo{width:100%;aspect-ratio:16/9;margin-bottom:46rpx;overflow:hidden;border-radius:16rpx;background:var(--theme-bg-photo);color:var(--theme-text-action)}.photo image{width:100%;height:100%}.photo>view{display:flex;width:100%;height:100%;align-items:center;justify-content:center;flex-direction:column}.photo text{margin-top:12rpx;font-size:24rpx}.form-section{padding:38rpx 24rpx;border-top:1px solid var(--theme-border-subtle)}.form-section:first-of-type{border-top:0}.form-grid{display:grid;grid-template-columns:1fr;gap:0}.section-head{display:flex;margin-bottom:22rpx;align-items:center;justify-content:space-between}.section-head>view{display:flex;flex-direction:column}.section-head .chip{gap:6rpx}.ingredient{display:grid;grid-template-columns:minmax(0,1fr) 126rpx 100rpx 64rpx;gap:10rpx;margin-bottom:12rpx;align-items:center}.step{display:grid;grid-template-columns:42rpx minmax(0,1fr) 64rpx;gap:10rpx;margin-bottom:16rpx;align-items:start}.step-number{padding-top:24rpx;color:var(--theme-text-action);font-weight:650}.remove{display:flex;width:62rpx;height:62rpx;min-height:62rpx;padding:0;align-items:center;justify-content:center;border-radius:50%;background:transparent;color:var(--theme-text-secondary)}.picker{display:flex;align-items:center}.save{margin-top:24rpx}@media(min-width:700px){.form-grid{grid-template-columns:1fr 1fr;gap:24rpx}}
.section-head{flex-direction:row}
</style>
