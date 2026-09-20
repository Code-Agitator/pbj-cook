<template>
  <view class="page no-tab dish-form-page">
    <view v-if="unauthorized" class="state panel">
      <text>仅管理员可管理菜品</text>
      <view class="btn tonal" @tap="uni.reLaunch({ url: '/pages/me/index' })">返回我的</view>
    </view>
    <view v-else-if="loading && !ready" class="state">正在加载菜品编辑器...</view>
    <view v-else-if="error && !ready" class="state panel">
      <text>{{ error }}</text>
      <view class="btn tonal" @tap="load">重试</view>
      <view class="btn ghost" @tap="uni.reLaunch({ url: '/pages/dishes/index' })">返回菜品管理</view>
    </view>
    <template v-else-if="ready">
      <!-- 顶部 -->
      <view class="top">
        <BackButton label="菜品管理" fallback-url="/pages/dishes/index"/>
        <view class="top-text">
          <view class="title">{{ id ? '编辑菜品' : '添加菜品' }}</view>
        </view>
      </view>
      <view class="prompt">录好的菜，家人点饭局时就能点到</view>

      <!-- 基本信息 -->
      <section class="section">
        <h2>基本信息</h2>

        <view class="field">
          <label for="fName">菜名 <span class="optional">必填</span></label>
          <input id="fName" v-model="form.name" type="text" maxlength="30" placeholder="例如：红烧肉" class="input"/>
        </view>

        <view class="field">
          <label for="fDesc">一句话介绍 <span class="optional">选填</span></label>
          <textarea id="fDesc" v-model="form.description" maxlength="300" rows="2" placeholder="口味、特色或家人的偏好" class="input"></textarea>
        </view>

        <view class="field">
          <label>菜系</label>
          <view class="chips" role="group" aria-label="选择菜系">
            <view v-for="cuisine in cuisines" :key="cuisine.id"
                  class="chip"
                  :class="{ on: form.cuisine_id === cuisine.id }"
                  @tap="form.cuisine_id = cuisine.id">
              <span v-if="cuisine.emoji">{{ cuisine.emoji }}</span>
              <span>{{ cuisine.name }}</span>
            </view>
          </view>
        </view>

        <view class="field">
          <label>标签 <span class="optional">可多选</span></label>
          <view class="tag-chips" role="group" aria-label="选择标签">
            <view v-for="tag in availableTags" :key="tag"
                  class="chip"
                  :class="{ on: selectedTags.includes(tag), alt: customTags.includes(tag) }"
                  @tap="toggleTag(tag)">
              {{ tag }}
            </view>
            <view class="add-tag" @tap="addCustomTag">
              <Icon icon="Plus" :size="13"/>
              自定义
            </view>
          </view>
          <text class="hint">最多选 3 个标签</text>
        </view>
      </section>

      <!-- 图片 -->
      <section class="section">
        <h2>菜品图片 <span class="optional">选填</span></h2>
        <view class="upload" @tap="choose">
          <view class="upload-thumb" :style="preview ? { backgroundImage: 'url(' + preview + ')' } : {}">
            <text v-if="!preview">{{ form.name ? form.name.charAt(0) : '菜' }}</text>
          </view>
          <view class="upload-main">
            <text class="t">{{ preview ? '重新上传' : '上传成品图' }}</text>
            <text class="m">拍一张出锅的照片，家人看着更好选</text>
          </view>
        </view>
      </section>

      <!-- 食材 -->
      <section class="section">
        <h2>食材 <span class="optional">{{ form.ingredients.length }}/30</span></h2>
        <view class="ing-head" aria-hidden="true">
          <text>名称</text>
          <text>用量</text>
          <text>单位</text>
          <text></text>
        </view>
        <view id="ingRows">
          <view v-for="(item, idx) in form.ingredients" :key="item.key" class="ing-row">
            <input v-model="item.name" type="text" placeholder="食材" class="input" aria-label="食材名称"/>
            <input v-model="item.quantity" type="text" placeholder="用量" class="input" aria-label="用量"/>
            <input v-model="item.unit" type="text" placeholder="单位" class="input" aria-label="单位"/>
            <view class="row-remove" @tap="removeIngredient(item.key)" :class="{ hidden: form.ingredients.length <= 1 }">
              <Icon icon="X" :size="16"/>
            </view>
          </view>
        </view>
        <view class="row-add" :class="{ disabled: form.ingredients.length >= 30 }" @tap="addIngredient">
          <Icon icon="Plus" :size="15"/>
          添加食材
        </view>
      </section>

      <!-- 做法 -->
      <section class="section">
        <h2>做法 <span class="optional">{{ form.steps.length }}/20</span></h2>
        <view id="stepRows">
          <view v-for="(step, index) in form.steps" :key="step.key" class="step-row">
            <view class="step-no">{{ index + 1 }}</view>
            <textarea v-model="step.body" rows="1" placeholder="这一步怎么做" class="input" :aria-label="'第 ' + (index + 1) + ' 步'"></textarea>
            <view class="row-remove" @tap="removeStep(step.key)" :class="{ hidden: form.steps.length <= 1 }">
              <Icon icon="X" :size="16"/>
            </view>
          </view>
        </view>
        <view class="row-add" :class="{ disabled: form.steps.length >= 20 }" @tap="addStep">
          <Icon icon="Plus" :size="15"/>
          添加一步
        </view>
      </section>

      <!-- 来源链接 -->
      <section class="section">
        <h2>其他 <span class="optional">选填</span></h2>
        <view class="field">
          <label for="fSource">来源链接</label>
          <input id="fSource" v-model="form.source_url" type="text" placeholder="菜谱或视频链接" class="input"/>
        </view>
      </section>

      <!-- 保存 -->
      <view class="cta" :class="{ disabled: saving }" @tap="save">
        <Icon icon="Check" :size="18"/>
        {{ saving ? '保存中...' : '保存菜品' }}
      </view>

      <footer class="foot">
        <text>保存后立即出现在菜品库</text>
      </footer>
    </template>
  </view>
