<template>
  <view class="page"> 
    <!-- 页面头部 -->
    <PageHeader title="我的" subtitle="个人中心" />

    <!-- 资料卡 -->
    <view class="profile" @tap="openProfile">
      <Avatar :name="me?.name" :src="assetUrl(me?.avatar_path)" :size="120" />
      <view class="profile-main">
        <view class="name-line">
          <text class="name">{{ me?.name || '未设置昵称' }}</text>
          <text v-if="me?.is_admin" class="badge">管理员</text>
        </view>
        <text class="sub">{{ settings.family_name || '我们的家' }}</text>
      </view>
      <Icon icon="Pencil" :size="18" />
    </view>

    <!-- 管理员功能分组 -->
    <view v-if="me?.is_admin" class="menu-section">
      <text class="menu-heading">管理员功能</text>
      <view class="menu-list">
        <view class="menu-row" @tap="goDishes">
          <view class="menu-icon"><Icon icon="BookOpen" :size="19" /></view>
          <view class="menu-copy">
            <text>菜品管理</text>
            <text class="menu-sub">菜品、菜系与做法</text>
          </view>
          <Icon icon="ChevronRight" :size="17" />
        </view>
        <view class="menu-row" @tap="goCuisines">
          <view class="menu-icon"><Icon icon="UtensilsCrossed" :size="19" /></view>
          <view class="menu-copy">
            <text>菜系管理</text>
            <text class="menu-sub">统一菜系分类</text>
          </view>
          <Icon icon="ChevronRight" :size="17" />
        </view>
        <view class="menu-row" @tap="goIngredients">
          <view class="menu-icon"><Icon icon="Sprout" :size="19" /></view>
          <view class="menu-copy">
            <text>食材管理</text>
            <text class="menu-sub">统一食材名称与别名</text>
          </view>
          <Icon icon="ChevronRight" :size="17" />
        </view>
        <view class="menu-row" @tap="goAdmin">
          <view class="menu-icon"><Icon icon="Settings" :size="19" /></view>
          <view class="menu-copy">
            <text>家庭管理</text>
            <text class="menu-sub">成员与自动饭局</text>
          </view>
          <Icon icon="ChevronRight" :size="17" />
        </view>
      </view>
    </view>

    <!-- 账户分组 -->
    <view class="menu-section">
      <text class="menu-heading">账户</text>
      <view class="menu-list">
        <view class="menu-row" @tap="changePin">
          <view class="menu-icon"><Icon icon="KeyRound" :size="19" /></view>
          <view class="menu-copy">
            <text>修改密码</text>
          </view>
          <Icon icon="ChevronRight" :size="17" />
        </view>
        <view class="menu-row logout" @tap="logout">
          <view class="menu-icon danger"><Icon icon="LogOut" :size="19" /></view>
          <view class="menu-copy">
            <text class="logout-text">{{ loggingOut ? '正在退出...' : '退出登录' }}</text>
          </view>
        </view>
      </view>
    </view>

    <!-- 页脚 -->
    <text class="foot-note">我们的家 · PBJ-COOK</text>

    <!-- 底部导航 -->
    <AppTabBar active="me" />

    <!-- 编辑资料弹层 -->
    <view v-if="showProfile" class="modal-mask" @tap.self="closeProfile">
      <view class="sheet">
        <view class="handle" aria-hidden="true" />
        <view class="sheet-head">
          <text class="section-title">编辑个人资料</text>
          <view class="sheet-close" @tap="closeProfile"><Icon icon="X" :size="18" /></view>
        </view>
        <view class="avatar-edit" @tap="chooseAvatar">
          <Avatar :name="profile.name" :src="profilePreview" :size="168" />
          <text>更换头像</text>
        </view>
        <view class="form-group">
          <text class="label">昵称</text>
          <BaseInput v-model="profile.name" maxlength="12" placeholder="请输入昵称" />
        </view>
        <AppButton block :loading="savingProfile" @tap="saveProfile">保存资料</AppButton>
      </view>
    </view>
  </view>
</template>

<script setup lang="js">
import { onActivated, onMounted, reactive, ref } from 'vue'
import Icon from '../../components/Icons.vue'
import AppTabBar from '../../components/AppTabBar.vue'
import Avatar from '../../components/Avatar.vue'
import PageHeader from '../../components/PageHeader.vue'
import BaseInput from '../../components/BaseInput.vue'
import AppButton from '../../components/AppButton.vue'
import { assetUrl, bootstrap, clearSession, currentUser, request, run, uploadImage } from '../../api/client'
import { validatePin, validateProfileName } from '../../utils/app'

