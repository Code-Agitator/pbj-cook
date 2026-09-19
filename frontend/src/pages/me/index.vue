<template>
  <view class="page"> 
    <PageHeader title="我的" subtitle="个人中心" />
    <button class="profile" @tap="openProfile">
      <Avatar :name="me?.name" :src="assetUrl(me?.avatar_path)" :size="112" />
      <view class="profile-meta"><view class="name-line"><text class="name">{{ me?.name || '未设置昵称' }}</text><text v-if="me?.is_admin" class="badge">管理员</text></view><text class="subtle">{{ settings.family_name || '' }}</text></view>
      <Icon icon="Pencil" :size="20" />
    </button>

    <view v-if="loadError" class="state panel"><text>{{ loadError }}</text><button class="btn tonal" @tap="load">重试</button></view>

    <view v-if="me?.is_admin" class="menu-section">
      <text class="menu-heading">管理员功能</text>
      <view class="menu-list">
        <view class="menu-row" @tap="goDishes"><view class="menu-icon"><Icon icon="BookOpen" :size="20" /></view><view class="menu-copy"><text>菜品管理</text><text class="subtle">菜品、菜系与做法</text></view><Icon icon="ChevronRight" :size="18" /></view>
        <view class="menu-row" @tap="goAdmin"><view class="menu-icon"><Icon icon="Settings" :size="20" /></view><view class="menu-copy"><text>家庭管理</text><text class="subtle">成员与自动饭局</text></view><Icon icon="ChevronRight" :size="18" /></view>
      </view>
    </view>

    <view class="menu-section">
      <text class="menu-heading">账户</text>
      <view class="menu-list">
        <view class="menu-row" @tap="changePin"><view class="menu-icon"><Icon icon="KeyRound" :size="20" /></view><view class="menu-copy"><text>修改密码</text></view><Icon icon="ChevronRight" :size="18" /></view>
        <view class="menu-row logout" @tap="logout"><view class="menu-icon"><Icon icon="LogOut" :size="20" /></view><view class="menu-copy"><text>{{ loggingOut ? '正在退出...' : '退出登录' }}</text></view></view>
      </view>
    </view>

    <AppTabBar active="me" />
    <view v-if="showProfile" class="modal-mask" @tap.self="closeProfile"><view class="sheet">
      <view class="sheet-title"><text class="section-title">编辑个人资料</text><button class="close" @tap="closeProfile"><Icon icon="X" :size="18" /></button></view>
      <view class="avatar-edit" @tap="chooseAvatar"><Avatar :name="profile.name" :src="profilePreview" :size="140" /><text>更换头像</text></view>
      <view class="form-group"><text class="label">昵称</text><input v-model="profile.name" class="input" maxlength="12" /></view>
      <button class="btn block" :disabled="savingProfile" @tap="saveProfile">{{ savingProfile ? '保存中...' : '保存资料' }}</button>
    </view></view>
  </view>
</template>

<script setup lang="js">
import { onActivated, onMounted, reactive, ref } from 'vue'
import Icon from '../../components/Icons.vue'
import AppTabBar from '../../components/AppTabBar.vue'
import PageHeader from '../../components/PageHeader.vue'
import Avatar from '../../components/Avatar.vue'
import { assetUrl, bootstrap, clearSession, currentUser, request, run, uploadImage } from '../../api/client'
import { validatePin, validateProfileName } from '../../utils/app'

const me = ref(currentUser()), settings = ref({}), showProfile = ref(false), loadError = ref('')
const savingProfile = ref(false), loggingOut = ref(false), profilePreview = ref(''), localAvatar = ref('')
const profile = reactive({ name: '', avatar_path: null })

