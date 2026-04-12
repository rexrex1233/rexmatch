<template>
  <view class="login-page">
    <!-- 装饰背景 -->
    <view class="bg-decor">
      <view class="decor-circle c1 float-anim-1"></view>
      <view class="decor-circle c2 float-anim-2"></view>
      <view class="decor-circle c3 float-anim-3"></view>
    </view>

    <!-- Logo区域 -->
    <view class="logo-section">
      <view class="logo-ring pulse-ring">
        <view class="logo-inner beat-heart">
          <text class="logo-icon">💕</text>
        </view>
      </view>
      <text class="app-name">RexMatch</text>
      <text class="app-slogan">遇见对的人，从这里开始</text>
    </view>

    <!-- 功能亮点 (毛玻璃质感) -->
    <view class="features glass-morphism">
      <view class="feature-item">
        <text class="feature-icon">🎯</text>
        <text class="feature-text">智能推荐</text>
      </view>
      <view class="feature-dot"></view>
      <view class="feature-item">
        <text class="feature-icon">🔒</text>
        <text class="feature-text">实名认证</text>
      </view>
      <view class="feature-dot"></view>
      <view class="feature-item">
        <text class="feature-icon">💬</text>
        <text class="feature-text">极速畅聊</text>
      </view>
    </view>

    <!-- 登录按钮区 -->
    <view class="login-section fade-up">
      <button class="login-btn interactive-scale" @tap="handleLogin" :loading="loggingIn">
        <text class="btn-icon" v-if="!loggingIn">💚</text>
        <text class="btn-label">微信一键开启</text>
      </button>
      <text class="agreement">
        登录即表示同意
        <text class="link">《用户协议》</text>
        和
        <text class="link">《隐私政策》</text>
      </text>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useUserStore } from '../../stores/user'

const userStore = useUserStore()
const loggingIn = ref(false)

