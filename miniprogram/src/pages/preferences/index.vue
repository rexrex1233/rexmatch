<template>
  <view class="pref-page">
    <!-- 性别 -->
    <view class="pref-card">
      <text class="card-title">期望性别</text>
      <view class="chip-row">
        <view :class="['chip', { active: form.preferred_gender === null }]" @tap="form.preferred_gender = null">
          <text>不限</text>
        </view>
        <view :class="['chip', { active: form.preferred_gender === 1 }]" @tap="form.preferred_gender = 1">
          <text>♂ 男生</text>
        </view>
        <view :class="['chip', { active: form.preferred_gender === 2 }]" @tap="form.preferred_gender = 2">
          <text>♀ 女生</text>
        </view>
      </view>
    </view>

    <!-- 年龄 -->
    <view class="pref-card">
      <text class="card-title">期望年龄</text>
      <view class="age-row">
        <view class="age-input-wrap">
          <input class="age-input" type="number" v-model="form.min_age" placeholder="最小" />
          <text class="age-unit">岁</text>
        </view>
        <text class="age-dash">—</text>
        <view class="age-input-wrap">
          <input class="age-input" type="number" v-model="form.max_age" placeholder="最大" />
          <text class="age-unit">岁</text>
        </view>
      </view>
    </view>

    <!-- 城市 -->
    <view class="pref-card">
      <text class="card-title">期望城市</text>
      <input class="text-input" v-model="form.preferred_city" placeholder="不限" />
    </view>

    <!-- 学历 -->
    <view class="pref-card">
      <text class="card-title">期望学历</text>
      <view class="chip-row">
        <view
          :class="['chip', { active: form.preferred_education === opt }]"
          v-for="opt in eduOptions"
          :key="opt"
          @tap="form.preferred_education = form.preferred_education === opt ? null : opt"
        >
          <text>{{ opt }}</text>
        </view>
      </view>
    </view>

    <!-- 性格标签 -->
    <view class="pref-card">
      <view class="title-row">
        <text class="card-title">喜欢的性格</text>
        <text class="card-sub">{{ (form.personality_tags || []).length }}/5</text>
      </view>
      <view class="chip-row">
        <view
          :class="['chip', { active: (form.personality_tags || []).includes(tag) }]"
          v-for="tag in personalityOptions"
          :key="tag"
          @tap="toggleTag(tag)"
        >
          <text>{{ tag }}</text>
        </view>
      </view>
    </view>

    <view class="bottom-spacer"></view>

    <!-- 保存按钮 -->
    <view class="fixed-bottom">
      <button class="save-btn" :loading="saving" @tap="savePreferences">
        保存偏好
      </button>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { userApi } from '../../api'

const saving = ref(false)
const eduOptions = ['不限', '大专', '本科', '硕士', '博士']
const personalityOptions = [
  '温柔体贴', '阳光开朗', '幽默风趣', '踏实稳重',
  '独立自主', '善解人意', '积极向上', '文艺清新',
  '热爱运动', '社交达人', '安静内敛', '浪漫多情',
]

const form = reactive<any>({
  preferred_gender: null,
  min_age: '',
  max_age: '',
  preferred_city: '',
  preferred_education: null,
  personality_tags: [] as string[],
})

onMounted(async () => {
  try {
    const res = await userApi.getPreferences()
    const p = res.data
    if (p) {
      form.preferred_gender = p.preferred_gender || null
      form.min_age = p.min_age || ''
      form.max_age = p.max_age || ''
      form.preferred_city = p.preferred_city || ''
      form.preferred_education = p.preferred_education || null
      form.personality_tags = p.personality_tags || []
    }
  } catch (e) {
    console.error('加载偏好失败', e)
  }
})

function toggleTag(tag: string) {
  const tags = form.personality_tags || []
  const idx = tags.indexOf(tag)
  if (idx >= 0) {
    tags.splice(idx, 1)
  } else if (tags.length < 5) {
    tags.push(tag)
  } else {
    uni.showToast({ title: '最多选择5个', icon: 'none' })
  }
  form.personality_tags = [...tags]
}

async function savePreferences() {
  saving.value = true
  try {
    const data: any = {}
    if (form.preferred_gender) data.preferred_gender = form.preferred_gender
    if (form.min_age) data.min_age = Number(form.min_age)
    if (form.max_age) data.max_age = Number(form.max_age)
    if (form.preferred_city) data.preferred_city = form.preferred_city
    if (form.preferred_education && form.preferred_education !== '不限') {
      data.preferred_education = form.preferred_education
    }
    if (form.personality_tags?.length) data.personality_tags = form.personality_tags

    await userApi.updatePreferences(data)
    uni.showToast({ title: '保存成功', icon: 'success' })
    setTimeout(() => uni.navigateBack(), 800)
  } catch (e) {
    console.error('保存失败', e)
    uni.showToast({ title: '保存失败', icon: 'none' })
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
.pref-page {
  min-height: 100vh;
  background: #f7f8fa;
}

.pref-card {
  background: #fff;
  margin: 20rpx 24rpx;
  border-radius: 24rpx;
  padding: 28rpx 32rpx;
  box-shadow: 0 2rpx 12rpx rgba(0,0,0,0.04);
}

.card-title {
  font-size: 30rpx;
  font-weight: 700;
  color: #1a1a1a;
  margin-bottom: 20rpx;
  display: block;
}

.title-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20rpx;
}

.card-sub {
  font-size: 26rpx;
  color: #ff6b81;
  font-weight: 600;
}

.chip-row {
  display: flex;
  flex-wrap: wrap;
  gap: 16rpx;
}

.chip {
  padding: 14rpx 32rpx;
  border-radius: 32rpx;
  background: #f0f1f5;
  font-size: 26rpx;
  color: #666;
  transition: all 0.2s;
}

.chip.active {
  background: rgba(255,107,129,0.1);
  color: #ff4757;
  font-weight: 600;
  border: 2rpx solid rgba(255,107,129,0.3);
}

.age-row {
  display: flex;
  align-items: center;
  gap: 16rpx;
}

.age-input-wrap {
  flex: 1;
  display: flex;
  align-items: center;
  background: #f0f1f5;
  border-radius: 16rpx;
  padding: 0 20rpx;
}

.age-input {
  flex: 1;
  height: 80rpx;
  font-size: 28rpx;
  color: #1a1a1a;
}

.age-unit {
  font-size: 26rpx;
  color: #999;
}

.age-dash {
  font-size: 28rpx;
  color: #ccc;
}

.text-input {
  width: 100%;
  height: 80rpx;
  background: #f0f1f5;
  border-radius: 16rpx;
  padding: 0 24rpx;
  font-size: 28rpx;
  color: #1a1a1a;
  box-sizing: border-box;
}

.bottom-spacer { height: 160rpx; }

.fixed-bottom {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 20rpx 32rpx;
  padding-bottom: calc(20rpx + env(safe-area-inset-bottom));
  background: linear-gradient(180deg, rgba(247,248,250,0) 0%, rgba(247,248,250,1) 30%);
}

.save-btn {
  width: 100%;
  height: 96rpx;
  background: linear-gradient(135deg, #ff6b81, #ff4757);
  border-radius: 48rpx;
  color: #fff;
  font-size: 32rpx;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  box-shadow: 0 8rpx 30rpx rgba(255,71,87,0.35);
}

.save-btn::after { border: none; }
</style>