</template>

<script setup lang="js">
import {computed, onMounted, reactive, ref} from 'vue'
import BackButton from '../../components/BackButton.vue'
import Icon from '../../components/Icons.vue'
import {assetUrl, currentUser, request, run, uploadImage} from '../../api/client'
import {cuisineIdFromPicker, normalizeDishDraft} from '../../utils/app'

let rowSequence = 0

function newIngredient(item = {}) {
  rowSequence += 1;
  return {
    key: `ingredient-${rowSequence}`,
    name: typeof item.name === 'string' ? item.name : '',
    quantity: typeof item.quantity === 'string' ? item.quantity : '',
    unit: typeof item.unit === 'string' ? item.unit : ''
  }
}

function newStep(body = '') {
  rowSequence += 1;
  return {key: `step-${rowSequence}`, body: typeof body === 'string' ? body : ''}
}

const id = ref(''), cuisines = ref([]), preview = ref(''), localImage = ref('')
const loading = ref(false), ready = ref(false), error = ref(''), saving = ref(false), unauthorized = ref(false)
const selectedTags = ref([]), customTags = ref([])
const availableTags = computed(() => Array.from(new Set([...predefinedTags, ...customTags.value])).slice(0, 12))

const predefinedTags = ['下饭', '清淡', '微辣', '快手', '硬菜', '素食', '汤羹', '面点', '家常', '宴客', '懒人', '营养']

const form = reactive({
  name: '',
  description: '',
  image_path: null,
  cuisine_id: null,
  source_url: '',
  ingredients: [newIngredient()],
  steps: [newStep()]
})

async function load() {
  if (currentUser()?.is_admin !== true) {
    unauthorized.value = true;
    ready.value = false;
    return false
  }
  if (loading.value) return false
  loading.value = true;
  ready.value = false;
  error.value = ''
  try {
    const loadedCuisines = await request('/api/cuisines');
    if (!Array.isArray(loadedCuisines)) throw new Error('菜系加载失败');
    cuisines.value = loadedCuisines;
    if (id.value) {
      const dish = await request(`/api/dishes/${id.value}`);
      if (!dish || typeof dish !== 'object') throw new Error('菜品加载失败');
      applyDish(dish)
    }
    ready.value = true;
    return true
  } catch (loadError) {
    error.value = loadError?.message || '菜品加载失败';
    return false
  } finally {
    loading.value = false
  }
}

function applyDish(dish) {
  form.name = typeof dish.name === 'string' ? dish.name : '';
  form.description = typeof dish.description === 'string' ? dish.description : '';
  form.image_path = typeof dish.image_path === 'string' ? dish.image_path : null;
  form.cuisine_id = typeof dish.cuisine_id === 'string' ? dish.cuisine_id : null;
  form.source_url = typeof dish.source_url === 'string' ? dish.source_url : '';
  form.ingredients = (Array.isArray(dish.ingredients) ? dish.ingredients : []).map(newIngredient);
  form.steps = (Array.isArray(dish.steps) ? dish.steps : []).map(step => newStep(step?.body));
  selectedTags.value = Array.isArray(dish.tags) ? dish.tags.filter(Boolean) : [];
  customTags.value = selectedTags.value.filter(tag => !predefinedTags.includes(tag));
  preview.value = assetUrl(form.image_path);
  localImage.value = ''
}

