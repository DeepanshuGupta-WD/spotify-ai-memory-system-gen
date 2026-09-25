import { defineStore } from 'pinia'
import chatService from '@/services/chatService'

let idCounter = 0
const nextId = () => `local-${Date.now()}-${idCounter++}`

export const useChatStore = defineStore('chat', {
  state: () => ({
    isOpen: false,
    messages: [],
    quickReplies: [],
    isSending: false,
    isLoadingHistory: false,
    error: null,

    // IMPORTANT:
    // Chat history is intentionally NOT restored from backend.
    // Every browser refresh starts with a fresh chat UI.
    hasLoadedHistory: true,

    _sessionMarker: 0
  }),

  getters: {
    unreadCount: (state) =>
      state.isOpen
        ? 0
        : state.messages.filter(
            (m) => m.role === 'assistant' && m.unread
          ).length
  },

  actions: {
    open() {
      this.isOpen = true

      this.messages.forEach((m) => {
        m.unread = false
      })

      // Never restore old chat history.
      // Always keep the current fresh conversation.
      if (!this.messages.length) {
        this._seedGreeting()
      }

      if (!this.quickReplies.length) {
        this.loadQuickReplies()
      }
    },

    close() {
      this.isOpen = false
    },

    toggle() {
      this.isOpen ? this.close() : this.open()
    },

    /**
     * Completely refresh the visible chatbot conversation.
     *
     * IMPORTANT:
     * This only clears the chatbot UI conversation.
     * It does NOT delete Spotify listening memory,
     * preferences, Neo4j memories or PostgreSQL events.
     */
   async refreshHistory() {
  if (this.isSending || this.isLoadingHistory) return

  // Invalidate any previous in-flight request.
  this._sessionMarker += 1

  // Activate the reload button spinner.
  this.isLoadingHistory = true
  this.error = null
  this.hasLoadedHistory = true

  // Clear the previous visible conversation.
  this.messages = []

  // Start with a completely fresh chat.
  this._seedGreeting()

  // Refresh quick replies.
  this.quickReplies = []

  try {
    await this.loadQuickReplies()
  } finally {
    this.isLoadingHistory = false
  }
},

    /**
     * Called when the authenticated session changes.
     */
    resetSession() {
      this._sessionMarker += 1

      this.isOpen = false
      this.messages = []
      this.quickReplies = []
      this.isSending = false
      this.isLoadingHistory = false
      this.error = null

      // Do NOT load backend chat history after login/session reset.
      this.hasLoadedHistory = true
    },

    /**
     * Kept for compatibility with any existing callers.
     *
     * Deliberately does NOT fetch /chat/messages.
     */
    async loadHistory() {
      this.hasLoadedHistory = true

      if (!this.messages.length) {
        this._seedGreeting()
      }

      return this.messages
    },

    async loadQuickReplies() {
      try {
        this.quickReplies = await chatService.getQuickReplies()
      } catch {
        this.quickReplies = [
          {
            id: 'genre-electronic',
            label: 'I like electronic'
          },
          {
            id: 'artist-nova',
            label: 'I like Nova Lane'
          },
          {
            id: 'song-contrast',
            label: 'I like Midnight Circuit but not Neon Rain'
          }
        ]
      }
    },

    async sendMessage(content) {
      const trimmed = content.trim()

      if (!trimmed || this.isSending) return

      const userMessage = {
        id: nextId(),
        role: 'user',
        content: trimmed
      }

      this.messages.push(userMessage)

      const pendingId = nextId()
      const sessionMarker = this._sessionMarker

      this.messages.push({
        id: pendingId,
        role: 'assistant',
        content: '',
        pending: true
      })

      this.isSending = true
      this.error = null

      try {
        const recentContext = this.messages
          .filter((m) => !m.pending)
          .slice(-10)
          .map((m) => ({
            role: m.role,
            content: m.content
          }))

        const reply = await chatService.sendMessage(
          trimmed,
          recentContext
        )

        // If reload was clicked while request was running,
        // ignore the old response.
        if (sessionMarker !== this._sessionMarker) return

        const idx = this.messages.findIndex(
          (m) => m.id === pendingId
        )

        if (idx !== -1) {
          this.messages[idx] = {
            id: reply.id || nextId(),
            role: 'assistant',
            content: reply.content,
            trackRefs: reply.trackRefs || [],
            unread: !this.isOpen
          }
        }

        if (reply.quickReplies?.length) {
          this.quickReplies = reply.quickReplies
        }
      } catch (err) {
        if (sessionMarker !== this._sessionMarker) return

        this.error = err.message

        const idx = this.messages.findIndex(
          (m) => m.id === pendingId
        )

        if (idx !== -1) {
          this.messages[idx] = {
            id: pendingId,
            role: 'assistant',
            content:
              "I couldn't reach your memory service just now. Try again in a moment.",
            isError: true
          }
        }
      } finally {
        if (sessionMarker === this._sessionMarker) {
          this.isSending = false
        }
      }
    },

    sendQuickReply(reply) {
      this.sendMessage(
        reply.label || reply.prompt || reply.id
      )
    },

    _seedGreeting() {
      this.messages = [
        {
          id: nextId(),
          role: 'assistant',
          content:
            "Hey — I use what you play, skip, and tell me to shape recommendations. Which genre do you like?"
        }
      ]
    }
  }
})