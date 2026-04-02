<template>
  <view class="chat-page">
    <!-- 搜索栏 -->
    <view class="search-bar">
      <view class="search-inner">
        <text class="search-icon">🔍</text>
        <text class="search-placeholder">搜索</text>
      </view>
    </view>

    <!-- 骨架屏 -->
    <view class="skeleton" v-if="loading && matches.length === 0 && chats.length === 0">
      <view class="sk-match-section">
        <view class="sk-label shimmer"></view>
        <view class="sk-match-row">
          <view class="sk-match-item" v-for="i in 4" :key="i">
            <view class="sk-match-avatar shimmer"></view>
            <view class="sk-match-name shimmer"></view>
          </view>
        </view>
      </view>
      <view class="sk-chat-list">
        <view class="sk-chat-item" v-for="i in 5" :key="i">
          <view class="sk-chat-avatar shimmer"></view>
          <view class="sk-chat-body">
            <view class="sk-chat-name shimmer"></view>
            <view class="sk-chat-msg shimmer"></view>
          </view>
        </view>
      </view>
    </view>

    <!-- 内容区域（下拉刷新） -->
    <scroll-view
      scroll-y
      class="content-scroll"
      v-if="!loading || matches.length > 0 || chats.length > 0"
      refresher-enabled
      :refresher-triggered="refreshing"
      @refresherrefresh="onRefresh"
    >
      <!-- 新匹配横向列表 -->
      <view class="match-section" v-if="matches.length">
        <text class="section-label">新匹配</text>
        <scroll-view scroll-x class="match-scroll" :show-scrollbar="false">
          <view class="match-list-inner">
            <view class="match-card" v-for="m in matches" :key="m.match_id" @tap="goChat(m.match_id, m.partner_nickname)">
              <view class="match-avatar-ring">
                <image class="match-avatar" :src="m.partner_avatar || defaultAvatar" mode="aspectFill" />
              </view>
              <text class="match-nick">{{ m.partner_nickname }}</text>
            </view>
          </view>
        </scroll-view>
      </view>

      <!-- 消息列表 -->
      <view class="msg-section" v-if="chats.length">
        <text class="section-label" style="padding: 0 32rpx;">消息</text>
        <view class="chat-list">
          <view class="chat-item" v-for="chat in chats" :key="chat.match_id" @tap="goChat(chat.match_id, chat.partner_nickname)">
            <view class="chat-avatar-wrap">
              <image class="chat-avatar" :src="chat.partner_avatar || defaultAvatar" mode="aspectFill" />
              <view class="online-dot" v-if="chat.is_online"></view>
              <view class="unread-dot" v-if="chat.unread_count > 0">
                <text class="unread-num">{{ chat.unread_count > 99 ? '99+' : chat.unread_count }}</text>
              </view>
            </view>
            <view class="chat-body">
              <view class="chat-top-row">
                <text class="chat-name">{{ chat.partner_nickname }}</text>
                <text class="chat-time">{{ formatTime(chat.last_message_at) }}</text>
              </view>
              <text class="chat-preview">{{ chat.last_message || '还没聊过，快去打个招呼吧' }}</text>
            </view>
          </view>
        </view>
      </view>

      <!-- 空状态 -->
      <view class="empty-state" v-if="!loading && chats.length === 0 && matches.length === 0">
        <view class="empty-circle">
          <text class="empty-icon">💬</text>
        </view>
        <text class="empty-title">还没有匹配和消息</text>
        <text class="empty-desc">去首页划一划，遇见心仪的TA</text>
      </view>
    </scroll-view>
  </view>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { chatApi, matchApi } from '../../api'

const defaultAvatar = 'https://api.dicebear.com/7.x/avataaars/svg?seed=default'
const loading = ref(false)
const refreshing = ref(false)
const matches = ref<any[]>([])
const chats = ref<any[]>([])

onShow(() => {
  loadData()
})

async function loadData() {
  loading.value = true
  try {
    const [matchRes, chatRes] = await Promise.all([
      matchApi.getMatchList(),
      chatApi.getChatList(),
    ])
    matches.value = matchRes.data || []
    chats.value = chatRes.data || []
    const totalUnread = chats.value.reduce((sum: number, c: any) => sum + (c.unread_count || 0), 0)
    if (totalUnread > 0) {
      uni.setTabBarBadge({ index: 2, text: String(totalUnread > 99 ? '99+' : totalUnread) })
    } else {
      uni.removeTabBarBadge({ index: 2 })
    }
  } finally {
    loading.value = false
    refreshing.value = false
  }
}

async function onRefresh() {
  refreshing.value = true
  await loadData()
}

function goChat(matchId: number, nickname: string) {
  uni.navigateTo({
    url: `/pages/chat-detail/index?matchId=${matchId}&nickname=${encodeURIComponent(nickname)}`,
  })
}

function formatTime(timeStr: string | null): string {
  if (!timeStr) return ''
  const d = new Date(timeStr)
  const now = new Date()
  const diff = now.getTime() - d.getTime()
  if (diff < 60000) return '刚刚'
  if (diff < 3600000) return `${Math.floor(diff / 60000)}分钟前`
  if (diff < 86400000) return `${Math.floor(diff / 3600000)}小时前`
  return `${d.getMonth() + 1}/${d.getDate()}`
}
</script>

