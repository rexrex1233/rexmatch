<template>
  <view class="onboarding-page">
    <view class="top-nav" :style="{ paddingTop: statusBarHeight + 'px' }">
      <view class="nav-left" @tap="prevStep">
        <view class="back-btn interactive-scale" v-show="swiperIndex > 0">
          <text class="back-icon">‹</text>
        </view>
      </view>
      <view class="nav-center">
        <view class="dash-progress">
          <view v-for="i in 6" :key="i" class="dash" :class="{ active: swiperIndex >= (i - 1) }"></view>
        </view>
      </view>
      <view class="nav-right">
        <!-- 提供选填跳过按钮 -->
        <text class="skip-btn" v-if="[3, 4].includes(swiperIndex)" @tap="nextStep">跳过</text>
      </view>
    </view>

    <swiper class="ob-swiper" :current="swiperIndex" :duration="400" :disable-touch="true">
      
      <!-- 步骤 0：性别 (必填) -->
      <swiper-item class="ob-slide">
        <view class="slide-content">
          <text class="apple-title fade-up-1">选择你的性别</text>
          <text class="apple-subtitle fade-up-2">这将决定系统会为你推荐的人</text>
          <view class="gender-cards fade-up-3">
            <view class="g-card interactive-scale" :class="{ selected: form.gender === 1 }" @tap="selectGender(1)">
              <view class="g-bg boy-bg"></view>
              <view class="g-content"><text class="g-emoji">👨</text><text class="g-text">我是男生</text></view>
              <view class="g-check" v-if="form.gender === 1"><text class="g-check-icon">✓</text></view>
            </view>
            <view class="g-card interactive-scale" :class="{ selected: form.gender === 2 }" @tap="selectGender(2)">
              <view class="g-bg girl-bg"></view>
              <view class="g-content"><text class="g-emoji">👩</text><text class="g-text">我是女生</text></view>
              <view class="g-check" v-if="form.gender === 2"><text class="g-check-icon">✓</text></view>
            </view>
          </view>
        </view>
      </swiper-item>

      <!-- 步骤 1：生日与身高 (必填) -->
      <swiper-item class="ob-slide">
        <view class="slide-content">
          <text class="apple-title fade-up-1">基础档案</text>
          <text class="apple-subtitle fade-up-2">这有助于匹配同频且外型相仿的人</text>
          
          <view class="fade-up-3" style="margin-top: 40rpx;">
            <text class="info-label">生日</text>
            <picker mode="date" :value="form.birthday || '2000-01-01'" start="1970-01-01" end="2005-12-31" @change="onBirthdayChange">
              <view class="data-row interactive-scale" :class="{ hasval: form.birthday }">
                <text class="data-text">{{ form.birthday ? form.birthday.replace(/-/g, ' / ') : '点此选择出生日期' }}</text>
                <text class="data-extra" v-if="extZodiac">{{ extZodiac }}</text>
              </view>
            </picker>
          </view>

          <view class="fade-up-3" style="margin-top: 40rpx;">
            <text class="info-label">身高 (cm)</text>
            <picker mode="selector" :range="heightList" @change="onHeightChange">
              <view class="data-row interactive-scale" :class="{ hasval: form.height }">
                <text class="data-text">{{ form.height ? form.height + ' cm' : '滑动选择身高' }}</text>
              </view>
            </picker>
          </view>

          <view class="next-action fade-up-4 flex-bottom">
            <button class="apple-btn primary interactive-scale lg" :class="{ disabled: !form.birthday || !form.height }" @tap="nextStep">继续</button>
          </view>
        </view>
      </swiper-item>

      <!-- 步骤 2：名片 (头像与昵称必填) -->
      <swiper-item class="ob-slide">
        <view class="slide-content">
          <text class="apple-title fade-up-1">社交名片</text>
          <text class="apple-subtitle fade-up-2">上传一张清晰的正脸照片能提升85%匹配率</text>
          
          <view class="profile-setup fade-up-3">
            <view class="avatar-upload interactive-scale" @tap="chooseAvatar">
              <image v-if="form.avatarUrl" :src="form.avatarUrl" class="avatar-img" mode="aspectFill" />
              <view v-else class="avatar-placeholder">
                <text class="avatar-ph-icon">📷</text>
                <text>点击上传头像</text>
              </view>
              <view class="edit-badge" v-if="form.avatarUrl"><text>✏️</text></view>
            </view>

            <view class="nickname-box" :class="{ 'is-focused': isNicknameFocused }">
              <input class="nickname-input" v-model="rawNickname" @focus="isNicknameFocused = true" @blur="isNicknameFocused = false" @input="onNicknameInput" placeholder="你希望别人怎么称呼你？" maxlength="12" placeholder-class="ph" />
              <view class="status-icon">
                <view v-if="checkingName" class="spinner"></view>
                <view v-else-if="nameStatus === 'ok'" class="icon-ok bounce-in"><text class="status-icon-text ok">✓</text></view>
                <view v-else-if="nameStatus === 'error'" class="icon-err wobble"><text class="status-icon-text err">✕</text></view>
              </view>
            </view>
            <text class="name-msg" :class="nameStatus">{{ nameMessage }}</text>
          </view>

          <view class="next-action flex-bottom fade-up-4">
            <button class="apple-btn primary interactive-scale lg" :class="{ disabled: !form.avatarUrl || nameStatus !== 'ok' }" @tap="nextStep">继续</button>
          </view>
        </view>
      </swiper-item>

      <!-- 步骤 3：背景状况 (城市必填，其余选填) -->
      <swiper-item class="ob-slide">
        <view class="slide-content">
          <text class="apple-title fade-up-1">你的背景资料</text>
          <text class="apple-subtitle fade-up-2">丰富资料能吸引更多同好（可点右上角跳过）</text>
          
          <scroll-view scroll-y class="fade-up-3 form-scroll">
            <text class="info-label">现居地</text>
            <picker :range="cityList" @change="(e) => form.city = cityList[e.detail.value]">
              <view class="data-row interactive-scale" :class="{ hasval: form.city }">
                <text class="data-text">{{ form.city || '请选择现居城市' }}</text>
              </view>
            </picker>

            <text class="info-label" style="margin-top:24rpx;">家乡</text>
            <picker :range="cityList" @change="(e) => form.hometown = cityList[e.detail.value]">
              <view class="data-row interactive-scale" :class="{ hasval: form.hometown }">
                <text class="data-text">{{ form.hometown || '请选择家乡' }}</text>
              </view>
            </picker>

            <text class="info-label" style="margin-top:24rpx;">学历状况</text>
            <picker :range="['专科', '本科', '硕士', '博士']" @change="(e) => form.education = ['专科', '本科', '硕士', '博士'][e.detail.value]">
              <view class="data-row interactive-scale" :class="{ hasval: form.education }">
                <text class="data-text">{{ form.education || '最高学历' }}</text>
              </view>
            </picker>

            <text class="info-label" style="margin-top:24rpx;">所在行业</text>
            <picker :range="industryList" @change="(e) => form.industry = industryList[e.detail.value]">
              <view class="data-row interactive-scale" :class="{ hasval: form.industry }">
                <text class="data-text">{{ form.industry || '从事什么行业？' }}</text>
              </view>
            </picker>
            <view style="height: 120rpx;"></view>
          </scroll-view>

          <view class="next-action fade-up-4 flex-bottom-fixed">
            <button class="apple-btn primary interactive-scale lg" :class="{ disabled: !form.city }" @tap="nextStep">继续</button>
          </view>
        </view>
      </swiper-item>

      <!-- 步骤 4：内心与感情观 (全选填) -->
      <swiper-item class="ob-slide">
        <view class="slide-content">
          <text class="apple-title fade-up-1">内心独白与倾向</text>
          <text class="apple-subtitle fade-up-2">这些将展示在你的主页中</text>
          
          <scroll-view scroll-y class="fade-up-3 form-scroll">
            <text class="info-label">MBTI 性格</text>
            <picker :range="mbtiList" @change="(e) => form.mbti = mbtiList[e.detail.value]">
              <view class="data-row interactive-scale" :class="{ hasval: form.mbti }">
                <text class="data-text">{{ form.mbti || '你的十六型人格是？' }}</text>
              </view>
            </picker>

            <text class="info-label" style="margin-top:24rpx;">交友目的</text>
            <picker :range="purposeList" @change="(e) => form.dating_purpose = purposeList[e.detail.value]">
              <view class="data-row interactive-scale" :class="{ hasval: form.dating_purpose }">
                <text class="data-text">{{ form.dating_purpose || '寻找什么关系？' }}</text>
              </view>
            </picker>

            <text class="info-label" style="margin-top:24rpx;">恋爱节奏倾向</text>
            <picker :range="rhythmList" @change="(e) => form.dating_rhythm = rhythmList[e.detail.value]">
              <view class="data-row interactive-scale" :class="{ hasval: form.dating_rhythm }">
                <text class="data-text">{{ form.dating_rhythm || '比如：顺其自然 / 慢热...' }}</text>
              </view>
            </picker>

            <text class="info-label" style="margin-top:24rpx;">关于我 (简短介绍)</text>
            <view class="bio-box interactive-scale">
              <textarea v-model="form.bio" placeholder="聊点生活趣事、兴趣爱好或者性格特质..." class="bio-textarea" :maxlength="150" />
            </view>
            <view style="height: 120rpx;"></view>
          </scroll-view>

          <view class="next-action fade-up-4 flex-bottom-fixed">
            <button class="apple-btn primary interactive-scale lg" @tap="nextStep">继续</button>
          </view>
        </view>
      </swiper-item>

      <!-- 步骤 5：生活相册与最终提交 -->
      <swiper-item class="ob-slide">
        <view class="slide-content">
          <text class="apple-title fade-up-1">最后生活秀</text>
          <text class="apple-subtitle fade-up-2">加点相册的人总显得更有魅力（可选）</text>

          <view class="fade-up-3 photo-grid">
            <!-- 已经上传的生活相册 -->
            <view class="photo-item interactive-scale" v-for="(img, idx) in extPhotos" :key="idx">
              <image :src="img.url" mode="aspectFill" class="p-img" />
              <view class="p-del" @tap="removeExtPhoto(idx)"><text>✕</text></view>
            </view>
            
            <!-- 上传按钮 (最多支持 4 张展示) -->
            <view class="photo-item photo-add interactive-scale" @tap="chooseLifePhotos" v-if="extPhotos.length < 4">
              <text class="p-add-icon">+</text>
            </view>
          </view>
          
          <view class="next-action flex-bottom-fixed fade-up-4">
            <button class="apple-btn heartbeat interactive-scale lg" :loading="saving" @tap="submitProfile">完成注册，开启匹配宇宙 🚀</button>
          </view>
        </view>
      </swiper-item>

    </swiper>
  </view>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { userApi, checkNickname } from '../../api'
