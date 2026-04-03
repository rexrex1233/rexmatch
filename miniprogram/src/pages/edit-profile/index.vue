<template>
  <view class="edit-page">
    <!-- 头像区域 -->
    <view class="avatar-section">
      <view class="avatar-wrapper" @tap="chooseAvatar">
        <image class="edit-avatar" :src="form.avatarUrl || defaultAvatar" mode="aspectFill" />
        <view class="avatar-badge">
          <text class="badge-icon">📷</text>
        </view>
      </view>
      <text class="avatar-tip">点击更换头像，展现最真实的你</text>
    </view>

    <!-- 照片墙 (最多9张) -->
    <view class="card photo-card">
      <view class="card-title-row">
        <text class="card-title">我的相册</text>
        <text class="card-subtitle">{{ photos.length }}/9</text>
      </view>
      <view class="photo-grid">
        <view class="photo-slot" v-for="(photo, idx) in photos" :key="photo.id || idx">
          <image class="slot-photo" :src="photo.url" mode="aspectFill" @tap="previewPhoto(idx)" />
          <view class="slot-delete" @tap.stop="deletePhoto(photo, idx)">
            <text class="delete-icon">✕</text>
          </view>
          <view class="slot-badge" v-if="photo.is_avatar">
            <text class="badge-text">封面</text>
          </view>
        </view>
        <view class="photo-slot add-slot" v-if="photos.length < 9" @tap="addPhoto">
          <text class="add-icon">+</text>
        </view>
      </view>
      <text class="photo-tip">丰富的相册能让你获得3倍以上的喜欢喔！</text>
    </view>

    <!-- 基本资料 -->
    <view class="card">
      <text class="card-title">基本资料</text>

      <view class="form-row">
        <text class="form-label">昵称</text>
        <view class="form-right">
          <input class="form-input right" v-model="form.nickname" placeholder="输入好听的昵称" maxlength="15" placeholder-class="ph-color" />
        </view>
      </view>

      <view class="form-row">
        <text class="form-label">性别</text>
        <view class="gender-group">
          <view class="gender-btn" :class="{ active: form.gender === 1 }" @tap="form.gender = 1">
            <text class="gender-icon">♂</text>男生
          </view>
          <view class="gender-btn" :class="{ active: form.gender === 2 }" @tap="form.gender = 2">
            <text class="gender-icon">♀</text>女生
          </view>
        </view>
      </view>

      <view class="form-row">
        <text class="form-label">生日</text>
        <picker class="form-picker" mode="date" :value="form.birthday" start="1970-01-01" end="2008-12-31" @change="onBirthdayChange">
          <view class="form-right">
            <text :class="['form-value', { placeholder: !form.birthday }]">
              {{ form.birthday || '选择生日' }}
            </text>
            <text class="form-arrow">›</text>
          </view>
        </picker>
      </view>

      <view class="form-row">
        <text class="form-label">城市</text>
        <picker class="form-picker" mode="region" @change="onCityChange">
          <view class="form-right">
            <text :class="['form-value', { placeholder: !form.city }]">
              {{ form.city || '选择常驻城市' }}
            </text>
            <text class="form-arrow">›</text>
          </view>
        </picker>
      </view>

      <view class="form-row">
        <text class="form-label">身高</text>
        <picker class="form-picker" mode="selector" :range="heightOptions" @change="onHeightChange">
          <view class="form-right">
            <text :class="['form-value', { placeholder: !form.height }]">
              {{ form.height ? form.height + ' cm' : '选择身高' }}
            </text>
            <text class="form-arrow">›</text>
          </view>
        </picker>
      </view>

      <view class="form-row">
        <text class="form-label">学历</text>
        <picker class="form-picker" mode="selector" :range="educationOptions" @change="onEduChange">
          <view class="form-right">
            <text :class="['form-value', { placeholder: !form.education }]">
              {{ form.education || '选择学历' }}
            </text>
            <text class="form-arrow">›</text>
          </view>
        </picker>
      </view>

      <view class="form-row last">
        <text class="form-label">职业</text>
        <picker class="form-picker" mode="selector" :range="occupationOptions" @change="onOccChange">
          <view class="form-right">
            <text :class="['form-value', { placeholder: !form.occupation }]">
              {{ form.occupation || '选择行业/职业' }}
            </text>
            <text class="form-arrow">›</text>
          </view>
        </picker>
      </view>
    </view>

    <!-- 关于我 -->
    <view class="card">
      <text class="card-title">关于我</text>
      <view class="bio-wrapper">
        <textarea
          class="bio-input"
          v-model="form.bio"
          placeholder="介绍一下你的性格、爱好，或者期待遇到怎样的人..."
          maxlength="500"
          :auto-height="true"
          placeholder-class="ph-color"
        />
        <text class="bio-count">{{ (form.bio || '').length }}/500</text>
      </view>
    </view>

    <!-- 兴趣标签 -->
    <view class="card">
      <view class="card-title-row">
        <text class="card-title">兴趣标签</text>
        <text class="card-subtitle">{{ selectedInterests.length }}/10</text>
      </view>
      <text class="section-desc">选择契合的标签，更容易遇到同频的人</text>

      <view class="interest-group" v-for="group in interestGroups" :key="group.category">
        <text class="group-label">{{ group.category }}</text>
        <view class="tag-wall">
          <view
            class="tag-chip"
            :class="{ selected: selectedInterests.includes(tag.id) }"
            v-for="tag in group.tags"
            :key="tag.id"
            @tap="toggleInterest(tag.id)"
          >
            <text>{{ tag.name }}</text>
          </view>
        </view>
      </view>
    </view>

    <view class="bottom-spacer"></view>

    <!-- 悬浮保存按钮 -->
    <view class="fixed-bottom">
      <button class="save-btn" :class="{ 'is-saving': saving }" :loading="saving" @tap="saveProfile">
        完成并保存
      </button>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import { userApi } from '../../api'
