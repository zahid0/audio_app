<template>
  <div class="container">
    <div class="search">
      <input type="text" v-model="searchQuery" placeholder="Search audios..." class="search-bar" />
    </div>
    <div class="main-content">
      <div class="collections-menu">
        <ul>
          <li v-for="collection in collections" :key="collection.id" @click="selectCollection(collection.id)" :class="{ 'selected': selectedCollectionId === collection.id }">{{ collection.name }}</li>
        </ul>
      </div>
      <div class="audio-list" :class="{ 'transcript-open': showTranscript }">
        <ul>
          <li v-for="audio in filteredAudios" :key="audio.id" @click="playAudio(audio)">
            {{ audio.title }}
            <i @click.stop="fetchTranscript(audio.title)">&#x1F4DC;</i>
          </li>
        </ul>
      </div>
      <div class="transcript-modal" v-if="showTranscript">
        <span class="close-button" @click="this.showTranscript = false">X</span>
        <pre class="transcript-content">{{ this.transcript }}</pre>
      </div>
    </div>
    <div class="audio-container">
      <span>Now Playing: {{ this.currentAudio.title }}</span>
      <audio ref="audioPlayer" :src="currentAudio.url" preload="auto" controls autoplay class="audio-player"></audio>
    </div>
  </div>
</template>

<script>
import axios from '../axios';

export default {
  name: 'Home',
  components: {
  },
  data() {
    return {
      audios: [],
      currentAudio: {},
      searchQuery: '',
      collections: [],
      selectedCollectionId: null,
      showTranscript: false,
      transcript: '',
    };
  },
  computed: {
    filteredAudios() {
      return this.audios.filter(audio =>
        audio.title.toLowerCase().includes(this.searchQuery.toLowerCase())
      );
    }
  },
  methods: {
    async fetchControlCollections() {
      const response = await axios.get('/api/collections');
      this.collections = response.data;
      if (this.collections.length > 0) {
        this.selectCollection(this.collections[0].id);
      }
    },
    async fetchAudios(collectionId) {
      const response = await axios.get(`/api/audios/${collectionId}`);
      this.audios = response.data;
    },
    selectCollection(collectionId) {
      if (this.selectedCollectionId === collectionId) return;
      this.selectedCollectionId = collectionId;
      this.fetchAudios(collectionId);
    },
    async playAudio(audio) {
      this.currentAudio = audio;
      this.$nextTick(() => {
        this.$refs.audioPlayer.play();
      });
    },
    async fetchTranscript(id) {
      try {
        const response = await axios.get(`/api/transcripts/${id}`);
        const response_json = response.data;
        this.transcript = response_json['text'];
        this.showTranscript = true;
      } catch (error) {
        const response_code = error.response ? error.response.status : 'unknown';
        this.transcript = `Unable to fetch transcript, response code = ${response_code}`;
        this.showTranscript = true;
      }
    },
  },
  mounted() {
    this.fetchControlCollections();
  },
};
</script>

<style>

.container {
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.search {
  flex: 0 0 40px;
  border: 2px solid black;
}

.main-content {
  flex: 1;
  display: flex;
  overflow: hidden;
}

.collections-menu {
  flex: 0 0 max(150px, 15%);
  border: 2px solid black;
  overflow-y: auto;
}

.audio-list {
  flex: 1;
  overflow-y: auto;
  transition: flex 0.3s ease;
}

.audio-list.transcript-open {
  flex: 0 0 35%;
}

.transcript-modal {
  flex: 0 0 50%;
  overflow-y: auto;
  position: relative;
  border-left: 2px solid black;
}

.audio-container {
  flex: 0 0 60px;
  border: 1px solid black;
}

.search-bar {
  padding: 10px;
  border: 1px solid #ccc;
  border-radius: 4px;
  width: 98%;
}

li {
  cursor: pointer;
  list-style-type: none;
}

li:hover {
  background-color: #f5f5f5;
}

ul .selected {
  background-color: #EDF7FA;
}

.transcript-content {
  white-space: pre-wrap;
  overflow-wrap: break-word;
}

.close-button {
  position: absolute;
  top: 10px;
  right: 10px;
  cursor: pointer;
  font-size: 16px;
  background: none;
  border: none;
  color: #000;
  z-index: 10;
}

.close-button:hover {
  color: red;
}

.icon {
  height: 15px;
  width: auto;
}

.audio-player {
  width: 100%;
  background-color: #e9ecef;
}

.audio-container span {
  color: #343a40;
  margin: 0;
}

@media (max-width: 768px) {
  .main-content {
    flex-direction: column;
  }

  .collections-menu {
    flex: 0 0 auto;
    max-height: 30vh;
  }

  .audio-list {
    flex: 1;
  }

  .transcript-modal {
    position: fixed;
    top: 40px;
    left: 0;
    right: 0;
    bottom: 60px;
    z-index: 1000;
    background: white;
    border: none;
    box-shadow: 0 0 10px rgba(0,0,0,0.1);
  }
}

</style>
