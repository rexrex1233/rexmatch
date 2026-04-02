<template>
  <view class="modal-overlay" v-if="visible" @tap="$emit('close')">
    <view class="modal-card" :class="{ 'card-enter': animating }" @tap.stop>
      <!-- 粒子动画背景 -->
      <view class="particles">
        <view class="particle" v-for="i in 12" :key="i" :class="'p' + i"></view>
      </view>

      <!-- 渐变顶部 -->
      <view class="header-gradient">
        <view class="hearts-float">
          <text class="hf hf1">💕</text>
          <text class="hf hf2">✨</text>
          <text class="hf hf3">💖</text>
          <text class="hf hf4">🎉</text>
          <text class="hf hf5">💗</text>
        </view>
      </view>

      <view class="modal-body">
        <!-- 大心跳动画 -->
        <view class="match-icon-ring pulse-ring">
          <text class="match-heart beat-heart">💖</text>
        </view>

        <text class="modal-title fade-up d1">配对成功!</text>
        <text class="modal-desc fade-up d2">你们互相喜欢了，快去打个招呼吧</text>

        <button class="chat-btn bounce-in d3" @tap="$emit('chat')">
          <text class="chat-btn-text">💬 开始聊天</text>
        </button>
        <view class="continue-link fade-up d4" @tap="$emit('close')">
          <text class="continue-text">继续浏览</text>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'

const props = defineProps<{ visible: boolean }>()
defineEmits(['close', 'chat'])

const animating = ref(false)

watch(() => props.visible, (v) => {
  if (v) {
    animating.value = false
    setTimeout(() => { animating.value = true }, 30)
  }
})
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 999;
  animation: overlayIn 0.3s ease-out;
}

