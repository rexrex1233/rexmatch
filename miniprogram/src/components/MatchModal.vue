<template>
  <view class="modal-overlay" v-if="visible" @tap="$emit('close')">
    <view class="blur-bg"></view> <!-- 全屏毛玻璃 -->

    <view class="modal-card" :class="{ 'card-enter': animating }" @tap.stop>
      <!-- 动态发光光源 -->
      <view class="ambient-light light-1"></view>
      <view class="ambient-light light-2"></view>

      <view class="modal-body">
        
        <!-- 飞入的抽象双人碰撞波纹 -->
        <view class="match-hero">
          <view class="avatar-mock a-left"></view>
          <view class="avatar-mock a-right"></view>
          <view class="ripple-ring r1"></view>
          <view class="ripple-ring r2"></view>
          <view class="heart-center beat-heart">💖</view>
        </view>

        <text class="modal-title fade-up d1">It's a Match!</text>
        <text class="modal-desc fade-up d2">不可思议的缘分，你们相互喜欢了</text>

        <view class="action-group fade-up d3">
          <button class="apple-btn primary interactive-scale" @tap="$emit('chat')">
            <text>马上打招呼</text>
          </button>
          <view class="apple-btn secondary interactive-scale" @tap="$emit('close')">
            <text>继续浏览</text>
          </view>
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
    uni.vibrateLong({}) // 匹配震动反馈
  }
})
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 999;
  animation: overlayIn 0.5s ease-out;
  font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", Helvetica, sans-serif;
}

.blur-bg {
  position: absolute; top:0; left:0; right:0; bottom:0;
  background: rgba(0, 0, 0, 0.45);
  backdrop-filter: blur(48px);
  -webkit-backdrop-filter: blur(48px);
}

@keyframes overlayIn { from { opacity: 0; backdrop-filter: blur(0); } to { opacity: 1; backdrop-filter: blur(48px); } }

.modal-card {
  width: 100%;
  height: 100vh;
  display: flex; align-items: center; justify-content: center;
  position: relative;
  z-index: 10;
}

/* 动态景深环境光 */
.ambient-light { position: absolute; border-radius: 50%; filter: blur(80px); opacity: 0; }
.light-1 { width: 500rpx; height: 500rpx; background: #FF2D55; top: 10%; left: -100rpx; }
.light-2 { width: 400rpx; height: 400rpx; background: #5E5CE6; bottom: 10%; right: -50rpx; }

.card-enter .ambient-light { opacity: 0.5; animation: breathe 4s infinite alternate; }
@keyframes breathe { 0% { transform: scale(1); } 100% { transform: scale(1.2); } }

.modal-body {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 0 60rpx;
  width: 100%;
}

/* 匹配飞行特效 */
.match-hero { position: relative; width: 400rpx; height: 200rpx; margin-bottom: 80rpx; display: flex; justify-content: center; align-items: center; }
.avatar-mock { position: absolute; top: 50%; width: 140rpx; height: 140rpx; border-radius: 50%; opacity: 0; border: 6rpx solid #FFF; background: linear-gradient(135deg, #F2F2F7, #E5E5EA); box-shadow: 0 16rpx 48rpx rgba(0,0,0,0.3); z-index: 5; }
.a-left { left: 0; transform: translate(-200rpx, -50%); }
.a-right { right: 0; transform: translate(200rpx, -50%); }

.card-enter .a-left { animation: flyLeft 0.8s 0.2s cubic-bezier(0.34, 1.56, 0.64, 1) forwards; }
.card-enter .a-right { animation: flyRight 0.8s 0.2s cubic-bezier(0.34, 1.56, 0.64, 1) forwards; }

@keyframes flyLeft { to { transform: translate(40rpx, -50%) rotate(-10deg); opacity: 1; } }
@keyframes flyRight { to { transform: translate(-40rpx, -50%) rotate(10deg); opacity: 1; } }

.heart-center { position: absolute; z-index: 10; font-size: 80rpx; text-shadow: 0 8rpx 32rpx rgba(255,45,85,0.6); opacity: 0; transform: scale(0); }
.card-enter .heart-center { animation: popHeart 0.6s 0.6s cubic-bezier(0.34, 1.56, 0.64, 1) forwards; }
@keyframes popHeart { to { opacity: 1; transform: scale(1); } }

.beat-heart { animation: beat 1.2s 1.2s infinite; }
@keyframes beat { 0%, 100% { transform: scale(1); } 15% { transform: scale(1.2); } 30% { transform: scale(1); } }

/* 波纹 */
.ripple-ring { position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); border-radius: 50%; border: 4rpx solid #FFF; opacity: 0; }
.card-enter .r1 { animation: ripple 1.5s 0.8s infinite; }
.card-enter .r2 { animation: ripple 1.5s 1.2s infinite; }
@keyframes ripple { 0% { width: 140rpx; height: 140rpx; opacity: 1; } 100% { width: 400rpx; height: 400rpx; opacity: 0; border-width: 0; } }

/* 排版 */
.modal-title { font-size: 80rpx; font-weight: 900; color: #FFF; text-shadow: 0 8rpx 32rpx rgba(0,0,0,0.4); text-align: center; margin-bottom: 24rpx; letter-spacing: 2rpx; background: linear-gradient(to right, #FFF, #FFE0E6); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.modal-desc { font-size: 30rpx; color: rgba(255,255,255,0.8); margin-bottom: 100rpx; text-align: center; font-weight: 500; }

.fade-up { opacity: 0; transform: translateY(40rpx); }
.card-enter .fade-up { animation: fadeUpIn 0.8s cubic-bezier(0.34, 1.56, 0.64, 1) forwards; }
.d1 { animation-delay: 0.6s; }
.d2 { animation-delay: 0.7s; }
.d3 { animation-delay: 0.8s; }

@keyframes fadeUpIn { to { opacity: 1; transform: translateY(0); } }

/* 按钮组 */
.action-group { width: 100%; display: flex; flex-direction: column; gap: 32rpx; }
.interactive-scale { transition: transform 0.2s cubic-bezier(0.25, 0.1, 0.25, 1); }
.interactive-scale:active { transform: scale(0.95); }

.apple-btn { width: 100%; height: 112rpx; border-radius: 56rpx; display: flex; align-items: center; justify-content: center; font-size: 34rpx; font-weight: 800; border: none; }
.apple-btn::after { border: none; }
.primary { background: linear-gradient(135deg, #FF2D55, #FF375F); color: #FFF; box-shadow: 0 16rpx 48rpx rgba(255,45,85,0.4); }
.secondary { background: rgba(255,255,255,0.15); color: #FFF; border: 2rpx solid rgba(255,255,255,0.3); backdrop-filter: blur(20px); }
</style>
