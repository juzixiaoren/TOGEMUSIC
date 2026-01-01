<template>
  <div class="player-room">
    <el-card>
      <template #header>
        <div>播放房间</div>
      </template>
      <div class="player-controls">
        <el-button @click="previousSong" :disabled="!musicStore.currentSong">上一首</el-button>
        <el-button @click="togglePlay" type="primary">
          {{ musicStore.isPlaying ? '暂停' : '播放' }}
        </el-button>
        <el-button @click="nextSong" :disabled="!musicStore.currentSong">下一首</el-button>
        <el-button @click="toggleRandom">
          {{ musicStore.isRandom ? '顺序播放' : '随机播放' }}
        </el-button>
      </div>
      <div class="current-song" v-if="musicStore.currentSong">
        <h3>{{ musicStore.currentSong.title }} - {{ musicStore.currentSong.artist }}</h3>
        <el-progress :percentage="progress" :show-text="false"></el-progress>
        <div class="time">{{ formatTime(musicStore.currentTime) }} / {{ formatTime(musicStore.duration) }}</div>
      </div>
      <el-table :data="musicStore.currentPlaylist" style="width: 100%; margin-top: 20px;" @selection-change="handleSelectionChange">
        <el-table-column type="selection" width="55"></el-table-column>
        <el-table-column prop="title" label="歌名"></el-table-column>
        <el-table-column prop="artist" label="歌手"></el-table-column>
        <el-table-column label="操作">
          <template #default="scope">
            <el-button @click="playSong(scope.row)" :type="musicStore.currentSong?.id === scope.row.id ? 'primary' : ''">播放</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-button type="danger" @click="removeSelected" :disabled="selectedSongs.length === 0">删除选中</el-button>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useMusicStore } from '../stores'
import { Howl } from 'howler'
import http from '../utils/http'

const musicStore = useMusicStore()
const selectedSongs = ref([])
const sound = ref(null)

const progress = computed(() => {
  if (musicStore.duration === 0) return 0
  return (musicStore.currentTime / musicStore.duration) * 100
})

const formatTime = (seconds) => {
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  return `${mins}:${secs.toString().padStart(2, '0')}`
}

const handleSelectionChange = (selection) => {
  selectedSongs.value = selection
}

const playSong = (song) => {
  if (sound.value) {
    sound.value.stop()
  }
  musicStore.setCurrentSong(song)
  sound.value = new Howl({
    src: [`/reverse/music/${song.file_path}`],
    html5: true,
    onload: () => {
      musicStore.setDuration(sound.value.duration())
    },
    onplay: () => {
      musicStore.togglePlay()
      requestAnimationFrame(updateTime)
    },
    onpause: () => {
      musicStore.togglePlay()
    },
    onend: () => {
      nextSong()
    }
  })
  sound.value.play()
}

const togglePlay = () => {
  if (sound.value) {
    if (musicStore.isPlaying) {
      sound.value.pause()
    } else {
      sound.value.play()
    }
  }
}

const previousSong = () => {
  const currentIndex = musicStore.currentPlaylist.findIndex(song => song.id === musicStore.currentSong.id)
  if (currentIndex > 0) {
    playSong(musicStore.currentPlaylist[currentIndex - 1])
  }
}

const nextSong = () => {
  const currentIndex = musicStore.currentPlaylist.findIndex(song => song.id === musicStore.currentSong.id)
  let nextIndex
  if (musicStore.isRandom) {
    nextIndex = Math.floor(Math.random() * musicStore.currentPlaylist.length)
  } else {
    nextIndex = (currentIndex + 1) % musicStore.currentPlaylist.length
  }
  playSong(musicStore.currentPlaylist[nextIndex])
}

const toggleRandom = () => {
  musicStore.toggleRandom()
}

const removeSelected = async () => {
  try {
    const songIds = selectedSongs.value.map(song => song.id)
    await http.delete('/reverse/player/songs', { data: { song_ids: songIds } })
    musicStore.setCurrentPlaylist(musicStore.currentPlaylist.filter(song => !songIds.includes(song.id)))
    selectedSongs.value = []
  } catch (error) {
    console.error(error)
  }
}

const updateTime = () => {
  if (sound.value && musicStore.isPlaying) {
    musicStore.setCurrentTime(sound.value.seek())
    requestAnimationFrame(updateTime)
  }
}

const fetchCurrentPlaylist = async () => {
  try {
    const response = await http.get('/reverse/player/playlist')
    musicStore.setCurrentPlaylist(response.data)
  } catch (error) {
    console.error(error)
  }
}

onMounted(() => {
  fetchCurrentPlaylist()
})

onUnmounted(() => {
  if (sound.value) {
    sound.value.stop()
  }
})
</script>

<style scoped>
.player-controls {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}

.current-song {
  margin-bottom: 20px;
}

.time {
  text-align: center;
  margin-top: 10px;
}
</style>