@keyframes overlayIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.modal-card {
  width: 620rpx;
  background: #fff;
  border-radius: 36rpx;
  overflow: hidden;
  position: relative;
  transform: scale(0.7) translateY(40rpx);
  opacity: 0;
  transition: all 0.5s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.modal-card.card-enter {
  transform: scale(1) translateY(0);
  opacity: 1;
}

/* Particles */
.particles { position: absolute; top: 0; left: 0; right: 0; bottom: 0; pointer-events: none; overflow: hidden; z-index: 0; }
.particle { position: absolute; width: 12rpx; height: 12rpx; border-radius: 50%; opacity: 0; }

@keyframes particleFly {
  0% { opacity: 0; transform: translateY(0) scale(0); }
  20% { opacity: 1; }
  100% { opacity: 0; transform: translateY(-300rpx) scale(1.5); }
}

.p1 { background: #ff6b81; left: 10%; top: 70%; animation: particleFly 2s 0.2s infinite; }
.p2 { background: #ffa502; left: 25%; top: 80%; animation: particleFly 1.8s 0.4s infinite; }
.p3 { background: #ff4757; left: 40%; top: 75%; animation: particleFly 2.2s 0.1s infinite; }
.p4 { background: #a29bfe; left: 55%; top: 85%; animation: particleFly 1.9s 0.6s infinite; }
.p5 { background: #fd79a8; left: 70%; top: 72%; animation: particleFly 2.1s 0.3s infinite; }
.p6 { background: #e84393; left: 85%; top: 78%; animation: particleFly 1.7s 0.5s infinite; }
.p7 { background: #ff6b81; left: 15%; top: 60%; animation: particleFly 2.3s 0.7s infinite; width: 8rpx; height: 8rpx; }
.p8 { background: #feca57; left: 35%; top: 65%; animation: particleFly 2s 0.8s infinite; width: 8rpx; height: 8rpx; }
.p9 { background: #ff9ff3; left: 60%; top: 68%; animation: particleFly 1.8s 0.9s infinite; width: 8rpx; height: 8rpx; }
.p10 { background: #ff4757; left: 80%; top: 62%; animation: particleFly 2.2s 0.15s infinite; width: 8rpx; height: 8rpx; }
.p11 { background: #ffa502; left: 48%; top: 90%; animation: particleFly 2.4s 0.35s infinite; }
.p12 { background: #a29bfe; left: 5%; top: 88%; animation: particleFly 2s 0.55s infinite; }

/* Header gradient */
.header-gradient {
  position: relative;
  height: 120rpx;
  background: linear-gradient(135deg, #ff6b81 0%, #ff4757 40%, #e84393 100%);
  overflow: hidden;
}

.hearts-float { position: absolute; top: 0; left: 0; right: 0; bottom: 0; }

@keyframes floatUp {
  0% { opacity: 0; transform: translateY(20rpx) scale(0.5); }
  30% { opacity: 1; }
  100% { opacity: 0; transform: translateY(-80rpx) scale(1.2); }
}

.hf { position: absolute; font-size: 32rpx; animation: floatUp 2.5s infinite; }
.hf1 { top: 30rpx; left: 50rpx; animation-delay: 0s; }
.hf2 { top: 16rpx; left: 180rpx; animation-delay: 0.6s; }
.hf3 { top: 40rpx; right: 160rpx; animation-delay: 0.3s; }
.hf4 { top: 10rpx; right: 60rpx; animation-delay: 0.9s; }
.hf5 { top: 50rpx; left: 320rpx; animation-delay: 1.2s; }

.modal-body {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 0 48rpx 56rpx;
  margin-top: -56rpx;
  position: relative;
  z-index: 1;
}

/* Pulsing ring */
.match-icon-ring {
  width: 112rpx;
  height: 112rpx;
  border-radius: 50%;
  background: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 8rpx 32rpx rgba(255, 107, 129, 0.35);
  margin-bottom: 28rpx;
  position: relative;
}

@keyframes pulseRing {
  0%, 100% { box-shadow: 0 8rpx 32rpx rgba(255,107,129,0.35); }
  50% { box-shadow: 0 8rpx 48rpx rgba(255,107,129,0.55), 0 0 0 12rpx rgba(255,107,129,0.1); }
}

.pulse-ring { animation: pulseRing 1.5s ease-in-out infinite; }

@keyframes heartBeat {
  0%, 100% { transform: scale(1); }
  15% { transform: scale(1.3); }
  30% { transform: scale(1); }
  45% { transform: scale(1.2); }
  60% { transform: scale(1); }
}

.beat-heart { font-size: 52rpx; animation: heartBeat 1.2s ease-in-out infinite; display: inline-block; }

/* Staggered fade-up */
@keyframes fadeUp {
  from { opacity: 0; transform: translateY(30rpx); }
  to { opacity: 1; transform: translateY(0); }
}

.fade-up { opacity: 0; animation: fadeUp 0.5s ease-out forwards; }
.d1 { animation-delay: 0.3s; }
.d2 { animation-delay: 0.45s; }
.d4 { animation-delay: 0.75s; }

@keyframes bounceIn {
  0% { opacity: 0; transform: scale(0.3); }
  50% { transform: scale(1.05); }
  70% { transform: scale(0.95); }
  100% { opacity: 1; transform: scale(1); }
}

.bounce-in { opacity: 0; animation: bounceIn 0.6s ease-out forwards; }
.d3 { animation-delay: 0.55s; }

.modal-title {
  font-size: 44rpx;
  font-weight: 800;
  color: #1a1a1a;
  margin-bottom: 12rpx;
}

.modal-desc {
  font-size: 28rpx;
  color: #999;
  margin-bottom: 44rpx;
  text-align: center;
  line-height: 1.5;
}

.chat-btn {
  width: 100%;
  height: 96rpx;
  background: linear-gradient(135deg, #ff6b81, #ff4757);
  border-radius: 48rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  margin-bottom: 24rpx;
  box-shadow: 0 10rpx 32rpx rgba(255, 71, 87, 0.35);
}

.chat-btn::after { border: none; }

.chat-btn-text {
  color: #fff;
  font-size: 32rpx;
  font-weight: 600;
}

.continue-link { padding: 8rpx 0; }
.continue-text { font-size: 28rpx; color: #b3b3b3; }
</style>
