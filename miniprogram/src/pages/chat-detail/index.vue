<template>
  <view class="chat-detail">
    <!-- 连接状态 -->
    <view class="conn-status" v-if="!wsConnected">
      <text class="conn-text">连接中...</text>
    </view>

    <!-- 对方正在输入 -->
    <view class="typing-bar" v-if="partnerTyping">
      <text class="typing-text">对方正在输入...</text>
    </view>

    <!-- 消息列表 -->
    <scroll-view
      scroll-y
      class="message-list"
      :scroll-into-view="scrollToId"
      :scroll-with-animation="true"
    >
      <view class="msg-date-hint" v-if="messages.length">
        <text>以下是聊天记录</text>
      </view>

      <view
        v-for="(msg, idx) in messages"
        :key="msg.id"
        :id="'msg-' + msg.id"
      >
        <view class="time-divider" v-if="shouldShowTime(idx)">
          <text class="time-text">{{ formatFullTime(msg.created_at) }}</text>
        </view>

        <view :class="['msg-row', msg.sender_id === myUserId ? 'mine' : 'other']">
          <image
            v-if="msg.sender_id !== myUserId"
            class="msg-avatar"
            :src="partnerAvatar || defaultAvatar"
            mode="aspectFill"
          />
          <!-- 已撤回 -->
          <view v-if="msg.is_recalled" class="bubble-recalled">
            <text class="recalled-text">{{ msg.sender_id === myUserId ? '你撤回了一条消息' : '对方撤回了一条消息' }}</text>
          </view>
          <!-- 文字消息 -->
          <view v-else-if="msg.msg_type !== 'image'" :class="getBubbleClass(idx, msg)"
            @longpress="onLongPress(msg)">
            <!-- 引用块 -->
            <view v-if="msg.reply_to_id" class="quote-block">
              <text class="quote-author">{{ msg.reply_to_sender_id === myUserId ? '你' : partnerName }}</text>
              <text class="quote-content-text">{{ truncateQuote(msg) }}</text>
            </view>
            <text class="bubble-text">{{ msg.content }}</text>
          </view>
          <!-- 图片消息 -->
          <view v-else class="bubble-img-wrap" @tap="previewImg(msg.content)"
            @longpress="onLongPress(msg)">
            <!-- 引用块（图片消息也可能有引用） -->
            <view v-if="msg.reply_to_id" class="quote-block quote-in-img">
              <text class="quote-author">{{ msg.reply_to_sender_id === myUserId ? '你' : partnerName }}</text>
              <text class="quote-content-text">{{ truncateQuote(msg) }}</text>
            </view>
            <image class="bubble-img" :src="msg.content" mode="widthFix" />
          </view>
        </view>

        <!-- 已读标记 (仅对自己发的最后一条已读消息显示) -->
        <view class="read-tag" v-if="msg.sender_id === myUserId && msg.is_read && isLastReadMsg(idx)">
          <text class="read-text">已读</text>
        </view>
      </view>

      <view class="empty-chat" v-if="messages.length === 0">
        <view class="wave-hand">👋</view>
        <text class="empty-hint">说点什么开始聊天吧</text>
      </view>
    </scroll-view>

    <!-- 引用预览条 -->
    <view class="reply-preview" v-if="replyingTo">
      <view class="reply-preview-inner">
        <text class="reply-preview-label">引用</text>
        <text class="reply-preview-text">{{ truncateQuote(replyingTo) }}</text>
      </view>
      <view class="reply-preview-close" @tap="replyingTo = null">✕</view>
    </view>

    <!-- 输入栏 -->
    <view class="input-bar">
      <view class="extra-btn" @tap="chooseImage">
        <text class="extra-icon">🖼</text>
      </view>
      <view class="input-wrapper">
        <input
          class="msg-input"
          v-model="inputText"
          placeholder="输入消息..."
          confirm-type="send"
          @confirm="sendMessage"
          @input="onTyping"
        />
      </view>
      <view
        :class="['send-btn', { active: inputText.trim() }]"
        @tap="sendMessage"
      >
        <text class="send-icon">➤</text>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick, onUnmounted } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import { chatApi } from '../../api/index'
import { BASE_URL } from '../../api/request'
import { useUserStore } from '../../stores/user'