const me = ref(currentUser()), settings = ref({}), showProfile = ref(false)
const savingProfile = ref(false), loggingOut = ref(false), profilePreview = ref(''), localAvatar = ref('')
const profile = reactive({ name: '', avatar_path: null })

async function load() { 
  try { 
    const [bootstrapData, user] = await Promise.all([bootstrap(), request('/api/me')]); 
    settings.value = bootstrapData?.settings || {}; 
    me.value = user; 
    uni.setStorageSync('dacook_user', user) 
  } catch (error) { 
    uni.showToast({ title: error?.message || '个人资料加载失败', icon: 'none' })
  } 
}
function goAdmin() { if (me.value?.is_admin) uni.navigateTo({ url: '/pages/admin/index' }) }
function goDishes() { if (me.value?.is_admin) uni.navigateTo({ url: '/pages/dishes/index' }) }
function goCuisines() { if (me.value?.is_admin) uni.navigateTo({ url: '/pages/cuisines/index' }) }
function goIngredients() { if (me.value?.is_admin) uni.navigateTo({ url: '/pages/ingredients/index' }) }
function openProfile() { 
  const saved = me.value || {}; 
  profile.name = saved.name || ''; 
  profile.avatar_path = saved.avatar_path || null; 
  localAvatar.value = ''; 
  profilePreview.value = assetUrl(profile.avatar_path); 
  showProfile.value = true 
}
function closeProfile() { if (!savingProfile.value) showProfile.value = false }
function chooseAvatar() { 
  try { 
    uni.chooseImage({ 
      count: 1, 
      sizeType: ['compressed'], 
      success: result => { 
        const path = result?.tempFilePaths?.[0]; 
        if (path) { localAvatar.value = path; profilePreview.value = path } 
      } 
    }) 
  } catch {} 
}
async function saveProfile() {
  if (savingProfile.value) return
  const validation = validateProfileName(profile.name); if (validation) return uni.showToast({ title: validation, icon: 'none' })
  savingProfile.value = true
  try {
    await run(async () => { 
      const payload = { name: profile.name.trim(), avatar_path: profile.avatar_path }; 
      if (localAvatar.value) {
        const uploaded = await uploadImage(localAvatar.value, { preset: 'avatar' });
        payload.avatar_path = uploaded?.path || null
      }
      await request('/api/me/profile', { method: 'PUT', data: payload }) 
    }, '资料已保存')
    me.value = await request('/api/me'); uni.setStorageSync('dacook_user', me.value); showProfile.value = false
  } catch {} finally { savingProfile.value = false }
}
function changePin() {
  uni.showModal({ 
    title: '输入原密码', editable: true, placeholderText: '6 位数字', 
    success: result => { 
      if (!result?.confirm) return; 
      const oldPin = String(result.content || ''), error = validatePin(oldPin); 
      if (error) return uni.showToast({ title: error, icon: 'none' }); 
      uni.showModal({ 
        title: '输入新密码', editable: true, placeholderText: '6 位数字', 
        success: async nextResult => { 
          if (!nextResult?.confirm) return; 
          const newPin = String(nextResult.content || ''), nextError = validatePin(newPin); 
          if (nextError) return uni.showToast({ title: nextError, icon: 'none' }); 
          try { 
            await run(() => request('/api/me/pin', { method: 'PUT', data: { old_pin: oldPin, new_pin: newPin } }), '密码已修改') 
          } catch {} 
        } 
      }) 
    } 
  })
}
function logout() { 
  if (loggingOut.value) return; 
  uni.showModal({ 
    title: '确认退出登录？', 
    success: async result => { 
      if (!result?.confirm) return; 
      loggingOut.value = true; 
      try { await request('/api/auth/logout', { method: 'POST' }) } catch {} 
      clearSession(); 
      uni.reLaunch({ url: '/pages/login/index' }); 
      loggingOut.value = false 
    } 
  }) 
}
onMounted(load)
onActivated(load)
</script>

