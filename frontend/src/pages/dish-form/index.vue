<template>
  <view class="page no-tab">
    <text class="back" @tap="back">‹ 菜品库</text>
    <view v-if="loading && !ready" class="card empty state-card">正在加载菜品编辑器...</view>
    <view v-else-if="error && !ready" class="card empty state-card"><text>{{ error }}</text><button class="btn tonal" @tap="load">重试</button><button class="btn ghost" @tap="back">返回菜品库</button></view>
    <template v-else-if="ready">
      <PageHeader :title="id ? '编辑菜品' : '添加菜品'" />
      <view class="photo" @tap="choose"><image v-if="preview" :src="preview" mode="aspectFill" /><view v-else><Icon icon="Camera" :size="30" /><text>拍照或选择图片</text></view></view>
      <view class="form-group"><text class="label">菜名</text><input v-model="form.name" class="input" maxlength="30" placeholder="例如：番茄炒蛋" /></view>
      <view class="form-group"><text class="label">一句话介绍</text><textarea v-model="form.description" class="input" maxlength="300" placeholder="口味、特色或家人的偏好" /></view>
      <view class="form-group"><text class="label">菜系</text><picker :range="cuisineNames" :value="cuisinePickerValue" @change="selectCuisine"><view class="input picker">{{ selectedCuisine || '未分类' }}</view></picker></view>
      <view class="form-group"><text class="label">标签（用逗号分隔）</text><input v-model="tags" class="input" placeholder="荤菜, 下饭, 快手" /></view>
      <view class="row between group-head"><text class="section-title">食材</text><button class="chip" :disabled="form.ingredients.length >= 30" @tap="addIngredient">+ 添加</button></view>
      <view v-for="item in form.ingredients" :key="item.key" class="ingredient"><input v-model="item.name" class="input" placeholder="食材" /><input v-model="item.quantity" class="input qty" placeholder="用量" /><input v-model="item.unit" class="input unit" placeholder="单位" /><text @tap="removeIngredient(item.key)">×</text></view>
      <view class="row between group-head"><text class="section-title">做法步骤</text><button class="chip" :disabled="form.steps.length >= 20" @tap="addStep">+ 添加</button></view>
      <view v-for="(step, index) in form.steps" :key="step.key" class="step"><text>{{ index + 1 }}</text><textarea v-model="step.body" class="input" placeholder="描述这一步怎么做" /><text @tap="removeStep(step.key)">×</text></view>
      <view class="form-group"><text class="label">来源链接（可选）</text><input v-model="form.source_url" class="input" placeholder="菜谱或视频链接" /></view>
      <button class="btn block save" :disabled="saving" @tap="save">{{ saving ? '保存中...' : '保存菜品' }}</button>
    </template>
  </view>
</template>

<script>
import Icon from '../../components/Icons.vue'
import PageHeader from '../../components/PageHeader.vue'
import { assetUrl, request, run, uploadImage } from '../../api/client'
import { cuisineIdFromPicker, normalizeDishDraft } from '../../utils/app'

let rowSequence = 0

function newIngredient(item) {
  rowSequence += 1
  item = item || {}
  return {
    key: `ingredient-${rowSequence}`,
    name: typeof item.name === 'string' ? item.name : '',
    quantity: typeof item.quantity === 'string' ? item.quantity : '',
    unit: typeof item.unit === 'string' ? item.unit : ''
  }
}

function newStep(body) {
  rowSequence += 1
  return {
    key: `step-${rowSequence}`,
    body: typeof body === 'string' ? body : ''
  }
}