import { useUserStore } from '../../stores/user'

const userStore = useUserStore()
const defaultAvatar = 'https://api.dicebear.com/7.x/avataaars/svg?seed=default'
const saving = ref(false)
const isFromLogin = ref(false)

// 选择器配置数据
const heightOptions = Array.from({ length: 81 }, (_, i) => i + 140) // 140-220cm
const educationOptions = ['高中及以下', '大专', '本科', '硕士', '博士']
const occupationOptions = [
  '在校学生', 'IT/互联网', '金融/投资', '医疗/健康', 
  '教育/科研', '传媒/影视', '艺术/设计', '法律/法务',
  '政府/事业单位', '人事/行政', '销售/市场', '自由职业', '其他行业'
]

interface PhotoItem {
  id?: number
  url: string
  is_avatar: boolean
  tempPath?: string
}

const photos = ref<PhotoItem[]>([])

onLoad((options: any) => {
  if (options?.from === 'login') {
    isFromLogin.value = true
  }
})

const form = reactive({
  nickname: '',
  gender: 0 as number,
  birthday: '',
  city: '',
  height: '' as string | number,
  education: '',
  occupation: '',
  bio: '',
  avatarUrl: '',
})

const allInterests = ref<any[]>([])
const selectedInterests = ref<number[]>([])

const interestGroups = computed(() => {
  const groups: Record<string, { category: string; tags: any[] }> = {}
  for (const tag of allInterests.value) {
    if (!groups[tag.category]) {
      groups[tag.category] = { category: tag.category, tags: [] }
    }
    groups[tag.category].tags.push(tag)
  }
  return Object.values(groups)
})

onMounted(async () => {
  await loadInterests()
  await loadProfile()
})

// === 数据加载 ===
async function loadProfile() {
  try {
    const res = await userApi.getMyProfile()
    const p = res.data
    if (p) {
      form.nickname = p.nickname || ''
      form.gender = p.gender || 0
      form.birthday = p.birthday || ''
      form.city = p.city || ''
      form.height = p.height || ''
      form.education = p.education || ''
      form.occupation = p.occupation || ''
      form.bio = p.bio || ''

      if (p.photos && p.photos.length > 0) {
        photos.value = p.photos.map((ph: any) => ({
          id: ph.id,
          url: ph.url,
          is_avatar: ph.is_avatar || false,
        }))
        const avatar = p.photos.find((ph: any) => ph.is_avatar)
        form.avatarUrl = avatar?.url || p.photos[0]?.url || ''
      }

      selectedInterests.value = p.interests?.map((i: any) => i.id) || []
    }
  } catch (e) {
    console.error('加载资料失败', e)
  }
}

