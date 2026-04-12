<template>
  <view class="onboarding-page">
    
    <!-- 顶部导航与进度 -->
    <view class="top-nav" :style="{ paddingTop: statusBarHeight + 'px' }">
      <view class="nav-left" @tap="prevStep">
        <view class="back-btn interactive-scale" v-show="swiperIndex > 0">
          <text class="back-icon">‹</text>
        </view>
      </view>
      <view class="nav-center">
        <view class="dash-progress">
          <view class="dash" :class="{ active: swiperIndex >= 0 }"></view>
          <view class="dash" :class="{ active: swiperIndex >= 1 }"></view>
          <view class="dash" :class="{ active: swiperIndex >= 2 }"></view>
        </view>
      </view>
      <view class="nav-right"></view>
    </view>

    <!-- 可滑动主视区 -->
    <swiper class="ob-swiper" :current="swiperIndex" :duration="500" :disable-touch="true" @change="onSwiperChange">
      
      <!-- 步骤 0：性别 -->
      <swiper-item class="ob-slide">
        <view class="slide-content">
          <text class="apple-title fade-up-1">选择你的性别</text>
          <text class="apple-subtitle fade-up-2">这将决定系统会为你推荐的人</text>

          <view class="gender-cards fade-up-3">
            <view class="g-card interactive-scale" :class="{ selected: form.gender === 1 }" @tap="selectGender(1)">
              <view class="g-bg boy-bg"></view>
              <view class="g-content">
                <text class="g-emoji">👨</text>
                <text class="g-text">我是男生</text>
              </view>
              <view class="g-check" v-if="form.gender === 1">
                <text class="g-check-icon">✓</text>
              </view>
            </view>

            <view class="g-card interactive-scale" :class="{ selected: form.gender === 2 }" @tap="selectGender(2)">
              <view class="g-bg girl-bg"></view>
              <view class="g-content">
                <text class="g-emoji">👩</text>
                <text class="g-text">我是女生</text>
              </view>
              <view class="g-check" v-if="form.gender === 2">
                <text class="g-check-icon">✓</text>
              </view>
            </view>
          </view>
        </view>
      </swiper-item>

      <!-- 步骤 1：生日 -->
      <swiper-item class="ob-slide">
        <view class="slide-content">
          <text class="apple-title fade-up-1">你的生日是？</text>
          <text class="apple-subtitle fade-up-2">这有助于匹配同频的人（年龄计算后不可改）</text>

          <view class="birthday-section fade-up-3">
            <picker mode="date" :value="form.birthday || '2000-01-01'" start="1970-01-01" end="2005-12-31" @change="onBirthdayChange">
              <view class="date-display interactive-scale" :class="{ hasval: form.birthday }">
                {{ form.birthday ? form.birthday.replace(/-/g, ' / ') : '点此选择出生日期' }}
              </view>
            </picker>
          </view>

          <view class="next-action fade-up-4" v-if="form.birthday">
            <button class="apple-btn primary interactive-scale" @tap="nextStep">继续</button>
          </view>
        </view>
      </swiper-item>

      <!-- 步骤 2：资料卡 (昵称验证) -->
      <swiper-item class="ob-slide">
        <view class="slide-content">
          <text class="apple-title fade-up-1">最后，装饰一下吧</text>
          <text class="apple-subtitle fade-up-2">上传头像可提升 85% 的匹配率（可跳过，之后再补）</text>

          <view class="profile-setup fade-up-3">
            <!-- 头像上传 -->
            <view class="avatar-upload interactive-scale" @tap="chooseAvatar">
              <image v-if="form.avatarUrl" :src="form.avatarUrl" class="avatar-img" mode="aspectFill" />
              <view v-else class="avatar-placeholder">
                <text class="avatar-ph-icon">📷</text>
                <text>点击上传</text>
              </view>
              <view class="edit-badge" v-if="form.avatarUrl"><text>✏️</text></view>
            </view>

            <!-- 昵称校验输入 -->
            <view class="nickname-box" :class="{ 'is-focused': isNicknameFocused }">
              <input
                class="nickname-input"
                v-model="rawNickname"
                @focus="isNicknameFocused = true"
                @blur="isNicknameFocused = false"
                @input="onNicknameInput"
                placeholder="你希望别人怎么称呼你？"
                maxlength="12"
                placeholder-class="ph"
              />
              <view class="status-icon">
                <view v-if="checkingName" class="spinner"></view>
                <view v-else-if="nameStatus === 'ok'" class="icon-ok bounce-in">
                  <text class="status-icon-text ok">✓</text>
                </view>
                <view v-else-if="nameStatus === 'error'" class="icon-err wobble">
                  <text class="status-icon-text err">✕</text>
                </view>
              </view>
            </view>
            <text class="name-msg" :class="nameStatus">{{ nameMessage }}</text>

            <!-- 城市选择 -->
            <picker class="city-picker-wrap" :range="cityList" @change="onCityChange">
              <view class="city-picker-row" :class="{ hasval: form.city }">
                <text class="city-icon">📍</text>
                <text class="city-label">{{ form.city || '选择你的城市（可提升匹配率）' }}</text>
                <text class="city-arrow">›</text>
              </view>
            </picker>
          </view>

          <view class="next-action flex-bottom fade-up-4">
            <button 
              class="apple-btn primary interactive-scale lg" 
              :class="{ disabled: !canSubmit }"
              :loading="saving"
              @tap="submitProfile"
            >
              开启 RexMatch
            </button>
          </view>
        </view>
      </swiper-item>

    </swiper>
  </view>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { userApi, checkNickname } from '../../api'
