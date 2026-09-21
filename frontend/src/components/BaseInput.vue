<template>
  <view class="base-input-wrap" :class="{ 'base-input-wrap--disabled': disabled, ['base-input-wrap--' + variant]: true }">

    <!-- 日期 / 时间 / 日期时间选择器 -->
    <picker
      v-if="isPicker"
      :mode="mode"
      :value="modelValue"
      :start="start"
      :end="end"
      :fields="pickerFields"
      @change="onPickerChange"
    >
      <view class="input input--picker" :class="{ 'input--has-prefix': $slots.prefix || prefixIcon, 'input--has-suffix': $slots.suffix || suffixIcon, ['input--' + variant]: variant !== 'default' }">
        <text v-if="!modelValue" class="input--placeholder">{{ placeholder }}</text>
        <text v-else>{{ displayValue }}</text>
      </view>
    </picker>

    <!-- input / textarea -->
    <template v-else>
      <input
        v-if="type !== 'textarea'"
        :value="modelValue"
        :type="type"
        :placeholder="placeholder"
        :disabled="disabled"
        :readonly="readonly"
        :maxlength="maxlength"
        class="input"
        :class="{ 'input--has-prefix': $slots.prefix || prefixIcon, 'input--has-suffix': $slots.suffix || suffixIcon || (clearable && modelValue && !disabled), ['input--' + variant]: variant !== 'default' }"
        @input="onInput"
        @focus="$emit('focus', $event)"
        @blur="$emit('blur', $event)"
        @confirm="$emit('confirm', $event)"
      />
      <textarea
        v-else
        :value="modelValue"
        :placeholder="placeholder"
        :disabled="disabled"
        :readonly="readonly"
        :maxlength="maxlength"
        class="input input--textarea"
        :class="{ 'input--has-prefix': $slots.prefix || prefixIcon, 'input--has-suffix': $slots.suffix || suffixIcon || (clearable && modelValue && !disabled), ['input--' + variant]: variant !== 'default' }"
        :rows="rows"
        @input="onInput"
        @focus="$emit('focus', $event)"
        @blur="$emit('blur', $event)"
        @confirm="$emit('confirm', $event)"
      />
    </template>

    <!-- 前缀图标 — 嵌入 input 内部左侧 -->
    <view v-if="$slots.prefix || prefixIcon" class="base-input__prefix">
      <slot name="prefix">
        <Icon v-if="prefixIcon" :icon="prefixIcon" :size="iconSize"/>
      </slot>
    </view>

    <!-- 清除按钮（仅非 picker 模式） -->
    <view
      v-if="!isPicker && clearable && modelValue && !disabled"
      class="base-input__clear"
      @tap="onClear"
    >
      <Icon icon="X" :size="14"/>
    </view>

    <!-- 后缀图标 — 嵌入 input 内部右侧 -->
    <view v-if="$slots.suffix || suffixIcon" class="base-input__suffix">
      <slot name="suffix">
        <Icon v-if="suffixIcon" :icon="suffixIcon" :size="iconSize"/>
      </slot>
    </view>
  </view>
</template>

<script setup lang="js">
import { computed } from 'vue'
import Icon from './Icons.vue'

const props = defineProps({
  modelValue: { type: [String, Number], default: '' },
  type: { type: String, default: 'text' },
  placeholder: { type: String, default: '' },
  disabled: { type: Boolean, default: false },
  readonly: { type: Boolean, default: false },
  maxlength: { type: [Number, String], default: -1 },
  clearable: { type: Boolean, default: false },
  rows: { type: [Number, String], default: 1 },
  prefixIcon: { type: String, default: '' },
  suffixIcon: { type: String, default: '' },
  iconSize: { type: [Number, String], default: 18 },
  variant: { type: String, default: 'default' },

  // ---------- 选择器模式 ----------
  mode: { type: String, default: '' },        // date | time | datetime
  start: { type: String, default: '' },        // 起始日期/时间
  end: { type: String, default: '' },          // 结束日期/时间
  fields: { type: String, default: 'day' },    // year | month | day  (仅 date 模式)
  valueFormat: { type: String, default: '' }   // 用于格式化显示（不影响 v-model 值）
})

