<template>
  <!-- #ifndef MP-WEIXIN -->
  <svg :width="size" :height="size" viewBox="0 0 24 24" :fill="filled ? 'currentColor' : 'none'"
       :stroke="filled ? 'none' : 'currentColor'" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
    <template v-if="icon === 'Home'">
      <path d="M4.5 10.5c2.5-2.7 5-4.8 7.5-7 2.5 2.2 5 4.3 7.5 7"/>
      <path d="M6 9.5c-.3 3.4-.3 6.9-.2 10.4 4.1.4 8.3.4 12.4 0 .1-3.5.1-7-.2-10.4"/>
      <path d="M10.5 19.6c.1-1.7.1-3.3.4-4.9 1.4-.2 2.6-.2 4 0 .3 1.6.3 3.2.4 4.9"/>
    </template>
    <template v-else-if="icon === 'UtensilsCrossed'">
      <path d="M3.5 12c.3 4.5 3.8 8 8.5 8s8.2-3.5 8.5-8z"/>
      <path d="M6 5.5c2.5 2 5 3.5 7 4.5"/>
      <path d="M9.5 4c2.5 2.2 5 3.8 7.5 5"/>
    </template>
    <template v-else-if="icon === 'ChefHat' && !filled">
      <path d="M7.5 13.5c-2.2-.4-3.6-2-3.2-4 .3-1.8 1.8-3 3.6-2.9C8.4 4.4 10 3 12 3s3.6 1.4 4.1 3.6c1.8-.1 3.3 1.1 3.6 2.9.4 2-1 3.6-3.2 4"/>
      <path d="M7.5 13.5c0 2.4-.2 4.8-.1 7.2 3.1.3 6.1.3 9.2 0 .1-2.4-.1-4.8-.1-7.2"/>
    </template>
    <template v-else-if="icon === 'ChefHat' && filled">
      <path d="M4.3 13.6c-.5-2.3.9-4.5 3.2-4.7C8.2 5.7 10 3.5 12 3.5s3.8 2.2 4.5 5.4c2.3.2 3.7 2.4 3.2 4.7-.3 1.3-1.1 2.3-2.1 2.9v5.7c0 .4-.3.7-.7.7H7c-.4 0-.7-.3-.7-.7v-5.7c-1-.6-1.8-1.6-2-2.9z"/>
    </template>
    <template v-else-if="icon === 'Sprout'">
      <path d="M6.5 20.5c3.7-.2 7.3-.2 11 0"/>
      <path d="M12 20.5c0-3 .2-5.5 1.2-7.8"/>
      <path d="M12.8 12.5c-1.6-1.2-2.4-3-2.6-5.4 2.5.3 4.3 1.4 5.4 3.4"/>
      <path d="M13 9.5c.3-2.4 1.7-4.3 4.4-5.3.3 2.7-.7 4.7-3 5.9"/>
    </template>
    <template v-else-if="icon === 'UserRound'">
      <path d="M5.5 20.5c.4-3.6 3.1-6 6.5-6s6.1 2.4 6.5 6"/>
      <path d="M12 4a4.2 4.2 0 1 0 .1 8.4A4.2 4.2 0 0 0 12 4z"/>
    </template>
    <template v-else-if="icon === 'Plus'">
      <path d="M12 5.5c.2 4.3.2 8.7 0 13"/>
      <path d="M5.5 12c4.3-.2 8.7-.2 13 0"/>
    </template>
    <template v-else-if="icon === 'PlusCircle'">
      <circle cx="12" cy="12" r="9"/>
      <path d="M12 8v8"/>
      <path d="M8 12h8"/>
    </template>
    <template v-else-if="icon === 'Camera'">
      <path
          d="M8.5 6.5c.4-1 1-1.7 2-2h3c1 .3 1.6 1 2 2h3.3c1.3.2 2.2 1.2 2.2 2.6v7.4c-.2 1.3-1.1 2.2-2.4 2.4H6.4c-1.3-.2-2.2-1.1-2.4-2.4V9.1c0-1.4.9-2.4 2.2-2.6z"/>
      <path d="M12 9.5a3.2 3.2 0 1 0 .1 6.4 3.2 3.2 0 0 0-.1-6.4z"/>
    </template>
    <template v-else-if="icon === 'KeyRound'">
      <path
          d="M9.5 20.5c-3.6-.3-6.4-3.4-6-7 .3-3.4 3.2-6 6.6-6 3.7 0 6.6 3 6.4 6.6-.1 1.4-.6 2.6-1.4 3.6l1.9 1.9-1.6 1.6-1.6-1.6-1.4 1.4"/>
      <path d="M10.5 10.5a1.5 1.5 0 1 0 .1 3 1.5 1.5 0 0 0-.1-3z"/>
    </template>
    <template v-else-if="icon === 'LogOut'">
      <path d="M8.5 21H5.8c-1.5-.2-2.5-1.2-2.6-2.7V6c.1-1.6 1.1-2.6 2.7-2.7h2.6"/>
      <path d="M15 8l4.5 4-4.4 4.1"/>
      <path d="M19.5 12H10"/>
    </template>
    <template v-else-if="icon === 'Pencil'">
      <path d="M18.5 2.5 21.5 5.5 18 9 15 6z"/>
      <path d="M15 6 3.8 17.2c-.4 1.5-.9 3-1.6 4.6 1.6-.7 3.1-1.2 4.6-1.6L18 9"/>
    </template>
    <template v-else-if="icon === 'Server'">
      <path
          d="M4.5 3h15c1 .1 1.6.7 1.7 1.7v3.6c-.1 1-.7 1.6-1.7 1.7h-15c-1-.1-1.6-.7-1.7-1.7V4.7c.1-1 .7-1.6 1.7-1.7z"/>
      <path
          d="M4.5 14h15c1 .1 1.6.7 1.7 1.7v3.6c-.1 1-.7 1.6-1.7 1.7h-15c-1-.1-1.6-.7-1.7-1.7v-3.6c.1-1 .7-1.6 1.7-1.7z"/>
      <path d="M7 6.8h.01"/>
      <path d="M7 17.8h.01"/>
    </template>
    <template v-else-if="icon === 'Settings'">
      <path d="M12 8.8a3.2 3.2 0 1 0 .1 6.4 3.2 3.2 0 0 0-.1-6.4z"/>
      <path
          d="M12 2.5c.9 0 1.6.7 1.7 1.6l.2 1.6 1.5.9 1.5-.7c.8-.4 1.7 0 2.1.8l.4.7c.4.8.1 1.7-.6 2.2l-1.3.9v1.7l1.3.9c.7.5 1 1.4.6 2.2l-.4.7c-.4.8-1.3 1.2-2.1.8l-1.5-.7-1.5.9-.2 1.6c-.1.9-.8 1.6-1.7 1.6s-1.6-.7-1.7-1.6l-.2-1.6-1.5-.9-1.5.7c-.8.4-1.7 0-2.1-.8l-.4-.7c-.4-.8-.1-1.7.6-2.2l1.3-.9v-1.7L5 9.4c-.7-.5-1-1.4-.6-2.2l.4-.7c.4-.8 1.3-1.2 2.1-.8l1.5.7 1.5-.9.2-1.6c.1-.9.8-1.6 1.7-1.6z"/>
    </template>
    <template v-else-if="icon === 'BookOpen'">
      <path d="M12 6.5C11 4.8 9.2 4 7 4H2.5v14H7c2.2 0 4 .8 5 2.5 1-1.7 2.8-2.5 5-2.5h4.5V4H17c-2.2 0-4 .8-5 2.5z"/>
      <path d="M12 6.5V20.5"/>
    </template>
    <template v-else-if="icon === 'ChevronRight'">
      <path d="M9.5 5.5c2.3 2.1 4.4 4.2 6 6.5-1.6 2.3-3.7 4.4-6 6.5"/>
    </template>
    <template v-else-if="icon === 'ChevronLeft'">
      <path d="M14.5 5.5c-2.3 2.1-4.4 4.2-6 6.5 1.6 2.3 3.7 4.4 6 6.5"/>
    </template>
    <template v-else-if="icon === 'Search'">
      <path d="M10.5 3.5a7 7 0 1 0 .1 14 7 7 0 0 0-.1-14z"/>
      <path d="M15.5 15.5 21 21"/>
    </template>
    <template v-else-if="icon === 'Check'">
      <path d="M4.5 12.5c2.2 1.6 3.8 3.2 5 5 2.8-4.4 6.3-8.1 10-11"/>
    </template>
    <template v-else-if="icon === 'X'">
      <path d="M6 6c4 3.8 8 7.8 12 12"/>
      <path d="M18 6C14 9.8 10 13.8 6 18"/>
    </template>
    <template v-else-if="icon === 'ListFilter'">
      <path d="M3.5 6c5.6-.3 11.4-.3 17 0"/>
      <path d="M7 12c3.3-.2 6.7-.2 10 0"/>
      <path d="M10 18c1.4-.1 2.6-.1 4 0"/>
    </template>
    <template v-else-if="icon === 'ClipboardList'">
      <path
          d="M9.5 3.5c.2-.6.7-1 1.4-1h2.2c.7 0 1.2.4 1.4 1H17c1 .1 1.6.7 1.7 1.7v14.6c-.1 1-.7 1.6-1.7 1.7H7c-1-.1-1.6-.7-1.7-1.7V5.2c.1-1 .7-1.6 1.7-1.7z"/>
      <path d="M9 11.5h6"/>
      <path d="M9 16h6"/>
    </template>
    <template v-else-if="icon === 'ArrowUp'">
      <path d="M12 20c-.2-4.8-.2-9.7 0-14.5"/>
      <path d="M5.5 12C7.7 9.5 9.9 7.2 12 5c2.1 2.2 4.3 4.5 6.5 7"/>
    </template>
    <template v-else-if="icon === 'More'">
      <path d="M12 5a1.3 1.3 0 1 0 .1 2.6A1.3 1.3 0 0 0 12 5z"/>
      <path d="M12 10.7a1.3 1.3 0 1 0 .1 2.6 1.3 1.3 0 0 0-.1-2.6z"/>
      <path d="M12 16.4a1.3 1.3 0 1 0 .1 2.6 1.3 1.3 0 0 0-.1-2.6z"/>
    </template>
    <template v-else-if="icon === 'GitMerge'">
      <circle cx="5" cy="6" r="2"/>
      <circle cx="5" cy="18" r="2"/>
      <circle cx="19" cy="12" r="2"/>
      <path d="M5 8v8c0 2.2 1.8 4 4 4"/>
      <path d="M5 8v0c0-2.2 1.8-4 4-4h6c2.2 0 4 1.8 4 4v0"/>
    </template>
    <template v-else-if="icon === 'Trash2'">
      <path d="M4 7h16"/>
      <path d="M9 7V4h6v3"/>
      <path d="M6 7l1 13h10l1-13"/>
      <path d="M10 11v5"/>
      <path d="M14 11v5"/>
    </template>
    <template v-else-if="icon === 'Clock'">
      <circle cx="12" cy="12" r="9"/>
      <path d="M12 7v5l3 2"/>
    </template>
    <template v-else-if="icon === 'Calendar'">
      <rect x="3" y="4" width="18" height="17" rx="2"/>
      <path d="M3 9h18"/>
      <path d="M8 2v4"/>
      <path d="M16 2v4"/>
      <path d="M8.5 13h.01"/>
      <path d="M12 13h.01"/>
      <path d="M15.5 13h.01"/>
      <path d="M8.5 17h.01"/>
      <path d="M12 17h.01"/>
    </template>
  </svg>
  <!-- #endif -->
  <!-- #ifdef MP-WEIXIN -->
  <view class="icon-svg-mask" :style="maskStyle"/>
  <!-- #endif -->