import { useUserStore } from '../../stores/user'

const statusBarHeight = ref(uni.getSystemInfoSync().statusBarHeight || 44)
const userStore = useUserStore()

const swiperIndex = ref(0)
const isNicknameFocused = ref(false)

// 各种列表数据
const cityList = ['北京','上海','广州','深圳','成都','杭州','武汉','重庆','西安','南京','苏州','天津','其他']
const heightList = Array.from({length: 81}, (_, k) => k + 140) // 140-220
const industryList = ['互联网/IT','金融/投资','医疗/健康','教育/研究','广告/传媒','艺术/设计','公务体系','商业/服务','其他']
const mbtiList = ['INTJ','INTP','ENTJ','ENTP','INFJ','INFP','ENFJ','ENFP','ISTJ','ISFJ','ESTJ','ESFJ','ISTP','ISFP','ESTP','ESFP']
const purposeList = ['想找对象结婚','寻找长期稳定恋爱','结识新朋友','暂无明确目标','顺其自然']
const rhythmList = ['一见钟情','慢热了解','先做朋友','顺其自然']

// 逻辑状态
const form = reactive({
  gender: 0,
  birthday: '',
  height: null as number | null,
  nickname: '',
  avatarUrl: '',
  avatarId: null as number | null,
  city: '',
  hometown: '',
  education: '',
  industry: '',
  mbti: '',
  dating_purpose: '',
  dating_rhythm: '',
  bio: '',
})

