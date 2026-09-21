<template>
  <view class="page no-tab login">
    <view class="mark">PBJ-COOK</view>
    <text class="title">{{ settings.family_name || '我们的家' }} 开饭啦！</text>
    <text class="intro">{{ pinLabel }}</text>

    <view v-if="settings.registration_open && !selected" class="segment">
      <view :class="{ on: mode === 'login' }" @tap="switchMode('login')">登录</view>
      <view :class="{ on: mode === 'register' }" @tap="switchMode('register')">注册</view>
    </view>

    <view v-if="mode === 'login' && !selected" class="members">
      <view v-for="member in members" :key="member.id" class="member" @tap="pickMember(member)">
        <Avatar :name="member.name" :src="assetUrl(member.avatar_path)" :size="62"/>
        <text>{{ member.name }}</text>
      </view>
    </view>

    <view v-if="mode === 'login' && selected" class="pin-panel">
      <view class="back-member" @tap="goBack">‹ 换个成员</view>
      <Avatar :name="selected.name" :src="assetUrl(selected.avatar_path)" :size="144"/>
      <text class="member-name">{{ selected.name }}</text>
      <PinPad v-model="pin" :disabled="submitting" @complete="onPinComplete"/>
    </view>

    <view v-if="mode === 'register'" class="register">
      <view class="field">
        <input v-model="name" class="input" maxlength="12" placeholder="你的昵称"/>
      </view>
      <view v-if="settings.has_join_code" class="field">
        <input v-model="joinCode" class="input" placeholder="注册口令"/>
      </view>
      <PinPad v-model="pin" :disabled="submitting" @complete="onPinComplete"/>
    </view>

    <text class="hint">密码仅用于本机登录 · 忘记密码请找管理员</text>
  </view>
</template>

<script setup lang="js">
import { computed, onMounted, ref } from 'vue'
import Avatar from '../../components/Avatar.vue'
import PinPad from '../../components/PinPad.vue'
import { assetUrl, bootstrap, request, run, setSession } from '../../api/client'

const members = ref([]), settings = ref({}), selected = ref(null), mode = ref('login'),
    pin = ref(''), name = ref(''), joinCode = ref(''), submitting = ref(false)

const pinLabel = computed(() => {
  if (selected.value || mode.value === 'register') return '输入 6 位密码'
  return mode.value === 'login' ? '选择你的身份' : '新成员加入家庭'
})

async function init() {
  try {
    const data = await bootstrap({ redirectOnUnauthorized: false })
    if (data.setup_needed) return uni.reLaunch({ url: '/pages/setup/index' })
    members.value = Array.isArray(data.members) ? data.members : []
    settings.value = data.settings || {}
  } catch (error) {
    uni.showToast({ title: error?.message || '无法连接服务器', icon: 'none' })
  }
}

function switchMode(value) {
  mode.value = value
  pin.value = ''
  selected.value = null
}

function pickMember(member) {
  selected.value = member
  pin.value = ''
}

function goBack() {
  selected.value = null
  pin.value = ''
}

function onPinComplete(value) {
  if (mode.value === 'login') loginNow(value)
  else registerNow(value)
}

async function loginNow(value) {
  if (submitting.value || !selected.value) return
  submitting.value = true
  try {
    const data = await run(() => request('/api/auth/login', {
      method: 'POST',
      data: { name: selected.value.name.trim(), pin: value },
      redirectOnUnauthorized: false
    }))
    setSession(data)
    uni.reLaunch({ url: '/pages/home/index' })
  } catch {
    pin.value = ''
  } finally {
    submitting.value = false
  }
}

async function registerNow(value) {
  if (submitting.value) return
  name.value = name.value.trim()
  joinCode.value = joinCode.value.trim()
  if (!name.value) {
    pin.value = ''
    return uni.showToast({ title: '请填写昵称', icon: 'none' })
  }
  submitting.value = true
  try {
    const data = await run(() => request('/api/auth/register', {
      method: 'POST',
      data: { name: name.value, pin: value, join_code: joinCode.value },
      redirectOnUnauthorized: false
    }))
    setSession(data)
    uni.reLaunch({ url: '/pages/home/index' })
  } catch {
    pin.value = ''
  } finally {
    submitting.value = false
  }
}

onMounted(init)
</script>