<style scoped>
.chat-page { min-height: 100vh; background: #f7f8fa; }

.search-bar { padding: 16rpx 32rpx 12rpx; background: #fff; }
.search-inner { display: flex; align-items: center; gap: 12rpx; background: #f0f1f5; border-radius: 36rpx; padding: 16rpx 28rpx; }
.search-icon { font-size: 28rpx; }
.search-placeholder { font-size: 26rpx; color: #b3b3b3; }

/* ---- 骨架屏 ---- */
.skeleton { padding: 0; }
.sk-match-section { background: #fff; padding: 24rpx 32rpx 20rpx; margin-bottom: 16rpx; }
.sk-label { width: 100rpx; height: 24rpx; border-radius: 12rpx; margin-bottom: 20rpx; }
.sk-match-row { display: flex; gap: 28rpx; }
.sk-match-item { display: flex; flex-direction: column; align-items: center; gap: 10rpx; }
.sk-match-avatar { width: 108rpx; height: 108rpx; border-radius: 50%; }
.sk-match-name { width: 80rpx; height: 20rpx; border-radius: 10rpx; }
.sk-chat-list { background: #fff; padding: 24rpx 32rpx; }
.sk-chat-item { display: flex; align-items: center; gap: 20rpx; padding: 20rpx 0; border-bottom: 1rpx solid #f5f6f8; }
.sk-chat-avatar { width: 100rpx; height: 100rpx; border-radius: 50%; flex-shrink: 0; }
.sk-chat-body { flex: 1; }
.sk-chat-name { width: 40%; height: 28rpx; border-radius: 14rpx; margin-bottom: 12rpx; }
.sk-chat-msg { width: 70%; height: 24rpx; border-radius: 12rpx; }

@keyframes shimmer {
  0% { background-position: -200% 0; }
  100% { background-position: 200% 0; }
}
.shimmer {
  background: linear-gradient(90deg, #e8e8e8 25%, #f5f5f5 50%, #e8e8e8 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
}

.content-scroll { height: calc(100vh - 88rpx); }

/* ---- 新匹配 ---- */
.match-section { background: #fff; padding: 24rpx 0 20rpx; margin-bottom: 16rpx; }
.section-label { font-size: 26rpx; color: #999; font-weight: 600; margin-bottom: 20rpx; display: block; padding-left: 32rpx; text-transform: uppercase; letter-spacing: 2rpx; }
.match-scroll { white-space: nowrap; padding-left: 32rpx; }
.match-list-inner { display: inline-flex; gap: 28rpx; padding-right: 32rpx; }
.match-card { display: flex; flex-direction: column; align-items: center; width: 120rpx; }
.match-avatar-ring { width: 108rpx; height: 108rpx; border-radius: 50%; padding: 4rpx; background: linear-gradient(135deg, #ff6b81, #ff4757, #ffa502); margin-bottom: 10rpx; }
.match-avatar { width: 100%; height: 100%; border-radius: 50%; border: 4rpx solid #fff; }
.match-nick { font-size: 22rpx; color: #333; width: 120rpx; text-align: center; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }

/* ---- 消息列表 ---- */
.msg-section { background: #fff; padding-top: 24rpx; }
.chat-list { padding: 0 32rpx; }
.chat-item { display: flex; align-items: center; padding: 24rpx 0; border-bottom: 1rpx solid #f5f6f8; }
.chat-item:last-child { border-bottom: none; }
.chat-avatar-wrap { position: relative; margin-right: 24rpx; flex-shrink: 0; }
.chat-avatar { width: 100rpx; height: 100rpx; border-radius: 50%; }
.online-dot { position: absolute; bottom: 4rpx; right: 4rpx; width: 20rpx; height: 20rpx; border-radius: 50%; background: #07c160; border: 4rpx solid #fff; }
.unread-dot { position: absolute; top: -6rpx; right: -6rpx; background: #ff4757; border-radius: 24rpx; padding: 2rpx 12rpx; min-width: 32rpx; text-align: center; border: 3rpx solid #fff; }
.unread-num { color: #fff; font-size: 20rpx; font-weight: 600; }
.chat-body { flex: 1; overflow: hidden; }
.chat-top-row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10rpx; }
.chat-name { font-size: 30rpx; font-weight: 600; color: #1a1a1a; }
.chat-time { font-size: 22rpx; color: #ccc; flex-shrink: 0; }
.chat-preview { font-size: 26rpx; color: #999; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; display: block; }

/* ---- 空状态 ---- */
.empty-state { display: flex; flex-direction: column; align-items: center; padding-top: 240rpx; }
.empty-circle { width: 140rpx; height: 140rpx; border-radius: 50%; background: linear-gradient(135deg, #fff0f3, #ffe0e6); display: flex; align-items: center; justify-content: center; margin-bottom: 28rpx; }
.empty-icon { font-size: 56rpx; }
.empty-title { font-size: 32rpx; font-weight: 700; color: #1a1a1a; margin-bottom: 12rpx; }
.empty-desc { font-size: 26rpx; color: #b3b3b3; }
</style>
