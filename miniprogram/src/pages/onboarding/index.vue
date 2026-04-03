<template>
  <view class="onboarding-page">
    <view class="progress-bar">
      <view class="progress-inner" :style="{ width: (currentStep / totalSteps) * 100 + '%' }"></view>
    </view>

    <!-- 步骤 1：性别 -->
    <view class="step-container" :class="{ active: currentStep === 1 }">
      <text class="step-title">请问你的性别是？</text>
      <text class="step-subtitle">选择后无法修改，这将决定你匹配到的人</text>

      <view class="gender-cards">
        <view class="g-card boy" :class="{ selected: form.gender === 1 }" @tap="selectGender(1)">
          <view class="g-icon">👨</view>
          <text>男生</text>
        </view>
        <view class="g-card girl" :class="{ selected: form.gender === 2 }" @tap="selectGender(2)">
          <view class="g-icon">👩</view>
          <text>女生</text>
        </view>
      </view>
    </view>

    <!-- 步骤 2：生日 -->
    <view class="step-container" :class="{ active: currentStep === 2 }">
      <text class="step-title">你的生日是哪天？</text>
      <text class="step-subtitle">用来计算年龄和星座，不对外公开具体日期</text>

      <picker class="date-picker-wrap" mode="date" :value="form.birthday" start="1970-01-01" end="2008-12-31" @change="onBirthdayChange">
        <view class="date-display" :class="{ hasval: form.birthday }">
          {{ form.birthday ? form.birthday.replace(/-/g, ' / ') : 'YYYY / MM / DD' }}
        </view>
      </picker>
    </view>

    <!-- 步骤 3：昵称与头像 -->
    <view class="step-container" :class="{ active: currentStep === 3 }">
      <text class="step-title">设置你的个人形象</text>
      <text class="step-subtitle">第一印象很重要哦</text>

      <view class="avatar-upload" @tap="chooseAvatar">
        <image v-if="form.avatarUrl" :src="form.avatarUrl" class="avatar-img" mode="aspectFill" />
        <view v-else class="avatar-placeholder">
          <text class="camera-icon">📷</text>
          <text class="camera-text">上传真实照片</text>
        </view>
      </view>

      <view class="nickname-box">
        <input 
          class="nickname-input" 
          v-model="form.nickname" 
          placeholder="输入好听的昵称" 
          maxlength="15"
          placeholder-class="ph"
        />
      </view>
    </view>

    <!-- 底部操作区 -->
    <view class="bottom-action">
      <button class="btn back-btn" v-if="currentStep > 1" @tap="prevStep">上一步</button>
      <view style="flex: 1" v-if="currentStep > 1"></view>

      <button 
        class="btn next-btn" 
        :class="{ disabled: !canGoNext }"
        :loading="saving"
        @tap="nextStep"
      >
        {{ currentStep === totalSteps ? '开启 RexMatch' : '下一步' }}
      </button>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { userApi } from '../../api'
import { useUserStore } from '../../stores/user'

const userStore = useUserStore()
const currentStep = ref(1)
const totalSteps = 3
const saving = ref(false)

const form = reactive({
  gender: 0,
  birthday: '',
  nickname: '',
  avatarUrl: '',
  avatarId: null as number | null,
})

const canGoNext = computed(() => {
  if (currentStep.value === 1) return form.gender !== 0
  if (currentStep.value === 2) return !!form.birthday
  if (currentStep.value === 3) return !!form.nickname.trim() && !!form.avatarUrl
  return false
})

function selectGender(g: number) {
  form.gender = g
  setTimeout(() => nextStep(), 300) // 自动进下一步，体验更好
}

function onBirthdayChange(e: any) {
  form.birthday = e.detail.value
}

async function chooseAvatar() {
  uni.chooseImage({
    count: 1,
    async success(res) {
      const tempPath = res.tempFilePaths[0]
      form.avatarUrl = tempPath // 乐观更新
      try {
        const uploadRes = await userApi.uploadPhoto(tempPath, true)
        if (uploadRes.data) {
          form.avatarUrl = uploadRes.data.url
          form.avatarId = uploadRes.data.id
        }
      } catch (e) {
        uni.showToast({ title: '照片上传失败', icon: 'none' })
        form.avatarUrl = ''
      }
    }
  })
}

function prevStep() {
  if (currentStep.value > 1) {
    currentStep.value--
  }
}

