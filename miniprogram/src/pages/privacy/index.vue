<template>
  <view class="privacy-page">
    <!-- 黑名单管理 -->
    <view class="section">
      <view class="section-header">
        <text class="section-title">黑名单</text>
        <text class="section-hint" v-if="blockList.length">{{ blockList.length }} 人</text>
      </view>

      <view class="block-list" v-if="blockList.length">
        <view class="block-item" v-for="item in blockList" :key="item.user_id">
          <view class="block-left">
            <image class="block-avatar" :src="item.avatar_url || defaultAvatar" mode="aspectFill" />
            <view class="block-info">
              <text class="block-name">{{ item.nickname }}</text>
              <text class="block-time">{{ formatDate(item.blocked_at) }}</text>
            </view>
          </view>
          <view class="unblock-btn" @tap="handleUnblock(item)">
            <text class="unblock-text">取消拉黑</text>
          </view>
        </view>
      </view>

      <view class="empty" v-else>
        <text class="empty-icon">🕊</text>
        <text class="empty-text">黑名单为空</text>
        <text class="empty-hint">被拉黑的用户会出现在这里</text>
      </view>
    </view>

    <!-- 隐私说明 -->
    <view class="section">
      <view class="section-header">
        <text class="section-title">隐私保护</text>
      </view>
      <view class="privacy-items">
        <view class="privacy-row">
          <view class="privacy-icon-wrap green"><text>🔒</text></view>
          <view class="privacy-desc">
            <text class="pd-title">信息安全</text>
            <text class="pd-hint">你的真实手机号不会被其他用户看到</text>
          </view>
        </view>
        <view class="privacy-row">
          <view class="privacy-icon-wrap blue"><text>🛡</text></view>
          <view class="privacy-desc">
            <text class="pd-title">举报机制</text>
            <text class="pd-hint">不当行为可随时举报，平台将及时处理</text>
          </view>
        </view>
        <view class="privacy-row">
          <view class="privacy-icon-wrap purple"><text>👁</text></view>
          <view class="privacy-desc">
            <text class="pd-title">浏览隐私</text>
            <text class="pd-hint">跳过或喜欢不会通知对方具体操作</text>
          </view>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { reportApi } from '../../api/index'

const defaultAvatar = 'https://api.dicebear.com/7.x/avataaars/svg?seed=default'
const blockList = ref<any[]>([])

onMounted(async () => {
  await loadBlockList()
})

async function loadBlockList() {
  try {
    const res = await reportApi.getBlockList()
    blockList.value = res.data || []
  } catch {}
}

function handleUnblock(item: any) {
  uni.showModal({
    title: '取消拉黑',
    content: `确定取消拉黑 ${item.nickname} 吗？`,
    confirmColor: '#ff4757',
    success(res) {
      if (res.confirm) {
        reportApi.unblock(item.user_id).then(() => {
          uni.showToast({ title: '已取消拉黑', icon: 'success' })
          blockList.value = blockList.value.filter(b => b.user_id !== item.user_id)
        }).catch(() => {
          uni.showToast({ title: '操作失败', icon: 'none' })
        })
      }
    },
  })
}

function formatDate(dateStr: string) {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  return `${d.getFullYear()}-${(d.getMonth() + 1).toString().padStart(2, '0')}-${d.getDate().toString().padStart(2, '0')}`
}
</script>

<style scoped>
.privacy-page { min-height: 100vh; background: #f7f8fa; padding-bottom: calc(40rpx + env(safe-area-inset-bottom)); }

.section { background: #fff; margin: 24rpx; border-radius: 24rpx; overflow: hidden; box-shadow: 0 2rpx 12rpx rgba(0,0,0,0.04); }

.section-header { display: flex; align-items: center; justify-content: space-between; padding: 28rpx 32rpx 20rpx; }
.section-title { font-size: 32rpx; font-weight: 700; color: #1a1a1a; }
.section-hint { font-size: 24rpx; color: #999; }

/* Block list */
.block-item { display: flex; align-items: center; justify-content: space-between; padding: 24rpx 32rpx; border-bottom: 1rpx solid #f5f6f8; }
.block-item:last-child { border-bottom: none; }
.block-left { display: flex; align-items: center; gap: 20rpx; flex: 1; min-width: 0; }
.block-avatar { width: 88rpx; height: 88rpx; border-radius: 50%; flex-shrink: 0; }
.block-info { display: flex; flex-direction: column; min-width: 0; }
.block-name { font-size: 30rpx; color: #1a1a1a; font-weight: 600; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.block-time { font-size: 22rpx; color: #ccc; margin-top: 4rpx; }
.unblock-btn { padding: 12rpx 28rpx; border-radius: 24rpx; border: 2rpx solid #e8e8e8; flex-shrink: 0; }
.unblock-text { font-size: 24rpx; color: #666; }

/* Empty */
.empty { display: flex; flex-direction: column; align-items: center; padding: 60rpx 0 48rpx; }
.empty-icon { font-size: 56rpx; margin-bottom: 16rpx; }
.empty-text { font-size: 30rpx; color: #666; font-weight: 600; margin-bottom: 8rpx; }
.empty-hint { font-size: 24rpx; color: #ccc; }

/* Privacy items */
.privacy-items { padding: 0 32rpx 28rpx; }
.privacy-row { display: flex; align-items: flex-start; gap: 20rpx; padding: 20rpx 0; border-bottom: 1rpx solid #f5f6f8; }
.privacy-row:last-child { border-bottom: none; }
.privacy-icon-wrap { width: 64rpx; height: 64rpx; border-radius: 16rpx; display: flex; align-items: center; justify-content: center; flex-shrink: 0; font-size: 28rpx; }
.privacy-icon-wrap.green { background: rgba(7,193,96,0.1); }
.privacy-icon-wrap.blue { background: rgba(116,185,255,0.1); }
.privacy-icon-wrap.purple { background: rgba(162,155,254,0.1); }
.privacy-desc { display: flex; flex-direction: column; }
.pd-title { font-size: 28rpx; color: #1a1a1a; font-weight: 600; }
.pd-hint { font-size: 24rpx; color: #999; margin-top: 4rpx; line-height: 1.5; }
</style>