async function load() { loadError.value = ''; try { const [bootstrapData, user] = await Promise.all([bootstrap(), request('/api/me')]); settings.value = bootstrapData?.settings || {}; me.value = user; uni.setStorageSync('dacook_user', user) } catch (error) { loadError.value = error?.message || '个人资料加载失败' } }
function goAdmin() { if (me.value?.is_admin) uni.navigateTo({ url: '/pages/admin/index' }) }
function goDishes() { if (me.value?.is_admin) uni.navigateTo({ url: '/pages/dishes/index' }) }
function openProfile() { const saved = me.value || {}; profile.name = saved.name || ''; profile.avatar_path = saved.avatar_path || null; localAvatar.value = ''; profilePreview.value = assetUrl(profile.avatar_path); showProfile.value = true }
function closeProfile() { if (!savingProfile.value) showProfile.value = false }
function chooseAvatar() { try { uni.chooseImage({ count: 1, sizeType: ['compressed'], success: result => { const path = result?.tempFilePaths?.[0]; if (path) { localAvatar.value = path; profilePreview.value = path } } }) } catch {} }
async function saveProfile() {
  if (savingProfile.value) return
  const validation = validateProfileName(profile.name); if (validation) return uni.showToast({ title: validation, icon: 'none' })
  savingProfile.value = true
  try {
    await run(async () => { const payload = { name: profile.name.trim(), avatar_path: profile.avatar_path }; if (localAvatar.value) { const uploaded = await uploadImage(localAvatar.value); payload.avatar_path = uploaded?.path || null } await request('/api/me/profile', { method: 'PUT', data: payload }) }, '资料已保存')
    me.value = await request('/api/me'); uni.setStorageSync('dacook_user', me.value); showProfile.value = false
  } catch {} finally { savingProfile.value = false }
}
function changePin() {
  uni.showModal({ title: '输入原密码', editable: true, placeholderText: '6 位数字', success: result => { if (!result?.confirm) return; const oldPin = String(result.content || ''), error = validatePin(oldPin); if (error) return uni.showToast({ title: error, icon: 'none' }); uni.showModal({ title: '输入新密码', editable: true, placeholderText: '6 位数字', success: async nextResult => { if (!nextResult?.confirm) return; const newPin = String(nextResult.content || ''), nextError = validatePin(newPin); if (nextError) return uni.showToast({ title: nextError, icon: 'none' }); try { await run(() => request('/api/me/pin', { method: 'PUT', data: { old_pin: oldPin, new_pin: newPin } }), '密码已修改') } catch {} } }) } })
}
function logout() { if (loggingOut.value) return; uni.showModal({ title: '确认退出登录？', success: async result => { if (!result?.confirm) return; loggingOut.value = true; try { await request('/api/auth/logout', { method: 'POST' }) } catch {} clearSession(); uni.reLaunch({ url: '/pages/login/index' }); loggingOut.value = false } }) }
onMounted(load)
onActivated(load)
</script>

<style scoped>
.profile{display:flex;width:100%;min-height:176rpx;padding:28rpx 24rpx;align-items:center;border-bottom:1px solid var(--theme-border-subtle);background:transparent;color:var(--theme-text-primary);text-align:left}.profile-meta{display:flex;min-width:0;margin-left:24rpx;flex:1;flex-direction:column}.name-line{display:flex;align-items:center}.name{margin-right:14rpx;font-size:36rpx;font-weight:650}.menu-section{margin-top:54rpx}.menu-heading{display:block;margin-bottom:14rpx;color:var(--theme-text-secondary);font-size:22rpx}.menu-list{border-top:1px solid var(--theme-border-subtle)}.state{margin-top:20rpx}.state .btn{margin-top:18rpx}.menu-row{display:flex;min-height:116rpx;padding:0 24rpx;align-items:center;border-bottom:1px solid var(--theme-border-subtle);font-size:28rpx}.menu-icon{display:flex;width:58rpx;height:58rpx;margin-right:20rpx;align-items:center;justify-content:center;border-radius:10rpx;background:var(--theme-bg-menu-icon);color:var(--theme-text-action)}.menu-copy{display:flex;min-width:0;flex:1;flex-direction:column}.logout{color:var(--theme-danger)}.avatar-edit{display:flex;margin:22rpx 0 34rpx;align-items:center;flex-direction:column;color:var(--theme-text-action);font-size:24rpx}.avatar-edit text{margin-top:12rpx}.sheet-title{display:flex;align-items:center;justify-content:space-between}.close{display:flex;width:62rpx;height:62rpx;min-height:62rpx;padding:0;align-items:center;justify-content:center;border-radius:50%;background:var(--theme-control-subtle);color:var(--theme-text-primary)}.state{margin-top:20rpx}.state .btn{margin-top:18rpx}
.profile,.name-line,.menu-row,.sheet-title{flex-direction:row}
</style>
