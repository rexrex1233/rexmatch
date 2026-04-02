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
      <text class="avatar-tip">点击更换头像</text>
    </view>

    <!-- 照片墙 (最多9张) -->
    <view class="card">
      <view class="card-title-row">
        <text class="card-title">我的照片</text>
        <text class="card-subtitle">{{ photos.length }}/9</text>
      </view>
      <view class="photo-grid">
        <view class="photo-slot" v-for="(photo, idx) in photos" :key="photo.id || idx">
          <image class="slot-photo" :src="photo.url" mode="aspectFill" @tap="previewPhoto(idx)" />
          <view class="slot-delete" @tap.stop="deletePhoto(photo, idx)">
            <text class="delete-icon">✕</text>
          </view>
          <view class="slot-badge" v-if="photo.is_avatar">
            <text class="badge-text">头像</text>
          </view>
        </view>
        <view class="photo-slot add-slot" v-if="photos.length < 9" @tap="addPhoto">
          <text class="add-icon">+</text>
          <text class="add-text">添加</text>
        </view>
      </view>
      <text class="photo-tip">添加更多照片能获得更多关注</text>
    </view>

    <!-- 基本信息卡片 -->
    <view class="card">
      <text class="card-title">基本信息</text>

      <view class="form-row">
        <text class="form-label">昵称</text>
        <input class="form-input" v-model="form.nickname" placeholder="取个好听的名字" maxlength="20" />
      </view>

      <view class="form-row">
        <text class="form-label">性别</text>
        <view class="gender-group">
          <view class="gender-chip" :class="{ active: form.gender === 1 }" @tap="form.gender = 1">
            <text>♂ 男</text>
          </view>
          <view class="gender-chip" :class="{ active: form.gender === 2 }" @tap="form.gender = 2">
            <text>♀ 女</text>
          </view>
        </view>
      </view>

      <view class="form-row" @tap="openBirthdayPicker">
        <text class="form-label">生日</text>
        <view class="form-right">
          <text :class="['form-value', { placeholder: !form.birthday }]">
            {{ form.birthday || '选择生日' }}
          </text>
          <text class="form-arrow">›</text>
        </view>
        <picker
          class="hidden-picker"
          mode="date"
          :value="form.birthday"
          start="1970-01-01"
          end="2008-12-31"
          @change="onBirthdayChange"
        >
          <view ref="birthdayPickerRef"></view>
        </picker>
      </view>

      <view class="form-row">
        <text class="form-label">城市</text>
        <view class="form-right">
          <input class="form-input right" v-model="form.city" placeholder="你在哪座城市" />
        </view>
      </view>

      <view class="form-row">
        <text class="form-label">身高</text>
        <view class="form-right">
          <input class="form-input right short" v-model="form.height" placeholder="选填" type="number" />
          <text class="form-unit">cm</text>
        </view>
      </view>

      <view class="form-row" @tap="showEduPicker = true">
        <text class="form-label">学历</text>
        <view class="form-right">
          <text :class="['form-value', { placeholder: !form.education }]">
            {{ form.education || '选择学历' }}
          </text>
          <text class="form-arrow">›</text>
        </view>
      </view>

      <view class="form-row last">
        <text class="form-label">职业</text>
        <view class="form-right">
          <input class="form-input right" v-model="form.occupation" placeholder="你做什么工作" />
        </view>
      </view>
    </view>

    <!-- 关于我卡片 -->
    <view class="card">
      <text class="card-title">关于我</text>
      <view class="bio-wrapper">
        <textarea
          class="bio-input"
          v-model="form.bio"
          placeholder="写点什么让别人更了解你吧..."
          maxlength="500"
          :auto-height="true"
        />
        <text class="bio-count">{{ (form.bio || '').length }}/500</text>
      </view>
    </view>

    <!-- 兴趣标签卡片 -->
    <view class="card">
      <view class="card-title-row">
        <text class="card-title">兴趣标签</text>
        <text class="card-subtitle">{{ selectedInterests.length }}/10</text>
      </view>

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
      <button class="save-btn" :loading="saving" @tap="saveProfile">
        保存资料
      </button>
    </view>

    <!-- 学历选择底部弹窗 -->
    <view class="picker-mask" v-if="showEduPicker" @tap="showEduPicker = false">
      <view class="picker-sheet" @tap.stop>
        <view class="picker-header">
          <text class="picker-cancel" @tap="showEduPicker = false">取消</text>
          <text class="picker-title">选择学历</text>
          <view style="width: 80rpx"></view>
        </view>
        <view
          class="picker-option"
          :class="{ active: form.education === opt }"
          v-for="opt in educationOptions"
          :key="opt"
          @tap="form.education = opt; showEduPicker = false"
        >
          <text>{{ opt }}</text>
          <text class="check-icon" v-if="form.education === opt">✓</text>
        </view>
      </view>
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
const educationOptions = ['高中', '大专', '本科', '硕士', '博士']
const saving = ref(false)
const showEduPicker = ref(false)
const isFromLogin = ref(false)

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