function showMessage(title) {
  uni.showToast({title, icon: 'none'})
}

function toggleTag(tag) {
  const idx = selectedTags.value.indexOf(tag)
  if (idx >= 0) {
    selectedTags.value.splice(idx, 1)
  } else {
    if (selectedTags.value.length >= 3) return showMessage('最多选 3 个标签');
    selectedTags.value.push(tag)
  }
}

function addCustomTag() {
  try {
    uni.showModal({
      title: '新标签',
      editable: true,
      placeholderText: '输入标签名称（最多 6 字）',
      success: res => {
        if (!res.confirm) return
        let name = (res.content || '').trim().slice(0, 6)
        if (!name) return
        if (availableTags.value.includes(name)) return showMessage('标签已存在')
        customTags.value.push(name)
        selectedTags.value.push(name)
      }
    })
  } catch {}
}

function addIngredient() {
  if (form.ingredients.length >= 30) return showMessage('食材最多 30 项');
  form.ingredients.push(newIngredient())
}

function removeIngredient(key) {
  if (form.ingredients.length <= 1) return
  form.ingredients = form.ingredients.filter(item => item.key !== key)
}

function addStep() {
  if (form.steps.length >= 20) return showMessage('步骤最多 20 项');
  form.steps.push(newStep())
}

function removeStep(key) {
  if (form.steps.length <= 1) return
  form.steps = form.steps.filter(step => step.key !== key)
}

function choose() {
  uni.chooseImage({
    count: 1, sizeType: ['compressed'], success: result => {
      const path = result?.tempFilePaths?.[0];
      if (!path) return showMessage('未选择图片');
      localImage.value = path;
      preview.value = path
    }, fail: chooseError => showMessage(chooseError?.errMsg || '选择图片失败')
  })
}

async function save() {
  if (saving.value || unauthorized.value) return
  const tags = selectedTags.value
  const draft = normalizeDishDraft({...form, tags});
  if (!draft.name) return showMessage('请填写菜名');
  if (draft.source_url === null) return showMessage('来源链接格式不正确')
  saving.value = true
  try {
    let imagePath = form.image_path;
    if (localImage.value) {
      const uploaded = await uploadImage(localImage.value);
      if (!uploaded?.path) throw new Error('上传图片失败');
      imagePath = uploaded.path
    }
    const payload = normalizeDishDraft({...form, tags, image_path: imagePath});
    await run(() => request(id.value ? `/api/dishes/${id.value}` : '/api/dishes', {
      method: id.value ? 'PUT' : 'POST',
      data: payload
    }), '菜品已保存');
    uni.navigateBack()
  } catch (saveError) {
    if (saveError?.message) showMessage(saveError.message)
  } finally {
    saving.value = false
  }
}

let isFirstLoad = true

onMounted(() => {
  try {
    const pages = typeof getCurrentPages === 'function' ? getCurrentPages() : []
    const options = pages[pages.length - 1]?.options || {}
    id.value = typeof options.id === 'string' ? options.id.trim() : ''
  } catch {
  }
  load()
})
</script>

<style scoped>
.dish-form-page {
  max-width: 820px;
  padding-bottom: 60rpx;
}

.state .btn {
  margin-top: 20rpx;
}

/* ---------- 顶部 ---------- */
.top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 32rpx 28rpx 0;
  flex-direction: row;
}

.eyebrow {
  font-size: 22rpx;
  color: var(--theme-text-secondary);
  letter-spacing: 0.5px;
}

.title {
  font-size: 38rpx;
  font-weight: 800;
  line-height: 1.3;
  color: var(--theme-text-primary);
}

.prompt {
  padding: 8rpx 28rpx 0;
  font-size: 24rpx;
  color: var(--theme-text-secondary);
}

/* ---------- 表单区块 ---------- */
.section {
  margin-top: 48rpx;
  padding: 0 24rpx;
}

.section > h2 {
  font-size: 24rpx;
  font-weight: 700;
  color: var(--theme-text-secondary);
  margin-bottom: 20rpx;
  display: flex;
  align-items: center;
  gap: 12rpx;
  flex-direction: row;
}

.section > h2::after {
  content: "";
  flex: 1;
  height: 1px;
  background: var(--theme-border-subtle);
}

.section > h2 .optional {
  font-weight: 500;
  font-size: 20rpx;
  color: var(--theme-text-tertiary);
}