async function handleLogin() {
  if (loggingIn.value) return
  loggingIn.value = true
  try {
    await userStore.wxLogin()
  } catch (e) {
    console.error('登录失败', e)
  } finally {
    loggingIn.value = false
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  align-items: center;
  background: linear-gradient(165deg, #FFF1F5 0%, #FFFFFF 40%, #F5F0FF 100%);
  padding: 0 48rpx;
  position: relative;
  overflow: hidden;
  font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", "Helvetica Neue", Arial, sans-serif;
}

/* ---- 装饰圆与沉浸式浮动动效 ---- */
.bg-decor { position: absolute; top: 0; left: 0; right: 0; bottom: 0; pointer-events: none; overflow: hidden; }
.decor-circle { position: absolute; border-radius: 50%; opacity: 0.2; filter: blur(40px); }

.c1 { width: 500rpx; height: 500rpx; background: #FF2D55; top: -120rpx; right: -160rpx; }
.c2 { width: 400rpx; height: 400rpx; background: #5E5CE6; bottom: 100rpx; left: -140rpx; }
.c3 { width: 300rpx; height: 300rpx; background: #FF9500; top: 350rpx; left: -100rpx; }

@keyframes float1 { 0%, 100% { transform: translateY(0) scale(1); } 50% { transform: translateY(-40rpx) scale(1.05); } }
@keyframes float2 { 0%, 100% { transform: translate(0,0) scale(1); } 50% { transform: translate(40rpx, 40rpx) scale(0.95); } }
@keyframes float3 { 0%, 100% { transform: translate(0,0) scale(1); } 50% { transform: translate(-30rpx, 30rpx) scale(1.1); } }

.float-anim-1 { animation: float1 8s ease-in-out infinite; }
.float-anim-2 { animation: float2 10s ease-in-out infinite; }
.float-anim-3 { animation: float3 9s ease-in-out infinite; }

/* ---- Logo 区域 ---- */
.logo-section { display: flex; flex-direction: column; align-items: center; padding-top: 240rpx; z-index: 10; }

.logo-ring { width: 220rpx; height: 220rpx; border-radius: 50%; background: linear-gradient(135deg, rgba(255,45,85,0.15), rgba(255,45,85,0.05)); display: flex; align-items: center; justify-content: center; margin-bottom: 48rpx; }
.pulse-ring { animation: pulse 3s infinite; }
@keyframes pulse { 0% { box-shadow: 0 0 0 0 rgba(255, 45, 85, 0.4); } 70% { box-shadow: 0 0 0 40rpx rgba(255, 45, 85, 0); } 100% { box-shadow: 0 0 0 0 rgba(255, 45, 85, 0); } }

.logo-inner { width: 140rpx; height: 140rpx; border-radius: 50%; background: linear-gradient(135deg, #FF2D55, #FF375F); display: flex; align-items: center; justify-content: center; box-shadow: 0 16rpx 48rpx rgba(255, 45, 85, 0.4); }
.beat-heart { animation: heartBeat 2s ease-in-out infinite; }
@keyframes heartBeat { 0%, 100% { transform: scale(1); } 15% { transform: scale(1.1); } 30% { transform: scale(1); } 45% { transform: scale(1.1); } 60% { transform: scale(1); } }

.logo-icon { font-size: 64rpx; }

.app-name { font-size: 72rpx; font-weight: 900; color: #000000; letter-spacing: 2rpx; margin-bottom: 16rpx; text-shadow: 0 8rpx 24rpx rgba(0,0,0,0.05); }
.app-slogan { font-size: 32rpx; color: #8E8E93; font-weight: 500; letter-spacing: 4rpx; }

/* ---- 功能亮点 (毛玻璃胶囊) ---- */
.glass-morphism { background: rgba(255, 255, 255, 0.6); backdrop-filter: blur(40px); -webkit-backdrop-filter: blur(40px); border: 2rpx solid rgba(255, 255, 255, 0.5); }
.features { display: flex; align-items: center; justify-content: center; gap: 32rpx; z-index: 10; padding: 24rpx 48rpx; border-radius: 60rpx; box-shadow: 0 16rpx 48rpx rgba(0,0,0,0.04); margin-top: 60rpx; }
.feature-item { display: flex; flex-direction: column; align-items: center; gap: 12rpx; }
.feature-icon { font-size: 44rpx; }
.feature-text { font-size: 24rpx; color: #3A3A3C; font-weight: 600; }
.feature-dot { width: 8rpx; height: 8rpx; border-radius: 50%; background: #D1D1D6; }

/* ---- 登录区 ---- */
.login-section { width: 100%; padding-bottom: 80rpx; padding-bottom: calc(80rpx + env(safe-area-inset-bottom)); z-index: 10; }
.fade-up { animation: fadeUpIn 0.8s cubic-bezier(0.32, 0.72, 0, 1) forwards; }
@keyframes fadeUpIn { from { opacity: 0; transform: translateY(60rpx); } to { opacity: 1; transform: translateY(0); } }

.interactive-scale { transition: transform 0.2s cubic-bezier(0.25, 0.1, 0.25, 1); }
.interactive-scale:active { transform: scale(0.95); }

.login-btn { width: 100%; height: 112rpx; background: #000000; border-radius: 56rpx; display: flex; flex-direction: row; align-items: center; justify-content: center; gap: 16rpx; box-shadow: 0 16rpx 48rpx rgba(0,0,0,0.15); border: none; }
.login-btn::after { border: none; }

.btn-icon { font-size: 40rpx; }
.btn-label { color: #FFFFFF; font-size: 34rpx; font-weight: 700; letter-spacing: 2rpx; }

.agreement { display: block; text-align: center; font-size: 24rpx; color: #8E8E93; margin-top: 40rpx; line-height: 1.8; font-weight: 500; }
.link { color: #FF2D55; font-weight: 600; }
</style>