// 推算星座
const extZodiac = computed(() => {
  if (!form.birthday) return ''
  const parts = form.birthday.split('-')
  if (parts.length!==3) return ''
  const m = parseInt(parts[1], 10), d = parseInt(parts[2], 10)
  if ((m == 3 && d >= 21) || (m == 4 && d <= 19)) return "白羊座"
  if ((m == 4 && d >= 20) || (m == 5 && d <= 20)) return "金牛座"
  if ((m == 5 && d >= 21) || (m == 6 && d <= 21)) return "双子座"
  if ((m == 6 && d >= 22) || (m == 7 && d <= 22)) return "巨蟹座"
  if ((m == 7 && d >= 23) || (m == 8 && d <= 22)) return "狮子座"
  if ((m == 8 && d >= 23) || (m == 9 && d <= 22)) return "处女座"
  if ((m == 9 && d >= 23) || (m == 10 && d <= 23)) return "天秤座"
  if ((m == 10 && d >= 24) || (m == 11 && d <= 22)) return "天蝎座"
  if ((m == 11 && d >= 23) || (m == 12 && d <= 21)) return "射手座"
  if ((m == 12 && d >= 22) || (m == 1 && d <= 19)) return "摩羯座"
  if ((m == 1 && d >= 20) || (m == 2 && d <= 18)) return "水瓶座"
  if ((m == 2 && d >= 19) || (m == 3 && d <= 20)) return "双鱼座"
  return ""
})