const emit = defineEmits(['update:modelValue', 'focus', 'blur', 'confirm', 'clear', 'change'])

// 是否是选择器模式
const isPicker = computed(() => ['date', 'time', 'datetime'].includes(props.mode))

// picker 的 fields 属性
const pickerFields = computed(() => {
  if (!isPicker.value) return undefined
  if (props.mode === 'date') return props.fields || 'day'
  return undefined
})

// 显示值（如果提供 valueFormat，则格式化显示）
const displayValue = computed(() => {
  if (!props.modelValue) return ''
  if (props.valueFormat === 'datetime' && props.mode === 'date') {
    // 例如把 2024-01-15 格式化为 2024年1月15日
    try {
      const d = new Date(props.modelValue.replace(/-/g, '/'))
      if (isNaN(d.getTime())) return props.modelValue
      return `${d.getFullYear()}年${d.getMonth() + 1}月${d.getDate()}日`
    } catch {
      return props.modelValue
    }
  }
  return props.modelValue
})

function onInput(e) {
  const value = e.detail?.value ?? e.target?.value ?? ''
  emit('update:modelValue', value)
}

function onClear() {
  emit('update:modelValue', '')
  emit('clear')
}

function onPickerChange(e) {
  const value = e.detail?.value ?? ''
  emit('update:modelValue', value)
  emit('change', value)
}
</script>

<style scoped>
.base-input-wrap {
  position: relative;
  display: flex;
  align-items: center;
  width: 100%;
  flex-direction: row;
}


/* Textarea 变体 */
.base-input--textarea {
  min-height: 76rpx;
  display: block;
}

/* picker 占满宽度 */
picker {
  width: 100%;
}

/* ---------- 选择器触发的区域 ---------- */
.input--picker {
  width: 100%;
  display: flex;
  align-items: center;
  min-height: 84rpx;
  cursor: pointer;
}

.input--placeholder {
  color: var(--theme-text-placeholder, #8B7F70);
  font-size: 30rpx;
}

/* 前缀图标 — 嵌入 input 内部左侧 */
.base-input__prefix {
  position: absolute;
  left: 20rpx;
  top: 50%;
  transform: translateY(-50%);
  display: flex;
  align-items: center;
  justify-content: center;
  pointer-events: none;
  color: var(--theme-text-primary, #19221c);
  z-index: 2;
}

/* input 有前缀图标时增加左内边距 */
.input--has-prefix {
  padding-left: 60rpx;
}

/* 清除按钮 */
.base-input__clear {
  position: absolute;
  right: 16rpx;
  top: 50%;
  transform: translateY(-50%);
  width: 36rpx;
  height: 36rpx;
  border-radius: 50%;
  background: rgba(25, 34, 28, 0.08);
  color: var(--theme-text-secondary);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  flex-shrink: 0;
  transition: background 0.1s ease;
  z-index: 2;
}

.base-input__clear:active {
  background: rgba(25, 34, 28, 0.16);
}

/* 后缀图标 — 嵌入 input 内部右侧 */
.base-input__suffix {
  position: absolute;
  right: 16rpx;
  top: 50%;
  transform: translateY(-50%);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2;
}

/* input 有后缀图标时增加右内边距 */
.input--has-suffix {
  padding-right: 60rpx;
}

/* 禁用态 */
.base-input-wrap--disabled .input {
  opacity: 0.5;
  pointer-events: none;
}

/* ===== Outline 风格 ===== */
.input--outline {
  background: transparent;
  box-shadow: inset 0 0 0 2rpx var(--theme-border-subtle);
}
.input--outline:focus {
  box-shadow: inset 0 0 0 2rpx var(--theme-action-primary);
}

/* ===== Outline Dashed 风格 ===== */
.input--outline-dashed {
  background: transparent;
  box-shadow: none;
  border: 2rpx dashed var(--theme-border-subtle);
}
.input--outline-dashed:focus {
  border-color: var(--theme-action-primary);
}
</style>