<style scoped>
/* 资料卡 */
.profile {
  display: flex;
  align-items: center;
  gap: 28rpx;
  margin: 24rpx 0;
  padding: 36rpx;
  background: var(--theme-bg-surface);
  border-radius: 44rpx;
  border-left: 8rpx solid var(--theme-action-primary);
  text-align: left;
  color: var(--theme-text-primary);
}
.profile-main {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
}
.name-line {
  display: flex;
  align-items: center;
  gap: 20rpx;
}
.name {
  font-size: 38rpx;
  font-weight: 800;
}
.badge {
  font-size: 22rpx;
  font-weight: 700;
  color: var(--theme-action-primary);
  background: rgba(232, 130, 74, 0.09);
  padding: 4rpx 18rpx;
  border-radius: 999rpx;
}
.sub {
  font-size: 26rpx;
  color: var(--theme-text-secondary);
  margin-top: 4rpx;
}
.profile .menu-copy {
  display: flex;
  min-width: 0;
  flex: 1;
  flex-direction: column;
}

/* 分组菜单 */
.menu-section {
  margin: 28rpx 0;
}
.menu-heading {
  display: block;
  font-size: 24rpx;
  color: var(--theme-text-secondary);
  margin: 0 0 18rpx 12rpx;
}
.menu-list {
  background: var(--theme-bg-surface);
  border-radius: 36rpx;
  overflow: hidden;
}
.menu-row {
  display: flex;
  align-items: center;
  gap: 24rpx;
  width: 100%;
  padding: 30rpx 34rpx;
  border: 0;
  border-bottom: 1px solid var(--theme-border-subtle);
  background: none;
  font-size: 30rpx;
  font-weight: 650;
  color: var(--theme-text-primary);
  text-align: left;
}
.menu-row:last-child {
  border-bottom: 0;
}
.menu-icon {
  width: 70rpx;
  height: 70rpx;
  border-radius: 22rpx;
  background: rgba(232, 130, 74, 0.08);
  color: var(--theme-action-primary);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.menu-copy {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
}
.menu-sub {
  font-size: 24rpx;
  color: var(--theme-text-secondary);
  font-weight: 500;
  margin-top: 2rpx;
}

/* 退出登录 */
.menu-row.logout {
  color: var(--theme-danger);
}
.menu-row.logout .menu-icon.danger {
  background: rgba(181, 71, 71, 0.08);
  color: var(--theme-danger);
}
.logout-text {
  color: var(--theme-danger);
}

/* 页脚 */
.foot-note {
  display: block;
  padding: 48rpx 48rpx 16rpx;
  text-align: center;
  font-size: 22rpx;
  color: rgba(198, 187, 169, 0.8);
}

/* 编辑资料弹层 - Sheet */
.modal-mask {
  position: fixed;
  z-index: 100;
  inset: 0;
  display: flex;
  align-items: flex-end;
  justify-content: center;
  background: var(--theme-modal-scrim);
}
.handle {
  width: 70rpx;
  height: 8rpx;
  border-radius: 4rpx;
  background: var(--theme-control-neutral);
  margin: 0 auto 32rpx;
}
.sheet {
  width: 100%;
  padding: var(--space-4) 48rpx calc(var(--space-6) + env(safe-area-inset-bottom));
  border-radius: 52rpx 52rpx 0 0;
  background: var(--theme-bg-surface);
  flex-direction: column;
}
.sheet-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 32rpx;
}
.sheet-head .section-title {
  font-size: 38rpx;
  font-weight: 700;
}
.sheet-close {
  width: 60rpx;
  height: 60rpx;
  min-height: 60rpx;
  padding: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 0;
  border-radius: 50%;
  background: var(--theme-control-subtle);
  color: var(--theme-text-primary);
}
.avatar-edit {
  display: flex;
  align-items: center;
  flex-direction: column;
  gap: 18rpx;
  margin: 16rpx 0 48rpx;
  border: 0;
  background: none;
  width: 100%;
  color: var(--theme-action-primary);
  font-weight: 600;
  font-size: 26rpx;
}
.form-group {
  margin-bottom: 38rpx;
}
.form-group .label {
  display: block;
  font-size: 26rpx;
  font-weight: 600;
  margin-bottom: 14rpx;
}
.sheet :deep(.app-btn--block) {
  margin-top: 12rpx;
}

/* Flex row overrides */
.profile,
.name-line,
.menu-row,
.sheet-head {
  flex-direction: row;
}
</style>