// === 生活相册 ===
const extPhotos = ref<any[]>([])

// === 昵称校验逻辑 ===
const rawNickname = ref('')
const checkingName = ref(false)
const nameStatus = ref<'idle'|'ok'|'error'>('idle')
const nameMessage = ref('')
let debounceTimer: any = null

function prevStep() { if (swiperIndex.value > 0) swiperIndex.value-- }
function nextStep() { if (swiperIndex.value < 5) swiperIndex.value++ }

function selectGender(g: number) {
  form.gender = g
  setTimeout(() => nextStep(), 300)
}

function onBirthdayChange(e: any) { form.birthday = e.detail.value }
function onHeightChange(e: any) { form.height = heightList[e.detail.value] }

async function chooseAvatar() {
  uni.chooseImage({
    count: 1,
    success: async (res) => {
      const tempPath = res.tempFilePaths[0]
      form.avatarUrl = tempPath 
      try {
        const uploadRes = await userApi.uploadPhoto(tempPath, true)
        if (uploadRes.data) {
          form.avatarUrl = uploadRes.data.url
          form.avatarId = uploadRes.data.id
        }
      } catch (e) {
        uni.showToast({ title: '照片上传失败', icon: 'none' })
      }
    }
  })
}

async function chooseLifePhotos() {
  uni.chooseImage({
    count: 4 - extPhotos.value.length,
    success: async (res) => {
      for (const tempPath of res.tempFilePaths) {
        // 先插入占位
        const idx = extPhotos.value.push({ url: tempPath, id: null }) - 1
        try {
          const uploadRes = await userApi.uploadPhoto(tempPath, false)
          if (uploadRes.data) {
            extPhotos.value[idx].url = uploadRes.data.url
            extPhotos.value[idx].id = uploadRes.data.id
          }
        } catch(e) {
          extPhotos.value.splice(idx, 1) // 失败则移除
        }
      }
    }
  })
}