import { useUserStore } from '../../stores/user'

const statusBarHeight = ref(uni.getSystemInfoSync().statusBarHeight || 44)
const userStore = useUserStore()

const swiperIndex = ref(0)
const isNicknameFocused = ref(false)

const cityList = [
  '北京','上海','广州','深圳','成都','杭州','武汉','重庆','西安','南京',
  '苏州','天津','长沙','郑州','青岛','沈阳','宁波','东莞','昆明','合肥',
  '福州','厦门','哈尔滨','济南','南宁','贵阳','太原','石家庄','海口','三亚',
  '其他',
]

// 逻辑状态
const form = reactive({
  gender: 0,
  birthday: '',
  nickname: '',
  city: '',
  avatarUrl: '',
  avatarId: null as number | null,
})

// 昵称输入去重
const rawNickname = ref('')
const checkingName = ref(false)
const nameStatus = ref<'idle'|'ok'|'error'>('idle')
const nameMessage = ref('')
let debounceTimer: any = null

function onSwiperChange(e: any) {
  // 如果是由于滑动导致的更新（如果我们开启了 allow touch）
  swiperIndex.value = e.detail.current
}

function prevStep() {
  if (swiperIndex.value > 0) swiperIndex.value--
}

function nextStep() {
  if (swiperIndex.value < 2) swiperIndex.value++
}

function selectGender(g: number) {
  form.gender = g
  setTimeout(() => nextStep(), 400) // 阻尼延时跳往下一页
}

function onBirthdayChange(e: any) {
  form.birthday = e.detail.value
}

function onCityChange(e: any) {
  form.city = cityList[e.detail.value]
}

async function chooseAvatar() {
  uni.chooseImage({
    count: 1,
    async success(res) {
      const tempPath = res.tempFilePaths[0]
      form.avatarUrl = tempPath 
      try {
        const uploadRes = await userApi.uploadPhoto(tempPath, true)
        if (uploadRes.data) {
          form.avatarUrl = uploadRes.data.url
          form.avatarId = uploadRes.data.id
        }
      } catch (e) {
        uni.showToast({ title: '照片上传失败自动降级', icon: 'none' })
      }
    }
  })
}

async function checkNicknameApi(name: string): Promise<{unique: boolean, msg?: string}> {
  try {
    const res = await checkNickname(name)
    return { unique: res.data.available, msg: res.data.message }
  } catch {
    // 降级：网络错误时允许继续
    return { unique: true }
  }
}

function onNicknameInput() {
  const val = rawNickname.value.trim()
  form.nickname = val
  if (!val) {
    nameStatus.value = 'idle'
    nameMessage.value = ''
    return
  }
  
  checkingName.value = true
  nameStatus.value = 'idle'
  nameMessage.value = ''

  if (debounceTimer) clearTimeout(debounceTimer)
  debounceTimer = setTimeout(async () => {
    if (val.length < 2) {
      checkingName.value = false
      nameStatus.value = 'error'
      nameMessage.value = '昵称太短啦（至少2字）'
      return
    }
    const res = await checkNicknameApi(val)
    checkingName.value = false
    if (res.unique) {
      nameStatus.value = 'ok'
      nameMessage.value = '昵称可用，很棒的名字！'
    } else {
      nameStatus.value = 'error'
      nameMessage.value = res.msg || '昵称已被使用'
    }
  }, 500)
}

const canSubmit = computed(() => {
  return form.gender !== 0 && form.birthday && form.nickname && nameStatus.value === 'ok'
})

const saving = ref(false)
async function submitProfile() {
  if (!canSubmit.value || saving.value) return
  saving.value = true
  try {
    await userApi.updateProfile({
      nickname: form.nickname,
      gender: form.gender,
      birthday: form.birthday,
      ...(form.city ? { city: form.city } : {}),
    })
    await userStore.fetchProfile()
    
    uni.showToast({ title: '设置成功', icon: 'success' })
    setTimeout(() => {
      uni.switchTab({ url: '/pages/home/index' })
    }, 1000)
  } catch (e) {
    console.error(e)
    uni.showToast({ title: '保存失败', icon: 'none' })
    saving.value = false
  }
}
</script>

