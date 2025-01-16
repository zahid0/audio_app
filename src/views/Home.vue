<template>
  <div class="container">
    <div class="search">
      <input type="text" v-model="searchQuery" placeholder="Search audios..." class="search-bar" />
    </div>
    <div class="collections-menu">
      <ul>
        <li v-for="collection in collections" :key="collection.id" @click="selectCollection(collection.id)" :class="{ 'selected': selectedCollectionId === collection.id }">{{ collection.name }}</li>
      </ul>
    </div>
    <div class="audio-list">
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
    <div class="audio-container">
      <span> Now Playing: {{ this.currentAudio.title }}</span>
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
      const response = await axios.get(`/api/transcripts/${id}`);
      const response_json = response.data;
      this.transcript = response_json['text'];
      this.showTranscript = true;
    },
  },
  mounted() {
    this.fetchControlCollections();
  },
};
</script>

<style>

.container {
  height: 100%;
  display: grid;
  grid-gap: 1px;
  grid-template-columns: minmax(150px, 1fr) repeat(auto-fit, minmax(200px, 5fr));
  grid-template-rows: 40px repeat(auto-fit, minmax(200px, 1fr)) 60px;
}

.search {
  grid-column: 1 / -1;
  border: 2px solid black;
}

.collections-menu {
  border: 2px solid black;
  overflow-y: auto;
}

.audio-list {
  overflow-y: auto;
}

.transcript-modal {
  overflow-y: auto;
  position: relative;
}

.audio-container {
  grid-column: 1 / -1;
  grid-row: -1;
  border: 1px solid black;
}

.search-bar {
  padding: 10px;
  margin-bottom: 10px;
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
  overflow-y: auto;
  overflow-wrap: break-word;
}

.close-button {
  position: fixed;
  top: 70px;
  right: 20px;
  cursor: pointer;
  font-size: 16px;
  background: none;
  border: none;
  color: #000;
  z-index: 10px;
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
  background-color: #e9ecef; /* and a pleasing background color for player */
}

.audio-container span {
  color: #343a40;
  margin: 0;
}

</style>