async function loadInterests() {
  try {
    const res = await userApi.getAllInterests()
    allInterests.value = res.data || []
  } catch (e) {
    console.error('加载兴趣标签失败', e)
  }
}

// === Picker 处理 ===
function onBirthdayChange(e: any) {
  form.birthday = e.detail.value
}

function onCityChange(e: any) {
  // mode="region" e.detail.value 是一个数组 ['省', '市', '区']
  const val = e.detail.value
  if (Array.isArray(val) && val.length >= 2) {
    // 省市相同（如直辖市 北京 北京市），可以只取其一
    if (val[0] === val[1] || val[1].includes(val[0])) {
      form.city = val[1]
    } else {
      form.city = `${val[0]} ${val[1]}`
    }
  }
}

function onHeightChange(e: any) {
  form.height = heightOptions[e.detail.value]
}

function onEduChange(e: any) {
  form.education = educationOptions[e.detail.value]
}

function onOccChange(e: any) {
  form.occupation = occupationOptions[e.detail.value]
}

function toggleInterest(id: number) {
  const idx = selectedInterests.value.indexOf(id)
  if (idx >= 0) {
    selectedInterests.value.splice(idx, 1)
  } else if (selectedInterests.value.length < 10) {
    selectedInterests.value.push(id)
  } else {
    uni.showToast({ title: '最多选择10个标签', icon: 'none' })
  }
}

// === 照片处理 ===
async function chooseAvatar() {
  uni.chooseImage({
    count: 1,
    async success(res) {
      const tempPath = res.tempFilePaths[0]
      form.avatarUrl = tempPath
      try {
        const uploadRes = await userApi.uploadPhoto(tempPath, true)
        if (uploadRes.data) {
          const existingAvatar = photos.value.findIndex(p => p.is_avatar)
          if (existingAvatar >= 0) {
            photos.value[existingAvatar].is_avatar = false
          }
          photos.value.unshift({
            id: uploadRes.data.id,
            url: uploadRes.data.url || tempPath,
            is_avatar: true,
          })
        }
        uni.showToast({ title: '封面已更新', icon: 'success' })
      } catch (e) {
        uni.showToast({ title: '上传失败', icon: 'none' })
      }
    },
  })
}

function addPhoto() {
  const remaining = 9 - photos.value.length
  if (remaining <= 0) {
    uni.showToast({ title: '最多上传9张', icon: 'none' })
    return
  }
  uni.chooseImage({
    count: Math.min(remaining, 9),
    async success(res) {
      for (const tempPath of res.tempFilePaths) {
        try {
          const uploadRes = await userApi.uploadPhoto(tempPath, false)
          photos.value.push({
            id: uploadRes.data?.id,
            url: uploadRes.data?.url || tempPath,
            is_avatar: false,
          })
        } catch (e) {
          uni.showToast({ title: '部分上传失败', icon: 'none' })
        }
      }
    },
  })
}

async function deletePhoto(photo: PhotoItem, idx: number) {
  if (photo.is_avatar) {
    uni.showToast({ title: '不能删除封面', icon: 'none' })
    return
  }
  if (photo.id) {
    try {
      await userApi.deletePhoto(photo.id)
    } catch (e) {
      console.error(e)
    }
  }
  photos.value.splice(idx, 1)
}

function previewPhoto(idx: number) {
  const urls = photos.value.map(p => p.url)
  uni.previewImage({ urls, current: urls[idx] })
}