/* ---------- 字段 ---------- */
.field label {
  display: block;
  font-size: 24rpx;
  font-weight: 600;
  margin-bottom: 10rpx;
  color: var(--theme-text-primary);
}

.field label .optional {
  color: var(--theme-text-secondary);
  font-weight: 500;
  font-size: 20rpx;
}

.field .input {
  width: 100%;
  padding: 22rpx 26rpx;
  border: 0;
  border-radius: 28rpx;
  background: var(--theme-bg-surface);
  font-size: 27rpx;
  font-family: inherit;
  color: var(--theme-text-primary);
  outline: none;
  transition: box-shadow 0.15s ease;
  display: flex;
  align-items: center;
  box-shadow: 0 4rpx 16rpx rgba(25, 34, 28, 0.06), 0 1px 2rpx rgba(25, 34, 28, 0.04);
}

.field textarea.input {
  min-height: 100rpx;
  padding-top: 22rpx;
  resize: none;
  line-height: 1.6;
  box-shadow: 0 4rpx 16rpx rgba(25, 34, 28, 0.06), 0 1px 2rpx rgba(25, 34, 28, 0.04);
}

.field .input:focus {
  box-shadow: 0 6rpx 24rpx rgba(232, 130, 74, 0.18), 0 2rpx 4rpx rgba(232, 130, 74, 0.1);
}