const userStore = useUserStore()
const matchId = ref(0)
const messages = ref<any[]>([])
const inputText = ref('')
const scrollToId = ref('')
const myUserId = ref(0)
const partnerAvatar = ref('')
const partnerName = ref('')
const defaultAvatar = 'https://api.dicebear.com/7.x/avataaars/svg?seed=default'
const wsConnected = ref(false)
const partnerTyping = ref(false)
const replyingTo = ref<any>(null)
const scrollToMsgId = ref<number | null>(null)

let socketTask: UniApp.SocketTask | null = null
let pingTimer: any = null
let reconnectTimer: any = null
let pollingTimer: any = null
let typingTimer: any = null
let typingCooldown = 0

onLoad((options: any) => {
  matchId.value = Number(options.matchId)
  if (options.nickname) {
    const name = decodeURIComponent(options.nickname)
    partnerName.value = name
    uni.setNavigationBarTitle({ title: name })
  }
  if (options.scrollToMsgId) {
    scrollToMsgId.value = Number(options.scrollToMsgId)
  }
})

onMounted(async () => {
  myUserId.value = userStore.profile?.user_id || 0
  await loadMessages()
  connectWebSocket()
})

onUnmounted(() => {
  closeWebSocket()
  if (pollingTimer) clearInterval(pollingTimer)
  if (typingTimer) clearTimeout(typingTimer)
})

function connectWebSocket() {
  const token = uni.getStorageSync('access_token')
  if (!token) { startPolling(); return }

  const wsUrl = BASE_URL.replace(/^http/, 'ws').replace(/\/api\/v1$/, '')
  const url = `${wsUrl}/api/v1/ws/chat?token=${token}`

  try {
    socketTask = uni.connectSocket({ url, success() {}, fail() { startPolling() } })

    socketTask.onOpen(() => {
      wsConnected.value = true
      if (pollingTimer) { clearInterval(pollingTimer); pollingTimer = null }
      pingTimer = setInterval(() => {
        socketTask?.send({ data: JSON.stringify({ type: 'ping' }) })
      }, 30000)
      socketTask?.send({ data: JSON.stringify({ type: 'read', match_id: matchId.value }) })
    })

    socketTask.onMessage((res: any) => {
      try {
        const data = typeof res.data === 'string' ? JSON.parse(res.data) : res.data

        if (data.type === 'new_message' && data.data) {
          const msg = data.data
          if (msg.match_id === matchId.value) {
            const exists = messages.value.some((m: any) => m.id === msg.id)
            if (!exists) { messages.value.push(msg); scrollToBottom() }
            if (msg.sender_id !== myUserId.value) {
              socketTask?.send({ data: JSON.stringify({ type: 'read', match_id: matchId.value }) })
            }
          }
        }

        if (data.type === 'read_ack' && data.match_id === matchId.value) {
          messages.value.forEach((m: any) => {
            if (m.sender_id === myUserId.value) m.is_read = true
          })
        }

        if (data.type === 'typing' && data.match_id === matchId.value) {
          partnerTyping.value = true
          if (typingTimer) clearTimeout(typingTimer)
          typingTimer = setTimeout(() => { partnerTyping.value = false }, 3000)
        }
      } catch {}
    })

    socketTask.onClose(() => {
      wsConnected.value = false; cleanupTimers()
      reconnectTimer = setTimeout(() => connectWebSocket(), 3000)
    })

    socketTask.onError(() => {
      wsConnected.value = false; cleanupTimers(); startPolling()
    })
  } catch { startPolling() }
}

function closeWebSocket() {
  cleanupTimers()
  if (reconnectTimer) { clearTimeout(reconnectTimer); reconnectTimer = null }
  if (socketTask) { try { socketTask.close({}) } catch {}; socketTask = null }
}

function cleanupTimers() {
  if (pingTimer) { clearInterval(pingTimer); pingTimer = null }
}

function startPolling() {
  if (pollingTimer) return
  pollingTimer = setInterval(async () => {
    try {
      const res = await chatApi.getMessages(matchId.value)
      if (res.data && res.data.length > messages.value.length) {
        messages.value = res.data; scrollToBottom()
      }
    } catch {}
  }, 5000)
}

function onTyping() {
  const now = Date.now()
  if (now - typingCooldown > 2000 && wsConnected.value && socketTask) {
    typingCooldown = now
    socketTask.send({ data: JSON.stringify({ type: 'typing', match_id: matchId.value }) })
  }
}

