<template>
  <text class="icon" :style="style">{{ symbol }}</text>
</template>

<script>
export default {
  name: 'Icon',
  props: {
    icon: { type: String, required: true },
    size: { type: [Number, String], default: 21 }
  },
  data() {
    return {
      iconMap: {
        Home: '🏠',
        UtensilsCrossed: '🍴',
        ChefHat: '👨‍🍳',
        Sprout: '🌱',
        UserRound: '👤',
        Plus: '➕',
        Camera: '📷',
        KeyRound: '🔑',
        LogOut: '🚪',
        Pencil: '✏️',
        Server: '🖥️',
        Settings: '⚙️'
      }
    }
  },
  computed: {
    symbol() {
      return this.iconMap[this.icon] || '?'
    },
    style() {
      return {
        fontSize: `${Number(this.size) * 1.6}rpx`,
        lineHeight: 1
      }
    }
  }
}
</script>

<style scoped>
.icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
}
</style>