<style scoped>
.onboarding-page {
  height: 100vh;
  background: #F2F2F7;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", "Helvetica Neue", Arial, sans-serif;
}

/* 顶部导航与分段指示器 */
.top-nav {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16rpx 32rpx;
  background: transparent;
  z-index: 10;
}
.nav-left, .nav-right { width: 80rpx; display: flex; align-items: center; }
.back-btn { width: 72rpx; height: 72rpx; border-radius: 50%; background: #ffffff; display: flex; align-items: center; justify-content: center; box-shadow: 0 4rpx 16rpx rgba(0,0,0,0.06); }

.nav-center { flex: 1; display: flex; align-items: center; justify-content: center; }
.dash-progress { display: flex; gap: 12rpx; }
.dash { width: 64rpx; height: 8rpx; border-radius: 8rpx; background: #D1D1D6; transition: all 0.4s cubic-bezier(0.32, 0.72, 0, 1); }
.dash.active { background: #000000; width: 80rpx; }

/* 主滑动区 */
.ob-swiper {
  flex: 1;
  width: 100%;
}
.ob-slide {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
}
.slide-content {
  flex: 1;
  padding: 60rpx 48rpx;
  display: flex;
  flex-direction: column;
}

/* 苹果风排版 */
.apple-title { font-size: 64rpx; font-weight: 800; color: #000; letter-spacing: -1rpx; margin-bottom: 16rpx; display: block; }
.apple-subtitle { font-size: 30rpx; color: #8E8E93; line-height: 1.5; font-weight: 500; display: block; margin-bottom: 80rpx; }

/* 交互反馈类 */
.interactive-scale { transition: transform 0.2s cubic-bezier(0.25, 0.1, 0.25, 1); }
.interactive-scale:active { transform: scale(0.95); }

/* FadeUp 动画 */
.fade-up-1 { opacity: 0; animation: fadeUpIn 0.8s 0.1s cubic-bezier(0.32, 0.72, 0, 1) forwards; }
.fade-up-2 { opacity: 0; animation: fadeUpIn 0.8s 0.2s cubic-bezier(0.32, 0.72, 0, 1) forwards; }
.fade-up-3 { opacity: 0; animation: fadeUpIn 0.8s 0.3s cubic-bezier(0.32, 0.72, 0, 1) forwards; }
.fade-up-4 { opacity: 0; animation: fadeUpIn 0.8s 0.4s cubic-bezier(0.32, 0.72, 0, 1) forwards; }
@keyframes fadeUpIn { from { opacity: 0; transform: translateY(40rpx); } to { opacity: 1; transform: translateY(0); } }

/* 性别卡片 (Apple Squircle) */
.gender-cards { display: flex; flex-direction: column; gap: 40rpx; }
.g-card { 
  position: relative; 
  height: 240rpx; 
  border-radius: 48rpx; 
  background: #FFFFFF; 
  box-shadow: 0 16rpx 48rpx rgba(0,0,0,0.06); 
  overflow: hidden; 
  transition: all 0.3s cubic-bezier(0.32, 0.72, 0, 1);
}
.g-card.selected { transform: scale(0.98); box-shadow: 0 4rpx 12rpx rgba(0,0,0,0.04); }
.g-card.selected::after { content: ''; position: absolute; top:0;left:0;right:0;bottom:0; border: 6rpx solid #000; border-radius: 48rpx; pointer-events: none; z-index: 10; }

.g-bg { position: absolute; right: -80rpx; top: -80rpx; width: 300rpx; height: 300rpx; border-radius: 50%; opacity: 0.1; }
.boy-bg { background: #007AFF; }
.girl-bg { background: #FF2D55; }

.g-content { position: absolute; left: 48rpx; top: 0; bottom: 0; display: flex; align-items: center; gap: 32rpx; }
.g-emoji { font-size: 80rpx; }
.g-text { font-size: 44rpx; font-weight: 700; color: #1C1C1E; }
.g-check { position: absolute; right: 48rpx; top: 50%; transform: translateY(-50%); width: 56rpx; height: 56rpx; border-radius: 50%; background: #000; display: flex; align-items: center; justify-content: center; }

/* 步骤 2：生日 */
.birthday-section { margin-top: 40rpx; }
.date-display { 
  height: 140rpx; background: #FFFFFF; border-radius: 36rpx; 
  display: flex; align-items: center; justify-content: center; 
  font-size: 40rpx; font-weight: 700; color: #C7C7CC; 
  box-shadow: 0 8rpx 32rpx rgba(0,0,0,0.04);
}
.date-display.hasval { color: #000000; font-size: 48rpx; font-variant-numeric: tabular-nums; tracking: 4rpx; background: #F2F2F7; border: 4rpx solid #000; }

.next-action { margin-top: 60rpx; display: flex; justify-content: center; }
.flex-bottom { margin-top: auto; padding-bottom: 40rpx; }

/* 步骤 3：综合资料 */
.profile-setup { display: flex; flex-direction: column; align-items: center; }
.avatar-upload { 
  position: relative; width: 240rpx; height: 240rpx; border-radius: 50%; 
  background: #E5E5EA; margin-bottom: 80rpx; 
  display: flex; align-items: center; justify-content: center; 
  box-shadow: 0 16rpx 48rpx rgba(0,0,0,0.1); border: 8rpx solid #FFFFFF;
}
.avatar-img { width: 100%; height: 100%; border-radius: 50%; }
.avatar-placeholder { display: flex; flex-direction: column; align-items: center; gap: 12rpx; }
.avatar-placeholder text { font-size: 26rpx; color: #8E8E93; font-weight: 600; }
.edit-badge { position: absolute; right: 0; bottom: 0; width: 64rpx; height: 64rpx; background: #FFFFFF; border-radius: 50%; display: flex; align-items: center; justify-content: center; box-shadow: 0 4rpx 12rpx rgba(0,0,0,0.1); border: 2rpx solid #F2F2F7; font-size: 28rpx; }

/* 智能排重昵称框 */
.nickname-box {
  width: 100%; display: flex; align-items: center; 
  background: #FFFFFF; height: 128rpx; border-radius: 36rpx; 
  padding: 0 40rpx; box-shadow: 0 8rpx 32rpx rgba(0,0,0,0.04);
  transition: all 0.3s; position: relative;
}
.nickname-box.is-focused { box-shadow: 0 16rpx 48rpx rgba(0,0,0,0.08); transform: translateY(-4rpx); }
.nickname-input { flex: 1; height: 100%; font-size: 36rpx; font-weight: 600; color: #000; }
.ph { color: #C7C7CC; font-weight: 500; }

.status-icon { width: 48rpx; height: 48rpx; display: flex; align-items: center; justify-content: center; margin-left: 20rpx; }
.spinner { width: 36rpx; height: 36rpx; border: 6rpx solid #F2F2F7; border-top-color: #000; border-radius: 50%; animation: spin 0.8s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }

.bounce-in { animation: bounceIn 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275) forwards; }
@keyframes bounceIn { 0% { transform: scale(0); } 100% { transform: scale(1); } }
.wobble { animation: wobble 0.5s ease-in-out; }
@keyframes wobble { 0%, 100% { transform: translateX(0); } 25% { transform: translateX(-10rpx); } 75% { transform: translateX(10rpx); } }

.name-msg { font-size: 24rpx; font-weight: 500; margin-top: 24rpx; align-self: flex-start; height: 32rpx; transition: color 0.3s; }

.city-picker-wrap { width: 100%; margin-top: 24rpx; }
.city-picker-row {
  width: 100%; height: 112rpx; background: #FFFFFF; border-radius: 36rpx;
  display: flex; align-items: center; padding: 0 40rpx; gap: 16rpx;
  box-shadow: 0 8rpx 32rpx rgba(0,0,0,0.04);
}
.city-picker-row.hasval { border: 4rpx solid #000; background: #F2F2F7; }
.city-icon { font-size: 36rpx; }
.city-label { flex: 1; font-size: 32rpx; font-weight: 600; color: #C7C7CC; }
.city-picker-row.hasval .city-label { color: #000; }
.city-arrow { font-size: 40rpx; color: #C7C7CC; font-weight: 300; }
.name-msg.ok { color: #34C759; }
.name-msg.error { color: #FF3B30; }
.name-msg.idle { color: transparent; }

/* 苹果风通用按钮 */
.apple-btn { height: 112rpx; border-radius: 56rpx; font-size: 34rpx; font-weight: 700; display: flex; align-items: center; justify-content: center; border: none; }
.apple-btn::after { border: none; }
.primary { background: #000000; color: #FFFFFF; min-width: 400rpx; box-shadow: 0 16rpx 48rpx rgba(0,0,0,0.15); }
.primary.lg { width: 100%; }
.primary.disabled { background: #E5E5EA; color: #8E8E93; box-shadow: none; pointer-events: none; }
.back-icon { font-size: 52rpx; font-weight: 300; color: #000; line-height: 1; }
.g-check-icon { font-size: 32rpx; color: #fff; font-weight: 700; line-height: 1; }
.avatar-ph-icon { font-size: 64rpx; line-height: 1; }
.status-icon-text { font-size: 40rpx; font-weight: 700; line-height: 1; }
.status-icon-text.ok { color: #34C759; }
.status-icon-text.err { color: #FF3B30; }
</style>