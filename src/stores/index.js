import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const token = ref(localStorage.getItem('token') || '')

  const isLoggedIn = computed(() => !!token.value)

  function login(userData, userToken) {
    user.value = userData
    token.value = userToken
    localStorage.setItem('token', userToken)
  }

  function logout() {
    user.value = null
    token.value = ''
    localStorage.removeItem('token')
  }

  return { user, token, isLoggedIn, login, logout }
})

export const useMusicStore = defineStore('music', () => {
  const songs = ref([])
  const playlists = ref([])
  const currentPlaylist = ref([])
  const currentSong = ref(null)
  const isPlaying = ref(false)
  const currentTime = ref(0)
  const duration = ref(0)
  const isRandom = ref(false)

  function setSongs(newSongs) {
    songs.value = newSongs
  }

  function setPlaylists(newPlaylists) {
    playlists.value = newPlaylists
  }

  function setCurrentPlaylist(playlist) {
    currentPlaylist.value = playlist
  }

  function setCurrentSong(song) {
    currentSong.value = song
  }

  function togglePlay() {
    isPlaying.value = !isPlaying.value
  }

  function setCurrentTime(time) {
    currentTime.value = time
  }

  function setDuration(dur) {
    duration.value = dur
  }

  function toggleRandom() {
    isRandom.value = !isRandom.value
  }

  return {
    songs,
    playlists,
    currentPlaylist,
    currentSong,
    isPlaying,
    currentTime,
    duration,
    isRandom,
    setSongs,
    setPlaylists,
    setCurrentPlaylist,
    setCurrentSong,
    togglePlay,
    setCurrentTime,
    setDuration,
    toggleRandom
  }
})