function shouldShowTime(idx: number): boolean {
  if (idx === 0) return true
  const prev = new Date(messages.value[idx - 1].created_at).getTime()
  const curr = new Date(messages.value[idx].created_at).getTime()
  return curr - prev > 300000
}

function isLastReadMsg(idx: number): boolean {
  for (let i = messages.value.length - 1; i >= 0; i--) {
    if (messages.value[i].sender_id === myUserId.value && messages.value[i].is_read) {
      return i === idx
    }
  }
  return false
}

function getBubbleClass(idx: number, msg: any) {
  const isMine = msg.sender_id === myUserId.value
  let base = isMine ? 'bubble-mine' : 'bubble-other'

  const prevSame = idx > 0 && messages.value[idx - 1].sender_id === msg.sender_id
  const nextSame = idx < messages.value.length - 1 && messages.value[idx + 1].sender_id === msg.sender_id

  if (!prevSame && !nextSame) return `bubble ${base} isolated`
  if (!prevSame && nextSame) return `bubble ${base} first`
  if (prevSame && !nextSame) return `bubble ${base} last`
  return `bubble ${base} middle`
}

function truncateQuote(msg: any): string {
  const content = msg.reply_to_content || msg.content || ''
  const isImage = msg.reply_to_id
    ? (msg.reply_to_content || '').startsWith('http') && /\.(jpg|jpeg|png|gif|webp)/i.test(msg.reply_to_content || '')
    : msg.msg_type === 'image'
  if (isImage) return '[图片]'
  return content.length > 40 ? content.substring(0, 40) + '…' : content
}

function formatFullTime(timeStr: string): string {
  const d = new Date(timeStr)
  const now = new Date()
  const isToday = d.toDateString() === now.toDateString()
  const hh = d.getHours().toString().padStart(2, '0')
  const mm = d.getMinutes().toString().padStart(2, '0')
  if (isToday) return `${hh}:${mm}`
  return `${d.getMonth() + 1}/${d.getDate()} ${hh}:${mm}`
}

async function loadMessages() {
  try {
    const res = await chatApi.getMessages(matchId.value)
    messages.value = res.data || []
    if (scrollToMsgId.value) {
      // 滚动到搜索命中的特定消息
      nextTick(() => {
        setTimeout(() => {
          scrollToId.value = `msg-${scrollToMsgId.value}`
          scrollToMsgId.value = null
        }, 100)
      })
    } else {
      scrollToBottom()
    }
  } catch (e) { console.error('加载消息失败', e) }
}

async function sendMessage() {
  const text = inputText.value.trim()
  if (!text) return
  const replyId = replyingTo.value?.id || undefined
  inputText.value = ''
  replyingTo.value = null

  if (wsConnected.value && socketTask) {
    socketTask.send({
      data: JSON.stringify({
        type: 'message',
        match_id: matchId.value,
        content: text,
        msg_type: 'text',
        ...(replyId ? { reply_to_id: replyId } : {}),
      }),
    })
  } else {
    try {
      const res = await chatApi.sendMessage(matchId.value, text, 'text', replyId)
      messages.value.push(res.data); scrollToBottom()
    } catch (e) {
      console.error('发送失败', e)
      uni.showToast({ title: '发送失败', icon: 'none' })
    }
  }
}

function chooseImage() {
  uni.chooseImage({
    count: 1,
    sizeType: ['compressed'],
    success(res) {
      const filePath = res.tempFilePaths[0]
      uni.showLoading({ title: '发送中...' })
      const token = uni.getStorageSync('access_token') || ''
      uni.uploadFile({
        url: `${BASE_URL}/upload/photo?is_avatar=false`,
        filePath,
        name: 'file',
        header: { Authorization: `Bearer ${token}` },
        success(uploadRes) {
          uni.hideLoading()
          try {
            const data = JSON.parse(uploadRes.data)
            if (data.code === 0 && data.data?.url) {
              const apiBase = BASE_URL.replace(/\/api\/v1$/, '')
              const imgUrl = data.data.url.startsWith('http') ? data.data.url : `${apiBase}${data.data.url}`
              if (wsConnected.value && socketTask) {
                socketTask.send({
                  data: JSON.stringify({ type: 'message', match_id: matchId.value, content: imgUrl, msg_type: 'image' }),
                })
              } else {
                chatApi.sendMessage(matchId.value, imgUrl, 'image').then(r => {
                  messages.value.push(r.data); scrollToBottom()
                })
              }
            } else {
              uni.showToast({ title: '上传失败', icon: 'none' })
            }
          } catch { uni.showToast({ title: '上传失败', icon: 'none' }) }
        },
        fail() {
          uni.hideLoading()
          uni.showToast({ title: '上传失败', icon: 'none' })
        },
      })
    },
  })
}