function removeExtPhoto(idx: number) {
  const p = extPhotos.value[idx]
  extPhotos.value.splice(idx, 1)
  if (p.id) {
    userApi.deletePhoto(p.id).catch(() => {})
  }
}

async function checkNicknameApi(name: string): Promise<{unique: boolean, msg?: string}> {
  try {
    const res = await checkNickname(name)
    return { unique: res.data.available, msg: res.data.message }
  } catch { return { unique: true } }
}

function onNicknameInput() {
  const val = rawNickname.value.trim()
  form.nickname = val
  if (!val) {
    nameStatus.value = 'idle'; nameMessage.value = ''
    return
  }
  checkingName.value = true
  nameStatus.value = 'idle'; nameMessage.value = ''

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

const saving = ref(false)
async function submitProfile() {
  if (saving.value) return
  saving.value = true
  try {
    // 过滤掉空字符串避免影响后端判断
    const payload: any = {}
    for (const [k, v] of Object.entries(form)) {
      if (v !== '' && v !== null && k !== 'avatarUrl' && k !== 'avatarId') {
        payload[k] = v
      }
    }
    await userApi.updateProfile(payload)
    await userStore.fetchProfile()
    
    uni.showToast({ title: '资料建立成功', icon: 'success' })
    setTimeout(() => {
      uni.switchTab({ url: '/pages/home/index' })
    }, 1000)
  } catch (e) {
    uni.showToast({ title: '保存失败', icon: 'none' })
    saving.value = false
  }
}
</script>

<style scoped>
.onboarding-page {
  height: 100vh; background: #F2F2F7;
  display: flex; flex-direction: column; overflow: hidden;
  font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", "Helvetica Neue", Arial, sans-serif;
}

/* 导航 */
.top-nav { display: flex; align-items: center; justify-content: space-between; padding: 16rpx 32rpx; z-index: 10; }
.nav-left, .nav-right { width: 100rpx; display: flex; align-items: center; }
.nav-right { justify-content: flex-end; }
.skip-btn { font-size: 30rpx; color: #8E8E93; font-weight: 500; padding: 10rpx 0; }
.back-btn { width: 72rpx; height: 72rpx; border-radius: 50%; background: #ffffff; display: flex; align-items: center; justify-content: center; box-shadow: 0 4rpx 16rpx rgba(0,0,0,0.06); }
.nav-center { flex: 1; display: flex; align-items: center; justify-content: center; }
.dash-progress { display: flex; gap: 8rpx; }
.dash { width: 44rpx; height: 8rpx; border-radius: 8rpx; background: #D1D1D6; transition: all 0.4s; }
.dash.active { background: #000000; width: 64rpx; }

/* Swiper */
.ob-swiper { flex: 1; width: 100%; }
.ob-slide { width: 100%; height: 100%; display: flex; flex-direction: column; }
.slide-content { flex: 1; padding: 48rpx; display: flex; flex-direction: column; position: relative; }

/* 文字样式 */
.apple-title { font-size: 60rpx; font-weight: 800; color: #000; letter-spacing: -1rpx; margin-bottom: 12rpx; display: block; }
.apple-subtitle { font-size: 28rpx; color: #8E8E93; line-height: 1.5; font-weight: 500; display: block; margin-bottom: 50rpx; }
.info-label { font-size: 28rpx; font-weight: 600; color: #333; margin-bottom: 16rpx; display: block; padding-left: 8rpx; }

/* 表单行 (Glassmorphism) */
.form-scroll { height: calc(100vh - 400rpx); padding-bottom: 120rpx; }
.data-row {
  height: 112rpx; background: #FFF; border-radius: 36rpx;
  display: flex; align-items: center; padding: 0 40rpx;
  box-shadow: 0 8rpx 24rpx rgba(0,0,0,0.04);
  justify-content: space-between;
}
.data-row.hasval { border: 4rpx solid #000; background: #F2F2F7; }
.data-text { font-size: 34rpx; font-weight: 600; color: #C7C7CC; }
.hasval .data-text { color: #000; }
.data-extra { font-size: 28rpx; color: #8E8E93; font-weight: 600; background: #E5E5EA; padding: 6rpx 16rpx; border-radius: 20rpx; }

/* BIO 多行 */
.bio-box { background: #FFF; border-radius: 36rpx; padding: 32rpx; box-shadow: 0 8rpx 24rpx rgba(0,0,0,0.04); }
.bio-textarea { width: 100%; height: 180rpx; font-size: 30rpx; line-height: 1.5; color: #000; }

/* 照片墙 */
.photo-grid { display: flex; flex-wrap: wrap; gap: 24rpx; margin-top: 40rpx; }
.photo-item { position: relative; width: 280rpx; height: 380rpx; border-radius: 36rpx; background: #FFF; box-shadow: 0 16rpx 48rpx rgba(0,0,0,0.08); overflow: hidden; }
.p-img { width: 100%; height: 100%; }
.photo-add { border: 4rpx dashed #C7C7CC; background: transparent; display: flex; align-items: center; justify-content: center; box-shadow: none; pointer-events: auto; }
.p-add-icon { font-size: 80rpx; color: #C7C7CC; font-weight: 300; }
.p-del { position: absolute; top: 16rpx; right: 16rpx; width: 56rpx; height: 56rpx; background: rgba(0,0,0,0.5); border-radius: 50%; color: #FFF; display: flex; align-items: center; justify-content: center; font-size: 24rpx; backdrop-filter: blur(8rpx); }

/* 原本的性别和头像 */
.gender-cards { display: flex; flex-direction: column; gap: 40rpx; }
.g-card { position: relative; height: 240rpx; border-radius: 48rpx; background: #FFFFFF; box-shadow: 0 16rpx 48rpx rgba(0,0,0,0.06); overflow: hidden; transition: all 0.3s; }
.g-card.selected { transform: scale(0.98); box-shadow: 0 4rpx 12rpx rgba(0,0,0,0.04); }
.g-card.selected::after { content: ''; position: absolute; top:0;left:0;right:0;bottom:0; border: 6rpx solid #000; border-radius: 48rpx; pointer-events: none; z-index: 10; }
.g-bg { position: absolute; right: -80rpx; top: -80rpx; width: 300rpx; height: 300rpx; border-radius: 50%; opacity: 0.1; }
.boy-bg { background: #007AFF; } .girl-bg { background: #FF2D55; }
.g-content { position: absolute; left: 48rpx; top: 0; bottom: 0; display: flex; align-items: center; gap: 32rpx; }
.g-emoji { font-size: 80rpx; } .g-text { font-size: 44rpx; font-weight: 700; color: #1C1C1E; }
.g-check { position: absolute; right: 48rpx; top: 50%; transform: translateY(-50%); width: 56rpx; height: 56rpx; border-radius: 50%; background: #000; display: flex; align-items: center; justify-content: center; }

.profile-setup { display: flex; flex-direction: column; align-items: center; }
.avatar-upload { position: relative; width: 240rpx; height: 240rpx; border-radius: 50%; background: #E5E5EA; margin-bottom: 80rpx; display: flex; align-items: center; justify-content: center; box-shadow: 0 16rpx 48rpx rgba(0,0,0,0.1); border: 8rpx solid #FFFFFF; }
.avatar-img { width: 100%; height: 100%; border-radius: 50%; }
.avatar-placeholder { display: flex; flex-direction: column; align-items: center; gap: 12rpx; }
.avatar-placeholder text { font-size: 26rpx; color: #8E8E93; font-weight: 600; }
.edit-badge { position: absolute; right: 0; bottom: 0; width: 64rpx; height: 64rpx; background: #FFFFFF; border-radius: 50%; display: flex; align-items: center; justify-content: center; box-shadow: 0 4rpx 12rpx rgba(0,0,0,0.1); border: 2rpx solid #F2F2F7; font-size: 28rpx; }

.nickname-box { width: 100%; display: flex; align-items: center; background: #FFFFFF; height: 128rpx; border-radius: 36rpx; padding: 0 40rpx; box-shadow: 0 8rpx 32rpx rgba(0,0,0,0.04); transition: all 0.3s; position: relative; }
.nickname-box.is-focused { box-shadow: 0 16rpx 48rpx rgba(0,0,0,0.08); transform: translateY(-4rpx); }
.nickname-input { flex: 1; height: 100%; font-size: 36rpx; font-weight: 600; color: #000; }
.status-icon { width: 48rpx; height: 48rpx; display: flex; align-items: center; justify-content: center; margin-left: 20rpx; }
.spinner { width: 36rpx; height: 36rpx; border: 6rpx solid #F2F2F7; border-top-color: #000; border-radius: 50%; animation: spin 0.8s linear infinite; }
.name-msg { font-size: 24rpx; font-weight: 500; margin-top: 24rpx; align-self: flex-start; height: 32rpx; transition: color 0.3s; }

/* 交互反馈类 */
.interactive-scale { transition: transform 0.2s; }
.interactive-scale:active { transform: scale(0.95); }

/* 后继动画 */
.fade-up-1 { animation: fadeUpIn 0.6s 0.1s both; } .fade-up-2 { animation: fadeUpIn 0.6s 0.2s both; } .fade-up-3 { animation: fadeUpIn 0.6s 0.3s both; } .fade-up-4 { animation: fadeUpIn 0.6s 0.4s both; }
@keyframes fadeUpIn { from { opacity: 0; transform: translateY(40rpx); } to { opacity: 1; transform: translateY(0); } }

/* 动作栏 */
.next-action { margin-top: 60rpx; display: flex; justify-content: center; }
.flex-bottom { margin-top: auto; padding-bottom: 20rpx; }
.flex-bottom-fixed { position: absolute; bottom: 48rpx; left: 48rpx; right: 48rpx; }

/* 按钮 */
.apple-btn { height: 112rpx; border-radius: 56rpx; font-size: 34rpx; font-weight: 700; display: flex; align-items: center; justify-content: center; border: none; }
.primary { background: #000000; color: #FFFFFF; min-width: 400rpx; box-shadow: 0 16rpx 48rpx rgba(0,0,0,0.15); }
.primary.lg { width: 100%; }
.primary.disabled { background: #E5E5EA; color: #8E8E93; box-shadow: none; pointer-events: none; }
.heartbeat { background: linear-gradient(135deg, #000000, #333333); color: #fff; width: 100%; box-shadow: 0 16rpx 48rpx rgba(0,0,0,0.2); }

@keyframes spin { to { transform: rotate(360deg); } }
.bounce-in { animation: bounceIn 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275) both; }
@keyframes bounceIn { 0% { transform: scale(0); } 100% { transform: scale(1); } }
.wobble { animation: wobble 0.5s ease-in-out; }
@keyframes wobble { 0%, 100% { transform: translateX(0); } 25% { transform: translateX(-10rpx); } 75% { transform: translateX(10rpx); } }
.name-msg.ok { color: #34C759; } .name-msg.error { color: #FF3B30; } .name-msg.idle { color: transparent; }
.back-icon { font-size: 52rpx; font-weight: 300; color: #000; line-height: 1; }
.g-check-icon { font-size: 32rpx; color: #fff; font-weight: 700; line-height: 1; }
.avatar-ph-icon { font-size: 64rpx; line-height: 1; }
.status-icon-text { font-size: 40rpx; font-weight: 700; line-height: 1; }
.status-icon-text.ok { color: #34C759; } .status-icon-text.err { color: #FF3B30; }
</style>