<style scoped>
/* 瓷 · 设计系统变量 */
.login {
  --porcelain: #FAF7F1;
  --card: #FFFFFF;
  --clay: #EFE5D8;
  --ink: #27211A;
  --muted: #8B7F70;
  --tomato: #D9482B;
  --tomato-deep: #B93517;
  --moss: #56735A;
  --butter: #F3C64B;

  display: flex;
  min-height: 100vh;
  padding: 144rpx 56rpx 96rpx;
  align-items: center;
  flex-direction: column;
  background: var(--porcelain);
}

/* ---- 品牌标识 ---- */
.mark {
  font-size: 26rpx;
  font-weight: 800;
  letter-spacing: 8rpx;
  text-indent: 8rpx;
  color: var(--tomato);
  margin-bottom: 52rpx;
}

/* ---- 大标题 ---- */
.title {
  font-family: "Songti SC", "STSong", "Noto Serif CJK SC", serif;
  font-size: 56rpx;
  font-weight: 800;
  line-height: 1.3;
  color: var(--ink);
  text-align: center;
}

/* ---- 副标题 ---- */
.intro {
  margin-top: 16rpx;
  font-size: 28rpx;
  color: var(--muted);
  text-align: center;
}

/* ---- 登录/注册切换 ---- */
.segment {
  display: flex;
  margin-top: 52rpx;
  padding: 8rpx;
  background: var(--clay);
  border-radius: 1998rpx;
  width: 440rpx;
  align-self: center;
}

.segment view {
  flex: 1;
  padding: 18rpx 0;
  border: 0;
  border-radius: 1998rpx;
  background: none;
  font-size: 28rpx;
  font-weight: 700;
  color: var(--muted);
  cursor: pointer;
  transition: background 0.15s ease, color 0.15s ease;
  text-align: center;
}

.segment view.on {
  background: var(--card);
  color: var(--ink);
  box-shadow: 0 4rpx 16rpx rgba(90, 60, 30, 0.08);
}

/* ---- 成员选择网格 ---- */
.members {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 28rpx;
  margin-top: 68rpx;
  width: 100%;
  max-width: 960rpx;
  align-self: center;
}

.member {
  border: 0;
  background: none;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 18rpx;
  padding: 24rpx 8rpx;
  border-radius: 36rpx;
  transition: background 0.15s ease;
}

.member:hover {
  background: var(--card);
}

.member text {
  font-size: 27rpx;
  font-weight: 650;
  color: var(--ink);
}

/* ---- PIN 面板 ---- */
.pin-panel {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-top: 20rpx;
  width: 100%;
  max-width: 960rpx;
  align-self: center;
}

.back-member {
  border: 0;
  background: none;
  color: var(--muted);
  font-size: 27rpx;
  cursor: pointer;
  padding: 16rpx 0;
  align-self: center;
}

.member-name {
  margin-top: 20rpx;
  margin-bottom: 40rpx;
  font-size: 34rpx;
  font-weight: 750;
  color: var(--ink);
  align-self: center;
}

/* ---- PinPad 组件居中 & 宽度 100%（小程序组件宿主标签需要） ---- */
.pin-panel > :deep(pin-pad),
.register > :deep(pin-pad) {
  width: 100%;
}
.pin-panel > :deep(.pin-wrap),
.register > :deep(.pin-wrap) {
  align-self: center;
  width: 100%;
}

/* ---- 注册表单 ---- */
.register {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-top: 48rpx;
  width: 100%;
  max-width: 960rpx;
  align-self: center;
}

.field {
  width: 100%;
  margin-bottom: 28rpx;
}

.input {
  width: 100%;
  padding: 26rpx 32rpx;
  border: 3rpx solid var(--clay);
  border-radius: 28rpx;
  background: var(--card);
  font-size: 30rpx;
  font-family: inherit;
  color: var(--ink);
  outline: none;
  transition: border-color 0.15s ease;
}

.input:focus {
  border-color: var(--tomato);
}

.input::placeholder {
  color: #B8AC9C;
}

/* ---- 底部提示 ---- */
.hint {
  margin-top: auto;
  padding-top: 80rpx;
  font-size: 24rpx;
  color: var(--muted);
  text-align: center;
}

/* ---- 焦点可访问性 ---- */
:focus-visible {
  outline: 4rpx solid var(--tomato);
  outline-offset: 6rpx;
  border-radius: 12rpx;
}
</style>