function onLongPress(msg: any) {
  if (msg.is_recalled) return
  const isMine = msg.sender_id === myUserId.value
  const now = Date.now()
  const sentAt = new Date(msg.created_at).getTime()
  const canRecall = isMine && (now - sentAt) < 120000

  const items: string[] = []
  items.push('引用')
  if (canRecall) items.push('撤回')

  uni.showActionSheet({
    itemList: items,
    success(res) {
      const action = items[res.tapIndex]
      if (action === '引用') replyingTo.value = msg
      else if (action === '撤回') doRecall(msg)
    }
  })
}

async function doRecall(msg: any) {
  try {
    await chatApi.recallMessage(msg.id)
    const idx = messages.value.findIndex((m: any) => m.id === msg.id)
    if (idx !== -1) messages.value[idx] = { ...messages.value[idx], is_recalled: true }
  } catch (e: any) {
    uni.showToast({ title: e?.message || '撤回失败', icon: 'none' })
  }
}

function previewImg(url: string) {
  uni.previewImage({ urls: [url], current: url })
}

function scrollToBottom() {
  nextTick(() => {
    if (messages.value.length > 0) {
      scrollToId.value = ''
      setTimeout(() => {
        scrollToId.value = `msg-${messages.value[messages.value.length - 1].id}`
      }, 50)
    }
  })
}
</script>