</template>
<script setup lang="js">
import {computed} from 'vue'

const props = defineProps({
  icon: {type: String, required: true},
  size: {type: [Number, String], default: 21},
  filled: {type: Boolean, default: false}
})

/* #ifdef MP-WEIXIN */
const ICON_PATHS = {
  Home: '<path d="M4.5 10.5c2.5-2.7 5-4.8 7.5-7 2.5 2.2 5 4.3 7.5 7"/><path d="M6 9.5c-.3 3.4-.3 6.9-.2 10.4 4.1.4 8.3.4 12.4 0 .1-3.5.1-7-.2-10.4"/><path d="M10.5 19.6c.1-1.7.1-3.3.4-4.9 1.4-.2 2.6-.2 4 0 .3 1.6.3 3.2.4 4.9"/>',
  UtensilsCrossed: '<path d="M3.5 12c.3 4.5 3.8 8 8.5 8s8.2-3.5 8.5-8z"/><path d="M6 5.5c2.5 2 5 3.5 7 4.5"/><path d="M9.5 4c2.5 2.2 5 3.8 7.5 5"/>',
  ChefHat: '<path d="M7.5 13.5c-2.2-.4-3.6-2-3.2-4 .3-1.8 1.8-3 3.6-2.9C8.4 4.4 10 3 12 3s3.6 1.4 4.1 3.6c1.8-.1 3.3 1.1 3.6 2.9.4 2-1 3.6-3.2 4"/><path d="M7.5 13.5c0 2.4-.2 4.8-.1 7.2 3.1.3 6.1.3 9.2 0 .1-2.4-.1-4.8-.1-7.2"/>',
  ChefHatFilled: '<path d="M4.3 13.6c-.5-2.3.9-4.5 3.2-4.7C8.2 5.7 10 3.5 12 3.5s3.8 2.2 4.5 5.4c2.3.2 3.7 2.4 3.2 4.7-.3 1.3-1.1 2.3-2.1 2.9v5.7c0 .4-.3.7-.7.7H7c-.4 0-.7-.3-.7-.7v-5.7c-1-.6-1.8-1.6-2-2.9z"/>',
  Sprout: '<path d="M6.5 20.5c3.7-.2 7.3-.2 11 0"/><path d="M12 20.5c0-3 .2-5.5 1.2-7.8"/><path d="M12.8 12.5c-1.6-1.2-2.4-3-2.6-5.4 2.5.3 4.3 1.4 5.4 3.4"/><path d="M13 9.5c.3-2.4 1.7-4.3 4.4-5.3.3 2.7-.7 4.7-3 5.9"/>',
  UserRound: '<path d="M5.5 20.5c.4-3.6 3.1-6 6.5-6s6.1 2.4 6.5 6"/><path d="M12 4a4.2 4.2 0 1 0 .1 8.4A4.2 4.2 0 0 0 12 4z"/>',
  Plus: '<path d="M12 5.5c.2 4.3.2 8.7 0 13"/><path d="M5.5 12c4.3-.2 8.7-.2 13 0"/>',
  PlusCircle: '<circle cx="12" cy="12" r="9"/><path d="M12 8v8"/><path d="M8 12h8"/>',
  Camera: '<path d="M8.5 6.5c.4-1 1-1.7 2-2h3c1 .3 1.6 1 2 2h3.3c1.3.2 2.2 1.2 2.2 2.6v7.4c-.2 1.3-1.1 2.2-2.4 2.4H6.4c-1.3-.2-2.2-1.1-2.4-2.4V9.1c0-1.4.9-2.4 2.2-2.6z"/><path d="M12 9.5a3.2 3.2 0 1 0 .1 6.4 3.2 3.2 0 0 0-.1-6.4z"/>',
  KeyRound: '<path d="M9.5 20.5c-3.6-.3-6.4-3.4-6-7 .3-3.4 3.2-6 6.6-6 3.7 0 6.6 3 6.4 6.6-.1 1.4-.6 2.6-1.4 3.6l1.9 1.9-1.6 1.6-1.6-1.6-1.4 1.4"/><path d="M10.5 10.5a1.5 1.5 0 1 0 .1 3 1.5 1.5 0 0 0-.1-3z"/>',
  LogOut: '<path d="M8.5 21H5.8c-1.5-.2-2.5-1.2-2.6-2.7V6c.1-1.6 1.1-2.6 2.7-2.7h2.6"/><path d="M15 8l4.5 4-4.4 4.1"/><path d="M19.5 12H10"/>',
  Pencil: '<path d="M18.5 2.5 21.5 5.5 18 9 15 6z"/><path d="M15 6 3.8 17.2c-.4 1.5-.9 3-1.6 4.6 1.6-.7 3.1-1.2 4.6-1.6L18 9"/>',
  Server: '<path d="M4.5 3h15c1 .1 1.6.7 1.7 1.7v3.6c-.1 1-.7 1.6-1.7 1.7h-15c-1-.1-1.6-.7-1.7-1.7V4.7c.1-1 .7-1.6 1.7-1.7z"/><path d="M4.5 14h15c1 .1 1.6.7 1.7 1.7v3.6c-.1 1-.7 1.6-1.7 1.7h-15c-1-.1-1.6-.7-1.7-1.7v-3.6c.1-1 .7-1.6 1.7-1.7z"/><path d="M7 6.8h.01"/><path d="M7 17.8h.01"/>',
  Settings: '<path d="M12 8.8a3.2 3.2 0 1 0 .1 6.4 3.2 3.2 0 0 0-.1-6.4z"/><path d="M12 2.5c.9 0 1.6.7 1.7 1.6l.2 1.6 1.5.9 1.5-.7c.8-.4 1.7 0 2.1.8l.4.7c.4.8.1 1.7-.6 2.2l-1.3.9v1.7l1.3.9c.7.5 1 1.4.6 2.2l-.4.7c-.4.8-1.3 1.2-2.1.8l-1.5-.7-1.5.9-.2 1.6c-.1.9-.8 1.6-1.7 1.6s-1.6-.7-1.7-1.6l-.2-1.6-1.5-.9-1.5.7c-.8.4-1.7 0-2.1-.8l-.4-.7c-.4-.8-.1-1.7.6-2.2l1.3-.9v-1.7L5 9.4c-.7-.5-1-1.4-.6-2.2l.4-.7c.4-.8 1.3-1.2 2.1-.8l1.5.7 1.5-.9.2-1.6c.1-.9.8-1.6 1.7-1.6z"/>',
  BookOpen: '<path d="M12 6.5C11 4.8 9.2 4 7 4H2.5v14H7c2.2 0 4 .8 5 2.5 1-1.7 2.8-2.5 5-2.5h4.5V4H17c-2.2 0-4 .8-5 2.5z"/><path d="M12 6.5V20.5"/>',
  ChevronRight: '<path d="M9.5 5.5c2.3 2.1 4.4 4.2 6 6.5-1.6 2.3-3.7 4.4-6 6.5"/>',
  ChevronLeft: '<path d="M14.5 5.5c-2.3 2.1-4.4 4.2-6 6.5 1.6 2.3 3.7 4.4 6 6.5"/>',
  Search: '<path d="M10.5 3.5a7 7 0 1 0 .1 14 7 7 0 0 0-.1-14z"/><path d="M15.5 15.5 21 21"/>',
  Check: '<path d="M4.5 12.5c2.2 1.6 3.8 3.2 5 5 2.8-4.4 6.3-8.1 10-11"/>',
  X: '<path d="M6 6c4 3.8 8 7.8 12 12"/><path d="M18 6C14 9.8 10 13.8 6 18"/>',
  ListFilter: '<path d="M3.5 6c5.6-.3 11.4-.3 17 0"/><path d="M7 12c3.3-.2 6.7-.2 10 0"/><path d="M10 18c1.4-.1 2.6-.1 4 0"/>',
  ClipboardList: '<path d="M9.5 3.5c.2-.6.7-1 1.4-1h2.2c.7 0 1.2.4 1.4 1H17c1 .1 1.6.7 1.7 1.7v14.6c-.1 1-.7 1.6-1.7 1.7H7c-1-.1-1.6-.7-1.7-1.7V5.2c.1-1 .7-1.6 1.7-1.7z"/><path d="M9 11.5h6"/><path d="M9 16h6"/>',
  ArrowUp: '<path d="M12 20c-.2-4.8-.2-9.7 0-14.5"/><path d="M5.5 12C7.7 9.5 9.9 7.2 12 5c2.1 2.2 4.3 4.5 6.5 7"/>',
  GitMerge: '<circle cx="5" cy="6" r="2"/><circle cx="5" cy="18" r="2"/><circle cx="19" cy="12" r="2"/><path d="M5 8v8c0 2.2 1.8 4 4 4"/><path d="M5 8v0c0-2.2 1.8-4 4-4h6c2.2 0 4 1.8 4 4v0"/>',
  Trash2: '<path d="M4 7h16"/><path d="M9 7V4h6v3"/><path d="M6 7l1 13h10l1-13"/><path d="M10 11v5"/><path d="M14 11v5"/>',
  More: '<path d="M12 5a1.3 1.3 0 1 0 .1 2.6A1.3 1.3 0 0 0 12 5z"/><path d="M12 10.7a1.3 1.3 0 1 0 .1 2.6 1.3 1.3 0 0 0-.1-2.6z"/><path d="M12 16.4a1.3 1.3 0 1 0 .1 2.6 1.3 1.3 0 0 0-.1-2.6z"/>',
  Clock: '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
  Calendar: '<rect x="3" y="4" width="18" height="17" rx="2"/><path d="M3 9h18"/><path d="M8 2v4"/><path d="M16 2v4"/><path d="M8.5 13h.01"/><path d="M12 13h.01"/><path d="M15.5 13h.01"/><path d="M8.5 17h.01"/><path d="M12 17h.01"/>'
}

const maskStyle = computed(() => {
  const key = props.filled && props.icon === 'ChefHat' ? 'ChefHatFilled' : props.icon
  const inner = ICON_PATHS[key] || ''
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="${props.filled ? '#000' : 'none'}" stroke="${props.filled ? 'none' : '#000'}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">${inner}</svg>`
  const url = `url("data:image/svg+xml,${encodeURIComponent(svg)}")`
  const px = `${props.size}px`
  return {
    width: px,
    height: px,
    WebkitMaskImage: url,
    WebkitMaskRepeat: 'no-repeat',
    WebkitMaskPosition: 'center',
    WebkitMaskSize: '100% 100%',
    maskImage: url,
    maskRepeat: 'no-repeat',
    maskPosition: 'center',
    maskSize: '100% 100%'
  }
})
/* #endif */
</script>
<style scoped>
.icon-svg-mask {
  display: inline-block;
  vertical-align: middle;
  background-color: currentColor;
}
</style>
