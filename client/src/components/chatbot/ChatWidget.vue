<script setup>
import { ref, nextTick, watch } from 'vue'
import { useChatStore } from '@/store/chat'
import ChatMessage from './ChatMessage.vue'
import PreferenceQuickReplies from './PreferenceQuickReplies.vue'

const chatStore = useChatStore()
const draft = ref('')
const scrollEl = ref(null)

async function scrollToBottom() {
  await nextTick()
  if (scrollEl.value) scrollEl.value.scrollTop = scrollEl.value.scrollHeight
}

watch(() => chatStore.messages.length, scrollToBottom)
watch(() => chatStore.isOpen, (open) => { if (open) scrollToBottom() })

function handleSubmit() {
  if (!draft.value.trim()) return
  chatStore.sendMessage(draft.value)
  draft.value = ''
}

function handleQuickReply(reply) {
  chatStore.sendQuickReply(reply)
}
</script>

<template>
  <transition name="chat-widget-fade">
    <aside v-if="chatStore.isOpen" class="chat-widget" role="dialog" aria-label="Memory assistant">
      <header class="chat-widget__header">
        <div class="chat-widget__title">
         <button
  type="button"
  class="chat-widget__reload"
  aria-label="Refresh conversation"
  title="Refresh conversation"
  
  :disabled="chatStore.isLoadingHistory || chatStore.isSending"
  @click="chatStore.refreshHistory()"
>
  <svg
    width="16"
    height="16"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    stroke-width="1.8"
    :class="{ 'is-spinning': chatStore.isLoadingHistory }"
  >
    <path d="M21 12a8 8 0 1 1-3.2-6.4" />
    <path d="M21 4v5h-5" />
  </svg>
</button>
          <div>
            <p class="chat-widget__title-text">Listening memory</p>
            <p class="chat-widget__subtitle">Knows what you play &amp; skip</p>
          </div>
        </div>
        <button class="icon-btn" aria-label="Close" @click="chatStore.close()">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M6 6l12 12M18 6 6 18"/></svg>
        </button>
      </header>

      <div ref="scrollEl" class="chat-widget__messages">
        <ChatMessage v-for="message in chatStore.messages" :key="message.id" :message="message" />
        <p v-if="chatStore.isLoadingHistory" class="chat-widget__hint">Loading your conversation…</p>
      </div>

      <PreferenceQuickReplies
        :replies="chatStore.quickReplies"
        :disabled="chatStore.isSending"
        @select="handleQuickReply"
      />

      <form class="chat-widget__composer" @submit.prevent="handleSubmit">
        <input
          v-model="draft"
          type="text"
          placeholder="Tell me a genre, artist, or song preference…"
          aria-label="Message"
          :disabled="chatStore.isSending"
        />
        <button type="submit" class="chat-widget__send" :disabled="chatStore.isSending || !draft.trim()" aria-label="Send">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 2 11 13"/><path d="M22 2 15 22l-4-9-9-4 20-7z"/></svg>
        </button>
      </form>
    </aside>
  </transition>
</template>

<style scoped>
.chat-widget {
  position: fixed;
  right: 28px;
  bottom: calc(var(--playerbar-h) + 24px);
  width: 360px;
  max-height: 560px;
  display: flex;
  flex-direction: column;
  background: var(--bg-base);
  border: 1px solid var(--line-soft);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-panel);
  z-index: 20;
  overflow: hidden;
}

.chat-widget__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 14px 12px 16px;
  border-bottom: 1px solid var(--line-soft);
}
.chat-widget__title { display: flex; align-items: center; gap: 10px; }
.chat-widget__mark { color: var(--accent); }
.chat-widget__reload {
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 0;
  border-radius: 50%;
  background: transparent;
  color: var(--accent);
  cursor: pointer;
  transition: background 0.15s ease, opacity 0.15s ease;
}

.chat-widget__reload:hover:not(:disabled) {
  background: var(--bg-raised);
}

.chat-widget__reload:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.chat-widget__reload svg {
  transition: transform 0.2s ease;
}

.chat-widget__reload .is-spinning {
  animation: chat-reload-spin 0.8s linear infinite;
}

@keyframes chat-reload-spin {
  from {
    transform: rotate(0deg);
  }

  to {
    transform: rotate(360deg);
  }
}
.chat-widget__title-text { margin: 0; font-size: 13.5px; font-weight: 700; color: var(--text-primary); }
.chat-widget__subtitle { margin: 1px 0 0; font-size: 11px; color: var(--text-tertiary); }

.chat-widget__messages {
  flex: 1;
  overflow-y: auto;
  padding: 14px 16px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  min-height: 240px;
}

.chat-widget__hint { color: var(--text-tertiary); font-size: 12px; text-align: center; }

.chat-widget__composer {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px;
  border-top: 1px solid var(--line-soft);
}
.chat-widget__composer input {
  flex: 1;
  background: var(--bg-raised);
  border: 1px solid var(--line);
  border-radius: var(--radius-pill);
  padding: 9px 14px;
  font-size: 13px;
  outline: none;
  color: var(--text-primary);
}
.chat-widget__composer input::placeholder { color: var(--text-tertiary); }
.chat-widget__composer input:focus { border-color: var(--accent-dim); }

.chat-widget__send {
  width: 34px;
  height: 34px;
  border-radius: 50%;
  background: var(--accent);
  color: #1a1305;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: background 0.15s ease;
}
.chat-widget__send:hover:not(:disabled) { background: var(--accent-strong); }
.chat-widget__send:disabled { opacity: 0.4; cursor: not-allowed; }

.chat-widget-fade-enter-active,
.chat-widget-fade-leave-active { transition: opacity 0.15s ease, transform 0.15s ease; }
.chat-widget-fade-enter-from,
.chat-widget-fade-leave-to { opacity: 0; transform: translateY(8px); }

@media (max-width: 860px) {
  .chat-widget { right: 12px; left: 12px; width: auto; bottom: calc(var(--playerbar-h) + 16px); }
}
</style>