async function nextStep() {
  if (!canGoNext.value) return

  if (currentStep.value < totalSteps) {
    currentStep.value++
    return
  }

  // 最后一步：提交资料
  saving.value = true
  try {
    await userApi.updateProfile({
      nickname: form.nickname.trim(),
      gender: form.gender,
      birthday: form.birthday,
    })
    await userStore.fetchProfile()
    
    uni.showToast({ title: '设置成功', icon: 'success' })
    setTimeout(() => {
      uni.switchTab({ url: '/pages/home/index' })
    }, 1000)
  } catch (e) {
    console.error(e)
    uni.showToast({ title: '保存失败', icon: 'none' })
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
.onboarding-page {
  min-height: 100vh;
  background: #ffffff;
  display: flex;
  flex-direction: column;
  position: relative;
  overflow: hidden;
}

/* 进度条 */
.progress-bar {
  height: 8rpx;
  background: #f0f2f5;
  width: 100%;
}
.progress-inner {
  height: 100%;
  background: #1a1a1a;
  transition: width 0.4s ease;
}

/* 步骤容器 */
.step-container {
  flex: 1;
  padding: 80rpx 60rpx;
  display: none;
  animation: slideIn 0.4s ease forwards;
}
.step-container.active {
  display: flex;
  flex-direction: column;
}

@keyframes slideIn {
  from { opacity: 0; transform: translateX(40rpx); }
  to { opacity: 1; transform: translateX(0); }
}

.step-title {
  font-size: 52rpx;
  font-weight: 800;
  color: #1a1a1a;
  margin-bottom: 20rpx;
  letter-spacing: 2rpx;
}
.step-subtitle {
  font-size: 28rpx;
  color: #999;
  margin-bottom: 80rpx;
}

/* 步骤 1：性别卡片 */
.gender-cards {
  display: flex;
  flex-direction: column;
  gap: 32rpx;
}
.g-card {
  height: 180rpx;
  border-radius: 32rpx;
  border: 4rpx solid #f0f2f5;
  display: flex;
  align-items: center;
  padding: 0 48rpx;
  font-size: 36rpx;
  font-weight: 600;
  color: #1a1a1a;
  transition: all 0.25s;
}
.g-icon {
  font-size: 64rpx;
  margin-right: 32rpx;
}
.g-card.selected {
  border-color: #1a1a1a;
  background: #fafafa;
  box-shadow: 0 12rpx 32rpx rgba(0,0,0,0.06);
}

/* 步骤 2：生日 */
.date-picker-wrap {
  width: 100%;
}
.date-display {
  height: 120rpx;
  border-bottom: 4rpx solid #f0f2f5;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 44rpx;
  font-weight: 700;
  color: #ccc;
  letter-spacing: 4rpx;
  transition: all 0.3s;
}
.date-display.hasval {
  color: #1a1a1a;
  border-bottom-color: #1a1a1a;
}

/* 步骤 3：形象 */
.avatar-upload {
  width: 240rpx;
  height: 240rpx;
  border-radius: 50%;
  background: #f4f6f8;
  margin: 0 auto 60rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  box-shadow: 0 16rpx 40rpx rgba(0,0,0,0.06);
}
.avatar-img {
  width: 100%;
  height: 100%;
}
.avatar-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12rpx;
}
.camera-icon { font-size: 56rpx; opacity: 0.6; }
.camera-text { font-size: 24rpx; color: #999; font-weight: 500; }

.nickname-box {
  border-bottom: 4rpx solid #1a1a1a;
  padding: 20rpx 0;
  margin: 0 40rpx;
}
.nickname-input {
  font-size: 40rpx;
  font-weight: 600;
  text-align: center;
  height: 60rpx;
}
.ph { color: #ccc; font-weight: 400; }

/* 底部操作 */
.bottom-action {
  padding: 40rpx 48rpx;
  padding-bottom: calc(40rpx + env(safe-area-inset-bottom));
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.btn {
  height: 100rpx;
  border-radius: 50rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 32rpx;
  font-weight: 600;
  margin: 0;
}
.btn::after { border: none; }
.back-btn {
  background: transparent;
  color: #999;
  width: 180rpx;
}
.next-btn {
  background: #1a1a1a;
  color: #fff;
  width: 360rpx;
  box-shadow: 0 12rpx 32rpx rgba(0,0,0,0.15);
  transition: all 0.3s;
}
.next-btn.disabled {
  background: #f0f2f5;
  color: #b3b3b3;
  box-shadow: none;
}
</style>