.field .input::placeholder {
  color: var(--palette-placeholder, #B8AC9C);
}

.field + .field {
  margin-top: 24rpx;
}

.field .hint {
  margin-top: 10rpx;
  font-size: 20rpx;
  color: var(--theme-text-secondary);
  display: block;
}

/* ---------- 菜系/标签胶囊 ---------- */
.chips {
  display: flex;
  flex-direction: row;
  gap: 12rpx;
  flex-wrap: wrap;
}

.chip {
  display: inline-flex;
  flex-direction: row;
  align-items: center;
  gap: 6rpx;
  padding: 12rpx 24rpx;
  border: 1.5px solid var(--theme-border-subtle);
  border-radius: 999px;
  background: var(--theme-bg-surface);
  color: var(--theme-text-secondary);
  font-size: 24rpx;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s ease;
}

.chip.on {
  border-color: var(--theme-action-primary);
  color: var(--theme-action-primary);
  background: rgba(232, 130, 74, 0.06);
}

.chip.on.alt {
  border-color: #e8c04a;
  color: #6B4A00;
  background: rgba(243, 198, 75, 0.14);
}

.chip:active {
  transform: scale(0.96);
}

.tag-chips {
  display: flex;
  gap: 12rpx;
  flex-wrap: wrap;
  flex-direction: row;
}

.add-tag {
  display: inline-flex;
  align-items: center;
  gap: 8rpx;
  padding: 12rpx 24rpx;
  border: 1.5px dashed var(--theme-border-subtle);
  border-radius: 999px;
  background: none;
  color: var(--theme-text-secondary);
  font-size: 24rpx;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s ease;
  flex-direction: row;
}

.add-tag:active {
  border-color: var(--theme-action-primary);
  color: var(--theme-action-primary);
}

/* ---------- 图片上传 ---------- */
.upload {
  display: flex;
  align-items: center;
  gap: 24rpx;
  padding: 22rpx;
  background: var(--theme-bg-surface);
  border: 1.5px solid var(--theme-border-subtle);
  border-radius: 26rpx;
  cursor: pointer;
  width: 100%;
  text-align: left;
  flex-direction: row;
}

.upload:active {
  border-color: var(--theme-action-primary);
}

.upload-thumb {
  width: 100rpx;
  height: 100rpx;
  border-radius: 18rpx;
  background: linear-gradient(150deg, #E07B5F, #C43D20);
  background-size: cover;
  background-position: center;
  color: rgba(255, 255, 255, 0.9);
  font-size: 36rpx;
  font-weight: 800;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.upload-main {
  min-width: 0;
}

.upload-main .t {
  display: block;
  font-size: 26rpx;
  font-weight: 650;
  color: var(--theme-text-primary);
}

.upload-main .m {
  display: block;
  margin-top: 4rpx;
  font-size: 22rpx;
  color: var(--theme-text-secondary);
}

/* ---------- 食材行 ---------- */
.ing-row {
  display: grid;
  grid-template-columns: 1.4fr 0.8fr 0.7fr 64rpx;
  gap: 12rpx;
  align-items: center;
}

.ing-row + .ing-row {
  margin-top: 16rpx;
}

.ing-row .input {
  width: 100%;
  padding: 18rpx 18rpx;
  border: 0;
  border-radius: 22rpx;
  background: var(--theme-bg-surface);
  font-size: 26rpx;
  font-family: inherit;
  color: var(--theme-text-primary);
  outline: none;
  display: flex;
  align-items: center;
  box-shadow: 0 4rpx 16rpx rgba(25, 34, 28, 0.06), 0 1px 2rpx rgba(25, 34, 28, 0.04);
}

.ing-row .input:focus {
  box-shadow: 0 6rpx 24rpx rgba(232, 130, 74, 0.18), 0 2rpx 4rpx rgba(232, 130, 74, 0.1);
}

.ing-row .input::placeholder {
  color: var(--palette-placeholder, #B8AC9C);
}

.ing-head {
  display: grid;
  grid-template-columns: 1.4fr 0.8fr 0.7fr 64rpx;
  gap: 12rpx;
  margin-bottom: 12rpx;
  font-size: 20rpx;
  color: var(--theme-text-secondary);
  flex-direction: row;
}

.ing-head span {
  padding-left: 18rpx;
}

.row-remove {
  width: 64rpx;
  height: 64rpx;
  min-height: 64rpx;
  border: 0;
  border-radius: 18rpx;
  background: none;
  color: var(--theme-text-secondary);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.15s ease;
}

.row-remove:active {
  color: var(--theme-danger);
  background: var(--theme-danger-subtle);
}

.row-remove.hidden {
  opacity: 0;
  pointer-events: none;
}

.row-add {
  margin-top: 18rpx;
  width: 100%;
  padding: 18rpx 0;
  border: 1.5px dashed var(--theme-border-subtle);
  border-radius: 20rpx;
  background: none;
  color: var(--theme-text-secondary);
  font-size: 26rpx;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10rpx;
  transition: all 0.15s ease;
  flex-direction: row;
}

.row-add:active {
  border-color: var(--theme-action-primary);
  color: var(--theme-action-primary);
}

.row-add.disabled {
  opacity: 0.48;
  pointer-events: none;
}

/* ---------- 做法步骤 ---------- */
.step-row {
  display: grid;
  grid-template-columns: 42rpx 1fr 64rpx;
  gap: 16rpx;
  align-items: flex-start;
}

.step-row + .step-row {
  margin-top: 16rpx;
}

.step-no {
  width: 42rpx;
  height: 42rpx;
  margin-top: 14rpx;
  border-radius: 50%;
  background: var(--theme-bg-subtle);
  color: var(--theme-text-primary);
  font-size: 20rpx;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  font-variant-numeric: tabular-nums;
  flex-shrink: 0;
}

.step-row .input {
  width: 100%;
  padding: 18rpx 18rpx;
  border: 0;
  border-radius: 22rpx;
  background: var(--theme-bg-surface);
  font-size: 26rpx;
  font-family: inherit;
  color: var(--theme-text-primary);
  outline: none;
  resize: none;
  line-height: 1.55;
  min-height: 76rpx;
  box-shadow: 0 4rpx 16rpx rgba(25, 34, 28, 0.06), 0 1px 2rpx rgba(25, 34, 28, 0.04);
}

.step-row .input:focus {
  box-shadow: 0 6rpx 24rpx rgba(232, 130, 74, 0.18), 0 2rpx 4rpx rgba(232, 130, 74, 0.1);
}

.step-row .input::placeholder {
  color: var(--palette-placeholder, #B8AC9C);
}

/* ---------- 保存按钮 ---------- */
.cta {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10rpx;
  width: calc(100% - 48rpx);
  margin: 48rpx 24rpx 0;
  padding: 26rpx;
  border: 0;
  border-radius: 26rpx;
  background: var(--theme-action-primary);
  color: var(--theme-action-on-primary);
  font-size: 30rpx;
  font-weight: 700;
  cursor: pointer;
  box-shadow: 0 10rpx 30rpx rgba(232, 130, 74, 0.28);
  transition: background 0.15s ease, transform 0.1s ease;
  flex-direction: row;
}

.cta:active {
  transform: scale(0.98);
  filter: brightness(0.96);
}

.cta.disabled {
  opacity: 0.48;
  pointer-events: none;
  box-shadow: none;
}

/* ---------- 底部 ---------- */
.foot {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 28rpx 24rpx 8rpx;
  font-size: 22rpx;
  color: var(--theme-text-secondary);
  flex-direction: row;
}

/* ---------- 焦点样式 ---------- */
:focus-visible {
  outline: 2px solid var(--theme-focus-ring);
  outline-offset: 3px;
}

@media (hover: hover) {
  .cta:hover {
    filter: brightness(0.96);
  }

  .chip:hover {
    border-color: var(--theme-action-primary);
  }
}
</style>