// === 提交 ===
async function saveProfile() {
  if (!form.nickname.trim()) {
    uni.showToast({ title: '请填写昵称', icon: 'none' })
    return
  }
  if (!form.gender) {
    uni.showToast({ title: '请选择性别', icon: 'none' })
    return
  }
  if (!form.birthday) {
    uni.showToast({ title: '请选择生日', icon: 'none' })
    return
  }

  saving.value = true
  try {
    const data: any = {
      nickname: form.nickname,
      gender: form.gender,
      birthday: form.birthday,
      city: form.city || undefined,
      bio: form.bio || undefined,
      education: form.education || undefined,
      occupation: form.occupation || undefined,
      interest_ids: selectedInterests.value,
    }
    if (form.height) data.height = Number(form.height)

    await userApi.updateProfile(data)
    await userStore.fetchProfile()
    uni.showToast({ title: '保存成功', icon: 'success' })
    setTimeout(() => {
      if (isFromLogin.value) {
        uni.switchTab({ url: '/pages/home/index' })
      } else {
        uni.navigateBack()
      }
    }, 1000)
  } catch (e) {
    console.error(e)
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
.edit-page { 
  min-height: 100vh; 
  background: #f4f6f8; 
  padding-bottom: 200rpx;
}

/* 头像区域 */
.avatar-section { 
  display: flex; 
  flex-direction: column; 
  align-items: center; 
  padding: 60rpx 0 40rpx; 
  background: linear-gradient(180deg, #fff 0%, #f4f6f8 100%); 
}
.avatar-wrapper { 
  position: relative; 
  width: 200rpx; 
  height: 200rpx; 
  margin-bottom: 16rpx;
}
.edit-avatar { 
  width: 200rpx; 
  height: 200rpx; 
  border-radius: 50%; 
  border: 6rpx solid #fff; 
  box-shadow: 0 12rpx 36rpx rgba(255, 71, 87, 0.15); 
}
.avatar-badge { 
  position: absolute; 
  bottom: 0; 
  right: 0; 
  width: 56rpx; 
  height: 56rpx; 
  background: #1a1a1a; 
  border-radius: 50%; 
  display: flex; 
  align-items: center; 
  justify-content: center; 
  border: 4rpx solid #fff; 
  box-shadow: 0 4rpx 8rpx rgba(0,0,0,0.1);
}
.badge-icon { font-size: 26rpx; }
.avatar-tip { font-size: 26rpx; color: #888; letter-spacing: 1rpx; }

/* 通用卡片样式 */
.card { 
  background: #fff; 
  margin: 0 24rpx 24rpx; 
  border-radius: 28rpx; 
  padding: 36rpx; 
  box-shadow: 0 4rpx 24rpx rgba(0, 0, 0, 0.02); 
}
.card-title { font-size: 34rpx; font-weight: 700; color: #1a1a1a; margin-bottom: 32rpx; display: block; letter-spacing: 1rpx; }
.card-title-row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16rpx; }
.card-subtitle { font-size: 28rpx; color: #ff4757; font-weight: 600; }
.section-desc { font-size: 24rpx; color: #999; margin-bottom: 24rpx; display: block; }

/* 照片墙 */
.photo-card { padding: 36rpx 24rpx; }
.photo-grid { display: flex; flex-wrap: wrap; gap: 12rpx; margin-bottom: 16rpx; }
.photo-slot { position: relative; width: calc(33.33% - 8rpx); aspect-ratio: 3 / 4; border-radius: 20rpx; overflow: hidden; background: #f8f9fa; }
.slot-photo { width: 100%; height: 100%; }
.slot-delete { position: absolute; top: 12rpx; right: 12rpx; width: 48rpx; height: 48rpx; border-radius: 50%; background: rgba(0,0,0,0.4); display: flex; align-items: center; justify-content: center; backdrop-filter: blur(4px); }
.delete-icon { font-size: 22rpx; color: #fff; font-weight: 600; }
.slot-badge { position: absolute; bottom: 0; left: 0; right: 0; background: linear-gradient(180deg, transparent, rgba(0,0,0,0.6)); padding: 20rpx 0 12rpx; text-align: center; }
.badge-text { font-size: 22rpx; color: #fff; font-weight: 600; letter-spacing: 1rpx; }
.add-slot { background: #f0f2f5; display: flex; flex-direction: column; align-items: center; justify-content: center; border: 2rpx dashed #dce0e5; }
.add-icon { font-size: 60rpx; color: #a0a5ab; line-height: 1; font-weight: 300; }
.photo-tip { font-size: 24rpx; color: #a0a5ab; text-align: center; display: block; margin-top: 16rpx; }

/* 表单行设计 */
.form-row { 
  display: flex; 
  align-items: center; 
  justify-content: space-between; 
  min-height: 100rpx; 
  border-bottom: 1rpx solid #f4f6f8; 
}
.form-row.last { border-bottom: none; }
.form-label { font-size: 30rpx; color: #1a1a1a; font-weight: 600; width: 140rpx; }
.form-right { flex: 1; display: flex; align-items: center; justify-content: flex-end; }
.form-picker { flex: 1; }
.form-input { font-size: 30rpx; color: #1a1a1a; font-weight: 500; width: 100%; }
.form-input.right { text-align: right; }
.form-value { font-size: 30rpx; color: #1a1a1a; font-weight: 500; }
.form-value.placeholder { color: #a0a5ab; font-weight: 400; }
.form-arrow { font-size: 36rpx; color: #c4c7cc; margin-left: 12rpx; font-weight: 300; margin-top: -4rpx; }
.ph-color { color: #a0a5ab; }

/* 性别按钮 */
.gender-group { display: flex; gap: 24rpx; justify-content: flex-end; flex: 1; }
.gender-btn { 
  padding: 12rpx 36rpx; 
  border-radius: 40rpx; 
  background: #f0f2f5; 
  font-size: 28rpx; 
  color: #666; 
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 8rpx;
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1); 
  border: 2rpx solid transparent;
}
.gender-icon { font-size: 32rpx; margin-top: -2rpx; }
.gender-btn.active { 
  background: #fff; 
  color: #1a1a1a; 
  border-color: #1a1a1a;
  box-shadow: 0 4rpx 12rpx rgba(0,0,0,0.05);
}

/* 关于我 */
.bio-wrapper { position: relative; }
.bio-input { 
  width: 100%; 
  min-height: 200rpx; 
  font-size: 30rpx; 
  color: #1a1a1a; 
  line-height: 1.6; 
  padding: 24rpx; 
  background: #f8f9fa; 
  border-radius: 20rpx; 
  box-sizing: border-box; 
}
.bio-count { position: absolute; bottom: 20rpx; right: 24rpx; font-size: 24rpx; color: #a0a5ab; font-weight: 500; }

/* 兴趣标签 */
.interest-group { margin-bottom: 36rpx; }
.interest-group:last-child { margin-bottom: 0; }
.group-label { font-size: 28rpx; color: #1a1a1a; font-weight: 600; margin-bottom: 20rpx; display: block; }
.tag-wall { display: flex; flex-wrap: wrap; gap: 20rpx 16rpx; }
.tag-chip { 
  padding: 14rpx 36rpx; 
  border-radius: 40rpx; 
  background: #f0f2f5; 
  font-size: 26rpx; 
  color: #555; 
  font-weight: 500;
  transition: all 0.25s; 
  border: 2rpx solid transparent; 
}
.tag-chip.selected { 
  background: rgba(255, 71, 87, 0.08); 
  color: #ff4757; 
  border-color: #ff4757; 
}

/* 底部按钮 */
.bottom-spacer { height: constant(safe-area-inset-bottom); height: env(safe-area-inset-bottom); }
.fixed-bottom { 
  position: fixed; 
  bottom: 0; 
  left: 0; 
  right: 0; 
  padding: 24rpx 40rpx; 
  padding-bottom: calc(24rpx + env(safe-area-inset-bottom)); 
  background: rgba(255,255,255,0.9); 
  backdrop-filter: blur(20px);
  border-top: 1rpx solid rgba(0,0,0,0.05);
  z-index: 100;
}
.save-btn { 
  width: 100%; 
  height: 96rpx; 
  background: #1a1a1a; 
  border-radius: 48rpx; 
  color: #fff; 
  font-size: 32rpx; 
  font-weight: 600; 
  display: flex; 
  align-items: center; 
  justify-content: center; 
  border: none; 
  box-shadow: 0 8rpx 24rpx rgba(0,0,0,0.15);
  transition: transform 0.1s;
}
.save-btn:active { transform: scale(0.98); }
.save-btn.is-saving { opacity: 0.8; }
.save-btn::after { border: none; }
</style>