<style scoped>
.chat-detail { display: flex; flex-direction: column; height: 100vh; background: #f0f1f5; }

.conn-status { text-align: center; padding: 8rpx 0; background: #fff3cd; }
.conn-text { font-size: 22rpx; color: #856404; }

.typing-bar { text-align: center; padding: 6rpx 0; background: rgba(255,107,129,0.08); }
.typing-text { font-size: 22rpx; color: #ff6b81; }

.message-list { flex: 1; padding: 20rpx 24rpx; overflow-y: auto; }
.msg-date-hint { text-align: center; padding: 16rpx 0 24rpx; font-size: 22rpx; color: #ccc; }

.time-divider { text-align: center; padding: 24rpx 0 16rpx; }
.time-text { font-size: 22rpx; color: #b3b3b3; background: rgba(0,0,0,0.04); padding: 6rpx 20rpx; border-radius: 12rpx; }

.msg-row { display: flex; margin-bottom: 24rpx; align-items: flex-end; }
.msg-row.mine { flex-direction: row-reverse; }
.msg-row.other { flex-direction: row; }
.msg-avatar { width: 68rpx; height: 68rpx; border-radius: 50%; margin-right: 16rpx; flex-shrink: 0; }

.bubble { max-width: 520rpx; padding: 22rpx 32rpx; word-break: break-all; line-height: 1.5; }

/* iMessage 风格颜色 */
.bubble-mine { background: linear-gradient(135deg, #007AFF, #0056D6); box-shadow: 0 4rpx 16rpx rgba(0, 122, 255, 0.25); }
.bubble-mine .bubble-text { color: #fff; font-size: 32rpx; font-weight: 400; }
.bubble-other { background: #E5E5EA; border: none; box-shadow: none; }
.bubble-other .bubble-text { color: #000; font-size: 32rpx; font-weight: 400; }

/* 智能气泡圆角分配 (iOS Native Specs) */
.bubble-mine.isolated { border-radius: 40rpx 40rpx 12rpx 40rpx; }
.bubble-mine.first { border-radius: 40rpx 40rpx 12rpx 40rpx; margin-bottom: -16rpx; }
.bubble-mine.middle { border-radius: 40rpx 12rpx 12rpx 40rpx; margin-bottom: -16rpx; }
.bubble-mine.last { border-radius: 40rpx 12rpx 40rpx 40rpx; }

.bubble-other.isolated { border-radius: 40rpx 40rpx 40rpx 12rpx; }
.bubble-other.first { border-radius: 40rpx 40rpx 40rpx 12rpx; margin-bottom: -16rpx; }
.bubble-other.middle { border-radius: 12rpx 40rpx 40rpx 12rpx; margin-bottom: -16rpx; }
.bubble-other.last { border-radius: 12rpx 40rpx 40rpx 40rpx; }

/* 引用块 - 蓝色气泡内（自己发的） */
.bubble-mine .quote-block {
  background: rgba(255, 255, 255, 0.18);
  border-left: 4rpx solid rgba(255, 255, 255, 0.7);
  border-radius: 8rpx;
  padding: 10rpx 16rpx;
  margin-bottom: 14rpx;
}
.bubble-mine .quote-author { font-size: 20rpx; color: rgba(255,255,255,0.75); display: block; margin-bottom: 4rpx; font-weight: 600; }
.bubble-mine .quote-content-text { font-size: 22rpx; color: rgba(255,255,255,0.65); display: block; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }

/* 引用块 - 灰色气泡内（对方发的） */
.bubble-other .quote-block {
  background: rgba(0, 0, 0, 0.06);
  border-left: 4rpx solid #ff6b81;
  border-radius: 8rpx;
  padding: 10rpx 16rpx;
  margin-bottom: 14rpx;
}
.bubble-other .quote-author { font-size: 20rpx; color: #ff6b81; display: block; margin-bottom: 4rpx; font-weight: 600; }
.bubble-other .quote-content-text { font-size: 22rpx; color: #666; display: block; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }

/* 图片消息内引用块 */
.quote-in-img { margin-bottom: 12rpx; }

/* Image bubble */
.bubble-img-wrap { max-width: 400rpx; border-radius: 16rpx; overflow: hidden; background: #E5E5EA; padding: 16rpx; }
.bubble-img { width: 100%; border-radius: 12rpx; }

/* Read receipt */
.read-tag { text-align: right; padding-right: 16rpx; margin-top: -16rpx; margin-bottom: 12rpx; }
.read-text { font-size: 20rpx; color: #b3b3b3; }

/* Recalled message */
.bubble-recalled { padding: 12rpx 24rpx; }
.recalled-text { font-size: 24rpx; color: #b3b3b3; font-style: italic; }

.empty-chat { display: flex; flex-direction: column; align-items: center; padding-top: 240rpx; }
.wave-hand { font-size: 80rpx; margin-bottom: 20rpx; }
.empty-hint { font-size: 28rpx; color: #b3b3b3; }

/* 引用预览条 */
.reply-preview {
  display: flex;
  align-items: center;
  padding: 14rpx 24rpx;
  background: #fafafa;
  border-top: 1rpx solid #ebebeb;
  gap: 16rpx;
}
.reply-preview-inner { flex: 1; overflow: hidden; display: flex; align-items: center; gap: 10rpx; }
.reply-preview-label { font-size: 22rpx; color: #ff6b81; font-weight: 700; flex-shrink: 0; }
.reply-preview-text { font-size: 24rpx; color: #888; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.reply-preview-close { font-size: 28rpx; color: #bbb; padding: 8rpx 4rpx; flex-shrink: 0; }

.input-bar { display: flex; align-items: center; padding: 16rpx 24rpx; background: #fff; border-top: 1rpx solid #f0f1f5; gap: 12rpx; padding-bottom: calc(16rpx + env(safe-area-inset-bottom)); }
.extra-btn { width: 72rpx; height: 72rpx; border-radius: 50%; background: #f0f1f5; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.extra-icon { font-size: 30rpx; }
.input-wrapper { flex: 1; background: #f0f1f5; border-radius: 40rpx; padding: 0 28rpx; display: flex; align-items: center; }
.msg-input { height: 76rpx; font-size: 28rpx; width: 100%; }
.send-btn { width: 76rpx; height: 76rpx; border-radius: 50%; background: #e0e0e0; display: flex; align-items: center; justify-content: center; flex-shrink: 0; transition: all 0.2s; }
.send-btn.active { background: linear-gradient(135deg, #ff6b81, #ff4757); box-shadow: 0 4rpx 16rpx rgba(255, 71, 87, 0.3); }
.send-icon { font-size: 32rpx; color: #fff; }
</style>