function onBirthdayChange(e: any) {
  form.birthday = e.detail.value
}

function openBirthdayPicker() {}

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
        uni.showToast({ title: '头像已更新', icon: 'success' })
      } catch (e) {
        console.error('上传失败', e)
        uni.showToast({ title: '上传失败', icon: 'none' })
      }
    },
  })
}

function addPhoto() {
  const remaining = 9 - photos.value.length
  if (remaining <= 0) {
    uni.showToast({ title: '最多9张照片', icon: 'none' })
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
          console.error('上传失败', e)
          uni.showToast({ title: '部分照片上传失败', icon: 'none' })
        }
      }
    },
  })
}

async function deletePhoto(photo: PhotoItem, idx: number) {
  if (photo.is_avatar) {
    uni.showToast({ title: '不能删除头像照片', icon: 'none' })
    return
  }
  if (photo.id) {
    try {
      await userApi.deletePhoto(photo.id)
    } catch (e) {
      console.error('删除失败', e)
    }
  }
  photos.value.splice(idx, 1)
}

function previewPhoto(idx: number) {
  const urls = photos.value.map(p => p.url)
  uni.previewImage({ urls, current: urls[idx] })
}

async function saveProfile() {
  if (!form.nickname.trim()) {
    uni.showToast({ title: '请输入昵称', icon: 'none' })
    return
  }
  if (!form.gender) {
    uni.showToast({ title: '请选择性别', icon: 'none' })
    return
  }

  saving.value = true
  try {
    const data: any = {
      nickname: form.nickname,
      gender: form.gender,
      city: form.city || undefined,
      bio: form.bio || undefined,
      education: form.education || undefined,
      occupation: form.occupation || undefined,
      interest_ids: selectedInterests.value,
    }
    if (form.birthday) data.birthday = form.birthday
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
    console.error('保存失败', e)
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
.edit-page { min-height: 100vh; background: #f7f8fa; }

/* ---- 头像区域 ---- */
.avatar-section { display: flex; flex-direction: column; align-items: center; padding: 48rpx 0 32rpx; background: linear-gradient(180deg, #fff0f3 0%, #f7f8fa 100%); }
.avatar-wrapper { position: relative; width: 180rpx; height: 180rpx; }
.edit-avatar { width: 180rpx; height: 180rpx; border-radius: 50%; border: 6rpx solid #fff; box-shadow: 0 8rpx 30rpx rgba(255, 107, 129, 0.25); }
.avatar-badge { position: absolute; bottom: 4rpx; right: 4rpx; width: 52rpx; height: 52rpx; background: linear-gradient(135deg, #ff6b81, #ff4757); border-radius: 50%; display: flex; align-items: center; justify-content: center; border: 4rpx solid #fff; }
.badge-icon { font-size: 24rpx; }
.avatar-tip { font-size: 24rpx; color: #b3b3b3; margin-top: 16rpx; }

/* ---- 照片墙 ---- */
.photo-grid { display: flex; flex-wrap: wrap; gap: 16rpx; }
.photo-slot { position: relative; width: calc(33.33% - 11rpx); aspect-ratio: 3 / 4; border-radius: 16rpx; overflow: hidden; }
.slot-photo { width: 100%; height: 100%; }
.slot-delete { position: absolute; top: 8rpx; right: 8rpx; width: 44rpx; height: 44rpx; border-radius: 50%; background: rgba(0,0,0,0.5); display: flex; align-items: center; justify-content: center; }
.delete-icon { font-size: 24rpx; color: #fff; font-weight: bold; }
.slot-badge { position: absolute; bottom: 0; left: 0; right: 0; background: rgba(255,107,129,0.85); padding: 6rpx 0; text-align: center; }
.badge-text { font-size: 20rpx; color: #fff; font-weight: 600; }
.add-slot { background: #f0f1f5; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 8rpx; border: 3rpx dashed #d0d0d0; }
.add-icon { font-size: 48rpx; color: #ccc; line-height: 1; }
.add-text { font-size: 22rpx; color: #b3b3b3; }
.photo-tip { font-size: 22rpx; color: #b3b3b3; margin-top: 16rpx; }

/* ---- 卡片通用 ---- */
.card { background: #fff; margin: 20rpx 24rpx; border-radius: 24rpx; padding: 32rpx; box-shadow: 0 2rpx 12rpx rgba(0, 0, 0, 0.04); }
.card-title { font-size: 32rpx; font-weight: 700; color: #1a1a1a; margin-bottom: 24rpx; display: block; }
.card-title-row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24rpx; }
.card-subtitle { font-size: 26rpx; color: #ff6b81; font-weight: 600; }

/* ---- 表单行 ---- */
.form-row { display: flex; align-items: center; justify-content: space-between; padding: 28rpx 0; border-bottom: 1rpx solid #f0f1f5; }
.form-row.last { border-bottom: none; }
.form-label { font-size: 30rpx; color: #1a1a1a; font-weight: 500; flex-shrink: 0; width: 120rpx; }
.form-right { flex: 1; display: flex; align-items: center; justify-content: flex-end; gap: 8rpx; }
.form-input { font-size: 28rpx; color: #1a1a1a; flex: 1; }
.form-input.right { text-align: right; }
.form-input.short { width: 120rpx; flex: none; }
.form-value { font-size: 28rpx; color: #1a1a1a; }
.form-value.placeholder { color: #b3b3b3; }
.form-arrow { font-size: 32rpx; color: #ccc; margin-left: 4rpx; }
.form-unit { font-size: 26rpx; color: #999; }
.hidden-picker { position: absolute; opacity: 0; width: 0; height: 0; }

/* ---- 性别 ---- */
.gender-group { display: flex; gap: 20rpx; }
.gender-chip { padding: 12rpx 36rpx; border-radius: 32rpx; background: #f0f1f5; font-size: 28rpx; color: #666; transition: all 0.2s; }
.gender-chip.active { background: linear-gradient(135deg, #ff6b81, #ff4757); color: #fff; box-shadow: 0 4rpx 16rpx rgba(255, 71, 87, 0.3); }

/* ---- 关于我 ---- */
.bio-wrapper { position: relative; }
.bio-input { width: 100%; min-height: 160rpx; font-size: 28rpx; color: #1a1a1a; line-height: 1.7; padding: 20rpx; background: #f7f8fa; border-radius: 16rpx; box-sizing: border-box; }
.bio-count { position: absolute; bottom: 16rpx; right: 20rpx; font-size: 22rpx; color: #ccc; }

/* ---- 兴趣标签 ---- */
.interest-group { margin-bottom: 28rpx; }
.interest-group:last-child { margin-bottom: 0; }
.group-label { font-size: 26rpx; color: #999; font-weight: 500; margin-bottom: 16rpx; display: block; }
.tag-wall { display: flex; flex-wrap: wrap; gap: 16rpx; }
.tag-chip { padding: 14rpx 32rpx; border-radius: 32rpx; background: #f0f1f5; font-size: 26rpx; color: #666; transition: all 0.2s; border: 2rpx solid transparent; }
.tag-chip.selected { background: rgba(255, 107, 129, 0.1); color: #ff4757; border-color: #ff6b81; font-weight: 600; }

/* ---- 底部按钮 ---- */
.bottom-spacer { height: 160rpx; }
.fixed-bottom { position: fixed; bottom: 0; left: 0; right: 0; padding: 20rpx 32rpx; padding-bottom: calc(20rpx + env(safe-area-inset-bottom)); background: linear-gradient(180deg, rgba(247,248,250,0) 0%, rgba(247,248,250,1) 30%); }
.save-btn { width: 100%; height: 96rpx; background: linear-gradient(135deg, #ff6b81, #ff4757); border-radius: 48rpx; color: #fff; font-size: 32rpx; font-weight: 600; letter-spacing: 2rpx; display: flex; align-items: center; justify-content: center; border: none; box-shadow: 0 8rpx 30rpx rgba(255, 71, 87, 0.35); }
.save-btn::after { border: none; }

/* ---- 底部弹窗选择器 ---- */
.picker-mask { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0, 0, 0, 0.45); z-index: 200; display: flex; align-items: flex-end; }
.picker-sheet { width: 100%; background: #fff; border-radius: 28rpx 28rpx 0 0; padding-bottom: calc(20rpx + env(safe-area-inset-bottom)); max-height: 70vh; overflow-y: auto; }
.picker-header { display: flex; align-items: center; justify-content: space-between; padding: 28rpx 32rpx; border-bottom: 1rpx solid #f0f1f5; }
.picker-cancel { font-size: 28rpx; color: #999; width: 80rpx; }
.picker-title { font-size: 30rpx; font-weight: 600; color: #1a1a1a; }
.picker-option { display: flex; align-items: center; justify-content: space-between; padding: 32rpx 40rpx; font-size: 30rpx; color: #333; }
.picker-option.active { color: #ff4757; font-weight: 600; }
.check-icon { color: #ff4757; font-size: 32rpx; font-weight: bold; }
</style>