export default {
  components: { Icon, PageHeader },
  created() {
    this.assetUrl = assetUrl
  },
  data() {
    return {
      id: '',
      cuisines: [],
      tags: '',
      preview: '',
      localImage: '',
      loading: false,
      ready: false,
      error: '',
      saving: false,
      form: {
        name: '', description: '', image_path: null, cuisine_id: null, source_url: '',
        ingredients: [newIngredient()], steps: [newStep()]
      }
    }
  },
  computed: {
    cuisineNames() {
      return ['未分类', ...this.cuisines.map(cuisine => `${cuisine && cuisine.emoji || ''} ${cuisine && cuisine.name || '未命名菜系'}`)]
    },
    selectedCuisine() {
      const found = this.cuisines.find(cuisine => cuisine && cuisine.id === this.form.cuisine_id)
      return found ? found.name : ''
    },
    cuisinePickerValue() {
      const index = this.cuisines.findIndex(cuisine => cuisine && cuisine.id === this.form.cuisine_id)
      return index < 0 ? 0 : index + 1
    }
  },
  mounted() {
    const pages = getCurrentPages()
    const page = pages[pages.length - 1]
    this.id = page && page.options && typeof page.options.id === 'string' ? page.options.id.trim() : ''
    this.load()
  },
  methods: {
    async load() {
      if (this.loading) return false
      this.loading = true
      this.ready = false
      this.error = ''
      try {
        const loadedCuisines = await request('/api/cuisines')
        if (!Array.isArray(loadedCuisines)) throw new Error('菜系加载失败')
        let loadedDish = null
        if (this.id) {
          loadedDish = await request(`/api/dishes/${this.id}`)
          if (!loadedDish || typeof loadedDish !== 'object') throw new Error('菜品加载失败')
        }
        this.cuisines = loadedCuisines
        if (loadedDish) this.applyDish(loadedDish)
        this.ready = true
        return true
      } catch (loadError) {
        this.error = (loadError && loadError.message) || '菜品加载失败'
        return false
      } finally {
        this.loading = false
      }
    },
    applyDish(dish) {
      this.form.name = typeof dish.name === 'string' ? dish.name : ''
      this.form.description = typeof dish.description === 'string' ? dish.description : ''
      this.form.image_path = typeof dish.image_path === 'string' ? dish.image_path : null
      this.form.cuisine_id = typeof dish.cuisine_id === 'string' ? dish.cuisine_id : null
      this.form.source_url = typeof dish.source_url === 'string' ? dish.source_url : ''
      this.form.ingredients = (Array.isArray(dish.ingredients) ? dish.ingredients : []).map(item => newIngredient(item))
      this.form.steps = (Array.isArray(dish.steps) ? dish.steps : []).map(step => newStep(step && step.body))
      this.tags = Array.isArray(dish.tags) ? dish.tags.filter(Boolean).join(', ') : ''
      this.preview = assetUrl(this.form.image_path)
      this.localImage = ''
    },
    selectCuisine(event) {
      this.form.cuisine_id = cuisineIdFromPicker(this.cuisines, Number(event && event.detail && event.detail.value))
    },
    addIngredient() {
      if (this.form.ingredients.length >= 30) return this.showMessage('食材最多 30 项')
      this.form.ingredients.push(newIngredient())
    },
    removeIngredient(key) {
      this.form.ingredients = this.form.ingredients.filter(item => item.key !== key)
    },
    addStep() {
      if (this.form.steps.length >= 20) return this.showMessage('步骤最多 20 项')
      this.form.steps.push(newStep())
    },
    removeStep(key) {
      this.form.steps = this.form.steps.filter(step => step.key !== key)
    },
    choose() {
      try {
        uni.chooseImage({
          count: 1,
          sizeType: ['compressed'],
          success: (result) => {
            const path = result && result.tempFilePaths && result.tempFilePaths[0]
            if (!path) return this.showMessage('未选择图片')
            this.localImage = path
            this.preview = path
          },
          fail: (chooseError) => this.showMessage((chooseError && chooseError.errMsg) || '选择图片失败')
        })
      } catch (chooseError) {
        this.showMessage((chooseError && chooseError.message) || '选择图片失败')
      }
    },
    async save() {
      if (this.saving) return
      const draft = normalizeDishDraft(Object.assign({}, this.form, { tags: this.tags }))
      if (!draft.name) return this.showMessage('请填写菜名')
      if (draft.source_url === null) return this.showMessage('来源链接格式不正确')
      this.saving = true
      try {
        let imagePath = this.form.image_path
        if (this.localImage) {
          try {
            const uploaded = await uploadImage(this.localImage)
            if (typeof (uploaded && uploaded.path) !== 'string' || !(uploaded && uploaded.path)) throw new Error('上传图片失败')
            imagePath = uploaded.path
          } catch (uploadError) {
            this.showMessage((uploadError && uploadError.message) || '上传图片失败')
            return
          }
        }
        const payload = normalizeDishDraft(Object.assign({}, this.form, { tags: this.tags, image_path: imagePath }))
        const path = this.id ? `/api/dishes/${this.id}` : '/api/dishes'
        await run(() => request(path, { method: this.id ? 'PUT' : 'POST', data: payload }), '菜品已保存')
        uni.navigateBack()
      } catch (e) {
        // Upload errors are handled above; run already reports save request failures.
      } finally {
        this.saving = false
      }
    },
    back() {
      try { uni.navigateBack() } catch (e) { uni.reLaunch({ url: '/pages/dishes/index' }) }
    },
    showMessage(title) {
      try { uni.showToast({ title, icon: 'none' }) } catch (e) {}
    }
  }
}
</script>

<style scoped>
.state-card { margin-top: 80rpx }
.state-card .btn { margin-top: 22rpx }
.photo { height: 330rpx; border-radius: 34rpx; background: #e5eee7; display: flex; flex-direction: row; align-items: center; justify-content: center; margin-bottom: 35rpx; overflow: hidden; color: #63af7d }
.photo image { width: 100%; height: 100% }
.photo view { display: flex; flex-direction: column; align-items: center }
.picker { display: flex; flex-direction: row; align-items: center }
.group-head { margin: 38rpx 0 20rpx }
.ingredient { display: flex; flex-direction: row; align-items: center; margin-bottom: 12rpx }
.ingredient .input { flex: 1; margin-right: 10rpx }
.ingredient .input:nth-child(2) { flex: 0 0 130rpx; margin-right: 10rpx }
.ingredient .input:nth-child(3) { flex: 0 0 100rpx }
.step { display: flex; flex-direction: row; align-items: flex-start; margin-bottom: 16rpx }
.step > text { padding-top: 22rpx; margin-right: 12rpx }
.save { margin-top: 40rpx }
</style>
